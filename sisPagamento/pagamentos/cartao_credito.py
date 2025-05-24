from datetime import datetime
from .forma_pagamento import FormaPagamento
from sisPagamento.util import seguranca
from typing import Dict
class CartaoCredito(FormaPagamento):
    def __init__(self, numero: str, titular: str, validade: str, cvv: str):
        super().__init__()
        self.numero = numero
        self.titular = titular
        self.validade = validade
        self.cvv = cvv
        self.metodo = "Cartão de Crédito"
    
    def processar_pagamento(self, valor: float) -> Dict:
        if not self.validar():
            self.status = "Recusado"
            return {"status": self.status, "mensagem": "Validação do cartão falhou"}
        
        #self.status = self.simular_processamento()
        self.status = 'Aprovado'
        return {
            "metodo": self.metodo,
            "valor": valor,
            "status": self.status,
            "data_transacao": self.transaction_date,
            "detalhes": {
                "titular": self.titular,
                "ultimos_quatro": self.numero[-4:]
            },
            "dados_mascarados": {
                "numero_cartao": seguranca.mascarar_dados(self.numero, 4),
                "cvv": seguranca.mascarar_dados(self.cvv)
            }
        }
    
    def validar(self) -> bool:
        # Verifica se o CVV é numérico e tem 3 dígitos
        if len(self.cvv) != 3 or not self.cvv.isdigit():
            return False

        # Verifica se o número do cartão tem 16 dígitos
        if not self.numero.isdigit() or len(self.numero) != 16:
            return False

        # Verifica se o nome do titular não está vazio
        if not self.titular.strip():
            return False

        # Verifica validade no formato MM/AA e se é futura
        try:
            mes, ano = self.validade.split('/')
            ano_atual = datetime.now().strftime("%y")
            mes_atual = datetime.now().strftime("%m")

            if ano < ano_atual:
                return False
            if ano == ano_atual and mes < mes_atual:
                return False
        except:
            return False

        return True
