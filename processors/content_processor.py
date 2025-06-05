"""Content processor for structuring extracted content for LLM/Vector DB usage."""

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    from langdetect import detect
except ImportError:
    detect = None


class ContentProcessor:
    """Processes raw extracted content into structured format optimized for LLM/Vector DB."""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
    
    def process(self, raw_content: Dict, url: str, site_type: str) -> Dict:
        """
        Process raw extracted content into structured format.
        
        Args:
            raw_content: Raw content dictionary from extractor
            url: Original URL
            site_type: Type of site (linkedin, reddit, etc.)
            
        Returns:
            Structured content dictionary optimized for LLM/Vector DB
        """
        # Generate unique ID
        content_id = self._generate_id(url)
        
        # Extract domain
        domain = self._extract_domain(url)
        
        # Clean and process text
        title = self._clean_text(raw_content.get('title', ''))
        content = self._clean_text(raw_content.get('content', ''))
        
        # Detect language
        language = self._detect_language(content)
        
        # Extract keywords/tags
        tags = self._extract_keywords(title + ' ' + content)
        
        # Determine content type
        content_type = self._determine_content_type(site_type, raw_content)
        
        # Create chunks for vector embedding
        chunks = self._create_chunks(content)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(raw_content, content)
        
        # Structure the final output
        structured_content = {
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
                "word_count": len(content.split()) if content else 0,
                "language": language,
                "images": raw_content.get('images', [])
            },
            "metadata": {
                "author": raw_content.get('author', ''),
                "publish_date": raw_content.get('publish_date', ''),
                "tags": tags,
                "content_type": content_type
            },
            "processing": {
                "extraction_method": "site_specific" if site_type != "generic" else "generic",
                "confidence_score": confidence_score,
                "chunks": chunks
            }
        }
        
        return structured_content
    
    def _generate_id(self, url: str) -> str:
        """Generate a unique ID for the content."""
        timestamp = datetime.utcnow().isoformat()
        content_string = f"{url}_{timestamp}"
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return 'unknown'
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove common artifacts
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces
        text = re.sub(r'\n+', '\n', text)  # Multiple newlines
        
        return text.strip()
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        if not text or not detect:
            return "en"  # Default to English
        
        try:
            return detect(text)
        except Exception:
            return "en"
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        if not text:
            return []
        
        # Simple keyword extraction - remove common words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words, filter stop words, and get most common
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:max_keywords]]
    
    def _determine_content_type(self, site_type: str, raw_content: Dict) -> str:
        """Determine the type of content."""
        type_mapping = {
            'linkedin': 'article',
            'reddit': 'post',
            'twitter': 'post',
            'wikipedia': 'encyclopedia',
            'research': 'paper',
            'generic': 'article'
        }
        return type_mapping.get(site_type, 'article')
    
    def _create_chunks(self, content: str) -> List[Dict]:
        """Create text chunks for vector embedding."""
        if not content:
            return []
        
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), self.chunk_size):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "position": len(chunks) + 1,
                "char_count": len(chunk_text)
            })
        
        return chunks
    
    def _calculate_confidence(self, raw_content: Dict, processed_content: str) -> float:
        """Calculate confidence score for the extraction."""
        score = 0.0
        
        # Base score
        if processed_content and len(processed_content) > 50:
            score += 0.3
        
        # Title presence
        if raw_content.get('title'):
            score += 0.2
        
        # Content length
        word_count = len(processed_content.split()) if processed_content else 0
        if word_count > 100:
            score += 0.2
        if word_count > 500:
            score += 0.1
        
        # Author presence
        if raw_content.get('author'):
            score += 0.1
        
        # Images presence
        if raw_content.get('images'):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
