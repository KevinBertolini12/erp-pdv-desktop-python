from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import db_session
from app.api.schemas.sales import SaleCreate
from app.db.models.product import Product
from app.db.models.stock_move import StockMove
from app.db.models.sales import Sale, SaleItem

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("")
async def create_sale(payload: SaleCreate, db: AsyncSession = Depends(db_session)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="items vazio")

    ids = [it.product_id for it in payload.items]
    res = await db.execute(select(Product).where(Product.id.in_(ids)))
    products = res.scalars().all()
    by_id = {p.id: p for p in products}

    # valida
    for it in payload.items:
        p = by_id.get(it.product_id)
        if not p:
            raise HTTPException(status_code=404, detail=f"Produto {it.product_id} não existe")
        if it.qty <= 0:
            raise HTTPException(status_code=400, detail="qty inválido")
        if int(p.stock_qty) < int(it.qty):
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente: {p.name}")

    now = datetime.utcnow()

    sale = Sale(created_at=now)
    db.add(sale)
    await db.flush()  # garante sale.id

    for it in payload.items:
        p = by_id[it.product_id]
        p.stock_qty = int(p.stock_qty) - int(it.qty)

        db.add(SaleItem(sale_id=sale.id, product_id=p.id, qty=int(it.qty)))
        db.add(StockMove(product_id=p.id, delta=-int(it.qty), reason=f"VENDA #{sale.id}", created_at=now))

    await db.commit()
    return {"id": sale.id}

# --- NOVO ENDPOINT: LISTAGEM DE VENDAS ---
# Isso resolve o erro 405 Method Not Allowed
@router.get("")
async def list_sales(db: AsyncSession = Depends(db_session)):
    """Retorna o histórico de todas as vendas"""
    result = await db.execute(select(Sale).order_by(Sale.created_at.desc()))
    return result.scalars().all()