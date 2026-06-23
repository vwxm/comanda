# Comanda Digital - Ecossistema para Restaurantes

Projeto interno para evoluir um sistema de gestao de restaurantes, com foco inicial em comandas digitais, controle de mesas, cardapio, pedidos e metricas operacionais.

O objetivo e substituir comandas fisicas por uma experiencia visual e centralizada: garcons abrem pedidos por mesa, lancam itens, acompanham o consumo e fecham a conta ao final do atendimento.

## Status do Projeto

Este repositorio contem a primeira versao/prototipo, construido em Python com Streamlit e PostgreSQL.

O projeto atual ja possui:

- Dashboard administrativo com metricas de vendas.
- Cadastro de produtos e categorias do cardapio.
- Cadastro e visualizacao de mesas.
- Abertura de pedidos por mesa.
- Lancamento e remocao de itens em pedidos abertos.
- Fechamento e cancelamento de pedidos.
- Modelo inicial de banco de dados em PostgreSQL.

Ainda nao e uma versao final de produto. Esta base sera usada para organizar as primeiras regras de negocio e evoluir gradualmente para um ecossistema mais completo.

## Visao do Produto

A ideia e construir uma plataforma para operacao de restaurantes, bares, lanchonetes e casas similares.

O primeiro modulo sera o de comandas:

- Mesas livres em verde.
- Mesas ocupadas em vermelho.
- Mesas reservadas em amarelo.
- Pedido vinculado a uma mesa.
- Itens lancados pelo garcom.
- Total da mesa atualizado automaticamente.
- Fechamento da conta pelo caixa ou responsavel.

Com o tempo, o ecossistema podera incluir:

- Controle de reservas.
- Perfis de usuario: admin, garcom, caixa e cozinha.
- Painel de cozinha/bar.
- Controle de estoque.
- Fechamento de caixa.
- Relatorios financeiros.
- Historico de atendimentos.
- Integracoes com pagamento, impressoras e delivery.

## Stack Atual

- Python
- Streamlit
- PostgreSQL
- Pandas
- Plotly
- psycopg2
- python-dotenv

## Estrutura

```text
.
+-- app.py                 # Dashboard principal de metricas
+-- auth.py                # Autenticacao simples de admin e estilo da sidebar
+-- crud.py                # Operacoes de leitura/escrita no banco
+-- database.py            # Conexao PostgreSQL e queries de metricas
+-- schema.sql             # Estrutura inicial do banco e dados de exemplo
+-- migrations/            # Ajustes incrementais para bancos existentes
+-- requirements.txt       # Dependencias Python
+-- .env.example           # Exemplo de configuracao local
+-- logo.svg               # Logo usado na interface
+-- PLANO_EXECUCAO.md      # Plano interno de evolucao
+-- pages/
    +-- 1_cardapio.py      # Gestao de produtos e categorias
    +-- 2_pedidos.py       # Abertura, itens e fechamento de pedidos
    +-- 3_mesas.py         # Cadastro e status visual das mesas
```

## Modelo de Dados Atual

O banco inicial trabalha com as seguintes entidades:

- `categorias`: grupos do cardapio.
- `cardapio`: produtos vendidos pelo restaurante.
- `mesas`: mesas fisicas do estabelecimento.
- `pedidos`: comandas abertas, fechadas ou canceladas.
- `pedido_itens`: itens vinculados a cada pedido.

Fluxo principal:

```text
mesa -> pedido -> pedido_itens -> cardapio
```

## Como Rodar Localmente

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/Mac:

```bash
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variaveis de ambiente

Copie o arquivo de exemplo:

```bash
copy .env.example .env
```

No Linux/Mac:

```bash
cp .env.example .env
```

Depois edite o `.env` com os dados do PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=restaurante
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_CONNECT_TIMEOUT=5
```

### 4. Criar banco e aplicar schema

```bash
psql -U postgres -c "CREATE DATABASE restaurante;"
psql -U postgres -d restaurante -f schema.sql
```

Para atualizar um banco existente, aplique as migrations em ordem:

```bash
psql -U postgres -d restaurante -f migrations/001_comandas_status.sql
```

### 5. Rodar o app

```bash
streamlit run app.py
```

Depois acesse:

```text
http://localhost:8501
```

## Acesso Admin

O projeto possui uma autenticacao simples para o painel administrativo.

Por padrao, caso `ADMIN_PASSWORD_HASH` nao seja configurado no `.env`, a senha usada pelo sistema e:

```text
admin123
```

Para producao ou testes compartilhados, a senha deve ser trocada usando um hash SHA-256 no `.env`.

## Roadmap Inicial

### Fase 1 - Organizar a Base

- Padronizar nomes de arquivos.
- Corrigir textos com encoding quebrado.
- Proteger todas as telas administrativas.
- Criar constraints importantes no banco.
- Melhorar README e documentacao interna.
- Versionar o projeto no GitHub.

### Fase 2 - Comandas Visuais

- Criar tela principal de mesas mais visual.
- Adicionar status: livre, ocupada, reservada, aguardando pagamento.
- Permitir abrir comanda clicando diretamente na mesa.
- Mostrar total, tempo aberto e quantidade de itens na mesa.
- Melhorar fluxo de adicionar itens.

### Fase 3 - Operacao de Restaurante

- Criar usuarios e permissoes.
- Registrar qual garcom abriu/lancou cada pedido.
- Criar painel de cozinha/bar.
- Adicionar status por item: enviado, preparando, pronto, entregue.
- Permitir transferir mesa.
- Permitir dividir ou juntar contas.

### Fase 4 - Gestao e Escala

- Fechamento de caixa.
- Relatorios por periodo.
- Controle de estoque.
- Reservas.
- Integracoes externas.
- Avaliar migracao da interface operacional para React/Next.js com backend em FastAPI.

## Decisoes Tecnicas Provaveis

Para o prototipo, Streamlit atende bem porque permite evoluir rapido.

Para uma versao mais robusta e usada por varios usuarios ao mesmo tempo, a stack provavel sera:

- Frontend: React ou Next.js.
- Backend: FastAPI.
- Banco: PostgreSQL.
- Atualizacao em tempo real: WebSockets ou recurso similar.
- Autenticacao com perfis e permissoes.

Essa decisao ainda sera tomada conforme o produto evoluir.

## Observacoes Internas

- Nao versionar `.env`.
- Nao versionar `venv/`.
- Nao versionar arquivos temporarios.
- Manter `.env.example` atualizado.
- Registrar mudancas importantes em commits pequenos e claros.
- Antes de mudancas grandes, validar o fluxo real de atendimento do restaurante.
