import os
import time
import configparser

class ACBrEngine:
    # Pastas onde o ACBr fica "ouvindo"
    DIR_ENTRADA = r"C:\ACBrMonitorPLUS\ENT.TXT"
    DIR_SAIDA = r"C:\ACBrMonitorPLUS\SAI.TXT"

    @staticmethod
    def enviar_comando(comando):
        """
        Escreve o comando no arquivo de entrada do ACBr.
        Ex: NFE.StatusServico
        """
        try:
            # 1. Limpa resposta anterior se existir
            if os.path.exists(ACBrEngine.DIR_SAIDA):
                os.remove(ACBrEngine.DIR_SAIDA)

            # 2. Envia o comando
            with open(ACBrEngine.DIR_ENTRADA, 'w', encoding='ansi') as f:
                f.write(comando + "\n")

            return True
        except Exception as e:
            print(f"Erro ao comunicar com ACBr: {e}")
            return False

    @staticmethod
    def ler_resposta(timeout=10):
        """
        Fica esperando o arquivo SAI.TXT aparecer com a resposta.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if os.path.exists(ACBrEngine.DIR_SAIDA):
                try:
                    # Dá um tempinho para o arquivo terminar de ser escrito
                    time.sleep(0.5) 
                    with open(ACBrEngine.DIR_SAIDA, 'r', encoding='ansi') as f:
                        resposta = f.read()
                    
                    # Limpa para a próxima
                    os.remove(ACBrEngine.DIR_SAIDA)
                    
                    return resposta
                except:
                    pass # Arquivo pode estar bloqueado ainda
            time.sleep(1)
        
        return "ERRO: Sem resposta do ACBr (Timeout)"