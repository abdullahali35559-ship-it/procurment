from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database.models import Contact, User
from config.database import get_db
from auth.dependencies import get_current_user

router = APIRouter(tags=["contacts"])

@router.get("/api/contacts")
async def get_contacts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return {
        "success": True,
        "count": len(contacts),
        "data": [
            {
                "id": c.id,
                "name": c.contact_name,
                "email": c.email_domain,
                "threads": len(c.threads) if c.threads else 0,
                "status": "active"
            }
            for c in contacts
        ]
    }

@router.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {
        "success": True,
        "data": {
            "id": contact.id,
            "name": contact.contact_name,
            "email": contact.email_domain,
            "first_seen": contact.first_seen.isoformat() if contact.first_seen else None,
            "last_contact": contact.last_contact.isoformat() if contact.last_contact else None,
            "threads": len(contact.threads) if contact.threads else 0
        }
    }

@router.post("/api/contacts")
async def add_contact(contact_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        new_contact = Contact(
            contact_name=contact_data.get("name"),
            email_domain=contact_data.get("email"),
            meta_data=contact_data.get("meta_data", {})
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return {"success": True, "data": {"id": new_contact.id}}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
