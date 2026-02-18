from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QFrame, QGridLayout, QGroupBox, QPushButton, QLCDNumber
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor
import random

class ProductionPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()
        
        # Simulador de Sensores (Modbus Mock)
        # Na vida real, aqui entraria a leitura do IP do CLP da máquina
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensors)
        self.timer.start(1000) # Atualiza a cada 1 segundo (Tempo Real)

    def init_ui(self):
        # Fundo Escuro Industrial (Estilo Sala de Controle SCADA)
        self.setStyleSheet("background-color: #1e1e1e; color: #ecf0f1;")
        layout = QVBoxLayout(self)
        
        # Cabeçalho
        header = QLabel("🏭 BERTOLINI SCADA - MONITORAMENTO INDUSTRIAL (INDÚSTRIA 4.0)")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f1c40f; margin-bottom: 10px;")
        layout.addWidget(header)

        # Painel Principal de Máquinas
        grid = QGridLayout()
        
        # --- MÁQUINA 1: MOENDA A (Esmagamento) ---
        self.gauge_moenda = self.create_machine_card("MOENDA TERN A", "RPM", 0, 100)
        grid.addWidget(self.gauge_moenda, 0, 0)
        
        # --- MÁQUINA 2: CALDEIRA 04 (Pressão de Vapor) ---
        self.gauge_caldeira = self.create_machine_card("CALDEIRA 04 - ALTA", "Bar", 0, 60)
        grid.addWidget(self.gauge_caldeira, 0, 1)
        
        # --- MÁQUINA 3: COZEDOR C (Nível de Massa) ---
        self.gauge_cozedor = self.create_machine_card("COZEDOR C - VÁCUO", "Nível %", 0, 100)
        grid.addWidget(self.gauge_cozedor, 0, 2)

        # --- KPI: EFICIÊNCIA GLOBAL (OEE) ---
        kpi_frame = QFrame()
        kpi_frame.setStyleSheet("background-color: #2c3e50; border-radius: 10px; border: 2px solid #34495e;")
        kpi_lay = QVBoxLayout(kpi_frame)
        kpi_lay.addWidget(QLabel("EFICIÊNCIA GLOBAL (OEE)", alignment=Qt.AlignCenter))
        
        self.lcd_oee = QLCDNumber()
        self.lcd_oee.setDigitCount(5)
        self.lcd_oee.setStyleSheet("color: #2ecc71; border: none;")
        kpi_lay.addWidget(self.lcd_oee)
        grid.addWidget(kpi_frame, 1, 0, 1, 3) # Ocupa a largura toda embaixo

        layout.addLayout(grid)
        
        # Botões de Comando
        btn_stop = QPushButton("🚨 PARADA DE EMERGÊNCIA")
        btn_stop.setCursor(Qt.PointingHandCursor)
        btn_stop.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; font-size: 16px; padding: 15px; border-radius: 8px;")
        layout.addWidget(btn_stop)

    def create_machine_card(self, nome, unidade, min_val, max_val):
        frame = QFrame()
        frame.setStyleSheet("background-color: #2d3436; border-radius: 8px; padding: 10px;")
        lay = QVBoxLayout(frame)
        
        lbl_name = QLabel(f"🔴 {nome}")
        lbl_name.setStyleSheet("font-weight: bold; font-size: 14px; color: #e74c3c;") # Começa "Parado"
        
        bar = QProgressBar()
        bar.setRange(min_val, max_val)
        bar.setStyleSheet("""
            QProgressBar { border: 1px solid #555; border-radius: 5px; text-align: center; background: #333; color: white; }
            QProgressBar::chunk { background-color: #3498db; }
        """)
        bar.setFormat(f"%v {unidade}")
        
        lbl_val = QLabel("0.0")
        lbl_val.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498db;")
        lbl_val.setAlignment(Qt.AlignCenter)
        
        lay.addWidget(lbl_name)
        lay.addWidget(lbl_val)
        lay.addWidget(bar)
        
        # Guarda referências para atualizar depois
        frame.lbl_status = lbl_name
        frame.bar = bar
        frame.lbl_val = lbl_val
        frame.machine_name = nome
        return frame

    def update_sensors(self):
        # Simula leitura de sensores industriais
        
        # Moenda (Oscila entre 45 e 55 RPM)
        val_moenda = random.randint(45, 55)
        self.update_card(self.gauge_moenda, val_moenda, 50, "RPM")
        
        # Caldeira (Pressão estável ~42 Bar)
        val_caldeira = random.uniform(41.5, 42.5)
        self.update_card(self.gauge_caldeira, val_caldeira, 42, "Bar")
        
        # Cozedor (Nível subindo devagar até esvaziar)
        current = self.gauge_cozedor.bar.value()
        val_coz = current + 1 if current < 98 else 10
        self.update_card(self.gauge_cozedor, val_coz, 90, "%")
        
        # OEE Dinâmico
        self.lcd_oee.display(f"{random.uniform(88.0, 92.5):.2f}")

    def update_card(self, card, valor, limit, unit):
        card.bar.setValue(int(valor))
        card.lbl_val.setText(f"{valor:.1f}")
        
        # Lógica de Alarme Visual
        if valor > limit * 1.1: # 10% acima do limite ideal
            card.lbl_status.setText(f"⚠️ {card.machine_name} (ALERTA)")
            card.lbl_status.setStyleSheet("color: #f1c40f; font-weight: bold;")
            card.bar.setStyleSheet("QProgressBar::chunk { background-color: #f1c40f; }")
        else:
            card.lbl_status.setText(f"🟢 {card.machine_name} (OPERANDO)")
            card.lbl_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
            card.bar.setStyleSheet("QProgressBar::chunk { background-color: #2ecc71; }")