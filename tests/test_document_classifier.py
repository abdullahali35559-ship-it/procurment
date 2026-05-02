"""
Test Document Classifier Module
"""
import sys
sys.path.append('..')

from agents.procurement_agent.document_classifier import DocumentClassifier
import os

def test_classification():
    """Test document classification"""
    
    classifier = DocumentClassifier()
    
    # Create test file
    test_content = """
INSTRUCTIONS TO TENDERERS

Tender Reference: Procurement-NEOM-2026-001
Submission Deadline: February 15, 2026 at 15:00 GMT+3

All tenderers must submit:
1. Technical proposal
2. Commercial proposal
3. Company registration documents
4. Financial statements

Please ensure all documents are submitted before the deadline.
"""
    
    test_file = "sample_data/test_instructions.txt"
    os.makedirs("sample_data", exist_ok=True)
    
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # Classify
    result = classifier.classify_document(
        filename="Tender_Instructions.txt",
        file_path=test_file
    )
    
    print("=== Document Classification Test ===\n")
    print(f"  ✅ Category: {result['category']}")
    print(f"  ✅ Confidence: {result['confidence']:.2f}")
    print(f"  ✅ Reasoning: {result['reasoning']}")
    print(f"  ✅ Keywords: {result['keywords_matched']}")
    print()
    
    # Cleanup
    os.remove(test_file)
    
    # Verify correct category
    if result['category'] == "01_Instructions":
        print("✅ Classification test passed!")
        return True
    else:
        print(f"❌ Expected 01_Instructions, got {result['category']}")
        return False

if __name__ == "__main__":
    test_classification()
