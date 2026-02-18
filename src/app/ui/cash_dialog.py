from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox

class CashMoveDialog(QDialog):
    def __init__(self, session_id, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.setWindowTitle("Movimentação de Caixa - Bertolini ERP")
        self.setFixedSize(300, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Tipo de Movimentação:"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["SANGRIA (Retirar Dinheiro)", "SUPRIMENTO (Colocar Troco)"])
        layout.addWidget(self.combo_type)
        
        layout.addWidget(QLabel("Valor (R$):"))
        self.edit_value = QLineEdit()
        self.edit_value.setPlaceholderText("0.00")
        layout.addWidget(self.edit_value)
        
        layout.addWidget(QLabel("Motivo / Observação:"))
        self.edit_reason = QLineEdit()
        layout.addWidget(self.edit_reason)
        
        self.btn_save = QPushButton("Confirmar Operação")
        self.btn_save.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; height: 40px;")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)

    def save(self):
        m_type = "SANGRIA" if "SANGRIA" in self.combo_type.currentText() else "SUPRIMENTO"
        try:
            val = float(self.edit_value.text().replace(",", "."))
            reason = self.edit_reason.text()
            
            # Chama o motor
            from app.utils.cash_engine import CashEngine
            CashEngine.registrar_movimento(self.session_id, m_type, val, reason)
            
            QMessageBox.information(self, "Sucesso", f"{m_type} realizada com sucesso!")
            self.accept()
        except:
            QMessageBox.critical(self, "Erro", "Valor inválido!")