"""Base extractor class that defines the interface for all extractors."""

import requests
import time
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import Dict, List, Optional


class BaseExtractor(ABC):
    """Abstract base class for all content extractors."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page.
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    @abstractmethod
    def extract(self, url: str) -> Optional[Dict]:
        """
        Extract content from the given URL.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content or None if failed
        """
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        return text.strip()
    
    def extract_images(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract image information from the page.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of dictionaries containing image information
        """
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            alt_text = img.get('alt', '').strip()
            src = img.get('src', '').strip()
            
            # Skip if no meaningful content
            if not alt_text and not src:
                continue
                
            # Look for caption in nearby elements
            caption = ""
            parent = img.parent
            if parent:
                # Check for figcaption
                figcaption = parent.find('figcaption')
                if figcaption:
                    caption = self.clean_text(figcaption.get_text())
                # Check for nearby text that might be a caption
                elif parent.name in ['figure', 'div']:
                    text_elements = parent.find_all(text=True)
                    potential_caption = ' '.join([t.strip() for t in text_elements if t.strip()])
                    if len(potential_caption) < 200:  # Reasonable caption length
                        caption = self.clean_text(potential_caption)
            
            if alt_text or caption:
                images.append({
                    'alt_text': alt_text,
                    'caption': caption
                })
        
        return images
