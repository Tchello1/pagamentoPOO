import streamlit as st
import pandas as pd
import plotly.express as px
from sisPagamento.banco.operacoes import BancoDados
from util.email import enviar_email_relatorio  # sua função no backend

def mostrar_dashboard():

    col1, col2 = st.columns([8, 1])
    with col1:
        st.markdown(f"👤 Logado como: **{st.session_state['usuario'].username}**")
    with col2:
        if st.button("Logout"):
            st.session_state["usuario"] = None
            st.success("Logout realizado com sucesso.")
            st.session_state["pagina"] = "Realizar Pagamento"
            st.rerun()
    st.title("📊 Dashboard Analítico")
    
    banco = BancoDados()
    transacoes = banco.obter_transacoes()
    estatisticas = banco.obter_estatisticas()
    
    if not transacoes:
        st.warning("Nenhuma transação encontrada no banco de dados.")
        return
    
    df = pd.DataFrame(transacoes)
    df['data_transacao'] = pd.to_datetime(df['data_transacao'])
    
    aba_analise, aba_email = st.tabs(["Análise", "Enviar por E-mail"])

    with aba_analise:
        # ... seu código atual do dashboard aqui ...
        st.subheader("Estatísticas Gerais")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total de Transações", estatisticas['total_transacoes'])
        col2.metric("Transações Aprovadas", estatisticas['transacoes_aprovadas'])
        col3.metric("Transações Recusadas", estatisticas['transacoes_recusadas'])
        col4.metric("Taxa de Aprovação", f"{estatisticas['taxa_aprovacao']:.1%}")
        
        st.metric("Valor Total Processado", f"R$ {estatisticas['valor_total_processado']:,.2f}")
        
        fig1 = px.pie(
            df['metodo'].value_counts().reset_index(),
            names='metodo',
            values='count',
            hole=0.3
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.bar(
            df['status'].value_counts().reset_index(),
            x='status',
            y='count',
            color='status'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        fig3 = px.bar(
            df.groupby('metodo')['valor'].sum().reset_index(),
            x='metodo',
            y='valor',
            color='metodo'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        st.subheader("Histórico Completo")
        st.dataframe(df.sort_values('data_transacao', ascending=False))


    with aba_email:
        st.subheader("Enviar Relatório do Dashboard por E-mail")
        email_destino = st.text_input("E-mail destinatário:")
        if st.button("Enviar E-mail"):
            if email_destino:
                # Aqui você pode gerar um resumo simples (exemplo em texto)
                resumo = (
                    f"Total de Transações: {estatisticas['total_transacoes']}\n"
                    f"Transações Aprovadas: {estatisticas['transacoes_aprovadas']}\n"
                    f"Transações Recusadas: {estatisticas['transacoes_recusadas']}\n"
                    f"Taxa de Aprovação: {estatisticas['taxa_aprovacao']:.1%}\n"
                    f"Valor Total Processado: R$ {estatisticas['valor_total_processado']:,.2f}\n"
                )
                sucesso = enviar_email_relatorio(email_destino, "Relatório do Dashboard Analítico", resumo)
                if sucesso:
                    st.success("E-mail enviado com sucesso!")
                else:
                    st.error("Erro ao enviar o e-mail.")
            else:
                st.warning("Por favor, insira um e-mail válido.")

    
