import os
import sys
import hashlib
from datetime import datetime
sys.path.append('.')

from database.connection import SessionLocal
from database.models import Project, Document, Tender, Client
from config.settings import STORAGE_PATH

def sync_storage_to_db():
    """
    Scans STORAGE_PATH and ensures every file and folder has a 
    corresponding record in the database.
    """
    print("=== STORAGE-DB SYNC STARTED ===\n")
    db = SessionLocal()
    
    try:
        # Get a default client for unmatched tenders
        default_client = db.query(Client).first()
        if not default_client:
            print("[!] No clients found in DB. Creating 'Unknown Client'.")
            default_client = Client(client_name="Unknown Client")
            db.add(default_client)
            db.commit()

        # 1. Walk through all tender folders
        folders = os.listdir(STORAGE_PATH)
        for tender_id in folders:
            tender_path = os.path.join(STORAGE_PATH, tender_id)
            if not os.path.isdir(tender_path) or tender_id == "temp_scan":
                continue
            
            print(f"[*] Processing Tender: {tender_id}")
            
            # 2. Ensure Project record exists
            project = db.query(Project).filter(Project.tender_id == tender_id).first()
            if not project:
                print(f"  [+] Creating Project record for {tender_id}")
                project = Project(
                    client_id=default_client.id,
                    tender_id=tender_id,
                    project_name=f"Synced - {tender_id}",
                    folder_path=tender_path
                )
                db.add(project)
                db.commit()
                db.refresh(project)

            # 3. Ensure Tender record exists
            tender = db.query(Tender).filter(Tender.tender_id == tender_id).first()
            if not tender:
                print(f"  [+] Creating Tender record for {tender_id}")
                tender = Tender(
                    tender_id=tender_id,
                    status='READY_FOR_TENDER_AGENT',
                    client_id=default_client.id,
                    project_id=project.id,
                    client_name=default_client.client_name,
                    project_name=project.project_name,
                    tender_reference=tender_id,
                    location="Saudi Arabia",
                    created_at=datetime.utcnow()
                )
                db.add(tender)
                db.commit()
            
            # 4. Scan document category folders
            for cat in os.listdir(tender_path):
                cat_path = os.path.join(tender_path, cat)
                if not os.path.isdir(cat_path) or cat == "08_Output":
                    continue
                
                # Verify it's a valid category
                valid_prefixes = ["01_", "02_", "03_", "04_", "05_", "06_", "07_"]
                if not any(cat.startswith(p) for p in valid_prefixes):
                    continue

                for filename in os.listdir(cat_path):
                    file_path = os.path.join(cat_path, filename)
                    if not os.path.isfile(file_path):
                        continue
                    
                    # 5. Check if document exists in DB
                    doc = db.query(Document).filter(
                        Document.tender_id == tender_id,
                        Document.filename == filename
                    ).first()
                    
                    if not doc:
                        print(f"  [+] Registering missing document: {filename} in {cat}")
                        try:
                            file_data = open(file_path, 'rb').read()
                            file_hash = hashlib.sha256(file_data).hexdigest()
                            file_size = len(file_data)
                            
                            new_doc = Document(
                                tender_id=tender_id,
                                filename=filename,
                                original_filename=filename.split('_v')[0], # Extract original name from v1, v2 etc 
                                file_path=file_path,
                                file_hash=file_hash,
                                file_size_bytes=file_size,
                                category=cat,
                                classification_confidence=1.0, # Manually synced
                                version=1,
                                uploaded_at=datetime.utcnow()
                            )
                            db.add(new_doc)
                            db.commit()
                        except Exception as e:
                            print(f"  [!] Failed to sync file {filename}: {e}")
                            
    except Exception as e:
        print(f"\n[X] Sync failed: {e}")
        db.rollback()
    finally:
        db.close()
        print("\n=== SYNC COMPLETED ===")

if __name__ == "__main__":
    sync_storage_to_db()
