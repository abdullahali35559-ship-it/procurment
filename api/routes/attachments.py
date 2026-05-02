from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import Attachment, User, Thread
from config.database import get_db
from auth.dependencies import get_current_user
from datetime import datetime
import os

router = APIRouter(tags=["attachments"])

@router.get("/api/attachments")
async def get_all_attachments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    attachments = db.query(Attachment).order_by(desc(Attachment.uploaded_at)).all()
    return {"success": True, "data": attachments}

@router.get("/api/attachments/{att_id}")
async def get_attachment(att_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    att = db.query(Attachment).filter(Attachment.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # In a real app, this would return the file content or a signed URL
    # For now, return metadata
    return {
        "success": True,
        "data": {
            "id": att.id,
            "filename": att.filename,
            "original_filename": att.original_filename,
            "size": att.file_size_bytes,
            "summary": att.summary,
            "type": att.doc_type
        }
    }

@router.get("/api/attachments/{att_id}/download")
async def download_attachment(att_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    att = db.query(Attachment).filter(Attachment.id == att_id).first()
    if not att or not att.file_path or not os.path.exists(att.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(att.file_path, filename=att.original_filename)
