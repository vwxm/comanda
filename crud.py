"""
crud.py - Operacoes de escrita e leitura operacional no banco.
"""
import psycopg2
import psycopg2.extras

from database import get_connection


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
                """
                INSERT INTO cardapio (nome, categoria_id, preco, custo)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (nome, categoria_id, preco, custo),
            )
            conn.commit()
            return cur.fetchone()[0]


def atualizar_produto(id, nome, categoria_id, preco, custo):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE cardapio
                SET nome = %s, categoria_id = %s, preco = %s, custo = %s
                WHERE id = %s
                """,
                (nome, categoria_id, preco, custo, id),
            )
            conn.commit()


def deletar_produto(id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE cardapio SET ativo = FALSE WHERE id = %s", (id,))
            conn.commit()


def listar_mesas():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, numero, ativa, status FROM mesas ORDER BY numero")
            return cur.fetchall()


def listar_mesas_salao():
    """Retorna as mesas com um resumo da comanda aberta, quando existir."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    m.id,
                    m.numero,
                    m.ativa,
                    m.status,
                    p.id AS pedido_id,
                    p.aberto_em,
                    COALESCE(SUM(pi.quantidade), 0)::INTEGER AS quantidade_itens,
                    COALESCE(SUM(pi.quantidade * pi.preco_unit), 0) AS subtotal
                FROM mesas m
                LEFT JOIN pedidos p
                    ON p.mesa_id = m.id
                   AND p.status = 'aberto'
                LEFT JOIN pedido_itens pi ON pi.pedido_id = p.id
                GROUP BY m.id, m.numero, m.ativa, m.status, p.id, p.aberto_em
                ORDER BY m.numero
                """
            )
            return cur.fetchall()


def criar_mesa(numero: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO mesas (numero, status) VALUES (%s, 'livre') RETURNING id",
                (numero,),
            )
            conn.commit()
            return cur.fetchone()[0]


def reservar_mesa(mesa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE mesas
                SET status = 'reservada'
                WHERE id = %s
                  AND ativa = TRUE
                  AND status = 'livre'
                """,
                (mesa_id,),
            )
            if cur.rowcount != 1:
                raise ValueError("A mesa precisa estar livre para ser reservada.")
            conn.commit()


def liberar_mesa(mesa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE mesas
                SET status = 'livre'
                WHERE id = %s
                  AND status = 'reservada'
                  AND NOT EXISTS (
                      SELECT 1
                      FROM pedidos
                      WHERE mesa_id = %s
                        AND status = 'aberto'
                  )
                """,
                (mesa_id, mesa_id),
            )
            if cur.rowcount != 1:
                raise ValueError("Apenas mesas reservadas e sem pedido aberto podem ser liberadas.")
            conn.commit()


def listar_pedidos_abertos():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    m.numero AS mesa,
                    p.aberto_em,
                    COALESCE(SUM(pi.quantidade * pi.preco_unit), 0) AS subtotal
                FROM pedidos p
                JOIN mesas m ON m.id = p.mesa_id
                LEFT JOIN pedido_itens pi ON pi.pedido_id = p.id
                WHERE p.status = 'aberto'
                GROUP BY p.id, m.numero, p.aberto_em
                ORDER BY p.aberto_em
                """
            )
            return cur.fetchall()


def abrir_pedido(mesa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT status, ativa FROM mesas WHERE id = %s FOR UPDATE", (mesa_id,))
            mesa = cur.fetchone()
            if not mesa:
                raise ValueError("Mesa nao encontrada.")
            if not mesa[1]:
                raise ValueError("Mesa inativa.")
            if mesa[0] not in ("livre", "reservada"):
                raise ValueError("Mesa nao esta disponivel para abertura de pedido.")

            cur.execute(
                "SELECT id FROM pedidos WHERE mesa_id = %s AND status = 'aberto'",
                (mesa_id,),
            )
            if cur.fetchone():
                raise ValueError("Ja existe um pedido aberto para esta mesa.")

            cur.execute(
                "INSERT INTO pedidos (mesa_id, status) VALUES (%s, 'aberto') RETURNING id",
                (mesa_id,),
            )
            pedido_id = cur.fetchone()[0]
            cur.execute("UPDATE mesas SET status = 'ocupada' WHERE id = %s", (mesa_id,))
            conn.commit()
            return pedido_id


def solicitar_fechamento(pedido_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT mesa_id
                FROM pedidos
                WHERE id = %s
                  AND status = 'aberto'
                FOR UPDATE
                """,
                (pedido_id,),
            )
            pedido = cur.fetchone()
            if not pedido:
                raise ValueError("Pedido nao encontrado ou ja finalizado.")

            cur.execute(
                """
                UPDATE mesas
                SET status = 'aguardando_pagamento'
                WHERE id = %s
                  AND status = 'ocupada'
                """,
                (pedido[0],),
            )
            if cur.rowcount != 1:
                raise ValueError("A mesa nao esta ocupada ou ja aguarda pagamento.")
            conn.commit()


def adicionar_item(pedido_id, cardapio_id, quantidade, preco_unit, observacao=""):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pedido_itens (pedido_id, cardapio_id, quantidade, preco_unit, observacao)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (pedido_id, cardapio_id, quantidade, preco_unit, observacao),
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
            cur.execute(
                """
                SELECT
                    pi.id,
                    c.nome,
                    pi.quantidade,
                    pi.preco_unit,
                    pi.quantidade * pi.preco_unit AS subtotal,
                    pi.observacao
                FROM pedido_itens pi
                JOIN cardapio c ON c.id = pi.cardapio_id
                WHERE pi.pedido_id = %s
                ORDER BY pi.id
                """,
                (pedido_id,),
            )
            return cur.fetchall()


def fechar_pedido(pedido_id, forma_pagamento, desconto=0):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pedidos
                SET status = 'fechado',
                    fechado_em = NOW(),
                    forma_pagamento = %s,
                    desconto = %s,
                    total = (
                        SELECT COALESCE(SUM(quantidade * preco_unit), 0)
                        FROM pedido_itens
                        WHERE pedido_id = %s
                    )
                WHERE id = %s
                  AND status = 'aberto'
                RETURNING mesa_id
                """,
                (forma_pagamento, desconto, pedido_id, pedido_id),
            )
            pedido = cur.fetchone()
            if not pedido:
                raise ValueError("Pedido nao encontrado ou ja finalizado.")

            cur.execute(
                """
                UPDATE mesas
                SET status = 'livre'
                WHERE id = %s
                  AND status IN ('ocupada', 'aguardando_pagamento')
                """,
                (pedido[0],),
            )
            conn.commit()


def cancelar_pedido(pedido_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pedidos
                SET status = 'cancelado', fechado_em = NOW()
                WHERE id = %s
                  AND status = 'aberto'
                RETURNING mesa_id
                """,
                (pedido_id,),
            )
            pedido = cur.fetchone()
            if not pedido:
                raise ValueError("Pedido nao encontrado ou ja finalizado.")

            cur.execute(
                """
                UPDATE mesas
                SET status = 'livre'
                WHERE id = %s
                  AND status IN ('ocupada', 'aguardando_pagamento')
                """,
                (pedido[0],),
            )
            conn.commit()
