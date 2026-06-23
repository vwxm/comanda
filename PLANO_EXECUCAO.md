# Plano de Execucao - Comanda Digital

Este documento organiza o plano de trabalho do projeto. A ideia e manter um guia simples para acompanhar o que ja foi feito, o que esta em andamento e quais serao os proximos passos.

## Objetivo Geral

Construir um ecossistema para restaurantes, comecando pelo modulo de comandas digitais.

O primeiro objetivo pratico e substituir comandas fisicas por um sistema visual de controle de mesas, onde garcons possam abrir pedidos, lancar itens e acompanhar o consumo ate o fechamento da conta.

## Meta Inicial

Criar uma tela de salao bonita e funcional, onde cada mesa tenha um status visual e permita acessar ou gerenciar a comanda vinculada.

Estados iniciais das mesas:

- Verde: mesa disponivel.
- Vermelho: mesa ocupada.
- Amarelo: mesa reservada.
- Cinza ou azul: mesa aguardando pagamento, inativa ou em outro status operacional.

## Fase 0 - Subir e Organizar

Objetivo: colocar o projeto no GitHub e criar uma base minima para trabalho colaborativo.

Tarefas:

- [x] Criar repositorio no GitHub.
- [x] Inicializar Git localmente.
- [x] Fazer o primeiro commit limpo.
- [x] Conectar o repositorio local ao remoto.
- [x] Subir o projeto para o GitHub.
- [x] Criar branch de desenvolvimento, se necessario.
- [ ] Criar issues/tarefas iniciais no GitHub.
- [ ] Manter `.env`, `venv/`, caches e arquivos temporarios fora do repositorio.

## Fase 1 - Arrumar a Base Atual

Objetivo: estabilizar o projeto existente antes de adicionar novas funcionalidades.

Tarefas:

- [x] Corrigir textos com encoding quebrado.
- [x] Renomear arquivos com acentos e emojis para nomes seguros.
- [x] Renomear arquivo principal para `app.py`.
- [x] Renomear paginas para nomes simples:
  - [x] `pages/1_cardapio.py`
  - [x] `pages/2_pedidos.py`
  - [x] `pages/3_mesas.py`
- [x] Atualizar README depois das mudancas de nomes.
- [x] Remover arquivo `.tmp` da raiz.
- [x] Garantir que paginas administrativas estejam protegidas.
- [x] Revisar `.env.example`.
- [ ] Validar se o projeto roda do zero seguindo o README.
- [ ] Criar um commit apenas com limpeza e organizacao.

## Fase 2 - Melhorar o Banco Para Comandas

Objetivo: preparar o modelo de dados para suportar a operacao real de comandas.

Tarefas:

- [ ] Adicionar status real para mesas:
  - [ ] `livre`
  - [ ] `ocupada`
  - [ ] `reservada`
  - [ ] `aguardando_pagamento`
  - [ ] `inativa`
- [ ] Impedir mais de um pedido aberto na mesma mesa.
- [ ] Adicionar observacao geral no pedido.
- [ ] Preparar campo para taxa de servico.
- [ ] Melhorar status dos pedidos.
- [ ] Preparar estrutura inicial para reservas.
- [ ] Revisar queries impactadas pelas mudancas.
- [ ] Atualizar `schema.sql`.
- [ ] Testar criacao do banco do zero.

## Fase 3 - Tela Visual de Mesas

Objetivo: transformar a gestao de mesas em uma experiencia visual e operacional.

Tarefas:

- [ ] Criar tela principal de salao.
- [ ] Mostrar mesas em grid visual.
- [ ] Aplicar cores por status.
- [ ] Exibir numero da mesa.
- [ ] Exibir status da mesa.
- [ ] Exibir total atual da comanda.
- [ ] Exibir tempo desde abertura do pedido.
- [ ] Exibir quantidade de itens.
- [ ] Permitir clicar na mesa para abrir/ver comanda.
- [ ] Adicionar acoes rapidas:
  - [ ] Abrir pedido.
  - [ ] Adicionar item.
  - [ ] Fechar conta.
  - [ ] Reservar mesa.
  - [ ] Liberar mesa.
- [ ] Melhorar layout para uso em tablet/celular.

## Fase 4 - Fluxo de Comanda

Objetivo: deixar o lancamento de pedidos mais rapido, claro e proximo da rotina de um garcom.

Tarefas:

- [ ] Criar tela de comanda por mesa.
- [ ] Mostrar itens ja lancados.
- [ ] Mostrar subtotal em tempo real.
- [ ] Criar busca rapida de produto.
- [ ] Listar produtos por categoria.
- [ ] Adicionar quantidade com controles rapidos.
- [ ] Permitir observacao por item.
- [ ] Permitir remover item.
- [ ] Permitir cancelar item com motivo, futuramente.
- [ ] Fechar pedido com forma de pagamento.
- [ ] Melhorar fluxo de desconto.
- [ ] Preparar futura divisao de conta.

## Fase 5 - Perfis de Usuario

Objetivo: criar controle de acesso adequado para operacao real.

Perfis iniciais:

- Admin: configura cardapio, mesas, usuarios e visualiza metricas.
- Garcom: abre mesas e lanca pedidos.
- Caixa: fecha contas e registra pagamentos.
- Cozinha/bar: acompanha preparo dos itens.

Tarefas:

- [ ] Criar tabela de usuarios.
- [ ] Criar login real.
- [ ] Criar perfis/permissoes.
- [ ] Registrar quem abriu cada pedido.
- [ ] Registrar quem lancou cada item.
- [ ] Registrar quem fechou cada conta.
- [ ] Proteger telas conforme perfil.

## Fase 6 - Cozinha e Operacao

Objetivo: expandir o sistema para acompanhar o preparo e a entrega dos itens.

Tarefas:

- [ ] Criar painel de cozinha.
- [ ] Criar painel de bar, se necessario.
- [ ] Adicionar status por item:
  - [ ] Enviado.
  - [ ] Preparando.
  - [ ] Pronto.
  - [ ] Entregue.
  - [ ] Cancelado.
- [ ] Separar itens por setor:
  - [ ] Cozinha.
  - [ ] Bar.
  - [ ] Sobremesa.
- [ ] Criar historico de alteracoes.
- [ ] Registrar motivo de cancelamento.
- [ ] Criar alertas visuais para pedidos atrasados.

## Fase 7 - Decisao de Stack

Objetivo: decidir se o projeto continua em Streamlit ou se sera migrado para uma arquitetura mais robusta.

Caminho recomendado para agora:

- Manter Streamlit no prototipo.
- Validar regras de negocio.
- Construir rapidamente o fluxo de comanda.
- Evitar migracao prematura.

Cenario para migrar:

- Varios usuarios simultaneos.
- Necessidade de tempo real.
- Uso intenso em celular/tablet.
- Produto com clientes reais.
- Necessidade de interface mais personalizada.

Stack provavel para versao robusta:

- Frontend: React ou Next.js.
- Backend: FastAPI.
- Banco: PostgreSQL.
- Tempo real: WebSockets ou tecnologia similar.
- Autenticacao com perfis e permissoes.

## Ordem Recomendada Agora

1. Subir o projeto atual no GitHub.
2. Fazer limpeza da base atual.
3. Corrigir nomes de arquivos e encoding.
4. Proteger paginas sensiveis.
5. Melhorar modelo de mesas e pedidos.
6. Criar primeira versao visual da tela de mesas.
7. Melhorar fluxo de comanda.
8. Adicionar perfis de usuario.
9. Avaliar migracao de stack.

## Regras de Organizacao

- Commits pequenos e claros.
- Uma funcionalidade por branch quando fizer sentido.
- Atualizar README quando mudar forma de rodar.
- Atualizar este plano quando uma fase mudar.
- Nao versionar credenciais.
- Nao versionar ambiente virtual.
- Antes de grandes mudancas, validar impacto no fluxo de atendimento.
