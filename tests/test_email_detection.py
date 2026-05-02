"""
Test Email Detection Module
"""
import sys
sys.path.append('..')

from agents.procurement_agent.email_detector import EmailDetector

def test_tender_email():
    """Test with tender email"""
    detector = EmailDetector()
    
    result = detector.detect_tender_email(
        email_id="test_001",
        subject="Procurement-NEOM-2026-001 - MEP Package",
        sender="tenders@neom.com",
        body="Please submit your quotation for MEP works at Zone A"
    )
    
    print("Test 1 - Tender Email:")
    print(f"  ✅ Is Tender: {result['is_tender']}")
    print(f"  ✅ Confidence: {result['confidence']}")
    print(f"  ✅ Keywords: {result['keywords_found']}")
    print()
    
    return result['is_tender']

def test_non_tender_email():
    """Test with non-tender email"""
    detector = EmailDetector()
    
    result = detector.detect_tender_email(
        email_id="test_002",
        subject="Team Meeting Friday",
        sender="hr@company.com",
        body="Reminder for weekly sync meeting"
    )
    
    print("Test 2 - Non-Tender Email:")
    print(f"  ✅ Is Tender: {result['is_tender']}")
    print(f"  ✅ Confidence: {result['confidence']}")
    print()
    
    return not result['is_tender']

if __name__ == "__main__":
    print("=== Testing Email Detection ===\n")
    
    test1_passed = test_tender_email()
    test2_passed = test_non_tender_email()
    
    if test1_passed and test2_passed:
        print("✅ All email detection tests passed!")
    else:
        print("❌ Some tests failed!")
