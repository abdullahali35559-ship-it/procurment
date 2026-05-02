from agents.procurement_agent.reply_generator import ReplyGenerator
import json

def test_missing_attachment_detection():
    print("Testing Smart Detection for Missing Attachments...")
    
    gen = ReplyGenerator()
    
    # Case 1: Mentioned but missing
    sender = "abdullahali35559@gmail.com"
    subject = "Project Alpha Materials"
    body = "Hello, please provide a quotation for the attached BOQ and specifications. We need these by next Friday. Regards, John Doe"
    attachments = [] # NONE PROVIDED
    
    print("\n[Input] Body mentions 'attached BOQ' but attachments list is empty.")
    result = gen.generate_draft(sender, subject, body, attachments)
    
    print("\n[Output] Generated Draft Body:")
    print("-" * 30)
    print(result.get('body'))
    print("-" * 30)
    
    # Verification keywords
    output_body = result.get('body', '').lower()
    found = "missing" in output_body or "provide" in output_body or "attach" in output_body or "notice" in output_body
    
    if found:
        print("\n✅ SUCCESS: Agent detected missing attachment and asked for it.")
    else:
        print("\n❌ FAILURE: Agent did not detect/mention missing attachment.")

if __name__ == "__main__":
    test_missing_attachment_detection()
