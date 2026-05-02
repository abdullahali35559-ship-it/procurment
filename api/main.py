import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Initialize sys.path to include the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load .env FIRST
load_dotenv()

# Bcrypt Monkey Patch
try:
    import bcrypt
    if not hasattr(bcrypt, "__about__"):
        class About: pass
        about = About()
        about.__version__ = "4.0.0"
        bcrypt.__about__ = about
except ImportError: pass

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

from fastapi import FastAPI, Request, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from config.database import init_db, SessionLocal
from database.models import User
from auth.security import get_password_hash
from api.routes import auth, user, emails, drafts, threads, attachments, contacts, dashboard, assistant, admin

def run_migrations():
    """Ensure database schema is up to date with Self-Healing logic"""
    from sqlalchemy import text
    init_db()
    
    # Structural Drift Check: Ensure critical intelligence columns exist
    db = SessionLocal()
    try:
        # Check if users table has writing_style_guide
        inspector = db.execute(text("SELECT * FROM users LIMIT 1")).keys()
        if 'writing_style_guide' not in inspector:
            print("[INTEGRITY] Structural drift detected. Adding writing_style_guide column...")
            db.execute(text("ALTER TABLE users ADD COLUMN writing_style_guide TEXT"))
        if 'last_style_sync' not in inspector:
            print("[INTEGRITY] Structural drift detected. Adding last_style_sync column...")
            db.execute(text("ALTER TABLE users ADD COLUMN last_style_sync TIMESTAMP"))
        db.commit()
    except Exception as e:
        print(f"[INTEGRITY] Database auto-repair failed: {e}")
    finally:
        db.close()

def init_admin():
    """Seed initial admin users"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@123").first()
        if not admin:
            db.add(User(
                email="admin@123", 
                password_hash=get_password_hash("admin123"), 
                role="admin", 
                full_name="Portal Admin"
            ))
        
        super_user = db.query(User).filter(User.email == "superadmin").first()
        if not super_user:
            db.add(User(
                email="superadmin", 
                password_hash=get_password_hash("superadmin123"), 
                role="superadmin", 
                full_name="System Owner"
            ))
        db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    init_admin()
    yield

app = FastAPI(title="Procurement Agent API", lifespan=lifespan)

# --- Executive Guardian: Pro Security Layers ---
import time
from uuid import uuid4
from collections import defaultdict

# Simple In-Memory Rate Limiter (Anti-Brute Force)
RATE_LIMIT_STORAGE = defaultdict(list)
MAX_REQUESTS = 100 # per 60 seconds
WINDOW_SECONDS = 60

@app.middleware("http")
async def executive_guardian_middleware(request: Request, call_next):
    # 1. Request ID Tracking (Forensics)
    request_id = str(uuid4())
    request.state.request_id = request_id
    
    # 2. Rate Limiting Logic
    client_ip = request.client.host if request.client else "unknown"
    request.state.ip_address = client_ip
    
    now = time.time()
    # Clean old requests
    RATE_LIMIT_STORAGE[client_ip] = [t for t in RATE_LIMIT_STORAGE[client_ip] if now - t < WINDOW_SECONDS]
    
    if len(RATE_LIMIT_STORAGE[client_ip]) >= MAX_REQUESTS:
        return JSONResponse(
            status_code=429, 
            content={"detail": "Too many requests. Protective lockdown engaged."}
        )
    
    RATE_LIMIT_STORAGE[client_ip].append(now)
    
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 3. Security Hardening Headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS (Force HTTPS - Critical for VPS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Strict Content Security Policy (CSP)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://accounts.google.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://accounts.google.com; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Performance Tracking
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    except Exception as e:
        import logging
        logging.error(f"GUARD_ALERT [{request_id}]: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": f"Internal Shield Triggered. TraceID: {request_id}"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Router Inclusion ---
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(emails.router)
app.include_router(drafts.router)
app.include_router(threads.router)
app.include_router(attachments.router)
app.include_router(contacts.router)
app.include_router(dashboard.router)
app.include_router(assistant.router)
app.include_router(admin.router)

# --- Static Files ---
app.mount("/css", StaticFiles(directory="ui/css"), name="css")
app.mount("/js", StaticFiles(directory="ui/js"), name="js")
app.mount("/assets", StaticFiles(directory="ui/assets"), name="assets")
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# --- UI Serving ---
@app.get("/")
def root(): return FileResponse("ui/login.html")

@app.get("/user_portal")
@app.get("/dashboard")
def dashboard_page(): return FileResponse("ui/index.html")

@app.get("/admin_portal")
def admin_portal(): return FileResponse("ui/admin.html")

@app.get("/{page_name}")
async def serve_page(page_name: str):
    clean_name = page_name.replace(".html", "")
    path = Path(f"ui/{clean_name}.html")
    if path.exists(): return FileResponse(path)
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8069)