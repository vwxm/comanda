"""
Cadastro e status visual das mesas.
"""
import streamlit as st

from auth import requer_admin, sidebar_admin_status, sidebar_estilo
from crud import criar_mesa, listar_mesas, listar_pedidos_abertos

st.set_page_config(page_title="Mesas", page_icon=":chair:", layout="wide")

sidebar_estilo()
if not requer_admin():
    sidebar_admin_status()
    st.stop()
sidebar_admin_status()

st.title("Gestao de Mesas")

mesas = listar_mesas()
abertos = listar_pedidos_abertos()
mesas_ocupadas = {pedido["mesa"] for pedido in abertos}

st.markdown("#### Status atual")

if not mesas:
    st.info("Nenhuma mesa cadastrada ainda.")
else:
    cols = st.columns(5)
    for i, mesa in enumerate(mesas):
        ocupada = mesa["numero"] in mesas_ocupadas
        with cols[i % 5]:
            label = "Ocupada" if ocupada else "Livre"
            bg = "#7f1d1d" if ocupada else "#14532d"
            borda = "#dc2626" if ocupada else "#22c55e"
            st.markdown(
                f"""
            <div style='text-align:center; padding:1rem; border-radius:10px;
                        background:{bg}; border: 1px solid {borda};
                        margin-bottom:8px;'>
                <div style='font-size:18px; font-weight:bold; color:#ffffff;'>Mesa {mesa['numero']}</div>
                <div style='font-size:12px; color:#e5e7eb;'>{label}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

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
