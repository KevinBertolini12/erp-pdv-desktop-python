import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# --- CÁLCULO DE CAMINHO ABSOLUTO (FIM DO BANCO FANTASMA) ---
# Pega a pasta onde este arquivo está (src/app/core)
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
# Sobe níveis para chegar na raiz do projeto (erp_pdv)
PROJECT_ROOT = os.path.abspath(os.path.join(CORE_DIR, "..", "..", ".."))
# Define o arquivo do banco na raiz
DB_FILE = os.path.join(PROJECT_ROOT, "storage.db")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=False,
        extra="ignore" # Evita erros se houver variáveis extras no .env
    )

    app_env: str = Field(default="dev", validation_alias="APP_ENV")
    api_host: str = Field(default="127.0.0.1", validation_alias="API_HOST")
    api_port: int = Field(default=8765, validation_alias="API_PORT")
    api_base_url: str = Field(default="http://127.0.0.1:8765", validation_alias="API_BASE_URL")
    
    # URL usada pelo SQLAlchemy (Async)
    database_url: str = Field(default=f"sqlite+aiosqlite:///{DB_FILE}", validation_alias="DATABASE_URL")
    
    # Caminho físico usado pelo MigrationEngine (SQLite puro)
    db_file_path: str = DB_FILE

settings = Settings()