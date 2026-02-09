# ERP/PDV Desktop (Starter Completo)

Stack: **PySide6 (UI)** → HTTP → **FastAPI (local)** → **SQLAlchemy (async)** → SQLite (ou Postgres).
Inclui **Alembic** configurado para async engine.

## Setup (Windows)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
copy .env.example .env
```

## Rodar (UI + API local)
```powershell
python -m app.main
```

Clique em **Testar API (/health)**.

## Alembic (criar tabela products)
O `alembic.ini` já adiciona `src` ao sys.path.

```powershell
alembic revision --autogenerate -m "create products"
alembic upgrade head
```

## Testar API de produtos
Com o app rodando:

```powershell
curl -Method POST http://127.0.0.1:8765/products `
  -ContentType "application/json" `
  -Body '{"name":"Coca 2L","sku":"COCA-2L"}'

curl http://127.0.0.1:8765/products
```
