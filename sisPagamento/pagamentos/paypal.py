from .forma_pagamento import FormaPagamento
from sisPagamento.util import seguranca
from typing import Dict

class PayPal(FormaPagamento):
    def __init__(self, email: str, senha: str):
        super().__init__()
        self.email = email
        self.senha = senha
        self.metodo = "PayPal"
    
    def processar_pagamento(self, valor: float) -> Dict:
        if not self.validar():
            self.status = "Recusado"
            return {
            "metodo": self.metodo,
            "valor": valor,
            "status": self.status,
            "data_transacao": self.transaction_date,
            "mensagem": "Validação do PayPal falhou",
            "detalhes": {
                "email": self.email
            },
            "dados_mascarados": {
                "senha": seguranca.mascarar_dados(self.senha)
            }
        }
        
        self.status = self.simular_processamento()
        
        return {
            "metodo": self.metodo,
            "valor": valor,
            "status": self.status,
            "data_transacao": self.transaction_date,
            "detalhes": {
                "email": self.email
            },
            "dados_mascarados": {
                "senha": seguranca.mascarar_dados(self.senha)
            }
        }
    
    def validar(self) -> bool:
        email_valido = '@' in self.email and '.' in self.email.split('@')[-1]
        senha_valida = bool(self.senha and self.senha.strip()) 
        return email_valido and senha_valida
