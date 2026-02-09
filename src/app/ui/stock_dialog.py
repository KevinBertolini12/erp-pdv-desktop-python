from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QLineEdit, QPushButton


class StockDialog(QDialog):
    def __init__(self, parent=None, product_name: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Ajustar estoque")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Produto: {product_name}"))

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Delta (+/-):"))
        self.sp_delta = QSpinBox()
        self.sp_delta.setRange(-10_000_000, 10_000_000)
        self.sp_delta.setValue(1)
        row1.addWidget(self.sp_delta)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Motivo:"))
        self.ed_reason = QLineEdit()
        self.ed_reason.setText("Ajuste manual")
        row2.addWidget(self.ed_reason)

        btns = QHBoxLayout()
        btn_ok = QPushButton("Aplicar")
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btns.addStretch(1)
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(btns)

    def values(self):
        return int(self.sp_delta.value()), self.ed_reason.text().strip() or "Ajuste"
