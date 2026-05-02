import shutil
import os
import stat
from database.connection import SessionLocal
from database.models import Email, Document, Project, Tender, DraftEmail

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

db = SessionLocal()
target_id = 'TND-2026-00015'
email_ids = [222, 223, 224, 225]

try:
    print(f"Cleaning up DB records for {target_id}...")
    db.query(Document).filter(Document.tender_id == target_id).delete()
    db.query(DraftEmail).filter(DraftEmail.tender_id == target_id).delete()
    db.query(Tender).filter(Tender.tender_id == target_id).delete()
    db.query(Project).filter(Project.tender_id == target_id).delete()
    
    print(f"Resetting emails {email_ids}...")
    db.query(Email).filter(Email.id.in_(email_ids)).update(
        {Email.processed: False, Email.tender_id: None, Email.is_tender: False}, 
        synchronize_session=False
    )
    
    db.commit()
    print("DB Cleanup complete.")

    path_to_del = f'./storage/tenders/{target_id}'
    if os.path.exists(path_to_del):
        print(f"Deleting folder {path_to_del}...")
        shutil.rmtree(path_to_del, onerror=remove_readonly)
        print("Folder cleanup complete.")
    else:
        print("Folder already deleted.")

except Exception as e:
    db.rollback()
    print(f"Error during cleanup: {e}")
finally:
    db.close()
