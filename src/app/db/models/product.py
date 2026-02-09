from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(60), nullable=True, unique=True)
    stock_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
