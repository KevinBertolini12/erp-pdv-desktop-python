from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_env: str = Field(default="dev", validation_alias="APP_ENV")
    api_host: str = Field(default="127.0.0.1", validation_alias="API_HOST")
    api_port: int = Field(default=8765, validation_alias="API_PORT")
    api_base_url: str = Field(default="http://127.0.0.1:8765", validation_alias="API_BASE_URL")
    db_url: str = Field(default="sqlite+aiosqlite:///./data/app.db", validation_alias="DB_URL")

settings = Settings()
