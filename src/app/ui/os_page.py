from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
    QComboBox, QLineEdit, QGroupBox, QPlainTextEdit, QMessageBox, QInputDialog, QAbstractItemView
)
from PySide6.QtCore import Qt
# Mantendo sua importação de PDF caso queira usar depois
from app.utils.pdf_generator import gerar_pdf_os
import os

class OSPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # --- CABEÇALHO ---
        header_lay = QHBoxLayout()
        title = QLabel("Gestão de Ordens de Serviço")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        
        btn_new_os = QPushButton("+ Nova OS")
        btn_new_os.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
        btn_new_os.clicked.connect(self.handle_new_os) # Conectado
        
        header_lay.addWidget(title)
        header_lay.addStretch()
        header_lay.addWidget(btn_new_os)
        layout.addLayout(header_lay)

        # --- GRID DE ORDENS ---
        self.table_os = QTableWidget(0, 5) # 5 Colunas
        self.table_os.setHorizontalHeaderLabels([
            "Nº OS", "Cliente", "Equipamento/Veículo", "Status", "Total (R$)"
        ])
        self.table_os.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_os.setSelectionBehavior(QAbstractItemView.SelectRows) # Seleciona linha inteira
        self.table_os.setStyleSheet("background-color: white; border-radius: 5px;")
        # Ao clicar na tabela, preenche os detalhes abaixo
        self.table_os.itemSelectionChanged.connect(self.populate_details)
        layout.addWidget(self.table_os)

        # --- FORMULÁRIO DE DETALHES ---
        detail_box = QGroupBox("Detalhes da OS Selecionada")
        detail_lay = QVBoxLayout(detail_box)
        
        self.txt_problem = QPlainTextEdit()
        self.txt_problem.setPlaceholderText("Descrição do defeito reclamado pelo cliente...")
        self.txt_problem.setMaximumHeight(80)
        
        status_lay = QHBoxLayout()
        status_lay.addWidget(QLabel("Mudar Status:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Aguardando Início", "Em Manutenção", "Aguardando Peças", "Finalizada", "Entregue"])
        
        btn_print = QPushButton("🖨️ Imprimir OS")
        btn_print.clicked.connect(self.handle_imprimir_os)
        
        status_lay.addWidget(self.combo_status)
        status_lay.addStretch()
        status_lay.addWidget(btn_print)
        
        detail_lay.addWidget(self.txt_problem)
        detail_lay.addLayout(status_lay)
        layout.addWidget(detail_box)

        # Dados iniciais de exemplo
        self.add_os_row("001/2026", "Kevin Bertolini", "Bicicleta Caloi Aro 29", "Em Manutenção", "R$ 150,00", "Freio ruim e marcha escapando.")

    def add_os_row(self, num, cliente, equip, status, total, desc=""):
        row = self.table_os.rowCount()
        self.table_os.insertRow(row)
        self.table_os.setItem(row, 0, QTableWidgetItem(num))
        self.table_os.setItem(row, 1, QTableWidgetItem(cliente))
        self.table_os.setItem(row, 2, QTableWidgetItem(equip))
        self.table_os.setItem(row, 3, QTableWidgetItem(status))
        self.table_os.setItem(row, 4, QTableWidgetItem(total))
        # Guardamos a descrição escondida no item 0 para recuperar depois
        self.table_os.item(row, 0).setData(Qt.UserRole, desc)

    def handle_new_os(self):
        # Criação rápida via Dialogs
        cliente, ok1 = QInputDialog.getText(self, "Nova OS", "Nome do Cliente:")
        if ok1 and cliente:
            equip, ok2 = QInputDialog.getText(self, "Nova OS", "Equipamento/Veículo:")
            if ok2 and equip:
                num = f"{self.table_os.rowCount() + 1:03d}/2026"
                self.add_os_row(num, cliente, equip, "Aguardando Início", "R$ 0,00", "Defeito a avaliar")
                QMessageBox.information(self, "Sucesso", f"OS {num} aberta com sucesso!")

    def populate_details(self):
        """Preenche o formulário de baixo quando clica na tabela"""
        rows = self.table_os.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            status = self.table_os.item(row, 3).text()
            desc = self.table_os.item(row, 0).data(Qt.UserRole)
            
            self.txt_problem.setPlainText(desc)
            index = self.combo_status.findText(status)
            if index >= 0:
                self.combo_status.setCurrentIndex(index)

    def handle_imprimir_os(self):
        rows = self.table_os.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma OS na tabela para imprimir.")
            return
            
        row = rows[0].row()
        # Coleta dados da linha selecionada
        dados = {
            "numero": self.table_os.item(row, 0).text(),
            "cliente": self.table_os.item(row, 1).text(),
            "equipamento": self.table_os.item(row, 2).text(),
            "status": self.table_os.item(row, 3).text(),
            "total": self.table_os.item(row, 4).text(),
            "descricao": self.txt_problem.toPlainText()
        }

        try:
            arquivo = gerar_pdf_os(dados)
            os.startfile(arquivo) 
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {e}\n(Verifique se instalou 'reportlab')")