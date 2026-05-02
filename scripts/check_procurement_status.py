from database.connection import SessionLocal
from database.models import Document, DraftEmail, Tender
import json

db = SessionLocal()
tids = ['TND-2026-00018', 'TND-2026-00021']

print("=== TENDER STATUS DIAGNOSTIC ===")

for tid in tids:
    tender = db.query(Tender).filter(Tender.tender_id == tid).first()
    docs = db.query(Document).filter(Document.tender_id == tid).all()
    drafts = db.query(DraftEmail).filter(DraftEmail.tender_id == tid).all()
    
    print(f"\nTender: {tid} | Project: {tender.project_name if tender else 'N/A'}")
    print(f"  Docs found ({len(docs)}):")
    for d in docs:
        print(f"    - {d.original_filename} | Category: {d.category} | Correct: {d.is_correct}")
    
    print(f"  Drafts found ({len(drafts)}):")
    for dr in drafts:
        print(f"    - Subject: {dr.subject}")
        print(f"      Status: {dr.status}")
        # body_preview = dr.body[:100] if dr.body else "No Body"
        # print(f"      Body preview: {body_preview}...")

db.close()
