from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QDialog
)

from app.clients.api_client import ApiClient
from app.ui.supplier_dialog import SupplierDialog


class SuppliersWindow(QWidget):
    def __init__(self, api_base_url: str, bus=None):
        super().__init__()
        self.client = ApiClient(api_base_url)
        self.bus = bus

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Documento", "Telefone", "Email"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        actions = QHBoxLayout()
        btn_new = QPushButton("Novo")
        btn_edit = QPushButton("Editar")
        btn_delete = QPushButton("Excluir")
        btn_refresh = QPushButton("Atualizar")

        btn_new.clicked.connect(self.create_new)
        btn_edit.clicked.connect(self.edit_selected)
        btn_delete.clicked.connect(self.delete_selected)
        btn_refresh.clicked.connect(self.load_suppliers)

        actions.addWidget(btn_new)
        actions.addWidget(btn_edit)
        actions.addWidget(btn_delete)
        actions.addStretch(1)
        actions.addWidget(btn_refresh)

        layout.addLayout(actions)
        layout.addWidget(self.table)

        self.load_suppliers()

    def load_suppliers(self):
        try:
            rows = self.client.list_suppliers()
            self.table.setRowCount(0)
            for s in rows:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(s["id"])))
                self.table.setItem(r, 1, QTableWidgetItem(s["name"]))
                self.table.setItem(r, 2, QTableWidgetItem(s.get("document") or ""))
                self.table.setItem(r, 3, QTableWidgetItem(s.get("phone") or ""))
                self.table.setItem(r, 4, QTableWidgetItem(s.get("email") or ""))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def create_new(self):
        dlg = SupplierDialog(self, title="Novo fornecedor")
        if dlg.exec() != QDialog.Accepted:
            return
        name, doc, phone, email = dlg.values()
        if not name:
            QMessageBox.warning(self, "Atenção", "Nome é obrigatório.")
            return

        try:
            self.client.create_supplier(name=name, document=doc, phone=phone, email=email)
            self.load_suppliers()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def edit_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um fornecedor.")
            return

        supplier_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        doc = self.table.item(row, 2).text()
        phone = self.table.item(row, 3).text()
        email = self.table.item(row, 4).text()

        dlg = SupplierDialog(self, title=f"Editar fornecedor #{supplier_id}", name=name, document=doc, phone=phone, email=email)
        if dlg.exec() != QDialog.Accepted:
            return
        new_name, new_doc, new_phone, new_email = dlg.values()
        if not new_name:
            QMessageBox.warning(self, "Atenção", "Nome é obrigatório.")
            return

        try:
            self.client.update_supplier(
                supplier_id=supplier_id,
                name=new_name,
                document=new_doc,
                phone=new_phone,
                email=new_email,
            )
            self.load_suppliers()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def delete_selected(self):
        supplier_id = self._selected_id()
        if supplier_id is None:
            QMessageBox.warning(self, "Atenção", "Selecione um fornecedor.")
            return

        if QMessageBox.question(self, "Confirmar", f"Excluir fornecedor {supplier_id}?") != QMessageBox.Yes:
            return

        try:
            self.client.delete_supplier(supplier_id)
            self.load_suppliers()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
