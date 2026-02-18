from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, 
    QHeaderView, QFrame, QGroupBox
)
from PySide6.QtCore import Qt
import xml.etree.ElementTree as ET # Biblioteca para ler o XML da nota

class PurchasesPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.xml_data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Cabeçalho
        header = QLabel("Entrada de Mercadoria (Importar XML)")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        # --- ÁREA DE SELEÇÃO ---
        self.btn_open_xml = QPushButton("Selecionar Arquivo XML da Nota Fiscal")
        self.btn_open_xml.setMinimumHeight(50)
        self.btn_open_xml.setStyleSheet("""
            QPushButton { background-color: #8e44ad; color: white; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background-color: #9b59b6; }
        """)
        self.btn_open_xml.clicked.connect(self.load_xml_file)
        layout.addWidget(self.btn_open_xml)

        # --- DADOS DO FORNECEDOR ---
        self.group_supplier = QGroupBox("Dados do Fornecedor")
        self.group_supplier.hide()
        sup_lay = QVBoxLayout(self.group_supplier)
        self.lbl_sup_info = QLabel("")
        sup_lay.addWidget(self.lbl_sup_info)
        layout.addWidget(self.group_supplier)

        # --- TABELA DE ITENS DA NOTA ---
        self.lbl_items = QLabel("Itens identificados na nota:")
        self.lbl_items.hide()
        layout.addWidget(self.lbl_items)

        self.table_items = QTableWidget()
        self.table_items.setColumnCount(4)
        self.table_items.setHorizontalHeaderLabels(["Código/SKU", "Produto", "Qtd", "Preço Custo"])
        self.table_items.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_items.hide()
        layout.addWidget(self.table_items)

        # --- BOTÃO FINALIZAR ---
        self.btn_finalize = QPushButton("Confirmar Entrada e Gerar Contas a Pagar")
        self.btn_finalize.setEnabled(False)
        self.btn_finalize.setMinimumHeight(50)
        self.btn_finalize.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; border-radius: 8px;")
        self.btn_finalize.clicked.connect(self.finalize_import)
        layout.addWidget(self.btn_finalize)

    def load_xml_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir XML da NFe", "", "XML Files (*.xml)")
        if not file_path: return

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # O XML da NFe usa "namespaces", precisamos lidar com isso
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

            # 1. Extrair Fornecedor (emit)
            emit = root.find('.//nfe:emit', ns)
            nome_fantasia = emit.find('nfe:xFant', ns).text if emit.find('nfe:xFant', ns) is not None else emit.find('nfe:xNome', ns).text
            cnpj = emit.find('nfe:CNPJ', ns).text
            self.lbl_sup_info.setText(f"Fornecedor: {nome_fantasia}\nCNPJ: {cnpj}")
            self.group_supplier.show()

            # 2. Extrair Itens (det)
            self.table_items.setRowCount(0)
            items = root.findall('.//nfe:det', ns)
            for det in items:
                prod = det.find('nfe:prod', ns)
                sku = prod.find('nfe:cProd', ns).text
                nome = prod.find('nfe:xProd', ns).text
                qtd = prod.find('nfe:qCom', ns).text
                v_unit = prod.find('nfe:vUnCom', ns).text

                row = self.table_items.rowCount()
                self.table_items.insertRow(row)
                self.table_items.setItem(row, 0, QTableWidgetItem(sku))
                self.table_items.setItem(row, 1, QTableWidgetItem(nome))
                self.table_items.setItem(row, 2, QTableWidgetItem(str(float(qtd))))
                self.table_items.setItem(row, 3, QTableWidgetItem(f"R$ {float(v_unit):.2f}"))

            self.table_items.show()
            self.lbl_items.show()
            self.btn_finalize.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro no XML", f"Falha ao processar nota fiscal: {str(e)}")

    def finalize_import(self):
        # Aqui o sistema salvaria no banco de dados e geraria o financeiro
        QMessageBox.information(self, "Sucesso", "Estoque atualizado e fatura enviada para o Contas a Pagar!")
        self.group_supplier.hide()
        self.table_items.hide()
        self.btn_finalize.setEnabled(False)