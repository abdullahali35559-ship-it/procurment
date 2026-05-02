import os
import sys
import shutil
sys.path.append('.')

from agents.procurement_agent.procurement_generator import ProcurementGenerator
from config.settings import STORAGE_PATH

def test_physical_check():
    print("--- Testing Procurement Physical Folder Check ---")
    
    tender_id = "TND-SYNC-TEST"
    tender_path = os.path.join(STORAGE_PATH, tender_id)
    boq_folder = os.path.join(tender_path, "05_BOQ")
    
    # Setup: Create folder and a dummy file
    os.makedirs(boq_folder, exist_ok=True)
    dummy_file = os.path.join(boq_folder, "test_boq.xlsx")
    with open(dummy_file, 'w') as f:
        f.write("test content")
    
    print(f"Created physical file at: {dummy_file}")
    
    # 1. Run check with EMPTY documents list (DB simulation: no records)
    procurement_gen = ProcurementGenerator()
    completeness = procurement_gen.check_completeness(tender_id, [])
    
    missing = completeness.get('missing', [])
    print(f"\nDetection Results (DB is empty):")
    print(f"  Missing Categories: {missing}")
    
    # 05_BOQ should NOT be in missing because it's physically present
    if "05_BOQ" not in missing:
        print("SUCCESS: 05_BOQ correctly detected as present physically.")
    else:
        print("FAILURE: 05_BOQ marked as missing despite physical presence.")

    # Cleanup
    shutil.rmtree(tender_path)
    print("\nCleanup complete.")

if __name__ == "__main__":
    test_physical_check()
