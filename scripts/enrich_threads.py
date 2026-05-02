
import sys
sys.path.append('.')
from database.connection import SessionLocal
from database.models import Attachment, Thread, Email, Contact, Topic
from datetime import datetime
import re

def universal_enrich():
    db = SessionLocal()
    try:
        # 1. Find attachments whose thread_id is missing from Thread table
        all_att_threads = [t[0] for t in db.query(Attachment.thread_id).distinct().all() if t[0]]
        existing_threads = [t[0] for t in db.query(Thread.thread_id).all()]
        missing_ids = [tid for tid in all_att_threads if tid not in existing_threads]
        
        print(f"Found {len(missing_ids)} thread IDs with attachments but no Thread record.")
        
        for tid in missing_ids:
            email = db.query(Email).filter(Email.thread_id == tid).first()
            if email:
                # Helper to get clean name
                display_name = email.sender.split('@')[0]
                
                print(f"  [+] Creating Thread record for {tid} (Sender: {email.sender})...")
                # Ensure contact exists
                contact = db.query(Contact).filter(Contact.contact_emails.any(email.sender)).first()
                if not contact:
                    contact = Contact(contact_name=display_name, contact_emails=[email.sender])
                    db.add(contact)
                    db.flush()
                
                # Ensure topic exists
                topic = db.query(Topic).filter(Topic.thread_id == tid).first()
                if not topic:
                    topic = Topic(contact_id=contact.id, topic_name=email.subject, thread_id=tid)
                    db.add(topic)
                    db.flush()
                
                new_t = Thread(
                    thread_id=tid,
                    status='COMPLETED',
                    contact_id=contact.id,
                    topic_id=topic.id,
                    contact_name=contact.contact_name,
                    topic_name=topic.topic_name,
                    subject=email.subject,
                    source_email=email.sender,
                    source_sender=contact.contact_name
                )
                db.add(new_t)
            else:
                print(f"  [X] No Email metadata found for Thread ID {tid}")

        # 2. Fix existing Thread records with NULL or generic names
        all_threads = db.query(Thread).all()
        print(f"\nAudit: Checking {len(all_threads)} Thread records for better metadata...")
        r_count = 0
        for t in all_threads:
            email = db.query(Email).filter(Email.thread_id == t.thread_id).first()
            if email:
                changed = False
                if not t.source_email:
                    t.source_email = email.sender
                    changed = True
                
                # If name is generic or missing, try to get from email.sender
                if not t.contact_name or t.contact_name.lower() in ['gmail', 'unknown', 'instructor']:
                    # Try to get display name from contact if it exists
                    contact = db.query(Contact).filter(Contact.id == t.contact_id).first()
                    if contact and contact.contact_name and contact.contact_name.lower() not in ['gmail', 'unknown']:
                        t.contact_name = contact.contact_name
                        changed = True
                    else:
                        new_name = email.sender.split('@')[0].replace('.', ' ').title()
                        t.contact_name = new_name
                        changed = True
                
                if changed:
                    r_count += 1
            
        db.commit()
        print(f"\nUniversal enrichment complete. Repaired/Updated {r_count} records.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    universal_enrich()
