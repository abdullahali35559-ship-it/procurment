"""
Test Outlook Connection
Debug IMAP connection to Outlook
"""
from imapclient import IMAPClient
import ssl

def test_outlook():
    """Test Outlook IMAP connection"""
    
    # Settings to test
    configs = [
        {
            'name': 'Outlook (outlook.office365.com)',
            'host': 'outlook.office365.com',
            'port': 993,
            'user': 'aimicrossrlsoft@outlook.com',
            'password': 'inuspowjodyvyhru'
        },
        {
            'name': 'Outlook (imap-mail.outlook.com)',
            'host': 'imap-mail.outlook.com',
            'port': 993,
            'user': 'aimicrossrlsoft@outlook.com',
            'password': 'inuspowjodyvyhru'
        }
    ]
    
    for config in configs:
        print(f"\n{'=' * 60}")
        print(f"Testing: {config['name']}")
        print(f"{'=' * 60}")
        print(f"Host: {config['host']}")
        print(f"Port: {config['port']}")
        print(f"User: {config['user']}")
        print(f"Password: {config['password'][:4]}...{config['password'][-4:]}")
        print()
        
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            # Connect
            print("Connecting...")
            client = IMAPClient(config['host'], port=config['port'], 
                              ssl_context=ssl_context)
            
            # Login
            print("Logging in...")
            client.login(config['user'], config['password'])
            
            print("✅ SUCCESS! Connected to Outlook")
            
            # List folders
            folders = client.list_folders()
            print(f"\nFolders found: {len(folders)}")
            for flags, delimiter, name in folders[:5]:
                print(f"  - {name}")
            
            client.logout()
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            print()
    
    return False

if __name__ == "__main__":
    test_outlook()
