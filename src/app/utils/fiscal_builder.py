class FiscalBuilder:
    @staticmethod
    def montar_nfe_ini(venda, emitente, cliente, produtos):
        """
        Gera o texto no formato INI do ACBr para NFe (Indústria/Atacado).
        """
        ini = []
        
        # --- CABEÇALHO ---
        ini.append('[Identificacao]')
        ini.append('NaturezaOperacao=VENDA DE MERCADORIA')
        ini.append('Modelo=55') # 55=NFe, 65=NFCe
        ini.append('Serie=1')
        ini.append(f'Numero={venda["id"]}')
        ini.append(f'Emissao={venda["data_emissao"]}') # d/m/y
        ini.append('Tipo=1') # 1=Saída
        
        # --- EMITENTE (Sua Empresa) ---
        ini.append('[Emitente]')
        ini.append(f'CNPJ={emitente["cnpj"]}')
        ini.append(f'IE={emitente["ie"]}')
        ini.append(f'xNome={emitente["razao_social"]}')
        ini.append(f'xFant={emitente["fantasia"]}')
        
        # --- DESTINATÁRIO (Cliente) ---
        ini.append('[Destinatario]')
        ini.append(f'CNPJ={cliente["cnpj_cpf"]}')
        ini.append(f'xNome={cliente["nome"]}')
        
        # --- PRODUTOS ---
        for i, prod in enumerate(produtos):
            n = i + 1
            ini.append(f'[Produto{n:03d}]')
            ini.append(f'cProd={prod["id"]}')
            ini.append(f'xProd={prod["nome"]}')
            ini.append(f'NCM={prod["ncm"]}') # O NCM que criamos no passo anterior!
            ini.append(f'CFOP=5102')
            ini.append(f'uCom=UN')
            ini.append(f'qCom={prod["quantidade"]}')
            ini.append(f'vUnCom={prod["preco_unitario"]}')
            ini.append(f'vProd={prod["total"]}')
            
            # Impostos (Simples Nacional é mais fácil, mas aqui vai o básico)
            ini.append(f'[ICMS{n:03d}]')
            ini.append('CSOSN=102') # Tributado pelo Simples
            ini.append('Origem=0')  # Nacional

        # --- TOTAIS ---
        ini.append('[Total]')
        ini.append(f'vNF={venda["total_final"]}')

        return "\n".join(ini)

    @staticmethod
    def montar_sat_ini(venda, produtos):
        """
        Gera o texto para o SAT (Varejo SP - Sharon Sport Bike).
        O comando é diferente: SAT.CriarCFe
        """
        # A lógica é similar, mas a estrutura do INI muda levemente para CFe
        # ... (simplificado para o exemplo)
        return f"[Identificacao]\nsignAC=...codigo_vinculacao..."