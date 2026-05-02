import os
from database.connection import SessionLocal
from database.models import Email
from scripts.run_rfq_agent import process_tender_email
from agents.procurement_agent.gmail_api_client import GmailAPIFetcher

def verify_final():
    db = SessionLocal()
    gmail = GmailAPIFetcher()
    
    # IDs in order of processing to verify database-aware aggregation
    ids = [222, 224, 227, 225, 214]
    
    try:
        if not gmail.connect():
            print("Failed to connect to Gmail.")
            return

        for eid in ids:
            e = db.query(Email).filter(Email.id == eid).first()
            if not e:
                print(f"Email ID {eid} not found in DB.")
                continue
                
            print(f"\n{'='*60}")
            print(f"PROCESSING EMAIL {eid}: {e.subject}")
            print(f"{'='*60}")
            
            full_data = gmail._fetch_email_details(e.email_id)
            if not full_data:
                print(f"❌ Could not fetch details for {e.email_id}")
                continue
            
            # Map provider if missing (needed by run_rfq_agent)
            full_data['provider'] = 'gmail'
            
            result = process_tender_email(full_data)
            
            # Update DB status
            if result:
                e.processed = True
                e.is_tender = True
                e.tender_id = result.get('tender_id')
                db.commit()
                print(f"✅ Success: {result.get('tender_id')}")
            else:
                print(f"❌ Failed or Not a Tender")
                
    finally:
        db.close()

if __name__ == "__main__":
    verify_final()
