import os
import yaml
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "institute_db"
    DB_USER: str = "admin"
    DB_PASSWORD: str = "password"
    DATABASE_URL: str = ""
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

def load_settings() -> Settings:
    # 1. Start with defaults/env vars via BaseSettings
    settings = Settings()

    # 2. Override with config.yaml if present (for local dev backward compatibility)
    config_path = Path(__file__).resolve().parent.parent.parent / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                if config:
                    db_config = config.get("database", {})
                    if "host" in db_config: settings.DB_HOST = str(db_config["host"])
                    if "port" in db_config: settings.DB_PORT = int(db_config["port"])
                    if "name" in db_config: settings.DB_NAME = str(db_config["name"])
                    if "user" in db_config: settings.DB_USER = str(db_config["user"])
                    if "password" in db_config: settings.DB_PASSWORD = str(db_config["password"])
        except Exception as e:
            print(f"Warning: Error loading config.yaml: {e}")

    # 3. Construct Database URL (if not set via env var explicitly)
    if not settings.DATABASE_URL:
        settings.DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    
    return settings

settings = load_settings()
