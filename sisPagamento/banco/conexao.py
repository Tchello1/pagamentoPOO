import sqlite3
import os
from pathlib import Path

def criar_conexao(db_path: str = None):
    """Cria e retorna uma conexão com o banco de dados"""
    if db_path is None:
        db_path = str(Path(__file__).parent.parent / "data" / "transacoes.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    return sqlite3.connect(db_path)

""""
def criar_conexao_usuarios(db_path: str = None):
    if db_path is None:
        db_path = str(Path(__file__).parent.parent / "data" / "usuarios.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)
"""
