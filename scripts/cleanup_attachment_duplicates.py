
import sys
sys.path.append('.')
from database.connection import SessionLocal
from database.models import Attachment
from sqlalchemy import func

def cleanup_duplicates():
    db = SessionLocal()
    try:
        # Find duplicates
        # Group by thread_id and file_path
        duplicates = db.query(
            Attachment.thread_id, 
            Attachment.file_path, 
            func.count(Attachment.id).label('cnt')
        ).group_by(Attachment.thread_id, Attachment.file_path).having(func.count(Attachment.id) > 1).all()
        
        print(f"Found {len(duplicates)} duplicate groups.")
        
        total_removed = 0
        for thread_id, file_path, count in duplicates:
            # Keep the first one, delete the rest
            all_matches = db.query(Attachment).filter(
                Attachment.thread_id == thread_id,
                Attachment.file_path == file_path
            ).order_by(Attachment.id).all()
            
            to_delete = all_matches[1:]
            for att in to_delete:
                db.delete(att)
                total_removed += 1
            
            print(f"  [-] Cleaned '{file_path[:40]}...' in Thread {thread_id} (Removed {len(to_delete)})")
        
        db.commit()
        print(f"\nCleanup complete. Total duplicate attachments removed: {total_removed}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()
