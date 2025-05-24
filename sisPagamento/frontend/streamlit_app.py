import streamlit as st
from datetime import datetime
import time
import uuid
from pagamentos.cartao_credito import CartaoCredito
from pagamentos.paypal import PayPal
from pagamentos.transferencia_bancaria import TransferenciaBancaria
from banco.operacoes import BancoDados
from util.email import *
import hashlib
#import util.email



def mostrar_interface_pagamento():
    st.title("💳 Sistema de Pagamentos Fintech")
    
    metodo = st.radio(
        "Selecione o método de pagamento:",
        ("Cartão de Crédito", "PayPal", "Transferência Bancária")
    )
    
    valor = st.number_input("Valor do Pagamento:", min_value=0.01, step=0.01, format="%.2f")
    
    if metodo == "Cartão de Crédito":
        with st.form("form_cartao"):
            col1, col2 = st.columns(2)
            
            with col1:
                numero = st.text_input("Número do Cartão:", placeholder="1234 5678 9012 3456")
                titular = st.text_input("Nome no Cartão:")
            
            with col2:
                validade = st.text_input("Data de Validade (MM/AA):", placeholder="MM/AA")
                cvv = st.text_input("CVV:", placeholder="123", max_chars=3)
            
            if st.form_submit_button("Pagar"):
                processar_cartao(numero, titular, validade, cvv, valor)
        with st.expander("🔍 Ver histórico por número do cartão"):
            num_cartao_busca = st.text_input("Digite o número completo(sem espaço) do cartão (para busca segura):", type="password")
            if st.button("Buscar transações com cartão"):
                if num_cartao_busca:
                    resultados = BancoDados().buscar_transacoes_por_hash_cartao(num_cartao_busca)
                    if resultados:
                        st.subheader("Transações encontradas:")
                        for t in resultados:
                            st.write(f"🕒 {t['data_transacao'].strftime('%d/%m/%Y %H:%M:%S')}")
                            st.write(f"💰 Valor: R$ {t['valor']:.2f}")
                            st.write(f"📇 Cartão: {t['dados_mascarados'].get('numero', 'Desconhecido')}")
                            st.markdown("---")
                    else:
                        st.warning("Nenhuma transação encontrada.")
                else:
                    st.warning("Informe o número completo do cartão.")
    
    #testando
    elif metodo == "PayPal":
        with st.form("form_paypal"):
            email = st.text_input("E-mail do PayPal:")
            senha = st.text_input("Senha:", type="password")

            col1, col2 = st.columns(2)
            enviar = col1.form_submit_button("Pagar com PayPal")
            ver_historico = col2.form_submit_button("Ver Histórico")

            if enviar:
                processar_paypal(email, senha, valor)

            elif ver_historico:
                transacoes = BancoDados().buscar_transacoes_por_email(email)
                if transacoes:
                    st.subheader("📜 Histórico de Transações PayPal")
                    for transacao in transacoes:
                        st.markdown(f"""
                        - **ID**: {transacao['id_transacao']}
                        - **Valor**: R$ {transacao['valor']:.2f}
                        - **Status**: {transacao['status']}
                        - **Data**: {transacao['data_transacao'].strftime('%d/%m/%Y %H:%M:%S')}
                        """)
                else:
                    st.info("Nenhuma transação encontrada para este e-mail.")
                    
    
    elif metodo == "Transferência Bancária":
        with st.form("form_transferencia"):
            codigo_banco = st.text_input("Código do Banco:")
            conta_origem = st.text_input("Conta de Origem (8 dígitos):", max_chars=8)
            conta_destino = st.text_input("Conta de Destino (8 dígitos):", max_chars=8)
            
            if st.form_submit_button("Realizar Transferência"):
                processar_transferencia(codigo_banco, conta_origem, conta_destino, valor)
        with st.expander("🔍 Ver histórico por conta de origem"):
            conta_busca = st.text_input("Digite a conta de origem para buscar histórico:")
            if st.button("Buscar transferências"):
                if conta_busca:
                    resultados = BancoDados().buscar_transferencias_por_conta_origem(conta_busca)
                    if resultados:
                        st.subheader(f"Transações encontradas para conta {conta_busca}:")
                        for t in resultados:
                            st.write(f"🕒 {t['data_transacao'].strftime('%d/%m/%Y %H:%M:%S')}")
                            st.write(f"💰 Valor: R$ {t['valor']:.2f}")
                            st.write(f"📤 Conta Origem: {t['detalhes'].get('conta_origem')}")
                            st.write(f"📥 Conta Destino: {t['detalhes'].get('conta_destino')}")
                            st.markdown("---")
                    else:
                        st.warning("Nenhuma transação encontrada.")
                else:
                    st.warning("Informe uma conta de origem.")

def gerar_hash_cartao(numero_cartao: str) -> str:
    return hashlib.sha256(numero_cartao.encode('utf-8')).hexdigest()

def processar_cartao(numero, titular, validade, cvv, valor):
    with st.spinner("Processando pagamento..."):
        numero = ''.join(filter(str.isdigit, numero))  # limpa espaços e traços

        cartao = CartaoCredito(
            numero=numero,
            titular=titular,
            validade=validade,
            cvv=cvv
        )

        resultado = cartao.processar_pagamento(valor)

        # Adiciona hash do cartão nos detalhes para histórico
        hash_cartao = gerar_hash_cartao(numero)
        resultado.setdefault("detalhes", {})
        resultado["detalhes"]["hash_cartao"] = hash_cartao

        # Preenche dados obrigatórios caso não venham do processador
        resultado.setdefault("id_transacao", str(uuid.uuid4()))
        resultado.setdefault("metodo", "Cartão de Crédito")
        resultado.setdefault("valor", valor if valor is not None else 0.0)
        resultado.setdefault("status", resultado.get("status", "Desconhecido"))
        resultado.setdefault("data_transacao", datetime.now())
        resultado.setdefault("dados_mascarados", resultado.get("dados_mascarados", {}))

        BancoDados().salvar_transacao(resultado)
        mostrar_resultado(resultado)


def processar_paypal(email, senha, valor):
    with st.spinner("Processando pagamento via PayPal..."):
        paypal = PayPal(email=email, senha=senha)
        resultado = paypal.processar_pagamento(valor)
        resultado["id_transacao"] = str(uuid.uuid4())
        #st.session_state.resultado_pagamento = resultado #gambiarra
        
        BancoDados().salvar_transacao(resultado)
        mostrar_resultado(resultado)

def processar_transferencia(codigo_banco, conta_origem, conta_destino, valor):
    with st.spinner("Processando transferência bancária..."):
        transferencia = TransferenciaBancaria(
            codigo_banco=codigo_banco,
            conta_origem=conta_origem,
            conta_destino=conta_destino
        )
        
        resultado = transferencia.processar_pagamento(valor)
        resultado["id_transacao"] = str(uuid.uuid4())
        #st.session_state.resultado_pagamento = resultado #gambiarra
        BancoDados().salvar_transacao(resultado)
        mostrar_resultado(resultado)

def mostrar_resultado(resultado):
    time.sleep(1)  # Simular tempo de processamento
    
    st.subheader("Resultado do Pagamento")
    
    if resultado["status"] == "Aprovado":
        st.success("✅ Pagamento Aprovado!")
        #email_destino = st.text_input("Informe o e-mail para envio do comprovante:")


    else:
        st.error("❌ Pagamento Recusado")
    
    st.write(f"**ID da Transação:** {resultado['id_transacao']}")
    st.write(f"**Método:** {resultado['metodo']}")
    st.write(f"**Valor:** R$ {resultado['valor']:.2f}")
    st.write(f"**Data/Hora:** {resultado['data_transacao'].strftime('%d/%m/%Y %H:%M:%S')}")
    """"
    st.subheader("Detalhes (Mascarados)")
    st.json(resultado['dados_mascarados'])
    """
    
    if "mensagem" in resultado:
        st.warning(resultado["mensagem"])


#gambiarra

# Mostrar campo de envio de comprovante no final, se o pagamento foi feito
"""
if "resultado_pagamento" in st.session_state:
    resultado = st.session_state.resultado_pagamento

    st.subheader("Resultado do Pagamento")

    if resultado["status"] == "Aprovado":
        st.success("✅ Pagamento Aprovado!")

        st.write(f"**ID da Transação:** {resultado['id_transacao']}")
        st.write(f"**Método:** {resultado['metodo']}")
        st.write(f"**Valor:** R$ {resultado['valor']:.2f}")
        st.write(f"**Data/Hora:** {resultado['data_transacao'].strftime('%d/%m/%Y %H:%M:%S')}")

        st.markdown("---")
        st.subheader("✉️ Enviar comprovante por e-mail")

        email_destino = st.text_input("E-mail destinatário:")
        if st.button("Enviar Comprovante"):
            if email_destino:
                corpo_email = (
                    f"Comprovante de Pagamento\n\n"
                    f"ID da Transação: {resultado['id_transacao']}\n"
                    f"Método: {resultado['metodo']}\n"
                    f"Valor: R$ {resultado['valor']:.2f}\n"
                    f"Data/Hora: {resultado['data_transacao'].strftime('%d/%m/%Y %H:%M:%S')}\n"
                )
                sucesso = enviar_email_relatorio(email_destino, "Comprovante de Pagamento", corpo_email)
                if sucesso:
                    st.success("📧 Comprovante enviado com sucesso!")
                else:
                    st.error("❌ Erro ao enviar o comprovante.")
            else:
                st.warning("Por favor, insira um e-mail válido.")
    
    else:
        st.error("❌ Pagamento Recusado")
"""