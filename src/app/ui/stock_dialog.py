from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
)


class StockDialog(QDialog):
    def __init__(self, parent=None, *, product_name: str):
        super().__init__(parent)
        self.setWindowTitle(f"Ajustar estoque — {product_name}")
        self.setModal(True)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Quantidade (use negativo para saída)"))
        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(-1_000_000, 1_000_000)
        self.spin_qty.setValue(0)
        layout.addWidget(self.spin_qty)

        layout.addWidget(QLabel("Motivo"))
        self.txt_reason = QLineEdit()
        self.txt_reason.setText("Ajuste")
        layout.addWidget(self.txt_reason)

        buttons = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_ok = QPushButton("Aplicar")

        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self._on_ok)

        buttons.addStretch(1)
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_ok)

        layout.addLayout(buttons)

    def _on_ok(self):
        if self.spin_qty.value() == 0:
            QMessageBox.warning(self, "Atenção", "Quantidade não pode ser zero.")
            return
        self.accept()

    def values(self) -> tuple[int, str]:
        return self.spin_qty.value(), self.txt_reason.text().strip() or "Ajuste"
