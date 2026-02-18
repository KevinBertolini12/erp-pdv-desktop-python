import sqlite3
from datetime import datetime
from app.core.auth import current_session

class AuditLogger:
    @staticmethod
    def log(action: str, detail: str, level="INFO"):
        """Grava a ação do usuário no banco de dados de logs."""
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            
            # Garante que a tabela de logs existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    user_name TEXT,
                    user_role TEXT,
                    action TEXT,
                    detail TEXT,
                    level TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, user_name, user_role, action, detail, level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                current_session.user_name,
                current_session.role,
                action,
                detail,
                level
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Erro ao gravar log: {e}")

print("🛡️ Sentinela de Auditoria Ativado!")

@staticmethod
def log(action: str, detail: str, level="INFO"):
        # ... (seu código de gravar no banco continua igual)
        
        # Se o nível for CRITICAL, avisa o dono na hora!
        if level == "CRITICAL":
            from app.utils.bot_engine import BotEngine
            BotEngine.enviar_alerta(f"*AÇÃO CRÍTICA:* {action}\n*DETALHE:* {detail}", nivel="CRITICAL")