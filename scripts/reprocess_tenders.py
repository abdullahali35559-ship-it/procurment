import sys
sys.path.append('.')
import argparse
from database.models import Email, Document
from database.connection import SessionLocal
from sqlalchemy import or_

def reprocess_tender(tender_id=None, email_id=None, keyword=None, reset_all_failed=False):
    """
    Reset processed status for emails to allow Procurement Agent to re-run
    """
    db = SessionLocal()
    try:
        query = db.query(Email)
        
        if email_id:
            query = query.filter(Email.id == email_id)
        elif tender_id:
            query = query.filter(Email.tender_id == tender_id)
        elif keyword:
            query = query.filter(Email.subject.ilike(f"%{keyword}%"))
        elif reset_all_failed:
            print("Please specify --tender or --email_id or --keyword")
            return

        emails = query.all()
        if not emails:
            print("No matching emails found.")
            return

        print(f"Found {len(emails)} email(s) to reset.")
        
        for e in emails:
            print(f"Resetting: {e.subject} (Tender: {e.tender_id})")
            e.processed = False
        
        db.commit()
        print("\n[OK] Success. You can now run 'python scripts/process_emails.py' to re-process these emails.")
        
    except Exception as ex:
        db.rollback()
        print(f"[ERROR] {ex}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reprocess tender emails")
    parser.add_argument("--tender", help="Tender ID to reset")
    parser.add_argument("--email", type=int, help="Database Email ID to reset")
    parser.add_argument("--keyword", help="Keyword in email subject to reset")
    
    args = parser.parse_args()
    
    if args.tender or args.email or args.keyword:
        reprocess_tender(tender_id=args.tender, email_id=args.email, keyword=args.keyword)
    else:
        print("Usage: python scripts/reprocess_tenders.py --tender <TID> OR --email <EID> OR --keyword <KEYWORD>")
