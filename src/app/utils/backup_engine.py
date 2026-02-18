import shutil
import os
from datetime import datetime
import sqlite3

class BackupEngine:
    @staticmethod
    def realizar_backup():
        """Copia o banco de dados para uma pasta de backup com data e hora"""
        db_path = "test.db"
        backup_dir = "backups"
        
        if not os.path.exists(db_path):
            return False
            
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_bertolini_{timestamp}.db")
        
        try:
            # Garante que o banco não está travado antes de copiar
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA wal_checkpoint(FULL)")
            conn.close()
            
            shutil.copy2(db_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Erro no backup: {e}")
            return False