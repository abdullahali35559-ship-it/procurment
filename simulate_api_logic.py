from database.connection import SessionLocal
from database.models import Email, DraftEmail
from sqlalchemy import desc
import json

def simulate_get_emails(tender_id=None, status=None, include_all=True):
    db = SessionLocal()
    try:
        query = db.query(Email)
        
        if tender_id:
            query = query.filter(Email.tender_id == tender_id)
        
        if status:
            if status == "processed":
                query = query.filter(Email.processed == True)
            elif status == "unprocessed":
                query = query.filter(Email.processed == False)
            elif status == "tender":
                query = query.filter(Email.is_tender == True)
            elif status == "junk":
                query = query.filter(Email.is_tender == False)
        
        query = query.order_by(desc(Email.received_at))
        emails = query.limit(100).all()
        
        print(f"Total returned by simulation: {len(emails)}")
        
        target_ids = [190, 191]
        for e in emails:
            if e.id in target_ids:
                print(f"[FOUND] Email {e.id} in simulation results!")
                print(f"  Subject: {e.subject}")
                print(f"  Tender:  {e.tender_id}")
                print(f"  Status:  {'tender' if e.is_tender else 'processed' if e.processed else 'unprocessed'}")
        
        # If not found, check why
        found_ids = [e.id for e in emails]
        for tid in target_ids:
            if tid not in found_ids:
                print(f"[MISSING] Email {tid} not in top 100 simulation results.")
                # Is it further down?
                actual = db.query(Email).filter(Email.id == tid).first()
                if actual:
                    print(f"  Actually exists in DB. ReceivedAt: {actual.received_at}")
                    # Count how many are newer than this
                    newer_count = db.query(Email).filter(Email.received_at > actual.received_at).count()
                    print(f"  Emails newer than this: {newer_count}")

    finally:
        db.close()

if __name__ == "__main__":
    print("--- Simulating DEFAULT view (include_all=True) ---")
    simulate_get_emails()
    
    print("\n--- Simulating TENDERS ONLY view ---")
    simulate_get_emails(status="tender")
