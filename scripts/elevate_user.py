
import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import SessionLocal
from database.models import User

def elevate_user(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Error: User with email {email} not found.")
            # List all users to help
            all_users = db.query(User).all()
            if all_users:
                print("Available users:")
                for u in all_users:
                    print(f"  - {u.email} (Role: {u.role})")
            return
        
        user.role = 'superadmin'
        user.is_active = True
        db.commit()
        print(f"Success: User {email} has been elevated to superadmin status.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/elevate_user.py <email>")
        # Try to find any user if none provided
        db = SessionLocal()
        user = db.query(User).first()
        if user:
            print(f"Proposing elevation for first found user: {user.email}")
            elevate_user(user.email)
        db.close()
    else:
        elevate_user(sys.argv[1])
