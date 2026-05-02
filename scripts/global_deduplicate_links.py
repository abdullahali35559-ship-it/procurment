
import sys
sys.path.append('.')
from database.connection import SessionLocal
from database.models import Attachment

def global_deduplicate():
    db = SessionLocal()
    try:
        # Get all cloud links ordered by newest first
        links = db.query(Attachment).filter(Attachment.file_path.like('URL:%')).order_by(Attachment.id.desc()).all()
        
        seen_urls = set()
        removed = 0
        
        for l in links:
            url = l.file_path
            if url in seen_urls:
                print(f"  [X] Removing global duplicate: {url} (ID: {l.id}) from Thread {l.thread_id}")
                db.delete(l)
                removed += 1
            else:
                seen_urls.add(url)
                print(f"  [K] Keeping latest: {url} (ID: {l.id}) in Thread {l.thread_id}")
                
        db.commit()
        print(f"\nGlobal deduplication complete. Removed {removed} redundant links.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    global_deduplicate()
