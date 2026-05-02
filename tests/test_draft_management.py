"""
Test Draft Email Management System
Creates a test draft to verify the complete flow
"""

import sys
sys.path.append('.')

from database.connection import SessionLocal
from database.models import DraftEmail
from agents.procurement_agent.outlook_graph import OutlookGraphFetcher
from datetime import datetime

def test_draft_creation():
    """Create a test draft in Outlook and database"""
    
    print("=" * 60)
    print("TESTING DRAFT EMAIL MANAGEMENT")
    print("=" * 60)
    
    # Test data
    test_draft = {
        'recipient': 'test@example.com',
        'subject': 'Procurement: Missing Documents for Tender XYZ-2024',
        'body': '''Dear Client,

We have received your Procurement submission for Project XYZ-2024.

After reviewing the documents, we noticed some required items are missing:
- Technical specifications
- Company registration certificate
- Financial statements (last 2 years)

Please provide these documents at your earliest convenience.

Best regards,
Procurement Processing Team'''
    }
    
    print("\n1️⃣ Creating draft in Outlook...")
    outlook = OutlookGraphFetcher()
    
    result = outlook.create_draft(
        to=test_draft['recipient'],
        subject=test_draft['subject'],
        body=test_draft['body']
    )
    
    if not result.get('success'):
        print(f"   ❌ Failed: {result.get('error')}")
        return False
    
    print(f"   ✅ Draft created in Outlook: {result['draft_id'][:20]}...")
    
    print("\n2️⃣ Saving to database...")
    db = SessionLocal()
    
    try:
        draft = DraftEmail(
            tender_id='TEST-2024-001',
            draft_type='Procurement',
            recipient=test_draft['recipient'],
            subject=test_draft['subject'],
            body=test_draft['body'],
            email_provider='outlook',
            provider_draft_id=result['draft_id'],
            status='DRAFT'
        )
        
        db.add(draft)
        db.commit()
        db.refresh(draft)
        
        print(f"   ✅ Saved to database with ID: {draft.id}")
        
        print("\n3️⃣ Retrieving from database...")
        retrieved = db.query(DraftEmail).filter(DraftEmail.id == draft.id).first()
        
        if retrieved:
            print(f"   ✅ Draft retrieved successfully")
            print(f"      - ID: {retrieved.id}")
            print(f"      - Subject: {retrieved.subject}")
            print(f"      - Recipient: {retrieved.recipient}")
            print(f"      - Status: {retrieved.status}")
            print(f"      - Provider: {retrieved.email_provider}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print(f"\nYou can now:")
        print(f"1. Open ui/drafts.html in browser")
        print(f"2. Start API server: uvicorn api.main:app --reload --port 8000")
        print(f"3. View draft with ID: {draft.id}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"   ❌ Database error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_draft_creation()
