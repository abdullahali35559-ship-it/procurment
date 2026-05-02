"""
Outlook Troubleshooting Script
Tests different authentication methods for Outlook
"""
import sys
import os

# Fix Windows console encoding
if os.name == 'nt':
    os.system('chcp 65001 > nul')

sys.path.append('.')

from imapclient import IMAPClient
import ssl
import getpass

def test_outlook_connection():
    """Test Outlook IMAP with different methods"""
    
    print("=" * 70)
    print("OUTLOOK IMAP CONNECTION TROUBLESHOOTING")
    print("=" * 70)
    print()
    
    email = "aimicrossrlsoft@outlook.com"
    
    # Test configurations
    tests = [
        {
            'name': 'Method 1: App Password (outlook.office365.com)',
            'host': 'outlook.office365.com',
            'port': 993,
            'password': 'inuspowjodyvyhru',
            'description': 'Using app password on primary server'
        },
        {
            'name': 'Method 2: App Password (imap-mail.outlook.com)',
            'host': 'imap-mail.outlook.com',
            'port': 993,
            'password': 'inuspowjodyvyhru',
            'description': 'Using app password on alternate server'
        }
    ]
    
    success = False
    
    for idx, config in enumerate(tests, 1):
        print(f"\n{'=' * 70}")
        print(f"Test {idx}: {config['name']}")
        print(f"{'=' * 70}")
        print(f"Description: {config['description']}")
        print(f"Host: {config['host']}")
        print(f"Port: {config['port']}")
        print(f"Email: {email}")
        print(f"Password: {config['password'][:4]}...{config['password'][-4:]}")
        print()
        
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            print("Step 1: Creating connection...")
            client = IMAPClient(config['host'], port=config['port'], 
                              ssl_context=ssl_context)
            print("  ✅ Connection established")
            
            print("Step 2: Attempting login...")
            client.login(email, config['password'])
            print("  ✅ LOGIN SUCCESSFUL!")
            
            # Get capabilities
            print("\nStep 3: Checking server capabilities...")
            capabilities = client.capabilities()
            print(f"  Server capabilities: {capabilities}")
            
            # List folders
            print("\nStep 4: Listing folders...")
            folders = client.list_folders()
            print(f"  ✅ Found {len(folders)} folders:")
            for flags, delimiter, name in folders[:5]:
                print(f"    - {name}")
            
            # Select INBOX
            print("\nStep 5: Selecting INBOX...")
            client.select_folder('INBOX')
            print("  ✅ INBOX selected successfully")
            
            client.logout()
            
            print("\n" + "=" * 70)
            print(f"✅ SUCCESS! Method {idx} works!")
            print(f"Use these settings in .env:")
            print(f"OUTLOOK_HOST={config['host']}")
            print(f"OUTLOOK_PORT={config['port']}")
            print("=" * 70)
            
            success = True
            break
            
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            print()
    
    if not success:
        print("\n" + "=" * 70)
        print("❌ ALL METHODS FAILED")
        print("=" * 70)
        print("\nPOSSIBLE CAUSES:")
        print("1. Personal Outlook accounts don't support app passwords for IMAP")
        print("2. You need an Office 365 business/enterprise account")
        print("3. Try disabling 2FA and using regular password")
        print()
        print("SOLUTION OPTIONS:")
        print()
        print("Option A: Try Regular Password (2FA must be OFF)")
        print("-" * 70)
        
        try_regular = input("\nWant to try with regular password? (y/n): ").lower()
        
        if try_regular == 'y':
            print("\n⚠️  IMPORTANT: Two-Factor Authentication must be DISABLED")
            print("   Go to: https://account.microsoft.com/security")
            print("   Turn OFF: Two-step verification")
            print()
            
            regular_pwd = getpass.getpass("Enter your Outlook login password: ")
            
            print("\nTesting with regular password...")
            
            for host in ['outlook.office365.com', 'imap-mail.outlook.com']:
                try:
                    print(f"\nTrying {host}...")
                    ssl_context = ssl.create_default_context()
                    client = IMAPClient(host, port=993, ssl_context=ssl_context)
                    client.login(email, regular_pwd)
                    
                    print(f"✅ SUCCESS with regular password on {host}!")
                    print(f"\nUpdate .env with:")
                    print(f"OUTLOOK_HOST={host}")
                    print(f"OUTLOOK_PASSWORD={regular_pwd}")
                    
                    client.logout()
                    return
                    
                except Exception as e:
                    print(f"❌ Failed: {e}")
        
        print("\n" + "=" * 70)
        print("RECOMMENDATION: Use Gmail (already working perfectly)")
        print("=" * 70)
        print("\nTo switch back to Gmail:")
        print("1. Edit .env")
        print("2. Set: EMAIL_PROVIDER=gmail")
        print("3. Run: .\\process_emails.bat")

if __name__ == "__main__":
    test_outlook_connection()
