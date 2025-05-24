import hashlib
from datetime import datetime
#futuro
################NÃO USO#####################################
class Usuario:
    def __init__(self, username: str, senha: str, tipo: str = "comum"):
        self.username = username
        self.senha_hash = self.gerar_hash_senha(senha)
        self.tipo = tipo  
        self.data_criacao = datetime.now()

    def gerar_hash_senha(self, senha: str) -> str:
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()

    def validar_senha(self, senha_digitada: str) -> bool:
        return self.gerar_hash_senha(senha_digitada) == self.senha_hash

    def __repr__(self):
        return f"Usuario(username={self.username}, tipo={self.tipo}, criado_em={self.data_criacao})"
