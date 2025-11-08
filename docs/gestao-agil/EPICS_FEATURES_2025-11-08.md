# Epics, Features e Stories — Planejamento PO / Gestor de Portfólio

# Origin: DECISAO-002

## Visão geral
Documento criado por PO/Gestor de Portfólio em 2025-11-08 para operacionalizar a estratégia `FRONTEND-FIRST` com governança integrada.

Cada Epic abaixo possui Features, e cada Feature possui Histórias (User Stories) e Tasks mínimas para execução (acceptance criteria, estimativa e owner sugerido).

---

## EPIC 1 — MVP Cliente: Meu Home & Forex (Entrega visível)
Prioridade: P0
Objetivo: Entregar valor perceptível aos stakeholders com um conjunto mínimo funcional (Meu Home + Lista Forex) em entregas verticais.

Features:

- FEATURE 1.1: Meu Home — Dashboard Pessoal (vertical slice)
  - User Story 1.1.1: Como usuário, quero ver resumo de posições e P&L para entender performance rápida.
    - Tasks:
      - T1: Backend: endpoint `GET /api/v1/dashboard/summary` (mock → real) — Owner: Backend
      - T2: Frontend: Tela `Meu Home` com cards P&L e posições — Owner: Frontend
      - T3: Tests: 1 E2E básico (abrir tela + dados) — Owner: QA
      - Aceitação: Endpoint retorna JSON com fields (total_pnl, positions_count) e frontend mostra cards corretamente.
      - Estimativa: 3d

- FEATURE 1.2: Lista de pares Forex (28 pares)
  - User Story 1.2.1: Como investidor, quero ver lista de 28 pares com preço e spread para analisar oportunidades.
    - Tasks:
      - T1: Backend: endpoint `GET /api/v1/market/forex` com dados mock e cache Redis — Owner: Backend
      - T2: Frontend: componente listagem com filtros e busca — Owner: Frontend
      - T3: Tests: 2 integrações + 1 E2E (carregar lista) — Owner: QA
      - Aceitação: Lista carrega <200ms p95 com mock; filtros funcionam.
      - Estimativa: 4d

---

## EPIC 2 — Governança, Segurança e Conformidade
Prioridade: P0 (paralelo às entregas FE)
Objetivo: Garantir gates, auditoria e compliance para deploys e PRs críticos.

Features:

- FEATURE 2.1: Gates CI para PRs sensíveis
  - User Story 2.1.1: Como Tech Lead, quero que PRs que tocam infra/modelos/dados presidenciais incluam referência `DECISAO-002` e passem checks automáticos.
    - Tasks:
      - T1: Criar `.github/workflows/check-decisao.yml` — Owner: DevOps
      - T2: Criar `docs/governanca/decisoes/decisions.json` (machine-readable) — Owner: PO/Docs
      - T3: Template PR atualizado com checklist obrigatório — Owner: PO
      - Aceitação: PRs sem referência falham; workflow reporta motivo.
      - Estimativa: 3d

- FEATURE 2.2: Política de mascaramento e audit trails para dados sensíveis
  - Tasks:
    - T1: Definir política e instruções em `docs/07-GOVERNANCA/` — Owner: Legal/PO
    - T2: Implementar middleware simples de masking em endpoints que retornam PII — Owner: Backend
    - Aceitação: Endpoints com dados sensíveis retornam campos mascarados por default.
    - Estimativa: 5d

---

## EPIC 3 — Backend Modularization & Infra (DT-001)
Prioridade: P0 (refactor contínuo com entregas incrementais)
Objetivo: Consolidar módulos por domínio para reduzir débito técnico.

Features:

- FEATURE 3.1: Migrar serviços para `/modules/portfolio_intelligence`
  - Tasks:
    - T1: Criar estrutura de pastas (domain/application/infrastructure/interfaces) — Owner: Backend
    - T2: Migrar 20 arquivos críticos e validar imports — Owner: Backend
    - T3: ADR-002: documentar decisão DDD + modular — Owner: PO/Tech Lead
    - Aceitação: Imports passam em testes de import; pylint sem cyclic-import.
    - Estimativa: 10d (incremental)

---

## EPIC 4 — Testes E2E & CI (DT-002)
Prioridade: P0/P1
Objetivo: Estabelecer Playwright + fixtures + integração CI para reduzir regressões.

Features:

- FEATURE 4.1: Setup Playwright e testes críticos
  - Tasks:
    - T1: Instalar Playwright e configurar `tests/e2e/conftest.py` — Owner: QA/DevOps
    - T2: Escrever 5 testes E2E críticos (login, dashboard, export pdf, recommendations) — Owner: QA
    - T3: Integrar CI (GitHub Actions) para rodar E2E em PRs críticos — Owner: DevOps
    - Aceitação: 5 E2E passam em CI no ambiente de PR (com mocks) — Estimativa: 8d

---

## EPIC 5 — Dados & Migrations (DT-003)
Prioridade: P0 a P1
Objetivo: Mover de SQLite para PostgreSQL com Alembic para suportar multi-tenant.

Features:

- FEATURE 5.1: Docker Compose com Postgres + Redis
  - Tasks:
    - T1: Criar `docker-compose.yml` (postgres:15 + redis:7) — Owner: DevOps
    - T2: Inicializar Alembic e criar primeiras migrations — Owner: Backend/DBA
    - Aceitação: Ambiente dev com Postgres local reproduzível; migrations aplicam sem erro.
    - Estimativa: 5d

---

## Processo Agil pro backlog (PO)
1. Criar Epics → dividir em Features → decompor em Stories → criar Tasks técnicas/QA/Docs/DevOps.
2. Cada Story deve ter: descrição, critérios de aceitação, estimativa (dias), owner e dependências.
3. Definir sprint size (2 semanas) e alocar 2 engenheiros full-time como baseline.
4. Tags obrigatórias: `Origin: DECISAO-002` em alterações de governança; `FE` para frontend-first features.

---

## Próximas ações imediatas (PO)
- Popular backlog com todas as Stories/Tasks (automatizar via script ou criar PR com arquivo `docs/gestao-agil/EPICS_FEATURES_2025-11-08.md`).
- Gerar tickets para as 76 tarefas impedidas (prioridade de desbloqueio) e atribuir owners.
- Agendar reunião com Diretores: revisão de Epics e aprovação de recursos (2 engenheiros full-time + DevOps/QA).

Assinado: PO / Gestor de Portfólio — 2025-11-08
