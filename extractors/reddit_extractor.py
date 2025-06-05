"""Reddit-specific content extractor."""

from typing import Dict, Optional
from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor


class RedditExtractor(BaseExtractor):
    """Extractor for Reddit posts and comments."""
    
    def extract(self, url: str) -> Optional[Dict]:
        """
        Extract content from Reddit posts.
        
        Args:
            url: Reddit post URL
            
        Returns:
            Dictionary containing extracted content
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Extract title
        title = self._extract_title(soup)
        
        # Extract main content (post text + top comments)
        content = self._extract_content(soup)
        
        # Extract author
        author = self._extract_author(soup)
        
        # Extract images
        images = self.extract_images(soup)
        
        if not content:
            return None
        
        return {
            'title': title,
            'content': content,
            'author': author,
            'publish_date': "",
            'images': images,
            'word_count': len(content.split()) if content else 0
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the Reddit post title."""
        # Try multiple selectors for title
        selectors = [
            'h1[data-test-id="post-content-title"]',
            'h1.title',
            'h1',
            '[data-click-id="title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = self.clean_text(element.get_text())
                if title and len(title) > 5:
                    return title
        
        return ""
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the Reddit post content and top comments."""
        content_parts = []
        
        # Extract post content
        post_selectors = [
            '[data-test-id="post-content"]',
            '.usertext-body',
            '.md'
        ]
        
        for selector in post_selectors:
            post_element = soup.select_one(selector)
            if post_element:
                post_text = self.clean_text(post_element.get_text())
                if post_text and len(post_text) > 10:
                    content_parts.append("POST: " + post_text)
                    break
        
        # Extract top comments (limit to first few)
        comment_selectors = [
            '.Comment',
            '.comment',
            '[data-test-id="comment"]'
        ]
        
        comments_found = 0
        max_comments = 5  # Limit number of comments
        
        for selector in comment_selectors:
            comments = soup.select(selector)
            for comment in comments[:max_comments]:
                comment_text = self.clean_text(comment.get_text())
                if comment_text and len(comment_text) > 20:  # Filter very short comments
                    content_parts.append("COMMENT: " + comment_text)
                    comments_found += 1
                    if comments_found >= max_comments:
                        break
            if comments_found >= max_comments:
                break
        
        return '\n\n'.join(content_parts)
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract the Reddit post author."""
        author_selectors = [
            '[data-test-id="post-author"]',
            '.author',
            '.username'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author = self.clean_text(element.get_text())
                if author:
                    return author
        
        return ""
