from pydantic import BaseModel, Field


class SaleItemIn(BaseModel):
    product_id: int
    qty: int = Field(gt=0)


class SaleCreate(BaseModel):
    items: list[SaleItemIn]


class SaleCreated(BaseModel):
    id: int
