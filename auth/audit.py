from sqlalchemy.orm import Session
from database.models import AuditLog
from typing import Optional, Any
from datetime import datetime

def log_action(db: Session, user_id: Optional[int], action: str, details: Optional[Any] = None, thread_id: Optional[str] = None, ip_address: Optional[str] = None):
    """
    Log an action to the audit_log table.
    """
    try:
        new_log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            thread_id=thread_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.add(new_log)
        db.commit()
        return True
    except Exception as e:
        print(f"Error logging action: {e}")
        db.rollback()
        return False
