import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

def _ensure_sqlite_dir():
    if settings.db_url.lower().startswith("sqlite"):
        os.makedirs("./data", exist_ok=True)

_ensure_sqlite_dir()

engine = create_async_engine(settings.db_url, echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
