# 🗓️ Roadmap: Débito Técnico → MVP Production-Ready

**Versão:** 1.0
**Data:** 2025-11-07
**Objetivo:** Transformar Agent Especialista de monolito SQLite em arquitetura modular production-ready

---

## 📊 MÉTRICAS DE ACOMPANHAMENTO DE GOVERNANÇA E TREINAMENTO

**Status:** Pendente de aprovação formal dos stakeholders

- Percentual de PRs referenciando decisões (DECISAO-002)
- Percentual de adesão ao template de PR
- Participação em sessões de treinamento
- Feedback do time sobre novas regras
- Número de exceções registradas
- Tempo médio para aprovação de exceções

---

## ⚠️ STATUS DE APROVAÇÃO FORMAL

> As iniciativas estratégicas deste roadmap estão aguardando validação formal dos seguintes stakeholders:

> - Presidente (Hub Financeiro Inteligente)
> - Product Owner (Agent Especialista)
> - Tech Lead
> - CTO
> - Diretor Financeiro

---

## 📊 VISÃO EXECUTIVA

### Status Atual (Linha de Base)

```text
📂 Estrutura: Monolito (200+ arquivos /backend root)
🗄️ Database: SQLite (single-user, não escala)
🧪 Testes: <30% cobertura, ZERO E2E
📝 Docs: Ausente (sem OpenAPI, sem guias)
👀 Observability: Nenhuma (sem logs estruturados)
📏 Naming: Inconsistente (monitor_*, analisador_*, consultar_*)
```

### Meta Final (Production-Ready)

```text
📂 Estrutura: Modular DDD (/modules/portfolio_intelligence/...)
🗄️ Database: PostgreSQL + Redis + Docker Compose
🧪 Testes: 80% cobertura + E2E críticos (Playwright)
📝 Docs: OpenAPI completo + guias de deploy
👀 Observability: Prometheus + Grafana + alertas
📏 Naming: Padrão DDD (*_service.py, *_repository.py)
```

**Timeline:** 8 sprints (16 semanas / 4 meses)
**Esforço:** 2 engenheiros fulltime
**ROI:** Após resolução, velocidade aumenta 2-3x (menos rework, menos bugs)

---

## 🎯 FASE 1: FUNDAÇÃO (Sprints 1-3) - CRÍTICO

**Objetivo:** Resolver bloqueadores P0 que impedem MVP escalar

### Sprint 0-1: Governança e Conformidade (DT-012, DT-013)

**Problema:**

```text
❌ Ausência de mecanismos automáticos que garantam que decisões estratégicas sejam aplicadas em mudanças críticas
❌ Risco de alterações não conformes em áreas sensíveis (infra, modelos, docs de governança)
```

**Solução:**

- Criar `.github/COPILOT_INSTRUCTIONS.md` (regras obrigatórias)
- Adicionar `docs/governanca/decisoes/decisions.json` (machine-readable)
- Implementar workflow CI para checar PRs e template de PR com checklist
- Treinar time e documentar processo de exceção

**Esforço:** 1 sprint (Governança rápida)
**Prioridade:** 🔴 P0
**Owner:** Tech Lead + PO

---

## Ajuste de Prioridade: FRONTEND-FIRST (Sprints 1-3)

> Por determinação do PO/Presidência, priorizar entregas de frontend (entregas verticais) nas próximas sprints para demonstrar valor tangível a acionistas. A governança permanece obrigatória e será mantida em paralelo.

### Sprint 1 (Entrega Rápida)

- FEAT-001: MVP Dashboard Público (vertical slice) — Frontend mínimo + endpoint backend mínimo + testes básicos

### Sprint 2 (Entrega Rápida)

- FEAT-002: Lista de pares Forex (frontend) + backend mock
- FEAT-003: Formulário de Demo / Abertura de Conta (fluxo mínimo)

### Sprint 3 (Entrega Rápida)

- FEAT-004: Painel de Feedback in-app + coleta de feedbacks para PO

**Esforço:** 3 sprints (entregas visíveis semanais)
**Prioridade:** 🔴 Muito Alta (demonstração de valor)
**Notas:** Registrar aprovação formal da Presidência/PO em ata; manter compliance com DT-012/DT-013 em paralelo.


### Sprint 1-2: DT-001 - Backend Modularization

**Problema:**

```text
❌ 200 arquivos na raiz /backend sem organização
❌ Funções duplicadas (3 implementações de "calcular risco")
❌ Imports circulares frequentes
❌ Impossível onboarding novo dev (<1 semana)
```

**Solução:**

Estrutura modular por domínio (Domain-Driven Design):

```text
backend/
├── modules/
│   ├── portfolio_intelligence/       # Módulo principal MVP
│   │   ├── domain/
│   │   │   ├── entities/            # Position, Asset, Portfolio
│   │   │   ├── value_objects/       # Money, Percentage, CorrelationScore
│   │   │   └── repositories/        # Interfaces (abstrações)
│   │   ├── application/
│   │   │   ├── services/            # PortfolioService, RiskService
│   │   │   ├── use_cases/           # GetPortfolioAnalysisUseCase
│   │   │   └── dtos/                # Request/Response DTOs
│   │   ├── infrastructure/
│   │   │   ├── repositories/        # PostgreSQL implementations
│   │   │   ├── external/            # APIs terceiros (B3, Alpha Vantage)
│   │   │   └── cache/               # Redis client
│   │   └── interfaces/
│   │       ├── api/                 # FastAPI routers
│   │       └── cli/                 # Click commands
│   ├── market_data/                  # Módulo dados mercado
│   └── shared/                       # Código compartilhado (utils, config)
├── tests/
│   ├── unit/                         # Testes isolados
│   ├── integration/                  # Testes com BD/APIs
│   └── e2e/                          # Testes ponta-a-ponta
└── config/
```

**Tasks (Sprint 1):**

1. [ ] Criar estrutura de pastas (`/modules/portfolio_intelligence/domain/...`)
2. [ ] Migrar 20 arquivos principais (analisador_risco, monitor_portfolio, consultar_historico)
3. [ ] Estabelecer naming convention (`*_service.py`, `*_repository.py`, `*_entity.py`)
4. [ ] Atualizar imports quebrados (refatoração automática PyCharm/VSCode)
5. [ ] Escrever ADR-002 (Decisão Arquitetura: DDD + Modular)

**Tasks (Sprint 2):**

6. [ ] Migrar 80 arquivos restantes (batch de 20/dia)
7. [ ] Eliminar duplicações (consolidar 3 `calcular_risco` em 1 `RiskService`)
8. [ ] Criar `__init__.py` com exports públicos (API limpa)
9. [ ] Atualizar `requirements.txt` com dependências explícitas por módulo
10. [ ] Documentar guia de modularização (`docs/arquitetura/GUIA_MODULARIZACAO.md`)

**Critérios de Sucesso:**

- ✅ 100% arquivos migrados para `/modules/`
- ✅ Zero imports circulares (validado por `pylint --disable=all --enable=cyclic-import`)
- ✅ Build time <30s (antes: 2min)
- ✅ Onboarding novo dev <3 dias (antes: 2 semanas)

---

### Sprint 2: DT-002 - E2E Test Framework

**Problema:**

```text
❌ Proposta de "vertical slices" requer validação frontend→backend→BD
❌ Bugs em produção não detectados (ex: botão "Exportar PDF" quebrado 1 semana)
❌ Refatorações arriscadas (medo de quebrar algo sem perceber)
```

**Solução:**

Setup Playwright para Python com 5-10 testes críticos:

```python
# tests/e2e/test_portfolio_dashboard.py
import pytest
from playwright.sync_api import Page, expect

def test_portfolio_manager_happy_path(page: Page, auth_token: str):
    """
    E2E: Gerente de Portfólio visualiza dashboard e recebe recomendação IA
    """
    # 1. Login
    page.goto("http://localhost:8501/login")
    page.fill("#username", "gerente@fundo.com")
    page.fill("#password", "senha123")
    page.click("button:has-text('Entrar')")

    # 2. Dashboard carrega com posições
    expect(page.locator("h1")).to_contain_text("Dashboard Executivo")
    expect(page.locator("#positions-table tr")).to_have_count(32)  # 32 posições mock

    # 3. Gráfico P&L renderizado
    expect(page.locator("#pnl-chart")).to_be_visible()
    expect(page.locator("#pnl-chart .bar")).to_have_count(30)  # 30 dias

    # 4. Recomendação IA aparece
    page.click("button:has-text('Gerar Recomendações')")
    expect(page.locator(".ai-recommendation")).to_contain_text("Fechar posição USDBRL")
    expect(page.locator(".confidence-score")).to_contain_text("92%")

    # 5. Exportar relatório PDF
    with page.expect_download() as download_info:
        page.click("button:has-text('Exportar PDF')")
    download = download_info.value
    assert download.suggested_filename == "portfolio_2025-11-07.pdf"
```

**Tasks:**

1. [ ] Instalar Playwright (`pip install playwright; playwright install chromium`)
2. [ ] Configurar fixtures (`tests/e2e/conftest.py` com BD de teste, auth mock)
3. [ ] Escrever 5 testes críticos:
   - Login + Dashboard load
   - Visualizar posições + drill-down por ativo
   - Receber recomendação IA + aplicar ação
   - Alerta de risco dispara + notificação
   - Exportar relatório PDF/Excel
4. [ ] Integrar CI/CD (GitHub Actions roda E2E em PRs)
5. [ ] Documentar guia E2E (`docs/desenvolvimento/GUIA_TESTES_E2E.md`)

**Critérios de Sucesso:**

- ✅ 5 E2E tests passando (happy paths principais)
- ✅ CI/CD roda E2E automaticamente (<5min)
- ✅ Cobertura E2E >50% dos user flows críticos
- ✅ Bugs em produção caem 70% (histórico vs próximo sprint)

---

### Sprint 3: DT-003 - PostgreSQL + Docker

**Problema:**

```text
❌ SQLite não suporta multi-tenant (clientes compartilham BD)
❌ Performance ruim (>10k posições portfolio = 30s query)
❌ Backup manual (risco de perda de dados)
❌ Deploy complexo (dev precisa instalar PostgreSQL local)
```

**Solução:**

Docker Compose com PostgreSQL 15 + Redis 7:

```yaml
# docker-compose.yml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: agent_financeiro
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  backend:
    build: ./backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    environment:
      DATABASE_URL: postgresql://agent:${DB_PASSWORD}@postgres:5432/agent_financeiro
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"

volumes:
  postgres_data:
  redis_data:
```

**Tasks:**

1. [ ] Criar `docker-compose.yml` com PostgreSQL + Redis
2. [ ] Setup Alembic migrations (`alembic init alembic/`)
3. [ ] Migrar schema SQLite → PostgreSQL:
   - Exportar schema atual (`sqlite3 data.db .schema > schema.sql`)
   - Converter para PostgreSQL syntax (`AUTOINCREMENT` → `SERIAL`)
   - Criar migration inicial (`alembic revision --autogenerate -m "initial"`)
4. [ ] Implementar Row-Level Security (RLS) multi-tenant:

```sql
-- scripts/init_db.sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    asset_symbol VARCHAR(10) NOT NULL,
    quantity DECIMAL(18,8) NOT NULL,
    avg_price DECIMAL(18,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row-Level Security
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON positions
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

5. [ ] Atualizar conexão BD (`backend/config/database.py`):

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://agent:password@localhost/agent_financeiro")

engine = create_async_engine(DATABASE_URL, echo=True, pool_size=20, max_overflow=10)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

6. [ ] Manter SQLite para testes unitários (mais rápido, isolado)
7. [ ] Documentar setup Docker (`docs/manuais/SETUP_DOCKER.md`)

**Critérios de Sucesso:**

- ✅ Docker Compose sobe ambiente completo (`docker-compose up` < 2min)
- ✅ PostgreSQL com RLS multi-tenant funcionando
- ✅ Migrations Alembic aplicadas automaticamente
- ✅ Performance queries melhorou >5x (30s → <5s)
- ✅ Dev novo consegue setup ambiente <10min (antes: 4h)

---

## 🔧 FASE 2: QUALIDADE (Sprints 3-5) - ALTO IMPACTO

**Objetivo:** Elevar padrão de código e reduzir débito técnico acumulado

### Sprint 3-4: DT-004 - Naming Standardization

**Problema:**

```text
❌ Naming inconsistente:
   - monitor_portfolio.py (snake_case)
   - analisadorRisco.py (camelCase)
   - ConsultarHistorico.py (PascalCase)
   - calcular-indicadores.py (kebab-case)
❌ Funções não descrevem ação (ex: `processar()` - processar o quê?)
❌ Violação princípio DDD (nomes técnicos vs domínio negócio)
```

**Solução:**

Adotar Domain-Driven Design naming:

```text
SERVIÇOS (*_service.py):
  ✅ portfolio_service.py
  ✅ risk_service.py
  ✅ market_data_service.py

REPOSITÓRIOS (*_repository.py):
  ✅ position_repository.py
  ✅ asset_repository.py

ENTIDADES (domain/entities/*.py):
  ✅ portfolio.py (class Portfolio)
  ✅ position.py (class Position)

USE CASES (application/use_cases/*.py):
  ✅ get_portfolio_analysis_use_case.py
  ✅ generate_ai_recommendation_use_case.py

CLIENTES EXTERNOS (*_client.py):
  ✅ alpha_vantage_client.py
  ✅ b3_api_client.py
```

**Tasks (Sprint 3):**

1. [ ] Criar `docs/arquitetura/NAMING_CONVENTIONS.md` com guia completo
2. [ ] Refatorar 50 arquivos prioritários (core business logic)
3. [ ] Atualizar imports automaticamente (script Python + regex)
4. [ ] Adicionar pylint custom rules (`pylintrc` com naming patterns)

**Tasks (Sprint 4):**

5. [ ] Refatorar 150 arquivos restantes (batch de 30/dia)
6. [ ] Renomear funções ambíguas (`processar()` → `processar_sinal_compra()`)
7. [ ] Adicionar docstrings descritivas (1 linha mínimo):

```python
def calcular_risco_portfolio(posicoes: List[Position], volatilidade_mercado: float) -> RiskScore:
    """
    Calcula risco agregado do portfolio baseado em volatilidade individual
    e correlação entre ativos.

    Args:
        posicoes: Lista de posições ativas do portfolio
        volatilidade_mercado: VIX ou índice equivalente (0-100)

    Returns:
        Score de risco [0.0-1.0] onde 1.0 = risco extremo
    """
    # implementação
```

8. [ ] Validar com script (`scripts/validate_naming.py` verifica padrões)
9. [ ] Code review rigoroso (Tech Lead aprova 100% arquivos renomeados)
10. [ ] Atualizar CONTRIBUTING.md com regras naming

**Critérios de Sucesso:**

- ✅ 100% arquivos seguem padrão DDD
- ✅ Pylint naming score 10/10
- ✅ Onboarding novo dev: entende propósito arquivo em <10s (antes: 2min)
- ✅ Zero ambiguidade em nomes de funções

---

### Sprint 4-5: DT-005 - 80% Test Coverage

**Problema:**

```text
❌ Coverage atual estimado <30%
❌ Funções críticas sem testes (ex: calcular_risco_portfolio)
❌ Bugs em produção frequentes (3-5 por sprint)
❌ Refatorações com medo (não sabe se quebrou algo)
```

**Solução:**

Aumentar cobertura gradualmente para 80%:

**Tasks (Sprint 4 - 30%→55%):**

1. [ ] Configurar pytest-cov (`pytest --cov=backend --cov-report=html`)
2. [ ] Identificar top 20 funções críticas sem testes:

```bash
# Script para achar funções críticas sem testes
pytest --cov=backend --cov-report=term-missing | grep "0%"
```

3. [ ] Escrever testes unitários para 20 funções críticas:

```python
# tests/unit/test_risk_service.py
import pytest
from backend.modules.portfolio_intelligence.application.services import RiskService

@pytest.fixture
def risk_service():
    return RiskService()

def test_calcular_risco_portfolio_baixo_quando_diversificado(risk_service):
    """Dado portfolio diversificado (10 ativos descorrelacionados)
       Quando calcula risco
       Então retorna score <0.3 (baixo risco)"""
    posicoes = [
        Position("USDBRL", 1000, 5.20),
        Position("EURBRL", 800, 6.10),
        Position("BTCUSD", 0.5, 45000),
        # ... 7 mais
    ]
    volatilidade = 15.0  # VIX baixo

    score = risk_service.calcular_risco_portfolio(posicoes, volatilidade)

    assert score < 0.3, "Portfolio diversificado deve ter risco baixo"
    assert score > 0.0, "Score nunca pode ser zero"

def test_calcular_risco_portfolio_alto_quando_concentrado(risk_service):
    """Dado portfolio concentrado (1 ativo 100% exposição)
       Quando calcula risco
       Então retorna score >0.7 (alto risco)"""
    posicoes = [Position("BTCUSD", 10, 45000)]  # 100% crypto
    volatilidade = 80.0  # VIX alto

    score = risk_service.calcular_risco_portfolio(posicoes, volatilidade)

    assert score > 0.7, "Portfolio concentrado + volatilidade alta = risco extremo"
```

4. [ ] Adicionar testes de integração (10 cenários críticos):

```python
# tests/integration/test_portfolio_service_integration.py
@pytest.mark.asyncio
async def test_criar_portfolio_persiste_no_banco(db_session, tenant_id):
    """Testa fluxo completo: criar portfolio → salvar BD → recuperar"""
    service = PortfolioService(db_session)

    # Criar
    portfolio = await service.criar_portfolio(tenant_id, "Fundo Agressivo")
    assert portfolio.id is not None

    # Recuperar
    portfolio_bd = await service.buscar_portfolio(portfolio.id)
    assert portfolio_bd.nome == "Fundo Agressivo"
    assert portfolio_bd.tenant_id == tenant_id
```

5. [ ] Configurar CI/CD para falhar se coverage <55% (gate de qualidade)

**Tasks (Sprint 5 - 55%→80%):**

6. [ ] Escrever testes para módulos secundários (market_data, shared)
7. [ ] Adicionar testes de edge cases (valores nulos, negativos, overflow):

```python
def test_calcular_risco_com_volatilidade_negativa_levanta_erro(risk_service):
    """Volatilidade negativa é inválida, deve levantar ValueError"""
    with pytest.raises(ValueError, match="Volatilidade não pode ser negativa"):
        risk_service.calcular_risco_portfolio([], volatilidade=-10)
```

8. Property-based testing para funções matemáticas (Hypothesis):

```python
from hypothesis import given, strategies as st

@given(
    quantidade=st.floats(min_value=0.01, max_value=1e6),
    preco=st.floats(min_value=0.01, max_value=1e6)
)
def test_calcular_valor_posicao_sempre_positivo(quantidade, preco):
    """Valor posição nunca pode ser negativo (property-based test)"""
    valor = calcular_valor_posicao(quantidade, preco)
    assert valor > 0
```

9. Mutation testing (verificar se testes realmente detectam bugs):

```bash
pip install mutpy
mutpy --target backend/modules/portfolio_intelligence --unit-test tests/ --report-html htmlmut
```

10. Atualizar DoD: "Coverage >80% ou justificar no PR"

**Critérios de Sucesso:**

- ✅ Coverage 80% overall (pytest-cov)
- ✅ 100% cobertura em funções críticas de risco
- ✅ CI/CD bloqueia merge se coverage <80%
- ✅ Bugs em produção caem 80% (histórico vs próximo trimestre)
- ✅ Mutation score >75% (testes realmente eficazes)

---

### Sprint 5: DT-006 - API Documentation

**Problema:**

```text
❌ Zero documentação API (frontend não sabe contratos)
❌ Integrações externas difíceis (parceiros pedem "qual endpoint usar?")
❌ Onboarding frontend devs lento (precisam ler código backend)
```

**Solução:**

OpenAPI/Swagger completo + guias de integração:

**Tasks:**

1. [ ] Configurar FastAPI Swagger automático:

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Agent Especialista Mercado Financeiro API",
    description="API REST para gestão de portfolios com IA",
    version="1.0.0",
    contact={
        "name": "Time Backend",
        "email": "backend@agentfinanceiro.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Adicionar exemplos customizados
    openapi_schema["components"]["schemas"]["PortfolioAnalysisResponse"]["example"] = {
        "portfolio_id": "123e4567-e89b-12d3-a456-426614174000",
        "total_value": 1250000.50,
        "risk_score": 0.42,
        "recommendations": [
            {
                "action": "SELL",
                "asset": "USDBRL",
                "confidence": 0.92,
                "reason": "Correlação com EURBRL quebrada, risco de reversão"
            }
        ]
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

2. [ ] Documentar todos endpoints com exemplos:

```python
@app.post("/api/v1/portfolios/{portfolio_id}/analysis",
          response_model=PortfolioAnalysisResponse,
          summary="Analisa portfolio e gera recomendações IA",
          description="""
          Endpoint principal para obter análise completa de portfolio:
          - Calcula risco agregado (correlações + volatilidade)
          - Gera recomendações IA acionáveis
          - Retorna alertas preditivos

          **Exemplo de uso:**
          ```bash
          curl -X POST https://api.agentfinanceiro.com/api/v1/portfolios/123/analysis \
               -H "Authorization: Bearer $TOKEN" \
               -H "Content-Type: application/json" \
               -d '{"include_recommendations": true, "timeframe_days": 30}'
          ```
          """,
          responses={
              200: {
                  "description": "Análise gerada com sucesso",
                  "content": {
                      "application/json": {
                          "example": {
                              "portfolio_id": "123",
                              "risk_score": 0.42,
                              "recommendations": [...]
                          }
                      }
                  }
              },
              404: {"description": "Portfolio não encontrado"},
              401: {"description": "Token inválido ou expirado"}
          },
          tags=["Portfolio Intelligence"])
async def analisar_portfolio(portfolio_id: str, request: AnalysisRequest):
    # implementação
```

3. [ ] Gerar documentação estática (Redoc + Swagger UI):

```python
from fastapi.responses import HTMLResponse

@app.get("/docs/redoc", response_class=HTMLResponse, include_in_schema=False)
async def redoc_html():
    return get_redoc_html(openapi_url="/openapi.json", title="API Docs - Redoc")
```

4. [ ] Criar guia de integração (`docs/api/GUIA_INTEGRACAO.md`):

```markdown
# Guia de Integração API

## Autenticação

Todos endpoints requerem token JWT no header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Fluxo Típico

1. Autenticar (`POST /api/v1/auth/login`)
2. Criar portfolio (`POST /api/v1/portfolios`)
3. Adicionar posições (`POST /api/v1/portfolios/{id}/positions`)
4. Obter análise (`POST /api/v1/portfolios/{id}/analysis`)

## Rate Limits

- 1000 requests/hora por API key
- 10 requests/segundo burst

## Webhooks

Configure webhooks para receber alertas em tempo real:

```json
POST https://seu-servidor.com/webhooks
{
  "event": "risk_alert",
  "portfolio_id": "123",
  "risk_score": 0.85,
  "timestamp": "2025-11-07T10:30:00Z"
}
```

5. [ ] Publicar docs em URL pública (`docs.agentfinanceiro.com`)
6. [ ] Adicionar exemplos em múltiplas linguagens (Python, JavaScript, cURL)

**Critérios de Sucesso:**

- ✅ 100% endpoints documentados no Swagger
- ✅ Exemplos funcionais para top 10 endpoints
- ✅ Guia de integração completo publicado
- ✅ Frontend devs conseguem integrar sem perguntar backend (pesquisa: 100% satisfação)
- ✅ Tempo de onboarding parceiro externo: 4h → 1h

---

## 📈 FASE 3: MATURIDADE (Sprints 6-8) - NICE-TO-HAVE

**Objetivo:** Elevar sistema a nível enterprise-grade

### Sprint 6: DT-007 - Legacy Code Audit

**Problema:**

```text
❌ 50% do código pode estar obsoleto (features descontinuadas)
❌ Dependências não usadas (requirements.txt com 80 pacotes, usa 40)
❌ Código comentado há 6+ meses (ninguém lembra por quê)
```

**Solução:**

Auditoria completa e limpeza:

**Tasks:**

1. [ ] Análise de cobertura de uso (instrumentar código com logs):

```python
# Adicionar temporariamente em cada módulo
import logging
logger = logging.getLogger(__name__)

def funcao_possivelmente_obsoleta():
    logger.warning(f"AUDIT: funcao_possivelmente_obsoleta foi chamada em {datetime.now()}")
    # código original
```

2. [ ] Rodar em produção 2 semanas, analisar logs
3. [ ] Categorizar arquivos:
   - **USE:** Chamado >10x (manter)
   - **DEPRECATE:** Chamado <3x (marcar @deprecated, remover Sprint 7)
   - **DELETE:** Nunca chamado (deletar imediatamente)
4. [ ] Remover código comentado (`git log` já preserva histórico):

```bash
# Script para achar código comentado
grep -r "^#.*def\|^#.*class" backend/ | wc -l
```

5. [ ] Limpar `requirements.txt`:

```bash
pip install pipreqs
pipreqs backend/ --force  # Gera requirements.txt baseado em imports reais
```

6. [ ] Documentar decisões de remoção (`docs/arquitetura/ADR-003-REMOCOES_LEGACY.md`)

**Critérios de Sucesso:**

- ✅ 50% redução tamanho codebase (200 arquivos → 100)
- ✅ requirements.txt enxuto (80 → 40 pacotes)
- ✅ Zero código comentado
- ✅ Build time 50% mais rápido (CI/CD: 5min → 2.5min)

---

### Sprint 7-8: DT-008 - Observability

**Problema:**

```text
❌ Bugs em produção demoram 4-8h para diagnosticar (sem logs estruturados)
❌ Performance issues invisíveis (não sabe qual query lenta)
❌ Downtime não detectado (cliente avisa antes do time)
```

**Solução:**

Stack completa de observabilidade:

```text
📊 Métricas: Prometheus
📈 Dashboards: Grafana
🔍 Logs: Structlog → Loki
🚨 Alertas: Alertmanager → Slack/PagerDuty
📉 APM: OpenTelemetry (traces distribuídos)
```

**Tasks (Sprint 7):**

1. [ ] Setup Prometheus + Grafana via Docker:

```yaml
# docker-compose.observability.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    depends_on:
      - prometheus
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
```

2. [ ] Instrumentar backend com Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, Gauge

# Métricas de negócio
portfolios_criados = Counter('portfolios_criados_total', 'Total de portfolios criados')
recomendacoes_geradas = Counter('recomendacoes_ia_geradas_total', 'Recomendações IA geradas')
risk_score_atual = Gauge('portfolio_risk_score', 'Risk score atual', ['portfolio_id'])

# Métricas técnicas
request_duration = Histogram('http_request_duration_seconds', 'Duração requests HTTP', ['method', 'endpoint'])

@app.post("/api/v1/portfolios")
@request_duration.labels(method="POST", endpoint="/portfolios").time()
async def criar_portfolio(...):
    portfolio = await service.criar_portfolio(...)
    portfolios_criados.inc()  # Incrementa contador
    return portfolio
```

3. [ ] Adicionar logs estruturados (Structlog):

```python
import structlog

logger = structlog.get_logger()

async def analisar_portfolio(portfolio_id: str):
    logger.info("iniciando_analise_portfolio",
                portfolio_id=portfolio_id,
                tenant_id=current_tenant.id,
                user_id=current_user.id)

    try:
        analise = await service.analisar(portfolio_id)
        logger.info("analise_portfolio_concluida",
                    portfolio_id=portfolio_id,
                    risk_score=analise.risk_score,
                    num_recommendations=len(analise.recommendations),
                    duration_ms=duration)
        return analise
    except Exception as e:
        logger.error("erro_analise_portfolio",
                     portfolio_id=portfolio_id,
                     error=str(e),
                     traceback=traceback.format_exc())
        raise
```

4. [ ] Criar 5 dashboards Grafana essenciais:
   - **Health Overview:** CPU, memória, disk, requests/s, latência p50/p95/p99
   - **Business Metrics:** Portfolios criados, recomendações geradas, usuários ativos
   - **Database Performance:** Slow queries, connection pool, cache hit rate
   - **Errors & Alerts:** Taxa de erro 5xx, exceções não tratadas, alertas disparados
   - **User Journey:** Funil conversão (signup → primeiro portfolio → primeira recomendação)

5. [ ] Configurar alertas críticos (Alertmanager):

```yaml
# alertmanager.yml
groups:
  - name: critical
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Taxa de erro >5% por 2min"
          description: "{{ $value }}% requests retornando 5xx"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL DOWN"
          description: "Banco de dados inacessível há 1min"
```

**Tasks (Sprint 8):**

6. [ ] Adicionar distributed tracing (OpenTelemetry):

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

async def analisar_portfolio(portfolio_id: str):
    with tracer.start_as_current_span("analisar_portfolio") as span:
        span.set_attribute("portfolio_id", portfolio_id)

        with tracer.start_as_current_span("buscar_posicoes"):
            posicoes = await repo.buscar_posicoes(portfolio_id)

        with tracer.start_as_current_span("calcular_risco"):
            risco = risk_service.calcular_risco(posicoes)

        with tracer.start_as_current_span("gerar_recomendacoes_ia"):
            recomendacoes = await ia_service.gerar(posicoes, risco)

        return PortfolioAnalysis(risco, recomendacoes)
```

7. [ ] Implementar health checks (`/health`, `/ready`):

```python
@app.get("/health")
async def health_check():
    """Verifica se serviço está vivo (liveness probe)"""
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Verifica se serviço está pronto para receber tráfego"""
    try:
        await db.execute("SELECT 1")
        redis_client.ping()
        return {"status": "ready", "dependencies": {"database": "ok", "redis": "ok"}}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")
```

8. [ ] Configurar SLOs (Service Level Objectives):

```yaml
# SLOs documentados em docs/observability/SLOS.md
Availability: 99.9% uptime mensal (max 43min downtime/mês)
Latency p95: <500ms para análise portfolio
Latency p99: <2s para análise portfolio
Error Rate: <0.1% requests retornam 5xx
```

9. [ ] Runbooks para incidentes comuns (`docs/observability/RUNBOOKS/`):

```markdown
# Runbook: Database Connection Pool Exhausted

## Sintomas
- Erro: `sqlalchemy.exc.TimeoutError: QueuePool limit exceeded`
- Alertas: `database_connection_pool_usage > 0.9`

## Diagnóstico
1. Verificar Grafana dashboard "Database Performance"
2. Checar conexões ativas: `SELECT * FROM pg_stat_activity;`
3. Identificar queries longas: `SELECT pid, query FROM pg_stat_activity WHERE state = 'active' AND query_start < NOW() - INTERVAL '30 seconds';`

## Mitigação Imediata
1. Aumentar pool size temporariamente: `docker-compose restart backend -e SQLALCHEMY_POOL_SIZE=50`
2. Matar queries lentas: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE ...;`

## Resolução Permanente
1. Otimizar queries identificadas (adicionar índices)
2. Implementar timeout de conexão (10s max)
3. Revisar pool size configurado (atualmente 20, pode aumentar para 30)
```

10. [ ] Documentar guia de observabilidade (`docs/observability/GUIA_OBSERVABILIDADE.md`)

**Critérios de Sucesso:**

- ✅ MTTR (Mean Time To Recovery) reduz 80% (4h → 50min)
- ✅ 100% incidentes críticos detectados automaticamente (não depende de cliente reportar)
- ✅ 5 dashboards Grafana operacionais
- ✅ Alertas Slack funcionando (teste com incidente simulado)
- ✅ SLOs 99.9% uptime alcançado por 2 meses consecutivos

---

## 📘 APRENDIZADOS E MELHORIAS

### Aprendizados da Autoavaliação

1. **Completude:** Identificar gaps no início do planejamento evita retrabalho.
2. **Consistência:** Alinhar análise macro com recomendações técnicas aumenta a clareza.
3. **Riscos:** Mapear riscos por sprint melhora a previsibilidade.
4. **Confiança:** Ajustar confiança com base em dados reduz incertezas.

### Melhorias no Processo

1. **Business Case:** Incorporar projeções de ROI em fases iniciais.
2. **Onboarding:** Validar processos técnicos antes de escalar o time.
3. **Riscos:** Adicionar seção de riscos como padrão em roadmaps futuros.

---

## 📈 NOVAS OPORTUNIDADES

1. **Automação de Onboarding:** Estruturar automação como nova iniciativa no backlog.
2. **Validação Contínua:** Implementar validações incrementais para evitar regressões.
3. **Métricas de Sucesso:** Definir KPIs claros para cada sprint.

---

## 🔴 RISCOS IDENTIFICADOS

### Sprint 1-2: Modularização Backend

**Riscos:**

1. **Regressões:** Refatoração pode introduzir bugs em funcionalidades existentes.
2. **Capacitação:** Time pode não estar familiarizado com DDD.
3. **Integração Contínua:** Falta de pipelines robustos pode atrasar validações.

**Mitigação:**

1. Implementar testes unitários e integração antes da refatoração.
2. Realizar workshops internos sobre DDD.
3. Priorizar configuração de pipelines CI/CD no início do sprint.

---

### Sprint 3-5: Cobertura de Testes e E2E

**Riscos:**

1. **Ferramentas:** Adaptação ao Playwright pode ser lenta.
2. **Cobertura:** Testes podem não cobrir cenários críticos inicialmente.

**Mitigação:**

1. Criar guias rápidos para uso do Playwright.
2. Priorizar cenários críticos no planejamento de testes.

---

### Sprint 6-8: Observabilidade e Auditoria

**Riscos:**

1. **Complexidade:** Configuração de Prometheus e Grafana pode ser demorada.
2. **Alertas:** Alertas mal configurados podem gerar ruído excessivo.

**Mitigação:**

1. Usar templates prontos para configuração inicial.
2. Validar alertas com base em dados históricos.

---

## 📊 MÉTRICAS DE SUCESSO (KPIs)

### Antes (Linha de Base - Sprint 0)

```text
⏱️ Lead Time: 12 dias/US
🐛 Bugs Produção: 3-5/sprint
⚡ Velocity: 8 pontos/sprint
🧪 Test Coverage: <30%
🚀 Deploy Time: 45min
📉 MTTR: 4-8h
👨‍💻 Onboarding Dev: 2 semanas
```

### Depois (Meta - Sprint 8)

```text
⏱️ Lead Time: 3 dias/US (4x melhoria)
🐛 Bugs Produção: <1/sprint (5x redução)
⚡ Velocity: 20 pontos/sprint (2.5x aumento)
🧪 Test Coverage: 80% (2.7x aumento)
🚀 Deploy Time: 8min (5.6x mais rápido)
📉 MTTR: 50min (5x mais rápido)
👨‍💻 Onboarding Dev: 3 dias (5x mais rápido)
```

### ROI (Return On Investment)

**Investimento:**

```text
2 engenheiros × 8 sprints × 2 semanas = 32 semanas-engenheiro
Custo (estimado): R$ 320k (salário + overhead)
```

**Retorno:**

```text
Velocity aumenta 2.5x → Entrega 20 pontos/sprint vs 8 (12 pontos a mais)
Sprints futuros: 12 pontos × 10 sprints = 120 pontos EXTRA em 6 meses
Valor econômico: 120 pontos × R$ 5k/ponto = R$ 600k valor entregue

ROI = (R$ 600k - R$ 320k) / R$ 320k = 87.5% em 6 meses
Payback: 4 meses
```

**Benefícios Intangíveis:**

- ✅ Desenvolvedores mais felizes (menos frustração com código legado)
- ✅ Clientes mais satisfeitos (menos bugs, mais features)
- ✅ Competitividade aumentada (time to market mais rápido)

---

## 🚦 GATES DE QUALIDADE (Não Pular Etapas)

Cada sprint só passa para próximo se:

**Fase 1 (Fundação):**

- [ ] DT-001: 100% arquivos migrados para `/modules/`, zero imports circulares
- [ ] DT-002: 5 E2E tests passando, CI/CD rodando automaticamente
- [ ] DT-003: Docker Compose funcional, PostgreSQL com RLS, migrations aplicadas

**Fase 2 (Qualidade):**

- [ ] DT-004: Pylint naming score 10/10, zero violações
- [ ] DT-005: Coverage 80%, mutation score >75%
- [ ] DT-006: Swagger 100% endpoints, guia integração publicado

**Fase 3 (Maturidade):**

- [ ] DT-007: Codebase reduzido 50%, requirements.txt limpo
- [ ] DT-008: 5 dashboards Grafana, alertas Slack funcionando, SLOs 99.9%

**Validação Final:**

- [ ] PO aprova em Sprint Review (demo funcionando)
- [ ] Tech Lead aprova code review (qualidade OK)
- [ ] Scrum Master valida DoD (todos critérios atendidos)

---

## 📅 CRONOGRAMA VISUAL

```text
Sprint 1-2: ████████░░░░░░░░░░░░░░░░ DT-001 (Backend Modularization)
Sprint 2:   ░░░░░░░░████░░░░░░░░░░░░ DT-002 (E2E Framework)
Sprint 3:   ░░░░░░░░░░░░████░░░░░░░░ DT-003 (PostgreSQL + Docker)
Sprint 3-4: ░░░░░░░░░░░░░░░░████████ DT-004 (Naming Standards)
Sprint 4-5: ░░░░░░░░░░░░░░░░░░░░████████ DT-005 (80% Coverage)
Sprint 5:   ░░░░░░░░░░░░░░░░░░░░░░░░████ DT-006 (API Docs)
Sprint 6:   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░████ DT-007 (Legacy Audit)
Sprint 7-8: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████ DT-008 (Observability)
```

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

**Hoje (2025-11-07):**

1. [ ] Apresentar roadmap para PO + Tech Lead + Scrum Master (30min)
2. [ ] Obter aprovação formal (assinatura virtual)
3. [ ] Criar issues no backlog (8 épicos DT-001 a DT-008)

**Semana 1 (Sprint 1):**

4. [ ] Kickoff DT-001: Criar estrutura `/modules/portfolio_intelligence/`
5. [ ] Migrar 20 arquivos prioritários
6. [ ] Estabelecer naming convention (docs + pylintrc)

**Sprint Planning (próximo sprint):**

7. [ ] Comprometer DT-001 completo (2 sprints)
8. [ ] Reservar 20% capacidade para bugs/support (WIP limit)

---

**Aprovações:**

| Papel | Nome | Data | Status |
|-------|------|------|--------|
| Product Owner | [Nome] | YYYY-MM-DD | ⏳ Pendente |
| Tech Lead | [Nome] | YYYY-MM-DD | ⏳ Pendente |
| Scrum Master | [Nome] | YYYY-MM-DD | ⏳ Pendente |

---

**Próxima Revisão:** Sprint 3 (validar se Fase 1 foi bem-sucedida)

