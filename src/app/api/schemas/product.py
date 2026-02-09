from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sku: str | None = Field(default=None, max_length=60)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    stock_qty: int = 0

    class Config:
        from_attributes = True


class StockAdjust(BaseModel):
    delta: int
    reason: str = Field(default="Ajuste", max_length=200)
