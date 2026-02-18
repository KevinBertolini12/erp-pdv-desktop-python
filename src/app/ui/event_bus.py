from PySide6.QtCore import QObject, Signal

class EventBus(QObject):
    # --- SINAIS NATIVOS PYSIDE6 (Necessários para .connect) ---
    products_changed = Signal()
    stock_changed = Signal()      
    cart_updated = Signal()
    sale_completed = Signal(dict)
    stock_updated = Signal(int)
    order_selected = Signal(int)
    sync_status_changed = Signal(str)

    def __init__(self):
        super().__init__()
        # Mantendo sua lógica original de dicionário para o .subscribe
        self._subscribers = {}

    def subscribe(self, event_name: str, callback):
        """Inscreve uma função para ouvir um evento via string."""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def emit(self, event_name: str, *args, **kwargs):
        """Dispara o aviso para todos os ouvintes (Sinais e Subscriptions)."""
        # 1. Dispara como Sinal Nativo (se existir)
        if hasattr(self, event_name):
            attr = getattr(self, event_name)
            if hasattr(attr, 'emit'):
                # Sinais do PySide6 não aceitam kwargs, apenas args posicionais
                attr.emit(*args)

        # 2. Mantém sua lógica original de inscritos manuais
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                callback(*args, **kwargs)