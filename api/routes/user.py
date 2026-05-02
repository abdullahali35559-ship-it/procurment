from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.models import User
from config.database import get_db
from auth.dependencies import get_current_user
from agents.executive.style_analyzer import StyleAnalyzer
from agents.procurement_agent.style_agent import StyleAgent

router = APIRouter(tags=["user"])

class UserSettingsUpdate(BaseModel):
    brand_voice: Optional[str] = None
    custom_instructions: Optional[str] = None

@router.get("/api/user/settings")
async def get_user_settings(current_user: User = Depends(get_current_user)):
    return {
        "brand_voice": current_user.brand_voice,
        "custom_instructions": current_user.custom_instructions,
        "writing_style_guide": current_user.writing_style_guide
    }

@router.put("/api/user/settings")
async def update_user_settings(
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if settings.brand_voice is not None:
            current_user.brand_voice = settings.brand_voice
            # TRIGGER AI ANALYSIS
            style_agent = StyleAgent()
            guide = style_agent.analyze_samples(settings.brand_voice)
            print(f"DEBUG: Generated Style Guide: {guide}")
            current_user.writing_style_guide = guide
            
        if settings.custom_instructions is not None:
            current_user.custom_instructions = settings.custom_instructions
        
        db.add(current_user)
        db.commit()
        return {"success": True, "message": "Settings updated and style analyzed"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/user/sync-voice")
async def sync_voice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        analyzer = StyleAnalyzer(db)
        result = await analyzer.sync_user_voice(current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/user/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "brand_voice": current_user.brand_voice,
        "custom_instructions": current_user.custom_instructions,
        "writing_style_guide": current_user.writing_style_guide,
        "preferences": current_user.preferences,
        "is_active": current_user.is_active
    }
