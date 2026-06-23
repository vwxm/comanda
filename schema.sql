-- ===========================================
-- PAINEL DE MÉTRICAS - RESTAURANTE
-- Schema PostgreSQL
-- ===========================================

-- Categorias do cardápio
CREATE TABLE IF NOT EXISTS categorias (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    ativo       BOOLEAN DEFAULT TRUE
);

-- Itens do cardápio
CREATE TABLE IF NOT EXISTS cardapio (
    id            SERIAL PRIMARY KEY,
    nome          VARCHAR(150) NOT NULL,
    categoria_id  INT REFERENCES categorias(id),
    preco         NUMERIC(10,2) NOT NULL,
    custo         NUMERIC(10,2) NOT NULL,
    ativo         BOOLEAN DEFAULT TRUE
);

-- Mesas
CREATE TABLE IF NOT EXISTS mesas (
    id     SERIAL PRIMARY KEY,
    numero INT NOT NULL UNIQUE,
    ativa  BOOLEAN DEFAULT TRUE
);

-- Pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id             SERIAL PRIMARY KEY,
    mesa_id        INT REFERENCES mesas(id),
    aberto_em      TIMESTAMP DEFAULT NOW(),
    fechado_em     TIMESTAMP,
    total          NUMERIC(10,2),
    desconto       NUMERIC(10,2) DEFAULT 0,
    forma_pagamento VARCHAR(50),  -- 'dinheiro','cartao_credito','cartao_debito','pix'
    status         VARCHAR(30) DEFAULT 'aberto'  -- 'aberto','fechado','cancelado'
);

-- Itens de cada pedido
CREATE TABLE IF NOT EXISTS pedido_itens (
    id          SERIAL PRIMARY KEY,
    pedido_id   INT REFERENCES pedidos(id) ON DELETE CASCADE,
    cardapio_id INT REFERENCES cardapio(id),
    quantidade  INT NOT NULL DEFAULT 1,
    preco_unit  NUMERIC(10,2) NOT NULL,
    observacao  TEXT
);

-- ===========================================
-- DADOS DE EXEMPLO
-- ===========================================

INSERT INTO categorias (nome) VALUES
    ('Entradas'),
    ('Pratos Principais'),
    ('Sobremesas'),
    ('Bebidas'),
    ('Porções');

INSERT INTO mesas (numero) VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10);

INSERT INTO cardapio (nome, categoria_id, preco, custo) VALUES
    ('Caldo Verde',         1, 22.00, 6.00),
    ('Bruschetta',          1, 28.00, 7.50),
    ('Frango Grelhado',     2, 52.00, 18.00),
    ('Filé à Parmegiana',   2, 68.00, 22.00),
    ('Macarrão Carbonara',  2, 48.00, 14.00),
    ('Risoto de Camarão',   2, 75.00, 28.00),
    ('Petit Gateau',        3, 32.00, 8.00),
    ('Pudim',               3, 22.00, 5.00),
    ('Refrigerante',        4, 10.00, 3.00),
    ('Suco Natural',        4, 14.00, 4.00),
    ('Água Mineral',        4, 6.00,  1.50),
    ('Cerveja',             4, 12.00, 4.00),
    ('Porção de Batata',    5, 38.00, 10.00),
    ('Porção de Calabresa', 5, 42.00, 12.00);

-- Pedidos dos últimos 30 dias (exemplo realista)
INSERT INTO pedidos (mesa_id, aberto_em, fechado_em, total, desconto, forma_pagamento, status)
SELECT
    (random()*9+1)::int,
    NOW() - (random()*30 || ' days')::interval - (random()*12 || ' hours')::interval,
    NOW() - (random()*30 || ' days')::interval,
    (random()*200+40)::numeric(10,2),
    CASE WHEN random()<0.1 THEN (random()*20)::numeric(10,2) ELSE 0 END,
    (ARRAY['dinheiro','cartao_credito','cartao_debito','pix'])[floor(random()*4+1)],
    'fechado'
FROM generate_series(1, 300);

-- Itens de pedido (2-5 itens por pedido)
INSERT INTO pedido_itens (pedido_id, cardapio_id, quantidade, preco_unit)
SELECT
    p.id,
    (random()*13+1)::int,
    (random()*3+1)::int,
    c.preco
FROM pedidos p
JOIN LATERAL (
    SELECT id, preco FROM cardapio ORDER BY random() LIMIT (floor(random()*4+2))::int
) c ON true
WHERE p.status = 'fechado';
