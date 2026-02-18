import shutil
import os
from datetime import datetime
from pathlib import Path

def realizar_backup_diario():
    # 1. Localização do banco e da pasta de backup
    db_path = Path("app.db")
    backup_dir = Path("backups")
    
    if not db_path.exists():
        return # Se o banco não existe, não faz nada
        
    # 2. Cria a pasta de backup se não existir
    backup_dir.mkdir(exist_ok=True)
    
    # 3. Gera o nome do arquivo com a data (ex: backup_2026-02-11.db)
    data_str = datetime.now().strftime("%Y-%m-%d")
    nome_backup = f"backup_{data_str}.db"
    destino = backup_dir / nome_backup
    
    # 4. Só faz o backup se ainda não existir um de hoje (evita lentidão)
    if not destino.exists():
        try:
            shutil.copy2(db_path, destino)
            print(f"[BACKUP] Cópia de segurança criada: {nome_backup}")
        except Exception as e:
            print(f"[BACKUP] ERRO: {e}")