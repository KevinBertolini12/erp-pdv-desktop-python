from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QMessageBox, QAbstractItemView, QHeaderView, QLabel, QFrame
)
from PySide6.QtCore import Qt
from app.clients.api_client import ApiClient
from app.core.auth import current_session
from app.utils.audit_logger import AuditLogger
from app.utils.commission_engine import CommissionEngine

class SalesHistoryPage(QWidget):
    def __init__(self, api_base_url: str, bus=None):
        super().__init__()
        self.client = ApiClient(api_base_url)
        self.bus = bus

        if self.bus:
            # Inscreve para atualizar quando houver mudanças no sistema
            self.bus.subscribe("stock_changed", self.load_sales)
            self.bus.subscribe("sale_finalized", self.load_sales)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 1. CABEÇALHO E PERFORMANCE
        header_lay = QVBoxLayout()
        header_title = QLabel("🛡️ Histórico de Vendas e Auditoria de Performance")
        header_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        header_lay.addWidget(header_title)

        # Painel de Cards de Performance (Visão Gerencial)
        self.perf_layout = QHBoxLayout()
        self.card_top_vendedor = self.create_mini_card("🥇 TOP VENDEDOR", "---", "#f1c40f")
        self.card_ticket_medio = self.create_mini_card("📊 TICKET MÉDIO", "R$ 0,00", "#3498db")
        self.card_total_comissao = self.create_mini_card("💰 COMISSÕES TOTAIS", "R$ 0,00", "#27ae60")
        
        self.perf_layout.addWidget(self.card_top_vendedor)
        self.perf_layout.addWidget(self.card_ticket_medio)
        
        # Só mostra card de comissão para Gerentes
        if current_session.has_permission("gerente"):
            self.perf_layout.addWidget(self.card_total_comissao)
            
        header_lay.addLayout(self.perf_layout)
        self.main_layout.addLayout(header_lay)

        # 2. TABELA DE VENDAS (Expandida para Auditoria)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID Venda", "Data/Hora", "Vendedor", "Total (R$)", "Comissão"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { background-color: white; border-radius: 10px; }")
        self.main_layout.addWidget(self.table)

        # 3. BARRA DE AÇÕES INFERIOR
        actions = QHBoxLayout()
        
        self.btn_cancel = QPushButton("🗑️ Cancelar Venda Selecionada")
        self.btn_cancel.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.btn_cancel.clicked.connect(self.cancel_sale)
        
        # Vendedores não podem cancelar vendas sozinhos
        if not current_session.has_permission("gerente"):
            self.btn_cancel.setEnabled(False)
            self.btn_cancel.setToolTip("Apenas gerentes podem cancelar vendas efetuadas.")

        self.btn_refresh = QPushButton("🔄 Atualizar Lista (F5)")
        self.btn_refresh.setFixedWidth(180)
        self.btn_refresh.setFixedHeight(40)
        self.btn_refresh.clicked.connect(self.load_sales)
        
        actions.addWidget(self.btn_cancel)
        actions.addStretch(1)
        actions.addWidget(self.btn_refresh)
        self.main_layout.addLayout(actions)

        self.load_sales()

    def create_mini_card(self, title, value, color):
        card = QFrame()
        card.setObjectName("PerfCard")
        card.setStyleSheet(f"background: white; border-left: 6px solid {color}; border-radius: 8px; padding: 12px;")
        lay = QVBoxLayout(card)
        t_lbl = QLabel(title); t_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #7f8c8d;")
        v_lbl = QLabel(value); v_lbl.setStyleSheet(f"font-size: 20px; font-weight: 900; color: {color};")
        lay.addWidget(t_lbl); lay.addWidget(v_lbl)
        return card

    def load_sales(self):
        try:
            sales = self.client.list_sales()
            self.table.setRowCount(0)
            
            total_comissoes_acumuladas = 0.0
            
            for s in sales:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                vendedor = s.get("seller_name", "Caixa Principal")
                total_venda = s.get('total', 0.0)
                # Cálculo de comissão via Motor (Simulação de 5%)
                comissao = CommissionEngine.calcular_comissao(total_venda, 5.0)
                total_comissoes_acumuladas += comissao

                self.table.setItem(row, 0, QTableWidgetItem(f"#{s['id']}"))
                self.table.setItem(row, 1, QTableWidgetItem(s.get("created_at", "---")[:19]))
                self.table.setItem(row, 2, QTableWidgetItem(vendedor))
                self.table.setItem(row, 3, QTableWidgetItem(f"{total_venda:.2f}"))
                
                # Sigilo: Vendedor não vê comissão dos outros
                item_com = QTableWidgetItem(f"{comissao:.2f}")
                if not current_session.has_permission("gerente"):
                    item_com.setText("***")
                self.table.setItem(row, 4, item_com)

            # Atualiza os Cards de Performance
            self.update_performance_cards(sales, total_comissoes_acumuladas)

        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")

    def update_performance_cards(self, sales, total_comissoes):
        if not sales: return
        
        ranking = CommissionEngine.gerar_ranking_vendedores(sales)
        if ranking:
            top_v = max(ranking, key=lambda x: ranking[x]["faturamento"])
            self.card_top_vendedor.findChildren(QLabel)[1].setText(top_v.split(" ")[0])
            
            faturamento_total = sum(s.get('total', 0.0) for s in sales)
            # Ticket Médio: Faturamento / Número de Vendas
            ticket_medio = faturamento_total / len(sales)
            self.card_ticket_medio.findChildren(QLabel)[1].setText(f"R$ {ticket_medio:.2f}")
            
            if current_session.has_permission("gerente"):
                self.card_total_comissao.findChildren(QLabel)[1].setText(f"R$ {total_comissoes:.2f}")

    def cancel_sale(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma venda para cancelar.")
            return
        
        sale_id_str = self.table.item(row, 0).text().replace("#", "")
        sale_id = int(sale_id_str)
        
        confirm = QMessageBox.question(
            self, "Confirmar Cancelamento",
            f"Deseja realmente CANCELAR a venda #{sale_id}?\n\nOs produtos voltarão ao estoque e a comissão será estornada.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                self.client.delete_sale(sale_id)
                
                # REGISTRO NA CAIXA-PRETA (Auditoria)
                AuditLogger.log("CANCELAMENTO", f"Venda #{sale_id} cancelada por {current_session.user_name}", level="CRITICAL")
                
                self.load_sales()
                
                if self.bus:
                    self.bus.publish("stock_changed")
                    self.bus.publish("products_changed")
                
                QMessageBox.information(self, "Sucesso", f"Venda #{sale_id} cancelada com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao cancelar: {e}")