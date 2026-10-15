from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"   # project root

class Settings(BaseSettings):
    source_db_url: str
    warehouse_db_url: str

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

settings = Settings()