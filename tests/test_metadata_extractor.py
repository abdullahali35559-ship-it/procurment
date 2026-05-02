"""
Test Metadata Extractor Module
"""
import sys
sys.path.append('..')

from agents.procurement_agent.metadata_extractor import MetadataExtractor

def test_metadata_extraction():
    """Test metadata extraction from email"""
    
    print("=== Metadata Extraction Test ===\n")
    
    extractor = MetadataExtractor()
    
    # Sample email data
    email_data = {
        "subject": "Procurement-NEOM-2026-001 - MEP Package Zone A",
        "sender": "tenders@neom.com",
        "body": """
Dear Contractor,

We invite you to submit a quotation for MEP works at NEOM Zone A.

Project: Zone A MEP Package
Client: NEOM
Submission Deadline: February 15, 2026 at 15:00 GMT+3
Procurement Deadline: February 1, 2026 at 17:00 GMT+3

Contact: John Doe (john.doe@neom.com)

Please submit your proposal by the deadline.

Best regards,
NEOM Tender Team
"""
    }
    
    # Sample documents
    documents = [
        {"filename": "Tender_Instructions.pdf"},
        {"filename": "BOQ_Zone_A.xlsx"},
        {"filename": "Drawings_MEP.pdf"}
    ]
    
    # Extract metadata
    metadata = extractor.extract_metadata(
        tender_id="TND-2026-00001",
        email_data=email_data,
        documents=documents
    )
    
    print("  ✅ Extracted Metadata:")
    print(f"     Client: {metadata.get('client_name')}")
    print(f"     Project: {metadata.get('project_name')}")
    print(f"     Reference: {metadata.get('tender_reference')}")
    print(f"     Submission Deadline: {metadata.get('submission_deadline')}")
    print(f"     Procurement Deadline: {metadata.get('procurement_deadline')}")
    print(f"     Contact: {metadata.get('contact_person')}")
    print(f"     Email: {metadata.get('contact_email')}")
    print(f"     Trade: {metadata.get('trade')}")
    print(f"     Confidence: {metadata.get('confidence')}")
    
    print("\n✅ Metadata extraction test completed!")
    return True

if __name__ == "__main__":
    test_metadata_extraction()
