"""
Junk Cleanup Script
Removes misclassified marketing/junk emails from Tender status and deletes associated records.
"""
import sys
import os
sys.path.append('.')

from database.connection import SessionLocal
from database.models import Email, Tender, Project, Document, DraftEmail, ProcurementDraft, AgentHandover
import shutil

def cleanup_junk():
    db = SessionLocal()
    
    # Keywords that indicate marketing/junk
    junk_keywords = ["Zoho", "ClickUp", "Replit", "Prezi", "Gemini API", "Subscription", "Trial", "Product Update", "Loom AI", "Postman"]
    
    print("=== STARTING JUNK CLEANUP ===\n")
    
    # 1. Find emails incorrectly marked as tenders
    junk_emails = []
    for kw in junk_keywords:
        results = db.query(Email).filter(Email.subject.ilike(f"%{kw}%"), Email.is_tender == True).all()
        junk_emails.extend(results)
    
    # Deduplicate
    junk_emails = list({e.id: e for e in junk_emails}.values())
    
    if not junk_emails:
        print("No junk emails found to clean up.")
        db.close()
        return

    print(f"Found {len(junk_emails)} junk email(s) that were marked as tenders.\n")
    
    for email in junk_emails:
        tender_id = email.tender_id
        subject = email.subject
        print(f"Cleaning: {subject} (Tender ID: {tender_id})")
        
        # Reset Email record
        email.is_tender = False
        email.tender_id = None
        email.processed = False # Allow re-evaluation
        email.detection_confidence = 0.0
        
        if tender_id:
            # Delete associated records
            print(f"  - Deleting records for {tender_id}")
            db.query(AgentHandover).filter(AgentHandover.tender_id == tender_id).delete()
            db.query(ProcurementDraft).filter(ProcurementDraft.tender_id == tender_id).delete()
            db.query(DraftEmail).filter(DraftEmail.tender_id == tender_id).delete()
            db.query(Document).filter(Document.tender_id == tender_id).delete()
            
            # Find and delete Tender/Project
            tender = db.query(Tender).filter(Tender.tender_id == tender_id).first()
            if tender:
                db.delete(tender)
                
            project = db.query(Project).filter(Project.tender_id == tender_id).first()
            if project:
                db.delete(project)
            
            # Delete physical folder
            storage_path = os.path.join("storage", "tenders", tender_id)
            if os.path.exists(storage_path):
                print(f"  - Attempting to delete folder: {storage_path}")
                try:
                    # Handle read-only files on Windows
                    def remove_readonly(func, path, excinfo):
                        os.chmod(path, 0o777)
                        func(path)
                    shutil.rmtree(storage_path, onerror=remove_readonly)
                    print(f"  - Deleted folder successfully")
                except Exception as e:
                    print(f"  - Warning: Could not delete folder {storage_path}: {e}")
        
        # Commit each one to ensure progress
        db.commit()
    print("\n[OK] Cleanup complete. Marketing emails reset to non-tender status.")
    db.close()

if __name__ == "__main__":
    cleanup_junk()
