from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    source_db_url: str
    warehouse_db_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()