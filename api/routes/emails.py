from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import json
import os
import msal
from pathlib import Path
from config.database import get_db
from database.models import User, Email
from auth.dependencies import get_current_user
from api.tasks import sync_user_writing_style
from config.oauth_config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, SCOPES, TOKEN_FILE, REDIRECT_URI

# Gmail Config
from google_auth_oauthlib.flow import Flow
from config.gmail_oauth_config import (
    GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REDIRECT_URI, GMAIL_SCOPES
)

router = APIRouter(tags=["emails"])

# State storage for OAuth (simplified, should be in Redis/DB in prod)
oauth_sessions = {}

def get_msal_app():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority, client_credential=CLIENT_SECRET
    )

@router.get("/api/oauth/login")
@router.get("/api/outlook/oauth/login")
async def outlook_oauth_login():
    msal_app = get_msal_app()
    # Use REDIRECT_URI from config which matches .env
    auth_url = msal_app.get_authorization_request_url(list(SCOPES), redirect_uri=REDIRECT_URI)
    return {"auth_url": auth_url}

@router.get("/api/oauth/callback")
@router.get("/api/outlook/oauth/callback")
async def outlook_oauth_callback(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    code = request.query_params.get('code')
    if not code:
        return HTMLResponse("<h1>Error: No code received</h1>", status_code=400)
    
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code, scopes=list(SCOPES), redirect_uri=REDIRECT_URI
    )
    
    if "access_token" in result:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(result, f, indent=2)
        
        user = db.query(User).first()
        if user:
            background_tasks.add_task(sync_user_writing_style, user.id, 'outlook')

        return HTMLResponse(content=f"""
            <html>
                <head>
                    <title>Outlook Connected</title>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
                    <style>
                        body {{ font-family: 'Inter', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f9fafb; }}
                        .card {{ background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 400px; }}
                        .icon {{ font-size: 48px; margin-bottom: 20px; }}
                        h1 {{ color: #111827; margin: 0 0 10px 0; font-size: 24px; }}
                        p {{ color: #6b7280; line-height: 1.5; margin: 0; }}
                        .timer {{ margin-top: 25px; font-size: 14px; color: #9ca3af; }}
                    </style>
                </head>
                <body>
                    <div class="card">
                        <div class="icon">✅</div>
                        <h1>Outlook Connected!</h1>
                        <p>Your executive Procurement agent is now synchronized with your Outlook workspace.</p>
                        <div class="timer">Closing in <span id="sec">3</span>s...</div>
                    </div>
                    <script>
                        let s = 3;
                        setInterval(() => {{
                            s--;
                            document.getElementById('sec').innerText = s;
                            if (s <= 0) window.close();
                        }}, 1000);
                        setTimeout(() => window.close(), 3500);
                    </script>
                </body>
            </html>
        """)
    
    return HTMLResponse(f"<h1>Error: {result.get('error_description')}</h1>", status_code=400)

# GMAIL ROUTES
def get_gmail_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": GMAIL_CLIENT_ID,
                "client_secret": GMAIL_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GMAIL_REDIRECT_URI]
            }
        },
        scopes=GMAIL_SCOPES,
        redirect_uri=GMAIL_REDIRECT_URI
    )

@router.get("/api/gmail/oauth/login")
async def gmail_oauth_login():
    flow = get_gmail_flow()
    auth_url, state = flow.authorization_url(access_type='offline', prompt='consent')
    return {"auth_url": auth_url}

@router.get("/api/gmail/oauth/callback")
async def gmail_oauth_callback(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    code = request.query_params.get('code')
    flow = get_gmail_flow()
    flow.fetch_token(code=code)
    
    # Save credentials
    creds = flow.credentials
    with open('.gmail_oauth_token.json', 'w') as f:
        f.write(creds.to_json())
    
    user = db.query(User).first()
    if user:
        background_tasks.add_task(sync_user_writing_style, user.id, 'gmail')
        
    return HTMLResponse(content=f"""
        <html>
            <head>
                <title>Gmail Connected</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
                <style>
                    body {{ font-family: 'Inter', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f9fafb; }}
                    .card {{ background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 400px; }}
                    .icon {{ font-size: 48px; margin-bottom: 20px; }}
                    h1 {{ color: #111827; margin: 0 0 10px 0; font-size: 24px; }}
                    p {{ color: #6b7280; line-height: 1.5; margin: 0; }}
                    .timer {{ margin-top: 25px; font-size: 14px; color: #9ca3af; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="icon">📩</div>
                    <h1>Gmail Connected!</h1>
                    <p>Authentication successful. The Procurement agent is now connected to your Gmail account.</p>
                    <div class="timer">Closing in <span id="sec">3</span>s...</div>
                </div>
                <script>
                    let s = 3;
                    setInterval(() => {{
                        s--;
                        document.getElementById('sec').innerText = s;
                        if (s <= 0) window.close();
                    }}, 1000);
                    setTimeout(() => window.close(), 3500);
                </script>
            </body>
        </html>
    """)

@router.get("/api/emails")
async def get_emails(thread_id: str = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Email)
    if thread_id:
        query = query.filter(Email.thread_id == thread_id)
    emails = query.order_by(Email.received_at.desc()).all()
    return {"success": True, "data": emails}

@router.get("/api/oauth/status")
@router.get("/api/gmail/oauth/status")
async def get_oauth_status(request: Request):
    outlook_connected = Path(".outlook_oauth_token.json").exists()
    gmail_connected = Path(".gmail_oauth_token.json").exists()
    
    # If the request comes specifically from /api/gmail/oauth/status, return gmail specific status
    if "gmail" in request.url.path:
        return {
            "success": True,
            "status": "connected" if gmail_connected else "disconnected",
            "authenticated": gmail_connected
        }
    
    # Default response for general /api/oauth/status (Outlook uses this too)
    return {
        "success": True,
        "status": "connected" if outlook_connected else "disconnected", # UI looks at .status
        "outlook": "connected" if outlook_connected else "disconnected",
        "gmail": "connected" if gmail_connected else "disconnected",
        "authenticated": gmail_connected or outlook_connected
    }
