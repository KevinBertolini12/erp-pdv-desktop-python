from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter

from app.clients.api_client import ApiClient


def _card(title: str, value: str) -> QFrame:
    box = QFrame()
    box.setObjectName("Card")
    lay = QVBoxLayout(box)

    t = QLabel(title)
    t.setObjectName("CardTitle")

    v = QLabel(value)
    v.setObjectName("CardValue")

    lay.addWidget(t)
    lay.addWidget(v)
    return box


class DashboardPage(QWidget):
    def __init__(self, api_base_url: str, bus=None):
        super().__init__()
        self.bus = bus
        self.client = ApiClient(api_base_url)

        if self.bus is not None:
            self.bus.products_changed.connect(self.refresh)
            self.bus.stock_changed.connect(self.refresh)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        cards_row = QHBoxLayout()
        self.card_products = _card("Produtos", "—")
        self.card_stock = _card("Estoque total", "—")
        self.card_low = _card("Estoque baixo (<=5)", "—")
        cards_row.addWidget(self.card_products)
        cards_row.addWidget(self.card_stock)
        cards_row.addWidget(self.card_low)

        self.chart = QChart()
        self.chart.setTitle("Movimentação líquida de estoque (últimos 7 dias)")

        self.series = QLineSeries()
        self.chart.addSeries(self.series)

        self.axis_x = QValueAxis()
        self.axis_x.setTickCount(7)
        self.axis_x.setLabelFormat("%d")
        self.axis_x.setTitleText("Dia (0=6 dias atrás, 6=hoje)")

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Delta líquido (entrada - saída)")

        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        btn_refresh = QPushButton("Atualizar dashboard")
        btn_refresh.clicked.connect(self.refresh)

        layout.addLayout(cards_row)
        layout.addWidget(self.chart_view, 1)
        layout.addWidget(btn_refresh)

        self.refresh()

    def refresh(self):
        s = self.client.reports_summary()
        self.card_products.findChild(QLabel, "CardValue").setText(str(s["total_products"]))
        self.card_stock.findChild(QLabel, "CardValue").setText(str(s["total_stock"]))
        self.card_low.findChild(QLabel, "CardValue").setText(str(s["low_stock"]))

        data = self.client.reports_stock_moves_7d()["series"]
        self.series.clear()

        vals = []
        for i, pt in enumerate(data):
            net = int(pt["net"])
            vals.append(net)
            self.series.append(i, net)

        if vals:
            mn, mx = min(vals), max(vals)
        else:
            mn, mx = 0, 1

        if mn == mx:
            mn -= 1
            mx += 1

        self.axis_y.setRange(mn, mx)
        self.axis_x.setRange(0, 6)
