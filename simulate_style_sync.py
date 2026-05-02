import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.procurement_agent.style_agent import StyleAgent

def simulate_background_sync(provider="Gmail"):
    print(f"\n[SYSTEM] Starting Writing Style Synchronization for provider: {provider}")
    print(f"[SYSTEM] Connection established with {provider} OAuth2...")
    
    time.sleep(1)
    print(f"[INFO] Fetching last 50 sent emails from {provider} 'Sent Items'...")
    
    # Mock emails
    mock_emails = [
        {"subject": "Project Update", "body": "Hi team, we are making good progress on the Procurement. Let's touch base tomorrow. Best, Abdullah."},
        {"subject": "Meeting Request", "body": "Hello, can we schedule a call for Friday? I have some questions regarding the scope. Regards, Abdullah."},
        {"subject": "Inquiry", "body": "Hi there, please find the documents attached. Let me know if you need anything else. Best, Abdullah."}
    ]
    
    for i in range(1, 4):
        time.sleep(0.5)
        print(f"  --> Downloading email {i}/3: '{mock_emails[i-1]['subject']}'")

    print("\n[AI AGENT] Emails downloaded. Starting stylistic pattern analysis...")
    time.sleep(1)
    
    style_agent = StyleAgent()
    guide = style_agent.extract_style_from_emails(mock_emails)
    
    print("\n[AI AGENT] Analysis complete! New patterns identified:")
    print("-" * 50)
    print(guide)
    print("-" * 50)
    
    print(f"\n[SYSTEM] Writing Style Guide updated in Database for current user.")
    print("[SYSTEM] Background sync finished successfully.")

if __name__ == "__main__":
    # Test for Gmail
    simulate_background_sync("Gmail")
    
    # Test for Outlook
    time.sleep(1)
    simulate_background_sync("Outlook")
