#!/usr/bin/env python3
"""
Example usage of the web scraper for different types of content.
"""

from scraper import WebScraper
import json


def main():
    """Demonstrate scraper usage with different site types."""
    
    # Initialize scraper with custom settings
    scraper = WebScraper(
        delay=2.0,      # 2 second delay between requests
        retries=3,      # 3 retry attempts
        chunk_size=800  # 800 word chunks
    )
    
    # Example URLs for different site types
    test_urls = [
        "https://www.linkedin.com/blog/engineering/trust-and-safety/viral-spam-content-detection-at-linkedin",
        "https://en.wikipedia.org/wiki/Machine_learning"
    ]
    
    print("🚀 Starting web scraper example...")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📄 Scraping URL {i}/{len(test_urls)}: {url}")
        
        result = scraper.scrape_url(url)
        
        if result:
            print(f"✅ Success!")
            print(f"   Title: {result['content']['title']}")
            print(f"   Site Type: {result['source']['site_type']}")
            print(f"   Word Count: {result['content']['word_count']}")
            print(f"   Language: {result['content']['language']}")
            print(f"   Confidence: {result['processing']['confidence_score']:.2f}")
            print(f"   Chunks: {len(result['processing']['chunks'])}")
            print(f"   Tags: {', '.join(result['metadata']['tags'][:5])}")
            
            # Save individual result
            filename = f"example_result_{i}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"   💾 Saved to {filename}")
            
        else:
            print(f"❌ Failed to scrape {url}")
    
    print(f"\n🎉 Example completed!")


if __name__ == "__main__":
    main()
