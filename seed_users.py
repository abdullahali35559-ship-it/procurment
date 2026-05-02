from database.connection import SessionLocal
from database.models import User
from api.main import get_password_hash

db = SessionLocal()

accounts = [
    ('user123', 'user12345', 'user'),
    ('admin', 'admin123', 'admin'),
    ('admin@123', 'admin123', 'admin'),
    ('superadmin', 'superadmin123', 'superadmin')
]

for email, pwd, role in accounts:
    u = db.query(User).filter(User.email == email).first()
    if u:
        u.password_hash = get_password_hash(pwd)
    else:
        new_u = User(email=email, password_hash=get_password_hash(pwd), role=role)
        db.add(new_u)

db.commit()
db.close()
print("Saray accounts seed ho gaye: user123, admin, superadmin")
