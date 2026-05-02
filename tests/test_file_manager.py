"""
Test File Manager Module
"""
import sys
sys.path.append('..')

from agents.procurement_agent.file_manager import FileManager, generate_tender_id
import os

def test_file_manager():
    """Test file manager functionality"""
    
    print("=== File Manager Test ===\n")
    
    # Generate tender ID
    tender_id = generate_tender_id()
    print(f"Step 1: Generated Tender ID: {tender_id}")
    
    # Cleanup if exists from previous test
    import shutil
    test_path = f"./storage/tenders/{tender_id}"
    if os.path.exists(test_path):
        # Remove read-only attributes before deletion (Windows)
        if os.name == 'nt':
            os.system(f'attrib -r "{test_path}\\*" /s')
        shutil.rmtree(test_path, ignore_errors=True)
    
    # Create folder structure
    file_mgr = FileManager()
    base_path = file_mgr.create_folder_structure(tender_id)
    print(f"Step 2: ✅ Folder structure created at: {base_path}")
    
    # Verify folders exist
    folders = [
        "01_Instructions",
        "02_Scope_of_Work",
        "03_Drawings",
        "04_Specifications",
        "05_BOQ",
        "06_Standards",
        "07_Commercial",
        "08_Output"
    ]
    
    all_exist = True
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        if os.path.exists(folder_path):
            print(f"  ✅ {folder}")
        else:
            print(f"  ❌ {folder} NOT FOUND")
            all_exist = False
    
    # Test file save
    print("\nStep 3: Testing file save...")
    test_data = b"This is a test tender document with some content"
    result = file_mgr.save_file(
        file_data=test_data,
        tender_id=tender_id,
        category="01_Instructions",
        original_filename="test_document.txt"
    )
    
    print(f"  ✅ File saved:")
    print(f"     Path: {result['path']}")
    print(f"     Hash: {result['hash'][:16]}...")
    print(f"     Size: {result['size']} bytes")
    
    # Verify file exists
    if os.path.exists(result['path']):
        print(f"  ✅ File verified at: {result['path']}")
        
        # Verify file is read-only (on Windows)
        if os.name == 'nt':
            import stat
            file_stat = os.stat(result['path'])
            if not (file_stat.st_mode & stat.S_IWRITE):
                print(f"  ✅ File is read-only")
            else:
                print(f"  ⚠️ File is NOT read-only")
    
    print("\n✅ File manager test completed!")
    return all_exist

if __name__ == "__main__":
    test_file_manager()
