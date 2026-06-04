#!/usr/bin/env python3
"""
Standalone simple search script that uses DuckDuckGo to get 10 business results
without requiring Flask, database, or Gemini API.
"""

import sys
import re
from ddgs import DDGS

def search_web(query, max_results=10):
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
        print(f"Search error: {e}")
    return results

def simple_search(business_type, city, max_results=80):
    """
    Simple search that returns basic business information from DuckDuckGo
    """
    print(f"Searching for: {business_type} in {city}")
    print(f"Requesting {max_results} results...")
    
    # Use our search function
    results = search_web(f"{business_type} in {city}", max_results=max_results)
    
    # Format and display results
    print("\n" + "="*60)
    print(f"Found {len(results)} results:")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('name', 'N/A')}")
        print(f"   Website: {result.get('website', 'N/A')}")
        snippet = result.get('snippet', 'N/A')
        if len(snippet) > 100:
            snippet = snippet[:100] + "..."
        print(f"   Snippet: {snippet}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simple_search_standalone.py <business_type> <city> [max_results]")
        print("Example: python simple_search_standalone.py \"restaurants\" \"Rajkot\" 10")
        sys.exit(1)
    
    business_type = sys.argv[1]
    city = sys.argv[2]
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    simple_search(business_type, city, max_results)