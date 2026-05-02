from database.connection import SessionLocal
from database.models import User
from auth.security import get_password_hash

db = SessionLocal()
u = db.query(User).filter(User.email == 'superadmin').first()
if u:
    u.password_hash = get_password_hash('superadmin123')
    db.commit()
    print("✅ Superadmin password reset to: superadmin123")
else:
    print("❌ Superadmin user not found")
db.close()
