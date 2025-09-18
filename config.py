"""Configuration utilities for the Geospatial Data Engineering Demo."""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore

@dataclass
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    export_dir: str = "data/processed"

    @property
    def dsn(self) -> str:
        return (
            f"host={self.db_host} port={self.db_port} dbname={self.db_name} "
            f"user={self.db_user} password={self.db_password}"
        )

def load_settings(env_file: Optional[str] = None) -> Settings:
    """Load settings from environment (and optional .env file)."""
    if load_dotenv and env_file:
        load_dotenv(env_file)
    elif load_dotenv:
        load_dotenv()

    return Settings(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "utility"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "postgres"),
        export_dir=os.getenv("EXPORT_DIR", "data/processed"),
    )

def get_connection():  # pragma: no cover - simple wrapper
    import psycopg2  # local import to avoid dependency issues if unused
    settings = load_settings()
    return psycopg2.connect(settings.dsn)

if __name__ == "__main__":  # simple debug
    s = load_settings()
    print("Loaded settings:", s)
