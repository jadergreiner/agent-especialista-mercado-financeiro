# Definition of Done (DoD) & WIP Limits - Agent Especialista

**Versão:** 2.0  
**Data:** 2025-11-07  
**Aprovado por:** PO + Tech Lead + Scrum Master  
**Status:** ✅ Oficial (substitui DoD anterior)

---

## ✅ DEFINITION OF DONE (Atualizada)

Uma User Story só está **DONE** quando **TODAS** as condições abaixo forem atendidas:

### 1. Código

- [ ] **Funcionalidade completa** implementada conforme critérios de aceitação
- [ ] **Code review aprovado** por Tech Lead ou Senior Engineer
- [ ] **Padrões de naming** seguidos (Domain-Driven Design)
- [ ] **Sem warnings** de lint (flake8, mypy, black)
- [ ] **Commits** com mensagens convencionais (`feat:`, `fix:`, `docs:`)

### 2. Testes

- [ ] **Testes unitários** escritos e passando (cobertura >80% da feature)
- [ ] **Testes de integração** (se aplicável - ex: API + BD)
- [ ] **Testes E2E** escritos e passando (frontend → backend → BD completo)
- [ ] **CI/CD** passando (testes + lint + build)
- [ ] **Coverage report** atualizado no Codecov/SonarQube

### 3. Documentação

- [ ] **README atualizado** (se feature impacta uso)
- [ ] **API docs** gerados (Swagger/OpenAPI para endpoints novos)
- [ ] **Tutorial** ou guia de uso (para features complexas)
- [ ] **Changelog** atualizado (CHANGELOG.md com versão + mudanças)
- [ ] **Comentários de código** em português (funções públicas com docstrings)

### 4. Deploy & Produção

- [ ] **Deploy em staging** bem-sucedido
- [ ] **Smoke tests** manuais executados (happy path + edge cases)
- [ ] **Feature flag** configurado (se release progressivo)
- [ ] **Monitoring** adicionado (logs, métricas, alertas)
- [ ] **Rollback plan** documentado (caso dê errado)

### 5. Rastreabilidade

- [ ] **Issue/US linkado** nos commits (`#US-XXX`)
- [ ] **Evidências** de testes anexadas (screenshots/vídeos)
- [ ] **Demo** apresentado em Sprint Review (PO aprovou)
- [ ] **Métricas baseline** coletadas (DAU, latência, etc.)

---

## 🚦 WIP LIMITS (Work In Progress)

**Objetivo:** Evitar multitasking, garantir foco e qualidade.

### Limites por Papel

| Papel | WIP Limit | Rationale |
|-------|-----------|-----------|
| **Engenheiro A** | 1 módulo | Foco total, entrega completa |
| **Engenheiro B** | 1 módulo | Foco total, entrega completa |
| **Tech Lead** | 2 code reviews/dia | Qualidade > velocidade |
| **PO** | 3 refinamentos/sprint | Preparar backlog 1 sprint ahead |

### Regras de Fluxo

**Regra 1: Finish Before Starting** 🔴
- NÃO iniciar nova US enquanto atual não está DONE
- Exceção: Bloqueio externo (ex: aguardando API terceiro) - notificar Scrum Master

**Regra 2: Pair Programming em Bloqueios** 🟡
- Se bloqueado >4h, chamar outro engenheiro para pair programming
- Documentar bloqueio e solução (para futuros)

**Regra 3: Pull Before Push** 🟢
- Só pegar nova US quando anterior passar em TODOS critérios DoD
- Sprint Review: Engenheiro demonstra pessoalmente (não terceiro)

---

## 📊 MÉTRICAS DE QUALIDADE

### Lead Time (Objetivo: <5 dias por US)

```
Lead Time = Data Done - Data Start
Meta: <5 dias úteis (1 sprint)
```

### Cycle Time (Objetivo: <3 dias por US)

```
Cycle Time = Data Done - Data Em Progresso
Meta: <3 dias úteis
```

### Rework Rate (Objetivo: <10%)

```
Rework Rate = (US retrabalhadas / Total US) × 100
Meta: <10% (max 1 a cada 10 US volta)
```

### Defect Escape Rate (Objetivo: <5%)

```
Defect Escape = (Bugs prod / Total US deployed) × 100
Meta: <5% (max 1 bug a cada 20 US)
```

---

## 🎯 CRITÉRIOS SMART (User Stories)

Toda User Story deve ser:

**S (Specific):** Objetivo claro e sem ambiguidade
```
❌ "Melhorar dashboard"
✅ "Adicionar gráfico de P&L diário com drill-down por ativo"
```

**M (Measurable):** Critérios de aceitação testáveis
```
DADO que sou Gerente de Portfólio autenticado
QUANDO acesso dashboard
ENTÃO vejo gráfico P&L com:
  - 30 dias de histórico
  - Drill-down por ativo ao clicar barra
  - Exportar PNG (botão superior direito)
```

**A (Achievable):** Viável em 1 sprint (2 semanas)
```
❌ "Implementar IA completa de recomendações" (6 meses)
✅ "Implementar recomendação de fechamento de posição baseada em correlação" (1 sprint)
```

**R (Relevant):** Alinhado com OKRs/objetivos do sprint
```
Sprint Goal: "Dashboard executivo funcional"
✅ US-001: Gráfico P&L (alinhado)
❌ US-099: Integração Instagram (não alinhado)
```

**T (Time-bound):** Deadline explícito
```
❌ "Quando possível"
✅ "Pronto para demo na Sprint Review dia 21/11"
```

---

## 🔄 PROCESSO DE REFINAMENTO

### Pré-Requisitos para Planning

US só entra em Planning se:
- [ ] Refinada com Tech Lead (viabilidade técnica OK)
- [ ] Critérios aceitação escritos (SMART)
- [ ] Estimada em story points (Planning Poker)
- [ ] Dependências identificadas e resolvidas
- [ ] Mockups/wireframes prontos (se feature UI)

### Template de Refinamento

```markdown
## US-XXX: [Título 1 Linha]

**Como** [persona]  
**Quero** [funcionalidade]  
**Para** [valor/benefício]

### Critérios de Aceitação (Gherkin)

DADO [contexto inicial]
QUANDO [ação do usuário]
ENTÃO [resultado esperado]
  E [resultado adicional]

### Estimativa

Story Points: [1, 2, 3, 5, 8, 13] (Fibonacci)
Complexidade: [Baixa/Média/Alta]
Risco Técnico: [Baixo/Médio/Alto]

### Dependências

- [ ] US-AAA deve estar completa
- [ ] API terceiro X aprovada
- [ ] Design finalizado

### Tasks Técnicas (Checklist)

- [ ] Criar endpoint POST /api/xxx
- [ ] Implementar lógica negócio (service layer)
- [ ] Escrever testes unit + integration
- [ ] Atualizar Swagger docs
- [ ] Deploy staging
```

---

## 📈 VELOCITY HISTÓRICA

### Como Calcular

```
Velocity = Σ(Story Points completados) / Sprints
```

**Exemplo:**
- Sprint 1: 13 pontos
- Sprint 2: 21 pontos
- Sprint 3: 18 pontos
- **Velocity Média:** (13+21+18)/3 = **17.3 pontos/sprint**

### Como Usar

**Planejamento:** Comprometer apenas 80% da velocity (buffer)
```
Velocity média = 17 pontos
Comprometer no Planning = 17 × 0.8 = 13-14 pontos
```

**Projeção Roadmap:**
```
Backlog total = 200 pontos
Velocity = 17 pontos/sprint
Prazo estimado = 200/17 = 12 sprints (6 meses)
```

---

## ⚠️ SINAIS DE ALERTA (Red Flags)

| Sintoma | Causa Provável | Ação |
|---------|----------------|------|
| **WIP >2 por pessoa** | Multitasking, bloqueios | Retrospectiva, identificar gargalos |
| **Cycle Time >5 dias** | US muito grande | Quebrar em US menores |
| **Rework >15%** | Critérios aceitação ruins | Refinamento mais rigoroso |
| **Defects >10%** | Testes insuficientes | Code review mais rigoroso |
| **Velocity oscila >30%** | Estimativas ruins | Recalibrar Planning Poker |

---

## ✅ CHECKLIST PRÉ-DEPLOY

Antes de fazer deploy para produção:

- [ ] Todos critérios DoD atendidos
- [ ] Aprovação PO (demo em Review)
- [ ] Aprovação Tech Lead (code review)
- [ ] Smoke tests em staging passando
- [ ] Monitoring configurado (dashboards Grafana)
- [ ] Rollback testado (sabe reverter em <5min)
- [ ] Comunicação para stakeholders (se feature crítica)
- [ ] Feature flag ativo (release progressivo)

---

## 🔄 REVISÃO E MELHORIA CONTÍNUA

**Frequência:** Revisar DoD a cada 3 sprints (Retrospectiva)

**Perguntas:**
1. Algum critério está sendo ignorado? Por quê?
2. Falta algum critério importante?
3. Algum critério é burocrático demais?
4. Métricas (lead time, rework) melhoraram?

**Responsável:** Scrum Master facilita, time decide

---

**Aprovações:**

| Papel | Nome | Data | Assinatura |
|-------|------|------|------------|
| Product Owner | [Nome] | 2025-11-07 | ✅ Aprovado |
| Tech Lead | [Nome] | 2025-11-07 | ✅ Aprovado |
| Scrum Master | [Nome] | 2025-11-07 | ✅ Aprovado |
| Engenheiro A | [Nome] | 2025-11-07 | ✅ Aprovado |
| Engenheiro B | [Nome] | 2025-11-07 | ✅ Aprovado |

---

**Próxima Revisão:** 2025-12-21 (após Sprint 3)

