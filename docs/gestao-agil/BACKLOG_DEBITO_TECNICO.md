# Backlog de Débito Técnico - Agent Especialista

**Criado:** 2025-11-07  
**Responsável:** Tech Lead + Engenheiros  
**Objetivo:** Resolver débitos técnicos ANTES de escalar desenvolvimento de módulos

---

## 🔴 CRÍTICO (Bloqueia MVP)

### DT-001: Refatoração Modularização Backend

**Problema:**
- 200 arquivos na raiz `/backend` sem organização
- Naming inconsistente (`monitor_*`, `analisador_*`, `consultar_*`)
- Zero separação por domínio/módulo

**Impacto:**
- Impossível escalar time (novo dev leva 1+ semana para entender)
- Conflitos de merge constantes
- Testes difíceis de escrever/manter

**Solução Proposta:**

```
backend/
├── modules/
│   ├── portfolio_intelligence/     # MVP v1.0
│   │   ├── dashboard/
│   │   ├── ai_recommendations/
│   │   ├── risk_alerts/
│   │   └── compliance/
│   ├── market_data/                # Compartilhado
│   │   ├── forex/
│   │   ├── crypto/
│   │   └── integrations/
│   └── shared/                     # Utils
│       ├── database/
│       ├── cache/
│       └── monitoring/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/
    └── api/
```

**Esforço:** 2 sprints (refatoração incremental)  
**Prioridade:** 🔴 P0 (Sprint 1-2)  
**Owner:** Tech Lead + Engenheiro A

---

### DT-002: Implementar Framework de Testes E2E

**Problema:**
- Zero testes E2E (end-to-end)
- Proposta de "vertical slices" requer E2E para validar frontend→backend→db
- Sem E2E, impossível garantir qualidade de módulos

**Solução Proposta:**
- Framework: Playwright (Python) ou Cypress (se houver frontend JS)
- Estrutura:

```python
# tests/e2e/test_portfolio_dashboard.py

async def test_visualizar_posicoes_completo(browser):
    """
    DADO que sou Gerente de Portfólio autenticado
    QUANDO acesso dashboard
    ENTÃO vejo 32 posições com P&L atualizado
    E heatmap de correlação
    E alertas de risco (se houver)
    """
    page = await browser.new_page()
    await page.goto("/dashboard")
    
    # Login
    await page.fill("#email", "gerente@teste.com")
    await page.fill("#password", "senha123")
    await page.click("#login-button")
    
    # Validar posições
    positions = await page.query_selector_all(".position-card")
    assert len(positions) == 32
    
    # Validar P&L
    pnl_element = await page.query_selector("#total-pnl")
    pnl_value = await pnl_element.inner_text()
    assert "$" in pnl_value  # Tem valor monetário
```

**Esforço:** 1 sprint (setup + 5-10 testes iniciais)  
**Prioridade:** 🔴 P0 (Sprint 2)  
**Owner:** Engenheiro B + DevOps

---

### DT-003: PostgreSQL + Docker Local

**Problema:**
- Código usa SQLite (não suporta multi-tenant)
- MVP B2B requer isolamento de dados por cliente
- Proposta citou "Sprint 15", mas sem planejamento real

**Solução Proposta:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: agent_especialista
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**Migração:**
- Usar Alembic (migrations)
- Manter SQLite para testes (rápido)
- PostgreSQL para dev/staging/prod

**Esforço:** 1 sprint (setup + migração schema)  
**Prioridade:** 🔴 P0 (Sprint 3)  
**Owner:** Engenheiro A + DBA (se houver)

---

## 🟡 ALTO (Melhora qualidade, não bloqueia)

### DT-004: Padronização de Naming

**Problema:**
- `monitor_*`, `analisador_*`, `consultar_*` sem convenção clara
- Dificulta busca de arquivos
- Código parece amador

**Solução:**
- Adotar convenção Domain-Driven Design (DDD):
  - `portfolio_service.py` (serviços)
  - `position_repository.py` (acesso dados)
  - `risk_calculator.py` (lógica negócio)
  - `market_data_client.py` (integrações)

**Esforço:** 2 sprints (refatoração gradual)  
**Prioridade:** 🟡 P1 (Sprint 4-5)  
**Owner:** Tech Lead (code review rigoroso)

---

### DT-005: Cobertura de Testes (TDD)

**Problema:**
- Poucos `test_*.py` (cobertura <30% estimada)
- Sem CI/CD validando testes
- Regressões frequentes

**Solução:**
- Meta: 80% cobertura (já definido em PROCESSO_DESENVOLVIMENTO.md)
- Implementar pytest + coverage
- CI/CD: Build falha se coverage <80%

```bash
# .github/workflows/ci.yml (exemplo)
- name: Run tests with coverage
  run: |
    pytest --cov=backend --cov-report=xml --cov-fail-under=80
```

**Esforço:** 3 sprints (escrever testes para código existente)  
**Prioridade:** 🟡 P1 (Sprint 3-5)  
**Owner:** Ambos engenheiros (20% do tempo cada sprint)

---

### DT-006: Documentação API (OpenAPI/Swagger)

**Problema:**
- Zero docs de API
- Frontend (futuro) não terá contrato claro
- Impossível terceiros integrarem

**Solução:**
- FastAPI auto-gera Swagger (se usar FastAPI)
- Adicionar docstrings completos:

```python
@router.get("/api/v1/portfolio/positions")
async def get_positions(
    user_id: str = Depends(get_current_user)
) -> List[Position]:
    """
    Retorna todas as posições abertas do portfólio do usuário.
    
    Args:
        user_id: ID do usuário autenticado (via JWT)
    
    Returns:
        Lista de posições com:
        - ticker (str): Código do ativo (ex: "EURUSD")
        - quantity (float): Quantidade de contratos
        - avg_price (float): Preço médio de entrada
        - current_price (float): Preço atual
        - pnl_unrealized (float): P&L não realizado (USD)
    
    Raises:
        401: Usuário não autenticado
        403: Usuário sem permissão
    """
```

**Esforço:** 1 sprint (documentar endpoints existentes)  
**Prioridade:** 🟡 P1 (Sprint 5)  
**Owner:** Engenheiro A

---

## 🟢 MÉDIO (Nice-to-have)

### DT-007: Auditoria de Código Legacy

**Problema:**
- 50% do código pode estar obsoleto/não usado
- Arquivos como `monitor_win_*` (específico para WIN) não escaláveis

**Solução:**
- Sprint dedicado: Auditar 200 arquivos
- Categorizar:
  - 🟢 Usar: Refatorar e manter
  - 🟡 Deprecar: Avisar usuários, remover em 6 meses
  - 🔴 Deletar: Não usado, remover imediatamente

**Esforço:** 1 sprint (análise + decisões)  
**Prioridade:** 🟢 P2 (Sprint 6)  
**Owner:** Tech Lead + PO (decisões de produto)

---

### DT-008: Observabilidade (Logs + Métricas)

**Problema:**
- Difícil debugar problemas em produção
- Sem métricas de performance

**Solução:**
- Logs: Estruturados (JSON) com contexto
- Métricas: Prometheus + Grafana
- Tracing: OpenTelemetry (opcional)

**Esforço:** 2 sprints (setup + instrumentação)  
**Prioridade:** 🟢 P2 (Sprint 7-8)  
**Owner:** DevOps Lead (se houver) ou Engenheiro B

---

## 📊 Priorização Visual (Effort vs Impact)

```
Alto Impacto
│
│  DT-001 ●                    DT-002 ●
│  Modularização             Testes E2E
│
│                DT-003 ●
│              PostgreSQL
│
│  DT-004 ●         DT-005 ●
│  Naming          Cobertura
│
│         DT-006 ●        DT-007 ●
│        API Docs        Auditoria
│
│                    DT-008 ●
│                  Observabilidade
│
└────────────────────────────────────── Esforço (sprints)
   1      2      3      4      5
```

---

## 🎯 Roadmap de Execução

**Fase 1: Fundação (Sprints 1-3)**
- Sprint 1-2: DT-001 (Modularização)
- Sprint 2: DT-002 (Testes E2E)
- Sprint 3: DT-003 (PostgreSQL)

**Fase 2: Qualidade (Sprints 3-5)**
- Sprint 3-5: DT-005 (Cobertura 80%)
- Sprint 4-5: DT-004 (Naming padrão)
- Sprint 5: DT-006 (API docs)

**Fase 3: Maturidade (Sprints 6-8)**
- Sprint 6: DT-007 (Auditoria legacy)
- Sprint 7-8: DT-008 (Observabilidade)

---

## ✅ Definition of "Débito Resolvido"

Cada item deve ter:
- [ ] Código refatorado + testado
- [ ] Docs atualizados
- [ ] Code review aprovado (Tech Lead)
- [ ] CI/CD validando (se aplicável)
- [ ] Deploy em staging sem regressões

---

**Atualizado:** 2025-11-07  
**Próxima Revisão:** Semanal (reunião Tech Lead + Engenheiros)

