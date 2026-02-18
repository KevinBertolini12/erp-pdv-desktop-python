import os
import hashlib
import shutil
import requests
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from app.core.security_vault import SecurityVault 

class CloudSyncEngine(QThread):
    """
    Motor de Sincronização Bertolini Cloud v3.0
    Blindagem AES-256 + Telemetria em Tempo Real para o Painel Master.
    """
    sync_finished = Signal(bool, str)

    def __init__(self, db_path="test.db"):
        super().__init__()
        self.db_path = db_path
        
        # --- CORREÇÃO DE SEGURANÇA ---
        # A chave agora é um formato Fernet válido (32 bytes em Base64)
        self.master_key = b'kMh_vT8Y1P9I6Q9G1Y8_m8_T9K_v5L_v7X_9R_9I_20=' 
        
        # --- URL OFICIAL DA NUVEM ---
        self.cloud_hub_url = "https://erp-pdv-desktop-python-production.up.railway.app/api/sync" 

    def run(self):
        vault_path = None
        try:
            # 1. Validação de existência
            if not os.path.exists(self.db_path):
                self.sync_finished.emit(False, "Arquivo de banco de dados não encontrado.")
                return

            # 2. Gera o Checksum (Integridade)
            with open(self.db_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            # 3. BLINDAGEM AES-256
            vault_path = SecurityVault.criptografar_arquivo(self.db_path, self.master_key)

            # 4. TELEMETRIA EM TEMPO REAL
            # Envia o pulso de dados para o seu monitoramento Master
            self.enviar_resumo_vendas(file_hash)

            # 5. BACKUP EM NUVEM (Registro Local de Envio)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not os.path.exists("cloud_backups"): 
                os.makedirs("cloud_backups")
            
            backup_name = f"cloud_backups/backup_{timestamp}.db.vault"
            shutil.copy2(vault_path, backup_name)

            # 6. LIMPEZA DE RASTROS
            if vault_path and os.path.exists(vault_path):
                os.remove(vault_path)

            self.sync_finished.emit(
                True, 
                f"Sincronização Blindada Concluída!\nIntegridade: {file_hash[:8]}..."
            )

        except Exception as e:
            if vault_path and os.path.exists(vault_path):
                os.remove(vault_path)
            self.sync_finished.emit(False, f"Falha na Sincronização: {str(e)}")

    def enviar_resumo_vendas(self, checksum):
        """
        [MÉDULO CLOUD]
        Envia os dados de faturamento para o hub central no Railway.
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Pega o faturamento real para atualizar seu monitoramento
            cursor.execute("SELECT SUM(total_value) FROM sales")
            total = cursor.fetchone()[0] or 0.0
            
            payload = {
                "unit_id": "001", 
                "total_sales": total,
                "last_checksum": checksum,
                "timestamp": datetime.now().isoformat()
            }
            
            # ENVIO REAL PARA A NUVEM
            response = requests.post(self.cloud_hub_url, json=payload, timeout=8)
            
            if response.status_code == 200:
                print(f"📡 [NUVEM] Telemetria entregue: R$ {total:.2f}")
            else:
                print(f"⚠️ [NUVEM] Erro no servidor: {response.status_code}")
            
            conn.close()
        except Exception as e:
            print(f"⚠️ [NUVEM] Falha de conexão: {str(e)}")