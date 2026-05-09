from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.models import User
from config.database import SessionLocal, get_db
from auth.security import get_password_hash, verify_password, create_access_token
from auth.dependencies import get_current_user
from auth.audit import log_action
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Global Cache for Anti-Brute-Force (Industry Standard)
login_attempts = {}

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: Optional[str] = "user"

@router.post("/register")
async def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """Register a new user in PostgreSQL"""
    try:
        # Check if email exists
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = User(
            email=user_data.email,
            full_name=user_data.username,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role or "user"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        log_action(db, user_id=new_user.id, action="register", ip_address=request.client.host)
        return {"success": True, "message": "User registered successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(request: Request, response: Response, db: Session = Depends(get_db)):
    """Login and set HTTP-only session cookie with Brute-Force Shielding"""
    # We use Request to get form data manually or via OAuth2PasswordRequestForm
    from fastapi.security import OAuth2PasswordRequestForm
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    if not username or not password:
        # Fallback for JSON body if needed
        try:
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
        except: pass

    ip = request.client.host
    now = datetime.utcnow()
    
    # ── RATE LIMITING ──
    attempts = [a for a in login_attempts.get(ip, []) if a > now - timedelta(minutes=1)]
    if len(attempts) >= 5:
        log_action(db, user_id=None, action="BRUTE_FORCE_BLOCKED", details={"ip": ip})
        raise HTTPException(status_code=429, detail="Security Alert: Too many login attempts. Wait 1 min.")

    user = db.query(User).filter(User.email == username).first()
    
    if not user or not verify_password(password, user.password_hash):
        # Record failed attempt
        cur_attempts = login_attempts.get(ip, [])
        cur_attempts.append(now)
        login_attempts[ip] = cur_attempts
        
        log_action(db, user_id=None, action="login_failed", details={"email": username}, ip_address=request.client.host)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # Reset attempts on success
    if ip in login_attempts: del login_attempts[ip]

    # Create token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    # Smart Routing Logic
    if user.role in ["admin", "superadmin"]:
        redirect_to = "/admin.html"
    else:
        redirect_to = "/assistant.html"

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    log_action(db, user_id=user.id, action="login_session_started", ip_address=request.client.host)
    
    result = {
        "token_type": "bearer",
        "redirect_url": redirect_to,
        "role": user.role,
        "user_id": user.id
    }
    
    response = JSONResponse(content=result)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        max_age=18000,
        samesite="strict",
        secure=request.url.scheme == "https",
        path="/"
    )
    return response

@router.post("/logout")
async def logout(response: Response):
    """Professional Logout: Wipes the session cookie"""
    response.delete_cookie("access_token")
    return {"detail": "Logged out successfully"}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the current user's profile info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "brand_voice": current_user.brand_voice,
        "custom_instructions": current_user.custom_instructions,
        "writing_style_guide": current_user.writing_style_guide
    }
