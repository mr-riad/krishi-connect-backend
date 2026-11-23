import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import (
    calendar, calls, chat, listings, rates, users,
    advisory, machinery_news, forum, notifications, admin,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description=(
        "Krishi Connect full backend — Marketplace & Communication, "
        "Agricultural Advisory, Community Forum, Weather Alerts, "
        "Push Notifications, and Admin Dashboard."
    ),
)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ── Register all API routers (must come BEFORE any app.mount()) ──────────────
for r in (
    # Module 1 – Marketplace & Communication
    users.router,
    listings.router,
    rates.router,
    chat.router,
    calls.router,
    # Module 2 – Agricultural Advisory & Info
    calendar.router,
    advisory.router,
    machinery_news.router,
    notifications.router,
    # Module 3 – Community & Admin
    forum.router,
    admin.router,
):
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
