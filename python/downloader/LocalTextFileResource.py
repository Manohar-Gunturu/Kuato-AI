import os
from pathlib import Path
from python.downloader import Resource

class LocalTextFileResource(Resource):
    def __init__(self):
        pass

    def download(self, path: str) -> tuple[str, str]:
        """
        Download (read) a local file from the filesystem.
        
        Args:
            path (str): Path to the local file
            
        Returns:
            tuple[str, str]: Tuple where first element is file path and second is content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If no permission to read the file
            UnicodeDecodeError: If file can't be decoded with specified encoding
        """
        try:
            # Convert to Path object for better path handling
            file_path = Path(path).resolve()
            
            # Check if file exists
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            # Check if it's actually a file (not a directory)
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {path}")
            
            # Read the file content with default UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return (str(file_path), content)
                
        except Exception as e:
            # Log error but don't break the flow
            print(f"Error reading file {path}: {e}")
            return (path, "")
