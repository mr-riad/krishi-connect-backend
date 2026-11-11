import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import calls, chat, listings, rates, users

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Module 1 backend: Marketplace & Communication (listings, rate board, chat, call, search).",
)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

# Ensure uploads directory exists and mount static files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

for r in (users.router, listings.router, rates.router, chat.router, calls.router):
    app.include_router(r)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "database": "sqlite",
        "firebase": settings.use_firebase,
        "auth_mode": "hybrid",
    }
