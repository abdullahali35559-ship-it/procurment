from database.connection import SessionLocal
from database.models import Email, Document, Tender, Project

db = SessionLocal()

try:
    print("=== TENDER TO EMAIL MAPPING ===")
    tenders = db.query(Tender).filter(Tender.tender_id.like('TND-2026-000%')).all()
    for t in tenders:
        emails = db.query(Email).filter(Email.tender_id == t.tender_id).all()
        docs = db.query(Document).filter(Document.tender_id == t.tender_id).all()
        print(f"\nTender: {t.tender_id} | Project: {t.project_name}")
        print(f"  Emails: {[(e.id, e.subject) for e in emails]}")
        print(f"  Docs: {[d.original_filename for d in docs]}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
