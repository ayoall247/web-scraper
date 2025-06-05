"""Research paper-specific content extractor."""

from typing import Dict, Optional
from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor


class ResearchExtractor(BaseExtractor):
    """Extractor for research papers and academic content."""
    
    def extract(self, url: str) -> Optional[Dict]:
        """
        Extract content from research papers.
        
        Args:
            url: Research paper URL
            
        Returns:
            Dictionary containing extracted content
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Extract title
        title = self._extract_title(soup)
        
        # Extract abstract and content
        content = self._extract_content(soup)
        
        # Extract authors
        authors = self._extract_authors(soup)
        
        # Extract publish date
        publish_date = self._extract_publish_date(soup)
        
        # Extract images
        images = self.extract_images(soup)
        
        if not content:
            return None
        
        return {
            'title': title,
            'content': content,
            'author': authors,
            'publish_date': publish_date,
            'images': images,
            'word_count': len(content.split()) if content else 0
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the paper title."""
        # Try multiple selectors for title
        selectors = [
            'h1.title',
            '.paper-title',
            '.article-title',
            'h1',
            '.ltx_title'  # For arXiv LaTeX papers
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = self.clean_text(element.get_text())
                if title and len(title) > 5:
                    return title
        
        return ""
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the paper abstract and content."""
        content_parts = []
        
        # Extract abstract
        abstract_selectors = [
            '.abstract',
            '#abstract',
            '.ltx_abstract'  # arXiv
        ]
        
        for selector in abstract_selectors:
            abstract_element = soup.select_one(selector)
            if abstract_element:
                abstract_text = self.clean_text(abstract_element.get_text())
                if abstract_text and len(abstract_text) > 50:
                    content_parts.append("ABSTRACT: " + abstract_text)
                    break
        
        # Extract main content
        content_selectors = [
            '.paper-content',
            '.article-content',
            '.ltx_document',  # arXiv
            'main',
            '.content'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Remove references and citations
                for unwanted in content_element.find_all(['sup', '.citation', '.reference']):
                    unwanted.decompose()
                
                main_text = self.clean_text(content_element.get_text())
                if main_text and len(main_text) > 100:
                    content_parts.append("CONTENT: " + main_text)
                    break
        
        return '\n\n'.join(content_parts)
    
    def _extract_authors(self, soup: BeautifulSoup) -> str:
        """Extract the paper authors."""
        author_selectors = [
            '.authors',
            '.author',
            '.ltx_author'  # arXiv
        ]
        
        for selector in author_selectors:
            authors_element = soup.select_one(selector)
            if authors_element:
                authors = self.clean_text(authors_element.get_text())
                if authors:
                    return authors
        
        return ""
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        """Extract the publication date."""
        date_selectors = [
            '.publication-date',
            '.date',
            'time',
            '.ltx_dates'  # arXiv
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                date = date_element.get('datetime', '')
                if not date:
                    date = self.clean_text(date_element.get_text())
                if date:
                    return date
        
        return ""
