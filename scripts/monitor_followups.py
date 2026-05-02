import sys
import os
import time
from datetime import datetime, timezone
import email.utils

sys.path.append(os.getcwd())
from agents.procurement_agent.email_fetcher import EmailFetcher
from agents.executive.followup_manager import FollowupManager
from database.connection import SessionLocal
from database.models import Email, AuditLog, Thread

def sync_sent_emails():
    """
    Fetch and store recently sent emails
    """
    from config.settings import EMAIL_PROVIDERS
    
    print("=" * 60)
    print("SENT EMAIL MONITORING - Follow-up Assistant")
    print("=" * 60)

    db = SessionLocal()
    processed_count = 0
    
    for provider in EMAIL_PROVIDERS:
        print(f"\nCHECKING SENT ITEMS: {provider.upper()}...")
        
        try:
            fetcher = EmailFetcher(provider=provider)
            if not fetcher.connect(): continue
            
            # Use the underlying client directly
            client = fetcher.gmail_api_client if provider == 'gmail' else fetcher.outlook_graph
            
            if client and hasattr(client, 'fetch_sent_emails'):
                sent_emails = client.fetch_sent_emails(limit=50)
            else:
                print(f"   [!] Provider {provider} client does not support fetch_sent_emails yet.")
                continue

            if not sent_emails:
                print(f"   No new sent emails from {provider}")
                fetcher.disconnect()
                continue
            
            print(f"   Fetched {len(sent_emails)} sent email(s).")
            
            for email_data in sent_emails:
                email_id = email_data['email_id']
                
                # Check if exists
                existing = db.query(Email).filter(Email.email_id == email_id).first()
                if existing:
                    continue
                
                # Parse date
                received_at = datetime.now(timezone.utc).replace(tzinfo=None)
                if email_data.get('date'):
                    try: received_at = email.utils.parsedate_to_datetime(email_data['date'])
                    except: pass
                
                # Standardize sender string
                sender = email_data.get('sender', 'me')
                
                # Store in emails table with is_sent=True
                new_email = Email(
                    email_id=email_id,
                    subject=email_data['subject'],
                    sender=sender,
                    body=email_data['body'],
                    received_at=received_at,
                    is_sent=True,
                    processed=True # Sent emails don't need "Procurement processing"
                )
                
                # OPTIONAL: Try to link to a thread by subject or recipient if possible
                # For now, we'll rely on the thread_id being passed if it's available in metadata
                # but most sent emails are new entries.
                
                db.add(new_email)
                processed_count += 1
            
            db.commit()
            fetcher.disconnect()
        except Exception as e:
            print(f"[ERROR] Provider {provider} sent items failed: {e}")

    db.close()
    print(f"\nSynced {processed_count} new sent emails.")

def run_analysis():
    """
    Run the FollowupManager logic
    """
    db = SessionLocal()
    print("\nAnalyzing stale threads...")
    manager = FollowupManager(db)
    new_suggestions = manager.generate_suggestions()
    db.close()
    print(f"Generated {new_suggestions} new follow-up suggestion(s).")

if __name__ == "__main__":
    sync_sent_emails()
    run_analysis()
    print("\nFollow-up MONITORING COMPLETE.")
