"""Site detection module to identify the type of website being scraped."""

import re
from urllib.parse import urlparse
from typing import Dict, List


class SiteDetector:
    """Detects the type of website based on URL patterns and domain names."""
    
    def __init__(self):
        self.site_patterns = {
            'linkedin': [
                r'linkedin\.com',
                r'linkedin\.co\.',
            ],
            'reddit': [
                r'reddit\.com',
                r'redd\.it',
            ],
            'twitter': [
                r'twitter\.com',
                r'x\.com',
            ],
            'wikipedia': [
                r'wikipedia\.org',
                r'.*\.wikipedia\.org',
            ],
            'research': [
                r'arxiv\.org',
                r'researchgate\.net',
                r'scholar\.google\.',
                r'pubmed\.ncbi\.nlm\.nih\.gov',
                r'ieee\.org',
                r'acm\.org',
                r'springer\.com',
                r'sciencedirect\.com',
                r'nature\.com',
                r'science\.org',
            ]
        }
    
    def detect_site_type(self, url: str) -> str:
        """
        Detect the type of site based on the URL.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Site type string ('linkedin', 'reddit', 'twitter', 'wikipedia', 'research', or 'generic')
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check each site type pattern
            for site_type, patterns in self.site_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, domain):
                        return site_type
            
            return 'generic'
            
        except Exception:
            return 'generic'
    
    def get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return 'unknown'
