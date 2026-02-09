from pydantic import BaseModel

class SeriesPoint(BaseModel):
    day: str
    value: int

class StockMovesSeries(BaseModel):
    series: list[SeriesPoint]
