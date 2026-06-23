"""Painel visual e operacional do salao."""
from datetime import datetime

import streamlit as st

from auth import requer_admin, sidebar_admin_status, sidebar_estilo
from crud import (
    abrir_pedido,
    criar_mesa,
    liberar_mesa,
    listar_mesas_salao,
    reservar_mesa,
    solicitar_fechamento,
)

st.set_page_config(page_title="Salao", page_icon=":material/table_restaurant:", layout="wide")

sidebar_estilo()
if not requer_admin():
    sidebar_admin_status()
    st.stop()
sidebar_admin_status()


STATUS_VISUAL = {
    "livre": {"label": "Livre", "color": "#15803d", "soft": "#dcfce7"},
    "ocupada": {"label": "Ocupada", "color": "#b91c1c", "soft": "#fee2e2"},
    "reservada": {"label": "Reservada", "color": "#a16207", "soft": "#fef3c7"},
    "aguardando_pagamento": {
        "label": "Aguardando pagamento",
        "color": "#1d4ed8",
        "soft": "#dbeafe",
    },
    "inativa": {"label": "Inativa", "color": "#4b5563", "soft": "#f3f4f6"},
}


def formatar_moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_tempo(aberto_em):
    if not aberto_em:
        return "Sem comanda"

    agora = datetime.now(aberto_em.tzinfo) if aberto_em.tzinfo else datetime.now()
    minutos = max(int((agora - aberto_em).total_seconds() // 60), 0)
    horas, minutos = divmod(minutos, 60)
    if horas:
        return f"{horas}h {minutos:02d}min"
    return f"{minutos} min"


def abrir_comanda(pedido_id):
    st.session_state["pedido_foco"] = pedido_id
    st.switch_page("pages/2_pedidos.py")


st.markdown(
    """
    <style>
    .salao-title { margin-bottom: 0.1rem; }
    .salao-subtitle { color: #6b7280; margin: 0 0 1.25rem; }
    .mesa-header {
        min-height: 142px;
        border-left: 5px solid var(--status-color);
        background: var(--status-soft);
        padding: 14px 14px 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .mesa-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 17px;
    }
    .mesa-numero { color: #111827; font-size: 1.2rem; font-weight: 750; }
    .mesa-status {
        color: var(--status-color);
        font-size: 0.72rem;
        font-weight: 750;
        line-height: 1.2;
        text-align: right;
        max-width: 120px;
        text-transform: uppercase;
    }
    .mesa-total { color: #111827; font-size: 1.15rem; font-weight: 750; margin-bottom: 8px; }
    .mesa-meta { color: #4b5563; display: flex; justify-content: space-between; font-size: 0.79rem; gap: 8px; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="salao-title">Salao</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="salao-subtitle">Visao operacional das mesas e comandas em andamento.</p>',
    unsafe_allow_html=True,
)

mesas = listar_mesas_salao()
contagem = {status: 0 for status in STATUS_VISUAL}
for mesa in mesas:
    contagem[mesa["status"]] = contagem.get(mesa["status"], 0) + 1

resumo = st.columns(4)
resumo[0].metric("Total de mesas", len(mesas))
resumo[1].metric("Livres", contagem["livre"])
resumo[2].metric("Em atendimento", contagem["ocupada"])
resumo[3].metric("Aguardando pagamento", contagem["aguardando_pagamento"])

opcoes_filtro = ["todas", *STATUS_VISUAL.keys()]
filtro = st.segmented_control(
    "Filtrar mesas",
    options=opcoes_filtro,
    default="todas",
    format_func=lambda status: "Todas" if status == "todas" else STATUS_VISUAL[status]["label"],
    key="filtro_salao",
)

mesas_visiveis = mesas if filtro == "todas" else [mesa for mesa in mesas if mesa["status"] == filtro]

st.markdown("#### Mesas")
if not mesas_visiveis:
    st.info("Nenhuma mesa encontrada neste status.")
else:
    for inicio in range(0, len(mesas_visiveis), 4):
        colunas = st.columns(4)
        for coluna, mesa in zip(colunas, mesas_visiveis[inicio : inicio + 4]):
            status = mesa["status"]
            visual = STATUS_VISUAL.get(status, STATUS_VISUAL["inativa"])
            pedido_id = mesa["pedido_id"]
            total = formatar_moeda(mesa["subtotal"]) if pedido_id else "Disponivel"
            itens = int(mesa["quantidade_itens"] or 0)
            item_label = "item" if itens == 1 else "itens"
            tempo = formatar_tempo(mesa["aberto_em"])

            with coluna:
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div class="mesa-header" style="--status-color:{visual['color']};--status-soft:{visual['soft']};">
                            <div class="mesa-top">
                                <span class="mesa-numero">Mesa {mesa['numero']}</span>
                                <span class="mesa-status">{visual['label']}</span>
                            </div>
                            <div class="mesa-total">{total}</div>
                            <div class="mesa-meta"><span>{itens} {item_label}</span><span>{tempo}</span></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if status == "livre":
                        acao, reserva = st.columns(2)
                        if acao.button(
                            "Abrir",
                            key=f"abrir_{mesa['id']}",
                            icon=":material/add_circle:",
                            type="primary",
                            use_container_width=True,
                        ):
                            try:
                                abrir_comanda(abrir_pedido(mesa["id"]))
                            except ValueError as exc:
                                st.error(str(exc))
                        if reserva.button(
                            "Reservar",
                            key=f"reservar_{mesa['id']}",
                            icon=":material/bookmark:",
                            use_container_width=True,
                        ):
                            try:
                                reservar_mesa(mesa["id"])
                                st.rerun()
                            except ValueError as exc:
                                st.error(str(exc))
                    elif status == "reservada":
                        ocupar, liberar = st.columns(2)
                        if ocupar.button(
                            "Ocupar",
                            key=f"ocupar_{mesa['id']}",
                            icon=":material/table_restaurant:",
                            type="primary",
                            use_container_width=True,
                        ):
                            try:
                                abrir_comanda(abrir_pedido(mesa["id"]))
                            except ValueError as exc:
                                st.error(str(exc))
                        if liberar.button(
                            "Liberar",
                            key=f"liberar_{mesa['id']}",
                            icon=":material/event_available:",
                            use_container_width=True,
                        ):
                            try:
                                liberar_mesa(mesa["id"])
                                st.rerun()
                            except ValueError as exc:
                                st.error(str(exc))
                    elif status == "ocupada" and pedido_id:
                        comanda, pagamento = st.columns(2)
                        if comanda.button(
                            "Comanda",
                            key=f"comanda_{mesa['id']}",
                            icon=":material/receipt_long:",
                            type="primary",
                            use_container_width=True,
                        ):
                            abrir_comanda(pedido_id)
                        if pagamento.button(
                            "Pedir conta",
                            key=f"pagamento_{mesa['id']}",
                            icon=":material/payments:",
                            use_container_width=True,
                        ):
                            try:
                                solicitar_fechamento(pedido_id)
                                st.rerun()
                            except ValueError as exc:
                                st.error(str(exc))
                    elif status == "aguardando_pagamento" and pedido_id:
                        if st.button(
                            "Abrir pagamento",
                            key=f"cobrar_{mesa['id']}",
                            icon=":material/payments:",
                            type="primary",
                            use_container_width=True,
                        ):
                            abrir_comanda(pedido_id)
                    else:
                        st.button(
                            "Indisponivel",
                            key=f"inativa_{mesa['id']}",
                            icon=":material/block:",
                            disabled=True,
                            use_container_width=True,
                        )

st.divider()

with st.expander("Cadastrar nova mesa"):
    numeros_existentes = [mesa["numero"] for mesa in mesas]
    proximo = max(numeros_existentes) + 1 if numeros_existentes else 1

    with st.form("form_mesa", clear_on_submit=True):
        numero = st.number_input("Numero da mesa", min_value=1, max_value=200, value=proximo)
        adicionar = st.form_submit_button(
            "Adicionar mesa",
            icon=":material/add:",
            type="primary",
        )

    if adicionar:
        if numero in numeros_existentes:
            st.error(f"Mesa {numero} ja existe.")
        else:
            criar_mesa(numero)
            st.success(f"Mesa {numero} cadastrada.")
            st.rerun()
