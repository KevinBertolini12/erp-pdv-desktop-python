from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class SupplierDialog(QDialog):
    def __init__(self, parent=None, title="Fornecedor", name="", document="", phone="", email=""):
        super().__init__(parent)
        self.setWindowTitle(title)

        lay = QVBoxLayout(self)

        self.ed_name = QLineEdit(name)
        self.ed_doc = QLineEdit(document)
        self.ed_phone = QLineEdit(phone)
        self.ed_email = QLineEdit(email)

        lay.addWidget(QLabel("Nome *"))
        lay.addWidget(self.ed_name)
        lay.addWidget(QLabel("Documento (CNPJ/CPF)"))
        lay.addWidget(self.ed_doc)
        lay.addWidget(QLabel("Telefone"))
        lay.addWidget(self.ed_phone)
        lay.addWidget(QLabel("Email"))
        lay.addWidget(self.ed_email)

        row = QHBoxLayout()
        btn_ok = QPushButton("Salvar")
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        row.addStretch(1)
        row.addWidget(btn_cancel)
        row.addWidget(btn_ok)
        lay.addLayout(row)

    def values(self):
        return (
            self.ed_name.text().strip(),
            (self.ed_doc.text().strip() or None),
            (self.ed_phone.text().strip() or None),
            (self.ed_email.text().strip() or None),
        )
