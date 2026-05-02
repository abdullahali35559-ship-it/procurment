"""
Database Migration: Add draft_emails table
Run this to create the draft_emails table in PostgreSQL
"""

CREATE_DRAFT_EMAILS_TABLE = """
CREATE TABLE IF NOT EXISTS draft_emails (
    id SERIAL PRIMARY KEY,
    tender_id VARCHAR(50),
    draft_type VARCHAR(50),
    
    -- Email details
    recipient VARCHAR(255) NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    
    -- Provider details
    email_provider VARCHAR(20),
    provider_draft_id VARCHAR(255),
    
    -- Status and metadata
    status VARCHAR(50) DEFAULT 'DRAFT',
    created_by VARCHAR(50) DEFAULT 'RFQ_AGENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    
    -- Link to original email
    in_reply_to_email_id VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_draft_emails_tender_id ON draft_emails(tender_id);
CREATE INDEX IF NOT EXISTS idx_draft_emails_status ON draft_emails(status);
CREATE INDEX IF NOT EXISTS idx_draft_emails_provider ON draft_emails(email_provider);
"""

if __name__ == "__main__":
    import sys
    sys.path.append('.')
    
    from database.connection import engine
    from sqlalchemy import text
    
    print("Creating draft_emails table...")
    
    with engine.connect() as conn:
        conn.execute(text(CREATE_DRAFT_EMAILS_TABLE))
        conn.commit()
    
    print("✅ draft_emails table created successfully!")
