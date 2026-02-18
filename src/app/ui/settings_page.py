from __future__ import annotations
import json
import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QLabel, QFormLayout, QGroupBox, QMessageBox, QFrame, 
    QCheckBox, QProgressBar, QTabWidget, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from app.utils.cloud_sync import CloudSyncEngine # Motor de Sincronização mantido

class SettingsPage(QWidget):
    def __init__(self, bus=None, expiry_date="--/--/----", main_window=None):
        super().__init__()
        self.bus = bus
        self.expiry_date = expiry_date
        self.main_window = main_window
        self.settings_file = Path("settings.json")
        
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        header = QLabel("⚙️ Configurações Gerais do Sistema")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(header)

        # --- CRIAÇÃO DAS ABAS ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ddd; background: white; border-radius: 5px; }
            QTabBar::tab { background: #eee; padding: 10px 20px; }
            QTabBar::tab:selected { background: #fff; border-bottom: 2px solid #3498db; font-weight: bold; }
        """)

        # Aba 1: Sistema & Conectividade
        self.tab_system = QWidget()
        self.setup_system_tab(self.tab_system)
        
        # Aba 2: Personalização Visual
        self.tab_visual = QWidget()
        self.setup_visual_tab(self.tab_visual)

        self.tabs.addTab(self.tab_system, "🏢 Unidade & Nuvem")
        self.tabs.addTab(self.tab_visual, "🎨 Identidade Visual")

        layout.addWidget(self.tabs)

        # BOTÃO SALVAR GERAL
        self.btn_save = QPushButton("💾 Salvar Todas as Alterações")
        self.btn_save.setMinimumHeight(50)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #2c3e50; color: white; font-weight: bold; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background-color: #34495e; }
        """)
        self.btn_save.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save)

    def setup_system_tab(self, parent):
        lay = QVBoxLayout(parent)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(15)

        # 1. Aparência
        theme_group = QGroupBox("Aparência Global")
        theme_lay = QVBoxLayout(theme_group)
        self.check_dark = QCheckBox("🌙 Ativar Modo Escuro (Dark Mode)")
        self.check_dark.setStyleSheet("font-size: 14px;")
        self.check_dark.toggled.connect(self.toggle_theme)
        theme_lay.addWidget(self.check_dark)
        lay.addWidget(theme_group)

        # 2. Dados da Unidade (ZERADOS COM PLACEHOLDERS)
        group = QGroupBox("Dados de Identificação")
        f_lay = QFormLayout(group)
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("Digite o Nome Fantasia da Unidade...")
        
        self.edit_cnpj = QLineEdit()
        self.edit_cnpj.setPlaceholderText("00.000.000/0001-00")
        
        f_lay.addRow("Nome Comercial:", self.edit_name)
        f_lay.addRow("CNPJ/CPF:", self.edit_cnpj)
        lay.addWidget(group)

        # 3. Nuvem & Suporte (Para monitoramento remoto)
        cloud_group = QGroupBox("🌐 Sincronização & Suporte Remoto")
        cloud_lay = QVBoxLayout(cloud_group)
        
        self.lbl_cloud_status = QLabel("Status: Conectado ao Servidor Bertolini Cloud")
        self.lbl_cloud_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        self.progress_sync = QProgressBar()
        self.progress_sync.setVisible(False)
        self.progress_sync.setFixedHeight(10)
        
        btn_manual_sync = QPushButton("🔄 Forçar Sincronização Agora")
        btn_manual_sync.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; height: 30px; border-radius: 4px;")
        btn_manual_sync.clicked.connect(self.run_manual_sync)

        btn_support = QPushButton("🎧 Solicitar Suporte Remoto (Kevin Bertolini)")
        btn_support.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; height: 30px; border-radius: 4px;")
        btn_support.clicked.connect(lambda: QMessageBox.information(self, "Suporte", "Solicitação enviada ao painel central! O técnico entrará em contato em breve."))
        
        cloud_lay.addWidget(self.lbl_cloud_status)
        cloud_lay.addWidget(self.progress_sync)
        cloud_lay.addWidget(btn_manual_sync)
        cloud_lay.addWidget(btn_support)
        lay.addWidget(cloud_group)

        # 4. Status Licença
        self.lic_card = QFrame()
        self.lic_card.setStyleSheet("background-color: #d1e7dd; border-radius: 8px; border: 1px solid #badbcc;")
        lic_lay = QVBoxLayout(self.lic_card)
        self.lbl_expiry = QLabel(f"✅ Assinatura Ativa até: {self.expiry_date}")
        self.lbl_expiry.setStyleSheet("color: #0f5132; font-weight: bold; font-size: 14px; background: transparent; border: none;")
        lic_lay.addWidget(self.lbl_expiry)
        lay.addWidget(self.lic_card)
        
        lay.addStretch()

    def setup_visual_tab(self, parent):
        lay = QVBoxLayout(parent)
        lay.setContentsMargins(20, 20, 20, 20)
        
        lbl_inst = QLabel("Personalize o sistema com a marca da sua empresa. A imagem será aplicada nos menus e na tela de login.")
        lbl_inst.setWordWrap(True)
        lbl_inst.setStyleSheet("color: #555; font-size: 14px; margin-bottom: 10px;")
        lay.addWidget(lbl_inst)
        
        self.lbl_preview = QLabel()
        self.lbl_preview.setFixedSize(250, 250)
        self.lbl_preview.setStyleSheet("border: 2px dashed #bdc3c7; border-radius: 10px; background: #f9f9f9;")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        
        btn_upload = QPushButton("📂 Carregar Logomarca")
        btn_upload.setFixedWidth(250)
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        btn_upload.clicked.connect(self.upload_logo)
        
        btn_reset = QPushButton("↺ Restaurar Logotipo Padrão")
        btn_reset.setFixedWidth(250)
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px; border-radius: 5px;")
        btn_reset.clicked.connect(self.reset_logo)

        lay.addSpacing(10)
        lay.addWidget(self.lbl_preview, alignment=Qt.AlignCenter)
        lay.addSpacing(15)
        lay.addWidget(btn_upload, alignment=Qt.AlignCenter)
        lay.addWidget(btn_reset, alignment=Qt.AlignCenter)
        lay.addStretch()
        
        self.load_current_logo_preview()

    def get_assets_path(self):
        return Path(__file__).resolve().parent / "assets"

    def load_current_logo_preview(self):
        assets = self.get_assets_path()
        custom_path = assets / "custom_logo.png"
        default_path = assets / "logo.png"
        path_to_show = str(custom_path) if custom_path.exists() else str(default_path)
        
        pix = QPixmap(path_to_show)
        if not pix.isNull():
            self.lbl_preview.setPixmap(pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.lbl_preview.setText("Sem Logotipo")

    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Logomarca", "", "Imagens (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                assets = self.get_assets_path()
                assets.mkdir(parents=True, exist_ok=True)
                dest_path = assets / "custom_logo.png"
                shutil.copy(file_path, dest_path)
                self.load_current_logo_preview()
                QMessageBox.information(self, "Sucesso", "Logomarca atualizada! As mudanças serão aplicadas na próxima inicialização.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar imagem: {e}")

    def reset_logo(self):
        try:
            assets = self.get_assets_path()
            custom_path = assets / "custom_logo.png"
            if custom_path.exists():
                os.remove(custom_path)
            self.load_current_logo_preview()
            QMessageBox.information(self, "Restaurado", "Configuração de marca retornada ao padrão.")
        except Exception as e:
            print(f"Erro reset: {e}")

    def run_manual_sync(self):
        self.progress_sync.setVisible(True)
        self.progress_sync.setRange(0, 0)
        self.lbl_cloud_status.setText("Status: Sincronizando dados com Bertolini Cloud...")
        self.lbl_cloud_status.setStyleSheet("color: #2980b9; font-weight: bold;")

        self.sync_engine = CloudSyncEngine()
        self.sync_engine.sync_finished.connect(self.on_sync_complete)
        self.sync_engine.start()

    def on_sync_complete(self, success, message):
        self.progress_sync.setVisible(False)
        if success:
            self.lbl_cloud_status.setText(f"Status: {message}")
            self.lbl_cloud_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.lbl_cloud_status.setText(f"Erro: {message}")
            self.lbl_cloud_status.setStyleSheet("color: #c0392b; font-weight: bold;")

    def toggle_theme(self, checked):
        if self.main_window:
            self.main_window.apply_theme(checked)

    def save_settings(self):
        data = {
            "company_name": self.edit_name.text(),
            "cnpj": self.edit_cnpj.text(),
            "dark_mode": self.check_dark.isChecked()
        }
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Salvo", "Todas as configurações foram registradas.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gravar arquivo: {e}")

    def load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.edit_name.setText(data.get("company_name", ""))
                    self.edit_cnpj.setText(data.get("cnpj", ""))
                    is_dark = data.get("dark_mode", False)
                    self.check_dark.setChecked(is_dark)
                    if self.main_window:
                        self.main_window.apply_theme(is_dark)
            except: pass