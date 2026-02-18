class TaxEngine:
    @staticmethod
    def calcular_impostos_venda(valor_venda, ncm_rules):
        """Calcula a carga tributária detalhada de uma venda."""
        icms = valor_venda * ncm_rules.get('icms_rate', 0.18)
        ipi = valor_venda * ncm_rules.get('ipi_rate', 0)
        pis_cofins = valor_venda * (ncm_rules.get('pis_rate', 0) + ncm_rules.get('cofins_rate', 0))
        
        total_imposto = icms + ipi + pis_cofins
        return {
            "icms": icms,
            "ipi": ipi,
            "pis_cofins": pis_cofins,
            "total_tributos": total_imposto,
            "lucro_liquido": valor_venda - total_imposto
        }