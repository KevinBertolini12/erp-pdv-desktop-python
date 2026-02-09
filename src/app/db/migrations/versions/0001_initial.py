"""initial

Revision ID: 0001a1b2c3d4
Revises: 
Create Date: 2026-02-07

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001a1b2c3d4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("sku", sa.String(length=60), nullable=True),
        sa.Column("stock_qty", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_products_name", "products", ["name"], unique=False)
    op.create_unique_constraint("uq_products_sku", "products", ["sku"])

    op.create_table(
        "stock_moves",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "sale_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("sale_items")
    op.drop_table("sales")
    op.drop_table("stock_moves")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")
