import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.database import SessionLocal
from database.models import User

def check_users():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"Total Users Found: {len(users)}")
    for u in users:
        print(f" - {u.email} (Role: {u.role})")
    db.close()

if __name__ == "__main__":
    check_users()
