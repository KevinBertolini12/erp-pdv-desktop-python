import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, 
    QFormLayout, QFrame, QDialog, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class CustomerDialog(QDialog):
    def __init__(self, parent=None, title="Cliente", name="", phone="", email=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        lay = QFormLayout(self)
        
        # --- INPUTS COM PLACEHOLDERS (TEXTO FANTASMA) ---
        self.inp_name = QLineEdit(name)
        self.inp_name.setPlaceholderText("Digite o nome completo...")
        
        self.inp_phone = QLineEdit(phone)
        self.inp_phone.setPlaceholderText("Ex: (16) 99123-4567")
        
        self.inp_email = QLineEdit(email)
        self.inp_email.setPlaceholderText("exemplo@email.com")
        
        lay.addRow("Nome Completo:", self.inp_name)
        lay.addRow("WhatsApp/Tel:", self.inp_phone)
        lay.addRow("Email:", self.inp_email)
        
        btn = QPushButton("💾 Salvar")
        btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.accept)
        lay.addRow(btn)

    def values(self):
        return self.inp_name.text().strip(), self.inp_phone.text().strip(), self.inp_email.text().strip()

class CustomersWindow(QWidget):
    def __init__(self, api_base_url=""):
        super().__init__()
        self.setWindowTitle("Gestão de Clientes - Bertolini ERP")
        self.resize(900, 600)
        
        # Tenta carregar o ícone da aplicação
        self.setWindowIcon(QIcon("src/app/ui/assets/icon/logo.png"))
        
        self.check_db()
        self.init_ui()
        self.load_data()

    def check_db(self):
        """Cria a tabela no banco local se não existir"""
        conn = sqlite3.connect("test.db")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, 
                phone TEXT, 
                email TEXT
            )
        """)
        conn.close()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # --- CABEÇALHO ---
        header = QFrame()
        header.setStyleSheet("background-color: #8e44ad; border-radius: 8px; padding: 15px;")
        h_lay = QHBoxLayout(header)
        
        icon_lbl = QLabel("👥")
        icon_lbl.setStyleSheet("font-size: 24px;")
        
        title_lbl = QLabel("BASE DE CLIENTES (CRM)")
        title_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 18px;")
        
        h_lay.addWidget(icon_lbl)
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()
        layout.addWidget(header)

        # --- BARRA DE AÇÕES ---
        actions_lay = QHBoxLayout()
        btn_new = QPushButton("➕ Novo Cliente")
        btn_new.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 12px; border-radius: 6px;")
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.clicked.connect(self.create_new)
        
        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.clicked.connect(self.load_data)
        
        actions_lay.addWidget(btn_new)
        actions_lay.addStretch()
        actions_lay.addWidget(btn_refresh)
        layout.addLayout(actions_lay)

        # --- TABELA DE CLIENTES ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Telefone", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { gridline-color: #dcdde1; }")
        
        # Conecta o duplo clique para edição rápida
        self.table.cellDoubleClicked.connect(self.edit_selected)
        
        layout.addWidget(self.table)
        
        # Rodapé de Ajuda
        help_lbl = QLabel("💡 Dica: Dê um duplo clique em uma linha para editar os dados do cliente.")
        help_lbl.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 11px;")
        layout.addWidget(help_lbl)

    def load_data(self):
        """Recarrega os dados do banco local para a tabela"""
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.execute("SELECT id, name, phone, email FROM customers ORDER BY name ASC")
            for row_data in cursor:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for i, val in enumerate(row_data):
                    item = QTableWidgetItem(str(val))
                    if i == 0: item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, i, item)
            conn.close()
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")

    def create_new(self):
        """Abre o diálogo para cadastrar um novo cliente"""
        dlg = CustomerDialog(self, "Novo Cliente")
        if dlg.exec():
            name, phone, email = dlg.values()
            if not name:
                QMessageBox.warning(self, "Atenção", "O nome do cliente é obrigatório.")
                return
            
            try:
                conn = sqlite3.connect("test.db")
                conn.execute("INSERT INTO customers (name, phone, email) VALUES (?,?,?)", (name, phone, email))
                conn.commit()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar: {e}")

    def edit_selected(self):
        """Edita o cliente selecionado na tabela"""
        row = self.table.currentRow()
        if row < 0:
            return
            
        cid = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        phone = self.table.item(row, 2).text()
        email = self.table.item(row, 3).text()
        
        dlg = CustomerDialog(self, f"Editar Cliente #{cid}", name, phone, email)
        if dlg.exec():
            n, p, e = dlg.values()
            if not n:
                return
            
            try:
                conn = sqlite3.connect("test.db")
                conn.execute("UPDATE customers SET name=?, phone=?, email=? WHERE id=?", (n, p, e, cid))
                conn.commit()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao atualizar: {e}")