import os
import shutil
from database.connection import SessionLocal
from database.models import Email, Document, Tender, Project, ProcurementDraft, DraftEmail, FileLink
from config.settings import STORAGE_PATH

def deep_cleanup():
    db = SessionLocal()
    
    # Target Tenders (17-23)
    tids = [f"TND-2026-0{i:04d}" for i in range(17, 24)]
    # Target Email IDs
    email_ids = [214, 222, 223, 224, 225, 227]
    
    print(f"Starting deep cleanup for tenders: {tids}")
    
    try:
        # 1. Delete Documents
        del_docs = db.query(Document).filter(Document.tender_id.in_(tids)).delete(synchronize_session=False)
        print(f"Deleted {del_docs} documents.")
        
        # 2. Delete Procurement Drafts & Draft Emails
        del_procurement = db.query(ProcurementDraft).filter(ProcurementDraft.tender_id.in_(tids)).delete(synchronize_session=False)
        del_drafts = db.query(DraftEmail).filter(DraftEmail.tender_id.in_(tids)).delete(synchronize_session=False)
        print(f"Deleted {del_procurement} Procurement drafts and {del_drafts} draft emails.")
        
        # 3. Delete File Links
        del_links = db.query(FileLink).filter(FileLink.tender_id.in_(tids)).delete(synchronize_session=False)
        print(f"Deleted {del_links} file links.")
        
        # 4. Delete Tenders and Projects
        # Note: Projects table uses incrementing ID, but we can match by tender_id
        del_tenders = db.query(Tender).filter(Tender.tender_id.in_(tids)).delete(synchronize_session=False)
        del_projects = db.query(Project).filter(Project.tender_id.in_(tids)).delete(synchronize_session=False)
        print(f"Deleted {del_tenders} tenders and {del_projects} projects.")
        
        # 5. Reset Emails
        emails = db.query(Email).filter(Email.id.in_(email_ids)).all()
        for e in emails:
            e.processed = False
            e.tender_id = None
        print(f"Reset {len(emails)} emails to unprocessed.")
        
        # 6. Physical Folder Cleanup
        import stat
        def remove_readonly(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        for tid in tids:
            folder_path = os.path.join(STORAGE_PATH, tid)
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path, onerror=remove_readonly)
                    print(f"Deleted physical folder: {folder_path}")
                except Exception as e:
                    print(f"Failed to delete {folder_path}: {e}")
        
        db.commit()
        print("\n=== CLEANUP COMPLETE ===")
        
    except Exception as ex:
        db.rollback()
        print(f"Error during cleanup: {ex}")
    finally:
        db.close()

if __name__ == "__main__":
    deep_cleanup()
