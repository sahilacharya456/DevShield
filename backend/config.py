import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "DevShield AI X"
    owner: str = "Sahil"
    api_v1_str: str = "/api/v1"
    
    gemini_api_key: str = ""
    claude_api_key: str = ""
    groq_api_key: str = ""
    shodan_api_key: str = ""
    virustotal_api_key: str = ""
    nvd_api_key: str = ""
    allowed_scan_targets: str = ""
    allow_private_scan_targets: bool = True

    # Database URL override. Use postgresql+asyncpg://... in production.
    database_url: Optional[str] = None
    
    # PostgreSQL Configuration
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_server: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "devshield"

    # JWT Authentication
    secret_key: str = os.getenv("SECRET_KEY", os.urandom(32).hex())
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    refresh_token_expire_days: int = 7
    
    # Celery / Redis Background Tasks
    redis_url: str = "redis://localhost:6379/0"

    # Local file-backed learning data.
    db_dir: Path = Path(__file__).parent.parent / "data"
    
    # Rate Limiting
    rate_limit: str = "100/minute"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def async_db_url(self) -> str:
        if self.database_url:
            if self.database_url.startswith("postgresql://"):
                return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.database_url

        if os.getenv("POSTGRES_SERVER") or os.getenv("POSTGRES_HOST"):
            server = os.getenv("POSTGRES_HOST", self.postgres_server)
            return (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{server}:{self.postgres_port}/{self.postgres_db}"
            )

        # Default to SQLite for easy local startup.
        db_dir = Path(__file__).parent.parent / "data"
        db_dir.mkdir(parents=True, exist_ok=True)
        return "sqlite+aiosqlite:///devshield_saas.db"

    @property
    def db_url(self) -> str:
        return self.async_db_url

    @property
    def feedback_file(self) -> Path:
        self.db_dir.mkdir(parents=True, exist_ok=True)
        return self.db_dir / "feedback.jsonl"

    @property
    def preferences_file(self) -> Path:
        self.db_dir.mkdir(parents=True, exist_ok=True)
        return self.db_dir / "preferences.json"

settings = Settings()
