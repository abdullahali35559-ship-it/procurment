from database.connection import SessionLocal
from database.models import Email
from datetime import datetime, date

def list_emails_by_date():
    db = SessionLocal()
    try:
        # Check for 23rd and 24th
        dates_to_check = [date(2026, 2, 23), date(2026, 2, 24), date(2026, 2, 25)]
        
        for d in dates_to_check:
            print(f"\n--- Emails for {d} ---")
            emails = db.query(Email).filter(
                Email.received_at >= datetime.combine(d, datetime.min.time()),
                Email.received_at <= datetime.combine(d, datetime.max.time())
            ).all()
            
            if not emails:
                print("  No emails found for this date.")
            else:
                for e in emails:
                    print(f"  [{'T' if e.is_tender else 'M'}] {e.received_at.time()} | {e.sender} | {e.subject[:50]}... | Tender: {e.tender_id}")

    finally:
        db.close()

if __name__ == "__main__":
    list_emails_by_date()
