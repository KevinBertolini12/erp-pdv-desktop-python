from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QSpinBox,
    QAbstractItemView,
    QHeaderView,
)

from app.clients.api_client import ApiClient


class PosPage(QWidget):
    """
    PDV/CAIXA (Opção B):
    - Busca por nome/SKU
    - Enter no campo busca adiciona o item selecionado (ou o primeiro da lista)
    - Duplo clique na lista adiciona
    - Carrinho com edição de quantidade (duplo clique), remover por botão X, total de itens
    - Finaliza venda e emite evento de estoque
    - Recarrega lista quando evento de produtos/estoque mudar
    """

    def __init__(self, api_base_url: str, bus=None):
        super().__init__()
        self.client = ApiClient(api_base_url)
        self.bus = bus

        # dados em memória
        self.all_products: list[dict] = []
        self.filtered_products: list[dict] = []
        self.cart: list[dict] = []  # {product_id, name, qty}

        # eventos (atualização)
        if self.bus:
            self.bus.products_changed.connect(self.reload_products)
            self.bus.stock_changed.connect(self.reload_products)

        root = QHBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(12)

        # =========================
        # LEFT: produtos + busca
        # =========================
        left = QVBoxLayout()
        left.setSpacing(8)

        left.addWidget(QLabel("Buscar produto:"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Digite nome ou SKU... (Enter = adicionar)")
        self.search.textChanged.connect(self.apply_filter)
        self.search.returnPressed.connect(self.add_best_match_to_cart)  # ENTER = adicionar
        left.addWidget(self.search)

        row_qty = QHBoxLayout()
        row_qty.setSpacing(8)
        row_qty.addWidget(QLabel("Qtd ao adicionar:"))
        self.sp_qty = QSpinBox()
        self.sp_qty.setRange(1, 9999)
        self.sp_qty.setValue(1)
        row_qty.addWidget(self.sp_qty)
        row_qty.addStretch(1)
        left.addLayout(row_qty)

        self.tbl_products = QTableWidget(0, 4)
        self.tbl_products.setHorizontalHeaderLabels(["ID", "Nome", "SKU", "Estoque"])
        self.tbl_products.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_products.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_products.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_products.setAlternatingRowColors(True)
        self.tbl_products.setSortingEnabled(False)
        self.tbl_products.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Nome estica
        self.tbl_products.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tbl_products.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tbl_products.verticalHeader().setVisible(False)
        self.tbl_products.cellDoubleClicked.connect(self.add_selected_to_cart)
        left.addWidget(self.tbl_products, 1)

        btn_add = QPushButton("Adicionar ao carrinho (Enter)")
        btn_add.clicked.connect(self.add_selected_to_cart)
        left.addWidget(btn_add)

        # =========================
        # RIGHT: carrinho
        # =========================
        right = QVBoxLayout()
        right.setSpacing(8)

        right.addWidget(QLabel("Carrinho:"))

        self.tbl_cart = QTableWidget(0, 3)
        self.tbl_cart.setHorizontalHeaderLabels(["Produto", "Qtd", "Remover"])
        self.tbl_cart.setEditTriggers(QAbstractItemView.DoubleClicked)  # Qtd editável
        self.tbl_cart.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_cart.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_cart.setAlternatingRowColors(True)
        self.tbl_cart.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tbl_cart.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbl_cart.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tbl_cart.verticalHeader().setVisible(False)
        right.addWidget(self.tbl_cart, 1)

        # conecta AGORA (depois de criar tbl_cart)
        self.tbl_cart.itemChanged.connect(self.on_cart_qty_changed)

        # total
        self.lbl_total = QLabel("Total itens: 0")
        self.lbl_total.setAlignment(Qt.AlignRight)
        right.addWidget(self.lbl_total)

        # ações
        row_actions = QHBoxLayout()
        btn_remove = QPushButton("Remover selecionado")
        btn_remove.clicked.connect(self.remove_selected_from_cart)
        btn_clear = QPushButton("Limpar carrinho")
        btn_clear.clicked.connect(self.clear_cart)
        row_actions.addWidget(btn_remove)
        row_actions.addWidget(btn_clear)
        right.addLayout(row_actions)

        btn_finalize = QPushButton("Finalizar venda")
        btn_finalize.clicked.connect(self.finalize_sale)
        right.addWidget(btn_finalize)

        root.addLayout(left, 2)
        root.addLayout(right, 1)

        # carga inicial
        self.reload_products()
        self.render_cart()
        self.search.setFocus()

    # =========================
    # Produtos
    # =========================
    def reload_products(self):
        """Recarrega produtos da API e reaplica filtro atual."""
        try:
            self.all_products = self.client.list_products()
            self.apply_filter()
        except Exception:
            # não estoura UI se API estiver inicializando / sem conexão
            return

    def apply_filter(self):
        q = (self.search.text() or "").strip().lower()

        if not q:
            self.filtered_products = list(self.all_products)
        else:
            out: list[dict] = []
            for p in self.all_products:
                name = (p.get("name") or "").lower()
                sku = (p.get("sku") or "").lower()
                if q in name or (sku and q in sku):
                    out.append(p)
            self.filtered_products = out

        self.tbl_products.setRowCount(0)
        for p in self.filtered_products:
            row = self.tbl_products.rowCount()
            self.tbl_products.insertRow(row)
            self.tbl_products.setItem(row, 0, QTableWidgetItem(str(p["id"])))
            self.tbl_products.setItem(row, 1, QTableWidgetItem(p.get("name") or ""))
            self.tbl_products.setItem(row, 2, QTableWidgetItem(p.get("sku") or ""))
            self.tbl_products.setItem(row, 3, QTableWidgetItem(str(p.get("stock_qty", 0))))

        self.tbl_products.resizeColumnsToContents()

        # seleciona a primeira linha automaticamente (boa UX pro Enter)
        if self.tbl_products.rowCount() > 0 and self.tbl_products.currentRow() < 0:
            self.tbl_products.selectRow(0)

    def _selected_product(self) -> dict | None:
        row = self.tbl_products.currentRow()
        if row < 0:
            return None
        pid = int(self.tbl_products.item(row, 0).text())
        name = self.tbl_products.item(row, 1).text()
        stock_txt = self.tbl_products.item(row, 3).text()
        try:
            stock_qty = int(stock_txt)
        except Exception:
            stock_qty = 0
        return {"product_id": pid, "name": name, "stock_qty": stock_qty}

    # =========================
    # Carrinho
    # =========================
    def add_best_match_to_cart(self):
        """
        ENTER no campo de busca:
        - se tiver seleção na tabela, usa ela
        - senão, usa o primeiro item filtrado
        """
        sel = self._selected_product()
        if not sel and self.tbl_products.rowCount() > 0:
            self.tbl_products.selectRow(0)
            sel = self._selected_product()
        if not sel:
            return

        self._add_to_cart(sel["product_id"], sel["name"], int(self.sp_qty.value()))

        # pós-ação: deixa pronto pra próxima
        self.search.selectAll()
        self.search.setFocus()

    def add_selected_to_cart(self):
        sel = self._selected_product()
        if not sel:
            QMessageBox.information(self, "Caixa", "Selecione um produto na lista (ou use a busca e Enter).")
            return
        self._add_to_cart(sel["product_id"], sel["name"], int(self.sp_qty.value()))
        self.search.selectAll()
        self.search.setFocus()

    def _add_to_cart(self, product_id: int, name: str, qty: int):
        if qty <= 0:
            return

        # soma se já existir no carrinho
        for it in self.cart:
            if it["product_id"] == product_id:
                it["qty"] += qty
                self.render_cart()
                return

        self.cart.append({"product_id": product_id, "name": name, "qty": qty})
        self.render_cart()

    def render_cart(self):
        # evita loop do itemChanged enquanto recria a tabela
        self.tbl_cart.blockSignals(True)
        try:
            self.tbl_cart.setRowCount(0)

            for it in self.cart:
                row = self.tbl_cart.rowCount()
                self.tbl_cart.insertRow(row)
                self.tbl_cart.setItem(row, 0, QTableWidgetItem(it["name"]))

                qty_item = QTableWidgetItem(str(it["qty"]))
                qty_item.setTextAlignment(Qt.AlignCenter)
                self.tbl_cart.setItem(row, 1, qty_item)

                btn = QPushButton("X")
                btn.setProperty("row", row)
                btn.clicked.connect(self._remove_row_button_clicked)
                self.tbl_cart.setCellWidget(row, 2, btn)

            self.tbl_cart.resizeColumnsToContents()
            self.lbl_total.setText(f"Total itens: {sum(int(it['qty']) for it in self.cart)}")
        finally:
            self.tbl_cart.blockSignals(False)

    def _remove_row_button_clicked(self):
        btn = self.sender()
        if not btn:
            return
        row = btn.property("row")
        if row is None:
            return
        try:
            row = int(row)
        except Exception:
            return
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self.render_cart()

    def remove_selected_from_cart(self):
        row = self.tbl_cart.currentRow()
        if row < 0:
            return
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self.render_cart()

    def clear_cart(self):
        self.cart.clear()
        self.render_cart()

    # =========================
    # Venda
    # =========================
    def finalize_sale(self):
        if not self.cart:
            QMessageBox.information(self, "Caixa", "Carrinho vazio.")
            return

        try:
            items = [{"product_id": it["product_id"], "qty": int(it["qty"])} for it in self.cart]
            res = self.client.create_sale(items=items)

            self.cart.clear()
            self.render_cart()
            self.reload_products()

            if self.bus:
                # estoque mudou e relatórios/dashboard dependem disso
                self.bus.stock_changed.emit()

            QMessageBox.information(self, "Venda finalizada", f"Venda #{res['id']} registrada com sucesso!")
            self.search.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao finalizar venda", str(e))

    def on_cart_qty_changed(self, item: QTableWidgetItem):
        if item.column() != 1:
            return

        row = item.row()
        try:
            new_qty = int(item.text())
        except ValueError:
            new_qty = 1

        if new_qty <= 0:
            new_qty = 1

        if 0 <= row < len(self.cart):
            self.cart[row]["qty"] = new_qty
            self.render_cart()
