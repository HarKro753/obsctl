"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from .env file or environment variables."""

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:3001/auth/callback"
    jwt_secret: str = "dev-secret-change-me"
    couchdb_url: str = "http://localhost:5984"
    couchdb_admin_user: str = "admin"
    couchdb_admin_password: str = ""
    database_path: str = "./data/users.db"
    port: int = 3001

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
