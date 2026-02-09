from datetime import datetime, timedelta, date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session
from app.db.models.product import Product
from app.db.models.stock_move import StockMove

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
async def summary(db: AsyncSession = Depends(db_session)):
    total_products = (await db.execute(select(func.count(Product.id)))).scalar_one()
    total_stock = (await db.execute(select(func.coalesce(func.sum(Product.stock_qty), 0)))).scalar_one()
    low_stock = (await db.execute(select(func.count(Product.id)).where(Product.stock_qty <= 5))).scalar_one()
    return {
        "total_products": int(total_products),
        "total_stock": int(total_stock),
        "low_stock": int(low_stock),
    }


@router.get("/stock_moves_7d")
async def stock_moves_7d(db: AsyncSession = Depends(db_session)):
    # últimos 7 dias incluindo hoje (UTC)
    today = date.today()
    start = today - timedelta(days=6)
    start_dt = datetime.combine(start, datetime.min.time())

    res = await db.execute(
        select(func.date(StockMove.created_at).label("d"), func.coalesce(func.sum(StockMove.delta), 0).label("net"))
        .where(StockMove.created_at >= start_dt)
        .group_by(func.date(StockMove.created_at))
        .order_by(func.date(StockMove.created_at))
    )
    rows = res.all()
    by_day = {r.d: int(r.net) for r in rows}

    series = []
    for i in range(7):
        d = start + timedelta(days=i)
        key = d.isoformat()
        series.append({"day": key, "net": int(by_day.get(key, 0))})

    # UI usa índice 0..6, então só manda net
    return {"series": [{"day": s["day"], "net": s["net"]} for s in series]}


@router.get("/stock_moves_range")
async def stock_moves_range(
    start: str = Query(..., description="YYYY-MM-DD"),
    end: str = Query(..., description="YYYY-MM-DD"),
    db: AsyncSession = Depends(db_session),
):
    start_d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)
    start_dt = datetime.combine(start_d, datetime.min.time())
    end_dt = datetime.combine(end_d + timedelta(days=1), datetime.min.time())  # exclusivo

    res = await db.execute(
        select(StockMove, Product)
        .join(Product, Product.id == StockMove.product_id)
        .where(StockMove.created_at >= start_dt, StockMove.created_at < end_dt)
        .order_by(StockMove.created_at.desc())
        .limit(500)
    )
    items = []
    for sm, p in res.all():
        items.append({
            "created_at": sm.created_at.isoformat(sep=" ", timespec="seconds"),
            "product_id": int(sm.product_id),
            "product_name": p.name,
            "delta": int(sm.delta),
            "reason": sm.reason,
        })
    return {"items": items}
