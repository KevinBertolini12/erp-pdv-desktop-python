from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QAbstractItemView,
    QDialog,
)

from app.clients.api_client import ApiClient
from app.ui.product_dialog import ProductDialog
from app.ui.stock_dialog import StockDialog


class ProductsWindow(QWidget):
    def __init__(self, api_base_url: str, bus=None):
        super().__init__()

        self.client = ApiClient(api_base_url)
        self.bus = bus

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "SKU", "Estoque"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        actions = QHBoxLayout()

        btn_stock = QPushButton("Ajustar estoque")
        btn_stock.clicked.connect(self.adjust_stock)

        btn_new = QPushButton("Novo")
        btn_new.clicked.connect(self.create_new)

        btn_edit = QPushButton("Editar")
        btn_edit.clicked.connect(self.edit_selected)

        btn_delete = QPushButton("Excluir")
        btn_delete.clicked.connect(self.delete_selected)

        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self.load_products)

        actions.addWidget(btn_stock)
        actions.addWidget(btn_new)
        actions.addWidget(btn_edit)
        actions.addWidget(btn_delete)
        actions.addStretch(1)
        actions.addWidget(btn_refresh)

        layout.addLayout(actions)
        layout.addWidget(self.table)

        self.load_products()

    def _selected_product_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def _selected_product(self) -> dict | None:
        row = self.table.currentRow()
        if row < 0:
            return None

        product_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        sku = self.table.item(row, 2).text() or None

        stock_txt = self.table.item(row, 3).text() if self.table.columnCount() > 3 else "0"
        try:
            stock_qty = int(stock_txt)
        except Exception:
            stock_qty = 0

        return {
            "id": product_id,
            "name": name,
            "sku": sku,
            "stock_qty": stock_qty,
        }

    def _row_data(self, row: int) -> dict:
        return {
            "id": int(self.table.item(row, 0).text()),
            "name": self.table.item(row, 1).text(),
            "sku": self.table.item(row, 2).text() or None,
        }

    def load_products(self):
        try:
            products = self.client.list_products()
            self.table.setRowCount(0)

            for p in products:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(p["name"]))
                self.table.setItem(row, 2, QTableWidgetItem(p.get("sku") or ""))
                self.table.setItem(row, 3, QTableWidgetItem(str(p.get("stock_qty", 0))))

            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def create_new(self):
        dlg = ProductDialog(self, title="Novo produto")
        if dlg.exec() != QDialog.Accepted:
            return

        name, sku = dlg.values()

        try:
            self.client.create_product(name=name, sku=sku)
            self.load_products()

            if self.bus:
                self.bus.products_changed.emit()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def edit_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um produto.")
            return

        data = self._row_data(row)
        dlg = ProductDialog(
            self,
            title=f"Editar produto #{data['id']}",
            name=data["name"],
            sku=data["sku"] or "",
        )

        if dlg.exec() != QDialog.Accepted:
            return

        name, sku = dlg.values()

        try:
            self.client.update_product(product_id=data["id"], name=name, sku=sku)
            self.load_products()

            if self.bus:
                self.bus.products_changed.emit()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def delete_selected(self):
        product_id = self._selected_product_id()
        if product_id is None:
            QMessageBox.warning(self, "Atenção", "Selecione um produto.")
            return

        if QMessageBox.question(self, "Confirmar", f"Excluir produto {product_id}?") != QMessageBox.Yes:
            return

        try:
            self.client.delete_product(product_id)
            self.load_products()

            if self.bus:
                self.bus.products_changed.emit()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def adjust_stock(self):
        data = self._selected_product()
        if not data:
            QMessageBox.warning(self, "Atenção", "Selecione um produto.")
            return

        dlg = StockDialog(self, product_name=data["name"])
        if dlg.exec() != QDialog.Accepted:
            return

        delta, reason = dlg.values()

        try:
            self.client.adjust_stock(
                product_id=data["id"],
                delta=delta,
                reason=reason,
            )
            self.load_products()

            if self.bus:
                self.bus.stock_changed.emit()
                self.bus.products_changed.emit()

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
