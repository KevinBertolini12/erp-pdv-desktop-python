from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFormLayout
)
from PySide6.QtCore import Qt

class SupplierDialog(QDialog):
    def __init__(self, parent=None, title="Fornecedor", name="", document="", phone="", email=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # O QFormLayout alinha automaticamente Label na esquerda e Campo na direita
        form = QFormLayout()
        form.setSpacing(12)

        self.ed_name = QLineEdit(name)
        self.ed_name.setPlaceholderText("Razão Social ou Nome Completo")
        
        self.ed_doc = QLineEdit(document)
        self.ed_doc.setPlaceholderText("CNPJ ou CPF")
        
        self.ed_phone = QLineEdit(phone)
        self.ed_phone.setPlaceholderText("(00) 00000-0000")
        
        self.ed_email = QLineEdit(email)
        self.ed_email.setPlaceholderText("exemplo@email.com")

        form.addRow("Nome/Razão Social *:", self.ed_name)
        form.addRow("Documento:", self.ed_doc)
        form.addRow("Telefone:", self.ed_phone)
        form.addRow("E-mail:", self.ed_email)

        layout.addLayout(form)

        # Botões de Ação
        btns_layout = QHBoxLayout()
        btn_ok = QPushButton("Salvar")
        btn_ok.setMinimumHeight(35)
        # Verde padrão Bertolini para ações positivas
        btn_ok.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumHeight(35)
        
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        btns_layout.addStretch(1)
        btns_layout.addWidget(btn_cancel)
        btns_layout.addWidget(btn_ok)
        
        layout.addLayout(btns_layout)

    def values(self):
        return (
            self.ed_name.text().strip(),
            self.ed_doc.text().strip() or None,
            self.ed_phone.text().strip() or None,
            self.ed_email.text().strip() or None,
        )