from backend.config import Settings


def test_database_url_override_converts_postgres_scheme(monkeypatch):
    monkeypatch.delenv("POSTGRES_SERVER", raising=False)
    settings = Settings(_env_file=None, database_url="postgresql://u:p@db:5432/devshield")

    assert settings.async_db_url == "postgresql+asyncpg://u:p@db:5432/devshield"


def test_postgres_env_composes_asyncpg_url(monkeypatch):
    monkeypatch.setenv("POSTGRES_SERVER", "db")
    settings = Settings(
        _env_file=None,
        postgres_user="devshield_user",
        postgres_password="devshield_password",
        postgres_port="5432",
        postgres_db="devshield_db",
    )

    assert settings.async_db_url == "postgresql+asyncpg://devshield_user:devshield_password@db:5432/devshield_db"


def test_sqlite_is_default_when_postgres_not_configured(monkeypatch):
    monkeypatch.delenv("POSTGRES_SERVER", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    settings = Settings(_env_file=None, database_url=None)

    assert settings.async_db_url.startswith("sqlite+aiosqlite:///")
    assert settings.db_url == settings.async_db_url
    assert settings.feedback_file.name == "feedback.jsonl"
    assert settings.preferences_file.name == "preferences.json"
