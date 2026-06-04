#!/usr/bin/env python3
"""
Simple search script that uses DuckDuckGo to get 10 business results
without Gemini API or complex processing.
"""

import sys
import os

# Add the current directory to Python path to import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import search_web

def simple_search(business_type, city, max_results=10):
    """
    Simple search that returns basic business information from DuckDuckGo
    """
    print(f"Searching for: {business_type} in {city}")
    print(f"Requesting {max_results} results...")
    
    # Use the existing search_web function from app.py
    results = search_web(f"{business_type} in {city}", max_results=max_results)
    
    # Format and display results
    print("\n" + "="*60)
    print(f"Found {len(results)} results:")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('name', 'N/A')}")
        print(f"   Website: {result.get('website', 'N/A')}")
        print(f"   Snippet: {result.get('snippet', 'N/A')[:100]}...")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simple_search.py <business_type> <city> [max_results]")
        print("Example: python simple_search.py \"restaurants\" \"Rajkot\" 10")
        sys.exit(1)
    
    business_type = sys.argv[1]
    city = sys.argv[2]
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    simple_search(business_type, city, max_results)