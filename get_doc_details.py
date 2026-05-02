from database.connection import SessionLocal
from database.models import Document
import json

def get_document_details():
    db = SessionLocal()
    try:
        # Check for specific tenders
        target_tenders = ['TND-2026-00013', 'TND-2026-00014']
        print(f"Details for Documents in Tenders: {target_tenders}")
        
        for tid in target_tenders:
            docs = db.query(Document).filter(Document.tender_id == tid).all()
            print(f"\n--- {tid} ({len(docs)} documents) ---")
            for d in docs:
                print(f"  - {d.filename} | Source Path: {d.file_path} | Type: {d.category} | Created: {d.created_at}")

    finally:
        db.close()

if __name__ == "__main__":
    get_document_details()
