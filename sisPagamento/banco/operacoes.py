from typing import List, Dict
from .conexao import criar_conexao
import json
import sqlite3
from datetime import datetime
import hashlib
class BancoDados:
    def __init__(self):
        self._inicializar_banco()
    
    def _inicializar_banco(self):
        """Cria a tabela de transações se não existir"""
        with criar_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id TEXT PRIMARY KEY,
                    metodo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    status TEXT NOT NULL,
                    data_transacao TEXT NOT NULL,
                    detalhes TEXT,
                    dados_mascarados TEXT
                )
            """)
            conn.commit()
    
    def salvar_transacao(self, transacao: Dict):
        """Salva uma transação no banco de dados"""
        with criar_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transacoes 
                (id, metodo, valor, status, data_transacao, detalhes, dados_mascarados)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transacao.get("id_transacao"),
                transacao.get("metodo"),
                transacao.get("valor"),
                transacao.get("status"),
                transacao.get("data_transacao").isoformat(),
                json.dumps(transacao.get("detalhes", {})),
                json.dumps(transacao.get("dados_mascarados", {}))
            ))
            conn.commit()
    
    def obter_transacoes(self) -> List[Dict]:
        """Recupera todas as transações do banco de dados"""
        with criar_conexao() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacoes ORDER BY data_transacao DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas das transações"""
        with criar_conexao() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM transacoes")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM transacoes WHERE status = 'Aprovado'")
            aprovadas = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM transacoes WHERE status = 'Recusado'")
            recusadas = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(valor) FROM transacoes WHERE status = 'Aprovado'")
            valor_total = cursor.fetchone()[0] or 0
            
            return {
                "total_transacoes": total,
                "transacoes_aprovadas": aprovadas,
                "transacoes_recusadas": recusadas,
                "taxa_aprovacao": aprovadas / total if total > 0 else 0,
                "valor_total_processado": valor_total
            }

    def buscar_transacoes_por_email(self, email: str) -> List[Dict]:
        """Busca transações que contenham o e-mail no campo 'detalhes' (usado no PayPal)."""
        with criar_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacoes ORDER BY data_transacao DESC")
            linhas = cursor.fetchall()

        transacoes = []
        for linha in linhas:
            try:
                detalhes = json.loads(linha[5])  # coluna 'detalhes'
                if detalhes.get("email") == email:
                    transacao = {
                        "id_transacao": linha[0],
                        "metodo": linha[1],
                        "valor": float(linha[2]),
                        "status": linha[3],
                        "data_transacao": datetime.fromisoformat(linha[4]),
                        "detalhes": detalhes,
                        "dados_mascarados": json.loads(linha[6])
                    }
                    transacoes.append(transacao)
            except Exception as e:
                print(f"Erro ao processar linha do banco: {e}")
                continue

        return transacoes
    

    def buscar_transferencias_por_conta_origem(self, conta_origem: str) -> List[Dict]:
        """Busca transações de transferência filtrando pela conta de origem"""
        with criar_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacoes WHERE metodo = 'Transferência Bancária' ORDER BY data_transacao DESC")
            linhas = cursor.fetchall()

        transacoes = []
        for linha in linhas:
            try:
                detalhes = json.loads(linha[5])  # coluna 'detalhes'
                if detalhes.get("conta_origem") == conta_origem:
                    transacao = {
                        "id_transacao": linha[0],
                        "metodo": linha[1],
                        "valor": float(linha[2]),
                        "status": linha[3],
                        "data_transacao": datetime.fromisoformat(linha[4]),
                        "detalhes": detalhes,
                        "dados_mascarados": json.loads(linha[6])
                    }
                    transacoes.append(transacao)
            except Exception as e:
                print(f"Erro ao processar linha do banco: {e}")
                continue

        return transacoes
    
    def buscar_transacoes_por_hash_cartao(self, numero_cartao: str) -> List[Dict]:
        """Busca transações por hash do número do cartão de crédito"""
        hash_cartao = hashlib.sha256(numero_cartao.encode('utf-8')).hexdigest()
        
        with criar_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacoes WHERE metodo = 'Cartão de Crédito'")
            linhas = cursor.fetchall()

        transacoes = []
        for linha in linhas:
            try:
                detalhes = json.loads(linha[5])
                if detalhes.get("hash_cartao") == hash_cartao:
                    transacoes.append({
                        "id_transacao": linha[0],
                        "metodo": linha[1],
                        "valor": float(linha[2]),
                        "status": linha[3],
                        "data_transacao": datetime.fromisoformat(linha[4]),
                        "detalhes": detalhes,
                        "dados_mascarados": json.loads(linha[6])
                    })
            except Exception as e:
                print(f"Erro ao processar linha do banco: {e}")
                continue

        return transacoes



