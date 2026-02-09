from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    # Produto criado/editado/excluído
    products_changed = Signal()
    # Movimento de estoque (ajuste/venda) que impacta dashboard/relatórios/caixa
    stock_changed = Signal()
