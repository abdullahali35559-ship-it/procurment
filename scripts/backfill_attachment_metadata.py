
import sys
sys.path.append('.')
from database.connection import SessionLocal
from database.models import Attachment, Thread, Email, Contact, Topic
from datetime import datetime

def backfill():
    db = SessionLocal()
    try:
        # Find attachments whose thread_id doesn't exist in Thread table
        orphans = db.query(Attachment).outerjoin(Thread, Attachment.thread_id == Thread.thread_id).filter(Thread.id == None).all()
        
        print(f"Repairing {len(orphans)} orphaned attachment(s)...")
        
        repaired = 0
        for att in orphans:
            if not att.thread_id: continue
            
            # Find the email associated with this thread_id
            email = db.query(Email).filter(Email.thread_id == att.thread_id).first()
            if not email:
                print(f"  [X] No email found for {att.filename} (Thread: {att.thread_id})")
                continue
                
            print(f"  [+] Found sender '{email.sender}' for {att.filename}. Creating recovery thread...")
            
            # 1. Find or create contact
            contact = db.query(Contact).filter(Contact.contact_emails.any(email.sender)).first()
            if not contact:
                contact = Contact(
                    contact_name=email.sender.split('@')[0],
                    contact_emails=[email.sender]
                )
                db.add(contact)
                db.flush()
            
            # 2. Find or create topic
            topic = db.query(Topic).filter(Topic.thread_id == att.thread_id).first()
            if not topic:
                topic = Topic(
                    contact_id=contact.id,
                    topic_name=email.subject,
                    thread_id=att.thread_id
                )
                db.add(topic)
                db.flush()
                
            # 3. Create missing Thread
            new_thread = Thread(
                thread_id=att.thread_id,
                status='COMPLETED',
                contact_id=contact.id,
                topic_id=topic.id,
                contact_name=contact.contact_name,
                topic_name=topic.topic_name,
                subject=email.subject,
                source_email=email.sender,
                source_sender=contact.contact_name
            )
            db.add(new_thread)
            repaired += 1
            
        db.commit()
        print(f"\nSuccessfully repaired {repaired} records.")

    except Exception as e:
        print(f"Error during backfill: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill()
