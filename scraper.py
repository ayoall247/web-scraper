#!/usr/bin/env python3
"""
Web Scraper for extracting content optimized for LLM/Vector Database usage.
Supports multiple site types including LinkedIn, Reddit, Twitter/X, Wikipedia, and research papers.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

from extractors.site_detector import SiteDetector
from extractors.extractor_factory import ExtractorFactory
from processors.content_processor import ContentProcessor
from utils.logger import setup_logger
from utils.file_handler import FileHandler


class WebScraper:
    """Main web scraper class that orchestrates the extraction process."""
    
    def __init__(self, delay: float = 1.0, retries: int = 3, chunk_size: int = 1000):
        self.delay = delay
        self.retries = retries
        self.chunk_size = chunk_size
        self.site_detector = SiteDetector()
        self.extractor_factory = ExtractorFactory()
        self.content_processor = ContentProcessor(chunk_size=chunk_size)
        self.logger = logging.getLogger(__name__)
        
    def scrape_url(self, url: str) -> Optional[Dict]:
        """
        Scrape a single URL and return structured data.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing extracted content or None if failed
        """
        self.logger.info(f"Starting to scrape: {url}")
        
        for attempt in range(self.retries):
            try:
                # Detect site type
                site_type = self.site_detector.detect_site_type(url)
                self.logger.info(f"Detected site type: {site_type}")
                
                # Get appropriate extractor
                extractor = self.extractor_factory.get_extractor(site_type)
                
                # Extract raw content
                raw_content = extractor.extract(url)
                if not raw_content:
                    self.logger.warning(f"No content extracted from {url}")
                    continue
                
                # Process and structure content
                processed_content = self.content_processor.process(raw_content, url, site_type)
                
                self.logger.info(f"Successfully scraped {url}")
                return processed_content
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < self.retries - 1:
                    time.sleep(self.delay * (attempt + 1))  # Exponential backoff
                    
        self.logger.error(f"Failed to scrape {url} after {self.retries} attempts")
        return None
    
    def scrape_urls(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple URLs with rate limiting.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of extracted content dictionaries
        """
        results = []
        
        for i, url in enumerate(urls):
            result = self.scrape_url(url)
            if result:
                results.append(result)
            
            # Rate limiting between requests
            if i < len(urls) - 1:
                time.sleep(self.delay)
                
        return results


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Web scraper for LLM/Vector DB content extraction")
    parser.add_argument("--url", help="Single URL to scrape")
    parser.add_argument("--urls-file", help="File containing URLs to scrape (one per line)")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--output-dir", help="Output directory for multiple files")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument("--retries", type=int, default=3, help="Number of retry attempts")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Text chunk size for processing")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Validate arguments
    if not args.url and not args.urls_file:
        logger.error("Must provide either --url or --urls-file")
        sys.exit(1)
    
    # Initialize scraper
    scraper = WebScraper(
        delay=args.delay,
        retries=args.retries,
        chunk_size=args.chunk_size
    )
    
    # Prepare URLs
    urls = []
    if args.url:
        urls = [args.url]
    elif args.urls_file:
        try:
            with open(args.urls_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.error(f"URLs file not found: {args.urls_file}")
            sys.exit(1)
    
    # Scrape URLs
    logger.info(f"Starting to scrape {len(urls)} URL(s)")
    results = scraper.scrape_urls(urls)
    
    # Save results
    file_handler = FileHandler()
    if args.output:
        file_handler.save_json(results, args.output)
        logger.info(f"Results saved to {args.output}")
    elif args.output_dir:
        file_handler.save_multiple_json(results, args.output_dir)
        logger.info(f"Results saved to {args.output_dir}")
    else:
        # Print to stdout
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    logger.info(f"Scraping completed. Successfully processed {len(results)} out of {len(urls)} URLs")


if __name__ == "__main__":
    main()
