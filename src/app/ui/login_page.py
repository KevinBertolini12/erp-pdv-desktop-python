from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, 
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from app.core.auth import current_session
from app.utils.audit_logger import AuditLogger

class LoginPage(QWidget):
    # Sinal envia quem logou (admin, vendedor, estoque ou bertolini_master)
    login_success = Signal(str) 

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # Fundo do Login (Identidade Visual Dark Industrial)
        self.setStyleSheet("background-color: #2c3e50;") 

        self.card = QFrame()
        self.card.setFixedSize(380, 520)
        self.card.setStyleSheet("background-color: white; border-radius: 15px;")
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(12)

        # Cabeçalho
        title = QLabel("BERTOLINI ERP")
        title.setStyleSheet("font-size: 26px; font-weight: 900; color: #2c3e50; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("SISTEMA DE GESTÃO INTEGRADA")
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        subtitle.setAlignment(Qt.AlignCenter)

        # Área de Status do QR Code
        self.lbl_status = QLabel("Aguardando Crachá ou Credenciais...")
        self.lbl_status.setStyleSheet("color: #3498db; font-size: 11px; font-style: italic;")
        self.lbl_status.setAlignment(Qt.AlignCenter)

        # ESTILO DOS CAMPOS
        field_style = """
            QLineEdit { 
                padding: 12px; 
                border: 2px solid #ecf0f1; 
                border-radius: 8px; 
                color: #2c3e50; 
                background-color: #f9f9f9; 
                font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #3498db; background-color: white; }
        """

        self.edit_user = QLineEdit()
        self.edit_user.setPlaceholderText("Usuário ou Token QR")
        self.edit_user.setMinimumHeight(45)
        self.edit_user.setStyleSheet(field_style)
        # Se o usuário der Enter no campo de usuário (comum em leitores de QR), tenta o login
        self.edit_user.returnPressed.connect(self.check_login)

        self.edit_pass = QLineEdit()
        self.edit_pass.setPlaceholderText("Senha")
        self.edit_pass.setEchoMode(QLineEdit.Password)
        self.edit_pass.setMinimumHeight(45)
        self.edit_pass.setStyleSheet(field_style)
        self.edit_pass.returnPressed.connect(self.check_login)

        self.btn_login = QPushButton("ENTRAR NO SISTEMA")
        self.btn_login.setMinimumHeight(55)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                font-weight: bold; 
                font-size: 14px;
                border-radius: 8px; 
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1a5276; }
        """)
        self.btn_login.clicked.connect(self.check_login)

        # Montagem do Card
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.lbl_status)
        card_layout.addSpacing(10)
        
        card_layout.addWidget(QLabel("<b>USUÁRIO</b>", styleSheet="color: #34495e; font-size: 11px;"))
        card_layout.addWidget(self.edit_user)
        
        card_layout.addWidget(QLabel("<b>SENHA</b>", styleSheet="color: #34495e; font-size: 11px;"))
        card_layout.addWidget(self.edit_pass)
        
        card_layout.addWidget(self.btn_login)
        
        # Rodapé de Versão
        ver = QLabel("v7.0 Enterprise Edition")
        ver.setStyleSheet("color: #bdc3c7; font-size: 9px;")
        ver.setAlignment(Qt.AlignCenter)
        card_layout.addStretch()
        card_layout.addWidget(ver)

        layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.edit_user.setFocus()

    def check_login(self):
        user = self.edit_user.text().lower().strip()
        pwd = self.edit_pass.text().strip()

        # --- LÓGICA DE CRACHÁ DIGITAL (QR CODE / TOKEN) ---
        # Simulamos tokens SHA256 curtos que o QRManager geraria
        tokens_mapeados = {
            "A1B2C3D4": ("admin", "gerente", "enterprise"),
            "E5F6G7H8": ("vendedor", "vendedor", "workshop"),
            "I9J0K1L2": ("estoque", "gerente", "workshop")
        }

        if user.upper() in tokens_mapeados:
            u_name, u_role, b_type = tokens_mapeados[user.upper()]
            current_session.start(u_name.capitalize(), u_role, b_type)
            AuditLogger.log("LOGIN", f"Acesso via Crachá Digital: {u_name}", level="INFO")
            self.login_success.emit(u_name)
            return

        # --- ACESSO MESTRE (GOD MODE) ---
        if user == "bertolini" and pwd == "masterkey":
            current_session.start("Bertolini Master", "admin", "enterprise")
            AuditLogger.log("LOGIN", "Acesso Mestre MasterKey utilizado", level="CRITICAL")
            self.login_success.emit("bertolini_master")
            return

        # --- ACESSOS TRADICIONAIS ---
        success = False
        if user == "admin" and pwd == "123":
            current_session.start("Administrador", "admin", "enterprise")
            self.login_success.emit("admin")
            success = True
        elif user == "vendedor" and pwd == "456":
            current_session.start("Vendedor Teste", "vendedor", "workshop")
            self.login_success.emit("vendedor")
            success = True
        elif user == "estoque" and pwd == "789":
            current_session.start("Operador Estoque", "gerente", "workshop")
            self.login_success.emit("estoque")
            success = True

        if success:
            AuditLogger.log("LOGIN", f"Usuário {user} logado manualmente", level="INFO")
        else:
            QMessageBox.warning(self, "Acesso Negado", "Credenciais ou Token Inválidos!")
            self.edit_user.clear()
            self.edit_pass.clear()
            self.edit_user.setFocus()