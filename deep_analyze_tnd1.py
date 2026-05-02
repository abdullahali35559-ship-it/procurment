from database.connection import SessionLocal
from database.models import Email, Document, Tender
import json

def analyze_tnd_00001():
    db = SessionLocal()
    try:
        tid = 'TND-2026-00001'
        print(f"--- Database Analysis for {tid} ---")
        
        # 1. Tender Info
        tender = db.query(Tender).filter(Tender.tender_id == tid).first()
        if tender:
            print(f"Source: {tender.source}")
            print(f"Created At: {tender.created_at}")
        
        # 2. Email Info
        email = db.query(Email).filter(Email.tender_id == tid).first()
        if email:
            print(f"\nAssociated Email:")
            print(f"  ID: {email.id}")
            print(f"  Subject: {email.subject}")
            print(f"  Sender: {email.sender}")
            print(f"  Body (partial): {email.body[:200]}...")
        else:
            print("\n[!] No email record directly linked with tender_id in DB.")

        # 3. Document Info
        docs = db.query(Document).filter(Document.tender_id == tid).all()
        print(f"\nDocuments in DB ({len(docs)}):")
        for d in docs:
            print(f"  - {d.filename}")
            print(f"    Category: {d.category}")
            print(f"    Source Path: {d.file_path}")
            print(f"    Classification Confidence: {d.classification_confidence}")
            print("-" * 20)

    finally:
        db.close()

if __name__ == "__main__":
    analyze_tnd_00001()
