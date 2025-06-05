"""File handling utilities for saving scraped content."""

import json
import os
from pathlib import Path
from typing import Dict, List, Union


class FileHandler:
    """Handles file operations for saving scraped content."""
    
    def save_json(self, data: Union[Dict, List], filepath: str) -> None:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save (dict or list)
            filepath: Path to save the file
        """
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_multiple_json(self, data_list: List[Dict], output_dir: str) -> None:
        """
        Save multiple content items to separate JSON files.
        
        Args:
            data_list: List of content dictionaries
            output_dir: Directory to save files
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for i, data in enumerate(data_list):
            # Generate filename from content ID or index
            content_id = data.get('id', f'content_{i}')
            filename = f"{content_id}.json"
            filepath = os.path.join(output_dir, filename)
            
            self.save_json(data, filepath)
    
    def load_urls_from_file(self, filepath: str) -> List[str]:
        """
        Load URLs from a text file (one URL per line).
        
        Args:
            filepath: Path to the file containing URLs
            
        Returns:
            List of URLs
        """
        urls = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # Skip empty lines and comments
                    urls.append(url)
        return urls
