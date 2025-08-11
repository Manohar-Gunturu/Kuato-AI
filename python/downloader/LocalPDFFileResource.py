from pathlib import Path
from python.downloader import Resource
import pdfplumber

class LocalPDFFileResource(Resource):
    def __init__(self):
        if pdfplumber is None:
            raise ImportError("pdfplumber is required. Install with: pip install pdfplumber")

    def extract_text_with_pdfplumber(self, file_path):
        """Extract text using pdfplumber (recommended for better accuracy)."""
        text_content = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        return '\n\n'.join(text_content)

    def clean_pdf_text(self, text):
        """
        Clean extracted PDF text by removing extra whitespace and normalizing.
        
        Args:
            text (str): Raw PDF text content
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Replace multiple whitespace characters with single space
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading and trailing whitespace
        text = text.strip()
        
        # Normalize line breaks and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text

    def download(self, path: str) -> tuple[str, str]:
        """
        Download (extract text from) a local PDF file from the filesystem.
        
        Args:
            path (str): Path to the local PDF file
            
        Returns:
            tuple[str, str]: Tuple where first element is file path and second is extracted text
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a PDF or cannot be read
            ImportError: If required PDF libraries are not installed
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
            
            # Check if it's a PDF file
            if not str(file_path).lower().endswith('.pdf'):
                raise ValueError(f"File is not a PDF: {path}")
            
            content = self.extract_text_with_pdfplumber(file_path)
            
            # Clean the extracted text
            cleaned_content = self.clean_pdf_text(content)
            return (str(file_path), cleaned_content)
                
        except Exception as e:
            # Log error but don't break the flow
            print(f"Error reading PDF file {path}: {e}")
            return (path, "")