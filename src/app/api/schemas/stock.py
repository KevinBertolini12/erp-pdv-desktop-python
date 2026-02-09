from pydantic import BaseModel

class StockAdjust(BaseModel):
    delta: int
    reason: str = "Ajuste"
