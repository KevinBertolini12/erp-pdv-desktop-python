from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
    QLineEdit, QCheckBox, QProgressBar
)
from PySide6.QtCore import Qt

class InventoryPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- CABEÇALHO COM KPIs ---
        kpi_layout = QHBoxLayout()
        self.card_total = self.create_kpi_card("Itens em Estoque", "1.240", "#3498db")
        self.card_critical = self.create_kpi_card("Itens Críticos", "12", "#e74c3c")
        self.card_value = self.create_kpi_card("Valor em Estoque", "R$ 45.200,00", "#2ecc71")
        
        kpi_layout.addWidget(self.card_total)
        kpi_layout.addWidget(self.card_critical)
        kpi_layout.addWidget(self.card_value)
        layout.addLayout(kpi_layout)

        # --- BARRA DE FERRAMENTAS ---
        tools = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Buscar produto no almoxarifado...")
        self.search_bar.setMinimumHeight(40)
        
        self.check_low_stock = QCheckBox("Mostrar apenas estoque baixo")
        
        btn_export = QPushButton("Exportar Inventário (PDF)")
        btn_export.setStyleSheet("background-color: #34495e; color: white; padding: 10px;")
        
        tools.addWidget(self.search_bar, stretch=2)
        tools.addWidget(self.check_low_stock)
        tools.addStretch()
        tools.addWidget(btn_export)
        layout.addLayout(tools)

        # --- TABELA DE ESTOQUE ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "SKU", "Produto", "Categoria", "Mínimo", "Atual", "Status Visual"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 8px;")
        layout.addWidget(self.table)

        # Exemplo de dado inserido
        self.add_inventory_row("PNEU-001", "Pneu Aro 29 Pirelli", "Peças", 5, 2)

    def create_kpi_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"background-color: white; border-radius: 10px; border-bottom: 4px solid {color};")
        card.setMinimumHeight(100)
        lay = QVBoxLayout(card)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: #7f8c8d; font-size: 13px; font-weight: bold; border: none;")
        lbl_v = QLabel(value)
        lbl_v.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold; border: none;")
        lay.addWidget(lbl_t)
        lay.addWidget(lbl_v)
        return card

    def add_inventory_row(self, sku, name, cat, min_q, current_q):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(sku))
        self.table.setItem(row, 1, QTableWidgetItem(name))
        self.table.setItem(row, 2, QTableWidgetItem(cat))
        self.table.setItem(row, 3, QTableWidgetItem(str(min_q)))
        self.table.setItem(row, 4, QTableWidgetItem(str(current_q)))
        
        # Barra de Progresso Visual do Estoque
        progress = QProgressBar()
        progress.setMaximum(min_q * 2) # Exemplo de escala
        progress.setValue(current_q)
        progress.setTextVisible(False)
        
        if current_q <= min_q:
            progress.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        else:
            progress.setStyleSheet("QProgressBar::chunk { background-color: #2ecc71; }")
            
        self.table.setCellWidget(row, 5, progress)