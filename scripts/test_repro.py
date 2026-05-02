import os
import json
from database.connection import SessionLocal
from database.models import Email, Document, Tender, Project, DraftEmail
from scripts.run_rfq_agent import process_tender_email
from agents.procurement_agent.gmail_api_client import GmailAPIFetcher

def test_full_repro_hardened():
    db = SessionLocal()
    gmail = GmailAPIFetcher()
    
    # IDs we want to process/verify
    # 214: Request for Quotation (Was merged into TND-2026-00011)
    # 222: For calculation (ID 17)
    # 223: For calculation (ID 18)
    # 224: Tender Document (ID 19 - IT project rejection)
    # 225: Request for calculation (Unprocessed - Drawings.zip)
    db_ids = [214, 222, 223, 224, 225]
    
    try:
        if not gmail.connect():
            print("Failed to connect to Gmail.")
            return

        print(f"Cleaning data for IDs {db_ids}...")
        for eid in db_ids:
            e = db.query(Email).filter(Email.id == eid).first()
            if e:
                # If it was merged into a tender, we might want to clean that tender 
                # but ONLY if it's one of the ones we just created.
                # TND-2026-00011 is OLD/REAL, don't delete the whole tender, 
                # just detach the email and its documents.
                if e.tender_id == 'TND-2026-00011':
                     print(f"  Detaching ID {eid} from TND-2026-00011...")
                     db.query(Document).filter(Document.tender_id == 'TND-2026-00011', Document.original_filename.like('08C-211-21SP-EE%')).delete()
                
                # Reset the email
                e.processed = False
                e.tender_id = None
                e.is_tender = False
        
        db.commit()

        # Fetch and process
        emails = db.query(Email).filter(Email.id.in_(db_ids)).all()
        print(f"Found {len(emails)} emails. Processing...")
        
        for e in emails:
            print(f"\n--- Processing Email {e.id}: {e.subject} ---")
            full_data = gmail._fetch_email_details(e.email_id)
            if not full_data:
                print(f"❌ Could not fetch data for Gmail ID {e.email_id}")
                continue
                
            result = process_tender_email(full_data)
            if result:
                print(f"✅ Success: Tender ID {result.get('tender_id')}")
            else:
                print(f"❌ Failed or Skipped")
                
    finally:
        db.close()

if __name__ == "__main__":
    os.environ['PYTHONPATH'] = "."
    test_full_repro_hardened()
