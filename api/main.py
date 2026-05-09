import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv

# Load ENV
load_dotenv()

# Add ROOT directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Professional Explicit Imports (Verified with local filesystem)
from api.routes.auth import router as auth_router
from api.routes.dashboard import router as dashboard_router
from api.routes.assistant import router as assistant_router
from api.routes.user import router as user_router
from api.routes.emails import router as emails_router
from api.routes.threads import router as threads_router
from api.routes.drafts import router as drafts_router

from database.config import engine, Base

# Create DB Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Procurement Assistant API - Abdex Industries")

# Global CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Explicit Route Registration
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(assistant_router, prefix="/api/assistant", tags=["Assistant"])
app.include_router(user_router, prefix="/api/user", tags=["User"])
app.include_router(emails_router, prefix="/api/emails", tags=["Emails"])
app.include_router(threads_router, prefix="/api/threads", tags=["Threads"])
app.include_router(drafts_router, prefix="/api/drafts", tags=["Drafts"])

# Static Asset Serving
app.mount("/css", StaticFiles(directory="ui/css"), name="css")
app.mount("/js", StaticFiles(directory="ui/js"), name="js")
app.mount("/images", StaticFiles(directory="ui/images"), name="images")

@app.get("/")
async def read_root():
    return FileResponse("ui/login.html")

@app.get("/{page_name}")
async def serve_page(page_name: str):
    clean_name = page_name.replace(".html", "")
    path = Path(f"ui/{clean_name}.html")
    if path.exists(): return FileResponse(path)
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8067))
    uvicorn.run(app, host="0.0.0.0", port=port)