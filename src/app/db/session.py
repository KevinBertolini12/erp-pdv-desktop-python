import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

def _ensure_sqlite_dir():
    # Atualizado para usar settings.database_url (o nome correto no config.py)
    if settings.database_url.lower().startswith("sqlite"):
        # Pega o caminho do arquivo removendo o prefixo do driver
        # Ex: sqlite+aiosqlite:///C:/Users/.../storage.db -> C:/Users/.../storage.db
        db_path = settings.database_url.split(":///")[-1]
        
        # Pega o diretório desse arquivo
        directory = os.path.dirname(db_path)
        
        # Se houver um diretório no caminho, garante que ele existe
        if directory:
            os.makedirs(directory, exist_ok=True)

_ensure_sqlite_dir()

# Atualizado para usar settings.database_url
engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)