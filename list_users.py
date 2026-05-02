from database.connection import SessionLocal
from database.models import User

db = SessionLocal()
users = db.query(User).all()
print("ID | EMAIL | ROLE | NAME")
print("-" * 40)
for u in users:
    print(f"{u.id} | {u.email} | {u.role} | {u.full_name}")
db.close()
