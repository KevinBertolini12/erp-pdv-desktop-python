from datetime import date, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import QDate

from app.clients.api_client import ApiClient


class ReportsPage(QWidget):
    def __init__(self, api_base_url: str, bus=None):
        super().__init__()
        self.client = ApiClient(api_base_url)
        self.bus = bus

        if self.bus:
            self.bus.stock_changed.connect(self.load)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.lbl_summary = QLabel("Resumo: —")
        layout.addWidget(self.lbl_summary)

        controls = QHBoxLayout()
        self.dt_start = QDateEdit()
        self.dt_end = QDateEdit()
        self.dt_start.setCalendarPopup(True)
        self.dt_end.setCalendarPopup(True)

        today = date.today()
        self.dt_end.setDate(QDate(today.year, today.month, today.day))
        start = today - timedelta(days=6)
        self.dt_start.setDate(QDate(start.year, start.month, start.day))

        btn_load = QPushButton("Carregar")
        btn_load.clicked.connect(self.load)

        controls.addWidget(QLabel("Início:"))
        controls.addWidget(self.dt_start)
        controls.addWidget(QLabel("Fim:"))
        controls.addWidget(self.dt_end)
        controls.addWidget(btn_load)
        controls.addStretch(1)
        layout.addLayout(controls)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Data", "Produto", "Delta", "Motivo"])
        layout.addWidget(self.table, 1)

        self.load()

    def load(self):
        try:
            s = self.client.reports_summary()
            self.lbl_summary.setText(
                f"Resumo: {s['total_products']} produtos | estoque total {s['total_stock']} | baixo (<=5): {s['low_stock']}"
            )

            start = self.dt_start.date().toPython()
            end = self.dt_end.date().toPython()
            data = self.client.reports_stock_moves_range(start=start.isoformat(), end=end.isoformat())["items"]

            self.table.setRowCount(0)
            for it in data:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(it.get("created_at", "")))
                self.table.setItem(row, 1, QTableWidgetItem(it.get("product_name", "")))
                self.table.setItem(row, 2, QTableWidgetItem(str(it.get("delta", 0))))
                self.table.setItem(row, 3, QTableWidgetItem(it.get("reason", "")))

            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
