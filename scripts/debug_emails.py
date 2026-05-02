"""
Debug script to check email fetching and filtering
"""
import sys
sys.path.append('.')

from agents.procurement_agent.email_fetcher import EmailFetcher

def debug_emails():
    """Debug email fetching"""
    print("=" * 60)
    print("EMAIL DEBUG TOOL")
    print("=" * 60)
    print()
    
    fetcher = EmailFetcher()
    
    if not fetcher.connect():
        print("❌ Connection failed")
        return
    
    try:
        # Select inbox
        fetcher.client.select_folder('INBOX')
        
        # Get ALL unread emails
        messages = fetcher.client.search(['UNSEEN'])
        
        print(f"📬 Found {len(messages)} unread emails\n")
        
        if not messages:
            print("No unread emails to analyze")
            return
        
        # Limit to recent 5
        messages = messages[-5:]
        
        print("Analyzing recent unread emails:\n")
        print("=" * 60)
        
        for idx, msg_id in enumerate(messages, 1):
            print(f"\nEmail #{idx} (ID: {msg_id})")
            print("-" * 60)
            
            # Parse email
            email_data = fetcher._parse_email(msg_id)
            
            if not email_data:
                print("  ❌ Failed to parse")
                continue
            
            # Show details
            print(f"  Subject: {email_data['subject']}")
            print(f"  From: {email_data['sender']}")
            print(f"  Attachments: {len(email_data['attachments'])}")
            
            # Check keywords
            subject_lower = email_data['subject'].lower()
            body_lower = email_data['body'][:200].lower()
            
            print(f"\n  Subject (lowercase): {subject_lower}")
            print(f"  Body preview: {body_lower[:100]}...")
            
            # Test each keyword
            print(f"\n  Keyword matches:")
            keywords = ['procurement', 'tender', 'itt', 'bid', 'quotation', 'request for quote']
            
            matched = False
            for keyword in keywords:
                in_subject = keyword in subject_lower
                in_body = keyword in body_lower
                
                if in_subject or in_body:
                    matched = True
                    print(f"    ✅ '{keyword}' - Found in:", "subject" if in_subject else "body")
                else:
                    print(f"    ❌ '{keyword}' - Not found")
            
            print(f"\n  Is Tender Email: {'✅ YES' if matched else '❌ NO'}")
            print("=" * 60)
        
    finally:
        fetcher.disconnect()

if __name__ == "__main__":
    debug_emails()
