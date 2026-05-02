import os
import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

from config.database import SessionLocal
from database.models import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n" + "="*50)
        print(f"{'EMAIL':<25} | {'ROLE':<15} | {'ACTIVE':<10}")
        print("-" * 50)
        for u in users:
            print(f"{u.email:<25} | {str(u.role):<15} | {u.is_active}")
        print("="*50 + "\n")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
