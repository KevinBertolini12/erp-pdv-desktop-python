class StatsEngine:
    @staticmethod
    def calcular_kpis(vendas, laudos, manutencoes):
        """
        vendas: lista de dicts [{'total': 100.0}]
        laudos: lista de dicts [{'status': 'APROVADO'}]
        """
        # 1. Faturamento Total
        total_faturado = sum(v.get('total', 0) for v in vendas)
        
        # 2. Índice de Qualidade (Indispensável para Polipet/Engevap)
        total_laudos = len(laudos)
        aprovados = len([l for l in laudos if l.get('status') == 'APROVADO'])
        indice_qualidade = (aprovados / total_laudos * 100) if total_laudos > 0 else 100
        
        # 3. Ticket Médio (Essencial para o comércio pequeno)
        ticket_medio = (total_faturado / len(vendas)) if len(vendas) > 0 else 0
        
        return {
            "faturamento": total_faturado,
            "qualidade": indice_qualidade,
            "ticket_medio": ticket_medio,
            "alertas_manutencao": len([m for m in manutencoes if m.get('status') == 'ALERTA'])
        }