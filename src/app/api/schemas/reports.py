from pydantic import BaseModel


class SummaryOut(BaseModel):
    total_products: int
    total_stock: int
    low_stock: int


class StockMovePoint(BaseModel):
    day: str
    net: int


class StockMoves7dOut(BaseModel):
    series: list[StockMovePoint]


class StockMoveItem(BaseModel):
    created_at: str
    product_id: int
    product_name: str
    delta: int
    reason: str


class StockMovesRangeOut(BaseModel):
    items: list[StockMoveItem]
