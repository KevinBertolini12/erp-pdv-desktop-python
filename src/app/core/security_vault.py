from cryptography.fernet import Fernet
import os

class SecurityVault:
    @staticmethod
    def gerar_chave_mestre():
        """Gera uma chave única para o cliente. Deve ser guardada a sete chaves!"""
        return Fernet.generate_key()

    @staticmethod
    def criptografar_arquivo(caminho_arquivo, chave):
        """Lê o banco de dados e gera uma versão blindada."""
        f = Fernet(chave)
        with open(caminho_arquivo, "rb") as file:
            dados_originais = file.read()
        
        dados_criptografados = f.encrypt(dados_originais)
        
        with open(caminho_arquivo + ".vault", "wb") as file:
            file.write(dados_criptografados)
        
        return caminho_arquivo + ".vault"

    @staticmethod
    def descriptografar_arquivo(caminho_vault, chave):
        """Restaura o banco de dados original a partir do arquivo blindado."""
        f = Fernet(chave)
        with open(caminho_vault, "rb") as file:
            dados_blindados = file.read()
        
        dados_restaurados = f.decrypt(dados_blindados)
        
        caminho_original = caminho_vault.replace(".vault", "")
        with open(caminho_original, "wb") as file:
            file.write(dados_restaurados)
            
        return caminho_original