from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFrame, QProgressBar, QTabWidget,
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QColor

class HRPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Cabeçalho de Performance
        header = QFrame()
        header.setStyleSheet("background-color: #2c3e50; border-radius: 8px; padding: 15px;")
        header_lay = QVBoxLayout(header)
        lbl = QLabel("👥 GESTÃO DE PESSOAS E COMISSÕES")
        lbl.setStyleSheet("color: white; font-weight: bold; font-size: 18px;")
        header_lay.addWidget(lbl)
        layout.addWidget(header)

        # Sistema de Abas para organizar Ranking e Ponto
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { height: 40px; font-weight: bold; padding: 0 20px; }")
        
        # --- ABA 1: PERFORMANCE ---
        self.tab_perf = QWidget()
        perf_lay = QVBoxLayout(self.tab_perf)
        
        perf_lay.addWidget(QLabel("<b>🏆 TOP PERFORMANCE (VENDAS MÊS)</b>"))
        self.table_ranking = QTableWidget(0, 3)
        self.table_ranking.setHorizontalHeaderLabels(["Colaborador", "Vendas Acumuladas", "Comissão a Pagar"])
        self.table_ranking.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        perf_lay.addWidget(self.table_ranking)
        
        # Mock de dados originais
        self.add_ranking_data("Kevin Bertolini", "R$ 15.400,00", "R$ 770,00")
        self.add_ranking_data("Vendedor Loja 01", "R$ 8.200,00", "R$ 164,00")

        # --- ABA 2: PONTO ELETRÔNICO (CRACHÁ) ---
        self.tab_ponto = QWidget()
        ponto_lay = QVBoxLayout(self.tab_ponto)
        
        # Box de Batida de Ponto
        clock_box = QFrame()
        clock_box.setStyleSheet("background: #f8f9fa; border: 2px solid #3498db; border-radius: 10px; padding: 20px;")
        clock_lay = QHBoxLayout(clock_box)
        
        self.badge_input = QLineEdit()
        self.badge_input.setPlaceholderText("Aguardando leitura do crachá...")
        self.badge_input.setStyleSheet("font-size: 18px; padding: 10px;")
        self.badge_input.returnPressed.connect(self.registrar_ponto)
        
        btn_punch = QPushButton("Bater Ponto")
        btn_punch.setStyleSheet("background: #3498db; color: white; font-weight: bold; padding: 10px 20px;")
        btn_punch.clicked.connect(self.registrar_ponto)
        
        clock_lay.addWidget(QLabel("<b>PONTO RÁPIDO:</b>"))
        clock_lay.addWidget(self.badge_input)
        clock_lay.addWidget(btn_punch)
        ponto_lay.addWidget(clock_box)
        
        # Tabela de Histórico de Batidas
        self.table_ponto = QTableWidget(0, 3)
        self.table_ponto.setHorizontalHeaderLabels(["Horário", "Colaborador", "Evento"])
        self.table_ponto.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ponto_lay.addWidget(self.table_ponto)
        
        self.tabs.addTab(self.tab_perf, "📊 Ranking & Comissões")
        self.tabs.addTab(self.tab_ponto, "⏱️ Ponto Eletrônico")
        
        layout.addWidget(self.tabs)

    def add_ranking_data(self, nome, total, comissao):
        row = self.table_ranking.rowCount()
        self.table_ranking.insertRow(row)
        self.table_ranking.setItem(row, 0, QTableWidgetItem(nome))
        self.table_ranking.setItem(row, 1, QTableWidgetItem(total))
        self.table_ranking.setItem(row, 2, QTableWidgetItem(comissao))

    def registrar_ponto(self):
        codigo = self.badge_input.text().strip()
        if not codigo: return
        
        nome = "Kevin Bertolini" if "001" in codigo else f"ID: {codigo}"
        agora = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")
        
        row = self.table_ponto.rowCount()
        self.table_ponto.insertRow(0)
        self.table_ponto.setItem(0, 0, QTableWidgetItem(agora))
        self.table_ponto.setItem(0, 1, QTableWidgetItem(nome))
        
        status = "Entrada" if row % 2 == 0 else "Saída"
        item_status = QTableWidgetItem(status)
        item_status.setForeground(QColor("green" if status == "Entrada" else "orange"))
        self.table_ponto.setItem(0, 2, item_status)
        
        self.badge_input.clear()
        QMessageBox.information(self, "Ponto", f"Batida de {status} registrada para {nome}")