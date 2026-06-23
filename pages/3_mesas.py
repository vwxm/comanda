"""
Cadastro e status visual das mesas.
"""
import streamlit as st

from auth import requer_admin, sidebar_admin_status, sidebar_estilo
from crud import criar_mesa, liberar_mesa, listar_mesas, reservar_mesa

st.set_page_config(page_title="Mesas", page_icon=":chair:", layout="wide")

sidebar_estilo()
if not requer_admin():
    sidebar_admin_status()
    st.stop()
sidebar_admin_status()

st.title("Gestao de Mesas")

mesas = listar_mesas()

STATUS_VISUAL = {
    "livre": {
        "label": "Livre",
        "background": "#14532d",
        "border": "#22c55e",
    },
    "ocupada": {
        "label": "Ocupada",
        "background": "#7f1d1d",
        "border": "#dc2626",
    },
    "reservada": {
        "label": "Reservada",
        "background": "#713f12",
        "border": "#f59e0b",
    },
    "aguardando_pagamento": {
        "label": "Aguardando pagamento",
        "background": "#1e3a8a",
        "border": "#3b82f6",
    },
    "inativa": {
        "label": "Inativa",
        "background": "#374151",
        "border": "#6b7280",
    },
}

st.markdown("#### Status atual")

if not mesas:
    st.info("Nenhuma mesa cadastrada ainda.")
else:
    cols = st.columns(5)
    for i, mesa in enumerate(mesas):
        with cols[i % 5]:
            status = mesa["status"]
            visual = STATUS_VISUAL.get(status, STATUS_VISUAL["inativa"])
            st.markdown(
                f"""
            <div style='text-align:center; padding:1rem; border-radius:10px;
                        background:{visual['background']}; border: 1px solid {visual['border']};
                        margin-bottom:8px;'>
                <div style='font-size:18px; font-weight:bold; color:#ffffff;'>Mesa {mesa['numero']}</div>
                <div style='font-size:12px; color:#e5e7eb;'>{visual['label']}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            if status == "livre":
                if st.button("Reservar", key=f"reservar_{mesa['id']}", use_container_width=True):
                    try:
                        reservar_mesa(mesa["id"])
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
            elif status == "reservada":
                if st.button("Liberar", key=f"liberar_{mesa['id']}", use_container_width=True):
                    try:
                        liberar_mesa(mesa["id"])
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))

st.divider()

st.markdown("#### Cadastrar nova mesa")

numeros_existentes = [mesa["numero"] for mesa in mesas]
proximo = max(numeros_existentes) + 1 if numeros_existentes else 1

with st.form("form_mesa", clear_on_submit=True):
    numero = st.number_input("Numero da mesa", min_value=1, max_value=200, value=proximo)
    add = st.form_submit_button("Adicionar mesa", use_container_width=False)

if add:
    if numero in numeros_existentes:
        st.error(f"Mesa {numero} ja existe.")
    else:
        criar_mesa(numero)
        st.success(f"Mesa {numero} cadastrada.")
        st.rerun()
