from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# --- CONFIGURAÇÃO DA NUVEM (ASYNC - AWS-1) ---
# Link Pooler IPv4 com sua senha (MANTENHA O LINK QUE ESTAVA FUNCIONANDO)
# Vou colocar o link que você me mandou por último, que estava certo:
DATABASE_URL = "postgresql+asyncpg://postgres.plubbnocnafpfpkyqshr:Bertolini1203*@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

# 1. Cria o Motor Async
# O SEGREDO ESTÁ AQUI: connect_args={"statement_cache_size": 0}
# Isso diz pro Python não tentar "cachear" comandos, o que o Supabase odeia.
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"statement_cache_size": 0}
)

# 2. Configura a Sessão
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# 3. Cria a Base
class Base(DeclarativeBase):
    pass

# 4. Dependência para injetar o banco nas rotas
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session