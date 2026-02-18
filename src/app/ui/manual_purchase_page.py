from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate

class ManualPurchasePage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        header = QLabel("Lançamento Manual de Documento / Compra")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        # --- GRUPO 1: CABEÇALHO DO DOCUMENTO ---
        doc_group = QGroupBox("Informações do Documento")
        doc_lay = QHBoxLayout(doc_group)

        self.combo_type = QComboBox()
        self.combo_type.addItems(["NFe (DANFE)", "NFS-e (Serviço)", "NFC-e", "Recibo/Outros"])
        
        self.edit_num = QLineEdit()
        self.edit_num.setPlaceholderText("Nº do Documento")
        
        self.date_emit = QDateEdit(calendarPopup=True)
        self.date_emit.setDate(QDate.currentDate())
        
        self.combo_supplier = QComboBox()
        self.combo_supplier.addItem("Selecione o Fornecedor...") # Aqui viriam os dados do banco
        
        doc_lay.addWidget(QLabel("Tipo:"))
        doc_lay.addWidget(self.combo_type)
        doc_lay.addWidget(QLabel("Nº:"))
        doc_lay.addWidget(self.edit_num)
        doc_lay.addWidget(QLabel("Data:"))
        doc_lay.addWidget(self.date_emit)
        doc_lay.addWidget(QLabel("Fornecedor:"))
        doc_lay.addWidget(self.combo_supplier)
        layout.addWidget(doc_group)

        # --- GRUPO 2: ITENS DA NOTA ---
        items_group = QGroupBox("Itens / Produtos")
        items_lay = QVBoxLayout(items_group)

        # Botão para adicionar linha
        btn_add_item = QPushButton("+ Adicionar Item")
        btn_add_item.setFixedWidth(150)
        btn_add_item.setStyleSheet("background-color: #34495e; color: white; font-weight: bold;")
        btn_add_item.clicked.connect(self.add_item_row)
        items_lay.addWidget(btn_add_item)

        self.table_items = QTableWidget(0, 4)
        self.table_items.setHorizontalHeaderLabels(["Cód/SKU", "Descrição do Produto", "Quantidade", "Vlr. Unitário (Custo)"])
        self.table_items.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        items_lay.addWidget(self.table_items)
        layout.addWidget(items_group)

        # --- BOTÃO SALVAR ---
        self.btn_save = QPushButton("Gravar Entrada e Atualizar Estoque")
        self.btn_save.setMinimumHeight(50)
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 16px;")
        self.btn_save.clicked.connect(self.save_manual_entry)
        layout.addWidget(self.btn_save)

    def add_item_row(self):
        row = self.table_items.rowCount()
        self.table_items.insertRow(row)
        # Colocamos valores vazios para o usuário digitar
        self.table_items.setItem(row, 0, QTableWidgetItem(""))
        self.table_items.setItem(row, 1, QTableWidgetItem(""))
        self.table_items.setItem(row, 2, QTableWidgetItem("1"))
        self.table_items.setItem(row, 3, QTableWidgetItem("0.00"))

    def save_manual_entry(self):
        # Lógica para percorrer a tabela e salvar no banco
        num_nota = self.edit_num.text()
        if not num_nota:
            QMessageBox.warning(self, "Atenção", "Por favor, preencha o número do documento.")
            return
            
        QMessageBox.information(self, "Sucesso", f"Documento {num_nota} lançado com sucesso!\nEstoque atualizado.")