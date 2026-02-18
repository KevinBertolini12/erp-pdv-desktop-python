from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox,
    QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QIcon
import os

# Tenta importar o motor de PDF do seu Utils
try:
    from app.utils.pdf_generator import PDFGenerator
except ImportError:
    PDFGenerator = None

class QualityPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # --- CABEÇALHO ---
        header = QFrame()
        header.setStyleSheet("background-color: #16a085; border-radius: 8px; padding: 15px;")
        h_lay = QHBoxLayout(header)
        
        lbl_icon = QLabel("🧪")
        lbl_icon.setStyleSheet("font-size: 30px;")
        
        lbl_title = QLabel("LIMS - GESTÃO DE QUALIDADE & LAUDOS TÉCNICOS")
        lbl_title.setStyleSheet("color: white; font-weight: bold; font-size: 20px;")
        
        h_lay.addWidget(lbl_icon)
        h_lay.addWidget(lbl_title)
        h_lay.addStretch()
        layout.addWidget(header)

        # --- FORMULÁRIO DE ANÁLISE ---
        group_ana = QGroupBox("Nova Análise Laboratorial")
        group_ana.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #aaa; margin-top: 10px; }")
        grid_ana = QFormLayout(group_ana)
        
        self.inp_lote = QLineEdit()
        self.inp_lote.setPlaceholderText("Ex: LOTE-2026-AB")
        
        self.inp_produto = QLineEdit()
        self.inp_produto.setPlaceholderText("Ex: Álcool Etílico Hidratado / Polímero PET")
        
        # Campos Específicos (Química)
        self.inp_param1 = QLineEdit() # Ex: Brix / pH
        self.inp_param1.setPlaceholderText("Parâmetro 1 (Ex: pH 7.0)")
        
        self.inp_param2 = QLineEdit() # Ex: Pol / Densidade
        self.inp_param2.setPlaceholderText("Parâmetro 2 (Ex: Densidade 0.8)")
        
        btn_run = QPushButton("🔬 Executar Análise e Gerar Laudo")
        btn_run.setFixedHeight(45)
        btn_run.setCursor(Qt.PointingHandCursor)
        btn_run.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; font-size: 14px;")
        btn_run.clicked.connect(self.run_analysis)
        
        grid_ana.addRow("Lote / Amostra:", self.inp_lote)
        grid_ana.addRow("Produto:", self.inp_produto)
        grid_ana.addRow("Resultado 1:", self.inp_param1)
        grid_ana.addRow("Resultado 2:", self.inp_param2)
        grid_ana.addRow(btn_run)
        
        layout.addWidget(group_ana)

        # --- TABELA DE HISTÓRICO ---
        lbl_hist = QLabel("📋 Histórico de Certificados Emitidos")
        lbl_hist.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495e; margin-top: 10px;")
        layout.addWidget(lbl_hist)
        
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Data", "Lote", "Produto", "Resultado", "Status", "Ação"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def run_analysis(self):
        lote = self.inp_lote.text()
        prod = self.inp_produto.text()
        p1 = self.inp_param1.text()
        
        if not lote or not p1:
            QMessageBox.warning(self, "Erro", "Preencha os dados da análise.")
            return
            
        # Lógica de Aprovação (Simulação Inteligente)
        try:
            val = float(p1.replace(',', '.'))
            # Exemplo: Se for pH, tem que ser entre 6 e 8
            status = "APROVADO" if 6.0 <= val <= 8.0 else "REPROVADO"
            color = "green" if status == "APROVADO" else "red"
        except:
            status = "EM ANÁLISE"
            color = "blue"

        # Adiciona na Tabela
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(QDate.currentDate().toString("dd/MM/yyyy")))
        self.table.setItem(row, 1, QTableWidgetItem(lote))
        self.table.setItem(row, 2, QTableWidgetItem(prod))
        self.table.setItem(row, 3, QTableWidgetItem(p1))
        
        item_status = QTableWidgetItem(status)
        item_status.setForeground(QColor(color))
        item_status.setFont(self.font()) # Negrito
        self.table.setItem(row, 4, item_status)
        
        # Botão PDF
        btn_pdf = QPushButton("📄 PDF")
        btn_pdf.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;")
        btn_pdf.clicked.connect(lambda: self.generate_pdf(lote, status))
        
        container = QWidget()
        lay = QHBoxLayout(container); lay.setContentsMargins(2,2,2,2)
        lay.addWidget(btn_pdf)
        self.table.setCellWidget(row, 5, container)
        
        QMessageBox.information(self, "Concluído", f"Lote {lote} processado com status: {status}")

    def generate_pdf(self, lote, status):
        """Chama o motor de PDF para criar o documento oficial"""
        if PDFGenerator:
            try:
                # Dados para o laudo
                empresa = {"razao_social": "BERTOLINI INDUSTRIAL SOLUTIONS"}
                lote_info = {"produto": self.inp_produto.text(), "lote_num": lote}
                resultados = [{
                    'param': 'Análise Principal',
                    'medido': self.inp_param1.text(),
                    'spec': '6.0 - 8.0',
                    'status': status
                }]
                
                path = PDFGenerator.gerar_certificado_qualidade(empresa, lote_info, resultados)
                os.startfile(os.path.abspath(path)) # Abre o PDF na tela
            except Exception as e:
                QMessageBox.critical(self, "Erro PDF", f"Falha ao gerar: {e}")
        else:
            QMessageBox.warning(self, "Aviso", "Módulo PDFGenerator não encontrado. Instale a biblioteca reportlab.")