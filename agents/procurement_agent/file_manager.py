import hashlib
import os
from datetime import datetime
from typing import Dict, Optional
from config.settings import STORAGE_PATH
from agents.procurement_agent.document_versioner import DocumentVersioner
from agents.procurement_agent.malware_scanner import MalwareScanner

class FileManager:
    """Manage file storage with flat structure and malware protection"""
    
    def __init__(self, storage_base: str = STORAGE_PATH):
        self.storage_base = storage_base
        self.versioner = DocumentVersioner()
        self.scanner = MalwareScanner()
        os.makedirs(storage_base, exist_ok=True)
    
    def create_thread_folder(self, thread_id: str) -> str:
        """Create a single flat folder for the thread"""
        base_path = os.path.join(self.storage_base, thread_id)
        os.makedirs(base_path, exist_ok=True)
        return base_path

    def create_tender_folder(self, *args, **kwargs):
        """Legacy alias"""
        return self.create_thread_folder(*args, **kwargs)

    def create_folder_structure(self, *args, **kwargs):
        """Legacy alias"""
        return self.create_thread_folder(*args, **kwargs)
    
    def save_file(self, 
                  file_data: bytes,
                  tender_id: str,
                  category: str,
                  original_filename: str,
                  version: int = 1,
                  source: str = "email_attachment") -> Dict:
        """
        Save file to flat directory structure
        """
        
        # Calculate SHA256 hash
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Create versioned filename
        versioned_filename = self.versioner.create_versioned_filename(
            original_filename, 
            version
        )
        
        # All files go to the base folder (FLAT STRUCTURE)
        dest_folder = os.path.join(self.storage_base, tender_id)
        dest_path = os.path.join(dest_folder, versioned_filename)
        
        # Ensure folder exists
        os.makedirs(dest_folder, exist_ok=True)
        
        # If file exists and is read-only, remove the attribute to allow overwriting
        if os.path.exists(dest_path):
            try:
                if os.name == 'nt':
                    os.system(f'attrib -r "{dest_path}"')
                else:
                    os.chmod(dest_path, 0o666)
            except:
                pass
        
        # Save to final destination
        with open(dest_path, 'wb') as f:
            f.write(file_data)
        
        # Set read-only (Windows: attrib +r, Linux: chmod 444)
        try:
            if os.name == 'nt':  # Windows
                os.system(f'attrib +r "{dest_path}"')
            else:  # Linux/Mac
                os.chmod(dest_path, 0o444)
        except:
            pass
        
        return {
            "status": "SAVED",
            "path": dest_path,
            "hash": file_hash,
            "size": len(file_data),
            "version": version,
            "versioned_filename": versioned_filename
        }
    
    def get_or_create_tender_folder(self, 
                                    project_id: Optional[int],
                                    tender_id: str,
                                    existing_folder: Optional[str] = None) -> str:
        """
        Get existing folder path or create new flat folder
        """
        if existing_folder and os.path.exists(existing_folder):
            return existing_folder
        
        return self.create_thread_folder(tender_id)

def generate_tender_id() -> str:
    """Generate unique ID: TND-YYYY-NNNNN"""
    from datetime import datetime
    from database.connection import SessionLocal
    from database.models import Topic
    from sqlalchemy import desc
    
    year = datetime.now().year
    db = SessionLocal()
    try:
        # Get last ID from database for the current year
        last_item = db.query(Topic).filter(
            Topic.thread_id.like(f"TND-{year}-%")
        ).order_by(desc(Topic.thread_id)).first()
        
        if last_item:
            try:
                 last_number_str = last_item.thread_id.split('-')[-1]
                 last_number = int(last_number_str)
            except (ValueError, IndexError):
                 last_number = 0
        else:
            last_number = 0
            
        new_number = last_number + 1
        return f"TND-{year}-{new_number:05d}"
    finally:
        db.close()
