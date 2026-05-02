import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from authlib.jose import jwt
from config.auth_settings import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token with Professional ISS/AUD claims."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iss": "procurement-platform-auth",  # ISSUER Claim
        "aud": "procurement-api-client"      # AUDIENCE Claim
    })
    header = {"alg": JWT_ALGORITHM}
    payload = to_encode
    
    token = jwt.encode(header, payload, JWT_SECRET_KEY)
    return token.decode('utf-8')

def decode_access_token(token: str) -> Optional[Dict]:
    """Decode and verify a JWT access token with Professional standards."""
    if not token or token in ["null", "undefined", "None", ""]:
        return None
    try:
        # Standard Authlib Decode
        claims = jwt.decode(token, JWT_SECRET_KEY)
        claims.validate()
        
        # Explicit Claim Verification for 100% Assurance
        if claims.get("iss") != "procurement-platform-auth" or claims.get("aud") != "procurement-api-client":
            return None
            
        return dict(claims)
    except Exception as e:
        print(f"DEBUG: auth.security.decode_access_token FAILED: {str(e)}")
        return None
