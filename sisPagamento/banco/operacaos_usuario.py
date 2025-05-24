'''
from typing import Optional
from .conexao import criar_conexao_usuarios
import sqlite3
import json

class BancoDadosUsuario:
    def __init__(self):
        self._inicializar_banco()
    
    def _inicializar_banco(self):
        with criar_conexao_usuarios() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    username TEXT PRIMARY KEY,
                    senha_hash TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    data_criacao TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def salvar_usuario(self, usuario):
        with criar_conexao_usuarios() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO usuarios
                (username, senha_hash, tipo, data_criacao)
                VALUES (?, ?, ?, ?)
            """, (
                usuario.username,
                usuario.senha_hash,
                usuario.tipo,
                usuario.data_criacao.isoformat()
            ))
            conn.commit()
    
    def obter_usuario(self, username: str) -> Optional[dict]:
        with criar_conexao_usuarios() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def listar_usuarios(self) -> list[dict]:
        with criar_conexao_usuarios() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios ORDER BY username")
            return [dict(row) for row in cursor.fetchall()]
'''