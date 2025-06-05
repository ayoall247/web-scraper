"""Generic content extractor using readability algorithms."""

from typing import Dict, Optional
from bs4 import BeautifulSoup
from readability import Document
from .base_extractor import BaseExtractor


class GenericExtractor(BaseExtractor):
    """Generic extractor that works on any website using readability algorithms."""
    
    def extract(self, url: str) -> Optional[Dict]:
        """
        Extract content from any website using readability.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            # Fetch raw HTML
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Use readability to extract main content
            doc = Document(response.content)
            
            # Get the main content
            content_html = doc.summary()
            title = doc.title()
            
            # Parse the extracted content
            soup = BeautifulSoup(content_html, 'html.parser')
            
            # Clean and extract text
            content = self.clean_text(soup.get_text())
            
            # Extract images from the cleaned content
            images = self.extract_images(soup)
            
            if not content or len(content) < 50:
                return None
            
            return {
                'title': self.clean_text(title) if title else "",
                'content': content,
                'author': "",
                'publish_date': "",
                'images': images,
                'word_count': len(content.split()) if content else 0
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None
