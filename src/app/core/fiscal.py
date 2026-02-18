# Arquivo: src/app/core/fiscal.py
import requests
import json
import logging

# CONFIGURAÇÕES (Depois você troca pela sua chave real)
API_KEY = "SUA_TOKEN_DA_FOCUS_NFE_AQUI"
AMBIENTE = "homologacao" # Use 'producao' quando for valer
URL_BASE = "https://api.focusnfe.com.br/v2" if AMBIENTE == "producao" else "https://homologacao.focusnfe.com.br/v2"

def emitir_nfce(venda_id, total, itens, cpf_cliente=None):
    """
    Envia os dados da venda para a API fiscal e retorna o status.
    """
    logging.info(f"Iniciando emissão NFC-e para Venda {venda_id}")
    
    # 1. Montar os dados da nota
    dados_nota = {
        "natureza_operacao": "Venda ao Consumidor",
        "data_emissao": "hoje", # A API assume hoje se omitido
        "forma_pagamento": "Dinheiro", # Você pode puxar isso dinamicamente da venda
        "items": []
    }

    # Adiciona o CPF se o cliente pediu
    if cpf_cliente:
        dados_nota["cliente"] = {"cpf": cpf_cliente}

    # Adiciona os produtos
    for item in itens:
        dados_nota["items"].append({
            "codigo": str(item.produto_id),
            "descricao": item.nome_produto,
            "unidade": "UN",
            "quantidade": item.quantidade,
            "valor_unitario": item.preco_unitario,
            "ncm": "99999999" # IMPORTANTE: Você precisa ter o NCM no cadastro do produto!
        })

    # 2. Enviar para a API
    url = f"{URL_BASE}/nfce?ref={venda_id}"
    
    try:
        response = requests.post(url, auth=(API_KEY, ""), json=dados_nota, timeout=10)
        
        if response.status_code in [200, 201, 202]:
            retorno = response.json()
            logging.info(f"Nota enviada! Status: {retorno.get('status')}")
            return {"sucesso": True, "mensagem": "Nota em processamento", "dados": retorno}
        else:
            logging.error(f"Erro ao emitir: {response.text}")
            return {"sucesso": False, "mensagem": f"Erro na SEFAZ: {response.text}"}
            
    except Exception as e:
        logging.error(f"Erro de conexão: {e}")
        return {"sucesso": False, "mensagem": "Sem internet ou erro de conexão"}