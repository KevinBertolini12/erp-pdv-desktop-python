import json
from pathlib import Path

def gerar_recibo_texto(venda_id, itens, total):
    """Gera uma string formatada para impressão térmica de 80mm"""
    
    # Busca dados da empresa nas configurações
    settings_path = Path("settings.json")
    empresa = "BERTOLINI ERP"
    cnpj = ""
    
    if settings_path.exists():
        try:
            with open(settings_path, "r") as f:
                data = json.load(f)
                empresa = data.get("company_name", empresa).upper()
                cnpj = data.get("cnpj", "")
        except: pass

    # Montagem do Cupom
    cupom =  f"{'='*40}\n"
    cupom += f"{empresa.center(40)}\n"
    if cnpj: cupom += f"CNPJ: {cnpj.center(40)}\n"
    cupom += f"{'='*40}\n"
    cupom += f"CUPOM DE VENDA: #{venda_id}\n"
    cupom += f"{'-'*40}\n"
    cupom += f"{'PRODUTO'.ljust(20)} {'QTD'.center(5)} {'TOTAL'.rjust(13)}\n"
    
    for it in itens:
        nome = it['name'][:18] # corta nome se for muito longo
        linha = f"{nome.ljust(20)} {str(it['qty']).center(5)} {it['price']*it['qty']:>13.2f}\n"
        cupom += linha
        
    cupom += f"{'-'*40}\n"
    cupom += f"TOTAL: R$ {total:>30.2f}\n"
    cupom += f"{'='*40}\n"
    cupom += f"{'Obrigado pela preferência!'.center(40)}\n"
    cupom += f"{'='*40}\n"
    
    return cupom