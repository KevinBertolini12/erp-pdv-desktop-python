import sqlite3
import os

class MigrationEngine:
    @staticmethod
    def check_and_migrate(db_path):
        # Garante o caminho absoluto
        abs_path = os.path.abspath(db_path)
        print(f"🔍 Auditando banco de dados em: {abs_path}")
        
        conn = sqlite3.connect(abs_path)
        cursor = conn.cursor()
        
        # 1. Garante Tabelas Essenciais (INCLUINDO stock_moves)
        cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS db_version (version INTEGER)")
        
        # Criação da tabela que faltava: stock_moves
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                delta INTEGER NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)
        conn.commit()

        # 2. LISTA DE COLUNAS OBRIGATÓRIAS
        # Formato: (Tabela, Coluna, Tipo/Default)
        required_columns = [
            ("products", "name", "TEXT DEFAULT 'Novo Produto'"),
            ("products", "sku", "TEXT"),
            ("products", "price", "REAL DEFAULT 0"),
            ("products", "cost_price", "REAL DEFAULT 0"),
            ("products", "stock_qty", "REAL DEFAULT 0"),
            ("products", "min_stock", "REAL DEFAULT 0"),
            ("products", "type", "TEXT DEFAULT 'product'"),
            ("products", "ncm_code", "TEXT"),
            ("products", "ipi_rate", "REAL DEFAULT 0"),
            ("products", "icms_rate", "REAL DEFAULT 0"),
            
            ("sales", "total", "REAL DEFAULT 0"),
            ("sales", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("sales", "branch_id", "INTEGER DEFAULT 1"),
            ("sales", "payment_method", "TEXT DEFAULT 'DINHEIRO'") # <--- Coluna Nova
        ]

        print("🛠️ Iniciando verificação coluna-por-coluna...")
        
        for table, col, definition in required_columns:
            try:
                # Tenta ler a coluna
                cursor.execute(f"SELECT {col} FROM {table} LIMIT 1")
            except sqlite3.OperationalError:
                # Se falhar, cria a coluna
                print(f"   ⚠️ Coluna '{col}' ausente em '{table}'. Criando...")
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
                    conn.commit()
                    print(f"   ✅ Coluna '{col}' criada com sucesso!")
                except Exception as e:
                    print(f"   ❌ Erro ao criar '{col}': {e}")

        conn.close()
        print("✅ Auditoria concluída. O banco está sincronizado.")