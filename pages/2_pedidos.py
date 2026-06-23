"""
Abertura, lancamento e fechamento de pedidos.
"""
import streamlit as st

from auth import requer_admin, sidebar_admin_status, sidebar_estilo
from crud import (
    adicionar_item,
    abrir_pedido,
    cancelar_pedido,
    fechar_pedido,
    listar_cardapio,
    listar_itens_pedido,
    listar_mesas,
    listar_pedidos_abertos,
    remover_item,
)

st.set_page_config(page_title="Pedidos", page_icon=":receipt:", layout="wide")

sidebar_estilo()
if not requer_admin():
    sidebar_admin_status()
    st.stop()
sidebar_admin_status()

st.title("Gestao de Pedidos")

tab_novo, tab_abertos = st.tabs(["Abrir novo pedido", "Pedidos em aberto"])

with tab_novo:
    st.markdown("#### Abrir pedido para uma mesa")
    mesas = listar_mesas()

    if not mesas:
        st.warning("Nenhuma mesa cadastrada. Cadastre mesas primeiro.")
    else:
        abertos = listar_pedidos_abertos()
        mesas_ocupadas = {pedido["mesa"] for pedido in abertos}
        mesas_disponiveis = [
            mesa for mesa in mesas if mesa["numero"] not in mesas_ocupadas and mesa["ativa"]
        ]

        if not mesas_disponiveis:
            st.info("Todas as mesas estao ocupadas no momento.")
        else:
            with st.form("form_abrir", clear_on_submit=True):
                mesa_num = st.selectbox(
                    "Selecione a mesa",
                    options=[mesa["numero"] for mesa in mesas_disponiveis],
                    format_func=lambda x: f"Mesa {x}",
                )
                abrir = st.form_submit_button("Abrir pedido", use_container_width=False)

            if abrir:
                mesa_id = next(mesa["id"] for mesa in mesas if mesa["numero"] == mesa_num)
                pedido_id = abrir_pedido(mesa_id)
                st.success(f"Pedido aberto para a Mesa {mesa_num}. ID #{pedido_id}.")
                st.rerun()

with tab_abertos:
    abertos = listar_pedidos_abertos()

    if not abertos:
        st.info("Nenhum pedido em aberto no momento.")
    else:
        produtos = listar_cardapio()

        if not produtos:
            st.warning("Nenhum produto ativo cadastrado. Cadastre produtos antes de lancar itens.")
            st.stop()

        prod_map = {f"{produto['nome']} - R$ {produto['preco']:.2f}": produto for produto in produtos}

        for pedido in abertos:
            pedido_id = pedido["id"]
            mesa = pedido["mesa"]
            hora = pedido["aberto_em"].strftime("%H:%M") if pedido["aberto_em"] else "-"
            subtotal = float(pedido["subtotal"])

            titulo = f"Mesa {mesa} - aberta as {hora} - subtotal R$ {subtotal:.2f}"
            with st.expander(titulo, expanded=False):
                itens = listar_itens_pedido(pedido_id)

                if itens:
                    st.markdown("**Itens do pedido:**")
                    for item in itens:
                        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
                        c1.write(item["nome"])
                        c2.write(f"x{item['quantidade']}")
                        c3.write(f"R$ {item['subtotal']:.2f}")
                        if c4.button("Remover", key=f"rm_{item['id']}"):
                            remover_item(item["id"])
                            st.rerun()
                else:
                    st.caption("Nenhum item lancado ainda.")

                st.divider()

                st.markdown("**Adicionar item:**")
                with st.form(f"add_item_{pedido_id}"):
                    c1, c2, c3 = st.columns([3, 1, 2])
                    produto_sel = c1.selectbox("Produto", options=list(prod_map.keys()), key=f"p_{pedido_id}")
                    qtd = c2.number_input("Qtd", min_value=1, max_value=50, value=1, key=f"q_{pedido_id}")
                    obs = c3.text_input("Observacao", placeholder="ex: sem cebola", key=f"o_{pedido_id}")
                    add_btn = st.form_submit_button("Adicionar item", use_container_width=True)

                if add_btn:
                    produto = prod_map[produto_sel]
                    adicionar_item(pedido_id, produto["id"], qtd, float(produto["preco"]), obs)
                    st.success("Item adicionado.")
                    st.rerun()

                st.divider()

                st.markdown("**Fechar pedido:**")
                itens_atuais = listar_itens_pedido(pedido_id)
                total = sum(float(item["subtotal"]) for item in itens_atuais)

                with st.form(f"fechar_{pedido_id}"):
                    c1, c2, c3 = st.columns(3)
                    forma = c1.selectbox(
                        "Forma de pagamento",
                        ["pix", "cartao_credito", "cartao_debito", "dinheiro"],
                        format_func=lambda x: {
                            "pix": "PIX",
                            "cartao_credito": "Cartao Credito",
                            "cartao_debito": "Cartao Debito",
                            "dinheiro": "Dinheiro",
                        }[x],
                    )
                    desconto = c2.number_input(
                        "Desconto (R$)",
                        min_value=0.0,
                        max_value=float(total),
                        step=1.0,
                        format="%.2f",
                    )
                    c3.metric("Total a cobrar", f"R$ {max(total - desconto, 0):.2f}")
                    b1, b2 = st.columns(2)
                    fechar = b1.form_submit_button("Fechar e cobrar", use_container_width=True)
                    cancelar = b2.form_submit_button("Cancelar pedido", use_container_width=True)

                if fechar:
                    if not itens_atuais:
                        st.error("Adicione pelo menos um item antes de fechar.")
                    else:
                        fechar_pedido(pedido_id, forma, desconto)
                        st.success(f"Pedido da Mesa {mesa} fechado. Total: R$ {max(total - desconto, 0):.2f}")
                        st.rerun()

                if cancelar:
                    cancelar_pedido(pedido_id)
                    st.warning(f"Pedido da Mesa {mesa} cancelado.")
                    st.rerun()
