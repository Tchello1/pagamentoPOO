import uuid
from datetime import datetime
from typing import Dict

class Transacao:
    def __init__(self, metodo: str, valor: float, status: str, detalhes: Dict):
        self.id = str(uuid.uuid4())
        self.metodo = metodo
        self.valor = valor
        self.status = status
        self.data = datetime.now()
        self.detalhes = detalhes