from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt

class LockScreen(QWidget):
    def __init__(self, on_unlock_callback):
        super().__init__()
        self.on_unlock_callback = on_unlock_callback
        self.init_ui()

    def init_ui(self):
        # Fundo escuro/avermelhado para dar clima de bloqueio
        self.setStyleSheet("background-color: #2c3e50;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Card de Bloqueio
        card = QFrame()
        card.setFixedSize(500, 400)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 2px solid #e74c3c;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        # Ícone e Título
        title = QLabel("⚠️ SISTEMA BLOQUEADO")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e74c3c; border: none;")
        title.setAlignment(Qt.AlignCenter)

        msg = QLabel("Sua licença expirou ou não foi identificada.\nPara continuar utilizando o Bertolini ERP, realize a renovação.")
        msg.setStyleSheet("font-size: 14px; color: #34495e; border: none;")
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignCenter)

        # Campo para nova Key
        self.edit_key = QLineEdit()
        self.edit_key.setPlaceholderText("Cole sua nova chave de ativação aqui...")
        self.edit_key.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #e74c3c; }
        """)

        btn_unlock = QPushButton("ATIVAR SISTEMA")
        btn_unlock.setCursor(Qt.PointingHandCursor)
        btn_unlock.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_unlock.clicked.connect(self.handle_unlock)

        # Rodapé com seu contato
        support_info = QLabel("Suporte Técnico: (16) 9xxxx-xxxx\nDesenvolvido por Bertolini Sistemas")
        support_info.setStyleSheet("font-size: 11px; color: #7f8c8d; border: none;")
        support_info.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(msg)
        card_layout.addStretch()
        card_layout.addWidget(self.edit_key)
        card_layout.addWidget(btn_unlock)
        card_layout.addStretch()
        card_layout.addWidget(support_info)

        main_layout.addWidget(card)

    def handle_unlock(self):
        key = self.edit_key.text().strip()
        # Aqui chamamos a função que a MainWindow vai passar para validar
        self.on_unlock_callback(key)