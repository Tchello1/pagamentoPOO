from abc import ABC, abstractmethod
from datetime import datetime
import random
from typing import Dict

class FormaPagamento(ABC):
    def __init__(self):
        self.id = None
        self.status = "Pendente"
        self.transaction_date = datetime.now()
    
    @abstractmethod
    def processar_pagamento(self, valor: float) -> Dict:
        pass
    
    @abstractmethod
    def validar(self) -> bool:
        pass
    
    def simular_processamento(self) -> str:
        """Simula aprovação (80%) ou recusa (20%) aleatória"""
        return "Aprovado" if random.random() < 0.8 else "Recusado"