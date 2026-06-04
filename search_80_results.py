#!/usr/bin/env python3
"""
Search script that gets approximately 80 business results using multiple DuckDuckGo queries
without requiring Flask, database, or Gemini API.
"""

import sys
import re
import time
from ddgs import DDGS

def search_web(query, max_results=50):
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

def get_multiple_search_queries(business_type, city):
    """
    Generate multiple search queries to get more comprehensive results.
    """
    queries = []
    if city:
        queries = [
            f"site:justdial.com {business_type} {city}",
            f"{business_type} in {city}",
            f"{business_type} company {city}",
            f"{business_type} dealer {city}",
            f"{business_type} supplier {city}",
            f"top {business_type} {city}",
            f"{business_type} {city} contact phone",
            f"{business_type} near me {city}",
        ]
    else:
        queries = [
            f"site:justdial.com {business_type} India",
            f"{business_type} company India",
            f"{business_type} dealer India",
            f"{business_type} supplier India contact",
            f"top {business_type} companies India",
            f"{business_type} India directory",
        ]
    return queries

def search_for_80_results(business_type, city, target_results=80):
    """
    Search for approximately target_results business information from DuckDuckGo
    using multiple queries.
    """
    print(f"Searching for: {business_type} in {city}")
    print(f"Targeting approximately {target_results} results...")
    
    all_results = []
    seen = set()  # To avoid duplicates
    
    # Get multiple search queries
    queries = get_multiple_search_queries(business_type, city)
    
    # Execute each query
    for i, query in enumerate(queries):
        if len(all_results) >= target_results * 2:  # Collect extra to account for filtering
            break
            
        print(f"  Query {i+1}/{len(queries)}: {query}")
        results = search_web(query, max_results=30)  # Get 30 per query
        
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
    
    print(f"\nCollected {len(all_results)} unique results before limiting.")
    
    # Limit to target results
    final_results = all_results[:target_results]
    
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
        print("Usage: python search_80_results.py <business_type> <city> [target_results]")
        print("Example: python search_80_results.py \"restaurants\" \"Rajkot\" 80")
        sys.exit(1)
    
    business_type = sys.argv[1]
    city = sys.argv[2]
    target_results = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    
    search_for_80_results(business_type, city, target_results)