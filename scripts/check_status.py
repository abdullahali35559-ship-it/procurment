from database.connection import SessionLocal
from database.models import Email, Document, Tender, Project

db = SessionLocal()
ids = [222, 223, 224, 225]

try:
    print("=== EMAIL STATUS ===")
    emails = db.query(Email).filter(Email.id.in_(ids)).all()
    for e in emails:
        print(f"ID: {e.id}")
        print(f"  Subject: {e.subject}")
        print(f"  TenderID: {e.tender_id}")
        print(f"  Processed: {e.processed}")
        print(f"  Is Tender: {e.is_tender}")
        print(f"  Confidence: {e.detection_confidence}")
        print("-" * 20)

    print("\n=== TENDER STATUS ===")
    tenders = db.query(Tender).all()
    for t in tenders:
        if t.tender_id in ['TND-2026-00017', 'TND-2026-00018', 'TND-2026-00019']:
            print(f"Tender: {t.tender_id} | Status: {t.status} | Client: {t.client_name}")

    print("\n=== DOCUMENT STATUS ===")
    docs = db.query(Document).all()
    for d in docs:
        if d.tender_id in ['TND-2026-00017', 'TND-2026-00018', 'TND-2026-00019']:
            print(f"TID: {d.tender_id} | File: {d.filename} | Cat: {d.category} | Correct: {d.is_correct}")

    print("\n=== PROJECT STATUS ===")
    projs = db.query(Project).all()
    for p in projs:
        if p.tender_id in ['TND-2026-00017', 'TND-2026-00018', 'TND-2026-00019']:
            print(f"TID: {p.tender_id} | Name: {p.project_name}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
