"""Factory for creating site-specific extractors."""

from typing import Dict
from .base_extractor import BaseExtractor
from .linkedin_extractor import LinkedInExtractor
from .reddit_extractor import RedditExtractor
from .twitter_extractor import TwitterExtractor
from .wikipedia_extractor import WikipediaExtractor
from .research_extractor import ResearchExtractor
from .generic_extractor import GenericExtractor


class ExtractorFactory:
    """Factory class for creating appropriate extractors based on site type."""
    
    def __init__(self):
        self.extractors = {
            'linkedin': LinkedInExtractor,
            'reddit': RedditExtractor,
            'twitter': TwitterExtractor,
            'wikipedia': WikipediaExtractor,
            'research': ResearchExtractor,
            'generic': GenericExtractor,
        }
    
    def get_extractor(self, site_type: str) -> BaseExtractor:
        """
        Get the appropriate extractor for the given site type.
        
        Args:
            site_type: The type of site ('linkedin', 'reddit', etc.)
            
        Returns:
            An instance of the appropriate extractor
        """
        extractor_class = self.extractors.get(site_type, GenericExtractor)
        return extractor_class()
