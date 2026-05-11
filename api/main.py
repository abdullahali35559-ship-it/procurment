import os
import sys
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from pathlib import Path
from dotenv import load_dotenv

# Load ENV
load_dotenv()

# Add ROOT directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Professional Explicit Imports
from api.routes.auth import router as auth_router
from api.routes.dashboard import router as dashboard_router
from api.routes.assistant import router as assistant_router
from api.routes.user import router as user_router
from api.routes.emails import router as emails_router
from api.routes.threads import router as threads_router
from api.routes.drafts import router as drafts_router

from database.connection import engine, Base

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

# Route Registration (Removed redundant prefixes)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(assistant_router)
app.include_router(user_router)
app.include_router(emails_router)
app.include_router(threads_router)
app.include_router(drafts_router)

# Static Asset Serving
app.mount("/css", StaticFiles(directory="ui/css"), name="css")
app.mount("/js", StaticFiles(directory="ui/js"), name="js")

@app.get("/api/image-proxy")
async def image_proxy(url: str):
    try:
        # Using professional headers to avoid blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://abdex.com/"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/jpeg"))
        return JSONResponse({"error": "Failed to fetch image"}, status_code=resp.status_code)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

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