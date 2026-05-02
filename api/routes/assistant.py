from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from config.database import get_db
from database.models import User
from auth.dependencies import get_current_user
from agents.executive.assistant import ExecutiveAssistant

router = APIRouter(tags=["assistant"])

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"

@router.get("/api/assistant/conversations")
async def get_conversations(mode: Optional[str] = "enterprise", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        from database.models import AssistantConversation
        # Filter by mode and return last 20
        convs = db.query(AssistantConversation).filter(AssistantConversation.mode == mode).order_by(AssistantConversation.id.desc()).limit(20).all()
        return {
            "success": True,
            "data": [
                {
                    "id": c.id, 
                    "title": c.title or "New Conversation", 
                    "mode": c.mode,
                    "created_at": datetime.now().isoformat()
                } for c in convs
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/api/assistant/conversations")
async def create_conversation(request: CreateConversationRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        from database.models import AssistantConversation
        new_conv = AssistantConversation(title=request.title)
        db.add(new_conv)
        db.commit()
        db.refresh(new_conv)
        return {"success": True, "id": new_conv.id}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.delete("/api/assistant/conversations/{conv_id}")
async def delete_conversation(conv_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        from database.models import AssistantConversation, AssistantChat
        db.query(AssistantChat).filter(AssistantChat.conversation_id == conv_id).delete()
        db.query(AssistantConversation).filter(AssistantConversation.id == conv_id).delete()
        db.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/api/assistant/history")
async def get_assistant_history(conversation_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        from database.models import AssistantChat
        query = db.query(AssistantChat)
        if conversation_id:
            query = query.filter(AssistantChat.conversation_id == conversation_id)
        
        history = query.order_by(AssistantChat.timestamp.asc()).all()
        return {
            "success": True,
            "data": [
                {"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()}
                for m in history
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/api/assistant/chat")
async def assistant_chat(request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        query = request.get("query")
        mode = request.get("mode", "enterprise")
        conversation_id = request.get("conversation_id")
        
        if not query:
            raise HTTPException(status_code=400, detail="Missing query")
        
        # Create new conversation if missing
        if not conversation_id:
            from database.models import AssistantConversation
            new_conv = AssistantConversation(title=query[:30] + "...", mode=mode)
            db.add(new_conv)
            db.commit()
            db.refresh(new_conv)
            conversation_id = new_conv.id
        
        assistant = ExecutiveAssistant(db, user=current_user)
        response = assistant.answer_query(query, conversation_id=conversation_id, mode=mode)
        
        return {
            "success": True,
            "response": response,
            "conversation_id": conversation_id
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
