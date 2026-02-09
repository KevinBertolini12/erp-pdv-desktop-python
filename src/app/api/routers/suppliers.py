from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import db_session
from app.api.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate
from app.db.models.supplier import Supplier

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierRead])
async def list_suppliers(db: AsyncSession = Depends(db_session)):
    rows = (await db.execute(select(Supplier).order_by(Supplier.name.asc()))).scalars().all()
    return [
        {"id": s.id, "name": s.name, "document": s.document, "phone": s.phone, "email": s.email}
        for s in rows
    ]


@router.post("", response_model=SupplierRead)
async def create_supplier(payload: SupplierCreate, db: AsyncSession = Depends(db_session)):
    # bloqueia nome duplicado
    exists = (await db.execute(select(Supplier).where(Supplier.name == payload.name))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Já existe fornecedor com esse nome.")

    s = Supplier(name=payload.name, document=payload.document, phone=payload.phone, email=payload.email)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return {"id": s.id, "name": s.name, "document": s.document, "phone": s.phone, "email": s.email}


@router.put("/{supplier_id}", response_model=SupplierRead)
async def update_supplier(supplier_id: int, payload: SupplierUpdate, db: AsyncSession = Depends(db_session)):
    s = (await db.execute(select(Supplier).where(Supplier.id == supplier_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")

    if payload.name is not None:
        # checa duplicidade de nome (outro id)
        dup = (await db.execute(
            select(Supplier).where(Supplier.name == payload.name, Supplier.id != supplier_id)
        )).scalar_one_or_none()
        if dup:
            raise HTTPException(status_code=400, detail="Já existe fornecedor com esse nome.")
        s.name = payload.name

    if payload.document is not None:
        s.document = payload.document
    if payload.phone is not None:
        s.phone = payload.phone
    if payload.email is not None:
        s.email = payload.email

    await db.commit()
    await db.refresh(s)
    return {"id": s.id, "name": s.name, "document": s.document, "phone": s.phone, "email": s.email}


@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: int, db: AsyncSession = Depends(db_session)):
    s = (await db.execute(select(Supplier).where(Supplier.id == supplier_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")
    await db.delete(s)
    await db.commit()
    return {"ok": True}
