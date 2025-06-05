"""Twitter/X-specific content extractor."""

from typing import Dict, Optional
from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor


class TwitterExtractor(BaseExtractor):
    """Extractor for Twitter/X posts and threads."""
    
    def extract(self, url: str) -> Optional[Dict]:
        """
        Extract content from Twitter/X posts.
        
        Args:
            url: Twitter/X post URL
            
        Returns:
            Dictionary containing extracted content
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Extract content
        content = self._extract_content(soup)
        
        # Extract author
        author = self._extract_author(soup)
        
        # Extract images
        images = self.extract_images(soup)
        
        if not content:
            return None
        
        return {
            'title': f"Tweet by {author}" if author else "Tweet",
            'content': content,
            'author': author,
            'publish_date': "",
            'images': images,
            'word_count': len(content.split()) if content else 0
        }
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the tweet content and thread."""
        content_parts = []
        
        # Try multiple selectors for tweet content
        tweet_selectors = [
            '[data-testid="tweetText"]',
            '.tweet-text',
            '.js-tweet-text',
            '.TweetTextSize'
        ]
        
        for selector in tweet_selectors:
            tweets = soup.select(selector)
            for tweet in tweets:
                tweet_text = self.clean_text(tweet.get_text())
                if tweet_text and len(tweet_text) > 5:
                    content_parts.append(tweet_text)
        
        return '\n\n'.join(content_parts)
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract the Twitter author."""
        author_selectors = [
            '[data-testid="User-Names"]',
            '.username',
            '.fullname'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author = self.clean_text(element.get_text())
                if author:
                    return author
        
        return ""
