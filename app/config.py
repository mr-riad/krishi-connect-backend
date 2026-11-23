from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Krishi Connect API"
    environment: str = "development"
    cors_origins: str = "*"

    use_firebase: bool = False
    auth_disabled: bool = False

    # Option 1: path to serviceAccountKey.json file
    firebase_credentials_path: str | None = None
    # Option 2: the entire serviceAccountKey.json content as a JSON string
    # (Useful for Render.com / Railway / Heroku where you cannot upload files)
    firebase_credentials_json: str | None = None

    firebase_storage_bucket: str | None = None
    max_upload_mb: int = 5

    # Comma-separated list of Firebase UIDs that should auto-get admin role
    admin_uids: str = ""

    # FCM sender ID (optional, informational)
    fcm_sender_id: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
