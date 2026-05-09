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

# Add ROOT directory to sys.path taake saray folders (api, database, models) mil sakein
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Ab hum absolute imports use kar sakte hain jo har jagah kaam karein gi
from api.routes import auth, dashboard, assistant, user, document, settings
from database.config import engine, Base

# Create DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Procurement Assistant API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["Assistant"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(document.router, prefix="/api/documents", tags=["Documents"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

# Static Files
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