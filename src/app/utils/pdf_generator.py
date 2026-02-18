import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class PDFGenerator:
    
    @staticmethod
    def _draw_header(c, title, empresa_nome="BERTOLINI ERP SYSTEM"):
        """Função auxiliar para desenhar cabeçalho padrão em todos os documentos"""
        width, height = A4
        # Fundo do cabeçalho
        c.setFillColor(colors.darkblue)
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        
        # Textos
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(30, height - 35, empresa_nome)
        
        c.setFont("Helvetica", 10)
        c.drawString(30, height - 55, f"{title}")
        c.drawString(30, height - 70, f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Reseta cor para preto para o corpo do texto
        c.setFillColor(colors.black)
        return height - 100 # Retorna posição Y onde o conteúdo deve começar

    @staticmethod
    def gerar_dre_pdf(dados_dre, filename="Relatorio_DRE.pdf"):
        """Gera o PDF do Financeiro"""
        c = canvas.Canvas(filename, pagesize=A4)
        y = PDFGenerator._draw_header(c, "RELATÓRIO FINANCEIRO (DRE)")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Demonstrativo do Resultado do Exercício")
        y -= 40
        
        c.setFont("Helvetica", 12)
        total_rec = 0
        total_desp = 0
        
        for linha in dados_dre:
            tipo = linha.get('tipo', 'neutro')
            valor = linha.get('valor', 0.0)
            
            # Cores dinâmicas
            if tipo == 'receita': 
                c.setFillColor(colors.green)
                total_rec += valor
            elif tipo == 'despesa': 
                c.setFillColor(colors.red)
                total_desp += valor
            else: 
                c.setFillColor(colors.black)
                
            c.drawString(50, y, f"{linha['descricao']}")
            # Alinha valor à direita (simulado)
            c.drawRightString(500, y, f"R$ {valor:,.2f}")
            
            # Linha pontilhada visual
            c.setStrokeColor(colors.lightgrey)
            c.line(50, y-5, 500, y-5)
            
            y -= 25
            
            if y < 50: 
                c.showPage()
                y = 800 
            
        # Totalizador
        y -= 15
        lucro = total_rec - total_desp
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "RESULTADO LÍQUIDO:")
        
        cor_final = colors.green if lucro >= 0 else colors.red
        c.setFillColor(cor_final)
        c.drawRightString(500, y, f"R$ {lucro:,.2f}")
        
        c.save()
        return os.path.abspath(filename)

    @staticmethod
    def gerar_inventario_pdf(produtos, filename="Relatorio_Estoque.pdf"):
        """Gera o PDF do Estoque"""
        c = canvas.Canvas(filename, pagesize=A4)
        y = PDFGenerator._draw_header(c, "POSIÇÃO DE ESTOQUE")
        
        # Cabeçalho da Tabela
        c.setFillColor(colors.lightgrey)
        c.rect(40, y-5, 520, 20, fill=True, stroke=False)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "PRODUTO")
        c.drawString(350, y, "QTD")
        c.drawString(450, y, "VALOR UNIT.")
        
        y -= 30
        c.setFont("Helvetica", 10)
        
        for p in produtos:
            # Espera tupla: (id, nome, custo, preco, estoque, min)
            nome = str(p[1])
            qtd = str(p[4])
            try: preco = f"R$ {float(p[3]):.2f}"
            except: preco = "R$ 0.00"
            
            c.drawString(50, y, nome[:55]) # Corta nomes muito longos
            c.drawString(350, y, qtd)
            c.drawString(450, y, preco)
            
            y -= 20
            if y < 50:
                c.showPage()
                y = 800
                
        c.save()
        return os.path.abspath(filename)

    @staticmethod
    def gerar_certificado_qualidade(empresa, lote_info, resultados):
        """Gera o Laudo Técnico do Laboratório"""
        # Garante pasta
        folder = "laudos_qualidade"
        if not os.path.exists(folder): os.makedirs(folder)
        filename = f"{folder}/Laudo_{lote_info['lote_num']}.pdf"
        
        c = canvas.Canvas(filename, pagesize=A4)
        y = PDFGenerator._draw_header(c, "CERTIFICADO DE ANÁLISE (COA)", empresa['razao_social'])
        
        # Dados do Lote
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"PRODUTO: {lote_info['produto']}")
        y -= 20
        c.drawString(50, y, f"LOTE: {lote_info['lote_num']}")
        y -= 40
        
        # Tabela de Resultados
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "PARÂMETRO")
        c.drawString(250, y, "ESPECIFICAÇÃO")
        c.drawString(400, y, "RESULTADO")
        c.line(50, y-5, 550, y-5)
        y -= 25
        
        c.setFont("Helvetica", 10)
        for res in resultados:
            c.setFillColor(colors.black)
            c.drawString(50, y, str(res['param']))
            c.drawString(250, y, str(res['spec']))
            
            # Status Colorido
            status = res['status']
            if "APROVADO" in status: c.setFillColor(colors.green)
            elif "REPROVADO" in status: c.setFillColor(colors.red)
            else: c.setFillColor(colors.orange)
            
            c.drawString(400, y, f"{res['medido']} ({status})")
            y -= 20
            
        # Assinatura
        y -= 60
        c.setStrokeColor(colors.black)
        c.line(50, y, 250, y)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(50, y-10, "Responsável Técnico - CRQ IV Região")
        c.drawString(50, y-20, "Documento assinado digitalmente pelo sistema Bertolini ERP")
        
        c.save()
        return os.path.abspath(filename)

    @staticmethod
    def gerar_orcamento_b2b(dados_empresa=None, dados_cliente=None, itens=None):
        """
        Gera Orçamento/OS (Substitui o antigo FPDF).
        Isso garante que o botão 'Emitir Nota/Recibo' do PDV funcione.
        """
        # Garante pasta
        folder = "documentos"
        if not os.path.exists(folder): os.makedirs(folder)
        filename = f"{folder}/Doc_{datetime.now().strftime('%H%M%S')}.pdf"
        
        c = canvas.Canvas(filename, pagesize=A4)
        
        # Dados padrão
        emp = dados_empresa or {"razao_social": "BERTOLINI ERP", "cnpj": "00.000.000/0001-00"}
        cli = dados_cliente or {"nome": "Consumidor Final"}
        lista_itens = itens or []

        y = PDFGenerator._draw_header(c, "COMPROVANTE DE VENDA / ORÇAMENTO", emp['razao_social'])
        
        # Dados Cliente
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Cliente: {cli['nome']}")
        y -= 30
        
        # Tabela Itens
        c.setFillColor(colors.lightgrey)
        c.rect(40, y-5, 520, 20, fill=True, stroke=False)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "ITEM")
        c.drawString(300, y, "QTD")
        c.drawString(380, y, "UNIT")
        c.drawString(480, y, "TOTAL")
        y -= 25
        
        c.setFont("Helvetica", 10)
        total_geral = 0
        
        for item in lista_itens:
            nome = item.get('name', item.get('nome', 'Item'))
            qtd = item.get('qty', item.get('qtd', 1))
            preco = item.get('price', item.get('preco', 0))
            sub = qtd * preco
            total_geral += sub
            
            c.drawString(50, y, str(nome)[:40])
            c.drawString(300, y, str(qtd))
            c.drawString(380, y, f"{preco:.2f}")
            c.drawString(480, y, f"{sub:.2f}")
            y -= 20
            
            if y < 100: c.showPage(); y = 800
            
        # Total Final
        y -= 10
        c.line(40, y, 560, y)
        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(520, y, f"TOTAL: R$ {total_geral:.2f}")
        
        c.save()
        return os.path.abspath(filename)

# --- PONTE DE COMPATIBILIDADE (CORREÇÃO DO ERRO) ---
# Esta função solta permite que os arquivos antigos chamem 'gerar_pdf_os' 
# sem saber que agora ela usa o motor novo.
def gerar_pdf_os(dados_empresa=None, dados_cliente=None, itens=None):
    return PDFGenerator.gerar_orcamento_b2b(dados_empresa, dados_cliente, itens)