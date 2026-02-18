import sqlite3
import requests
import uuid
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFrame, QDialog, QFormLayout, QLineEdit, 
    QComboBox, QMessageBox, QGroupBox, QScrollArea, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QCursor

class MasterDashboardPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.init_ui()
        QTimer.singleShot(200, self.load_clients)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho
        header = QFrame()
        header.setStyleSheet("background-color: #8e44ad; border-radius: 10px;")
        header.setFixedHeight(70)
        h_lay = QHBoxLayout(header)
        lbl = QLabel("🛸 BERTOLINI COMMAND CENTER - SaaS v5.0")
        lbl.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        h_lay.addWidget(lbl)
        
        # --- BOTÃO SAIR DA PÁGINA MASTER ---
        btn_logout_master = QPushButton("🚪 Sair / Trocar Usuário")
        btn_logout_master.setFixedSize(180, 40)
        btn_logout_master.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; border-radius: 5px;")
        btn_logout_master.clicked.connect(self.main.logout_system)
        h_lay.addWidget(btn_logout_master)
        
        layout.addWidget(header)

        # Ações
        btn_lay = QHBoxLayout()
        btn_add = QPushButton("➕ NOVO CLIENTE / EMPRESA")
        btn_add.setFixedHeight(45)
        btn_add.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; border-radius: 5px;")
        btn_add.clicked.connect(lambda: self.open_dialog())
        
        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.setFixedSize(100, 45)
        btn_refresh.clicked.connect(self.load_clients)
        
        btn_lay.addWidget(btn_add); btn_lay.addWidget(btn_refresh); btn_lay.addStretch()
        layout.addLayout(btn_lay)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(9) # Adicionada coluna de Ações
        self.table.setHorizontalHeaderLabels(["ID", "Empresa", "CNPJ", "Login", "Perfil", "Vencimento", "Status", "Licença", "Gerenciar"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def load_clients(self):
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, ie TEXT, im TEXT,
                    cep TEXT, endereco TEXT, numero TEXT, bairro TEXT, cidade TEXT, uf TEXT,
                    telefone TEXT, email TEXT, login TEXT, password TEXT, 
                    business_type TEXT, expiry_date TEXT, license_key TEXT, status TEXT DEFAULT 'Ativo'
                )
            """)
            cursor.execute("SELECT id, razao_social, cnpj, login, business_type, expiry_date, status, license_key FROM clients")
            rows = cursor.fetchall()
            conn.close()

            for idx, row in enumerate(rows):
                self.table.insertRow(idx)
                for col, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    if col == 5 and val and datetime.strptime(val, "%Y-%m-%d") < datetime.now():
                        item.setForeground(QColor("red"))
                    self.table.setItem(idx, col, item)
                
                # BOTÕES DE EDITAR E BLOQUEAR
                actions = QWidget()
                act_lay = QHBoxLayout(actions); act_lay.setContentsMargins(2,2,2,2)
                
                btn_edit = QPushButton("✏️"); btn_edit.setToolTip("Editar Empresa")
                btn_edit.clicked.connect(lambda ch, id=row[0]: self.open_dialog(id))
                
                btn_block = QPushButton("🔒" if row[6] == "Ativo" else "🔓")
                btn_block.clicked.connect(lambda ch, id=row[0], s=row[6]: self.toggle_status(id, s))
                
                act_lay.addWidget(btn_edit); act_lay.addWidget(btn_block)
                self.table.setCellWidget(idx, 8, actions)
        except Exception as e: print(f"Erro Master: {e}")

    def toggle_status(self, uid, current):
        new_s = "Bloqueado" if current == "Ativo" else "Ativo"
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE clients SET status = ? WHERE id = ?", (new_s, uid))
        conn.commit(); conn.close(); self.load_clients()

    def open_dialog(self, client_id=None):
        dlg = RegisterDialog(client_id, self)
        if dlg.exec(): self.load_clients()

class RegisterDialog(QDialog):
    def __init__(self, client_id=None, parent=None):
        super().__init__(parent)
        self.client_id = client_id # Se tiver ID, estamos EDITANDO
        self.setWindowTitle("🛸 Bertolini Command Center - Cadastro SaaS")
        self.setFixedSize(600, 750)
        self.init_ui()
        if client_id: self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); self.form = QFormLayout(content)
        
        # BUSCA INTELIGENTE CNPJ
        gb_busca = QGroupBox("🔍 Busca Automática (BrasilAPI)")
        bl = QHBoxLayout(gb_busca)
        self.inp_search = QLineEdit(); self.inp_search.setPlaceholderText("Digite CNPJ e clique em Buscar...")
        btn_s = QPushButton("Buscar"); btn_s.clicked.connect(self.fetch_cnpj)
        bl.addWidget(self.inp_search); bl.addWidget(btn_s)
        self.form.addRow(gb_busca)

        # CAMPOS COMPLETOS
        self.f = {}
        fields = [
            ("razao", "Razão Social"), ("fantasia", "Nome Fantasia"), ("cnpj", "CNPJ"),
            ("ie", "Inscrição Estadual"), ("im", "Inscrição Municipal"), ("cep", "CEP"),
            ("end", "Endereço"), ("num", "Número"), ("bairro", "Bairro"),
            ("cidade", "Cidade"), ("uf", "UF"), ("tel", "Telefone"), ("email", "Email"),
            ("user", "Login do Dono"), ("pwd", "Senha do Dono")
        ]
        
        for key, label in fields:
            self.f[key] = QLineEdit()
            self.form.addRow(f"{label}:", self.f[key])
            if key == "cep": self.f[key].editingFinished.connect(self.fetch_cep)

        self.combo_perfil = QComboBox(); self.combo_perfil.addItems(["workshop", "enterprise"])
        self.form.addRow("Perfil do Sistema:", self.combo_perfil)
        
        self.combo_plano = QComboBox(); self.combo_plano.addItems(["Mensal (30 dias)", "Anual (365 dias)", "Degustação (7 dias)"])
        self.form.addRow("Validade:", self.combo_plano)

        scroll.setWidget(content); layout.addWidget(scroll)
        
        btn_save = QPushButton("💾 SALVAR ALTERAÇÕES" if self.client_id else "🚀 CADASTRAR E ATIVAR")
        btn_save.setFixedHeight(50); btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)

    def fetch_cnpj(self):
        cnpj = self.inp_search.text().strip().replace(".","").replace("-","").replace("/","")
        try:
            r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}", timeout=5)
            if r.status_code == 200:
                d = r.json()
                self.f["razao"].setText(d.get("razao_social", ""))
                self.f["fantasia"].setText(d.get("nome_fantasia", ""))
                self.f["cnpj"].setText(cnpj)
                self.f["cep"].setText(d.get("cep", ""))
                self.f["end"].setText(d.get("logradouro", ""))
                self.f["num"].setText(d.get("numero", ""))
                self.f["bairro"].setText(d.get("bairro", ""))
                self.f["cidade"].setText(d.get("municipio", ""))
                self.f["uf"].setText(d.get("uf", ""))
        except: pass

    def fetch_cep(self):
        cep = self.f["cep"].text().strip().replace("-","")
        try:
            r = requests.get(f"https://brasilapi.com.br/api/cep/v1/{cep}")
            if r.status_code == 200:
                d = r.json()
                self.f["end"].setText(d.get("street", ""))
                self.f["bairro"].setText(d.get("neighborhood", ""))
                self.f["cidade"].setText(d.get("city", ""))
                self.f["uf"].setText(d.get("state", ""))
        except: pass

    def load_data(self):
        """Busca os dados do cliente para preencher os campos na edição"""
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id=?", (self.client_id,))
        c = cursor.fetchone()
        conn.close()
        if c:
            # Mapeia as colunas do banco para os seus campos de texto (f["key"])
            # Ordem no banco: 0:id, 1:razao, 2:fantasia, 3:cnpj... 14:user, 15:pwd
            self.f["razao"].setText(str(c[1]))
            self.f["cnpj"].setText(str(c[3]))
            self.f["cep"].setText(str(c[6]))
            self.f["end"].setText(str(c[7]))
            self.f["user"].setText(str(c[14]))
            self.f["pwd"].setText(str(c[15]))

    def save(self):
        """Salva: Faz UPDATE se for edição, INSERT se for novo"""
        dados = [self.f[k].text() for k in ["razao", "cnpj", "cep", "end", "user", "pwd"]]
        perfil = self.combo_perfil.currentText()
        
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        
        if self.client_id: # MODO EDIÇÃO
            cursor.execute("""
                UPDATE clients SET razao_social=?, cnpj=?, cep=?, endereco=?, login=?, password=?, business_type=? 
                WHERE id=?
            """, (*dados, perfil, self.client_id))
            msg = "Empresa atualizada com sucesso!"
        else: # MODO NOVO CADASTRO
            exp = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            lic = str(uuid.uuid4()).upper()[:16]
            cursor.execute("""
                INSERT INTO clients (razao_social, cnpj, cep, endereco, login, password, business_type, expiry_date, license_key)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (*dados, perfil, exp, lic))
            msg = f"Licença Ativada! Chave: {lic}"
            
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Sucesso", msg)
        self.accept()