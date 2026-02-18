from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, 
    QFrame, QProgressBar, QMessageBox, QInputDialog, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class FleetPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Cabeçalho Industrial
        header = QHBoxLayout()
        title = QLabel("🚜 Gestão de Frotas & Maquinário")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        # Status Rápido
        status_frame = QFrame()
        status_frame.setStyleSheet("background: #ecf0f1; border-radius: 5px; padding: 5px;")
        h_status = QHBoxLayout(status_frame)
        h_status.addWidget(QLabel("🔥 Combustível (Mês): <b>12.500 L</b>"))
        h_status.addSpacing(20)
        h_status.addWidget(QLabel("🔧 Em Manutenção: <b>2 Unidades</b>"))
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(status_frame)
        layout.addLayout(header)

        # --- ABAS ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { height: 40px; width: 150px; font-weight: bold; }
            QTabBar::tab:selected { background: #e67e22; color: white; }
        """)
        
        self.tab_fleet = QWidget()
        self.setup_fleet_tab()
        
        self.tab_fuel = QWidget()
        self.setup_fuel_tab()
        
        self.tabs.addTab(self.tab_fleet, "🚛 Veículos e Máquinas")
        self.tabs.addTab(self.tab_fuel, "⛽ Controle de Abastecimento")
        
        layout.addWidget(self.tabs)

    def setup_fleet_tab(self):
        lay = QVBoxLayout(self.tab_fleet)
        lay.setContentsMargins(10, 20, 10, 10)
        
        # Botões de Ação
        tools = QHBoxLayout()
        btn_add = QPushButton("+ Cadastrar Veículo/Máquina")
        btn_add.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        btn_add.clicked.connect(self.add_vehicle)
        
        btn_maint = QPushButton("🔧 Enviar para Manutenção")
        btn_maint.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; padding: 10px;")
        btn_maint.clicked.connect(self.send_maintenance)
        
        tools.addWidget(btn_add)
        tools.addWidget(btn_maint)
        tools.addStretch()
        lay.addLayout(tools)
        
        # Tabela
        self.table_fleet = QTableWidget(0, 6)
        self.table_fleet.setHorizontalHeaderLabels(["ID", "Tipo", "Modelo/Placa", "Horímetro/Km", "Status", "Operador"])
        self.table_fleet.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_fleet.setAlternatingRowColors(True)
        lay.addWidget(self.table_fleet)
        
        # Dados Fictícios
        self.add_fleet_row("FR-01", "Caminhão", "Volvo FH 540 (ABC-1234)", "150.000 Km", "🟢 Operante", "Carlos Silva")
        self.add_fleet_row("MQ-05", "Trator", "John Deere 7230J", "4.500 Hrs", "🔴 Manutenção", "--")
        self.add_fleet_row("UT-02", "Utilitário", "Fiat Strada (XYZ-9876)", "45.000 Km", "🟢 Operante", "Equipe Campo")

    def setup_fuel_tab(self):
        lay = QVBoxLayout(self.tab_fuel)
        lay.setContentsMargins(10, 20, 10, 10)
        
        tools = QHBoxLayout()
        btn_fuel = QPushButton("⛽ Registrar Abastecimento")
        btn_fuel.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; padding: 10px;")
        btn_fuel.clicked.connect(self.add_fuel)
        
        tools.addWidget(btn_fuel)
        tools.addStretch()
        lay.addLayout(tools)
        
        self.table_fuel = QTableWidget(0, 5)
        self.table_fuel.setHorizontalHeaderLabels(["Data", "Veículo", "Litros (L)", "Valor Total", "Posto/Bomba"])
        self.table_fuel.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.table_fuel)
        
        # Dados Exemplo
        self.add_fuel_row("14/02/2026", "Volvo FH 540", "450 L", "R$ 2.925,00", "Bomba Interna 01")

    # --- Funções Auxiliares ---
    def add_fleet_row(self, id_cod, tipo, modelo, km, status, op):
        r = self.table_fleet.rowCount()
        self.table_fleet.insertRow(r)
        self.table_fleet.setItem(r, 0, QTableWidgetItem(id_cod))
        self.table_fleet.setItem(r, 1, QTableWidgetItem(tipo))
        self.table_fleet.setItem(r, 2, QTableWidgetItem(modelo))
        self.table_fleet.setItem(r, 3, QTableWidgetItem(km))
        
        item_status = QTableWidgetItem(status)
        if "Manutenção" in status:
            item_status.setForeground(QColor("red"))
            item_status.setFont(item_status.font()) # Bold se quiser
        else:
            item_status.setForeground(QColor("green"))
            
        self.table_fleet.setItem(r, 4, item_status)
        self.table_fleet.setItem(r, 5, QTableWidgetItem(op))

    def add_fuel_row(self, data, veiculo, litros, total, posto):
        r = self.table_fuel.rowCount()
        self.table_fuel.insertRow(r)
        self.table_fuel.setItem(r, 0, QTableWidgetItem(data))
        self.table_fuel.setItem(r, 1, QTableWidgetItem(veiculo))
        self.table_fuel.setItem(r, 2, QTableWidgetItem(litros))
        self.table_fuel.setItem(r, 3, QTableWidgetItem(total))
        self.table_fuel.setItem(r, 4, QTableWidgetItem(posto))

    # --- Ações dos Botões ---
    def add_vehicle(self):
        tipo, ok = QInputDialog.getItem(self, "Novo Cadastro", "Tipo de Equipamento:", ["Caminhão", "Trator", "Carro", "Empilhadeira"], 0, False)
        if ok and tipo:
            modelo, ok2 = QInputDialog.getText(self, "Novo Cadastro", f"Modelo do {tipo}:")
            if ok2 and modelo:
                self.add_fleet_row(f"NV-{self.table_fleet.rowCount()}", tipo, modelo, "0 Km", "🟢 Operante", "A definir")
                QMessageBox.information(self, "Sucesso", "Equipamento adicionado à frota!")

    def send_maintenance(self):
        row = self.table_fleet.currentRow()
        if row >= 0:
            id_maq = self.table_fleet.item(row, 0).text()
            self.table_fleet.item(row, 4).setText("🔴 Manutenção")
            self.table_fleet.item(row, 4).setForeground(QColor("red"))
            QMessageBox.warning(self, "Manutenção", f"Veículo {id_maq} enviado para a oficina interna.")
        else:
            QMessageBox.warning(self, "Erro", "Selecione um veículo na tabela primeiro.")

    def add_fuel(self):
        QMessageBox.information(self, "Abastecimento", "Aqui abriria o formulário de lançamento de diesel/etanol.")