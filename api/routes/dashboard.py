from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from database.models import Thread, Email, Contact, DraftReply, User
from config.database import SessionLocal, get_db
from auth.dependencies import get_current_user
from agents.procurement_agent.outlook_graph import OutlookGraphFetcher
from agents.procurement_agent.gmail_api_client import GmailAPIFetcher
from models.pixtral_client import PixtralClient
from pathlib import Path
import time
import asyncio
from datetime import datetime

router = APIRouter(tags=["dashboard"])

# Global state for sync progress and caching
sync_progress = {"status": "Idle", "current": 0, "total": 0, "active": False}
CALENDAR_CACHE = {"data": [], "expiry": 0}
CACHE_DURATION = 300 # 5 minutes

@router.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get aggregate statistics for the dashboard"""
    try:
        active_threads = db.query(Thread).count()
        total_emails = db.query(Email).count()
        total_contacts = db.query(Contact).count()
        pending_replies = db.query(DraftReply).count()
        unprocessed_emails = db.query(Email).filter(Email.processed == False).count()
        
        return {
            "success": True,
            "data": {
                "activeTenders": active_threads,
                "unreadEmails": total_emails,
                "unprocessedEmails": unprocessed_emails,
                "pendingProcurements": pending_replies,
                "totalClients": total_contacts,
                "calendarEvents": 0 # Placeholder
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/api/status")
async def get_system_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Check connectivity to various system components"""
    status = {
        "database": False,
        "gmail": False,
        "outlook": "disconnected",
        "llm": False
    }
    try:
        db.execute(text("SELECT 1"))
        status["database"] = True
    except: pass
    
    try:
        outlook = OutlookGraphFetcher()
        if outlook.connect(): status["outlook"] = "connected"
        elif Path(".outlook_oauth_token.json").exists(): status["outlook"] = "unauthorized"
    except: pass
        
    if Path(".gmail_oauth_token.json").exists(): status["gmail"] = True
        
    try:
        llm = PixtralClient()
        if llm.test_connection(): status["llm"] = True
    except: pass
    
    return status

@router.get("/api/agent/status")
async def get_agent_status(current_user: User = Depends(get_current_user)):
    """Return the current processing status of the agent"""
    return sync_progress

@router.post("/api/process-emails")
async def trigger_email_processing(current_user: User = Depends(get_current_user)):
    """Trigger the email processing agent"""
    global sync_progress
    return {"success": True, "message": "Email processing triggered"}

@router.get("/api/morning-brief")
async def get_morning_brief(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "brief": f"Good morning, {current_user.full_name or 'Abdullah'}. You have 0 urgent Procurements and 0 meetings today.",
        "tasks": []
    }

@router.get("/api/tasks")
async def get_tasks(current_user: User = Depends(get_current_user)):
    return {"success": True, "data": []}

@router.get("/api/followups")
async def get_followups(current_user: User = Depends(get_current_user)):
    return {"success": True, "data": []}

@router.get("/api/calendar/events")
async def get_calendar_events(days: int = 30, current_user: User = Depends(get_current_user)):
    """Fetch events from both Google and Outlook with caching"""
    global CALENDAR_CACHE
    
    # Check cache
    now = time.time()
    if CALENDAR_CACHE["data"] and now < CALENDAR_CACHE["expiry"]:
        print("[Dashboard] Serving Calendar from Cache")
        return {"success": True, "data": CALENDAR_CACHE["data"], "cached": True}

    all_events = []
    
    # 1. Fetch from Outlook
    try:
        if Path(".outlook_oauth_token.json").exists():
            outlook = OutlookGraphFetcher()
            if outlook.connect():
                events = outlook.fetch_calendar_events(days=days)
                all_events.extend(events)
    except Exception as e:
        print(f"Dashboard: Outlook fetch error: {e}")
        
    # 2. Fetch from Gmail/Google
    try:
        if Path(".gmail_oauth_token.json").exists():
            gmail = GmailAPIFetcher()
            if gmail.connect():
                events = gmail.fetch_calendar_events(days=days)
                all_events.extend(events)
    except Exception as e:
        print(f"Dashboard: Google fetch error: {e}")
        
    # Sort by start time
    all_events.sort(key=lambda x: x['start'])
    
    # Update Cache
    CALENDAR_CACHE["data"] = all_events
    CALENDAR_CACHE["expiry"] = now + CACHE_DURATION
    
    return {"success": True, "data": all_events, "cached": False}

@router.post("/api/calendar/events")
async def create_calendar_event(data: dict, current_user: User = Depends(get_current_user)):
    """Create an event in either Google or Outlook"""
    provider = data.get('provider', 'google')
    title = data.get('title', 'Procurement Meeting')
    start = data.get('start')
    end = data.get('end')
    attendees = data.get('attendees', [])
    description = data.get('description', "")
    
    if not start or not end:
        raise HTTPException(status_code=400, detail="Start and End times required")
        
    try:
        if provider == 'outlook':
            fetcher = OutlookGraphFetcher()
            if not fetcher.connect(): return {"success": False, "error": "Outlook not connected"}
            result = fetcher.create_calendar_event(title, start, end, attendees, description)
            return result
        else:
            fetcher = GmailAPIFetcher()
            if not fetcher.connect(): return {"success": False, "error": "Gmail not connected"}
            result = fetcher.create_calendar_event(title, start, end, attendees, description)
            return result
    except Exception as e:
        return {"success": False, "error": str(e)}
@router.get("/api/dashboard/all")
async def get_dashboard_full(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Consolidated endpoint for dashboard to reduce network overhead"""
    
    # 1. Stats (Fast)
    stats = {
        "activeTenders": db.query(Thread).count(),
        "unreadEmails": db.query(Email).count(),
        "unprocessedEmails": db.query(Email).filter(Email.processed == False).count(),
        "pendingProcurements": db.query(DraftReply).count(),
        "totalClients": db.query(Contact).count()
    }
    
    # 2. Morning Brief
    brief = {
        "brief": f"Good morning, {current_user.full_name or 'Abdullah'}. Welcome back to your procurement portal.",
        "tasks": []
    }
    
    # 3. Tasks & Followups
    tasks = []
    followups = []
    
    # 4. Threads (Recent)
    threads = db.query(Thread).order_by(desc(Thread.updated_at)).limit(10).all()
    thread_data = []
    for t in threads:
        thread_data.append({
            "thread_id": t.thread_id,
            "subject": t.subject,
            "contact_name": t.contact_name,
            "status": t.status,
            "last_updated": t.updated_at.isoformat() if t.updated_at else None,
            "tags": [{"name": tag.name, "color": tag.color} for tag in t.tags] if hasattr(t, 'tags') else []
        })

    # Return consolidated data
    return {
        "success": True,
        "stats": stats,
        "brief": brief,
        "tasks": tasks,
        "followups": followups,
        "recentThreads": thread_data,
        "timestamp": datetime.now().isoformat()
    }
