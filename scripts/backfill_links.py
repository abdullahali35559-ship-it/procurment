
import sys
sys.path.append('.')
from database.connection import SessionLocal
from database.models import Email, Attachment, Thread
from agents.procurement_agent.cloud_link_detector import CloudLinkDetector, CloudProvider

def backfill_links():
    db = SessionLocal()
    detector = CloudLinkDetector()
    try:
        # Get all actionable emails
        emails = db.query(Email).filter(Email.is_actionable == True).all()
        print(f"Scanning {len(emails)} emails for missing cloud links...")
        
        found_count = 0
        for email in emails:
            links = detector.detect_links(email.body)
            if not links:
                continue
                
            for link in links:
                # Check if this link already exists as an attachment
                exists = db.query(Attachment).filter(
                    Attachment.thread_id == email.thread_id,
                    Attachment.file_path == f"URL:{link['url']}"
                ).first()
                
                if not exists:
                    print(f"  [+] Found missing link in '{email.subject[:30]}': {link['url']}")
                    link_name = f"[LINK] {link['provider'].value.title()} Documents"
                    new_link_att = Attachment(
                        thread_id=email.thread_id,
                        category="00_Cloud_Links",
                        filename=link_name,
                        original_filename=link_name,
                        file_path=f"URL:{link['url']}",
                        file_hash=f"link_{hash(link['url'])}",
                        doc_type="Cloud Link",
                        summary=f"External documents shared via {link['provider'].value}.",
                        is_correct=True
                    )
                    db.add(new_link_att)
                    found_count += 1
        
        db.commit()
        print(f"\nBackfill complete. Added {found_count} virtual attachments.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_links()
