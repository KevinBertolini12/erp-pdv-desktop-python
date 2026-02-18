from __future__ import annotations
import os
import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QSizePolicy, QAbstractItemView, QApplication, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCharts import (
    QChart, QChartView, QBarSet, QBarSeries, QLineSeries,
    QBarCategoryAxis, QValueAxis, QCategoryAxis
)

from app.clients.api_client import ApiClient
from app.utils.pdf_generator import PDFGenerator 
from app.core.auth import current_session 
from app.utils.stats_engine import StatsEngine 

DASHBOARD_STYLES = """
    QFrame#Card { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 15px; }
    QFrame#CardEnterprise { background-color: #ffffff; border-left: 8px solid #2980b9; border-radius: 8px; padding: 15px; }
    QFrame#CardAlert { background-color: #ffffff; border-left: 8px solid #e67e22; border-radius: 8px; padding: 15px; }
    QFrame#CardQuality { background-color: #ffffff; border-left: 8px solid #16a085; border-radius: 8px; padding: 15px; }
    QLabel#CardTitle { color: #757575; font-size: 11px; font-weight: bold; }
    QLabel#CardValue { color: #1a1a1a; font-size: 24px; font-weight: 800; }
    QTableWidget { background-color: #ffffff; border-radius: 10px; }
    QPushButton#RefreshBtn { background-color: #2c3e50; color: white; font-weight: bold; border-radius: 5px; }
    QPushButton#ExecBtn { background-color: #2980b9; color: white; font-weight: bold; border-radius: 5px; padding: 10px; }
"""

def _card(title: str, value: str, style_type="normal") -> QFrame:
    box = QFrame()
    if style_type == "enterprise": box.setObjectName("CardEnterprise")
    elif style_type == "alert": box.setObjectName("CardAlert")
    elif style_type == "quality": box.setObjectName("CardQuality")
    else: box.setObjectName("Card")
    
    lay = QVBoxLayout(box); lay.setSpacing(2)
    t = QLabel(title.upper()); t.setObjectName("CardTitle")
    v = QLabel(value); v.setObjectName("CardValue")
    lay.addWidget(t); lay.addWidget(v)
    return box

class DashboardPage(QWidget):
    def __init__(self, api_base_url: str, business_type="workshop", bus=None):
        super().__init__()
        self.setStyleSheet(DASHBOARD_STYLES)
        self.bus = bus
        self.business_type = business_type 
        self.client = ApiClient(api_base_url)

        if self.bus:
            self.bus.subscribe("products_changed", self.refresh)
            self.bus.subscribe("stock_changed", self.refresh)
            self.bus.subscribe("sale_finalized", self.refresh)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 1. CABEÇALHO DINÂMICO
        header_lay = QHBoxLayout()
        icon = "🏭" if self.business_type == "enterprise" else "🛒"
        title_text = "BI & PERFORMANCE INDUSTRIAL" if self.business_type == "enterprise" else "RESUMO DE VAREJO"
        self.lbl_title = QLabel(f"{icon} {title_text}")
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        header_lay.addWidget(self.lbl_title)
        header_lay.addStretch()
        
        if self.business_type == "enterprise" and current_session.has_permission("gerente"):
            self.btn_exec = QPushButton("📥 RELATÓRIO PDF")
            self.btn_exec.setObjectName("ExecBtn")
            self.btn_exec.clicked.connect(self.export_executive_report)
            header_lay.addWidget(self.btn_exec)

        self.btn_refresh = QPushButton("🔄 ATUALIZAR (F5)")
        self.btn_refresh.setObjectName("RefreshBtn")
        self.btn_refresh.setFixedSize(160, 40)
        self.btn_refresh.clicked.connect(self.refresh)
        header_lay.addWidget(self.btn_refresh)
        self.main_layout.addLayout(header_lay)

        # 2. CARDS DINÂMICOS
        self.cards_row = QHBoxLayout()
        self.setup_cards()
        self.main_layout.addLayout(self.cards_row)

        # 3. ÁREA DOS GRÁFICOS
        charts_layout = QHBoxLayout()
        self.bar_chart_view = QChartView(); self.bar_chart_view.setRenderHint(QPainter.Antialiasing)
        self.line_chart_view = QChartView(); self.line_chart_view.setRenderHint(QPainter.Antialiasing)
        self.bar_chart_view.setMinimumHeight(350); self.line_chart_view.setMinimumHeight(350)
        
        charts_layout.addWidget(self.bar_chart_view)
        charts_layout.addWidget(self.line_chart_view)
        self.main_layout.addLayout(charts_layout)

        # 4. TABELA DE ALERTAS
        bottom_layout = QVBoxLayout()
        self.lbl_table = QLabel("⚠️ ALERTAS DE ESTOQUE CRÍTICO / MÍNIMO")
        self.lbl_table.setStyleSheet("font-weight: bold; color: #c0392b;")
        
        self.low_stock_table = QTableWidget(0, 3)
        self.low_stock_table.setHorizontalHeaderLabels(["Produto", "NCM/Fiscal", "Qtd Atual"])
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.low_stock_table.setMaximumHeight(180)
        
        bottom_layout.addWidget(self.lbl_table)
        bottom_layout.addWidget(self.low_stock_table)
        self.main_layout.addLayout(bottom_layout)

        self.refresh()

    def setup_cards(self):
        for i in reversed(range(self.cards_row.count())): 
            item = self.cards_row.itemAt(i).widget()
            if item: item.setParent(None)

        if self.business_type == "enterprise":
            self.card_main = _card("Faturamento Total", "R$ 0,00", "enterprise")
            self.card_quality = _card("Índice de Qualidade", "100%", "quality")
            self.card_maint = _card("Alertas Manutenção", "0", "alert")
            
            self.cards_row.addWidget(self.card_main)
            self.cards_row.addWidget(self.card_quality)
            self.cards_row.addWidget(self.card_maint)
            
            if current_session.has_permission("gerente"):
                self.card_margin = _card("Margem Líquida", "0.0%", "enterprise")
                self.cards_row.addWidget(self.card_margin)
        else:
            self.card_main = _card("Vendas Hoje", "R$ 0,00")
            self.card_ticket = _card("Ticket Médio", "R$ 0,00")
            self.card_low = _card("Itens em Alerta", "0")
            self.card_valuation = _card("Patrimônio", "R$ 0,00")
            for c in [self.card_main, self.card_ticket, self.card_low, self.card_valuation]:
                self.cards_row.addWidget(c)

    def refresh(self):
        try:
            self.btn_refresh.setEnabled(False)
            products = self.client.list_products()
            summary = self.client.reports_summary() 
            moves = self.client.reports_stock_moves_7d()
            
            # --- INTEGRAÇÃO BI (Lógica Real de Banco) ---
            total_real_vendas = 0.0
            db_conn = sqlite3.connect("test.db")
            cursor = db_conn.cursor()
            try:
                # Tenta somar faturamento real se a tabela existir
                cursor.execute("SELECT SUM(total_value) FROM sales")
                res = cursor.fetchone()[0]
                total_real_vendas = res if res else 0.0
            except: pass
            db_conn.close()

            total_valuation = sum(p.get("price", 0) * p.get("stock_qty", 0) for p in products)
            
            if self.business_type == "enterprise":
                # Mostra o faturamento total acumulado no BI Industrial
                self.card_main.findChild(QLabel, "CardValue").setText(f"R$ {total_real_vendas:,.2f}")
                self.card_quality.findChild(QLabel, "CardValue").setText("98.4%")
                self.card_maint.findChild(QLabel, "CardValue").setText("2")
                
                if current_session.has_permission("gerente"):
                    lucro_est = total_real_vendas * 0.22 
                    self.card_margin.findChild(QLabel, "CardValue").setText(f"{(lucro_est/total_real_vendas*100) if total_real_vendas > 0 else 0:.1f}%")
            else:
                vendas_hoje = summary.get("sales_today_value", 0.0)
                n_vendas = summary.get("sales_today_count", 1)
                ticket_medio = vendas_hoje / n_vendas if n_vendas > 0 else 0
                
                self.card_main.findChild(QLabel, "CardValue").setText(f"R$ {vendas_hoje:,.2f}")
                self.card_ticket.findChild(QLabel, "CardValue").setText(f"R$ {ticket_medio:,.2f}")
                self.card_low.findChild(QLabel, "CardValue").setText(str(summary.get("low_stock", 0)))
                self.card_valuation.findChild(QLabel, "CardValue").setText(f"R$ {total_valuation:,.2f}")

            self.update_bar_chart(products)
            self.update_line_chart(moves)
            self.update_table(products)

        except Exception as e: print(f"Erro Dashboard: {e}")
        finally: self.btn_refresh.setEnabled(True)

    def export_executive_report(self):
        if not current_session.has_permission("gerente"): return
        try:
            faturamento_txt = self.card_main.findChild(QLabel, "CardValue").text()
            faturamento = float(faturamento_txt.replace("R$ ","").replace(".","").replace(",","."))
            dados = {"faturamento": faturamento, "custos": faturamento * 0.65, "impostos": faturamento * 0.18}
            path = PDFGenerator.gerar_relatorio_lucratividade({"razao_social": "BERTOLINI CORP - SERTÃOZINHO"}, dados)
            QMessageBox.information(self, "PDF", f"Relatório Gerado: {path}")
            os.startfile(os.path.abspath(path))
        except Exception as e: QMessageBox.critical(self, "Erro", str(e))

    def update_table(self, products):
        low_items = [p for p in products if p.get("stock_qty", 0) <= p.get("min_stock", 5)]
        self.low_stock_table.setRowCount(0)
        for p in low_items[:10]:
            r = self.low_stock_table.rowCount(); self.low_stock_table.insertRow(r)
            self.low_stock_table.setItem(r, 0, QTableWidgetItem(p["name"]))
            self.low_stock_table.setItem(r, 1, QTableWidgetItem(p.get("ncm_code", "0000.00.00")))
            self.low_stock_table.setItem(r, 2, QTableWidgetItem(str(p["stock_qty"])))
            if p["stock_qty"] <= 0: self.low_stock_table.item(r, 2).setForeground(QColor("red"))

    def update_bar_chart(self, products):
        top_items = sorted(products, key=lambda x: x.get("stock_qty", 0), reverse=True)[:5]
        series = QBarSeries(); set0 = QBarSet("Estoque"); categories = []
        for p in top_items:
            set0.append(p.get("stock_qty", 0))
            categories.append(p.get("name", "Item")[:10])
        series.append(set0)
        chart = QChart(); chart.addSeries(series); chart.setTitle("TOP 5 ESTOQUE")
        chart.setTheme(QChart.ChartThemeBlueIcy)
        axis_x = QBarCategoryAxis(); axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom); series.attachAxis(axis_x)
        self.bar_chart_view.setChart(chart)

    def update_line_chart(self, moves_data):
        series = QLineSeries(); series.setName("Vendas"); categories = []
        if isinstance(moves_data, list):
            for i, p in enumerate(moves_data):
                series.append(i, p.get("count", 0)); categories.append(p.get("date", ""))
        chart = QChart(); chart.addSeries(series); chart.setTitle("FLUXO 7 DIAS")
        chart.setTheme(QChart.ChartThemeBlueCerulean)
        axis_x = QCategoryAxis()
        for i, cat in enumerate(categories): axis_x.append(cat, i)
        chart.addAxis(axis_x, Qt.AlignBottom); series.attachAxis(axis_x)
        self.line_chart_view.setChart(chart)