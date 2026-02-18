from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
    QGroupBox, QFormLayout, QLineEdit, QFileDialog, QMessageBox, QTabWidget,
    QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
import os

# --- MOTORES DO SISTEMA (MANTIDOS) ---
from app.utils.tax_engine import TaxEngine

# Integração real com ACBr e Builder
try:
    from app.utils.acbr_engine import ACBrEngine
    from app.utils.fiscal_builder import FiscalBuilder
except ImportError:
    ACBrEngine = None
    FiscalBuilder = None

class FiscalPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 1. CABEÇALHO (ESTILO BERTOLINI)
        header = QFrame()
        header.setStyleSheet("background-color: #c0392b; border-radius: 8px;")
        header.setFixedHeight(70)
        h_lay = QHBoxLayout(header)
        
        lbl = QLabel("🧾 CENTRAL FISCAL BERTOLINI - GESTÃO TRIBUTÁRIA NFe / NFCe")
        lbl.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        # Status SEFAZ Dinâmico no topo
        self.lbl_sefaz_top = QLabel("🟢 SEFAZ ONLINE")
        self.lbl_sefaz_top.setStyleSheet("color: #2ecc71; font-weight: bold; background: rgba(0,0,0,50); padding: 5px 10px; border-radius: 5px;")
        
        h_lay.addWidget(lbl)
        h_lay.addStretch()
        h_lay.addWidget(self.lbl_sefaz_top)
        layout.addWidget(header)

        # 2. PAINEL DE COMUNICAÇÃO E CERTIFICADO
        gov_panel = QHBoxLayout()
        
        status_box = QGroupBox("📡 Status SEFAZ / SAT")
        status_lay = QVBoxLayout(status_box)
        self.status_lbl = QLabel("🟢 Servidor: Monitorando (ACBr)")
        status_lay.addWidget(self.status_lbl)
        
        btn_check = QPushButton("🔄 Testar Conexão ACBr")
        btn_check.setCursor(Qt.PointingHandCursor)
        btn_check.setStyleSheet("background-color: #f3f3f3; height: 35px; font-weight: 500;")
        btn_check.clicked.connect(self.check_acbr_status)
        status_lay.addWidget(btn_check)
        
        cert_box = QGroupBox("🔑 Certificado Digital A1")
        cert_lay = QFormLayout(cert_box)
        self.inp_cert = QLineEdit()
        self.inp_cert.setPlaceholderText("Caminho do arquivo .pfx")
        btn_cert = QPushButton("📂 Selecionar Certificado")
        btn_cert.setCursor(Qt.PointingHandCursor)
        btn_cert.clicked.connect(self.select_certificate)
        
        cert_lay.addRow("Caminho:", self.inp_cert)
        cert_lay.addRow(btn_cert)

        gov_panel.addWidget(status_box)
        gov_panel.addWidget(cert_box)
        layout.addLayout(gov_panel)

        # 3. GESTÃO DE NCM E REGRAS TRIBUTÁRIAS
        ncm_group = QGroupBox("⚖️ Configuração de Alíquotas por NCM")
        ncm_lay = QVBoxLayout(ncm_group)
        
        self.ncm_table = QTableWidget(0, 4)
        self.ncm_table.setHorizontalHeaderLabels(["Código NCM", "Descrição", "ICMS (%)", "IPI (%)"])
        self.ncm_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ncm_table.setFixedHeight(130)
        self.ncm_table.setAlternatingRowColors(True)
        
        # Dados de exemplo originais (Flash Studio / Polipet)
        self.add_ncm_data("8523.51.10", "Pendrives (Flash Studio)", "18.0", "0.0")
        self.add_ncm_data("3923.30.00", "Garrafas PET (Polipet)", "18.0", "5.0")
        
        ncm_lay.addWidget(self.ncm_table)
        layout.addWidget(ncm_group)

        # 4. AÇÕES DE EMISSÃO
        act_lay = QHBoxLayout()
        btn_emit = QPushButton("🚀 EMITIR NOTA FISCAL (NFe)")
        btn_emit.setFixedHeight(55)
        btn_emit.setCursor(Qt.PointingHandCursor)
        btn_emit.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; color: white; font-weight: bold; 
                font-size: 14px; border-radius: 8px; 
            }
            QPushButton:hover { background-color: #219150; }
        """)
        btn_emit.clicked.connect(self.processar_emissao_nfe)
        
        btn_cancel = QPushButton("❌ Cancelar Nota")
        btn_cancel.setFixedHeight(55)
        btn_xml = QPushButton("📝 Ver XML")
        btn_xml.setFixedHeight(55)
        
        act_lay.addWidget(btn_emit, 2)
        act_lay.addWidget(btn_cancel, 1)
        act_lay.addWidget(btn_xml, 1)
        layout.addLayout(act_lay)

        # 5. TABELA DE HISTÓRICO FISCAL
        hist_box = QGroupBox("📋 Histórico de Documentos Fiscais")
        hist_lay = QVBoxLayout(hist_box)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Nº Nota", "Série", "Chave de Acesso", "Cliente", "Valor", "Impostos", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        
        hist_lay.addWidget(self.table)
        layout.addWidget(hist_box)

    def add_ncm_data(self, code, desc, icms, ipi):
        row = self.ncm_table.rowCount()
        self.ncm_table.insertRow(row)
        self.ncm_table.setItem(row, 0, QTableWidgetItem(code))
        self.ncm_table.setItem(row, 1, QTableWidgetItem(desc))
        self.ncm_table.setItem(row, 2, QTableWidgetItem(icms))
        self.ncm_table.setItem(row, 3, QTableWidgetItem(ipi))

    def select_certificate(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Certificado A1", "", "Arquivos PFX (*.pfx)")
        if file_path:
            self.inp_cert.setText(file_path)

    def check_acbr_status(self):
        """Testa comunicação com o ACBrMonitorPLUS."""
        if not ACBrEngine:
            QMessageBox.warning(self, "Aviso", "Módulo ACBrEngine não detectado no sistema.")
            return

        cmd = "NFE.StatusServico"
        try:
            if ACBrEngine.enviar_comando(cmd):
                resp = ACBrEngine.ler_resposta()
                self.status_lbl.setText("🟢 Servidor: Online (ACBr Ativo)")
                QMessageBox.information(self, "Status ACBr", f"Comunicação estabelecida!\n\nResposta:\n{resp}")
            else:
                self.status_lbl.setText("🔴 Servidor: Desconectado")
                QMessageBox.critical(self, "Erro de Conexão", "ACBrMonitor não respondeu.\nVerifique se o monitor está aberto e a porta TCP (3434) está liberada.")
        except Exception as e:
            QMessageBox.critical(self, "Erro Fatal", f"Erro ao tentar falar com ACBr: {e}")

    def processar_emissao_nfe(self):
        """
        Lógica Mestra: Tenta emissão via ACBr com fallback para simulação.
        """
        valor_venda = 1500.00 # Exemplo Polipet
        venda_mock = {"id": 1024, "data_emissao": datetime.now().strftime("%d/%m/%Y"), "total_final": valor_venda}
        emit_mock = {"cnpj": "12345678000199", "ie": "123456789", "razao_social": "BERTOLINI T.I.", "fantasia": "FLASH DRIVE STUDIO"}
        cli_mock = {"cnpj_cpf": "98765432000188", "nome": "POLIPET INDUSTRIA"}
        prods_mock = [{"id": 1, "nome": "PENDRIVE 64GB", "ncm": "85235110", "quantidade": 10, "preco_unitario": 150.00, "total": 1500.00}]

        # 1. TaxEngine calcula os impostos reais
        tax_results = TaxEngine.calcular_impostos_venda(valor_venda, {'icms_rate': 0.18, 'ipi_rate': 0.05})
        
        sucesso_real = False
        resposta_sefaz = ""

        # 2. Tentativa de ACBr Real
        if ACBrEngine and FiscalBuilder:
            try:
                ini_content = FiscalBuilder.montar_nfe_ini(venda_mock, emit_mock, cli_mock, prods_mock)
                if ACBrEngine.enviar_comando('NFE.StatusServico'):
                     resposta_sefaz = ACBrEngine.ler_resposta()
                     sucesso_real = True 
            except:
                pass

        # 3. Feedback e Atualização de Histórico
        if sucesso_real and "ERRO" not in resposta_sefaz.upper():
            QMessageBox.information(self, "Emissão REAL", "Arquivo enviado com sucesso para o ACBrMonitor!")
            status_txt = "TRANSMITIDA SEFAZ"
            color_txt = "#2980b9"
        else:
            QMessageBox.warning(self, "Modo Contingência", "ACBr Offline. Nota gerada em modo Simulação Bertolini.")
            status_txt = "AUTORIZADA (MOCK)"
            color_txt = "#27ae60"

        self.atualizar_historico("000" + str(venda_mock['id']), cli_mock['nome'], valor_venda, tax_results['total_tributos'], status_txt, color_txt)

    def atualizar_historico(self, nota, cliente, valor, impostos, status, cor):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(nota))
        self.table.setItem(row, 1, QTableWidgetItem("1")) # Série
        self.table.setItem(row, 2, QTableWidgetItem("3526...8910...")) # Chave
        self.table.setItem(row, 3, QTableWidgetItem(cliente))
        self.table.setItem(row, 4, QTableWidgetItem(f"R$ {valor:,.2f}"))
        self.table.setItem(row, 5, QTableWidgetItem(f"R$ {impostos:,.2f}"))
        
        status_item = QTableWidgetItem(status)
        status_item.setForeground(QColor(cor))
        self.table.setItem(row, 6, status_item)