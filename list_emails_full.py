from database.connection import SessionLocal
from database.models import Email
from datetime import date, datetime

def list_emails():
    db = SessionLocal()
    try:
        d = date(2026, 2, 24)
        print(f"--- Emails for {d} ---")
        emails = db.query(Email).filter(
            Email.received_at >= datetime.combine(d, datetime.min.time()),
            Email.received_at <= datetime.combine(d, datetime.max.time())
        ).order_by(Email.received_at.desc()).all()
        
        for e in emails:
            print(f"Time: {e.received_at.time()}")
            print(f"  Subject: {e.subject}")
            print(f"  From:    {e.sender}")
            print(f"  Tender:  {e.tender_id}")
            print("-" * 40)
            
    finally:
        db.close()

if __name__ == "__main__":
    list_emails()
