import sys
import io
sys.path.append('.')

from agents.procurement_agent.email_fetcher import EmailFetcher
from scripts.run_rfq_agent import process_incoming_email, log_progress
import time
from datetime import datetime, timezone
import email.utils
from database.models import Email, AuditLog, Thread, Tag, email_tags
from database.connection import SessionLocal
from sqlalchemy import select

def apply_tag_inheritance(db, sender_email, current_email_obj):
    """
    If this sender has tags from previous emails, apply them to the current email.
    """
    try:
        # Find the most recent processed email from this sender that has tags
        previous_email = db.query(Email).filter(
            Email.sender == sender_email,
            Email.processed == True,
            Email.id != current_email_obj.id
        ).order_by(Email.received_at.desc()).first()
        
        if previous_email and previous_email.tags:
            print(f"   [Tag] Inherited {len(previous_email.tags)} tag(s) from previous interaction with {sender_email}")
            for tag in previous_email.tags:
                if tag not in current_email_obj.tags:
                    current_email_obj.tags.append(tag)
            db.commit()
    except Exception as e:
        print(f"   [!] Error during tag inheritance: {e}")

def process_email_batch():
    """
    Fetch and process emails (General Assistant)
    """
    from config.settings import EMAIL_PROVIDERS
    
    print("=" * 60)
    print("EMAIL MONITORING - General Email Assistant")
    print("=" * 60)
    print(f"Providers: {', '.join(EMAIL_PROVIDERS)}")

    processed_email_ids = set()
    
    db = SessionLocal()
    log_progress(db, None, "PROGRESS: Batch Started", {"providers": EMAIL_PROVIDERS})
    db.close()

    for provider in EMAIL_PROVIDERS:
        print(f"\nCHECKING: {provider.upper()}...")
        
        try:
            fetcher = EmailFetcher(provider=provider)
            if not fetcher.connect(): continue
            
            emails = fetcher.fetch_emails(limit=50)
            if not emails:
                print(f"No new emails from {provider}")
                fetcher.disconnect()
                continue
            
            print(f"Found {len(emails)} new email(s).")
            
            for email_data in emails:
                email_id = email_data['email_id']
                if email_id in processed_email_ids: continue
                
                db = SessionLocal()
                try:
                    # Check if exists
                    existing = db.query(Email).filter(Email.email_id == email_id).first()
                    if existing and existing.processed:
                        # SELF-HEALING: If it's already processed but we still fetched it, 
                        # it means the 'move_to_processed' failed last time. 
                        # Try to move it again now.
                        print(f"   [Self-Healing] Email {email_id} already processed but still in inbox. Moving now...")
                        fetcher.move_to_processed(email_data)
                        processed_email_ids.add(email_id)
                        continue
                    
                    if not existing:
                        received_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        if email_data.get('date'):
                            try: received_at = email.utils.parsedate_to_datetime(email_data['date'])
                            except: pass
                        
                        existing = Email(
                            email_id=email_id,
                            subject=email_data['subject'],
                            sender=email_data['sender'],
                            body=email_data['body'],
                            received_at=received_at,
                            processed=False
                        )
                        db.add(existing)
                        db.commit()

                    # 1. Apply Tag Inheritance BEFORE AI processing
                    apply_tag_inheritance(db, email_data['sender'], existing)

                    # 2. Run Main Workflow
                    print(f"\nAnalyzing: {email_data['subject'][:50]}...")
                    # Update progress for individual email
                    log_progress(db, None, f"PROGRESS: Analyzing Email", {"subject": email_data['subject']})
                    
                    result = process_incoming_email(email_data)
                    
                    # Consider it processed if it was either a SUCCESS or if it at least 
                    # reached the point where the email was recorded in the DB (even if draft failed)
                    success_or_recorded = (result and result.get('status') == 'SUCCESS') or \
                                        (db.query(Email).filter(Email.email_id == email_id, Email.processed == True).first())

                    if success_or_recorded:
                        existing.processed = True
                        db.commit()
                        fetcher.move_to_processed(email_data)
                        print(f"   [OK] Processed and moved to history.")
                    elif result and result.get('status') == 'SKIPPED':
                        # Mark as processed and move out of Inbox to keep it clean
                        existing.processed = True
                        existing.is_junk = True
                        db.commit()
                        fetcher.move_to_processed(email_data)
                        print(f"   [--] Junk email skipped and moved to processed.")
                    
                    processed_email_ids.add(email_id)
                except Exception as e:
                    error_msg = f"ERROR: {str(e)}"
                    print(f"   [ERROR] Processing {email_id}: {e}")
                    
                    # FINAL FALLBACK: If the email was recorded in DB but failed later, 
                    # move it anyway to prevent infinite loops/unread status
                    try:
                        record = db.query(Email).filter(Email.email_id == email_id).first()
                        if record:
                            record.processed = True
                            db.commit()
                            fetcher.move_to_processed(email_data)
                            print(f"   [!] Error occurred, but email was moved to processed to avoid unread loop.")
                    except: pass
                    
                    try:
                        log_progress(db, None, error_msg, {"email_id": email_id, "subject": email_data.get('subject')})
                    except: pass
                finally:
                    db.close()
            
            fetcher.disconnect()
        except Exception as e:
            print(f"[ERROR] Provider {provider} failed: {e}")

    db = SessionLocal()
    log_progress(db, None, "PROGRESS: Batch Complete", {"count": len(processed_email_ids)})
    db.close()
    
    print("\nBatch processing complete.")

if __name__ == "__main__":
    process_email_batch()
