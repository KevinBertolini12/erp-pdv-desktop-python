from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base, engine
import sqlite3
from datetime import datetime

# Função Mágica: Cria rotas vazias se o arquivo falhar (Mantendo sua lógica original)
def create_dummy_router(name):
    router = APIRouter()
    @router.get("")
    def dummy_list(): return []
    @router.get("/")
    def dummy_list_slash(): return []
    print(f"⚠️ Rota de emergência criada para: {name}")
    return router

def create_app() -> FastAPI:
    app = FastAPI(title="Bertolini ERP API", version="3.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup():
        print(">>> [SERVIDOR] Banco OK")
        # Tentativa de criar tabelas na nuvem se não existirem
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"⚠️ Aviso no startup do banco: {e}")

    # --- NOVO: ROTA DE SINCRONIZAÇÃO (TELEMETRIA MASTER) ---
    # Esta rota recebe os dados que o 'CloudSyncEngine' envia
    @app.post("/api/sync")
    async def receive_sync(request: Request):
        try:
            data = await request.json()
            unit_id = data.get("unit_id")
            total_sales = data.get("total_sales", 0.0)
            
            # Aqui gravamos no banco MASTER para aparecer na sua MonitoringPage
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            
            # Garante que a tabela de vendas existe no Master
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_value REAL,
                    payment_method TEXT,
                    timestamp TEXT
                )
            """)
            
            # Insere o registro vindo da nuvem
            cursor.execute("""
                INSERT INTO sales (total_value, payment_method, timestamp)
                VALUES (?, ?, ?)
            """, (total_sales, f"SYNC_FROM_{unit_id}", datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            print(f"📡 [CLOUD] Dados recebidos da Unidade {unit_id}: R$ {total_sales}")
            return {"status": "success", "message": "Dados integrados ao Hub Master"}
        except Exception as e:
            print(f"❌ [CLOUD ERROR] Falha na sincronização: {e}")
            return {"status": "error", "detail": str(e)}

    # --- IMPORTAÇÃO DE ROTAS ORIGINAIS ---
    
    # 1. Produtos
    try:
        from app.api.routers.products import router as products_router
        app.include_router(products_router, prefix="/products", tags=["products"])
    except Exception as e:
        print(f"❌ Erro Produtos: {e}")
        app.include_router(create_dummy_router("products"), prefix="/products")

    # 2. Vendas
    try:
        from app.api.routers.sales import router as sales_router
        app.include_router(sales_router, prefix="/sales", tags=["sales"])
    except Exception as e:
        print(f"❌ Erro Vendas: {e}")
        app.include_router(create_dummy_router("sales"), prefix="/sales")

    # 3. Fornecedores
    try:
        from app.api.routers.suppliers import router as suppliers_router
        app.include_router(suppliers_router, prefix="/suppliers", tags=["suppliers"])
    except Exception as e:
        print(f"❌ Erro Fornecedores: {e}")
        app.include_router(create_dummy_router("suppliers"), prefix="/suppliers")

    # 4. Relatórios / Dashboard
    try:
        from app.api.routers import reports
        r = getattr(reports, "router", getattr(reports, "reports_router", None))
        if r:
            app.include_router(r, prefix="/reports", tags=["reports"])
            print("✅ Rota de Relatórios (Dashboard) carregada!")
        else:
            raise ImportError("Não foi encontrado o objeto 'router' dentro de reports.py")
    except Exception as e:
        print(f"❌ Erro Relatórios: {e}")
        app.include_router(create_dummy_router("reports"), prefix="/reports")

    @app.get("/")
    def root(): return {"status": "online", "server": "Bertolini Cloud Hub"}

    return app

# Cria a instância global que o main.py procura
app = create_app()