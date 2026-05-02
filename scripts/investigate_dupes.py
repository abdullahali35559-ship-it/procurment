from database.connection import SessionLocal
from database.models import Email, Document, Tender, Project
from agents.procurement_agent.gmail_api_client import GmailAPIFetcher

db = SessionLocal()
g = GmailAPIFetcher()

try:
    if g.connect():
        ids = [214, 222, 223, 224, 225]
        print("=== EMAIL ATTACHMENTS ===")
        for eid in ids:
            e = db.query(Email).filter(Email.id == eid).first()
            if e:
                data = g._fetch_email_details(e.email_id)
                attachments = [a['filename'] for a in data.get('attachments', [])]
                print(f"Email ID {eid} | Subject: {e.subject} | Tender ID: {e.tender_id}")
                print(f"  Attachments: {attachments}")
                
        print("\n=== TENDER DOCUMENT CHECK ===")
        tids = ['TND-2026-00019', 'TND-2026-00020', 'TND-2026-00022']
        for tid in tids:
            docs = db.query(Document).filter(Document.tender_id == tid).all()
            print(f"Tender {tid} Documents: {[d.original_filename for d in docs]}")
            
except Exception as ex:
    print(f"Error: {ex}")
finally:
    db.close()
