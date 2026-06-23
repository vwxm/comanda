"""
pages/2_🧾_Pedidos.py — Abertura, lançamento e fechamento de pedidos
"""
import streamlit as st
from auth import sidebar_estilo, sidebar_admin_status
from crud import (
    listar_mesas, abrir_pedido,
    listar_pedidos_abertos, listar_itens_pedido,
    listar_cardapio, adicionar_item, remover_item,
    fechar_pedido, cancelar_pedido,
)

st.set_page_config(page_title="Pedidos", page_icon="🧾", layout="wide")

sidebar_estilo()
sidebar_admin_status()
st.title("🧾 Gestão de Pedidos")

tab_novo, tab_abertos = st.tabs(["Abrir novo pedido", "Pedidos em aberto"])

# --------------------------------------------------
# ABA: NOVO PEDIDO
# --------------------------------------------------
with tab_novo:
    st.markdown("#### Abrir pedido para uma mesa")
    mesas = listar_mesas()

    if not mesas:
        st.warning("Nenhuma mesa cadastrada. Cadastre mesas primeiro.")
    else:
        # Mesas que já têm pedido aberto
        abertos = listar_pedidos_abertos()
        mesas_ocupadas = {p["mesa"] for p in abertos}

        mesas_disponiveis = [m for m in mesas if m["numero"] not in mesas_ocupadas and m["ativa"]]

        if not mesas_disponiveis:
            st.info("Todas as mesas estão ocupadas no momento.")
        else:
            with st.form("form_abrir", clear_on_submit=True):
                mesa_num = st.selectbox(
                    "Selecione a mesa",
                    options=[m["numero"] for m in mesas_disponiveis],
                    format_func=lambda x: f"Mesa {x}",
                )
                abrir = st.form_submit_button("🟢 Abrir pedido", use_container_width=False)

            if abrir:
                mesa_id = next(m["id"] for m in mesas if m["numero"] == mesa_num)
                pid = abrir_pedido(mesa_id)
                st.success(f"✅ Pedido aberto para a Mesa {mesa_num}! (ID #{pid})")
                st.rerun()

# --------------------------------------------------
# ABA: PEDIDOS ABERTOS
# --------------------------------------------------
with tab_abertos:
    abertos = listar_pedidos_abertos()

    if not abertos:
        st.info("Nenhum pedido em aberto no momento.")
    else:
        produtos = listar_cardapio()
        prod_map = {f"{p['nome']} — R$ {p['preco']:.2f}": p for p in produtos}

        for pedido in abertos:
            pid  = pedido["id"]
            mesa = pedido["mesa"]
            hora = pedido["aberto_em"].strftime("%H:%M") if pedido["aberto_em"] else "—"
            sub  = float(pedido["subtotal"])

            with st.expander(f"🪑 Mesa {mesa} — aberto às {hora} — subtotal R$ {sub:.2f}", expanded=False):
                itens = listar_itens_pedido(pid)

                # Lista de itens
                if itens:
                    st.markdown("**Itens do pedido:**")
                    for it in itens:
                        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
                        c1.write(it["nome"])
                        c2.write(f"x{it['quantidade']}")
                        c3.write(f"R$ {it['subtotal']:.2f}")
                        if c4.button("🗑️", key=f"rm_{it['id']}"):
                            remover_item(it["id"])
                            st.rerun()
                else:
                    st.caption("Nenhum item lançado ainda.")

                st.divider()

                # Adicionar item
                st.markdown("**Adicionar item:**")
                with st.form(f"add_item_{pid}"):
                    c1, c2, c3 = st.columns([3, 1, 2])
                    produto_sel = c1.selectbox("Produto", options=list(prod_map.keys()), key=f"p_{pid}")
                    qtd         = c2.number_input("Qtd", min_value=1, max_value=50, value=1, key=f"q_{pid}")
                    obs         = c3.text_input("Observação", placeholder="ex: sem cebola", key=f"o_{pid}")
                    add_btn     = st.form_submit_button("➕ Adicionar item", use_container_width=True)

                if add_btn:
                    prod = prod_map[produto_sel]
                    adicionar_item(pid, prod["id"], qtd, float(prod["preco"]), obs)
                    st.success("Item adicionado!")
                    st.rerun()

                st.divider()

                # Fechar pedido
                st.markdown("**Fechar pedido:**")
                itens_atuais = listar_itens_pedido(pid)
                total = sum(float(i["subtotal"]) for i in itens_atuais)

                with st.form(f"fechar_{pid}"):
                    c1, c2, c3 = st.columns(3)
                    forma = c1.selectbox("Forma de pagamento", [
                        "pix", "cartao_credito", "cartao_debito", "dinheiro"
                    ], format_func=lambda x: {
                        "pix": "PIX",
                        "cartao_credito": "Cartão Crédito",
                        "cartao_debito": "Cartão Débito",
                        "dinheiro": "Dinheiro",
                    }[x])
                    desconto = c2.number_input("Desconto (R$)", min_value=0.0, max_value=float(total), step=1.0, format="%.2f")
                    c3.metric("Total a cobrar", f"R$ {max(total - desconto, 0):.2f}")
                    b1, b2 = st.columns(2)
                    fechar  = b1.form_submit_button("✅ Fechar e cobrar", use_container_width=True)
                    cancelar = b2.form_submit_button("❌ Cancelar pedido", use_container_width=True)

                if fechar:
                    if not itens_atuais:
                        st.error("Adicione pelo menos um item antes de fechar.")
                    else:
                        fechar_pedido(pid, forma, desconto)
                        st.success(f"✅ Pedido da Mesa {mesa} fechado! Total: R$ {max(total-desconto,0):.2f}")
                        st.rerun()

                if cancelar:
                    cancelar_pedido(pid)
                    st.warning(f"Pedido da Mesa {mesa} cancelado.")
                    st.rerun()
