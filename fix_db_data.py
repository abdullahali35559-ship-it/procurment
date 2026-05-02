
import sys
import os
sys.path.insert(0, os.getcwd())
from database.models import Email, Attachment
from config.database import SessionLocal

db = SessionLocal()
try:
    # Fix Email 170
    e = db.query(Email).get(170)
    if e:
        e.body = "Please find attached the Invitation to Tender (ITT) for the Riyadh Metro Expansion project. Note that the submission deadline is set for May 20, 2026."
        print(f"Updated Email {e.id}")
    
    # Fix Attachment for Thread TND-2026-00050
    # Search by thread_id or filename
    att = db.query(Attachment).filter(Attachment.thread_id.ilike('%TND-2026-00050%')).first()
    if att:
        att.summary = "Invitation to Tender for Riyadh Metro Expansion. Submission deadline: May 20, 2026."
        print(f"Updated Attachment {att.id}")
    
    db.commit()
    print("DB Changes Committed.")
finally:
    db.close()
