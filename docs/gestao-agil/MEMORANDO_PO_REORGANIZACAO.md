# MEMORANDO DO PO — Reorganização de Prioridades

**Data:** 07/11/2025 19:00 UTC
**Para:** Tech Lead, Engenheiros, Stakeholders
**De:** Product Owner
**Assunto:** Decisão Executiva — Novo Roadmap (Trilhas Paralelas)

---

## Decisão Executiva

✅ **Cenário C (Balanceado) — APROVADO**

Estratégia: Trilhas paralelas (Engenheiro A = Prompt MVP, Engenheiro B = Risco MVP)
Timeline: MVP v1 entregue em 5 dias (vs 10 sequencial)
Resultado: Ambos sprints avançam em paralelo

---

## Contexto da Decisão

### Situação Crítica Semana 1

Descoberta: 78% posições sem stop loss, alavancagem 32x, $63k em risco

**Mitigações Implementadas:**

- Avisos críticos vermelhos (HTML)
- Confiança downgrade 60% → 25%
- Disclaimers obrigatórios
- Validação de dados

**Conclusão:** Risco está GERENCIADO e TRANSPARENTE

### Oportunidade: Prompt MVP

Semana 1 completou base:

- CLI interativa (US-PROMPT-001)
- Orquestrador ferramentas (US-PROMPT-002)
- Validação consistência (US-QUALIDADE-003)

**Próximo Passo:** Agregar valor com templates, estrutura e disclaimers

### Opção de Paralelização

Com 2 engenheiros:

- Trilha A: Prompt MVP (templatesstrutura, disclaimers)
- Trilha B: Risco MVP (dashboard, alertas)

**Benefício:** Ambos entregues em 5 dias (não 10)

---

## Novo Roadmap

### Esta Semana (Dias 1-5)

### Trilha A: Engenheiro A (Prompt MVP)

1. US-PROMPT-003: Templates e Modos (2d)
   - Few-shot "Analista" (explicativo)
   - Few-shot "Trader Rápido" (objetivo)
   - Integração modo routing

2. US-PROMPT-004: Saída Estruturada (2d)
   - JSON schema padronizado
   - Markdown espelhando JSON
   - Fontes com URLs

3. US-PROMPT-006: Disclaimers (1d)
   - Disclaimer obrigatório prepend
   - Bloqueio linguagem prescritiva
   - Integração ambos modos

**Deliverable:** Prompt MVP Completo

- `analise EUR/USD` → JSON + Markdown
- Modo Analista vs Trader Rápido
- TTR <20s
- Disclaimers + Fontes visíveis

**Bloqueadores:** Nenhum (começar AGORA)

---

---

### Trilha B: Engenheiro B (Risco MVP)

1. US-RISCO-004: Dashboard Consolidado (6h)
   - Exposição por moeda (AUD: 8 pos, JPY: 5 pos)
   - Matriz visual correlação
   - Alavancagem tempo real
   - P&L realizado vs não realizado

2. US-RISCO-005: Alertas Críticos Auto (8h)
   - Alert: posições sem stop > 20%
   - Warning: alavancagem > 10x
   - Notificação: P&L não realizado > $50k
   - Config: email/telegram

3. Testes + Integração (6h)
   - Validação com dados reais
   - Zero regressões

**Deliverable:** Risco MVP Completo

- Dashboard mostra exposição agregada
- Alertas acionando automaticamente
- Alavancagem visível em tempo real

**Bloqueadores:** Nenhum (começar AGORA)

---

---

### Próxima Semana (Dias 6-10)

#### Trilha A: Prompt Robusto

- Cache por ativo/timeframe
- Métricas latência
- Integração sentimento

#### Trilha B: Risco Proativo

- Alertas 24/7 acionando
- Integração Telegram

---

## Métricas de Sucesso

### Fim Semana 1

✅ **Prompt MVP:**

- [ ] Templates "Analista" vs "Trader Rápido" funcionais
- [ ] JSON padronizado com todos os campos
- [ ] Markdown + Fontes + Disclaimer visíveis
- [ ] TTR <20s
- [ ] Zero erros de parsing

✅ **Risco MVP:**

- [ ] Dashboard mostra exposição por moeda
- [ ] Alertas acionam em teste
- [ ] Alavancagem atualizada tempo real
- [ ] P&L separado (realizado vs não realizado)

✅ **Nenhuma Regressão:**

- [ ] Avisos críticos HTML ainda visíveis
- [ ] Qualidade dados validada
- [ ] Transparência radical ativa

---

## Impacto Esperado

### Para Usuário

- ✅ Análise estruturada em <20s
- ✅ Disclaimers claros (não é recomendação)
- ✅ Fontes rastreáveis
- ✅ Dashboard mostra exposição total
- ✅ Alertas automáticos acionando

### Para Negócio

- ✅ MVP v1 entregue 50% mais rápido
- ✅ Risco gerenciado + Valor agregado
- ✅ TTM reduzido (Time To Market)
- ✅ Experiência completa (não meio-termo)

### Para Projeto

- ✅ Sprint Emergencial: 5/5 (100%)
- ✅ Sprint Prompt MVP: 6/8 (75%)
- ✅ Total: 11/16 (69%)
- ✅ Sem débito técnico

---

## Riscos Mitigados

| Risco | Probabilidade | Mitigação |
|-------|-------------|-----------|
| Desalinhamento paralelo | 20% | Daily standup + Schema aprovado HOJE |
| Templates simplificados | 15% | Tech Lead refinement + Iteração rápida |
| Dashboard lento | 10% | Query optimization + Cache existe |

---

## Ações Imediatas

### HOJE (19:00-23:59 UTC)

- [ ] Comunicar decisão ao Tech Lead
- [ ] Agendar refinements (US-PROMPT-003/004/006/RISCO-004)
- [ ] Obter approvals finais de specs
- [ ] Comunicar roadmap aos engenheiros

### AMANHÃ (08/11 09:00 UTC)

- [ ] Standup de kickoff (ambos + PO + Tech Lead)
- [ ] Eng A: Start US-PROMPT-003
- [ ] Eng B: Start US-RISCO-004
- [ ] Daily standup schedule confirmado

### Semana (08-12/11)

- [ ] Daily standups 09:00 UTC
- [ ] Mid-sprint review 10/11 17:00 UTC
- [ ] Blocker escalation imediata
- [ ] Test execution contínua

---

## Filosofia de Negócio

**De:** "Risco OU Prompt" (sequencial, 10 dias)
**Para:** "Risco E Prompt" (paralelo, 5 dias)

**Princípio:**

- Risco gerenciado = não assusta
- Valor entregue = satisfação
- Ambos = sucesso real

---

## Assinatura

**Aprovado pelo Product Owner:** ✅

**Data:** 07/11/2025 19:00 UTC
**Status:** ATIVO — Em Execução a partir de 08/11/2025
**Review:** 10/11/2025 17:00 UTC (Mid-Sprint)

---

**Cópia para:** Tech Lead, Engenheiros, Gerente de Portfólio, Stakeholders
**Arquivo:** docs/gestao-agil/2025-11-07_REORGANIZACAO_BACKLOG_PO.md
**Análise Detalhada:** docs/gestao-agil/2025-11-07_ANALISE_GERAL_PROJETO_PO.md
