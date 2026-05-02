from database.connection import SessionLocal
from database.models import AuditLog
from sqlalchemy import desc

db = SessionLocal()
try:
    logs = db.query(AuditLog).filter(AuditLog.action.like("PROGRESS:%")).order_by(desc(AuditLog.timestamp)).limit(5).all()
    print(f"Found {len(logs)} progress logs:")
    for log in logs:
        print(f"[{log.timestamp}] {log.action} - {log.details}")
finally:
    db.close()
