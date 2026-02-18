import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFrame, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QColor, QIcon

class MonitoringPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.check_database() # Garante que a estrutura exista
        self.init_ui()
        
        # Timer para verificar atualizações reais em tempo real
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_live_data)
        self.refresh_timer.start(5000) # Atualiza a cada 5 segundos

    def check_database(self):
        """Garante que a estrutura de vendas exista para evitar erros de SQL"""
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_value REAL,
                    payment_method TEXT,
                    items TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao inicializar banco master: {e}")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # --- HEADER (VISÃO MASTER) ---
        header = QFrame()
        header.setStyleSheet("background-color: #2c3e50; border-radius: 10px; padding: 15px;")
        h_lay = QHBoxLayout(header)
        
        lbl_title = QLabel("📡 CENTRAL DE MONITORAMENTO BERTOLINI CLOUD")
        lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.lbl_status = QLabel("● SISTEMA ONLINE")
        self.lbl_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        h_lay.addWidget(lbl_title)
        h_lay.addStretch()
        h_lay.addWidget(self.lbl_status)
        layout.addWidget(header)

        # --- PAINEL SUPERIOR: UNIDADES ATIVAS ---
        top_row = QHBoxLayout()
        
        # Tabela de Unidades Conectadas
        self.table_units = QTableWidget(0, 4)
        self.table_units.setHorizontalHeaderLabels(["Unidade ID", "Última Sincronização", "Status", "Faturamento Total"])
        self.table_units.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_units.setStyleSheet("QTableWidget { background: white; border-radius: 8px; }")
        top_row.addWidget(self.table_units, 2)
        
        # Painel KPI de Faturamento Global
        kpi_frame = QFrame()
        kpi_frame.setStyleSheet("background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px;")
        kpi_lay = QVBoxLayout(kpi_frame)
        self.lbl_total_sales = QLabel("Vendas Totais (Nuvem)\nR$ 0,00")
        self.lbl_total_sales.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
        self.lbl_active_users = QLabel("Unidades Conectadas: 0")
        self.lbl_active_users.setStyleSheet("font-weight: bold; color: #2980b9;")
        
        kpi_lay.addWidget(self.lbl_total_sales)
        kpi_lay.addWidget(self.lbl_active_users)
        kpi_lay.addStretch()
        top_row.addWidget(kpi_frame, 1)
        
        layout.addLayout(top_row)

        # --- PAINEL INFERIOR: LOGS EM TEMPO REAL ---
        log_group = QVBoxLayout()
        log_group.addWidget(QLabel("📜 Fluxo de Dados em Tempo Real (Live Stream):", styleSheet="font-weight: bold; color: #34495e;"))
        
        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True)
        self.txt_logs.setPlaceholderText("Aguardando tráfego de dados das unidades...")
        self.txt_logs.setStyleSheet("""
            background-color: #1e272e; 
            color: #2ecc71; 
            font-family: 'Consolas'; 
            font-size: 12px; 
            border-radius: 5px;
            padding: 10px;
        """)
        log_group.addWidget(self.txt_logs)
        
        layout.addLayout(log_group)

    def update_live_data(self):
        """Busca faturamento real e popula tabela de unidades dinamicamente"""
        try:
            # 1. Conexão com o Banco Master
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            
            # 2. Soma faturamento global real das unidades
            cursor.execute("SELECT SUM(total_value) FROM sales")
            res_total = cursor.fetchone()[0]
            total_global = res_total if res_total else 0.0
            self.lbl_total_sales.setText(f"Vendas Totais (Nuvem)\nR$ {total_global:,.2f}")
            
            # 3. Busca unidades únicas que já enviaram dados (Baseado no ID que criamos no server)
            # Filtramos por payment_method que contenha 'SYNC_FROM_'
            cursor.execute("""
                SELECT 
                    payment_method, 
                    MAX(timestamp), 
                    SUM(total_value) 
                FROM sales 
                WHERE payment_method LIKE 'SYNC_FROM_%'
                GROUP BY payment_method
            """)
            unidades_reais = cursor.fetchall()
            
            self.table_units.setRowCount(0)
            self.lbl_active_users.setText(f"Unidades Conectadas: {len(unidades_reais)}")
            
            for method, last_sync, unit_total in unidades_reais:
                unit_id = method.replace("SYNC_FROM_", "")
                row = self.table_units.rowCount()
                self.table_units.insertRow(row)
                
                # Preenche a tabela com dados reais vindos da nuvem
                self.table_units.setItem(row, 0, QTableWidgetItem(unit_id))
                self.table_units.setItem(row, 1, QTableWidgetItem(last_sync))
                
                status_item = QTableWidgetItem("ONLINE")
                status_item.setForeground(QColor("#27ae60")) # Verde se recebeu dados
                self.table_units.setItem(row, 2, status_item)
                
                self.table_units.setItem(row, 3, QTableWidgetItem(f"R$ {unit_total:,.2f}"))
            
            # 4. Gera log de pulsação (Apenas se houver nova atividade ou para manter o pulso)
            if len(unidades_reais) > 0:
                self.log_event("Sincronização de pacotes recebida com sucesso.")
            else:
                self.log_event("Escutando tráfego de dados regional...")
            
            conn.close()
        except Exception as e:
            self.log_event(f"ALERTA DE SISTEMA: Falha crítica na leitura SQL -> {str(e)}")

    def log_event(self, message):
        """Função para o sistema enviar logs externos para esta tela"""
        now = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.txt_logs.append(f"[{now}] {message}")