import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import calendar, calls, chat, listings, rates, users

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Module 1 backend: Marketplace & Communication (listings, rate board, chat, call, search).",
)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Register API routers FIRST (before any app.mount calls)
for r in (users.router, listings.router, rates.router, chat.router, calls.router, calendar.router):
    app.include_router(r)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "database": "sqlite",
        "firebase": settings.use_firebase,
        "auth_mode": "hybrid",
        "modules": [
            "marketplace",
            "chat",
            "advisory",
            "calendar",
            "intercrop",
            "machinery",
            "news",
            "forum",
            "notifications",
            "admin",
        ],
    }


# Mount static files LAST — app.mount() must come after all include_router() calls
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Admin panel (static HTML)
_admin_panel_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin_panel")
if os.path.isdir(_admin_panel_dir):
    app.mount("/admin-panel", StaticFiles(directory=_admin_panel_dir, html=True), name="admin-panel")
