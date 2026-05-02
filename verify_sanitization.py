import re
import os

def sanitize_filename(filename: str) -> str:
    if not filename:
        return "unnamed_file"
    s = re.sub(r'[\\/:*?"<>|]', '_', filename)
    s = re.sub(r'[\s]+', ' ', s).strip()
    return s

# Test cases
test_cases = [
    ("Bill:of:Quantities.pdf", "Bill_of_Quantities.pdf"),
    ("Folder/Subfolder/File.txt", "Folder_Subfolder_File.txt"),
    ("Crazy*Name?.zip", "Crazy_Name_.zip"),
    ("  Spaces  Everywhere  .doc  ", "Spaces Everywhere .doc"),
    ("", "unnamed_file"),
    ("Valid-Name_123.xlsx", "Valid-Name_123.xlsx"),
    ("Multiple ::: Colons.pdf", "Multiple ___ Colons.pdf")
]

print("Verifying sanitize_filename...")
success = True
for input_name, expected in test_cases:
    result = sanitize_filename(input_name)
    if result == expected:
        print(f"✅ '{input_name}' -> '{result}'")
    else:
        print(f"❌ '{input_name}' -> '{result}' (Expected: '{expected}')")
        success = False

if success:
    print("\nSanitization Logic: PASS")
else:
    print("\nSanitization Logic: FAIL")
