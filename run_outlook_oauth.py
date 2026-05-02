"""
Outlook OAuth2 - Auto Browser Opening (Gmail-style)
Automatically opens browser for authentication like Gmail
"""

import os
import webbrowser
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
from msal import ConfidentialClientApplication

load_dotenv()

# Outlook credentials
OUTLOOK_CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID") or os.getenv("AZURE_CLIENT_ID")
OUTLOOK_CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET") or os.getenv("AZURE_CLIENT_SECRET")
OUTLOOK_TENANT_ID = os.getenv("OUTLOOK_TENANT_ID", "common") or os.getenv("AZURE_TENANT_ID", "common")

# Use the REGISTERED redirect URI from Azure
REDIRECT_URI = "http://localhost:5001/oauth/callback"
AUTHORITY = f"https://login.microsoftonline.com/{OUTLOOK_TENANT_ID}"

# Scopes (offline_access is auto-added by MSAL)
SCOPES = [
    'https://graph.microsoft.com/Mail.ReadWrite',
    'https://graph.microsoft.com/Mail.Send',
    'https://graph.microsoft.com/IMAP.AccessAsUser.All',
    'https://graph.microsoft.com/Calendars.ReadWrite'
]

TOKEN_FILE = ".outlook_oauth_token.json"
auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth2 callback"""
    
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            
            # Beautiful success page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: 'Segoe UI', -apple-system, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 2rem;
                    }
                    .container {
                        background: white;
                        padding: 3rem;
                        border-radius: 20px;
                        box-shadow: 0 25px 70px rgba(0,0,0,0.3);
                        text-align: center;
                        max-width: 500px;
                        animation: slideIn 0.5s ease;
                    }
                    @keyframes slideIn {
                        from { transform: translateY(-50px); opacity: 0; }
                        to { transform: translateY(0); opacity: 1; }
                    }
                    .success-icon {
                        width: 100px;
                        height: 100px;
                        background: linear-gradient(135deg, #10b981, #059669);
                        border-radius: 50%;
                        margin: 0 auto 1.5rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 4rem;
                        animation: bounce 0.6s ease;
                    }
                    @keyframes bounce {
                        0%, 100% { transform: scale(1); }
                        50% { transform: scale(1.1); }
                    }
                    h1 {
                        color: #1f2937;
                        font-size: 2rem;
                        margin-bottom: 1rem;
                    }
                    p {
                        color: #6b7280;
                        margin-bottom: 2rem;
                        line-height: 1.8;
                        font-size: 1.1rem;
                    }
                    .btn {
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        border: none;
                        padding: 1rem 3rem;
                        border-radius: 10px;
                        font-size: 1.1rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: transform 0.2s;
                    }
                    .btn:hover {
                        transform: translateY(-2px);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✓</div>
                    <h1>🎉 Authentication Successful!</h1>
                    <p>
                        Your <strong>Outlook</strong> account has been connected successfully.<br>
                        You can now close this window and return to the terminal.
                    </p>
                    <button class="btn" onclick="window.close()">Close Window</button>
                </div>
                <script>
                    // Auto-close after 5 seconds
                    setTimeout(() => window.close(), 5000);
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Error page
            error = params.get('error_description', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        background: linear-gradient(135deg, #fee, #fcc);
                    }}
                    .error {{
                        background: white;
                        padding: 3rem;
                        border-radius: 16px;
                        text-align: center;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    }}
                    h1 {{ color: #dc2626; }}
                    p {{ color: #666; margin-top: 1rem; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>❌ Authentication Failed</h1>
                    <p>{error}</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def main():
    """Main OAuth2 flow"""
    print("=" * 70)
    print("🔐 Outlook OAuth2 - Auto Browser (Gmail-Style)")
    print("=" * 70)
    
    # Validate credentials
    if not OUTLOOK_CLIENT_ID or not OUTLOOK_CLIENT_SECRET:
        print("\n❌ ERROR: Missing Outlook credentials!")
        print("\nSet in .env file:")
        print("  OUTLOOK_CLIENT_ID=your_app_id")
        print("  OUTLOOK_CLIENT_SECRET=your_secret")
        print("  OUTLOOK_TENANT_ID=common")
        return
    
    print(f"\n📋 Configuration:")
    print(f"   Client ID: {OUTLOOK_CLIENT_ID[:20]}...")
    print(f"   Tenant: {OUTLOOK_TENANT_ID}")
    print(f"   Redirect URI: {REDIRECT_URI}")
    print(f"   Scopes: {', '.join(SCOPES)}")
    
    # Create MSAL app
    app = ConfidentialClientApplication(
        OUTLOOK_CLIENT_ID,
        authority=AUTHORITY,
        client_credential=OUTLOOK_CLIENT_SECRET
    )
    
    # Get authorization URL
    auth_url = app.get_authorization_request_url(
        SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    print(f"\n🌐 Opening browser automatically...")
    print(f"\nIf browser doesn't open, copy this URL:")
    print(f"{auth_url}\n")
    
    # Auto-open browser (Gmail-style!)
    webbrowser.open(auth_url)
    
    # Extract port from redirect URI
    port = int(REDIRECT_URI.split(':')[2].split('/')[0])
    
    # Start local server
    server = HTTPServer(('localhost', port), CallbackHandler)
    print(f"⏳ Waiting for authentication...")
    print(f"   (Server listening on http://localhost:{port})")
    
    # Wait for callback
    server.handle_request()
    server.server_close()
    
    if auth_code:
        print("\n✅ Authorization code received!")
        print("🔄 Exchanging for access token...")
        
        # Get tokens
        result = app.acquire_token_by_authorization_code(
            auth_code,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        if "access_token" in result:
            # Add expiry timestamp
            from datetime import datetime
            result["expires_at"] = datetime.now().timestamp() + result["expires_in"]
            
            # Save tokens
            with open(TOKEN_FILE, "w") as f:
                json.dump(result, f, indent=2)
            
            print("\n" + "=" * 70)
            print("🎉 SUCCESS! Outlook Connected!")
            print("=" * 70)
            print(f"✅ Token saved: {TOKEN_FILE}")
            print(f"✅ Expires in: {result.get('expires_in', 0) // 60} minutes")
            print(f"✅ Refresh token: {'Available ✓' if 'refresh_token' in result else 'Not available ✗'}")
            
            # Test the token
            print("\n🧪 Testing token with Microsoft Graph API...")
            import requests
            
            headers = {"Authorization": f"Bearer {result['access_token']}"}
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Authenticated as: {user_data.get('userPrincipalName')}")
                print(f"   Name: {user_data.get('displayName')}")
            else:
                print(f"⚠️  API test: {response.status_code}")
            
            print("\n" + "=" * 70)
            print("✅ Ready to use Outlook in Procurement Agent!")
            print("=" * 70)
            
        else:
            print("\n" + "=" * 70)
            print("❌ Failed to get access token")
            print("=" * 70)
            print(f"Error: {result.get('error', 'Unknown')}")
            print(f"Description: {result.get('error_description', 'N/A')}")
            
    else:
        print("\n❌ No authorization code received")
        print("   Authentication was cancelled")


if __name__ == "__main__":
    main()
