from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from database.models import (
        Contact, Topic, Tag, Thread, Email, Attachment, DraftReply, 
        AuditLog, AssistantConversation, AssistantChat, User, FollowupTask
    )
    Base.metadata.create_all(bind=engine)
