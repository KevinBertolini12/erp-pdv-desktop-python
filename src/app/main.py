import sys
import os
import time
import threading
import traceback
import uvicorn
import sqlite3
from datetime import datetime
from pathlib import Path

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# --- 2. IMPORTAÇÕES ---
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
from PySide6.QtGui import QIcon

try:
    from app.ui.main_window import MainWindow
    try:
        from app.db.migrations import MigrationEngine
    except ImportError:
        MigrationEngine = None
except ImportError as e:
    print("\n❌ ERRO CRÍTICO DE IMPORTAÇÃO:")
    print(f"Não foi possível encontrar os módulos do sistema.")
    print(f"Detalhe do erro: {e}")
    print(f"Caminho base tentado: {BASE_DIR}")
    sys.exit(1)

API_PORT = 8000
API_HOST = "127.0.0.1"
API_URL = f"http://{API_HOST}:{API_PORT}"
DB_PATH = os.path.join(BASE_DIR, "storage.db")

# --- 3. AUTO-MIGRAÇÃO ---
def run_database_migrations():
    print("🛠️ Verificando banco de dados...")
    if MigrationEngine:
        try:
            MigrationEngine.check_and_migrate(DB_PATH)
        except Exception as e:
            print(f"⚠️ Aviso: Falha na migração: {e}")

# --- 4. SERVIDOR API ---
def start_server():
    print(f"🚀 Iniciando Servidor em {API_URL}...")
    try:
        from app.api.server import app as fastapi_app
        uvicorn.run(fastapi_app, host=API_HOST, port=API_PORT, log_level="error")
    except Exception as e:
        print(f"❌ Erro no servidor: {e}")

# --- 5. EXECUÇÃO PRINCIPAL ---
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Bertolini ERP")

    try:
        if getattr(sys, 'frozen', False):
            icon_path = Path(sys._MEIPASS) / "app" / "ui" / "assets" / "icon" / "logo.png"
        else:
            icon_path = Path(__file__).resolve().parent / "ui" / "assets" / "icon" / "logo.png"
            
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    except: pass

    run_database_migrations()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("⏳ Iniciando interface...")
    time.sleep(1)

    try:
        window = MainWindow(api_base_url=API_URL)
        window.show()
        
        # --- EXECUÇÃO DO APP ---
        exit_code = app.exec()
        
        # --- GATILHO DE BACKUP DE SEGURANÇA AO FECHAR ---
        print("🛡️ Iniciando backup de segurança...")
        try:
            from app.utils.backup_engine import BackupEngine
            path_backup = BackupEngine.realizar_backup()
            if path_backup:
                print(f"✅ Backup concluído: {path_backup}")
        except Exception as be:
            print(f"⚠️ Falha no motor de backup: {be}")
        
        sys.exit(exit_code)
        
    except Exception as e:
        error_msg = f"Erro fatal ao abrir janela:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        QMessageBox.critical(None, "Erro Fatal", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()