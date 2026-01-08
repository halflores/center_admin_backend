from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Force reload
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.DB_NAME, # Using DB name as project name for now or hardcode
    openapi_url=f"/api/v1/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

app.include_router(api_router, prefix="/api/v1")

# Mount uploads directory ensuring it exists
# Use absolute path to avoid CWD issues
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
    
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

@app.get("/")
def root():
    return {"message": "Welcome to Institute LMS API"}
