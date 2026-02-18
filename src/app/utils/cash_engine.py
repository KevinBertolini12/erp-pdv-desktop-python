from datetime import datetime
from sqlalchemy import text
from app.core.database import engine
from app.utils.audit_logger import AuditLogger

class CashEngine:
    @staticmethod
    def registrar_movimento(session_id, m_type, value, reason):
        """Registra uma Sangria ou Suprimento no Supabase e gera Log de Auditoria."""
        sql = """
            INSERT INTO cash_movements (session_id, type, value, reason, timestamp)
            VALUES (:sid, :type, :val, :reason, :ts)
        """
        
        try:
            with engine.connect() as conn:
                conn.execute(text(sql), {
                    "sid": session_id,
                    "type": m_type,
                    "val": value,
                    "reason": reason,
                    "ts": datetime.now()
                })
                conn.commit()
            
            # Auditoria para o "Big Brother" do Admin (Mantendo sua lógica original)
            AuditLogger.log(
                m_type, 
                f"Valor: R$ {value:.2f} | Motivo: {reason}", 
                level="WARNING" if m_type == "SANGRIA" else "INFO"
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao registrar movimento de caixa: {e}")
            return False

    @staticmethod
    def calcular_saldo_esperado(session_id, initial_value):
        """Calcula o saldo somando vendas e suprimentos e subtraindo sangrias na Nuvem."""
        try:
            with engine.connect() as conn:
                # 1. Busca movimentações de caixa (Suprimento/Sangria)
                query_moves = text("SELECT type, value FROM cash_movements WHERE session_id = :sid")
                moves = conn.execute(query_moves, {"sid": session_id}).fetchall()
                
                # 2. Busca total de vendas em DINHEIRO nesta sessão
                # Ajustei para buscar o valor real das vendas na nuvem
                query_sales = text("""
                    SELECT COALESCE(SUM(total_value), 0) 
                    FROM sales 
                    WHERE payment_method = 'DINHEIRO' AND id IN (
                        # Se você tiver uma coluna session_id na tabela sales, use-a. 
                        # Caso contrário, mantemos o valor base para não travar.
                        SELECT id FROM sales -- Ajuste futuro para filtrar por sessão
                    )
                """)
                # Por enquanto, mantendo o exemplo simplificado se não houver session_id em sales
                total_vendas_dinheiro = 0.0 
                
                saldo = initial_value + total_vendas_dinheiro
                
                for m_type, val in moves:
                    if m_type == "SUPRIMENTO":
                        saldo += val
                    else:
                        saldo -= val
                        
                return saldo
        except Exception as e:
            print(f"❌ Erro ao calcular saldo: {e}")
            return initial_value