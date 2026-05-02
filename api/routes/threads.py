from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Dict, Any
from database.models import Thread, Email, Attachment, User, Tag
from config.database import get_db
from auth.dependencies import get_current_user
from datetime import datetime

router = APIRouter(tags=["threads"])

@router.get("/api/threads")
async def get_threads(status: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all threads with optional status filter"""
    try:
        query = db.query(Thread)
        if status:
            query = query.filter(Thread.status == status)
        threads = query.order_by(desc(Thread.updated_at)).all()
        
        results = []
        for t in threads:
            count = db.query(Attachment).filter(Attachment.thread_id == t.thread_id).count()
            
            # Fetch latest meeting suggestion
            latest_email = db.query(Email).filter(
                Email.thread_id == t.thread_id,
                Email.meta_data.isnot(None)
            ).order_by(Email.received_at.desc()).first()
            
            meeting_suggestion = None
            if latest_email and latest_email.meta_data:
                meeting_suggestion = latest_email.meta_data.get('meeting_suggestion')
            
            if t.status == 'MEETING_BOOKED' and meeting_suggestion:
                meeting_suggestion['booked'] = True

            first_msg = db.query(Email).filter(Email.thread_id == t.thread_id).order_by(Email.received_at.asc()).first()
            sender_email = first_msg.sender if first_msg else ""

            results.append({
                "id": t.id,
                "thread_id": t.thread_id,
                "status": t.status.lower() if t.status else "pending",
                "contact": t.contact_name,
                "sender_email": sender_email,
                "subject": t.subject or t.topic_name,
                "date": t.created_at.isoformat() if t.created_at else None,
                "contact_name": t.contact_name,
                "topic_name": t.topic_name,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                "attachments": count,
                "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in t.tags],
                "meeting_suggestion": meeting_suggestion
            })
            
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/threads/{thread_id}")
async def get_single_thread(thread_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return {
            "id": thread.id,
            "thread_id": thread.thread_id,
            "status": thread.status,
            "contact_name": thread.contact_name,
            "topic_name": thread.topic_name,
            "subject": thread.subject,
            "created_at": thread.created_at.isoformat() if thread.created_at else None
        }
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/threads/{thread_id}/attachments")
async def get_thread_attachments(thread_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if not thread_id or thread_id in ('undefined', 'all'):
            docs = db.query(Attachment).order_by(desc(Attachment.uploaded_at)).all()
        else:
            docs = db.query(Attachment).filter(Attachment.thread_id == thread_id).all()
            
        email_info = {}
        thread_ids = list(set([d.thread_id for d in docs if d.thread_id]))
        if thread_ids:
            emails = db.query(Email).filter(Email.thread_id.in_(thread_ids)).all()
            for e in emails:
                if e.thread_id not in email_info:
                    email_info[e.thread_id] = {"subject": e.subject, "sender": e.sender}

        results = []
        for d in docs:
            t = db.query(Thread).filter(Thread.thread_id == d.thread_id).first()
            results.append({
                "id": d.id,
                "name": d.original_filename or d.filename,
                "type": d.doc_type or 'Document',
                "thread": d.thread_id or 'N/A',
                "thread_updated_at": t.updated_at.isoformat() if t and t.updated_at else d.uploaded_at.isoformat(),
                "source_email": email_info.get(d.thread_id, {}).get('subject', 'N/A'),
                "source_sender": email_info.get(d.thread_id, {}).get('sender', 'N/A'),
                "summary": d.summary,
                "size": f"{d.file_size_bytes / 1024:.1f} KB" if d.file_size_bytes else "0 KB",
                "date": d.uploaded_at.isoformat() if d.uploaded_at else datetime.utcnow().isoformat(),
            })
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tags")
async def get_tags(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return {"success": True, "data": tags}
