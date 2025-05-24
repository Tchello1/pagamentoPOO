from .forma_pagamento import FormaPagamento
from sisPagamento.util import seguranca
from typing import Dict

class TransferenciaBancaria(FormaPagamento):
    def __init__(self, codigo_banco: str, conta_origem: str, conta_destino: str):
        super().__init__()
        self.codigo_banco = codigo_banco
        self.conta_origem = conta_origem
        self.conta_destino = conta_destino
        self.metodo = "Transferência Bancária"
    
    def processar_pagamento(self, valor: float) -> Dict:
        if not self.validar():
            self.status = "Recusado"
            return {
            "metodo": self.metodo,
            "valor": valor,
            "status": self.status,
            "data_transacao": self.transaction_date,
            "detalhes": {
                "codigo_banco": self.codigo_banco or "",
                "conta_origem": self.conta_origem or "",
                "conta_destino": self.conta_destino or ""
            },
            "dados_mascarados": {
                "conta_origem": seguranca.mascarar_dados(self.conta_origem, 2) if self.conta_origem else "",
                "conta_destino": seguranca.mascarar_dados(self.conta_destino, 2) if self.conta_destino else ""
            },
            "mensagem": "Validação da transferência falhou"
        }
        
        self.status = self.simular_processamento()
        
        return {
            "metodo": self.metodo,
            "valor": valor,
            "status": self.status,
            "data_transacao": self.transaction_date,
            "detalhes": {
                "codigo_banco": self.codigo_banco,
                "conta_origem": self.conta_origem,
                "conta_destino": self.conta_destino
            },
            "dados_mascarados": {
                "conta_origem": seguranca.mascarar_dados(self.conta_origem, 2),
                "conta_destino": seguranca.mascarar_dados(self.conta_destino, 2)
            }
        }
    
    def validar(self) -> bool:
        return (len(self.conta_origem) == 8 and self.conta_origem.isdigit() and
                len(self.conta_destino) == 8 and self.conta_destino.isdigit())