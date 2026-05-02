"""
Procurement Agent - Test Backend API
Quick test server for UI testing without full backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Procurement Agent Test API")

# Enable CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Procurement Agent Test API is running!", "status": "ok"}

@app.get("/api/status")
def get_system_status():
    """System status for dashboard"""
    return {
        "database": True,
        "gmail": False,
        "outlook": True,
        "llm": False
    }

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """Dashboard statistics"""
    return {
        "activeTenders": 2,
        "unreadEmails": 15,
        "pendingProcurements": 3,
        "totalClients": 3
    }

@app.get("/api/activity")
def get_recent_activity():
    """Recent activity feed"""
    return {
        "recent": [
            {
                "id": 1,
                "type": "email",
                "message": "New tender received from Test Client",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": 2,
                "type": "tender",
                "message": "Procurement draft created for Project Alpha",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

@app.get("/api/tenders")
def get_tenders():
    """Get all tenders"""
    return [
        {
            "id": "T001",
            "client": "Test Client A",
            "subject": "Construction Project Alpha - Building Materials",
            "date": "2026-02-09T10:30:00",
            "status": "active",
            "documents": 5
        },
        {
            "id": "T002",
            "client": "Test Client B",
            "subject": "Infrastructure Development Tender",
            "date": "2026-02-08T14:20:00",
            "status": "pending",
            "documents": 3
        },
        {
            "id": "T003",
            "client": "Test Client C",
            "subject": "Equipment Supply Procurement",
            "date": "2026-02-07T09:15:00",
            "status": "completed",
            "documents": 8
        }
    ]

@app.post("/api/process-emails")
def process_emails():
    """Process new emails"""
    return {
        "count": 10,
        "message": "Successfully processed emails",
        "new_tenders": 2
    }

@app.get("/api/oauth/status")
def get_oauth_status():
    """OAuth provider status"""
    return {
        "gmail": False,
        "outlook": True
    }

@app.get("/api/clients")
def get_clients():
    """Get all clients"""
    return [
        {
            "id": 1,
            "name": "Test Client A",
            "email": "client.a@example.com",
            "tenders": 5,
            "status": "active"
        },
        {
            "id": 2,
            "name": "Test Client B",
            "email": "client.b@example.com",
            "tenders": 3,
            "status": "active"
        },
        {
            "id": 3,
            "name": "Test Client C",
            "email": "client.c@example.com",
            "tenders": 7,
            "status": "active"
        }
    ]

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Procurement Agent Test Backend API")
    print("=" * 60)
    print("📍 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🧪 Test UI: Open ui/index.html in browser")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
