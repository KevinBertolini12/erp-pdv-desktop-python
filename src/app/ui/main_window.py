from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
)

from app.clients.api_client import ApiClient
from app.ui.dashboard_page import DashboardPage
from app.ui.products_window import ProductsWindow
from app.ui.reports_page import ReportsPage
from app.ui.pos_page import PosPage
from app.ui.event_bus import EventBus
from app.ui.suppliers_window import SuppliersWindow



class MainWindow(QMainWindow):
    def __init__(self, api_base_url: str):
        super().__init__()
        self.setWindowTitle("ERP/PDV")
        self.resize(1000, 650)

        self.bus = EventBus()
        self.client = ApiClient(api_base_url)

        # ROOT
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # TOP MENU
        topbar = QWidget()
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(0, 0, 0, 0)
        topbar_layout.setSpacing(8)

        btn_home = QPushButton("Início")
        btn_products = QPushButton("Produtos")
        btn_reports = QPushButton("Relatórios")
        btn_pos = QPushButton("Caixa")
        btn_suppliers = QPushButton("Fornecedores")
        self.status = QLabel("Status: (não testado)")

        topbar_layout.addWidget(btn_home)
        topbar_layout.addWidget(btn_products)
        topbar_layout.addWidget(btn_suppliers)
        topbar_layout.addWidget(btn_reports)
        topbar_layout.addWidget(btn_pos)
        topbar_layout.addStretch(1)
        topbar_layout.addWidget(self.status)

        # PAGES
        self.pages = QStackedWidget()

        home_page = DashboardPage(self.client.base_url, bus=self.bus)
        self.products_page = ProductsWindow(self.client.base_url, bus=self.bus)
        self.reports_page = ReportsPage(self.client.base_url, bus=self.bus)
        self.pos_page = PosPage(self.client.base_url, bus=self.bus)
        self.suppliers_page = SuppliersWindow(self.client.base_url, bus=self.bus)

        self.pages.addWidget(home_page)            # 0
        self.pages.addWidget(self.products_page)   # 1
        self.pages.addWidget(self.reports_page)    # 2
        self.pages.addWidget(self.pos_page)        # 3
        self.pages.addWidget(self.suppliers_page)  # 4

        # Actions
        btn_home.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        btn_reports.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        btn_pos.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        btn_suppliers.clicked.connect(lambda: self.pages.setCurrentIndex(4))

        def go_products():
            self.pages.setCurrentIndex(1)
            if hasattr(self.products_page, "load_products"):
                self.products_page.load_products()

        btn_products.clicked.connect(go_products)

        root_layout.addWidget(topbar)
        root_layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)

