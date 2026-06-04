#!/usr/bin/env python3
"""
Final business search script that gets approximately 80 relevant business results
for both Indian and international cities without requiring Flask, database, or Gemini API.
"""

import sys
import re
import time
from ddgs import DDGS

def is_likely_indian_city(city_name):
    """
    Improved detection for Indian cities.
    """
    city_lower = city_name.lower().strip()
    
    # Common Indian cities (major ones)
    major_indian_cities = {
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
        'yamunanagar', 'sonipat', 'faridkot', 'beja'  # Beja is also in India (though more known in Portugal)
    }
    
    # Direct match
    if city_lower in major_indian_cities:
        return True
        
    # Check for common Indian city suffixes/patterns
    indian_patterns = [
        'pur', 'bad', ' nagar', 'abad', 'garh', 'puram', 'patti', 'pet', 
        'pur', 'pura', 'bad', 'pur', 'pur', ' nagar', 'abad', 'garh'
    ]
    
    for pattern in indian_patterns:
        if pattern in city_lower:
            return True
            
    # If it's a single word that's not obviously European/Western, lean toward Indian
    # This is a heuristic - not perfect but helps
    if len(city_lower.split()) == 1 and len(city_lower) > 3:
        # Common Western city indicators
        western_indicators = ['ville', 'berg', 'bourg', 'furt', 'ham', 'ton', 'ford', 'mouth', 'bury', 'cester', 'caster']
        if not any(indicator in city_lower for indicator in western_indicators):
            # If it doesn't look Western, assume Indian for better local results
            # But don't be too aggressive - if we get bad results, user can refine
            pass
    
    return False

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
            # Filter out obvious junk and homepages unless they're directory sites
            skip_patterns = [
                'facebook.com/', 'instagram.com/', 'twitter.com/', 'youtube.com/',
                'pinterest.com/', 'linkedin.com/', 'wikipedia.org/',
                'google.com/search', 'justdial.com/$',  # Justdial homepage
            ]
            if any(pattern in href.lower() for pattern in skip_patterns):
                # Allow directory homepages but not deep links to social media/etc
                if 'justdial.com' in href and href.lower().count('/') <= 3:  # Allow justdial.com, justdial.com/city, etc
                    pass  # Allow Justdial directory pages
                elif 'sulekha.com' in href and href.lower().count('/') <= 3:
                    pass  # Allow Sulekha directory pages
                else:
                    continue  # Skip other homepages/junk
                    
            results.append({
                'name': title,
                'website': href,
                'snippet': body[:200]
            })
    except Exception as e:
        print(f"Search error for query '{query}': {e}")
    return results

def get_search_strategy(business_type, city):
    """
    Determine the best search strategy based on location.
    """
    city_lower = city.lower().strip()
    is_indian = is_likely_indian_city(city)
    
    if is_indian:
        # India-focused strategy
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
        ]
    else:
        # International strategy - avoid Indian directories unless specifically relevant
        return [
            f"{business_type} in {city}",
            f'"{business_type}" "{city}"',
            f"{business_type} company {city}",
            f"{business_type} {city} directory",
            f"top {business_type} {city}",
            f"{business_type} near me {city}",
            f"{business_type} {city} contact",
            f"{business_type} {city} address",
            f'"{business_type}" {city} phone',
            f'{business_type} "{city}"',
        ]

def filter_and_rank_results(results, city, business_type):
    """
    Filter results for relevance and rank them.
    """
    if not results:
        return results
        
    city_lower = city.lower().strip()
    business_lower = business_type.lower().strip()
    is_indian = is_likely_indian_city(city)
    
    scored_results = []
    
    for result in results:
        name = result.get('name', '').lower()
        website = result.get('website', '').lower()
        snippet = result.get('snippet', '').lower()
        
        score = 0
        
        # City relevance (most important)
        if city_lower in name:
            score += 10
        if city_lower in website:
            score += 8
        if city_lower in snippet:
            score += 6
            
        # Business type relevance
        if business_lower in name:
            score += 8
        if business_lower in snippet:
            score += 4
            
        # Prefer actual business listings over directory homepages
        if 'justdial.com' in website or 'sulekha.com' in website:
            # These are good for Indian searches - check if it's a specific listing
            if city_lower in website and business_lower in website:
                score += 5  # Specific listing
            elif city_lower in website:
                score += 3  # City-specific directory
            else:
                score += 1  # General directory (less preferred)
        elif any(domain in website for domain in ['.com', '.org', '.net']):
            # Regular business websites get bonus
            score += 4
            
        # Penalize obvious irrelevant results
        irrelevant_patterns = [
            'wikipedia', 'facebook.com/', 'instagram.com/', 'twitter.com/',
            'linkedin.com/', 'youtube.com/', 'pinterest.com/',
            'google.com/search', 'justdial.com/$'  # Justdial homepage only
        ]
        for pattern in irrelevant_patterns:
            if pattern in website:
                if pattern == 'justdial.com/$' and website == 'https://www.justdial.com/':
                    score -= 5  # Penalize Justdial homepage
                elif pattern != 'justdial.com/$':
                    score -= 10  # Heavy penalty for social media, etc
                    
        # Boost for having contact-like information in snippet
        contact_indicators = ['phone', 'contact', 'address', 'email', 'call', '+91', 'tel:']
        for indicator in contact_indicators:
            if indicator in snippet:
                score += 2
                break
                
        # Only include if it has some relevance
        if score > 0:
            scored_results.append((score, result))
    
    # Sort by score (descending) and return just the results
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [result for score, result in scored_results]

def search_for_businesses(business_type, city, target_results=80):
    """
    Main search function to get business results.
    """
    print(f"🔍 Searching for: {business_type} in {city}")
    print(f"🎯 Target: {target_results} results")
    print("-" * 50)
    
    all_results = []
    seen = set()  # To avoid duplicates by name+website
    
    # Get appropriate search strategy
    queries = get_search_strategy(business_type, city)
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
    filtered_results = filter_and_rank_results(all_results, city, business_type)
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
            
        print(f"\n{i:2d}. {name}")
        print(f"    🌐 {website}")
        print(f"    📄 {snippet}")
    
    return final_results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python final_business_search.py <business_type> <city> [target_results]")
        print("Examples:")
        print("  python final_business_search.py \"restaurants\" \"Rajkot\" 80")
        print("  python final_business_search.py \"hotels\" \"Beja\" 10")
        print("  python final_business_search.py \"doctors\" \"Mumbai\" 50")
        sys.exit(1)
    
    business_type = sys.argv[1]
    city = sys.argv[2]
    target_results = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    
    search_for_businesses(business_type, city, target_results)