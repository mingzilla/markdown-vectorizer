import os
import markdown
from typing import List, Dict, Any, Optional, Tuple


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def get_markdown_files(directory: str) -> List[str]:
        """
        Recursively find all markdown files in a directory.
        
        Args:
            directory: The directory to search for markdown files
            
        Returns:
            A list of paths to markdown files
        """
        markdown_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.md', '.markdown')):
                    markdown_files.append(os.path.join(root, file))
        return markdown_files

    @staticmethod
    def read_markdown_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Read a markdown file and extract its content.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            A tuple of (text_content, metadata)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to plain text to remove formatting
        html = markdown.markdown(content)
        
        # Simple html to text conversion (not perfect but works for basic markdown)
        text = html.replace('<p>', '').replace('</p>', '\n\n')
        text = text.replace('<h1>', '# ').replace('</h1>', '\n\n')
        text = text.replace('<h2>', '## ').replace('</h2>', '\n\n')
        text = text.replace('<h3>', '### ').replace('</h3>', '\n\n')
        text = text.replace('<h4>', '#### ').replace('</h4>', '\n\n')
        text = text.replace('<h5>', '##### ').replace('</h5>', '\n\n')
        text = text.replace('<h6>', '###### ').replace('</h6>', '\n\n')
        
        # Get relative path for better identification
        rel_path = os.path.relpath(file_path, '/volumes/input')
        
        # Extract metadata
        metadata = {
            "source": rel_path,
            "filename": os.path.basename(file_path),
            "directory": os.path.dirname(rel_path)
        }
        
        return text, metadata
