from __future__ import annotations
import secrets
import sqlite3
import re
import requests  # Biblioteca para consultar a API do Brasil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, 
    QDateEdit, QGroupBox, QFormLayout, QFrame, QMessageBox, 
    QHeaderView, QTabWidget, QGridLayout, QScrollArea, QApplication, QCheckBox
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QIcon, QCursor
from app.core.config import settings  # <--- IMPORTAÇÃO ESSENCIAL PARA O BANCO CERTO

class AdminPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.setWindowTitle("Gestão de Unidades")
        
        # --- FORÇA TEMA CLARO (LIGHT MODE) ---
        # Isso garante que as letras fiquem pretas e o fundo branco
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #000000;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #000000;
                font-weight: 500;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #bdc3c7;
                padding: 6px;
                border-radius: 4px;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTableWidget {
                background-color: #ffffff;
                color: #000000;
                gridline-color: #e0e0e0;
                selection-background-color: #3498db;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #000000;
                padding: 5px;
                border: 1px solid #bdc3c7;
            }
            QCheckBox {
                color: #000000;
            }
        """)
        
        self.check_database() 
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- CABEÇALHO ---
        header = QFrame()
        header.setStyleSheet("background-color: #2c3e50; border-bottom: 3px solid #1a252f;")
        header.setFixedHeight(70)
        head_lay = QHBoxLayout(header)
        
        title = QLabel("🛡️ BERTOLINI COMMAND CENTER - GESTÃO DE LICENÇAS")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ecf0f1; background: transparent;")
        
        btn_logout = QPushButton("Sair do Admin")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton { background-color: #c0392b; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        btn_logout.clicked.connect(self.main.logout_system)
        
        head_lay.addWidget(title)
        head_lay.addStretch()
        head_lay.addWidget(btn_logout)
        layout.addWidget(header)

        # --- ABAS (Organização) ---
        self.tabs = QTabWidget()
        # Estilos das abas já definidos no StyleSheet global da classe, mas reforçando:
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #bdc3c7; }
            QTabBar::tab { background: #ecf0f1; color: black; padding: 10px 20px; }
            QTabBar::tab:selected { background: #ffffff; border-bottom: 2px solid #2980b9; font-weight: bold; }
        """)
        
        # Aba 1: Lista de Clientes (Gestão)
        self.tab_list = QWidget()
        self.setup_list_tab()
        
        # Aba 2: Novo Cadastro (Completo)
        self.tab_add = QWidget()
        self.setup_add_tab()
        
        self.tabs.addTab(self.tab_list, "🏢 Clientes Ativos")
        self.tabs.addTab(self.tab_add, "➕ Nova Implantação Customizada")
        
        layout.addWidget(self.tabs)

    def setup_list_tab(self):
        lay = QVBoxLayout(self.tab_list)
        lay.setContentsMargins(20, 20, 20, 20)
        
        # Filtros
        filter_lay = QHBoxLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔍 Buscar por Nome, CNPJ ou Login...")
        self.input_search.textChanged.connect(self.load_clients) 
        
        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.setStyleSheet("background-color: #7f8c8d; color: white; padding: 6px;")
        btn_refresh.clicked.connect(self.load_clients)
        
        filter_lay.addWidget(self.input_search)
        filter_lay.addWidget(btn_refresh)
        lay.addLayout(filter_lay)
        
        # Tabela
        self.table_stores = QTableWidget(0, 8)
        cols = ["ID", "Razão Social", "CNPJ", "Módulos Ativos", "Login", "Chave", "Validade", "Ações"]
        self.table_stores.setHorizontalHeaderLabels(cols)
        self.table_stores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_stores.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_stores.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        lay.addWidget(self.table_stores)
        self.load_clients() 

    def setup_add_tab(self):
        # Scroll area para telas menores
        scroll = QScrollArea(self.tab_add)
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)
        
        main_lay = QVBoxLayout(self.tab_add)
        main_lay.addWidget(scroll)

        lay = QVBoxLayout(content)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)

        lbl = QLabel("Cadastro Completo de Unidade")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        lay.addWidget(lbl)

        # --- DADOS EMPRESARIAIS ---
        group_emp = QGroupBox("Dados da Empresa (Busca Automática)")
        grid_emp = QGridLayout(group_emp)
        
        self.inp_cnpj = QLineEdit(); self.inp_cnpj.setPlaceholderText("Digite CNPJ e aperte Enter...")
        self.inp_cnpj.returnPressed.connect(self.search_cnpj) # Gatilho Busca CNPJ
        self.inp_cnpj.editingFinished.connect(self.search_cnpj)

        self.inp_razao = QLineEdit(); self.inp_razao.setPlaceholderText("Razão Social")
        self.inp_fantasia = QLineEdit(); self.inp_fantasia.setPlaceholderText("Nome Fantasia")
        self.inp_ie = QLineEdit(); self.inp_ie.setPlaceholderText("Inscrição Estadual")
        
        grid_emp.addWidget(QLabel("CNPJ (Busca Auto):"), 0, 0); grid_emp.addWidget(self.inp_cnpj, 0, 1)
        grid_emp.addWidget(QLabel("IE:"), 0, 2); grid_emp.addWidget(self.inp_ie, 0, 3)
        grid_emp.addWidget(QLabel("Razão Social:"), 1, 0); grid_emp.addWidget(self.inp_razao, 1, 1, 1, 3)
        grid_emp.addWidget(QLabel("Fantasia:"), 2, 0); grid_emp.addWidget(self.inp_fantasia, 2, 1, 1, 3)
        
        lay.addWidget(group_emp)

        # --- ENDEREÇO ---
        group_end = QGroupBox("Endereço & Contato (Busca CEP)")
        grid_end = QGridLayout(group_end)
        
        self.inp_cep = QLineEdit(); self.inp_cep.setPlaceholderText("CEP")
        self.inp_cep.returnPressed.connect(self.search_cep) # Gatilho Busca CEP
        self.inp_cep.editingFinished.connect(self.search_cep)

        self.inp_logradouro = QLineEdit(); self.inp_logradouro.setPlaceholderText("Rua / Av.")
        self.inp_num = QLineEdit(); self.inp_num.setPlaceholderText("Nº")
        self.inp_bairro = QLineEdit(); self.inp_bairro.setPlaceholderText("Bairro")
        self.inp_cidade = QLineEdit(); self.inp_cidade.setPlaceholderText("Cidade")
        self.inp_uf = QLineEdit(); self.inp_uf.setPlaceholderText("UF")
        self.inp_fone = QLineEdit(); self.inp_fone.setPlaceholderText("Telefone/WhatsApp")
        self.inp_email = QLineEdit(); self.inp_email.setPlaceholderText("Email Admin")

        grid_end.addWidget(QLabel("CEP:"), 0, 0); grid_end.addWidget(self.inp_cep, 0, 1)
        grid_end.addWidget(QLabel("Endereço:"), 0, 2); grid_end.addWidget(self.inp_logradouro, 0, 3)
        grid_end.addWidget(QLabel("Número:"), 0, 4); grid_end.addWidget(self.inp_num, 0, 5)
        
        grid_end.addWidget(QLabel("Bairro:"), 1, 0); grid_end.addWidget(self.inp_bairro, 1, 1)
        grid_end.addWidget(QLabel("Cidade:"), 1, 2); grid_end.addWidget(self.inp_cidade, 1, 3)
        grid_end.addWidget(QLabel("UF:"), 1, 4); grid_end.addWidget(self.inp_uf, 1, 5)

        grid_end.addWidget(QLabel("Telefone:"), 2, 0); grid_end.addWidget(self.inp_fone, 2, 1)
        grid_end.addWidget(QLabel("Email:"), 2, 2); grid_end.addWidget(self.inp_email, 2, 3)

        lay.addWidget(group_end)

        # --- SELETOR DE MÓDULOS (CUSTOMIZAÇÃO) ---
        group_mod = QGroupBox("📦 Módulos Habilitados (Bertolini Custom)")
        mod_lay = QGridLayout(group_mod)
        
        self.chk_vendas = QCheckBox("🛒 Vendas (PDV)"); self.chk_vendas.setChecked(True)
        self.chk_fin = QCheckBox("💰 Financeiro & DRE"); self.chk_fin.setChecked(True)
        self.chk_est = QCheckBox("📦 Estoque & Compras"); self.chk_est.setChecked(True)
        self.chk_fis = QCheckBox("🧾 Fiscal (NFe/NFCe)")
        self.chk_fro = QCheckBox("🚜 Frotas & Maquinário")
        self.chk_rh = QCheckBox("👥 RH & Ponto")
        self.chk_crm = QCheckBox("🤝 CRM & Agenda (WhatsApp)")
        
        mod_lay.addWidget(self.chk_vendas, 0, 0)
        mod_lay.addWidget(self.chk_fin, 0, 1)
        mod_lay.addWidget(self.chk_est, 0, 2)
        mod_lay.addWidget(self.chk_fis, 1, 0)
        mod_lay.addWidget(self.chk_fro, 1, 1)
        mod_lay.addWidget(self.chk_rh, 1, 2)
        mod_lay.addWidget(self.chk_crm, 2, 0)
        
        lay.addWidget(group_mod)

        # --- ACESSO E LICENÇA ---
        group_sys = QGroupBox("Credenciais de Acesso")
        grid_sys = QGridLayout(group_sys)

        self.inp_login = QLineEdit(); self.inp_login.setPlaceholderText("Login Master")
        self.inp_pass = QLineEdit(); self.inp_pass.setPlaceholderText("Senha Inicial")
        self.date_expiry = QDateEdit(QDate.currentDate().addMonths(1))
        self.date_expiry.setCalendarPopup(True)
        
        self.inp_key = QLineEdit(); self.inp_key.setReadOnly(True)
        self.inp_key.setPlaceholderText("Gerada Automaticamente ao Salvar")
        self.inp_key.setStyleSheet("background-color: #eeeeee; color: #555;")

        grid_sys.addWidget(QLabel("Login Admin:"), 0, 0); grid_sys.addWidget(self.inp_login, 0, 1)
        grid_sys.addWidget(QLabel("Senha Admin:"), 0, 2); grid_sys.addWidget(self.inp_pass, 0, 3)
        grid_sys.addWidget(QLabel("Validade Licença:"), 1, 0); grid_sys.addWidget(self.date_expiry, 1, 1)
        grid_sys.addWidget(QLabel("Chave do Sistema:"), 1, 2); grid_sys.addWidget(self.inp_key, 1, 3)

        lay.addWidget(group_sys)

        btn_save = QPushButton("💾 CADASTRAR E ATIVAR UNIDADE")
        btn_save.setFixedHeight(50)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; font-size: 15px; border-radius: 8px; }
            QPushButton:hover { background-color: #219150; }
        """)
        btn_save.clicked.connect(self.handle_save)
        lay.addWidget(btn_save)
        lay.addStretch()

    # --- CÉREBRO DE AUTOMAÇÃO (BRASIL API) ---
    def search_cnpj(self):
        cnpj = re.sub(r'\D', '', self.inp_cnpj.text())
        if len(cnpj) != 14: return 

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            # Consulta API gratuita
            response = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                self.inp_razao.setText(data.get("razao_social", ""))
                self.inp_fantasia.setText(data.get("nome_fantasia", "") or data.get("razao_social", ""))
                
                self.inp_cep.setText(data.get("cep", ""))
                self.inp_logradouro.setText(data.get("logradouro", ""))
                self.inp_num.setText(data.get("numero", ""))
                self.inp_bairro.setText(data.get("bairro", ""))
                self.inp_cidade.setText(data.get("municipio", ""))
                self.inp_uf.setText(data.get("uf", ""))
                self.inp_fone.setText(data.get("ddd_telefone_1", ""))
                
                # Sugere login
                sugestao = data.get("nome_fantasia", "").split()[0].lower()
                if sugestao: self.inp_login.setText(sugestao)
                
            else:
                print("CNPJ não encontrado.")
        except Exception as e:
            print(f"Erro API: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def search_cep(self):
        cep = re.sub(r'\D', '', self.inp_cep.text())
        if len(cep) != 8: return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            response = requests.get(f"https://brasilapi.com.br/api/cep/v2/{cep}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                self.inp_logradouro.setText(data.get("street", ""))
                self.inp_bairro.setText(data.get("neighborhood", ""))
                self.inp_cidade.setText(data.get("city", ""))
                self.inp_uf.setText(data.get("state", ""))
                self.inp_num.setFocus()
        except Exception as e:
            print(f"Erro CEP: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    # --- BANCO DE DADOS (SQLite Local) ---
    def check_database(self):
        """Cria/Verifica a tabela no banco oficial."""
        # USA O CAMINHO CENTRALIZADO
        conn = sqlite3.connect(settings.db_file_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, ie TEXT,
                cep TEXT, endereco TEXT, numero TEXT, bairro TEXT, cidade TEXT, uf TEXT,
                telefone TEXT, email TEXT, business_type TEXT, login TEXT UNIQUE, password TEXT,
                license_key TEXT, expiry_date TEXT, status TEXT DEFAULT 'Ativo'
            )
        """)
        conn.commit()
        conn.close()

    def handle_save(self):
        razao = self.inp_razao.text().strip()
        login = self.inp_login.text().strip()
        pwd = self.inp_pass.text().strip()
        
        if not razao or not login or not pwd:
            QMessageBox.warning(self, "Erro", "Preencha Razão Social, Login e Senha!")
            return

        # Gera Chave de Licença
        new_key = secrets.token_hex(8).upper()
        formatted_key = "-".join([new_key[i:i+4] for i in range(0, len(new_key), 4)])
        self.inp_key.setText(formatted_key)
        
        # CRIA A STRING DE MÓDULOS (A MÁGICA ACONTECE AQUI)
        modules = []
        if self.chk_vendas.isChecked(): modules.append("vendas")
        if self.chk_fin.isChecked(): modules.append("financeiro")
        if self.chk_est.isChecked(): modules.append("estoque")
        if self.chk_fis.isChecked(): modules.append("fiscal")
        if self.chk_fro.isChecked(): modules.append("frotas")
        if self.chk_rh.isChecked(): modules.append("rh")
        if self.chk_crm.isChecked(): modules.append("crm")
        
        modules_string = ",".join(modules)

        try:
            # USA O CAMINHO CENTRALIZADO
            conn = sqlite3.connect(settings.db_file_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clients (
                    razao_social, nome_fantasia, cnpj, ie, 
                    cep, endereco, numero, bairro, cidade, uf, telefone, email,
                    business_type, login, password, license_key, expiry_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                razao, self.inp_fantasia.text(), self.inp_cnpj.text(), self.inp_ie.text(),
                self.inp_cep.text(), self.inp_logradouro.text(), self.inp_num.text(),
                self.inp_bairro.text(), self.inp_cidade.text(), self.inp_uf.text(),
                self.inp_fone.text(), self.inp_email.text(),
                modules_string, login, pwd, formatted_key, self.date_expiry.date().toString("yyyy-MM-dd")
            ))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Sucesso", f"Unidade {razao} cadastrada com sucesso!")
            self.tabs.setCurrentIndex(0)
            self.load_clients()
            self.inp_login.clear(); self.inp_pass.clear()
            
        except sqlite3.IntegrityError:
             QMessageBox.warning(self, "Erro", "Login já existe!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar: {e}")

    def load_clients(self):
        self.table_stores.setRowCount(0)
        filter_txt = self.input_search.text().lower()
        
        try:
            # USA O CAMINHO CENTRALIZADO
            conn = sqlite3.connect(settings.db_file_path)
            cursor = conn.cursor()
            
            # Seleciona colunas (business_type agora guarda os módulos)
            try:
                cursor.execute("SELECT id, razao_social, cnpj, business_type, login, license_key, expiry_date FROM clients")
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                conn.close()
                QMessageBox.critical(self, "Aviso de Sistema", "Banco de dados desatualizado. Exclua 'storage.db' e reinicie.")
                return

            conn.close()
            
            for row_data in rows:
                if filter_txt:
                    if filter_txt not in str(row_data[1]).lower() and filter_txt not in str(row_data[2]).lower():
                        continue

                row = self.table_stores.rowCount()
                self.table_stores.insertRow(row)
                
                for i, val in enumerate(row_data):
                    self.table_stores.setItem(row, i, QTableWidgetItem(str(val)))
                
                # Botão Excluir
                btn_del = QPushButton("🗑️")
                btn_del.setStyleSheet("background: #c0392b; color: white; border-radius: 4px; font-weight: bold;")
                btn_del.setFixedSize(30, 30)
                cid = row_data[0]
                btn_del.clicked.connect(lambda _, c=cid: self.delete_client(c))
                
                container = QWidget()
                h = QHBoxLayout(container); h.setContentsMargins(5,2,5,2); h.setAlignment(Qt.AlignCenter)
                h.addWidget(btn_del)
                self.table_stores.setCellWidget(row, 7, container)
                
        except Exception as e:
            print(f"Erro load: {e}")

    def delete_client(self, cid):
        if QMessageBox.question(self, 'Excluir', "Confirmar exclusão?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            try:
                # USA O CAMINHO CENTRALIZADO
                conn = sqlite3.connect(settings.db_file_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM clients WHERE id = ?", (cid,))
                conn.commit()
                conn.close()
                self.load_clients()
            except Exception as e: pass