from __future__ import annotations
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import QSize, Qt, Signal, QSettings, QTimer
from PySide6.QtGui import QIcon, QPixmap, QAction, QColor, QKeySequence
# ADICIONADO QSizePolicy NAS IMPORTAÇÕES
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QToolBar, QApplication, QMessageBox, 
    QFrame, QLineEdit, QPushButton, QLabel, QGridLayout, QCheckBox, QGraphicsDropShadowEffect, QSizePolicy
)

# --- IMPORTANDO AS PÁGINAS EXTERNAS ---
from app.ui.master_page import MasterDashboardPage
from app.ui.orders_page import OrdersPage
from app.ui.dashboard_page import DashboardPage
from app.ui.products_window import ProductsWindow
from app.ui.pos_page import PosPage
from app.ui.settings_page import SettingsPage
from app.ui.sales_history_page import SalesHistoryPage
from app.ui.admin_page import AdminPage 
from app.ui.lock_screen import LockScreen 
from app.ui.import_page import ImportPage
from app.ui.purchases_page import PurchasesPage
from app.ui.os_page import OSPage
from app.ui.finance_page import FinancePage
from app.ui.suppliers_window import SuppliersWindow
from app.ui.manual_purchase_page import ManualPurchasePage
from app.ui.inventory_page import InventoryPage
from app.ui.fiscal_page import FiscalPage 
from app.ui.event_bus import EventBus
from app.clients.api_client import ApiClient

# >>> IMPORTAÇÕES DE MÓDULOS DE ELITE <<<
from app.ui.customers_window import CustomersWindow 
from app.ui.fleet_page import FleetPage
from app.ui.hr_page import HRPage 
from app.ui.crm_page import CRMPage 
from app.ui.quality_page import QualityPage 
from app.ui.production_page import ProductionPage 
from app.ui.monitoring_page import MonitoringPage # >>> NOVO MÓDULO NUVEM <<<

def get_logo_path():
    """Retorna o caminho da logo DO CLIENTE (se existir) ou Padrão. Usado no Portal."""
    # Tenta subir um nível para achar a pasta assets na raiz do src ou app
    base = Path(__file__).resolve().parent.parent / "assets"
    if not base.exists():
        base = Path(__file__).resolve().parent / "assets"
        
    custom = base / "custom_logo.png"
    default = base / "logo.png"
    
    # Debug para ajudar a encontrar a logo
    print(f"🔍 Procurando logo em: {base}")
    
    return str(custom) if custom.exists() else str(default)

def get_original_logo():
    """Retorna SEMPRE a logo da BERTOLINI (Padrão). Usado no Login."""
    base = Path(__file__).resolve().parent.parent / "assets"
    if not base.exists():
        base = Path(__file__).resolve().parent / "assets"
    return str(base / "logo.png")

def get_icon(name: str) -> QIcon:
    """Busca ícones. O ícone da janela usa a logo do cliente para personalização na barra de tarefas."""
    if name == "logo.png":
        return QIcon(get_logo_path())
    
    base_path = Path(__file__).resolve().parent.parent / "assets" / "icon"
    if not base_path.exists():
        base_path = Path(__file__).resolve().parent / "assets" / "icon"
        
    file_path = base_path / name
    if file_path.exists():
        return QIcon(str(file_path))
    return QIcon()

# ==========================================
#  1. TELA DE LOGIN (SMART LOGIN + ACESSIBILIDADE)
# ==========================================
class LoginPage(QWidget):
    login_success = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("BertoliniSystems", "GlobusERP")
        self.init_db_fallback() # INICIALIZA O BANCO LOCAL SE NÃO EXISTIR
        self.init_ui()
        self.load_last_user()

    def init_db_fallback(self):
        """Cria o banco local e a tabela clients se não existirem para evitar erro."""
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT UNIQUE,
                    password TEXT,
                    business_type TEXT,
                    status TEXT
                )
            """)
            # Verifica se tem admin, se não, cria
            cursor.execute("SELECT count(*) FROM clients")
            if cursor.fetchone()[0] == 0:
                print("🛠️ Criando usuário admin padrão no banco local...")
                cursor.execute(
                    "INSERT INTO clients (login, password, business_type, status) VALUES (?, ?, ?, ?)",
                    ("admin", "admin", "vendas,financeiro,fiscal,estoque,frotas,rh,crm,producao,qualidade", "Ativo")
                )
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Erro ao inicializar banco local: {e}")

    def init_ui(self):
        # Fundo Degradê Moderno
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #0f2027, stop:0.5 #203a43, stop:1 #2c5364);
            }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Cartão de Login
        card = QFrame()
        card.setFixedSize(450, 620)
        card.setStyleSheet("""
            QFrame { 
                background-color: #ffffff; 
                border-radius: 20px; 
            }
            QLabel { 
                color: #333; font-family: 'Segoe UI'; border: none; background: transparent; 
            }
            QLineEdit { 
                padding: 14px; border: 2px solid #e0e0e0; border-radius: 8px; 
                background: #f8f9fa; color: #333; font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #2c5364; background: #fff; }
            QPushButton { 
                background-color: #2c5364; color: white; padding: 14px; 
                border-radius: 8px; font-weight: bold; font-size: 16px;
                border: none;
            }
            QPushButton:hover { background-color: #203a43; }
            QPushButton:pressed { background-color: #0f2027; }
            QCheckBox { 
                color: #555; background: transparent; font-size: 13px;
            }
            QCheckBox::indicator { width: 18px; height: 18px; }
        """)
        
        # Sombra Elegante
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(50, 50, 50, 50)
        lay.setSpacing(15)
        
        # --- LOGO DA BERTOLINI (FIXA NO LOGIN) ---
        self.lbl_logo = QLabel()
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(get_original_logo()) 
        if not pix.isNull():
            self.lbl_logo.setPixmap(pix.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.lbl_logo.setText("BERTOLINI ERP")
            self.lbl_logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
            
        lbl_badge = QLabel("💳 Aproxime o Crachá ou Digite")
        lbl_badge.setAlignment(Qt.AlignCenter)
        lbl_badge.setStyleSheet("color: #2980b9; font-weight: bold; font-size: 14px; margin-top: 10px;")

        self.user = QLineEdit(); self.user.setPlaceholderText("Usuário ou Código do Crachá")
        self.pwd = QLineEdit(); self.pwd.setPlaceholderText("Senha"); self.pwd.setEchoMode(QLineEdit.Password)
        
        # --- NOVO: SUPORTE A ENTER ---
        self.user.returnPressed.connect(self.check_login)
        self.pwd.returnPressed.connect(self.check_login)

        self.chk_remember = QCheckBox("Lembrar meu usuário")
        self.chk_remember.setCursor(Qt.PointingHandCursor)

        btn = QPushButton("ACESSAR SISTEMA")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.check_login)

        lay.addWidget(self.lbl_logo)
        lay.addWidget(lbl_badge) 
        lay.addWidget(self.user)
        lay.addWidget(self.pwd)
        lay.addWidget(self.chk_remember)
        lay.addSpacing(10); lay.addWidget(btn); lay.addStretch()
        
        lbl_info = QLabel("Sistema Multi-Empresa v5.0\nPowered by Bertolini Systems", alignment=Qt.AlignCenter)
        lbl_info.setStyleSheet("color: #999; font-size: 11px;")
        lay.addWidget(lbl_info)
        
        layout.addWidget(card)
        
        # --- NOVO: ORDEM DO TAB ---
        QWidget.setTabOrder(self.user, self.pwd)
        QWidget.setTabOrder(self.pwd, self.chk_remember)
        QWidget.setTabOrder(self.chk_remember, btn)

        # Foco automático no usuário para leitura de crachá
        QTimer.singleShot(500, self.user.setFocus)

    def load_last_user(self):
        saved_user = self.settings.value("last_user", "")
        if saved_user:
            self.user.setText(saved_user)
            self.chk_remember.setChecked(True)

    def check_login(self):
        u, p = self.user.text().strip(), self.pwd.text().strip()
        
        # --- SMART LOGIN (CRACHÁ) ---
        if u.startswith("CRACHA:"):
            badge_code = u.split(":")[1]
            if badge_code == "001": # Código do Gerente Usina
                self.login_success.emit("admin", "vendas,financeiro,fiscal,estoque,frotas,rh,crm,producao,qualidade")
                return
            elif badge_code == "002": # Código do Mecânico
                self.login_success.emit("admin", "oficina,estoque")
                return
        # ------------------------------------

        if self.chk_remember.isChecked():
            self.settings.setValue("last_user", u)
        else:
            self.settings.remove("last_user")

        if u == "bertolini" and p == "masterkey":
            self.login_success.emit("bertolini_master", "master")
            return
        
        try:
            # Login via Banco de Dados Local (Licenças)
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute("SELECT business_type, status FROM clients WHERE login=? AND password=?", (u, p))
            res = cursor.fetchone()
            conn.close()

            if res:
                modules_string, status = res
                if status == "Bloqueado":
                    QMessageBox.warning(self, "Acesso Negado", "🚫 Sua licença está suspensa.\nContate o suporte Bertolini.")
                else:
                    self.login_success.emit("admin", modules_string)
            else:
                QMessageBox.warning(self, "Erro", "🔒 Usuário ou senha incorretos.")
        except Exception as e:
            print(f"Erro login: {e}")
            if u == "admin" and p == "admin": 
                # Fallback de emergência
                self.login_success.emit("admin", "vendas,financeiro")

# ==========================================
#  2. PORTAL (MOSTRA A LOGO DO CLIENTE)
# ==========================================
class PortalPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window

    def refresh_ui(self, modules_string="vendas,financeiro"):
        if self.layout(): QWidget().setLayout(QVBoxLayout())
        lay = QVBoxLayout(self); lay.setContentsMargins(50, 40, 50, 40)

        # --- CABEÇALHO DO CLIENTE ---
        header_row = QHBoxLayout() # QHBoxLayout ESTÁ CORRETAMENTE IMPORTADO
        
        # Logo do Cliente (Esquerda) - Pega a customizada se tiver
        lbl_client_logo = QLabel()
        pix_client = QPixmap(get_logo_path()) 
        if not pix_client.isNull():
            lbl_client_logo.setPixmap(pix_client.scaled(120, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Textos de Boas-Vindas
        text_col = QVBoxLayout()
        text_col.setAlignment(Qt.AlignVCenter)
        lbl_welcome = QLabel(f"Bem-vindo ao Sistema, Comandante!")
        lbl_welcome.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        lbl_desc = QLabel(f"Módulos Ativos: {modules_string.replace(',', ' | ').upper()}")
        lbl_desc.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        text_col.addWidget(lbl_welcome)
        text_col.addWidget(lbl_desc)
        
        header_row.addWidget(lbl_client_logo)
        header_row.addSpacing(20)
        header_row.addLayout(text_col)
        header_row.addStretch()
        
        lay.addLayout(header_row)
        lay.addSpacing(30)

        grid = QGridLayout(); grid.setSpacing(25)

        # --- LÓGICA DE PERFIS DINÂMICA ---
        active_modules = modules_string.split(",")
        pos = 0
        
        # Mapeamento: (Chave no Banco, Título, Subtítulo, Ícone, Cor, Código para abrir)
        module_map = [
            ("vendas", "VENDAS (PDV)", "Frente de Caixa", "pos.png", "#27ae60", "vendas"),
            ("financeiro", "FINANCEIRO", "Fluxo, DRE e Boletos", "finance_icon.png", "#2980b9", "financeiro"),
            ("fiscal", "FISCAL & NFe", "Emissão Fiscal", "pos.png", "#c0392b", "fiscal"),
            ("estoque", "ESTOQUE", "Controle de Materiais", "stock_icon.png", "#f39c12", "estoque"),
            ("frotas", "FROTAS", "Gestão de Veículos", "shipping_icon.png", "#16a085", "frotas"),
            ("oficina", "MANUTENÇÃO", "Ordens de Serviço", "os_icon.png", "#d35400", "oficina"),
            ("rh", "RH & PONTO", "Gestão de Pessoas", "users.png", "#2c3e50", "rh"),
            ("crm", "CRM & AGENDA", "Relacionamento", "users.png", "#e67e22", "crm"),
            ("producao", "INDÚSTRIA 4.0", "Monitoramento SCADA", "stock_icon.png", "#8e44ad", "producao"),
            ("qualidade", "QUALIDADE (LIMS)", "Laboratório", "users.png", "#16a085", "qualidade")
        ]

        for mod_key, title, sub, icon, color, code in module_map:
            if mod_key in active_modules:
                r, c = divmod(pos, 4) # Organiza em 4 colunas
                self.add_tile(grid, r, c, title, sub, icon, color, code)
                pos += 1

        lay.addLayout(grid)
        lay.addStretch()
        
        # Botão Sair
        btn_out = QPushButton("🚪 Sair do Sistema")
        btn_out.setCursor(Qt.PointingHandCursor)
        btn_out.setStyleSheet("""
            QPushButton { background: transparent; color: #c0392b; font-weight: bold; font-size: 14px; text-align: left; }
            QPushButton:hover { text-decoration: underline; }
        """)
        btn_out.clicked.connect(self.main.logout_system)
        lay.addWidget(btn_out)

    def add_tile(self, grid, r, c, title, sub, icon, color, code):
        btn = QPushButton()
        btn.setFixedSize(260, 160)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background: white; 
                border-left: 6px solid {color}; 
                border-radius: 10px; 
                text-align: left; 
                padding: 20px; 
            }}
            QPushButton:hover {{ 
                background: #fdfdfd; 
                border-left: 8px solid {color};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0,0,0, 30))
        shadow.setOffset(0, 3)
        btn.setGraphicsEffect(shadow)
        
        v_lay = QVBoxLayout(btn)
        ico = QLabel(); ico.setPixmap(get_icon(icon).pixmap(48, 48))
        v_lay.addWidget(ico)
        v_lay.addSpacing(10)
        v_lay.addWidget(QLabel(f"<span style='font-size:16px; font-weight:bold; color:#333'>{title}</span>"))
        v_lay.addWidget(QLabel(f"<span style='font-size:12px; color:#777'>{sub}</span>"))
        
        btn.clicked.connect(lambda: self.main.open_workspace(code))
        grid.addWidget(btn, r, c)

# ==========================================
#  3. JANELA PRINCIPAL (ESTRUTURA COMPLETA)
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self, api_base_url: str):
        super().__init__()
        
        self.api_base_url = api_base_url
        self.bus = EventBus()
        self.client = ApiClient(api_base_url)
        self.current_role = None # Guarda papel para toolbar dinâmica
        
        self.setWindowTitle("Bertolini Globus ERP v5.0 Enterprise")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 768)
        
        # Ícone da Janela
        self.setWindowIcon(get_icon("logo.png"))
        
        self.root = QWidget(); self.setCentralWidget(self.root)
        self.layout = QVBoxLayout(self.root); self.layout.setContentsMargins(0,0,0,0)
        
        # Toolbar Estilizada
        self.toolbar = QToolBar("Navegação"); self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setStyleSheet("""
            QToolBar { background: #fff; border-bottom: 1px solid #ddd; padding: 10px; spacing: 15px; }
            QToolButton { color: #333; font-weight: 500; font-size: 13px; padding: 5px 10px; border-radius: 4px; }
            QToolButton:hover { background: #f0f0f0; color: #000; }
        """)
        self.toolbar.hide()
        
        self.pages = QStackedWidget(); self.layout.addWidget(self.pages)
        
        # --- INSTANCIANDO AS PÁGINAS ---
        self.login_page = LoginPage()
        self.portal_page = PortalPage(self)
        self.master_page = AdminPage(self) 
        
        self.pos_page = PosPage(self.client.base_url, bus=self.bus)
        self.fiscal_page = FiscalPage(bus=self.bus)
        self.finance_page = FinancePage(bus=self.bus)
        self.inventory_page = InventoryPage(bus=self.bus)
        self.os_page = OSPage(bus=self.bus)
        self.orders_page = OrdersPage(bus=self.bus) 
        self.purchases_page = PurchasesPage(bus=self.bus)
        self.manual_page = ManualPurchasePage(bus=self.bus)
        self.history_page = SalesHistoryPage(self.client.base_url, bus=self.bus)
        self.products_page = ProductsWindow(self.client.base_url, bus=self.bus)
        self.suppliers_page = SuppliersWindow(self.client.base_url, bus=self.bus)
        self.settings_page = SettingsPage(bus=self.bus, expiry_date="2026-12-31", main_window=self)
        self.import_page = ImportPage(bus=self.bus)
        self.dashboard_page = DashboardPage(api_base_url=self.api_base_url, business_type="enterprise", bus=self.bus)
        
        # >>> MÓDULOS DE ELITE <<<
        self.fleet_page = FleetPage(bus=self.bus)
        self.hr_page = HRPage(bus=self.bus)
        self.crm_page = CRMPage(bus=self.bus) 
        self.quality_page = QualityPage(bus=self.bus) 
        self.production_page = ProductionPage(bus=self.bus) 
        self.monitoring_page = MonitoringPage(bus=self.bus) # >>> NOVO MÓDULO NUVEM <<<

        # Adicionando ao Stack
        pages_list = [
            self.login_page, self.portal_page, self.master_page, 
            self.pos_page, self.fiscal_page, self.finance_page, 
            self.inventory_page, self.os_page, self.orders_page, 
            self.purchases_page, self.manual_page, self.history_page, 
            self.products_page, self.suppliers_page, self.settings_page, 
            self.import_page, self.dashboard_page, 
            self.fleet_page, self.hr_page, self.crm_page,
            self.quality_page, self.production_page, self.monitoring_page
        ]
        
        for p in pages_list: self.pages.addWidget(p)

        # --- CONEXÃO DO EVENT BUS PARA CLIENTES ---
        if hasattr(self.bus, 'subscribe'):
            self.bus.subscribe("open_customers", self.open_customers_window)

        self.login_page.login_success.connect(self.handle_login)
        self.pages.setCurrentWidget(self.login_page)
        
        # --- HEARTBEAT DE NUVEM (PARA MONITORAMENTO) ---
        self.cloud_timer = QTimer(self)
        self.cloud_timer.timeout.connect(self.background_cloud_sync)
        self.cloud_timer.start(30000) # Sincroniza meta-dados a cada 30s

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1: self.return_to_portal()
        elif event.key() == Qt.Key_F12: self.logout_system()
        elif event.key() == Qt.Key_F9: self.pages.setCurrentWidget(self.settings_page)
        super().keyPressEvent(event)

    def handle_login(self, role, b_type):
        self.current_role = role # IMPORTANTE: SALVA O PAPEL
        if role == "bertolini_master":
            self.open_workspace("master_monitoring") # Abre direto na central mestre
        else:
            self.portal_page.refresh_ui(b_type)
            self.dashboard_page.business_type = b_type
            self.pages.setCurrentWidget(self.portal_page)
        self.toolbar.hide()

    def open_workspace(self, code):
        """O Cérebro da Navegação - Configura a Toolbar e abre a página certa"""
        self.toolbar.show(); self.toolbar.clear()
        
        # Botão Voltar para o Portal
        self.add_nav("home.png", "Portal Início", self.return_to_portal)
        self.toolbar.addSeparator()

        # --- SEÇÃO MASTER (NAVEGAÇÃO NO TOPO) ---
        if self.current_role == "bertolini_master":
            self.add_nav("stock_icon.png", "Monitoramento Nuvem", lambda: self.pages.setCurrentWidget(self.monitoring_page))
            self.add_nav("users.png", "Gestão Master", lambda: self.pages.setCurrentWidget(self.master_page))
            if code == "master_monitoring": self.pages.setCurrentWidget(self.monitoring_page)

        # --- MÓDULOS OPERACIONAIS ---
        if code == "vendas":
            self.add_nav("pos.png", "Frente de Caixa", lambda: self.pages.setCurrentWidget(self.pos_page))
            self.add_nav("inventory.png", "Histórico de Vendas", lambda: self.pages.setCurrentWidget(self.history_page))
            self.add_nav("users.png", "Clientes", self.open_customers_window) 
            self.pages.setCurrentWidget(self.pos_page)
        
        elif code == "oficina": 
            self.add_nav("os_icon.png", "Nova O.S.", lambda: self.pages.setCurrentWidget(self.os_page))
            self.add_nav("inventory.png", "Consultar O.S.", lambda: self.pages.setCurrentWidget(self.os_page))
            self.pages.setCurrentWidget(self.os_page)

        elif code == "fiscal":
            self.add_nav("pos.png", "Painel NFe", lambda: self.pages.setCurrentWidget(self.fiscal_page))
            self.pages.setCurrentWidget(self.fiscal_page)
        
        elif code == "financeiro":
            self.add_nav("finance_icon.png", "Fluxo de Caixa", lambda: self.pages.setCurrentWidget(self.finance_page))
            self.add_nav("inventory.png", "DRE Gerencial", self.open_dre_tab)
            self.pages.setCurrentWidget(self.finance_page)
        
        elif code == "estoque":
            self.add_nav("stock_icon.png", "Visão Geral", lambda: self.pages.setCurrentWidget(self.inventory_page))
            self.add_nav("inventory.png", "Produtos", lambda: self.pages.setCurrentWidget(self.products_page))
            self.add_nav("users.png", "Fornecedores", lambda: self.pages.setCurrentWidget(self.suppliers_page))
            self.pages.setCurrentWidget(self.inventory_page)
            
        elif code == "frotas":
            self.add_nav("shipping_icon.png", "Gestão de Frotas", lambda: self.pages.setCurrentWidget(self.fleet_page))
            self.pages.setCurrentWidget(self.fleet_page)

        elif code == "rh":
            self.add_nav("users.png", "Recursos Humanos", lambda: self.pages.setCurrentWidget(self.hr_page))
            self.pages.setCurrentWidget(self.hr_page)

        elif code == "crm":
            self.add_nav("users.png", "Agenda & CRM", lambda: self.pages.setCurrentWidget(self.crm_page))
            self.pages.setCurrentWidget(self.crm_page)

        elif code == "producao":
            self.add_nav("stock_icon.png", "Indústria 4.0", lambda: self.pages.setCurrentWidget(self.production_page))
            self.pages.setCurrentWidget(self.production_page)

        elif code == "qualidade":
            self.add_nav("users.png", "Laboratório LIMS", lambda: self.pages.setCurrentWidget(self.quality_page))
            self.pages.setCurrentWidget(self.quality_page)
            
        # --- CORREÇÃO DO ADDSTRETCH ---
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        self.add_nav("settings.png", "Opções (F9)", lambda: self.pages.setCurrentWidget(self.settings_page))

    def add_nav(self, icon_name, label, callback):
        act = QAction(get_icon(icon_name), label, self)
        act.triggered.connect(callback)
        self.toolbar.addAction(act)

    def return_to_portal(self): self.toolbar.hide(); self.pages.setCurrentWidget(self.portal_page)
    def logout_system(self): 
        # Mantém Bertolini no Login
        self.toolbar.hide(); self.pages.setCurrentWidget(self.login_page)

    def open_customers_window(self):
        self.customers_win = CustomersWindow(self.api_base_url)
        self.customers_win.show()

    def open_dre_tab(self):
        self.pages.setCurrentWidget(self.finance_page)
        self.finance_page.tabs.setCurrentIndex(2)

    def apply_theme(self, dark_enabled):
        """Aplica o tema escuro ou claro dinamicamente."""
        if dark_enabled:
            QApplication.instance().setStyleSheet("QWidget { background-color: #1e272e; color: #ecf0f1; }")
        else:
            QApplication.instance().setStyleSheet("")

    def background_cloud_sync(self):
        """Simula a pulsação de sincronização com a nuvem"""
        if self.current_role == "bertolini_master":
            # Master apenas monitora a recepção
            print("📡 [MASTER] Monitorando tráfego de dados regional...")
        else:
            # Clientes enviam dados
            print("☁️ [CLIENTE] Sincronizando metadados com Bertolini Cloud...")