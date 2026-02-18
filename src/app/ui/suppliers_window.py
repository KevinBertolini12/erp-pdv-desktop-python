import sqlite3
import requests
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QGroupBox, QFormLayout, QFrame, QApplication, QDialog,
    QAbstractItemView # <--- O ERRO ERA A FALTA DESTA IMPORTAÇÃO
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QCursor
from app.clients.api_client import ApiClient

# Pequena classe auxiliar para o Dialog de Edição
class SupplierDialog(QDialog):
    def __init__(self, parent=None, title="Fornecedor", name="", document="", phone="", email=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        lay = QFormLayout(self)
        self.inp_name = QLineEdit(name)
        self.inp_doc = QLineEdit(document)
        self.inp_phone = QLineEdit(phone)
        self.inp_email = QLineEdit(email)
        
        lay.addRow("Nome:", self.inp_name)
        lay.addRow("CNPJ/CPF:", self.inp_doc)
        lay.addRow("Telefone:", self.inp_phone)
        lay.addRow("Email:", self.inp_email)
        
        btn = QPushButton("Salvar")
        btn.clicked.connect(self.accept)
        lay.addRow(btn)

    def values(self):
        return self.inp_name.text(), self.inp_doc.text(), self.inp_phone.text(), self.inp_email.text()

class SuppliersWindow(QWidget):
    def __init__(self, api_base_url: str, bus=None):
        super().__init__()
        self.client = ApiClient(api_base_url)
        self.bus = bus
        self.setWindowTitle("Gestão de Fornecedores - Bertolini ERP")
        self.resize(1000, 700)
        
        self.check_db() # Garante tabela local
        self.init_ui()
        self.load_suppliers()

    def check_db(self):
        """Garante tabela local para cache ou uso offline"""
        conn = sqlite3.connect("test.db")
        conn.execute("CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, document TEXT, phone TEXT, email TEXT, address TEXT)")
        conn.close()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- CABEÇALHO COM ÍCONE ---
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #f39c12; border-radius: 8px; padding: 15px;")
        h_lay = QHBoxLayout(header_frame)
        
        icon_lbl = QLabel("🚚")
        icon_lbl.setStyleSheet("font-size: 30px; margin-right: 10px;")
        
        text_lay = QVBoxLayout()
        title_lbl = QLabel("GESTÃO DE FORNECEDORES")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        sub_lbl = QLabel("Cadastro e Controle de Parceiros Comerciais")
        sub_lbl.setStyleSheet("color: white; font-size: 12px;")
        text_lay.addWidget(title_lbl)
        text_lay.addWidget(sub_lbl)
        
        h_lay.addWidget(icon_lbl)
        h_lay.addLayout(text_lay)
        h_lay.addStretch()
        layout.addWidget(header_frame)

        # --- FORMULÁRIO DE CADASTRO (COM AUTOMACÃO) ---
        group = QGroupBox("Novo Cadastro (Busca Automática)")
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #ccc; margin-top: 10px; }")
        form = QFormLayout(group)
        
        # Linha CNPJ e Botão
        self.inp_cnpj = QLineEdit(); self.inp_cnpj.setPlaceholderText("Digite apenas números e aperte Enter...")
        self.inp_cnpj.returnPressed.connect(self.search_cnpj) # GATILHO DA MÁGICA
        
        self.inp_nome = QLineEdit(); self.inp_nome.setPlaceholderText("Razão Social")
        self.inp_phone = QLineEdit(); self.inp_phone.setPlaceholderText("Telefone")
        self.inp_email = QLineEdit(); self.inp_email.setPlaceholderText("Email de Contato")
        
        # Endereço
        end_lay = QHBoxLayout()
        self.inp_cep = QLineEdit(); self.inp_cep.setPlaceholderText("CEP + Enter"); self.inp_cep.setFixedWidth(120)
        self.inp_cep.returnPressed.connect(self.search_cep) # GATILHO DO CEP
        self.inp_address = QLineEdit(); self.inp_address.setPlaceholderText("Endereço Completo")
        end_lay.addWidget(self.inp_cep); end_lay.addWidget(self.inp_address)

        btn_save = QPushButton("💾 Salvar Fornecedor")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; height: 35px;")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.create_new)

        form.addRow("CNPJ (Busca):", self.inp_cnpj)
        form.addRow("Razão Social:", self.inp_nome)
        form.addRow("Telefone:", self.inp_phone)
        form.addRow("Email:", self.inp_email)
        form.addRow("Endereço:", end_lay)
        form.addRow(btn_save)
        
        layout.addWidget(group)

        # --- TABELA ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Documento", "Telefone", "E-mail", "Endereço"])
        # Agora o QAbstractItemView está importado e vai funcionar
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Barra de Ações Inferior
        actions = QHBoxLayout()
        btn_edit = QPushButton("✏️ Editar"); btn_edit.clicked.connect(self.edit_selected)
        btn_del = QPushButton("🗑️ Excluir"); btn_del.clicked.connect(self.delete_selected)
        btn_refresh = QPushButton("🔄 Atualizar Lista"); btn_refresh.clicked.connect(self.load_suppliers)
        
        actions.addStretch(); actions.addWidget(btn_edit); actions.addWidget(btn_del); actions.addWidget(btn_refresh)
        layout.addLayout(actions)

    # --- CÉREBRO DE AUTOMAÇÃO (BRASIL API) ---
    def search_cnpj(self):
        cnpj = re.sub(r'\D', '', self.inp_cnpj.text())
        if len(cnpj) != 14: return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}", timeout=3)
            if r.status_code == 200:
                d = r.json()
                self.inp_nome.setText(d.get("razao_social", "") or d.get("nome_fantasia", ""))
                self.inp_phone.setText(d.get("ddd_telefone_1", ""))
                self.inp_email.setText(d.get("email", ""))
                self.inp_cep.setText(d.get("cep", ""))
                # Monta endereço
                end = f"{d.get('logradouro','')} {d.get('numero','')}, {d.get('bairro','')}, {d.get('municipio','')}-{d.get('uf','')}"
                self.inp_address.setText(end)
            else:
                QMessageBox.warning(self, "Aviso", "CNPJ não encontrado na base pública.")
        except Exception as e:
            print(e)
        finally:
            QApplication.restoreOverrideCursor()

    def search_cep(self):
        cep = re.sub(r'\D', '', self.inp_cep.text())
        if len(cep) != 8: return
        try:
            r = requests.get(f"https://brasilapi.com.br/api/cep/v2/{cep}", timeout=3)
            if r.status_code == 200:
                d = r.json()
                self.inp_address.setText(f"{d.get('street','')}, {d.get('neighborhood','')}, {d.get('city','')}-{d.get('state','')}")
        except: pass

    # --- CRUD ---
    def load_suppliers(self):
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.execute("SELECT id, name, document, phone, email, address FROM suppliers")
            for row_data in cursor:
                row = self.table.rowCount(); self.table.insertRow(row)
                for i, val in enumerate(row_data):
                    self.table.setItem(row, i, QTableWidgetItem(str(val)))
            conn.close()
        except Exception as e:
            print(f"Erro load: {e}")

    def create_new(self):
        name = self.inp_nome.text()
        if not name: return QMessageBox.warning(self, "Erro", "Nome é obrigatório")
        
        try:
            conn = sqlite3.connect("test.db")
            conn.execute("INSERT INTO suppliers (name, document, phone, email, address) VALUES (?,?,?,?,?)",
                        (name, self.inp_cnpj.text(), self.inp_phone.text(), self.inp_email.text(), self.inp_address.text()))
            conn.commit(); conn.close()
            self.load_suppliers()
            # Limpa campos
            self.inp_nome.clear(); self.inp_cnpj.clear(); self.inp_phone.clear(); self.inp_email.clear(); self.inp_address.clear(); self.inp_cep.clear()
            QMessageBox.information(self, "Sucesso", "Fornecedor cadastrado!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def edit_selected(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.warning(self, "Aviso", "Selecione para editar")
        sid = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        doc = self.table.item(row, 2).text()
        phone = self.table.item(row, 3).text()
        email = self.table.item(row, 4).text()
        
        dlg = SupplierDialog(self, f"Editar ID {sid}", name, doc, phone, email)
        if dlg.exec():
            n, d, p, e = dlg.values()
            conn = sqlite3.connect("test.db")
            conn.execute("UPDATE suppliers SET name=?, document=?, phone=?, email=? WHERE id=?", (n, d, p, e, sid))
            conn.commit(); conn.close()
            self.load_suppliers()

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0: return
        sid = self.table.item(row, 0).text()
        if QMessageBox.question(self, "Excluir", "Tem certeza?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            conn = sqlite3.connect("test.db")
            conn.execute("DELETE FROM suppliers WHERE id=?", (sid,))
            conn.commit(); conn.close()
            self.load_suppliers()