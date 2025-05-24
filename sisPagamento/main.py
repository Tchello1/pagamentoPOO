import streamlit as st
import sys
import os

# Adiciona o diretório atual ao path para permitir importações
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Importa as páginas existentes
from frontend.streamlit_app import mostrar_interface_pagamento
from frontend.dashboard import mostrar_dashboard
from usuarios.usuario import Usuario  # Certifique-se que está em usuarios/usuario.py

# Usuário admin estático para testes
usuario_admin = Usuario("admin", "1234", tipo="admin")

def autenticar_usuario(username, senha):
    if username == usuario_admin.username and usuario_admin.validar_senha(senha):
        return usuario_admin
    return None

def main():
    st.set_page_config(
        page_title="Fintech Payments",
        page_icon="💳",
        layout="wide"
    )

    # Inicializa o estado de sessão
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = None

    with st.sidebar:
        st.title("📋 Menu")

        if "pagina" not in st.session_state:
            st.session_state["pagina"] = "Realizar Pagamento"

        # Menu dinâmico conforme login
        opcoes_menu = []
        if st.session_state["usuario"] is None:
            opcoes_menu = ["Realizar Pagamento"]
        elif st.session_state["usuario"].tipo == "admin":
            opcoes_menu = ["Dashboard Analítico"]

        if opcoes_menu:
            pagina = st.radio(
                "Escolha uma opção:",
                opcoes_menu,
                index=opcoes_menu.index(st.session_state["pagina"]) if st.session_state["pagina"] in opcoes_menu else 0
            )
            st.session_state["pagina"] = pagina

        st.markdown("---")
        st.caption("© 2025 Fintech Payments")

    # Página: Realizar Pagamento com abas
    if st.session_state["pagina"] == "Realizar Pagamento":
        st.title("💳 Sistema de Pagamento")

        aba_pagamento, aba_login = st.tabs(["💳 Pagamento", "🔐 Login Admin(login:admin - senha:1234)"])

        with aba_pagamento:
            mostrar_interface_pagamento()

        with aba_login:
            if st.session_state["usuario"] is None:
                with st.form("form_login"):
                    username = st.text_input("Usuário")
                    senha = st.text_input("Senha", type="password")
                    if st.form_submit_button("Entrar"):
                        usuario = autenticar_usuario(username, senha)
                        if usuario:
                            st.session_state["usuario"] = usuario
                            st.success("✅ Login realizado com sucesso!")
                            st.session_state["pagina"] = "Dashboard Analítico"
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha inválidos.")
            else:
                st.info(f"👤 Logado como: **{st.session_state['usuario'].username}**")
                if st.button("Logout"):
                    st.session_state["usuario"] = None
                    st.session_state["pagina"] = "Realizar Pagamento"
                    st.success("Logout realizado com sucesso.")
                    st.rerun()

    # Página: Dashboard (restrita)
    elif st.session_state["pagina"] == "Dashboard Analítico":
        if st.session_state["usuario"] and st.session_state["usuario"].tipo == "admin":
            mostrar_dashboard()
        else:
            st.warning("⚠️ Acesso restrito. Faça login como administrador na aba 'Login Admin'.")

if __name__ == "__main__":
    main()
