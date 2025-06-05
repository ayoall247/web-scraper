"""Wikipedia-specific content extractor."""

from typing import Dict, Optional
from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor


class WikipediaExtractor(BaseExtractor):
    """Extractor for Wikipedia articles."""
    
    def extract(self, url: str) -> Optional[Dict]:
        """
        Extract content from Wikipedia articles.
        
        Args:
            url: Wikipedia article URL
            
        Returns:
            Dictionary containing extracted content
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Extract title
        title = self._extract_title(soup)
        
        # Extract main content
        content = self._extract_content(soup)
        
        # Extract images
        images = self.extract_images(soup)
        
        if not content:
            return None
        
        return {
            'title': title,
            'content': content,
            'author': "",
            'publish_date': "",
            'images': images,
            'word_count': len(content.split()) if content else 0
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the Wikipedia article title."""
        # Wikipedia title is usually in h1.firstHeading
        title_element = soup.select_one('h1.firstHeading, h1#firstHeading')
        if title_element:
            return self.clean_text(title_element.get_text())
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text()
            # Remove " - Wikipedia" suffix
            if " - Wikipedia" in title:
                title = title.replace(" - Wikipedia", "")
            return self.clean_text(title)
        
        return ""
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the main Wikipedia article content."""
        # Remove unwanted elements
        unwanted_selectors = [
            'script', 'style', 'sup.reference', '.navbox', '.infobox',
            '.sidebar', '.navigation-not-searchable', '.printfooter',
            '.catlinks', '#toc', '.toc', '.mw-editsection', '.hatnote'
        ]
        
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Get the main content div
        content_element = soup.select_one('#mw-content-text .mw-parser-output')
        if not content_element:
            content_element = soup.select_one('#content')
        
        if content_element:
            # Remove remaining unwanted elements
            for unwanted in content_element.find_all(['table', 'div.navbox', 'div.infobox']):
                unwanted.decompose()
            
            # Extract paragraphs and headings
            content_parts = []
            for element in content_element.find_all(['p', 'h2', 'h3', 'h4']):
                text = self.clean_text(element.get_text())
                if text and len(text) > 10:  # Filter out very short text
                    content_parts.append(text)
            
            return '\n\n'.join(content_parts)
        
        return ""
