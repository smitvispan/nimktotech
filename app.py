import re, io, csv, json, requests, os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session, Response
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from config import DATABASE_URL, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_SOCKET, OPENROUTER_KEY, AI_MODEL, GEMINI_KEYS as _GEMINI_KEYS, GEMINI_MODEL as _GEMINI_MODEL, SECRET_KEY

# Detect if we're using PostgreSQL (Render) or MySQL (local)
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
else:
    import pymysql

GEMINI_KEYS = _GEMINI_KEYS
GEMINI_MODEL = _GEMINI_MODEL
_gemini_key_idx = 0

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}


def get_db():
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        conn.autocommit = False
        return conn
    else:
        return pymysql.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
            database=DB_NAME, unix_socket=DB_SOCKET, cursorclass=pymysql.cursors.DictCursor,
        )


class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone(); cursor.close(); db.close()
    if user: return User(user['id'], user['username'], user['email'])
    return None

def init_db():
    db = get_db(); cursor = db.cursor()
    if USE_POSTGRES:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS search_history (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            business_type VARCHAR(100) NOT NULL,
            city VARCHAR(100) DEFAULT '',
            result_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )""")
    else:
        cursor.execute("""CREATE TABLE IF NOT EXISTS search_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            business_type VARCHAR(100) NOT NULL,
            city VARCHAR(100) DEFAULT '',
            result_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )""")
    db.commit(); cursor.close(); db.close()

init_db()


# ============ WEB SEARCH ============

EXCLUDE_DOMAINS = ['facebook.com', 'instagram.com', 'twitter.com', 'youtube.com',
                   'tripadvisor', 'pinterest.com', 'linkedin.com']

def search_web(query, max_results=30, page=1, backend='lite'):
    results = []
    try:
        ddgs = DDGS()
        for r in ddgs.text(query, max_results=max_results, backend=backend):
            title = r.get('title', '').strip()
            href = r.get('href', '').strip()
            body = r.get('body', '').strip()
            if not title or len(title) < 5 or not href:
                continue
            # Don't exclude a domain if it was explicitly requested in the query (e.g. site:linkedin.com)
            if any(d in href.lower() for d in EXCLUDE_DOMAINS if d not in query.lower()):
                continue
            results.append({'name': title, 'website': href, 'snippet': body[:300]})
    except Exception as e:
        print(f"Search error: {e}")
    return results


# ============ WEBSITE SCRAPING ============

def scrape_site(url, business_name=''):
    info = {'emails': [], 'linkedin': [], 'phones': [], 'owner_name': '', 'title': ''}
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        text = resp.text
        soup = BeautifulSoup(text, 'html.parser')

        title_tag = soup.select_one('title')
        if title_tag:
            info['title'] = title_tag.get_text(strip=True)[:150]

        for tag in soup(['script', 'style', 'noscript', 'form']):
            tag.decompose()
        clean_text = soup.get_text(separator=' ', strip=True)[:5000]

        info['emails'] = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', clean_text)))[:3]
        phone_matches = re.findall(r'(\+91[-\s]?\d{5}[-\s]?\d{5}|\d{5}[-\s]?\d{5})', clean_text)
        phones = [re.sub(r'[^0-9]', '', p)[-10:] for p in phone_matches]
        info['phones'] = list(set(p for p in phones if len(p) == 10))[:3]
        li_urls = re.findall(r'https?://(?:www\.)?(?:in\.)?linkedin\.com/[a-zA-Z0-9_/%\-?=]+', clean_text)
        if li_urls:
            info['linkedin'] = [li_urls[0]]

        owner_patterns = [
            r'(?:owner|proprietor|director|founder|md|ceo|manager|contact person)\s*[:\-–•]+?\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
            r'(?:Mr\.|Mrs\.|Ms\.|Shri)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s*[–\-–]\s*(?:owner|proprietor|director|founder)',
            r'(?:owned|managed|run)\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'prop[.\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        ]
        for pat in owner_patterns:
            m = re.search(pat, clean_text)
            if m:
                candidate = m.group(1).strip()
                if len(candidate.split()) >= 2 and not any(x in candidate.lower() for x in ['http', 'www.', '@', 'phone', 'limited', 'ltd', 'private']):
                    info['owner_name'] = candidate
                    break

    except Exception as e:
        print(f"Scrape error for {url}: {e}")
    return info

def deep_scrape(url, business_name=''):
    info = scrape_site(url, business_name)
    if info['phones'] or info['emails'] or info['owner_name']:
        return info
    try:
        for path in ['/contact', '/contact-us', '/contactus', '/about', '/about-us']:
            u = url.rstrip('/') + path
            info2 = scrape_site(u, business_name)
            if info2['phones'] or info2['emails'] or info2['owner_name']:
                for k in ['phones','emails','owner_name','linkedin','title']:
                    if info2[k] and not info[k]: info[k] = info2[k]
                if info['phones'] or info['owner_name']: break
    except: pass
    return info


def gemini_extract(texts, batch_size=8):
    """Use Gemini AI to extract contact info from text snippets with key rotation."""
    global _gemini_key_idx
    results = [{'phones': [], 'emails': [], 'owner_name': '', 'linkedin': []} for _ in texts]
    if not texts:
        return results

    for attempt in range(len(GEMINI_KEYS)):
        key = GEMINI_KEYS[_gemini_key_idx % len(GEMINI_KEYS)]
        _gemini_key_idx += 1

        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                prompt = """Extract Indian phone numbers, emails, owner/proprietor names, and LinkedIn URLs from these business listings.
Return a JSON array of objects with: phones (string array - 10 digits without +91), emails (string array), owner (string or null), linkedin (string or null).

Listings:\n"""
                for j, t in enumerate(batch):
                    prompt += f"{j}. {t[:200]}\n"

                import requests as req
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"
                payload = {"contents": [{"parts": [{"text": prompt + "\nReturn ONLY valid JSON array. No markdown, no code fences."}]}]}
                resp = req.post(url, json=payload, timeout=15)
                if resp.status_code == 429:
                    print(f"Gemini key {_gemini_key_idx % len(GEMINI_KEYS)} quota exceeded, trying next key")
                    break
                if resp.status_code != 200:
                    continue

                data = resp.json()
                text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                text = text.strip().removeprefix('```json').removeprefix('```').removesuffix('```')
                import json as _json
                extracted = _json.loads(text)
                for j, item in enumerate(extracted):
                    if i + j < len(results):
                        results[i+j]['phones'] = [re.sub(r'[^0-9]','',p)[-10:] for p in item.get('phones',[]) if re.sub(r'[^0-9]','',p)[-10:]]
                        results[i+j]['emails'] = item.get('emails', [])[:3]
                        results[i+j]['owner_name'] = item.get('owner', '') or ''
                        li = item.get('linkedin', '') or ''
                        results[i+j]['linkedin'] = [li] if li and 'linkedin.com' in li else []
            break
        except Exception as e:
            print(f"Gemini attempt {attempt} error: {e}")
            continue
    return results


# ============ AUTH ROUTES ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db(); cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, username))
        user = cursor.fetchone(); cursor.close(); db.close()
        if user and check_password_hash(user['password_hash'], password):
            login_user(User(user['id'], user['username'], user['email']))
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not username or not email or not password:
            flash('All fields are required', 'danger')
        elif password != confirm:
            flash('Passwords do not match', 'danger')
        else:
            db = get_db(); cursor = db.cursor()
            try:
                cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                               (username, email, generate_password_hash(password)))
                db.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except:
                flash('Username or email already exists', 'danger')
            finally:
                cursor.close(); db.close()
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ============ SIDEBAR PAGES ============

@app.route('/history')
@login_required
def history():
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT * FROM search_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 50", (current_user.id,))
    searches = cursor.fetchall(); cursor.close(); db.close()
    return render_template('history.html', username=current_user.username, searches=searches)

@app.route('/export-data')
@login_required
def export_data():
    return render_template('export.html', username=current_user.username)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    if request.method == 'POST':
        if 'clear_history' in request.form:
            db = get_db(); cursor = db.cursor()
            cursor.execute("DELETE FROM search_history WHERE user_id = %s", (current_user.id,))
            db.commit(); cursor.close(); db.close()
            flash('History cleared', 'success')
        else:
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')
            db = get_db(); cursor = db.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE id = %s", (current_user.id,))
            user = cursor.fetchone()
            if not user or not check_password_hash(user['password_hash'], current_pw):
                flash('Current password is incorrect', 'error')
            elif new_pw != confirm:
                flash('Passwords do not match', 'error')
            elif len(new_pw) < 4:
                flash('Password must be at least 4 characters', 'error')
            else:
                cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s",
                               (generate_password_hash(new_pw), current_user.id))
                db.commit()
                flash('Password updated successfully', 'success')
            cursor.close(); db.close()
        return redirect(url_for('settings_page'))
    return render_template('settings.html', username=current_user.username)


# ============ DASHBOARD ============

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)


@app.route('/api/live-search')
@login_required
def live_search():
    city = request.args.get('city', '').strip()
    business_type = request.args.get('type', '').strip()
    if not city or not business_type:
        return jsonify({'error': 'City and business type required'}), 400

    seen = set(); results = []
    for q in [f"{business_type} in {city}", f"{business_type} shops {city}", f"{business_type} dealers {city}"]:
        for r in search_web(q, max_results=6):
            key = re.sub(r'[^a-z0-9]', '', r.get('name', '').lower())[:30]
            if key and key not in seen:
                seen.add(key); results.append(r)
    return jsonify(results[:40])


@app.route('/api/bulk-scrape')
@login_required
def bulk_scrape():
    city = request.args.get('city', '').strip()
    business_type = request.args.get('type', '').strip()
    if not business_type:
        return jsonify({'error': 'Business type required'}), 400

    import concurrent.futures as cf

    # Phase 1: Maximum search angles — 14+ queries for 80+ results
    # Unquoted city → DuckDuckGo gives more results; city-filtering applied in post-step
    has_city = bool(city)
    queries = []
    if has_city:
        queries = [
            # Structured B2B/local directories (city in URL automatically)
            f"site:indiamart.com {business_type} {city}",
            f"site:justdial.com {business_type} {city}",
            f"site:sulekha.com {business_type} {city}",
            f"site:tradeindia.com {business_type} {city}",
            f"site:exportersindia.com {business_type} {city}",
            f"site:yellowpages.in {business_type} {city}",
            # LinkedIn (people + companies)
            f"site:linkedin.com/in/ {business_type} {city}",
            f"site:linkedin.com/company/ {business_type} {city}",
            # Direct web searches
            f"{business_type} in {city}",
            f"{business_type} company {city}",
            f"{business_type} supplier {city}",
            f"{business_type} manufacturer {city}",
            f"{business_type} dealer {city} contact phone",
            f"top {business_type} companies {city}",
            f"{business_type} {city} Gujarat India",
            f"{business_type} shop {city} India",
        ]
    else:
        queries = [
            f"site:indiamart.com {business_type} India",
            f"site:justdial.com {business_type} India",
            f"site:sulekha.com {business_type} India",
            f"site:tradeindia.com {business_type} India",
            f"site:exportersindia.com {business_type} India",
            f"site:yellowpages.in {business_type}",
            f"site:linkedin.com/in/ {business_type} India",
            f"site:linkedin.com/company/ {business_type} India",
            f"{business_type} company India",
            f"{business_type} supplier India",
            f"{business_type} manufacturer India contact",
            f"{business_type} dealer India phone email",
            f"top {business_type} companies India",
            f"{business_type} India directory",
        ]

    import time
    all_raw = []
    # Single backend per query with higher max_results — lite and html return same data
    for q in queries:
        try:
            res = search_web(q, max_results=50, backend='lite')
            all_raw.extend(res)
            time.sleep(0.4)
        except Exception as e:
            print(f"Search query error for '{q}': {e}")
        if len(all_raw) >= 400:
            break

    # ── City relevance SCORING (no hard drop) ──
    # City results sort to top; non-city results appear at bottom
    # This preserves 80+ total results while Rajkot ones come first
    city_lower = city.lower() if city else ''
    INDIA_DIRS = ['indiamart.com', 'justdial.com', 'sulekha.com', 'tradeindia.com',
                  'exportersindia.com', 'yellowpages.in']
    INDIAN_STATES = ['gujarat', 'maharashtra', 'rajasthan', 'punjab', 'india',
                     'delhi', 'mumbai', 'ahmedabad', 'surat', 'vadodara']

    def city_score(r):
        """Higher = more city-relevant. Used for sorting, NOT filtering."""
        score = 0
        if not city_lower:
            return 0
        url  = r.get('website', '').lower()
        snip = r.get('snippet', '').lower()
        name = r.get('name', '').lower()
        # City in URL → very strong signal (directory pages)
        if city_lower in url: score += 10
        # City in snippet
        if city_lower in snip: score += 6
        # City in title/name
        if city_lower in name: score += 4
        # Indian directory domain → trust it regardless
        if any(d in url for d in INDIA_DIRS): score += 3
        # Indian context in snippet (state, country)
        if any(s in snip for s in INDIAN_STATES): score += 2
        # Penalise obviously non-Indian results (USD, US states, etc.)
        non_india = ['washington', 'california', 'texas', 'florida', 'new york',
                     'canada', 'australia', '\$', 'zip code', 'united states']
        if any(x in snip for x in non_india): score -= 8
        return score

    seen = set(); scored = []
    for r in all_raw:
        key = re.sub(r'[^a-z0-9]', '', r.get('name', '').lower())[:30]
        if not key or key in seen:
            continue
        seen.add(key)
        scored.append((city_score(r), r))

    # Sort by city score descending, then extract
    scored.sort(key=lambda x: -x[0])
    results = [r for _, r in scored]


    def extract(r):
        raw_name = r.get('name', ''); website = r.get('website', '')
        snippet = r.get('snippet', '')[:250]
        text = snippet + ' | ' + raw_name
        
        # Clean business name by stripping common source suffixes
        name = raw_name
        for suffix in [' - IndiaMart', '| Justdial', ' - LinkedIn', ' | LinkedIn', ' - Wikipedia', ' | Wikipedia', ' - TradeIndia']:
            name = name.split(suffix)[0]
        name = name.strip()

        # Robust Indian phone extraction (mobile and landline)
        phones_raw = re.findall(r'(?:\+91|0)?[-\s]?[6-9]\d{9}|0\d{2,4}[-\s]?\d{6,8}', text)
        phones = []
        for p in phones_raw:
            cleaned = re.sub(r'[^0-9]', '', p)
            if len(cleaned) == 10:
                phones.append(cleaned)
            elif len(cleaned) > 10 and cleaned.startswith('91'):
                phones.append(cleaned[-10:])
            elif len(cleaned) > 10 and cleaned.startswith('0'):
                phones.append(cleaned[1:])
        phones = list(set(phones))[:3]

        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))[:3]
        owner = ''
        for pat in [r'(?:owner|proprietor|director|founder)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                    r'(?:Mr|Mrs|Ms|Shri|Prop)[.\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)']:
            m = re.search(pat, text[:500])
            if m and len(m.group(1).split()) >= 2: owner = m.group(1).strip(); break
        # Detect source
        source = 'Web'
        url_lower = website.lower()
        if 'indiamart.com' in url_lower: source = 'IndiaMart'
        elif 'justdial.com' in url_lower: source = 'JustDial'
        elif 'linkedin.com' in url_lower: source = 'LinkedIn'
        elif 'tradeindia.com' in url_lower: source = 'TradeIndia'
        elif 'sulekha.com' in url_lower: source = 'Sulekha'
        elif 'exportersindia.com' in url_lower: source = 'ExportersIndia'
        elif 'yellowpages' in url_lower: source = 'YellowPages'

        return {'name': name, 'website': website, 'snippet': snippet,
            'emails': emails, 'linkedin': [], 'phones': phones, 'owner_name': owner,
            'page_title': '', 'source': source}

    final = [extract(r) for r in results]

    # Phase 2: Scrape websites for real data (prioritize results with emails in snippets)
    skip_patterns = ['indiamart.com/', 'tradeindia.com/', 'justdial.com/', 'sulekha.com/']
    def should_scrape(f):
        url = f.get('website', '') or ''
        return bool(url) and not any(p in url for p in skip_patterns)

    def scrape_and_merge(f, deep=False):
        if not should_scrape(f): return f
        info = deep_scrape(f['website'], f['name']) if deep else scrape_site(f['website'], f['name'])
        for k in ['phones','emails','owner_name','linkedin']:
            if info.get(k) and not f.get(k): f[k] = info[k]
        return f

    # First: deep scrape all results that already have emails
    email_targets = [f for f in final if f.get('emails') and should_scrape(f)]
    if email_targets:
        with cf.ThreadPoolExecutor(max_workers=min(len(email_targets), 6)) as pool:
            pool.map(lambda f: scrape_and_merge(f, deep=True), email_targets)

    # Then: scrape remaining non-directory sites
    remaining = [f for f in final if not f.get('phones') and not f.get('emails') and not f.get('owner_name') and should_scrape(f)][:12]
    if remaining:
        with cf.ThreadPoolExecutor(max_workers=12) as pool:
            pool.map(lambda f: scrape_and_merge(f), remaining)

    # Phase 3: Find LinkedIn profiles (people + companies)
    try:
        ddgs = DDGS()
        for li_pattern, li_label in [('linkedin.com/in/', 'person'), ('linkedin.com/company/', 'company')]:
            li_q = f'site:{li_pattern} "{business_type}"'
            if city:
                li_q += f' "{city}"'
            for r in ddgs.text(li_q, max_results=10):
                url = r.get('href', '')
                if li_pattern in url:
                    li_name = r.get('title', '').replace(' - LinkedIn', '').replace(' | LinkedIn', '').strip()[:80]
                    snippet = r.get('body', '')[:200]
                    li_words = li_name.lower().split()[:4]
                    existing = next((f for f in final if any(w in f['name'].lower() for w in li_words if len(w) > 3)), None)
                    if existing:
                        existing['linkedin'] = list(set(existing.get('linkedin', []) + [url]))[:2]
                    else:
                        final.append({'name': li_name, 'website': url, 'snippet': snippet,
                            'emails': [], 'linkedin': [url], 'phones': [], 'owner_name': '', 'page_title': '',
                            'source': f'LinkedIn ({li_label})'})
    except Exception as e:
        print(f"LinkedIn search error: {e}")

    # Sort: city-relevance first, then contact richness
    final.sort(key=lambda f: -(
        (10 if city_lower and city_lower in (f.get('snippet','') + f.get('name','')).lower() else 0) +
        len(f.get('phones',[])) * 3 +
        len(f.get('emails',[])) * 2 +
        (2 if f.get('owner_name') else 0) +
        len(f.get('linkedin',[])) * 1
    ))

    # Save to history
    try:
        db = get_db(); cursor = db.cursor()
        cursor.execute("INSERT INTO search_history (user_id, business_type, city, result_count) VALUES (%s, %s, %s, %s)",
                       (current_user.id, business_type, city, len(final)))
        db.commit(); cursor.close(); db.close()
    except: pass

    return jsonify(final[:100])


@app.route('/api/ai-scrape')
@login_required
def ai_scrape():
    url = request.args.get('url', '').strip()
    name = request.args.get('name', '').strip()
    if not url:
        return jsonify({'error': 'URL required'}), 400
    info = scrape_site(url, name)
    return jsonify(info)


# ============ EXPORT ============

@app.route('/export/csv')
@login_required
def export_csv():
    data = request.args.get('data', '')
    try:
        businesses = json.loads(data)
    except:
        businesses = []

    if not businesses:
        flash('No data to export', 'warning')
        return redirect(url_for('dashboard'))

    output = io.StringIO()
    writer = csv.writer(output)
    has_details = 'emails' in businesses[0] if businesses else False

    if has_details:
        writer.writerow(['#', 'Business Name', 'Website', 'Email(s)', 'LinkedIn', 'Phone', 'Owner Name', 'About'])
        for i, b in enumerate(businesses, 1):
            writer.writerow([
                i, b.get('name', ''), b.get('website', ''),
                ', '.join(b.get('emails', [])), ', '.join(b.get('linkedin', [])),
                ', '.join(b.get('phones', [])), b.get('owner_name', ''),
                b.get('snippet', '')[:200],
            ])
    else:
        writer.writerow(['#', 'Business Name', 'Website', 'About'])
        for i, b in enumerate(businesses, 1):
            writer.writerow([i, b.get('name', ''), b.get('website', ''), b.get('snippet', '')[:200]])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=business_directory_export.csv'}
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, port=port, host='0.0.0.0')
