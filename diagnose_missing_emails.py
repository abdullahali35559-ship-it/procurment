from database.connection import SessionLocal
from database.models import Email, Tender
from sqlalchemy import desc
from datetime import datetime
import json

def check_missing_emails():
    db = SessionLocal()
    try:
        # Check for specific tenders
        target_tenders = ['TND-2026-00013', 'TND-2026-00014']
        print(f"Checking for tenders: {target_tenders}")
        
        for tid in target_tenders:
            tender = db.query(Tender).filter(Tender.tender_id == tid).first()
            if tender:
                print(f"\n[FOUND] Tender {tid}:")
                print(f"  Project: {tender.project_name}")
                print(f"  Client: {tender.client_name}")
                print(f"  Source: {tender.source}")
                print(f"  Source Email: {tender.source_email}")
                print(f"  Source Sender: {tender.source_sender}")
                print(f"  Created At: {tender.created_at}")
                
                # Check for associated email by ID
                email = db.query(Email).filter(Email.tender_id == tid).first()
                if email:
                    print(f"  [FOUND] Associated Email (by tender_id):")
                    print(f"    ID: {email.email_id}")
                    print(f"    Subject: {email.subject}")
                    print(f"    Sender: {email.sender}")
                else:
                    print(f"  [NOT FOUND] No email record with tender_id={tid}")
                    
                    # Search for any email that might match the sender
                    if tender.source_sender:
                        print(f"  Searching for emails by sender: {tender.source_sender}")
                        # Use ilike for partial matching if it's "Name <email@domain.com>"
                        sender_emails = db.query(Email).filter(Email.sender.ilike(f"%{tender.source_sender}%")).all()
                        for se in sender_emails:
                            print(f"    - [{se.tender_id or 'None'}] {se.subject[:50]}... ({se.received_at})")
                    
                    # Search by subject match
                    if tender.project_name:
                        print(f"  Searching for emails by subject: {tender.project_name}")
                        subj_emails = db.query(Email).filter(Email.subject.ilike(f"%{tender.project_name}%")).all()
                        for su in subj_emails:
                            print(f"    - [{su.tender_id or 'None'}] {su.subject[:50]}... ({su.received_at})")
            else:
                print(f"\n[NOT FOUND] Tender {tid}")

        # Summary of last 20 tenders to see creation pattern
        print("\n--- Latest 20 Tenders in DB ---")
        latest_tenders = db.query(Tender).order_by(desc(Tender.created_at)).limit(20).all()
        for t in latest_tenders:
            print(f"  {t.created_at} | {t.tender_id} | {t.project_name[:30] if t.project_name else 'None'} | Source: {t.source}")

        # Summary of last 20 emails
        print("\n--- Latest 20 Emails in DB ---")
        latest_emails = db.query(Email).order_by(desc(Email.received_at)).limit(20).all()
        for e in latest_emails:
            print(f"  [{'T' if e.is_tender else 'M'}] {e.received_at} | {e.subject[:40] if e.subject else 'None'}... | Tender: {e.tender_id}")

    finally:
        db.close()

if __name__ == "__main__":
    check_missing_emails()
