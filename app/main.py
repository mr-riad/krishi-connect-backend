import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import calendar, calls, chat, disease, listings, rates, users, weather, machinery, agnews

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Krishi Connect API – Marketplace, Communication, Crop Calendar & Disease Diagnosis.",
)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

# Register API routers FIRST (before any app.mount calls)
for r in (users.router, listings.router, rates.router, chat.router, calls.router, calendar.router, disease.router,
          weather.router, machinery.router, agnews.router):
    app.include_router(r)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "database": "sqlite",
        "firebase": settings.use_firebase,
        "auth_mode": "hybrid",
    }


# Mount static files LAST — app.mount() must come after all include_router() calls
# otherwise FastAPI/Starlette stops matching API routes after the mount point.
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
