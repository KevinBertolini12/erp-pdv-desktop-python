from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
import os
import uuid
from datetime import datetime
from app.core.auth import current_session
from app.utils.audit_logger import AuditLogger

# Motores de Inteligência
from app.utils.pdf_generator import gerar_pdf_os 
from app.utils.finance_engine import FinanceEngine
from app.utils.quality_engine import QualityEngine # Novo: Motor de Laboratório

class OrdersPage(QWidget):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Cabeçalho
        header = QFrame()
        header.setStyleSheet("background-color: #2c3e50; border-radius: 5px;")
        header.setFixedHeight(60)
        h_layout = QHBoxLayout(header)
        
        lbl = QLabel("📋 GESTÃO DE ORÇAMENTOS & PEDIDOS (B2B)")
        lbl.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        h_layout.addWidget(lbl)
        h_layout.addStretch()
        
        btn_new = QPushButton("➕ Novo Orçamento")
        btn_new.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; font-weight: bold;")
        btn_new.clicked.connect(self.new_order)
        h_layout.addWidget(btn_new)
        
        layout.addWidget(header)

        # Tabela de Pedidos (7 colunas)
        self.table = QTableWidget()
        self.table.setColumnCount(7) 
        self.table.setHorizontalHeaderLabels(["Número", "Cliente", "Data", "Valor Total", "Status", "Documento", "Financeiro"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.add_mock_data()

    def add_mock_data(self):
        rows = [
            ("ORD-8821", "Usina Bela Vista S/A", "13/02/2026", "R$ 12.500,00", "Pendente"),
            ("ORD-9042", "Transportadora Silva", "12/02/2026", "R$ 3.200,00", "Aprovado"),
        ]
        self.table.setRowCount(len(rows))
        for r, data in enumerate(rows):
            for c, val in enumerate(data):
                self.table.setItem(r, c, QTableWidgetItem(val))
            
            # COLUNA 5: Botão de PDF
            btn_pdf = QPushButton("📥 PDF")
            btn_pdf.clicked.connect(lambda _, row=r: self.generate_quote_pdf(row))
            self.table.setCellWidget(r, 5, btn_pdf)

            # COLUNA 6: Botão de Faturamento com Trava de Segurança
            btn_invoice = QPushButton("🚀 FATURAR")
            
            if current_session.has_permission("gerente"):
                btn_invoice.setEnabled(True)
                btn_invoice.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
                btn_invoice.setToolTip("Clique para processar o faturamento B2B.")
            else:
                btn_invoice.setEnabled(False)
                btn_invoice.setToolTip("Apenas gerentes ou admins podem faturar pedidos.")
                btn_invoice.setStyleSheet("background-color: #bdc3c7; color: #7f8c8d;")

            btn_invoice.clicked.connect(lambda _, row=r: self.faturar_pedido(row))
            self.table.setCellWidget(r, 6, btn_invoice)

    def faturar_pedido(self, row_index):
        """Transforma orçamento em faturamento com Trava de Qualidade"""
        try:
            cliente = self.table.item(row_index, 1).text()
            valor_texto = self.table.item(row_index, 3).text()
            valor_total = float(valor_texto.replace("R$ ","").replace(".","").replace(",","."))

            # 1. RASTREABILIDADE: Exige o número do lote
            lote, ok_lote = QInputDialog.getText(self, "Controle de Qualidade", 
                                               f"Informe o LOTE para o faturamento de {cliente}:")
            
            if not ok_lote or not lote:
                QMessageBox.warning(self, "Erro", "O número do lote é obrigatório para faturamento industrial.")
                return

            # 2. QUALITY GATE: Verifica se o laboratório aprovou
            if not QualityEngine.is_lote_aprovado(lote):
                QMessageBox.critical(self, "BLOQUEIO FISCAL", 
                                   f"❌ O lote <b>{lote}</b> não foi aprovado pelo Laboratório!<br><br>"
                                   "O faturamento foi bloqueado por questões de segurança e qualidade.")
                
                # Registra tentativa irregular na auditoria (Big Brother)
                AuditLogger.log("BLOQUEIO_QUALIDADE", 
                                f"Tentativa de faturar lote reprovado/pendente: {lote} para {cliente}", 
                                level="CRITICAL")
                return

            # 3. FINANCEIRO: Se aprovado, define prazos
            prazos = ["À Vista", "30 dias", "30/60 dias", "30/60/90 dias"]
            prazo, ok = QInputDialog.getItem(self, "Faturamento B2B", f"Lote {lote} Aprovado! Selecione o prazo:", prazos, 0, False)

            if ok and prazo:
                num_parcelas = 1 if "Vista" in prazo else len(prazo.split('/'))
                parcelas = FinanceEngine.gerar_parcelas(valor_total, num_parcelas)

                resumo = f"<b>Confirmar faturamento para {cliente}?</b><br>Lote: {lote}<br><br>"
                for p in parcelas:
                    resumo += f"📅 {p['vencimento']} - R$ {p['valor']:.2f}<br>"
                
                if QMessageBox.question(self, "Financeiro", resumo) == QMessageBox.Yes:
                    self.processar_faturamento_final(cliente, valor_total, parcelas)
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha no processo: {e}")

    def processar_faturamento_final(self, cliente, total, parcelas):
        QMessageBox.information(self, "OK", f"Faturamento de R$ {total:.2f} concluído!")
        if self.bus: self.bus.publish("sale_finalized")
        AuditLogger.log("FATURAMENTO", f"Pedido faturado para {cliente} no valor de R$ {total:.2f}", level="CRITICAL")

    def generate_quote_pdf(self, row_index):
        try:
            cliente_nome = self.table.item(row_index, 1).text()
            valor_total = self.table.item(row_index, 3).text()
            empresa = {"razao_social": "BERTOLINI ERP", "cnpj": "00.000.000/0001-00", "telefone": "(16) 9999-9999"}
            itens = [{"nome": "Item B2B", "qtd": 1, "preco": float(valor_total.replace("R$ ","").replace(".","").replace(",","."))}]
            path = gerar_pdf_os(empresa, {"nome": cliente_nome}, itens)
            if path: os.startfile(os.path.abspath(path))
        except Exception as e: QMessageBox.critical(self, "Erro PDF", str(e))

    def new_order(self): QMessageBox.information(self, "Novo", "Compondo itens...")