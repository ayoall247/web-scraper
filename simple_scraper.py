#!/usr/bin/env python3
"""
Simplified web scraper for LLM/Vector Database usage.
A streamlined single-file version with core functionality.
"""

import argparse
import json
import logging
import sys
import time
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from readability import Document

try:
    from langdetect import detect
except ImportError:
    detect = None


class SimpleScraper:
    """Simplified web scraper with essential functionality."""
    
    def __init__(self, delay: float = 1.0, retries: int = 3, chunk_size: int = 1000):
        self.delay = delay
        self.retries = retries
        self.chunk_size = chunk_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Site patterns for detection
        self.site_patterns = {
            'linkedin': [r'linkedin\.com'],
            'reddit': [r'reddit\.com', r'redd\.it'],
            'twitter': [r'twitter\.com', r'x\.com'],
            'wikipedia': [r'wikipedia\.org'],
            'research': [r'arxiv\.org', r'researchgate\.net', r'ieee\.org', r'acm\.org']
        }
    
    def detect_site_type(self, url: str) -> str:
        """Detect the type of site based on URL."""
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            for site_type, patterns in self.site_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, domain):
                        return site_type
            return 'generic'
        except:
            return 'generic'
    
    def extract_content(self, url: str) -> Optional[Dict]:
        """Extract content from URL using site-specific or generic methods."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            site_type = self.detect_site_type(url)
            
            # Site-specific extraction
            if site_type == 'linkedin':
                return self._extract_linkedin(soup, url)
            elif site_type == 'wikipedia':
                return self._extract_wikipedia(soup, url)
            else:
                return self._extract_generic(response.content, url)
                
        except Exception as e:
            logging.error(f"Error extracting from {url}: {e}")
            return None
    
    def _extract_linkedin(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract LinkedIn content."""
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.get_text().strip() if title_elem else ""
        
        # Extract main content
        content_selectors = ['article', '.content', 'main', 'body']
        content = ""
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                content = elem.get_text().strip()
                break
        
        return self._structure_content(title, content, url, 'linkedin')
    
    def _extract_wikipedia(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract Wikipedia content."""
        # Remove unwanted elements
        unwanted = ['script', 'style', '.navbox', '.infobox', '#toc', '.reference']
        for selector in unwanted:
            for elem in soup.select(selector):
                elem.decompose()
        
        # Extract title
        title_elem = soup.select_one('h1.firstHeading') or soup.find('title')
        title = title_elem.get_text().strip() if title_elem else ""
        if " - Wikipedia" in title:
            title = title.replace(" - Wikipedia", "")
        
        # Extract content
        content_elem = soup.select_one('#mw-content-text') or soup.find('body')
        content = content_elem.get_text().strip() if content_elem else ""
        
        return self._structure_content(title, content, url, 'wikipedia')
    
    def _extract_generic(self, html_content: bytes, url: str) -> Dict:
        """Extract content using readability."""
        try:
            doc = Document(html_content)
            title = doc.title()
            content_html = doc.summary()
            soup = BeautifulSoup(content_html, 'html.parser')
            content = soup.get_text().strip()
            
            return self._structure_content(title, content, url, 'generic')
        except Exception as e:
            logging.error(f"Generic extraction failed: {e}")
            return None
    
    def _structure_content(self, title: str, content: str, url: str, site_type: str) -> Dict:
        """Structure extracted content for LLM/Vector DB usage."""
        # Clean text
        title = ' '.join(title.split()).strip()
        content = ' '.join(content.split()).strip()
        
        # Generate ID
        content_id = hashlib.md5(f"{url}_{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        # Extract domain
        domain = urlparse(url).netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Detect language
        language = "en"
        if detect and content:
            try:
                language = detect(content)
            except:
                pass
        
        # Extract keywords
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [w for w in words if w not in stop_words]
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        tags = [word for word, freq in top_keywords]
        
        # Create chunks
        words = content.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            chunks.append({
                "text": chunk_text,
                "position": len(chunks) + 1,
                "char_count": len(chunk_text)
            })
        
        # Calculate confidence
        confidence = 0.3 if content else 0.0
        if title: confidence += 0.2
        if len(words) > 100: confidence += 0.3
        if len(words) > 500: confidence += 0.2
        
        return {
            "id": content_id,
            "source": {
                "url": url,
                "domain": domain,
                "site_type": site_type,
                "scraped_at": datetime.utcnow().isoformat() + "Z"
            },
            "content": {
                "title": title,
                "text": content,
                "word_count": len(words),
                "language": language,
                "images": []  # Simplified - no image extraction
            },
            "metadata": {
                "author": "",
                "publish_date": "",
                "tags": tags,
                "content_type": "article"
            },
            "processing": {
                "extraction_method": "site_specific" if site_type != "generic" else "generic",
                "confidence_score": min(confidence, 1.0),
                "chunks": chunks
            }
        }
    
    def scrape_url(self, url: str) -> Optional[Dict]:
        """Scrape a single URL with retry logic."""
        for attempt in range(self.retries):
            try:
                result = self.extract_content(url)
                if result:
                    return result
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.retries - 1:
                    time.sleep(self.delay * (attempt + 1))
        return None
    
    def scrape_urls(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs with rate limiting."""
        results = []
        for i, url in enumerate(urls):
            result = self.scrape_url(url)
            if result:
                results.append(result)
            if i < len(urls) - 1:
                time.sleep(self.delay)
        return results


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Simplified web scraper for LLM/Vector DB")
    parser.add_argument("--url", help="Single URL to scrape")
    parser.add_argument("--urls-file", help="File containing URLs (one per line)")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--output-dir", help="Output directory for multiple files")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
    parser.add_argument("--retries", type=int, default=3, help="Number of retry attempts")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Text chunk size")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    if not args.url and not args.urls_file:
        print("Error: Must provide either --url or --urls-file")
        sys.exit(1)
    
    # Initialize scraper
    scraper = SimpleScraper(
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
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            print(f"Error: URLs file not found: {args.urls_file}")
            sys.exit(1)
    
    # Scrape URLs
    logging.info(f"Starting to scrape {len(urls)} URL(s)")
    results = scraper.scrape_urls(urls)
    
    # Save results
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {args.output}")
    elif args.output_dir:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        for i, result in enumerate(results):
            filename = f"{result['id']}.json"
            filepath = Path(args.output_dir) / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {args.output_dir}")
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    logging.info(f"Completed. Successfully processed {len(results)} out of {len(urls)} URLs")


if __name__ == "__main__":
    main()
