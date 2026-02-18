from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(60), nullable=True, unique=True)
    
    # --- CAMPOS DE GESTÃO E LUCRO ---
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)      # Preço de Venda
    cost_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0) # Preço de Custo
    
    # --- CONTROLE DE ALMOXARIFADO ---
    stock_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    min_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=5)    # Alerta de estoque baixo

    # --- NOVO: CÉREBRO FISCAL (Nível SAP/Globus) ---
    type: Mapped[str] = mapped_column(String(20), default="PRODUTO")      # PRODUTO ou SERVICO
    ncm_code: Mapped[str | None] = mapped_column(String(8), nullable=True, default="00000000") 
    ipi_rate: Mapped[float] = mapped_column(Float, default=0.0)             # Alíquota IPI
    icms_rate: Mapped[float] = mapped_column(Float, default=18.0)           # Alíquota ICMS padrão SP