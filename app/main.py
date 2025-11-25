from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.DB_NAME, # Using DB name as project name for now or hardcode
    openapi_url=f"/api/v1/openapi.json"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to Institute LMS API"}
