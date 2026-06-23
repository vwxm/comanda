"""
auth.py — Autenticação de admin e estilo da sidebar
"""
import streamlit as st
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    hashlib.sha256("admin123".encode()).hexdigest()
)

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LOGO_PATH = os.path.join(_BASE_DIR, "logo.svg")


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def sidebar_estilo():
    # ── Logo no topo da sidebar (acima dos links de navegação) ──
    st.logo(_LOGO_PATH, size="large")

    # ── CSS geral da sidebar ──
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background: #111827 !important;
        border-right: 1px solid #1f2937;
    }
    [data-testid="stSidebar"] * { color: #e5e7eb !important; }

    /* Logo maior — seletor correto do Streamlit */
    [data-testid="stLogo"],
    [data-testid="stSidebarHeader"] img,
    [data-testid="stHeaderLogo"] img {
        height: 4.5rem !important;
        max-height: 4.5rem !important;
        width: auto !important;
        max-width: 100% !important;
        object-fit: contain !important;
    }
    [data-testid="stSidebarHeader"] {
        background: #111827 !important;
        border-bottom: 1px solid #1f2937 !important;
        padding: 1rem 0.75rem !important;
        height: auto !important;
        min-height: 6rem !important;
        align-items: center !important;
    }

    /* Label de seção */
    .sidebar-section {
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 1.4px !important;
        text-transform: uppercase !important;
        color: #9ca3af !important;
        padding: 0.9rem 0.2rem 0.3rem !important;
        display: block;
    }

    /* Links de navegação */
    [data-testid="stSidebarNav"] {
        padding-top: 0.5rem !important;
    }
    [data-testid="stSidebarNav"] a {
        border-radius: 8px !important;
        margin: 4px 8px !important;
        padding: 12px 16px !important;
        transition: background 0.15s !important;
    }
    [data-testid="stSidebarNav"] a span {
        font-size: 17px !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebarNav"] a:hover { background: #1f2937 !important; }
    [data-testid="stSidebarNav"] a[aria-selected="true"] { background: #1d4ed8 !important; }

    /* Badge admin */
    .admin-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #1d4ed8;
        color: #fff !important;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 0.25rem 0;
    }

    /* Botão Sair — contraste corrigido */
    [data-testid="stSidebar"] button {
        background: #1f2937 !important;
        border: 1px solid #374151 !important;
        color: #e5e7eb !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        transition: background 0.15s !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: #374151 !important;
        border-color: #4b5563 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] button p {
        color: #e5e7eb !important;
    }

    /* Selectbox da sidebar — contraste */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #1f2937 !important;
        border-color: #374151 !important;
    }
    .sidebar-divider {
        border: none;
        border-top: 1px solid #1f2937;
        margin: 0.75rem 0;
    }
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 260px;
        background: #111827;
        border-top: 1px solid #1f2937;
        padding: 0.6rem 1.2rem;
        font-size: 11px;
        color: #4b5563 !important;
        z-index: 998;
    }
    </style>
    """, unsafe_allow_html=True)


def sidebar_admin_status():
    if st.session_state.get("admin_logado"):
        st.sidebar.markdown(
            '<hr class="sidebar-divider"><span class="sidebar-section">Administração</span>',
            unsafe_allow_html=True
        )
        st.sidebar.markdown(
            '<div class="admin-badge">🔐 Admin logado</div>',
            unsafe_allow_html=True
        )
        if st.sidebar.button("Sair", key="btn_logout"):
            st.session_state.admin_logado = False
            st.rerun()

    st.sidebar.markdown(
        '<div class="sidebar-footer">Painel de Métricas v2.0</div>',
        unsafe_allow_html=True
    )


def requer_admin():
    if st.session_state.get("admin_logado"):
        return True

    st.markdown("""
    <div style='max-width:360px; margin:4rem auto; text-align:center;'>
        <div style='font-size:48px; margin-bottom:1rem;'>🔐</div>
        <h2 style='margin-bottom:0.25rem;'>Área restrita</h2>
        <p style='color:#6b7280; margin-bottom:2rem;'>
            Esta seção é exclusiva para administradores.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        senha  = st.text_input("Senha de administrador", type="password", key="input_senha_admin")
        entrar = st.button("Entrar", use_container_width=True)

    if entrar:
        if _hash(senha) == ADMIN_PASSWORD_HASH:
            st.session_state.admin_logado = True
            st.success("Acesso autorizado!")
            st.rerun()
        else:
            st.error("Senha incorreta.")

    return False