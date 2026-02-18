from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
    QTabWidget, QDateEdit, QGroupBox, QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
import os

# --- Importações do Sistema ---
from app.ui.manual_purchase_page import ManualPurchasePage 
# Tenta importar o gerador de PDF com segurança
try:
    from app.utils.pdf_generator import PDFGenerator
except ImportError:
    PDFGenerator = None

class FinancePage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- RESUMO RÁPIDO (CARDS) ---
        summary_layout = QHBoxLayout()
        self.card_in = self.create_summary_card("A Receber (Vendas)", "R$ 0,00", "#27ae60")
        self.card_out = self.create_summary_card("A Pagar (Despesas)", "R$ 0,00", "#e74c3c")
        self.card_balance = self.create_summary_card("Saldo Previsto", "R$ 0,00", "#2c3e50")
        
        summary_layout.addWidget(self.card_in)
        summary_layout.addWidget(self.card_out)
        summary_layout.addWidget(self.card_balance)
        layout.addLayout(summary_layout)

        # --- ABAS: PAGAR / RECEBER / DRE ---
        self.tabs = QTabWidget()
        
        self.tab_payable = QWidget()
        self.setup_payable_tab()
        
        self.tab_receivable = QWidget()
        self.setup_receivable_tab()

        self.tab_dre = QWidget()
        self.setup_dre_tab()

        self.tabs.addTab(self.tab_payable, "📉 Contas a Pagar (Despesas)")
        self.tabs.addTab(self.tab_receivable, "📈 Contas a Receber (Vendas)")
        self.tabs.addTab(self.tab_dre, "📊 Demonstrativo (DRE)")

        layout.addWidget(self.tabs)

    def create_summary_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"background-color: white; border-radius: 10px; border-left: 5px solid {color};")
        card.setMinimumHeight(100)
        lay = QVBoxLayout(card)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7f8c8d; font-size: 13px; font-weight: bold; border: none;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 900; border: none;")
        
        lay.addWidget(lbl_title)
        lay.addWidget(lbl_value)
        return card

    def setup_payable_tab(self):
        lay = QVBoxLayout(self.tab_payable)
        tools = QHBoxLayout()
        
        btn_new = QPushButton("+ Nova Despesa Manual")
        btn_new.setStyleSheet("background-color: #c0392b; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        btn_new.clicked.connect(self.open_manual_expense)
        
        tools.addWidget(btn_new)
        tools.addStretch()
        lay.addLayout(tools)

        self.table_payable = QTableWidget(0, 5)
        self.table_payable.setHorizontalHeaderLabels(["Vencimento", "Descrição", "Fornecedor", "Valor", "Status"])
        self.table_payable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.table_payable)

    def setup_receivable_tab(self):
        lay = QVBoxLayout(self.tab_receivable)
        self.table_receivable = QTableWidget(0, 5)
        self.table_receivable.setHorizontalHeaderLabels(["Data", "Cliente", "Forma Pagto", "Valor", "Status"])
        self.table_receivable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.table_receivable)

    def setup_dre_tab(self):
        lay = QVBoxLayout(self.tab_dre)
        lay.setContentsMargins(20, 20, 20, 20)

        header = QLabel("📝 DEMONSTRATIVO DE RESULTADOS DO EXERCÍCIO")
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        lay.addWidget(header)

        self.table_dre = QTableWidget(6, 2)
        self.table_dre.setHorizontalHeaderLabels(["Indicador Financeiro", "Valor Acumulado"])
        self.table_dre.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_dre.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Dados Iniciais (Mock)
        items = [
            ("RECEITA BRUTA OPERACIONAL", "R$ 45.000,00", "receita"),
            ("(-) TRIBUTOS E IMPOSTOS (NCM)", "R$ 4.500,00", "despesa"),
            ("(-) CUSTO DE MERCADORIA (CMV)", "R$ 15.000,00", "despesa"),
            ("(-) DESPESAS OPERACIONAIS", "R$ 8.000,00", "despesa"),
            ("(=) LUCRO LÍQUIDO", "R$ 17.500,00", "lucro"),
            ("⭐ MARGEM LÍQUIDA", "38%", "neutro")
        ]

        for i, (label, val, tipo) in enumerate(items):
            self.table_dre.setItem(i, 0, QTableWidgetItem(label))
            item_val = QTableWidgetItem(val)
            
            # Cores Visuais na Tabela
            if tipo == "lucro": item_val.setForeground(QColor("#27ae60")); item_val.setFont(self.font())
            elif tipo == "despesa": item_val.setForeground(QColor("#c0392b"))
            
            self.table_dre.setItem(i, 1, item_val)

        lay.addWidget(self.table_dre)
        
        btn_export = QPushButton("📂 Exportar DRE para PDF")
        btn_export.setStyleSheet("background-color: #2980b9; color: white; height: 40px; font-weight: bold;")
        btn_export.clicked.connect(self.export_dre_pdf)
        lay.addWidget(btn_export)

    # --- FUNÇÕES DE AÇÃO ---
    def open_manual_expense(self):
        self.manual_window = ManualPurchasePage(self.bus)
        self.manual_window.show()

    def export_dre_pdf(self):
        """Lê a tabela DRE e gera o PDF usando o novo motor"""
        if not PDFGenerator:
            QMessageBox.critical(self, "Erro", "Biblioteca 'reportlab' não encontrada.\nRode: pip install reportlab")
            return

        dados_exportacao = []
        for row in range(self.table_dre.rowCount()):
            desc = self.table_dre.item(row, 0).text()
            val_str = self.table_dre.item(row, 1).text()
            
            # Limpa R$ para converter (simplificado)
            try:
                val_float = float(val_str.replace("R$ ","").replace(".","").replace(",","."))
            except: val_float = 0.0
            
            tipo = 'neutro'
            if "(-)" in desc: tipo = 'despesa'
            elif "RECEITA" in desc: tipo = 'receita'
            
            dados_exportacao.append({"descricao": desc, "valor": val_float, "tipo": tipo})

        try:
            path = PDFGenerator.gerar_dre_pdf(dados_exportacao)
            QMessageBox.information(self, "Sucesso", f"DRE Gerado com Sucesso!\nSalvo em: {path}")
            os.startfile(path) # Abre o arquivo na tela
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar PDF: {e}")