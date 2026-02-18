import xml.etree.ElementTree as ET
from datetime import datetime
import os

class FinanceEngine:
    """
    Motor Financeiro do Bertolini ERP.
    Responsável por cálculos de totais, troco e validações de pagamento.
    """
    @staticmethod
    def calcular_total(itens):
        """Calcula o valor total da lista de itens da venda."""
        return sum(item['qtd'] * item['preco'] for item in itens)

    @staticmethod
    def calcular_troco(total, valor_pago):
        """Calcula o troco, garantindo que não seja negativo."""
        return max(0, valor_pago - total)

    @staticmethod
    def formatar_moeda(valor):
        """Formata valores para o padrão brasileiro (R$)."""
        return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

class FiscalEngine:
    """
    Motor Fiscal responsável pela geração de arquivos XML (NFe 4.0).
    """
    @staticmethod
    def gerar_xml_venda(venda, itens, cliente_cnpj="00000000000000"):
        # Estrutura básica simplificada da NFe 4.0
        nfe = ET.Element("NFe", xmlns="http://www.portalfiscal.inf.br/nfe")
        infNFe = ET.SubElement(nfe, "infNFe", versao="4.00", Id=f"NFe{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Ide - Identificação (UF 35 para São Paulo)
        ide = ET.SubElement(infNFe, "ide")
        ET.SubElement(ide, "cUF").text = "35" 
        ET.SubElement(ide, "natOp").text = "VENDA"
        ET.SubElement(ide, "dhEmi").text = datetime.now().isoformat()
        
        # Emitente (Bertolini ERP)
        emit = ET.SubElement(infNFe, "emit")
        ET.SubElement(emit, "CNPJ").text = "CNPJ_DA_LOJA"
        ET.SubElement(emit, "xNome").text = "BERTOLINI ERP SISTEMAS"
        
        # Destinatário
        dest = ET.SubElement(infNFe, "dest")
        ET.SubElement(dest, "CNPJ").text = cliente_cnpj
        
        # Itens
        for i, item in enumerate(itens):
            det = ET.SubElement(infNFe, "det", nItem=str(i+1))
            prod = ET.SubElement(det, "prod")
            ET.SubElement(prod, "cProd").text = str(item['id'])
            ET.SubElement(prod, "xProd").text = item['nome']
            ET.SubElement(prod, "NCM").text = item.get('ncm', '00000000')
            ET.SubElement(prod, "qCom").text = f"{item['qtd']:.4f}"
            ET.SubElement(prod, "vUnCom").text = f"{item['preco']:.2f}"
            ET.SubElement(prod, "vProd").text = f"{(item['qtd']*item['preco']):.2f}"
            
        tree = ET.ElementTree(nfe)
        path = "notas_fiscais_xml"
        if not os.path.exists(path): 
            os.makedirs(path)
            
        filename = f"{path}/nfe_{datetime.now().strftime('%H%M%S')}.xml"
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        return filename