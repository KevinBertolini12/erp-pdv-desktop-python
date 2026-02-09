from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class ProductDialog(QDialog):
    def __init__(self, parent=None, title: str = "Produto", name: str = "", sku: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Nome:"))
        self.ed_name = QLineEdit()
        self.ed_name.setText(name)
        row1.addWidget(self.ed_name)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("SKU:"))
        self.ed_sku = QLineEdit()
        self.ed_sku.setText(sku)
        row2.addWidget(self.ed_sku)

        btns = QHBoxLayout()
        btn_ok = QPushButton("Salvar")
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
        name = self.ed_name.text().strip()
        sku = self.ed_sku.text().strip() or None
        return name, sku
