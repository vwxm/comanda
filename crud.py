"""
crud.py — Operações de escrita no banco (INSERT, UPDATE, DELETE)
"""
import psycopg2
from database import get_connection


# --------------------------------------------------
# Categorias
# --------------------------------------------------

def listar_categorias(apenas_ativas=True):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT id, nome FROM categorias"
            if apenas_ativas:
                sql += " WHERE ativo = TRUE"
            sql += " ORDER BY nome"
            cur.execute(sql)
            return cur.fetchall()


def criar_categoria(nome: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO categorias (nome) VALUES (%s) RETURNING id", (nome,))
            conn.commit()
            return cur.fetchone()[0]


def deletar_categoria(id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE categorias SET ativo = FALSE WHERE id = %s", (id,))
            conn.commit()


# --------------------------------------------------
# Cardápio
# --------------------------------------------------

def listar_cardapio(apenas_ativos=True):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = """
                SELECT c.id, c.nome, cat.nome AS categoria, c.preco, c.custo, c.ativo
                FROM cardapio c
                JOIN categorias cat ON cat.id = c.categoria_id
            """
            if apenas_ativos:
                sql += " WHERE c.ativo = TRUE"
            sql += " ORDER BY cat.nome, c.nome"
            cur.execute(sql)
            return cur.fetchall()


def criar_produto(nome, categoria_id, preco, custo):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO cardapio (nome, categoria_id, preco, custo) VALUES (%s,%s,%s,%s) RETURNING id",
                (nome, categoria_id, preco, custo)
            )
            conn.commit()
            return cur.fetchone()[0]


def atualizar_produto(id, nome, categoria_id, preco, custo):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE cardapio SET nome=%s, categoria_id=%s, preco=%s, custo=%s WHERE id=%s",
                (nome, categoria_id, preco, custo, id)
            )
            conn.commit()


def deletar_produto(id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE cardapio SET ativo = FALSE WHERE id = %s", (id,))
            conn.commit()


# --------------------------------------------------
# Mesas
# --------------------------------------------------

def listar_mesas():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, numero, ativa FROM mesas ORDER BY numero")
            return cur.fetchall()


def criar_mesa(numero: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO mesas (numero) VALUES (%s) RETURNING id", (numero,))
            conn.commit()
            return cur.fetchone()[0]


# --------------------------------------------------
# Pedidos
# --------------------------------------------------

def listar_pedidos_abertos():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT p.id, m.numero AS mesa, p.aberto_em,
                       COALESCE(SUM(pi.quantidade * pi.preco_unit), 0) AS subtotal
                FROM pedidos p
                JOIN mesas m ON m.id = p.mesa_id
                LEFT JOIN pedido_itens pi ON pi.pedido_id = p.id
                WHERE p.status = 'aberto'
                GROUP BY p.id, m.numero, p.aberto_em
                ORDER BY p.aberto_em
            """)
            return cur.fetchall()


def abrir_pedido(mesa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pedidos (mesa_id, status) VALUES (%s, 'aberto') RETURNING id",
                (mesa_id,)
            )
            conn.commit()
            return cur.fetchone()[0]


def adicionar_item(pedido_id, cardapio_id, quantidade, preco_unit, observacao=""):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO pedido_itens (pedido_id, cardapio_id, quantidade, preco_unit, observacao)
                   VALUES (%s, %s, %s, %s, %s)""",
                (pedido_id, cardapio_id, quantidade, preco_unit, observacao)
            )
            conn.commit()


def remover_item(item_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pedido_itens WHERE id = %s", (item_id,))
            conn.commit()


def listar_itens_pedido(pedido_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT pi.id, c.nome, pi.quantidade, pi.preco_unit,
                       pi.quantidade * pi.preco_unit AS subtotal, pi.observacao
                FROM pedido_itens pi
                JOIN cardapio c ON c.id = pi.cardapio_id
                WHERE pi.pedido_id = %s
                ORDER BY pi.id
            """, (pedido_id,))
            return cur.fetchall()


def fechar_pedido(pedido_id, forma_pagamento, desconto=0):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pedidos
                SET status = 'fechado',
                    fechado_em = NOW(),
                    forma_pagamento = %s,
                    desconto = %s,
                    total = (
                        SELECT COALESCE(SUM(quantidade * preco_unit), 0)
                        FROM pedido_itens WHERE pedido_id = %s
                    )
                WHERE id = %s
            """, (forma_pagamento, desconto, pedido_id, pedido_id))
            conn.commit()


def cancelar_pedido(pedido_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE pedidos SET status = 'cancelado', fechado_em = NOW() WHERE id = %s",
                (pedido_id,)
            )
            conn.commit()
