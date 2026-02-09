from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session
from app.api.schemas.product import ProductCreate, ProductRead, ProductUpdate, StockAdjust
from app.db.models.product import Product
from app.db.models.stock_move import StockMove

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductRead)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(db_session)):
    p = Product(name=payload.name, sku=payload.sku)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("", response_model=list[ProductRead])
async def list_products(db: AsyncSession = Depends(db_session)):
    res = await db.execute(select(Product).order_by(Product.id.desc()))
    return list(res.scalars().all())


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: AsyncSession = Depends(db_session)):
    res = await db.execute(select(Product).where(Product.id == product_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(product_id: int, payload: ProductUpdate, db: AsyncSession = Depends(db_session)):
    res = await db.execute(select(Product).where(Product.id == product_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    p.name = payload.name
    p.sku = payload.sku
    await db.commit()
    await db.refresh(p)
    return p


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(db_session)):
    res = await db.execute(select(Product).where(Product.id == product_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(p)
    await db.commit()
    return {"ok": True}


@router.post("/{product_id}/stock")
async def adjust_stock(product_id: int, payload: StockAdjust, db: AsyncSession = Depends(db_session)):
    res = await db.execute(select(Product).where(Product.id == product_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    p.stock_qty = int(p.stock_qty) + int(payload.delta)

    db.add(StockMove(
        product_id=p.id,
        delta=int(payload.delta),
        reason=payload.reason,
        created_at=datetime.utcnow(),
    ))
    await db.commit()
    return {"ok": True, "stock_qty": p.stock_qty}
