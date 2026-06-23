"""
database.py — Conexão e queries com PostgreSQL
"""
import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# Conexão
# --------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "restaurante"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def query_df(sql: str, params=None) -> pd.DataFrame:
    """Executa uma query e retorna um DataFrame."""
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


# --------------------------------------------------
# KPIs gerais
# --------------------------------------------------

def get_kpis(dias: int = 30) -> dict:
    sql = """
        WITH periodo_atual AS (
            SELECT
                COUNT(*)                          AS total_pedidos,
                COALESCE(SUM(total - desconto), 0) AS receita,
                COALESCE(AVG(total - desconto), 0) AS ticket_medio,
                COALESCE(SUM(total - desconto) -
                    (SELECT SUM(pi.quantidade * c.custo)
                     FROM pedido_itens pi
                     JOIN cardapio c ON c.id = pi.cardapio_id
                     JOIN pedidos p2 ON p2.id = pi.pedido_id
                     WHERE p2.status = 'fechado'
                       AND p2.fechado_em >= NOW() - (%s || ' days')::interval), 0) AS lucro
            FROM pedidos
            WHERE status = 'fechado'
              AND fechado_em >= NOW() - (%s || ' days')::interval
        ),
        periodo_anterior AS (
            SELECT
                COUNT(*)                          AS total_pedidos,
                COALESCE(SUM(total - desconto), 0) AS receita,
                COALESCE(AVG(total - desconto), 0) AS ticket_medio
            FROM pedidos
            WHERE status = 'fechado'
              AND fechado_em BETWEEN NOW() - (%s || ' days')::interval * 2
                                 AND NOW() - (%s || ' days')::interval
        )
        SELECT
            a.total_pedidos, a.receita, a.ticket_medio, a.lucro,
            pa.receita   AS receita_anterior,
            pa.ticket_medio AS ticket_anterior,
            pa.total_pedidos AS pedidos_anterior
        FROM periodo_atual a, periodo_anterior pa;
    """
    row = query_df(sql, (dias, dias, dias, dias)).iloc[0]

    def delta_pct(atual, anterior):
        if anterior == 0:
            return 0.0
        return round((atual - anterior) / anterior * 100, 1)

    return {
        "receita":         float(row["receita"]),
        "receita_delta":   delta_pct(row["receita"], row["receita_anterior"]),
        "ticket_medio":    float(row["ticket_medio"]),
        "ticket_delta":    delta_pct(row["ticket_medio"], row["ticket_anterior"]),
        "total_pedidos":   int(row["total_pedidos"]),
        "pedidos_delta":   delta_pct(row["total_pedidos"], row["pedidos_anterior"]),
        "lucro":           float(row["lucro"]),
    }


# --------------------------------------------------
# Receita por dia
# --------------------------------------------------

def get_receita_diaria(dias: int = 30) -> pd.DataFrame:
    sql = """
        SELECT
            DATE(fechado_em)            AS data,
            SUM(total - desconto)       AS receita,
            COUNT(*)                    AS pedidos
        FROM pedidos
        WHERE status = 'fechado'
          AND fechado_em >= NOW() - (%s || ' days')::interval
        GROUP BY DATE(fechado_em)
        ORDER BY data;
    """
    return query_df(sql, (dias,))


# --------------------------------------------------
# Formas de pagamento
# --------------------------------------------------

def get_pagamentos(dias: int = 30) -> pd.DataFrame:
    sql = """
        SELECT
            forma_pagamento,
            COUNT(*)            AS qtd,
            SUM(total-desconto) AS total
        FROM pedidos
        WHERE status = 'fechado'
          AND fechado_em >= NOW() - (%s || ' days')::interval
        GROUP BY forma_pagamento
        ORDER BY total DESC;
    """
    return query_df(sql, (dias,))


# --------------------------------------------------
# Top produtos
# --------------------------------------------------

def get_top_produtos(dias: int = 30, limit: int = 10) -> pd.DataFrame:
    sql = """
        SELECT
            c.nome,
            cat.nome                        AS categoria,
            SUM(pi.quantidade)              AS quantidade,
            SUM(pi.quantidade * pi.preco_unit) AS receita,
            SUM(pi.quantidade * (pi.preco_unit - c.custo)) AS lucro,
            ROUND(
                SUM(pi.quantidade*(pi.preco_unit - c.custo)) /
                NULLIF(SUM(pi.quantidade * pi.preco_unit),0) * 100
            , 1)                            AS margem_pct
        FROM pedido_itens pi
        JOIN cardapio c   ON c.id  = pi.cardapio_id
        JOIN categorias cat ON cat.id = c.categoria_id
        JOIN pedidos p    ON p.id  = pi.pedido_id
        WHERE p.status = 'fechado'
          AND p.fechado_em >= NOW() - (%s || ' days')::interval
        GROUP BY c.nome, cat.nome
        ORDER BY receita DESC
        LIMIT %s;
    """
    return query_df(sql, (dias, limit))


# --------------------------------------------------
# Movimento por hora
# --------------------------------------------------

def get_movimento_hora(dias: int = 30) -> pd.DataFrame:
    sql = """
        SELECT
            EXTRACT(HOUR FROM fechado_em)::int AS hora,
            COUNT(*)                            AS pedidos,
            ROUND(AVG(total - desconto), 2)     AS ticket_medio
        FROM pedidos
        WHERE status = 'fechado'
          AND fechado_em >= NOW() - (%s || ' days')::interval
        GROUP BY hora
        ORDER BY hora;
    """
    return query_df(sql, (dias,))


# --------------------------------------------------
# Receita por categoria
# --------------------------------------------------

def get_receita_categoria(dias: int = 30) -> pd.DataFrame:
    sql = """
        SELECT
            cat.nome            AS categoria,
            SUM(pi.quantidade * pi.preco_unit) AS receita
        FROM pedido_itens pi
        JOIN cardapio c   ON c.id  = pi.cardapio_id
        JOIN categorias cat ON cat.id = c.categoria_id
        JOIN pedidos p    ON p.id  = pi.pedido_id
        WHERE p.status = 'fechado'
          AND p.fechado_em >= NOW() - (%s || ' days')::interval
        GROUP BY cat.nome
        ORDER BY receita DESC;
    """
    return query_df(sql, (dias,))
