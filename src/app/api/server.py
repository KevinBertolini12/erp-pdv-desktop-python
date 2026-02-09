from fastapi import FastAPI

from .routers.health import router as health_router
from .routers.products import router as products_router
from .routers.reports import router as reports_router
from .routers.sales import router as sales_router
from .routers.suppliers import router as suppliers_router


def create_app() -> FastAPI:
    app = FastAPI(title="ERP/PDV API", version="0.1.0")
    app.include_router(health_router)
    app.include_router(products_router)
    app.include_router(reports_router)
    app.include_router(sales_router)
    app.include_router(suppliers_router)

    return app
