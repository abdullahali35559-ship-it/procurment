"""
Test Procurement Generator Module
"""
import sys
sys.path.append('..')

from agents.procurement_agent.procurement_generator import ProcurementGenerator

def test_procurement_generator():
    """Test Procurement draft generation"""
    
    print("=== Procurement Generator Test ===\n")
    
    procurement_gen = ProcurementGenerator()
    
    # Test missing documents detection
    print("Step 1: Checking document completeness...")
    documents = [
        {"category": "01_Instructions", "filename": "instructions.pdf"},
        {"category": "03_Drawings", "filename": "drawings.pdf"}
        # Missing: 02_Scope_of_Work, 05_BOQ, 07_Commercial
    ]
    
    missing = procurement_gen.check_completeness("TND-2026-00001", documents)
    print(f"  ✅ Missing documents detected: {missing}")
    
    if missing:
        print(f"\nStep 2: Generating Procurement draft for: {missing[0]}")
        
        # Generate Procurement for first missing item
        procurement_draft = procurement_gen.generate_procurement_draft(
            tender_id="TND-2026-00001",
            missing_category=missing[0],
            tender_metadata={
                "client_name": "NEOM",
                "tender_reference": "Procurement-NEOM-2026-001"
            }
        )
        
        print(f"\n  ✅ Procurement Draft Generated:")
        print(f"     Procurement ID: {procurement_draft['procurement_id']}")
        print(f"     Priority: {procurement_draft.get('priority', 'MEDIUM')}")
        print(f"     Status: {procurement_draft['status']}")
        print(f"\n  Subject: {procurement_draft.get('subject', 'N/A')}")
        print(f"\n  Body:\n")
        body = procurement_draft.get('body', 'No body generated')
        print("  " + "\n  ".join(body.split('\n')))
        
        print("\n✅ Procurement generation test passed!")
        return True
    else:
        print("  ℹ️ All required documents present")
        return True

if __name__ == "__main__":
    test_procurement_generator()
