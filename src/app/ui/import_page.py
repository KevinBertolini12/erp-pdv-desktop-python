from __future__ import annotations
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, 
    QHeaderView, QFrame, QFormLayout, QComboBox, QScrollArea,
    QGroupBox
)
from PySide6.QtCore import Qt
from app.clients.api_client import ApiClient

class ImportPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.client = ApiClient("http://127.0.0.1:8000")
        self.df = None 
        self.temp_xml_data = [] # Armazena dados do XML
        self.mapping_combos = {} 
        self.mode = "SPREADSHEET" # SPREADSHEET ou XML
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Cabeçalho
        header_frame = QFrame()
        header_lay = QVBoxLayout(header_frame)
        header_title = QLabel("BERTOLINI IMPORT CENTER")
        header_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_sub = QLabel("Migração de Dados (Excel/CSV) ou Entrada via NFe (XML)")
        header_lay.addWidget(header_title)
        header_lay.addWidget(header_sub)
        layout.addWidget(header_frame)

        # 1. ÁREA DE SELEÇÃO (DOIS BOTÕES)
        btn_layout = QHBoxLayout()
        
        self.btn_select_sheet = QPushButton("📁 Selecionar Planilha (MIGRAÇÃO)")
        self.btn_select_sheet.setMinimumHeight(50)
        self.btn_select_sheet.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 8px;")
        self.btn_select_sheet.clicked.connect(self.open_file_dialog)

        self.btn_select_xml = QPushButton("🧾 Importar XML de Compra (NFe)")
        self.btn_select_xml.setMinimumHeight(50)
        self.btn_select_xml.setStyleSheet("background-color: #9b59b6; color: white; font-weight: bold; border-radius: 8px;")
        self.btn_select_xml.clicked.connect(self.open_xml_dialog)

        btn_layout.addWidget(self.btn_select_sheet)
        btn_layout.addWidget(self.btn_select_xml)
        layout.addLayout(btn_layout)

        # 2. ÁREA DINÂMICA: MAPEAMENTO (EXCEL)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.hide()
        self.mapping_container = QGroupBox("Tradutor de Colunas (Planilha Antiga -> Bertolini ERP)")
        self.mapping_layout = QFormLayout(self.mapping_container)
        self.scroll.setWidget(self.mapping_container)
        layout.addWidget(self.scroll)

        # 3. ÁREA DINÂMICA: TABELA DE REVISÃO (XML)
        self.xml_preview_table = QTableWidget(0, 5)
        self.xml_preview_table.setHorizontalHeaderLabels(["SKU", "Produto", "Qtd", "Custo Unit.", "NCM"])
        self.xml_preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.xml_preview_table.hide()
        layout.addWidget(self.xml_preview_table)

        # 4. BOTÃO DE CONFIRMAÇÃO FINAL
        self.btn_run = QPushButton("🚀 INICIAR PROCESSAMENTO")
        self.btn_run.setEnabled(False)
        self.btn_run.setMinimumHeight(60)
        self.btn_run.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; font-size: 16px; border-radius: 8px; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.btn_run.clicked.connect(self.process_import)
        layout.addWidget(self.btn_run)

    # --- LÓGICA DE EXCEL / CSV (ORIGINAL MANTIDA) ---
    def open_file_dialog(self):
        try: import pandas as pd
        except: 
            QMessageBox.critical(self, "Erro", "Rode: pip install pandas openpyxl")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Planilha", "", "Dados (*.xlsx *.csv *.xls)")
        if file_path:
            try:
                self.mode = "SPREADSHEET"
                self.xml_preview_table.hide()
                self.df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
                self.setup_mapping_ui()
                self.scroll.show()
                self.btn_run.setEnabled(True)
            except Exception as e: QMessageBox.critical(self, "Erro", str(e))

    def setup_mapping_ui(self):
        for i in reversed(range(self.mapping_layout.count())): 
            w = self.mapping_layout.itemAt(i).widget()
            if w: w.setParent(None)
        
        cols = ["(Não Importar)"] + list(self.df.columns)
        self.fields_to_map = {
            "name": "Nome do Produto*", "price": "Preço de Venda (R$)*",
            "cost_price": "Preço de Custo (R$)", "sku": "Código / SKU",
            "stock_qty": "Estoque Inicial", "ncm_code": "NCM (Fiscal)"
        }

        for key, label in self.fields_to_map.items():
            combo = QComboBox()
            combo.addItems(cols)
            # Auto-map simples
            index = combo.findText(label.split(" ")[0], Qt.MatchContains)
            if index >= 0: combo.setCurrentIndex(index)
            self.mapping_layout.addRow(f"{label}:", combo)
            self.mapping_combos[key] = combo

    # --- LÓGICA DE XML (NOVA) ---
    def open_xml_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar XML da NFe", "", "XML Files (*.xml)")
        if file_path:
            try:
                self.mode = "XML"
                self.scroll.hide()
                self.temp_xml_data = []
                
                tree = ET.parse(file_path)
                root = tree.getroot()
                ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
                
                self.xml_preview_table.setRowCount(0)
                for det in root.findall('.//nfe:det', ns):
                    prod = det.find('nfe:prod', ns)
                    item = {
                        "name": prod.find('nfe:xProd', ns).text,
                        "sku": prod.find('nfe:cProd', ns).text,
                        "ncm_code": prod.find('nfe:NCM', ns).text,
                        "stock_qty": int(float(prod.find('nfe:qCom', ns).text)),
                        "cost_price": float(prod.find('nfe:vUnCom', ns).text),
                        "price": float(prod.find('nfe:vUnCom', ns).text) * 1.5, # 50% margem padrão
                        "type": "PRODUTO"
                    }
                    self.temp_xml_data.append(item)
                    
                    row = self.xml_preview_table.rowCount()
                    self.xml_preview_table.insertRow(row)
                    self.xml_preview_table.setItem(row, 0, QTableWidgetItem(item['sku']))
                    self.xml_preview_table.setItem(row, 1, QTableWidgetItem(item['name']))
                    self.xml_preview_table.setItem(row, 2, QTableWidgetItem(str(item['stock_qty'])))
                    self.xml_preview_table.setItem(row, 3, QTableWidgetItem(f"R$ {item['cost_price']:.2f}"))
                    self.xml_preview_table.setItem(row, 4, QTableWidgetItem(item['ncm_code']))

                self.xml_preview_table.show()
                self.btn_run.setEnabled(True)
                QMessageBox.information(self, "Sucesso", f"{len(self.temp_xml_data)} produtos lidos do XML.")
            except Exception as e: QMessageBox.critical(self, "Erro XML", f"Arquivo inválido: {e}")

    # --- PROCESSAMENTO FINAL ---
    def process_import(self):
        mapped_data = []
        try:
            if self.mode == "SPREADSHEET":
                for _, row in self.df.iterrows():
                    item = {}
                    for key, combo in self.mapping_combos.items():
                        col = combo.currentText()
                        if col != "(Não Importar)":
                            val = row[col]
                            if key in ["price", "cost_price"]: val = float(str(val).replace(',','.')) if val else 0.0
                            elif key == "stock_qty": val = int(float(val)) if val else 0
                            item[key] = val
                    if item.get("name"): mapped_data.append(item)
            else:
                mapped_data = self.temp_xml_data

            # ENVIO PARA API
            if mapped_data:
                for data in mapped_data:
                    self.client.create_product(
                        name=data['name'], sku=data.get('sku'),
                        price=data.get('price', 0.0), cost_price=data.get('cost_price', 0.0),
                        min_stock=5, type=data.get('type', 'PRODUTO'), 
                        ncm_code=data.get('ncm_code', '00000000')
                    )
                
                QMessageBox.information(self, "Concluído", f"Sucesso! {len(mapped_data)} itens processados no Bertolini ERP.")
                if self.bus: self.bus.publish("products_changed")
                self.btn_run.setEnabled(False)
                self.xml_preview_table.hide()
                self.scroll.hide()

        except Exception as e: QMessageBox.critical(self, "Erro", f"Falha no processamento: {e}")