from database.connection import SessionLocal
from database.models import Tender
import json

def get_tender_details():
    db = SessionLocal()
    try:
        # Check for specific tenders
        target_tenders = ['TND-2026-00013', 'TND-2026-00014']
        print(f"Details for Tenders: {target_tenders}")
        
        for tid in target_tenders:
            t = db.query(Tender).filter(Tender.tender_id == tid).first()
            if t:
                print(f"\n--- {tid} ---")
                details = {
                    "tender_id": t.tender_id,
                    "project_name": t.project_name,
                    "client_name": t.client_name,
                    "source": t.source,
                    "source_email": t.source_email,
                    "source_sender": t.source_sender,
                    "created_at": str(t.created_at),
                    "status": t.status,
                    # Add any other relevant fields
                }
                print(json.dumps(details, indent=2))
            else:
                print(f"\n--- {tid} NOT FOUND ---")

    finally:
        db.close()

if __name__ == "__main__":
    get_tender_details()
