"""
Cadastro de categorias e produtos do cardapio.
"""
import streamlit as st

from auth import requer_admin, sidebar_admin_status, sidebar_estilo
from crud import (
    atualizar_produto,
    criar_categoria,
    criar_produto,
    deletar_categoria,
    deletar_produto,
    listar_cardapio,
    listar_categorias,
)

st.set_page_config(page_title="Cardapio", page_icon=":fork_and_knife:", layout="wide")

sidebar_estilo()
if not requer_admin():
    sidebar_admin_status()
    st.stop()
sidebar_admin_status()

st.title("Gestao do Cardapio")

tab_produtos, tab_categorias = st.tabs(["Produtos", "Categorias"])

with tab_produtos:
    col_form, col_lista = st.columns([1, 2])

    with col_form:
        st.markdown("#### Novo produto")
        categorias = listar_categorias()
        cat_map = {c["nome"]: c["id"] for c in categorias}

        if not cat_map:
            st.warning("Cadastre pelo menos uma categoria antes de adicionar produtos.")
        else:
            with st.form("form_produto", clear_on_submit=True):
                nome = st.text_input("Nome do produto *")
                categoria = st.selectbox("Categoria *", options=list(cat_map.keys()))
                col1, col2 = st.columns(2)
                preco = col1.number_input(
                    "Preco de venda (R$) *",
                    min_value=0.01,
                    step=0.50,
                    format="%.2f",
                )
                custo = col2.number_input(
                    "Custo (R$) *",
                    min_value=0.01,
                    step=0.50,
                    format="%.2f",
                )
                salvar = st.form_submit_button("Adicionar produto", use_container_width=True)

            if salvar:
                if not nome:
                    st.error("Informe o nome do produto.")
                elif preco <= custo:
                    st.warning("Atencao: preco de venda menor ou igual ao custo.")
                else:
                    criar_produto(nome, cat_map[categoria], preco, custo)
                    st.success(f"'{nome}' adicionado.")
                    st.rerun()

    with col_lista:
        st.markdown("#### Produtos cadastrados")
        produtos = listar_cardapio(apenas_ativos=False)

        if not produtos:
            st.info("Nenhum produto cadastrado ainda.")
        else:
            for produto in produtos:
                margem = (
                    (produto["preco"] - produto["custo"]) / produto["preco"] * 100
                    if produto["preco"] > 0
                    else 0
                )
                status = "Ativo" if produto["ativo"] else "Inativo"
                titulo = f"{status} - {produto['nome']} - R$ {produto['preco']:.2f} ({produto['categoria']})"
                with st.expander(titulo):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Preco", f"R$ {produto['preco']:.2f}")
                    c2.metric("Custo", f"R$ {produto['custo']:.2f}")
                    c3.metric("Margem", f"{margem:.1f}%")
                    c4.metric("Status", status)

                    st.markdown("**Editar produto:**")
                    categorias_edit = listar_categorias()
                    cat_map_edit = {c["nome"]: c["id"] for c in categorias_edit}
                    cat_names = list(cat_map_edit.keys())
                    cat_atual_idx = (
                        cat_names.index(produto["categoria"])
                        if produto["categoria"] in cat_names
                        else 0
                    )

                    with st.form(f"edit_{produto['id']}"):
                        e1, e2 = st.columns(2)
                        novo_nome = e1.text_input("Nome", value=produto["nome"])
                        nova_cat = e2.selectbox("Categoria", cat_names, index=cat_atual_idx)
                        e3, e4 = st.columns(2)
                        novo_preco = e3.number_input(
                            "Preco",
                            value=float(produto["preco"]),
                            step=0.50,
                            format="%.2f",
                        )
                        novo_custo = e4.number_input(
                            "Custo",
                            value=float(produto["custo"]),
                            step=0.50,
                            format="%.2f",
                        )
                        b1, b2 = st.columns(2)
                        salvar_edit = b1.form_submit_button("Salvar", use_container_width=True)
                        excluir = b2.form_submit_button("Desativar", use_container_width=True)

                    if salvar_edit:
                        atualizar_produto(
                            produto["id"],
                            novo_nome,
                            cat_map_edit[nova_cat],
                            novo_preco,
                            novo_custo,
                        )
                        st.success("Produto atualizado.")
                        st.rerun()
                    if excluir:
                        deletar_produto(produto["id"])
                        st.warning("Produto desativado.")
                        st.rerun()

with tab_categorias:
    col_f, col_l = st.columns([1, 2])

    with col_f:
        st.markdown("#### Nova categoria")
        with st.form("form_categoria", clear_on_submit=True):
            nome_cat = st.text_input("Nome da categoria *")
            add_cat = st.form_submit_button("Adicionar", use_container_width=True)
        if add_cat:
            if not nome_cat:
                st.error("Informe o nome.")
            else:
                criar_categoria(nome_cat)
                st.success(f"'{nome_cat}' criada.")
                st.rerun()

    with col_l:
        st.markdown("#### Categorias cadastradas")
        cats = listar_categorias(apenas_ativas=False)
        if not cats:
            st.info("Nenhuma categoria ainda.")
        else:
            for categoria in cats:
                col_n, col_b = st.columns([3, 1])
                col_n.write(categoria["nome"])
                if col_b.button("Remover", key=f"del_cat_{categoria['id']}"):
                    deletar_categoria(categoria["id"])
                    st.rerun()
