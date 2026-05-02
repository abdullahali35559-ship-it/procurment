from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ARRAY, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

# Association table for Many-to-Many relationship between Email and Tag
email_tags = Table(
    'email_tags',
    Base.metadata,
    Column('email_id', Integer, ForeignKey('emails.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# Association table for Many-to-Many relationship between Thread and Tag
thread_tags = Table(
    'thread_tags',
    Base.metadata,
    Column('thread_id', Integer, ForeignKey('threads.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Contact(Base):
    """Formerly Client"""
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    contact_name = Column(String(255), nullable=False)
    email_domain = Column(String(100))
    contact_emails = Column(ARRAY(Text))
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_contact = Column(DateTime)
    total_interactions = Column(Integer, default=0)
    meta_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topics = relationship('Topic', back_populates='contact')
    threads = relationship('Thread', back_populates='contact')

class Topic(Base):
    """Formerly Project"""
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    topic_name = Column(String(255))
    topic_reference = Column(String(100))
    thread_id = Column(String(50), unique=True)
    status = Column(String(50), default='ACTIVE')
    folder_path = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)
    
    # Relationships
    contact = relationship('Contact', back_populates='topics')
    threads = relationship('Thread', back_populates='topic')

class Tag(Base):
    """New Category/Tag Model"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(20), default='#6366f1') # Default indigo
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    emails = relationship('Email', secondary=email_tags, back_populates='tags')
    threads = relationship('Thread', secondary=thread_tags, back_populates='tags')

class Thread(Base):
    """Formerly Tender"""
    __tablename__ = 'threads'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default='PROCESSING')
    
    # Foreign Keys
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    topic_id = Column(Integer, ForeignKey('topics.id'))
    
    # Details
    subject = Column(Text)
    contact_name = Column(String(255))
    topic_name = Column(String(255))
    thread_reference = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source = Column(String(50))
    source_email = Column(String(255))
    source_sender = Column(String(255))
    
    # Relationships
    contact = relationship('Contact', back_populates='threads')
    topic = relationship('Topic', back_populates='threads')
    tags = relationship('Tag', secondary=thread_tags, back_populates='threads')

class Email(Base):
    __tablename__ = 'emails'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(50), index=True) # Link to Thread.thread_id
    email_id = Column(String(255), unique=True)
    subject = Column(Text)
    sender = Column(String(255))
    recipients = Column(ARRAY(Text))
    body = Column(Text)
    received_at = Column(DateTime(timezone=True))
    is_actionable = Column(Boolean, default=True)
    is_junk = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False) # New: Track outgoing mail
    detection_confidence = Column(Float)
    tags_suggested = Column(ARRAY(Text))
    processed = Column(Boolean, default=False)
    meta_data = Column(JSONB) # New: Store meeting details, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tags = relationship('Tag', secondary=email_tags, back_populates='emails')

class Attachment(Base):
    """Formerly Document"""
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(50), index=True)
    category = Column(String(100)) # e.g. "01_Instructions", "02_Scope_of_Work"
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(Text, nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_size_bytes = Column(Integer)
    doc_type = Column(String(50)) # e.g. "Invoice", "Contract", "Image"
    summary = Column(Text)
    is_correct = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(50))

# Aliases for backward compatibility
Document = Attachment

class DraftReply(Base):
    """Formerly DraftEmail / ProcurementDraft"""
    __tablename__ = 'draft_replies'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(50), index=True)
    draft_type = Column(String(50))  # 'REPLY', 'CLARIFICATION', 'ACKNOWLEDGMENT'
    
    # Email details
    recipient = Column(String(255), nullable=False)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    
    # Provider details (Outlook/Gmail)
    email_provider = Column(String(20))  # 'outlook' or 'gmail'
    provider_draft_id = Column(String(255))  # Draft ID from email provider
    
    # Status and metadata
    status = Column(String(50), default='DRAFT')  # 'DRAFT', 'SENT', 'DELETED'
    created_by = Column(String(50), default='GENERAL_EMAIL_ASSISTANT')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime)
    
    # Link to original email
    in_reply_to_email_id = Column(String(255))
    meta_data = Column(JSONB)
    scheduled_at = Column(DateTime) # For future "Send Later" feature

class FollowupTask(Base):
    """New: Track threads that need following up"""
    __tablename__ = 'followup_tasks'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(50), ForeignKey('threads.thread_id'))
    original_email_id = Column(String(255)) # ID of the sent email we are following up on
    recipient = Column(String(255))
    suggested_body = Column(Text)
    status = Column(String(50), default='PENDING') # PENDING, ACTIONED, IGNORED
    due_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='user') # 'superadmin', 'admin', 'user'
    is_active = Column(Boolean, default=True)
    preferences = Column(JSONB, default=lambda: {})
    
    # Intelligence & Style Settings
    brand_voice = Column(Text) # Raw samples provided by user
    custom_instructions = Column(Text) # Explicit user preferences
    writing_style_guide = Column(Text) # AI analyzed communication style rules
    last_style_sync = Column(DateTime) # Last time background sync ran
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    audit_logs = relationship('AuditLog', back_populates='user')

class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    thread_id = Column(String(50))
    agent = Column(String(50), default='Procurement_AGENT') 
    action = Column(String(100), nullable=False)
    details = Column(JSONB)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='audit_logs')

class AssistantConversation(Base):
    __tablename__ = 'assistant_conversations'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), default='New Conversation')
    mode = Column(String(20), default='enterprise') # 'enterprise' or 'general'
    created_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AssistantChat(Base):
    __tablename__ = 'assistant_chat'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('assistant_conversations.id'), nullable=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Aliases for backward compatibility with Procurement Agent code base
Tender = Thread
DraftEmail = DraftReply
Client = Contact
Project = Topic
ProcurementDraft = DraftReply
