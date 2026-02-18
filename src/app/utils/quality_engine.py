import json
import sqlite3

class QualityEngine:
    @staticmethod
    def verificar_conformidade(resultados, especificacoes):
        """
        Compara os valores reais com os limites técnicos.
        especificacoes: lista de dicts com min_value e max_value
        resultados: dict com os valores medidos { 'pH': 7.2 }
        """
        for spec in especificacoes:
            param = spec['parameter_name']
            valor_real = resultados.get(param)
            
            if valor_real is not None:
                if not (spec['min_value'] <= valor_real <= spec['max_value']):
                    return "REPROVADO", f"Parâmetro {param} fora dos limites!"
        
        return "APROVADO", "Produto dentro dos padrões de qualidade."

    @staticmethod
    def calcular_desvio_percentual(valor_alvo, valor_real):
        """Calcula o quanto a produção desviou do ideal."""
        if valor_alvo == 0: return 0
        desvio = ((valor_real - valor_alvo) / valor_alvo) * 100
        return round(desvio, 2)
    
    @staticmethod
    def is_lote_aprovado(lote_num):
        """Verifica no banco se o lote está liberado para venda."""
        try:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            # Busca o último laudo desse lote
            cursor.execute("""
                SELECT status FROM quality_logs 
                WHERE lot_number = ? 
                ORDER BY analysis_date DESC LIMIT 1
            """, (lote_num,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0] == "APROVADO":
                return True
            return False
        except Exception as e:
            print(f"Erro na verificação de qualidade: {e}")
            return False