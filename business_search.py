#!/usr/bin/env python3
"""
Business search script that gets relevant results for any city worldwide
without requiring Flask, database, or Gemini API.
"""

import sys
import re
import time
from ddgs import DDGS

# Comprehensive list of known cities to avoid misclassification
KNOWN_INDIAN_CITIES = {
    'mumbai', 'delhi', 'bangalore', 'hyderabad', 'ahmedabad', 'chennai', 'kolkata',
    'surat', 'pune', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'thane',
    'bhopal', 'visakhapatnam', 'pimpri-chinchwad', 'patna', 'vadodara', 'ghaziabad',
    'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan-dombivali',
    'vasai-virar', 'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar',
    'allahabad', 'ranchi', 'howrah', 'coimbatore', 'jabalpur', 'gwalior', 'vijayawada',
    'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur',
    'hubli-dharwad', 'tiruchirappalli', 'bareilly', 'mysore', 'tiruppur',
    'gurgaon', 'aligarh', 'jalandhar', 'bhiwandi', 'saharanpur', 'gorakhpur',
    'bikaner', 'amravati', 'noida', 'jamshedpur', 'bhilai', 'cuttack', 'firozabad',
    'kochi', 'bhavnagar', 'dehradun', 'durgapur', 'asansol', 'nanded', 'rajahmundry',
    'nellore', 'malegaon', 'siliguri', 'jalna', 'jalgaon', 'ambala', 'bilaspur',
    'yamunanagar', 'sonipat', 'faridkot'  # Removed 'beja' as it's primarily known as a Portuguese city
}

KNOWN_INTERNATIONAL_CITIES = {
    # Portugal
    'lisbon', 'porto', 'beja', 'braga', 'setubal', 'coimbra', 'faro',
    # Spain
    'madrid', 'barcelona', 'valencia', 'seville', 'zaragoza', 'malaga', 'bilbao',
    # France
    'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg',
    # Italy
    'rome', 'milan', 'naples', 'turin', 'palermo', 'genoa', 'bologna',
    # Germany
    'berlin', 'hamburg', 'munich', 'cologne', 'frankfurt', 'stuttgart',
    # UK
    'london', 'birmingham', 'manchester', 'glasgow', 'liverpool', 'leeds',
    # Others
    'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
    'toronto', 'vancouver', 'montreal', 'ottawa',
    'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
    'tokyo', 'osaka', 'kyoto', 'yokohama',
    'beijing', 'shanghai', 'guangzhou', 'shenzhen',
    'dubai', 'abu dhabi',
    'johannesburg', 'cape town',
    'rio de janeiro', 'sao paulo',
    'mexico city', 'cancun',
    'buenos aires',
}

def is_known_city(city_name, city_dict):
    """Check if city is in a known cities dictionary."""
    city_lower = city_name.lower().strip()
    # Direct match
    if city_lower in city_dict:
        return True
    # Check common variations (remove spaces, hyphens)
    normalized = re.sub(r'[\s\-]+', '', city_lower)
    for known_city in city_dict:
        if re.sub(r'[\s\-]+', '', known_city) == normalized:
            return True
    return False

def get_city_type(city_name):
    """
    Determine if a city is known to be Indian, International, or unknown.
    Returns: 'indian', 'international', or 'unknown'
    """
    city_lower = city_name.lower().strip()
    
    # Check against known cities first
    if is_known_city(city_name, KNOWN_INDIAN_CITIES):
        return 'indian'
    if is_known_city(city_name, KNOWN_INTERNATIONAL_CITIES):
        return 'international'
    
    # For unknown cities, use heuristics but be conservative
    # Check for strong Indian indicators
    strong_indian_patterns = [
        'pur', 'bad', ' nagar', 'abad', 'garh', 'puram', 'petti', 'pet',
        'pur', 'pura', 'pur', 'pur'
    ]
    
    # Check for strong international indicators
    strong_international_patterns = [
        'ville', 'berg', 'bourg', 'furt', 'ham', 'ton', 'ford', 'mouth', 
        'bury', 'cester', 'caster', 'stein', 'bruck', 'heim', 'port',
        'side', 'mouth', 'ford'
    ]
    
    indian_score = sum(1 for pattern in strong_indian_patterns if pattern in city_lower)
    international_score = sum(1 for pattern in strong_international_patterns if pattern in city_lower)
    
    # If stronglyindicates one over the other, classify accordingly
    if indian_score > international_score and indian_score >= 2:
        return 'indian'
    elif international_score > indian_score and international_score >= 2:
        return 'international'
    else:
        # Default to international for ambiguous cases to avoid forcing Indian results
        # on clearly international cities like Beja
        return 'international'

def search_web(query, max_results=25):
    """
    Search DuckDuckGo for businesses and return basic info.
    """
    results = []
    try:
        ddgs = DDGS()
        for r in ddgs.text(query, max_results=max_results, backend='lite'):
            title = r.get('title', '').strip()
            href = r.get('href', '').strip()
            body = r.get('body', '').strip()
            if not title or len(title) < 5 or not href:
                continue
            # Filter out obvious junk and social media homepages
            skip_patterns = [
                'facebook.com/', 'instagram.com/', 'twitter.com/', 'youtube.com/',
                'pinterest.com/', 'linkedin.com/', 'wikipedia.org/',
                'google.com/search'
            ]
            if any(pattern in href.lower() for pattern in skip_patterns):
                continue
                
            results.append({
                'name': title,
                'website': href,
                'snippet': body[:200]
            })
    except Exception as e:
        print(f"Search error for query '{query}': {e}")
    return results

def get_search_queries(business_type, city, city_type):
    """
    Generate appropriate search queries based on city type.
    """
    city_lower = city.lower().strip()
    business_lower = business_type.lower().strip()
    
    if city_type == 'indian':
        # India-focused strategy - use Indian directories
        return [
            f"site:justdial.com {business_type} {city}",
            f"site:sulekha.com {business_type} {city}",
            f"{business_type} in {city} contact phone",
            f"{business_type} dealers {city}",
            f"{business_type} suppliers {city}",
            f"top {business_type} {city} India",
            f"{business_type} company {city}",
            f"{business_type} near me {city}",
            f'"{business_type}" "{city}" contact',
            f"{business_type} {city} address phone",
            f"{business_type} {city} India",
            f"best {business_type} {city}",
        ]
    else:
        # International strategy - avoid Indian directories unless specifically relevant
        queries = [
            f'"{business_type}" "{city}"',
            f"{business_type} in {city}",
            f"{business_type} company {city}",
            f"{business_type} {city} directory",
            f"top {business_type} {city}",
            f"{business_type} near me {city}",
            f"{business_type} {city} contact",
            f"{business_type} {city} address",
            f'"{business_type}" {city} phone',
            f'{business_type} "{city}"',
            f"{business_type} {city} reviews",
            f"best {business_type} {city}",
        ]
        
        # Add country-specific searches for known international cities
        # This helps when the city is ambiguous
        country_map = {
            'beja': 'Portugal',
            'lisbon': 'Portugal', 
            'porto': 'Portugal',
            'madrid': 'Spain',
            'barcelona': 'Spain',
            'rome': 'Italy',
            'milan': 'Italy',
            'paris': 'France',
            'london': 'UK',
            'berlin': 'Germany',
            'tokyo': 'Japan',
            'sydney': 'Australia',
            'toronto': 'Canada',
        }
        
        if city_lower in country_map:
            country = country_map[city_lower]
            queries.extend([
                f"{business_type} in {city}, {country}",
                f"{business_type} {city} {country}",
                f'"{business_type}" "{city}" {country}',
            ])
        
        return queries

def filter_and_rank_results(results, city, business_type, city_type):
    """
    Filter results for relevance and rank them, being careful about location.
    """
    if not results:
        return results
        
    city_lower = city.lower().strip()
    business_lower = business_type.lower().strip()
    
    scored_results = []
    
    for result in results:
        name = result.get('name', '').lower()
        website = result.get('website', '').lower()
        snippet = result.get('snippet', '').lower()
        
        score = 0
        
        # City relevance (most important)
        city_in_name = city_lower in name
        city_in_website = city_lower in website
        city_in_snippet = city_lower in snippet
        
        if city_in_name:
            score += 15
        if city_in_website:
            score += 12
        if city_in_snippet:
            score += 8
            
        # Business type relevance
        if business_lower in name:
            score += 10
        if business_lower in snippet:
            score += 5
            
        # Source credibility
        trusted_sites = ['justdial.com', 'sulekha.com', 'yellowpages', 'yelp', 'tripadvisor',
                        'zomato', 'swiggy', 'foodpanda', 'google.com/maps']
        if any(site in website for site in trusted_sites):
            score += 6
            # Bonus for directory sites having specific listings
            business_in_name = business_lower in name
            if any(directory in website for directory in ['justdial.com', 'sulekha.com']):
                if city_in_website and business_in_name:
                    score += 4  # Specific relevant listing
                    
        # Penalize obviously wrong locations
        # For international cities, penalize strong Indian indicators unless city is known to be Indian
        if city_type == 'international':
            strong_indian_markers = ['gujarat', 'maharashtra', 'punjab', 'rajasthan', 
                                   'karnataka', 'tamil nadu', 'kerala', 'west bengal']
            india_matches = sum(1 for marker in strong_indian_markers if marker in snippet)
            if india_matches > 0 and not city_in_snippet:  # Only penalize if city not mentioned
                score -= india_matches * 3
                
        # Boost for having contact-like information in snippet
        contact_indicators = ['phone', 'contact', 'address', 'email', 'call', 'tel:', '+91']
        for indicator in contact_indicators:
            if indicator in snippet:
                score += 3
                break
                
        # Only include if it has meaningful relevance
        if score > 0:
            scored_results.append((score, result))
    
    # Sort by score (descending) and return just the results
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [result for score, result in scored_results]

def search_for_businesses(business_type, city, target_results=80):
    """
    Main search function to get business results for any city worldwide.
    """
    print(f"🔍 Searching for: {business_type} in {city}")
    print(f"🎯 Target: {target_results} results")
    print("-" * 50)
    
    # Determine city type
    city_type = get_city_type(city)
    print(f"🏙️  City classification: {city_type.upper()}")
    
    all_results = []
    seen = set()  # To avoid duplicates by name+website
    
    # Get appropriate search strategy
    queries = get_search_queries(business_type, city, city_type)
    print(f"📝 Using {len(queries)} search queries...")
    
    # Execute each query
    for i, query in enumerate(queries, 1):
        if len(all_results) >= target_results * 2:  # Get extra for filtering
            break
            
        print(f"  [{i}/{len(queries)}] {query}")
        results = search_web(query, max_results=20)
        
        # Add unique results
        for result in results:
            # Create uniqueness key
            key = (
                result.get('name', '').lower().strip(),
                result.get('website', '').lower().strip()
            )
            if key not in seen and key[0] and key[1]:
                seen.add(key)
                all_results.append(result)
        
        # Be respectful to the search service
        if i < len(queries):
            time.sleep(0.3)
    
    print(f"\n📊 Collected {len(all_results)} raw results...")
    
    # Filter and rank for relevance
    filtered_results = filter_and_rank_results(all_results, city, business_type, city_type)
    print(f"✅ After filtering: {len(filtered_results)} relevant results")
    
    # Limit to target
    final_results = filtered_results[:target_results]
    
    # Display results
    print("\n" + "="*70)
    print(f"📋 SHOWING {len(final_results)} RESULTS")
    print("="*70)
    
    if not final_results:
        print("❌ No results found. Try different search terms.")
        return []
    
    for i, result in enumerate(final_results, 1):
        name = result.get('name', 'N/A')
        website = result.get('website', 'N/A')
        snippet = result.get('snippet', 'N/A')
        
        # Truncate snippet for display
        if len(snippet) > 130:
            snippet = snippet[:130] + "..."
            
        # Add relevance indicator
        relevance_indicators = []
        city_lower = city.lower().strip()
        if city_lower in result.get('name', '').lower():
            relevance_indicators.append("📍")
        if any(indicator in result.get('snippet', '').lower() 
               for indicator in ['phone', 'contact', 'address']):
            relevance_indicators.append("📞")
            
        indicator_str = " " + " ".join(relevance_indicators) if relevance_indicators else ""
        
        print(f"\n{i:2d}. {name}{indicator_str}")
        print(f"    🌐 {website}")
        print(f"    📄 {snippet}")
    
    return final_results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python business_search.py <business_type> <city> [target_results]")
        print("Examples:")
        print("  python business_search.py \"restaurants\" \"Rajkot\" 80")
        print("  python business_search.py \"restaurants\" \"Beja\" 10")
        print("  python business_search.py \"hotels\" \"Lisbon\" 15")
        print("  python business_search.py \"doctors\" \"Mumbai\" 50")
        sys.exit(1)
    
    business_type = sys.argv[1]
    city = sys.argv[2]
    target_results = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    
    search_for_businesses(business_type, city, target_results)