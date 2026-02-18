from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt

class BIPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        # Cabeçalho
        self.header = QLabel("Dashboard de Inteligência - Bertolini ERP")
        self.header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        self.layout.addWidget(self.header)

        # Container para os gráficos (vazio inicialmente)
        self.charts_container = QHBoxLayout()
        
        # Mensagem inicial/Botão de ativação
        self.info_frame = QFrame()
        self.info_lay = QVBoxLayout(self.info_frame)
        
        msg = QLabel("Os gráficos de desempenho estão prontos para serem gerados.")
        msg.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        msg.setAlignment(Qt.AlignCenter)
        
        self.btn_render = QPushButton("📊 Gerar Relatórios Visuais")
        self.btn_render.setMinimumHeight(60)
        self.btn_render.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; font-size: 16px; border-radius: 10px; }
            QPushButton:hover { background-color: #219150; }
        """)
        self.btn_render.clicked.connect(self.draw_charts)
        
        self.info_lay.addWidget(msg)
        self.info_lay.addWidget(self.btn_render)
        self.layout.addWidget(self.info_frame)
        
        self.layout.addLayout(self.charts_container)

    def draw_charts(self):
        """Apenas aqui o Matplotlib é chamado"""
        try:
            # Imports tardios para evitar crash no boot
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            
            # Remove o frame de informação
            self.info_frame.hide()

            # --- Gráfico 1: Vendas ---
            fig1 = Figure(figsize=(5, 4), dpi=100)
            canvas1 = FigureCanvas(fig1)
            ax1 = fig1.add_subplot(111)
            ax1.plot(['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'], [12, 15, 11, 19, 25, 32, 8], marker='o', color='#3498db')
            ax1.set_title("Faturamento Semanal")
            self.charts_container.addWidget(canvas1)

            # --- Gráfico 2: Top Itens ---
            fig2 = Figure(figsize=(5, 4), dpi=100)
            canvas2 = FigureCanvas(fig2)
            ax2 = fig2.add_subplot(111)
            ax2.bar(['Pneu', 'Câmara', 'M.O.', 'Cabo', 'Freio'], [45, 80, 120, 30, 55], color='#2ecc71')
            ax2.set_title("Top Itens Vendidos")
            self.charts_container.addWidget(canvas2)

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro de Gráficos", f"Falha ao carregar motor de gráficos: {e}")