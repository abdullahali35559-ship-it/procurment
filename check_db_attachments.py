
import sys
import os
import asyncio

# Ensure project root is in sys.path
sys.path.append(os.getcwd())

from config.database import SessionLocal
from database.models import Attachment

def check_attachments():
    db = SessionLocal()
    try:
        attachments = db.query(Attachment).all()
        print(f"Total attachments in DB: {len(attachments)}")
        for att in attachments:
            print(f"ID: {att.id}, Name: {att.filename}, Thread: {att.thread_id}")
    finally:
        db.close()

if __name__ == "__main__":
    check_attachments()
