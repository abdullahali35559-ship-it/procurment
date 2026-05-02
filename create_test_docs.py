import os

def create_dummy_files():
    """Create dummy text files that can be renamed to PDF for testing classification"""
    files = {
        "Scope_of_Work.pdf": "This is a dummy Scope of Work document for NEOM Project. It contains electrical installation details.",
        "BOQ_Materials.pdf": "Item, Description, Quantity, Unit\n1, Copper Cable 10mm, 500, Meter\n2, PVC Conduit, 200, Meter",
        "Instructions.pdf": "Tender Instructions: Please submit your proposal by the deadline. Required documents include BOQ and SOW."
    }
    
    output_dir = "test_docs"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating dummy files in ./{output_dir}...")
    for filename, content in files.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        print(f" - Created {path}")

    print("\n✅ Done! Now attach these files from the 'test_docs' folder to your email.")

if __name__ == "__main__":
    create_dummy_files()
