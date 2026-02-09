from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String

from app.db.models import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    # opcionais (pode ir preenchendo depois)
    document: Mapped[str | None] = mapped_column(String(30), nullable=True)  # CNPJ/CPF
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
