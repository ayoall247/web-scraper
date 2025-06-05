"""LinkedIn-specific content extractor."""

from typing import Dict, Optional
from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor


class LinkedInExtractor(BaseExtractor):
    """Extractor for LinkedIn blog posts and articles."""
    
    def extract(self, url: str) -> Optional[Dict]:
        """
        Extract content from LinkedIn blog posts.
        
        Args:
            url: LinkedIn blog URL
            
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
        
        # Extract author if available
        author = self._extract_author(soup)
        
        # Extract publish date if available
        publish_date = self._extract_publish_date(soup)
        
        # Extract images
        images = self.extract_images(soup)
        
        if not content:
            return None
        
        return {
            'title': title,
            'content': content,
            'author': author,
            'publish_date': publish_date,
            'images': images,
            'word_count': len(content.split()) if content else 0
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the article title."""
        # Try multiple selectors for title
        selectors = [
            'h1.blog-post-title',
            'h1[data-test-id="blog-post-title"]',
            'h1.article-title',
            'h1',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = self.clean_text(element.get_text())
                if title and len(title) > 5:  # Reasonable title length
                    return title
        
        return ""
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the main article content."""
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try multiple selectors for content
        content_selectors = [
            '.blog-post-content',
            '.article-content',
            '.post-content',
            'article',
            '.content',
            'main'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Remove navigation and sidebar elements
                for unwanted in content_element.find_all(['nav', 'aside', '.sidebar', '.navigation']):
                    unwanted.decompose()
                
                content = self.clean_text(content_element.get_text())
                if content and len(content) > 100:  # Reasonable content length
                    return content
        
        # Fallback: extract from body, filtering out common non-content elements
        body = soup.find('body')
        if body:
            # Remove common non-content elements
            for unwanted in body.find_all(['nav', 'header', 'footer', 'aside', '.menu', '.navigation', '.sidebar']):
                unwanted.decompose()
            
            content = self.clean_text(body.get_text())
            return content
        
        return ""
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract the author name."""
        author_selectors = [
            '.author-name',
            '.byline',
            '[data-test-id="author"]',
            '.post-author',
            '.article-author'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author = self.clean_text(element.get_text())
                if author:
                    return author
        
        return ""
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        """Extract the publish date."""
        date_selectors = [
            'time',
            '.publish-date',
            '.post-date',
            '[data-test-id="publish-date"]',
            '.date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                # Try datetime attribute first
                date = element.get('datetime', '')
                if not date:
                    date = self.clean_text(element.get_text())
                if date:
                    return date
        
        return ""
