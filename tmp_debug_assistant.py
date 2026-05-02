
import sys
import os
sys.path.insert(0, os.getcwd())
from agents.executive.assistant import ExecutiveAssistant
from config.database import SessionLocal

db = SessionLocal()
try:
    ast = ExecutiveAssistant(db)
    query = "What is the deadline for the Riyadh Metro expansion project?"
    context = ast._retrieve_context(query)
    print("--- CONTEXT ---")
    with open('tmp_context.txt', 'w', encoding='utf-8') as f:
        f.write(context)
    print("Done writing context to tmp_context.txt")
    
    # Also check if the specific email is in DB
    from database.models import Email
    email = db.query(Email).filter(Email.subject.ilike('%Riyadh Metro%')).first()
    if email:
        print("\n--- EMAIL 170 DETAILS ---")
        print(f"Subject: {email.subject}")
        print(f"Body: {email.body[:200]}...")
    else:
        print("\n[!] Email 170 not found by subject 'Riyadh Metro'")
finally:
    db.close()
