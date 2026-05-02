from scripts.process_emails import process_specific_emails
import os

# Target Email IDs
# 222: Drawings (TND-18 part 1)
# 224: Other docs (TND-18 part 2) - Should combine with 222 and NOT generate Procurement
# 227: IT Project Management (TND-21) - Should generate Procurement for missing items and IRRELEVANT flag
# 225: Request for calculation (TND-22) - Drawings.zip
# 214: Request for Quotation (TND-23) - Instruction.pdf

email_ids = [222, 224, 227, 225, 214]

print(f"Starting verification processing for emails: {email_ids}")

try:
    process_specific_emails(email_ids)
    print("\n=== VERIFICATION PROCESSING COMPLETE ===")
except Exception as e:
    print(f"Error during verification: {e}")
