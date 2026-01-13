"""
Document parser utility for Dhanvantri.
Extracts text from PDF and JSON files.
"""

import json
import io
import logging
from typing import Optional
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def parse_document(file_content: bytes, filename: str) -> Optional[str]:
    """
    Parse uploaded file content and extract text.
    
    Args:
        file_content: Raw bytes of the uploaded file
        filename: Name of the file to determine type
        
    Returns:
        Extracted text string or None if parsing fails
    """
    try:
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return _parse_pdf(file_content)
        elif filename_lower.endswith('.json'):
            return _parse_json(file_content)
        else:
            logger.warning(f"Unsupported file type: {filename}")
            return None
            
    except Exception as e:
        logger.error(f"Error parsing document {filename}: {e}")
        return None

def _parse_pdf(content: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        text = []
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text.append(f"[Page {i+1}]\n{page_text}")
                
        return "\n\n".join(text)
    except Exception as e:
        logger.error(f"PDF parsing error: {e}")
        raise

def _parse_json(content: bytes) -> str:
    """Convert JSON to readable string."""
    try:
        data = json.loads(content)
        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        raise
