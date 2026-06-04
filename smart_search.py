#!/usr/bin/env python3
"""
Smart search script that gets business results with better location accuracy
without requiring Flask, database, or Gemini API.
"""

import sys
import re
import time
from ddgs import DDGS

# Common Indian cities for detection
INDIAN_CITIES = {
    'mumbai', 'delhi', 'bangalore', 'hyderabad', 'ahmedabad', 'chennai', 'kolkata',
    'surat', 'pune', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'thane',
    'bhopal', 'visakhapatnam', 'pimpri-chinchwad', 'patna', 'vadodara', 'ghaziabad',
    'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan-dombivali',
    'vasai-virar', 'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar',
    'allahabad', 'ranchi', 'howrah', 'coimbatore', 'jabalpur', 'gwalior', 'vijayawada',
    'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur',
    'hubli–dharwad', 'tiruchirappalli', 'bareilly', 'mysore', 'tiruppur',
    'gurgaon', 'aligarh', 'jalandhar', 'bhiwandi', 'saharanpur', 'gorakhpur',
    'bikaner', 'amravati', 'noida', 'jamshedpur', 'bhilai', 'cuttack', 'firozabad',
    'kochi', 'bhavnagar', 'dehradun', 'durgapur', 'asansol', 'nanded', 'rajahmundry',
    'nellore', 'malegaon', 'siliguri', 'jalna', 'jalgaon', 'ambala', 'bilaspur',
    'shiwalik nagar', 'yamunanagar', 'sonipat', 'faridkot', 'beja'  # Added beja as it came up in search
}

def is_likely_indian_city(city_name):
    """
    Check if a city name is likely in India based on known Indian cities.
    """
    city_lower = city_name.lower().strip()
    # Direct match
    if city_lower in INDIAN_CITIES:
        return True
    # Check if it contains common Indian city patterns
    indian_patterns = ['pur', 'bad', ' nagar', 'abad', 'garh', 'puram', 'patti', 'pet']
    for pattern in indian_patterns:
        if pattern in city_lower:
            return True
    return False

def search_web(query, max_results=30):
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
            # Basic filtering - exclude some common social media sites if not explicitly searched
            exclude_domains = ['facebook.com', 'instagram.com', 'twitter.com', 'youtube.com',
                             'pinterest.com', 'linkedin.com']
            if any(domain in href.lower() for domain in exclude_domains):
                # Only exclude if the domain wasn't part of the search query
                if not any(domain in query.lower() for domain in exclude_domains):
                    continue
            results.append({
                'name': title,
                'website': href,
                'snippet': body[:200]  # Limit snippet length
            })
    except Exception as e:
        print(f"Search error for query '{query}': {e}")
    return results

def get_smart_search_queries(business_type, city):
    """
    Generate intelligent search queries based on location.
    """
    queries = []
    city_lower = city.lower().strip()
    is_indian = is_likely_indian_city(city)
    
    if is_indian:
        # India-specific searches
        queries = [
            f"site:justdial.com {business_type} {city}",
            f"site:sulekha.com {business_type} {city}",
            f"{business_type} in {city}",
            f"{business_type} company {city}",
            f"{business_type} dealer {city}",
            f"{business_type} supplier {city}",
            f"top {business_type} {city}",
            f"{business_type} {city} contact phone",
            f"{business_type} near me {city}",
            f"{business_type} {city} India",
        ]
    else:
        # International searches - avoid India-specific sites
        queries = [
            f"{business_type} in {city}",
            f"{business_type} company {city}",
            f"{business_type} {city} directory",
            f"top {business_type} {city}",
            f"{business_type} near me {city}",
            f"{business_type} {city} contact",
            f'"{business_type}" "{city}"',
            f'{business_type} "{city}"',
        ]
        
        # Add country-specific searches if we can detect the country
        # Common country mappings (could be expanded)
        country_hints = {
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
            'osaka': 'Japan',
            'sydney': 'Australia',
            'melbourne': 'Australia',
            'toronto': 'Canada',
            'vancouver': 'Canada',
        }
        
        if city_lower in country_hints:
            country = country_hints[city_lower]
            queries.extend([
                f"{business_type} in {city}, {country}",
                f"{business_type} {city} {country}",
            ])
    
    return queries

def filter_results_by_location(results, city, business_type):
    """
    Filter results to remove obvious location mismatches.
    """
    if not results:
        return results
        
    city_lower = city.lower().strip()
    filtered_results = []
    
    for result in results:
        name = result.get('name', '').lower()
        website = result.get('website', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # Skip if it's clearly a different location
        location_mismatch_indicators = [
            # If result clearly mentions a different city/region
            f' in {city_lower} ',  # Look for " in city " pattern
        ]
        
        # For Indian cities, be more lenient since Justdial might return broader results
        # For international, be stricter
        is_indian = is_likely_indian_city(city)
        
        # Check if result contains the city name (case insensitive)
        city_in_result = (
            city_lower in name or 
            city_lower in website or 
            city_lower in snippet
        )
        
        # If we can't find the city in the result, be more careful
        if not city_in_result:
            # Allow some flexibility for directory/homepage results
            if any(site in website for site in ['justdial.com', 'sulekha.com', 'yellowpages']):
                # Directory sites might not have city in every result
                filtered_results.append(result)
                continue
            # For non-directory sites, be stricter
            elif not is_indian:
                # For international searches, be more strict about location relevance
                continue
        
        filtered_results.append(result)
    
    return filtered_results

def search_for_business_results(business_type, city, target_results=80):
    """
    Search for business information with improved location accuracy.
    """
    print(f"Searching for: {business_type} in {city}")
    print(f"Targeting approximately {target_results} results...")
    
    all_results = []
    seen = set()  # To avoid duplicates
    
    # Get smart search queries
    queries = get_smart_search_queries(business_type, city)
    
    # Execute each query
    for i, query in enumerate(queries):
        if len(all_results) >= target_results * 2:  # Collect extra to account for filtering
            break
            
        print(f"  Query {i+1}/{len(queries)}: {query}")
        results = search_web(query, max_results=25)  # Get 25 per query
        
        # Add results, avoiding duplicates
        for result in results:
            # Create a unique key based on name and website
            key = (
                result.get('name', '').lower().strip(),
                result.get('website', '').lower().strip()
            )
            if key not in seen and key[0] and key[1]:
                seen.add(key)
                all_results.append(result)
                
        # Small delay to be respectful to the search service
        if i < len(queries) - 1:
            time.sleep(0.5)
    
    print(f"\nCollected {len(all_results)} unique results before filtering.")
    
    # Filter results for better location accuracy
    filtered_results = filter_results_by_location(all_results, city, business_type)
    print(f"After location filtering: {len(filtered_results)} results.")
    
    # Limit to target results
    final_results = filtered_results[:target_results]
    
    # Format and display results
    print("\n" + "="*70)
    print(f"Showing {len(final_results)} results:")
    print("="*70)
    
    for i, result in enumerate(final_results, 1):
        print(f"\n{i:2d}. {result.get('name', 'N/A')}")
        print(f"     Website: {result.get('website', 'N/A')}")
        snippet = result.get('snippet', 'N/A')
        if len(snippet) > 120:
            snippet = snippet[:120] + "..."
        print(f"     Snippet: {snippet}")
    
    return final_results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python smart_search.py <business_type> <city> [target_results]")
        print("Example: python smart_search.py \"restaurants\" \"Rajkot\" 80")
        print("Example: python smart_search.py \"restaurants\" \"Beja\" 10")
        sys.exit(1)
    
    business_type = sys.argv[1]
    city = sys.argv[2]
    target_results = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    
    search_for_business_results(business_type, city, target_results)