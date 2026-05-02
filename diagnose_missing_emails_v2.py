from database.connection import SessionLocal
from database.models import Document, AuditLog, Tender, Email
import json

def diagnose_tenders(tender_ids):
    db = SessionLocal()
    try:
        for tid in tender_ids:
            print(f"\n========================================")
            print(f"DIAGNOSING: {tid}")
            print(f"========================================")
            
            # 1. Tender Metadata
            t = db.query(Tender).filter(Tender.tender_id == tid).first()
            if t:
                print(f"Tender Source: {t.source}")
                print(f"Project Name: {t.project_name}")
                print(f"Created At: {t.created_at}")
            
            # 2. Documents
            docs = db.query(Document).filter(Document.tender_id == tid).all()
            print(f"\nDocuments ({len(docs)}):")
            for d in docs:
                print(f"  - {d.filename} | Source: {d.source} | Uploaded: {d.uploaded_at}")
            
            # 3. Audit Log
            logs = db.query(AuditLog).filter(AuditLog.tender_id == tid).order_by(AuditLog.timestamp).all()
            print(f"\nAudit Log ({len(logs)}):")
            for l in logs:
                print(f"  {l.timestamp} | {l.agent} | {l.action}")
            
            # 4. Check for emails that might have BEEN this tender but are unlinked
            # Search emails by project name match
            if t and t.project_name:
                print(f"\nSearching for unlinked emails matching project: '{t.project_name}'")
                search_term = t.project_name.split(':')[0] # Try first part
                emails = db.query(Email).filter(Email.subject.ilike(f"%{search_term}%")).all()
                for e in emails:
                    print(f"  - Email ID: {e.id} | Subject: {e.subject} | Tender ID in Email Record: {e.tender_id}")

    finally:
        db.close()

if __name__ == "__main__":
    diagnose_tenders(['TND-2026-00013', 'TND-2026-00014'])
