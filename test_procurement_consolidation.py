import sys
import os
sys.path.append('.')

from agents.procurement_agent.procurement_generator import ProcurementGenerator
from config.settings import REQUIRED_DOCUMENTS

def test_consolidation():
    print("--- Testing Procurement Consolidation & Mandatory Categories ---")
    
    # 1. Verify REQUIRED_DOCUMENTS
    print(f"Mandatory Categories in settings: {len([k for k,v in REQUIRED_DOCUMENTS.items() if v])}")
    for cat, req in REQUIRED_DOCUMENTS.items():
        print(f"  - {cat}: {'REQUIRED' if req else 'OPTIONAL'}")
    
    # 2. Mock missing documents (only 1 present)
    tender_id = "TND-TEST-CONSOLIDATED"
    documents = [
        {"category": "01_Instructions", "is_correct": True}
    ]
    
    procurement_gen = ProcurementGenerator()
    completeness = procurement_gen.check_completeness(tender_id, documents)
    
    missing = completeness.get('missing', [])
    incorrect = completeness.get('incorrect', [])
    
    print(f"\nDetection Results:")
    print(f"  Missing Categories: {missing}")
    print(f"  Incorrect Categories: {incorrect}")
    
    if len(missing) == 6:
        print("SUCCESS: 6 categories correctly identified as missing (out of 7).")
    else:
        print(f"FAILURE: Expected 6 missing, got {len(missing)}")

    # 3. Simulate consolidated Procurement generation
    print("\nSimulating Consolidated Procurement Generation...")
    metadata = {
        'client_name': "Verification Team",
        'tender_reference': "REF-12345"
    }
    
    procurement_draft = procurement_gen.generate_consolidated_procurement_draft(
        tender_id=tender_id,
        missing_categories=missing,
        incorrect_categories=incorrect,
        tender_metadata=metadata
    )
    
    print(f"\nGenerated Procurement Draft:")
    print(f"  Subject: {procurement_draft.get('subject')}")
    print(f"  Body (partial):\n{procurement_draft.get('body')[:500]}...")
    
    # Check if multiple categories are mentioned in body (simple string check)
    body = procurement_draft.get('body', '').lower()
    found_count = 0
    keywords = ["bill of quantities", "boq", "drawings", "specifications", "scope of work", "commercial", "standards"]
    for k in keywords:
        if k in body:
            found_count += 1
    
    print(f"\nKeywords found in consolidated body: {found_count}")
    if found_count >= 3:
        print("SUCCESS: Procurement body contains multiple missing items.")
    else:
        print("WARNING: Procurement body might not be listing all items clearly.")

if __name__ == "__main__":
    test_consolidation()
