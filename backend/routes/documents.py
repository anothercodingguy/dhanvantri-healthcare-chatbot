"""
Document management routes for Dhanvantri.
Handles file uploads and processing.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from pydantic import BaseModel
import logging

from data.in_memory import get_storage
from utils.parser import parse_document
from utils.utils import format_error_response

logger = logging.getLogger(__name__)
router = APIRouter()

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    message: str
    preview: str

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: Optional[int] = Form(None)
):
    """
    Upload and parse a health document (PDF or JSON).
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename missing")
            
        logger.info(f"Receiving upload: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Parse content
        extracted_text = parse_document(content, file.filename)
        
        if not extracted_text:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from file. Please ensure it is a valid PDF or JSON."
            )
            
        # Determine type
        doc_type = 'pdf' if file.filename.lower().endswith('.pdf') else 'json'
        
        # Store in memory
        storage = get_storage()
        doc = storage.add_document(extracted_text, file.filename, doc_type, user_id)
        
        return {
            "id": doc.id,
            "filename": doc.filename,
            "message": "File uploaded and analyzed successfully",
            "preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
