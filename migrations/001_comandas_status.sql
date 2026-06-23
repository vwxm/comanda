-- Migration 001 - Status de mesas e base para comandas

ALTER TABLE mesas
    ADD COLUMN IF NOT EXISTS status VARCHAR(30) NOT NULL DEFAULT 'livre';

ALTER TABLE mesas
    DROP CONSTRAINT IF EXISTS mesas_status_check;

ALTER TABLE mesas
    ADD CONSTRAINT mesas_status_check
    CHECK (status IN ('livre', 'ocupada', 'reservada', 'aguardando_pagamento', 'inativa'));

UPDATE mesas
SET status = CASE
    WHEN ativa = FALSE THEN 'inativa'
    WHEN EXISTS (
        SELECT 1
        FROM pedidos
        WHERE pedidos.mesa_id = mesas.id
          AND pedidos.status = 'aberto'
    ) THEN 'ocupada'
    ELSE 'livre'
END;

ALTER TABLE pedidos
    ADD COLUMN IF NOT EXISTS taxa_servico NUMERIC(10,2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS observacao TEXT;

UPDATE pedidos
SET status = 'cancelado'
WHERE status IS NULL;

ALTER TABLE pedidos
    ALTER COLUMN status SET NOT NULL;

ALTER TABLE pedidos
    DROP CONSTRAINT IF EXISTS pedidos_status_check;

ALTER TABLE pedidos
    ADD CONSTRAINT pedidos_status_check
    CHECK (status IN ('aberto', 'fechado', 'cancelado'));

CREATE TABLE IF NOT EXISTS reservas (
    id            SERIAL PRIMARY KEY,
    mesa_id       INT NOT NULL REFERENCES mesas(id),
    nome_cliente  VARCHAR(150) NOT NULL,
    reservado_em  TIMESTAMP NOT NULL,
    observacao    TEXT,
    status        VARCHAR(30) NOT NULL DEFAULT 'ativa',
    criado_em     TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (status IN ('ativa', 'concluida', 'cancelada'))
);

DO $$
BEGIN
    IF EXISTS (
        SELECT mesa_id
        FROM pedidos
        WHERE status = 'aberto'
        GROUP BY mesa_id
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION
            'Existem mesas com mais de um pedido aberto. Corrija os dados antes de criar o indice unico.';
    END IF;
END
$$;

CREATE UNIQUE INDEX IF NOT EXISTS idx_pedidos_mesa_aberta
    ON pedidos (mesa_id)
    WHERE status = 'aberto';
