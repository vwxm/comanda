"""
Gestão.py — Painel de Métricas (restrito a admin)
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from auth import sidebar_estilo, sidebar_admin_status, requer_admin
from database import (
    get_kpis, get_receita_diaria, get_pagamentos,
    get_top_produtos, get_movimento_hora, get_receita_categoria,
)

st.set_page_config(
    page_title="Painel do Restaurante",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

sidebar_estilo()

# ── Bloqueia se não for admin ──────────────────────
if not requer_admin():
    sidebar_admin_status()
    st.stop()

# ── Filtro de período na sidebar ───────────────────
with st.sidebar:
    st.markdown('<span class="sidebar-section">Filtros</span>', unsafe_allow_html=True)
    periodo = st.selectbox(
        "Período de análise",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Últimos {x} dias",
    )

sidebar_admin_status()

# ── Cabeçalho ──────────────────────────────────────
st.title("📊 Painel de Métricas")
st.caption(f"Dados dos últimos {periodo} dias — comparado ao período anterior")
st.divider()

# ── KPIs ───────────────────────────────────────────
try:
    kpis = get_kpis(periodo)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Receita Total",    f"R$ {kpis['receita']:,.2f}",     f"{kpis['receita_delta']:+.1f}% vs período anterior")
    col2.metric("🧾 Total de Pedidos", f"{kpis['total_pedidos']:,}",      f"{kpis['pedidos_delta']:+.1f}% vs período anterior")
    col3.metric("🎫 Ticket Médio",     f"R$ {kpis['ticket_medio']:,.2f}", f"{kpis['ticket_delta']:+.1f}% vs período anterior")
    margem = (kpis["lucro"] / kpis["receita"] * 100) if kpis["receita"] > 0 else 0
    col4.metric("📈 Lucro Bruto",      f"R$ {kpis['lucro']:,.2f}",       f"Margem de {margem:.1f}%")
except Exception as e:
    st.error(f"Erro ao carregar KPIs: {e}")
    st.stop()

st.divider()

# ── Receita diária + Pagamentos ────────────────────
col_esq, col_dir = st.columns([2, 1])

with col_esq:
    st.markdown("#### Receita Diária")
    df_rec = get_receita_diaria(periodo)
    if not df_rec.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_rec["data"], y=df_rec["receita"],
            mode="lines+markers", line=dict(color="#3b82f6", width=2),
            marker=dict(size=5), fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
        ))
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title=None, yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f",
            showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig, use_container_width=True)

with col_dir:
    st.markdown("#### Formas de Pagamento")
    df_pag = get_pagamentos(periodo)
    if not df_pag.empty:
        labels_map = {"pix": "PIX", "cartao_credito": "Crédito", "cartao_debito": "Débito", "dinheiro": "Dinheiro"}
        df_pag["forma"] = df_pag["forma_pagamento"].map(labels_map).fillna(df_pag["forma_pagamento"])
        fig2 = px.pie(df_pag, names="forma", values="total", hole=0.55,
                      color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b", "#ef4444"])
        fig2.update_traces(textposition="outside", textinfo="percent+label")
        fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                           showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Movimento por hora + Categoria ─────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Movimento por Hora")
    df_hora = get_movimento_hora(periodo)
    if not df_hora.empty:
        fig3 = px.bar(df_hora, x="hora", y="pedidos", color="pedidos",
                      color_continuous_scale="Blues", labels={"hora": "Hora", "pedidos": "Pedidos"})
        fig3.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0),
                           coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(tickmode="linear", dtick=1), yaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig3, use_container_width=True)

with col_b:
    st.markdown("#### Receita por Categoria")
    df_cat = get_receita_categoria(periodo)
    if not df_cat.empty:
        fig4 = px.bar(df_cat, x="receita", y="categoria", orientation="h",
                      color="receita", color_continuous_scale="Teal",
                      text=df_cat["receita"].apply(lambda v: f"R$ {v:,.0f}"))
        fig4.update_traces(textposition="outside")
        fig4.update_layout(height=280, margin=dict(l=0, r=60, t=10, b=0),
                           coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(showgrid=False, showticklabels=False))
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Top produtos ───────────────────────────────────
st.markdown("#### 🏆 Produtos com Melhor Desempenho")
df_prod = get_top_produtos(periodo)
if not df_prod.empty:
    df_prod["receita"]    = df_prod["receita"].apply(lambda v: f"R$ {v:,.2f}")
    df_prod["lucro"]      = df_prod["lucro"].apply(lambda v: f"R$ {v:,.2f}")
    df_prod["margem_pct"] = df_prod["margem_pct"].apply(lambda v: f"{v}%")
    df_prod["quantidade"] = df_prod["quantidade"].astype(int)
    df_prod = df_prod.rename(columns={
        "nome": "Produto", "categoria": "Categoria", "quantidade": "Qtd. Vendida",
        "receita": "Receita", "lucro": "Lucro", "margem_pct": "Margem",
    })
    st.dataframe(df_prod, use_container_width=True, hide_index=True)