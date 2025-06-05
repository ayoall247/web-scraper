#!/usr/bin/env python3
"""
Simple test script for the web scraper.
"""

import json
from scraper import WebScraper


def test_linkedin_scraper():
    """Test the scraper with the LinkedIn blog example."""
    url = "https://www.linkedin.com/blog/engineering/trust-and-safety/viral-spam-content-detection-at-linkedin"
    
    print(f"Testing scraper with URL: {url}")
    
    # Initialize scraper
    scraper = WebScraper(delay=1.0, retries=2, chunk_size=500)
    
    # Scrape the URL
    result = scraper.scrape_url(url)
    
    if result:
        print("✅ Scraping successful!")
        print(f"Title: {result['content']['title']}")
        print(f"Word count: {result['content']['word_count']}")
        print(f"Language: {result['content']['language']}")
        print(f"Site type: {result['source']['site_type']}")
        print(f"Confidence score: {result['processing']['confidence_score']}")
        print(f"Number of chunks: {len(result['processing']['chunks'])}")
        print(f"Content preview: {result['content']['text'][:200]}...")
        
        # Save to file
        with open('test_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("✅ Result saved to test_result.json")
        
    else:
        print("❌ Scraping failed!")


if __name__ == "__main__":
    test_linkedin_scraper()
