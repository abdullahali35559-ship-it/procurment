from database.connection import SessionLocal
from database.models import Email, Document, Tender, Project

db = SessionLocal()

with open('debug_mappings.txt', 'w', encoding='utf-8') as f:
    f.write("=== TENDER TO EMAIL MAPPING ===\n")
    tenders = db.query(Tender).filter(Tender.tender_id.like('TND-2026-0002%')).all()
    for t in tenders:
        emails = db.query(Email).filter(Email.tender_id == t.tender_id).all()
        docs = db.query(Document).filter(Document.tender_id == t.tender_id).all()
        f.write(f"\nTender: {t.tender_id} | Project: {t.project_name}\n")
        f.write(f"  Emails: {[(e.id, e.subject) for e in emails]}\n")
        f.write(f"  Docs: {[d.original_filename for d in docs]}\n")

db.close()
print("Dump complete to debug_mappings.txt")
