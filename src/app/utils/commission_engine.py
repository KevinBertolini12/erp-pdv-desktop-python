class CommissionEngine:
    @staticmethod
    def calcular_comissao(valor_venda, taxa_comissao):
        """Calcula o valor líquido da comissão."""
        return (valor_venda * (taxa_comissao / 100))

    @staticmethod
    def gerar_ranking_vendedores(lista_vendas):
        """Transforma uma lista bruta de vendas em um ranking de performance."""
        ranking = {}
        for venda in lista_vendas:
            vendedor = venda.get("seller_name", "Geral")
            total = venda.get("total", 0.0)
            
            if vendedor not in ranking:
                ranking[vendedor] = {"vendas": 0, "faturamento": 0.0}
            
            ranking[vendedor]["vendas"] += 1
            ranking[vendedor]["faturamento"] += total
            
        return ranking