import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURAÇÃO DA NUVEM (CORRETA - AWS-1) ---
# Link Pooler IPv4 com sua senha já inserida
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.plubbnocnafpfpkyqshr:Bertolini1203*@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()