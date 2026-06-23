"""
pages/1_🍴_Cardápio.py — Cadastro de categorias e produtos
"""
import streamlit as st
from auth import sidebar_estilo, sidebar_admin_status
from crud import (
    listar_categorias, criar_categoria, deletar_categoria,
    listar_cardapio, criar_produto, atualizar_produto, deletar_produto,
)

st.set_page_config(page_title="Cardápio", page_icon="🍴", layout="wide")

sidebar_estilo()
sidebar_admin_status()
st.title("🍴 Gestão do Cardápio")

tab_produtos, tab_categorias = st.tabs(["Produtos", "Categorias"])

# --------------------------------------------------
# ABA: PRODUTOS
# --------------------------------------------------
with tab_produtos:
    col_form, col_lista = st.columns([1, 2])

    with col_form:
        st.markdown("#### Novo produto")
        categorias = listar_categorias()
        cat_map = {c["nome"]: c["id"] for c in categorias}

        with st.form("form_produto", clear_on_submit=True):
            nome      = st.text_input("Nome do produto *")
            categoria = st.selectbox("Categoria *", options=list(cat_map.keys()))
            col1, col2 = st.columns(2)
            preco = col1.number_input("Preço de venda (R$) *", min_value=0.01, step=0.50, format="%.2f")
            custo = col2.number_input("Custo (R$) *", min_value=0.01, step=0.50, format="%.2f")
            salvar = st.form_submit_button("➕ Adicionar produto", use_container_width=True)

        if salvar:
            if not nome:
                st.error("Informe o nome do produto.")
            elif preco <= custo:
                st.warning("Atenção: preço de venda menor ou igual ao custo.")
            else:
                criar_produto(nome, cat_map[categoria], preco, custo)
                st.success(f"✅ '{nome}' adicionado!")
                st.rerun()

    with col_lista:
        st.markdown("#### Produtos cadastrados")
        produtos = listar_cardapio(apenas_ativos=False)

        if not produtos:
            st.info("Nenhum produto cadastrado ainda.")
        else:
            for p in produtos:
                margem = ((p["preco"] - p["custo"]) / p["preco"] * 100) if p["preco"] > 0 else 0
                status = "✅" if p["ativo"] else "❌"
                with st.expander(f"{status} {p['nome']} — R$ {p['preco']:.2f} ({p['categoria']})"):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Preço", f"R$ {p['preco']:.2f}")
                    c2.metric("Custo", f"R$ {p['custo']:.2f}")
                    c3.metric("Margem", f"{margem:.1f}%")
                    c4.metric("Status", "Ativo" if p["ativo"] else "Inativo")

                    st.markdown("**Editar produto:**")
                    categorias_edit = listar_categorias()
                    cat_map_edit = {c["nome"]: c["id"] for c in categorias_edit}
                    cat_names = list(cat_map_edit.keys())
                    cat_atual_idx = cat_names.index(p["categoria"]) if p["categoria"] in cat_names else 0

                    with st.form(f"edit_{p['id']}"):
                        e1, e2 = st.columns(2)
                        novo_nome  = e1.text_input("Nome", value=p["nome"])
                        nova_cat   = e2.selectbox("Categoria", cat_names, index=cat_atual_idx)
                        e3, e4 = st.columns(2)
                        novo_preco = e3.number_input("Preço", value=float(p["preco"]), step=0.50, format="%.2f")
                        novo_custo = e4.number_input("Custo", value=float(p["custo"]), step=0.50, format="%.2f")
                        b1, b2 = st.columns(2)
                        salvar_edit = b1.form_submit_button("💾 Salvar", use_container_width=True)
                        excluir     = b2.form_submit_button("🗑️ Desativar", use_container_width=True)

                    if salvar_edit:
                        atualizar_produto(p["id"], novo_nome, cat_map_edit[nova_cat], novo_preco, novo_custo)
                        st.success("Produto atualizado!")
                        st.rerun()
                    if excluir:
                        deletar_produto(p["id"])
                        st.warning("Produto desativado.")
                        st.rerun()

# --------------------------------------------------
# ABA: CATEGORIAS
# --------------------------------------------------
with tab_categorias:
    col_f, col_l = st.columns([1, 2])

    with col_f:
        st.markdown("#### Nova categoria")
        with st.form("form_categoria", clear_on_submit=True):
            nome_cat = st.text_input("Nome da categoria *")
            add_cat  = st.form_submit_button("➕ Adicionar", use_container_width=True)
        if add_cat:
            if not nome_cat:
                st.error("Informe o nome.")
            else:
                criar_categoria(nome_cat)
                st.success(f"✅ '{nome_cat}' criada!")
                st.rerun()

    with col_l:
        st.markdown("#### Categorias cadastradas")
        cats = listar_categorias(apenas_ativas=False)
        if not cats:
            st.info("Nenhuma categoria ainda.")
        else:
            for c in cats:
                col_n, col_b = st.columns([3, 1])
                col_n.write(f"🏷️ {c['nome']}")
                if col_b.button("🗑️ Remover", key=f"del_cat_{c['id']}"):
                    deletar_categoria(c["id"])
                    st.rerun()
