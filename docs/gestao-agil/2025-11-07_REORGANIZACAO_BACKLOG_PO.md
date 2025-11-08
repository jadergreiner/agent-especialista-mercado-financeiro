# 🎯 REORGANIZAÇÃO DO BACKLOG — DECISÃO PO

**Data:** 07/11/2025 19:00 UTC
**Papel:** Product Owner
**Contexto:** Reorganização estratégica pós-implementação de US-RISCO-003
**Motivação:** Alterar foco para uso interativo do prompt para solicitar análise de ativos

---

## 📊 ANÁLISE GERAL DO PROJETO

### Situação Atual

**Sprints Ativos:**
- ✅ Sprint Emergencial (Risco): 3/5 completo (60%)
- ✅ Sprint Prompt MVP: 3/8 completo (38%)
- 🏗️ Fundação Operacional: Suporte contínuo

**Artefatos Entregues (Semana 1):**
- ✅ US-RISCO-001: Avisos Críticos HTML
- ✅ US-RISCO-002: Qualidade de Dados Portfolio
- ✅ US-RISCO-003: Radical Transparency (sistema completo)
- ✅ US-PROMPT-001: CLI Interativa com modos
- ✅ US-PROMPT-002: Orquestrador de Ferramentas
- ✅ US-QUALIDADE-003: Validação Consistência

**Descobertas Críticas:**
- 78% das posições sem stop loss
- Alavancagem de 32x (risco ilimitado)
- $63k não realizados
- Interface perigosamente otimista

---

## 🎲 TRÊS CENÁRIOS DE PRIORIZAÇÃO

### Cenário A: Foco Exclusivo Risco (Conservative)
**Vantagem:** Proteção máxima de capital
**Desvantagem:** Prompt fica incompleto, sem valor percebido rápido

```
US-RISCO-004 → US-RISCO-005 → US-QUALIDADE-004 → US-DATA-002
Risco operacional: Usuário nunca vê prompt completo
```

### Cenário B: Foco Exclusivo Prompt (Aggressive)
**Vantagem:** Valor percebido rápido, experiência de usuário completa
**Desvantagem:** Risco continua exposto (mas com avisos críticos já implementados)

```
US-PROMPT-003 → US-PROMPT-004 → US-PROMPT-006 → US-PROMPT-005
Operacional aprovado: Transparência Radical já mitiga riscos principais
```

### Cenário C: Balanceado (Recomendado) ⭐
**Vantagem:** Risco mitigado (avisos críticos já existem) + Valor rápido do prompt
**Desvantagem:** Paralelização de esforços

```
Trilha Risco:    US-RISCO-004 (engenheiro B) + US-RISCO-005 (semana 2)
Trilha Prompt:   US-PROMPT-003 (engenheiro A) + US-PROMPT-004 (paralelo)
Resultado:       Ambos entregues em ~5 dias com 2 engenheiros
```

---

## ✅ DECISÃO DO PO

**Cenário Escolhido: C (Balanceado)**

### Justificativa

1. **Risco Já Mitigado**
   - ✅ Avisos críticos visuais (US-RISCO-001)
   - ✅ Qualidade de dados garantida (US-RISCO-002)
   - ✅ Transparência radical forçada (US-RISCO-003)
   - 🔒 Usuário é alertado ANTES de fazer qualquer coisa

2. **Prompt MVP Agregará Valor Imediato**
   - Templates + modos (US-PROMPT-003) = experiência intuitiva
   - Saída estruturada (US-PROMPT-004) = confiança nas respostas
   - Disclaimers (US-PROMPT-006) = segurança jurídica
   - **Resultado:** Usuário vê análise completa, estruturada e segura

3. **Eficiência de Recursos**
   - 2 engenheiros em paralelo = ambas sprints avançam
   - Não cria gargalos de dependências
   - Timeline: 5 dias vs 10 dias (sequencial)

4. **Princípio de Negócio**
   - "Risco gerenciado" + "Valor entregue" = sucesso
   - Não é escolher entre risco E prompt, é AMBOS em paralelo

---

## 🔄 NOVO ROADMAP (Próximas 2 Semanas)

### Semana 1 (Hoje até Domingo 9/11)

#### Trilha A: Prompt MVP (Engenheiro A)
**Objetivos:** Templates, saída estruturada, disclaimers

| Task | Estimativa | Status | Pré-req |
|------|-----------|--------|---------|
| US-PROMPT-003: Templates e Modos | 2d | 🔄 TODO | US-PROMPT-001/002 ✅ |
| US-PROMPT-004: Saída Estruturada | 2d | 🔄 TODO | US-PROMPT-001 ✅ |
| US-PROMPT-006: Disclaimers | 1d | 🔄 TODO | US-PROMPT-001 ✅ |

**Resultado:** Prompt interativo completo, estruturado e seguro

#### Trilha B: Risco Management (Engenheiro B)
**Objetivos:** Dashboard consolidado + alertas automatizados

| Task | Estimativa | Status | Pré-req |
|------|-----------|--------|---------|
| US-RISCO-004: Dashboard Consolidado | 6h | 🔄 TODO | US-RISCO-002 ✅ |
| US-RISCO-005: Alertas Críticos Auto | 8h | 🔄 TODO | US-RISCO-004 |

**Resultado:** Gestão de risco passiva (alertas automáticos) funcionando

### Semana 2 (Terça 10/11 a Domingo 16/11)

#### Sprint Fundação Operacional (Paralelo)
**Objetivos:** Dados robustos, sentimento, autoavaliação

| Task | Estimativa | Status | Pré-req |
|------|-----------|--------|---------|
| US-DATA-002: Expansão Fontes | 5d | 🔄 TODO | - |
| US-QUALIDADE-004: Sentimento Notícias | 3d | 🔄 TODO | US-DATA-002 |
| US-QUALIDADE-005: Autoavaliação Auto | 2d | 🔄 TODO | US-PROMPT-004 |

**Resultado:** Sistema de dados robusto com sentimento integrado

---

## 🎯 METAS DE NEGÓCIO POR CENÁRIO

### MVP v1 Success Criteria (fim Semana 1)

✅ **Prompt Interativo Completo:**
- [ ] `analise EUR/USD` retorna JSON + Markdown
- [ ] Modo "Analista" vs "Trader Rápido" funcional
- [ ] Fontes com URLs clicáveis
- [ ] Disclaimer obrigatório presente
- [ ] TTR < 20s (sem cache)

✅ **Gestão de Risco Completa:**
- [ ] Dashboard mostra exposição por moeda
- [ ] Correlação visualizada
- [ ] Alertas automáticos acionando
- [ ] P&L realizado vs não realizado separado

✅ **Nenhuma Regressão:**
- [ ] Avisos críticos ainda visíveis
- [ ] Qualidade de dados validada
- [ ] Transparência radical ativa

### ROI Estimado

| Métrica | Baseline | Target | Timeline |
|---------|----------|--------|----------|
| TTR análise | N/A | <20s | Semana 1 ✅ |
| Cobertura ativos | EUR/USD | EUR/USD + XAU/USD | Semana 1 ✅ |
| Usuários ativos | 1 | 3-5 (teste beta) | Semana 2 |
| Confiança reportada | 60% fake | 25% real + disclaimers | Semana 1 ✅ |
| Risco detectado | 0/32 | 32/32 com alertas | Semana 1 ✅ |

---

## 📋 BACKLOG REORGANIZADO

### 🔴 CRÍTICA (Fazer Esta Semana)

#### Trilha Prompt
1. **US-PROMPT-003: Templates e Modos** (2d)
   - Few-shots: "Analista" (explicativo) vs "Trader Rápido" (direto)
   - Manutenção: Tone, estrutura, completude
   - Blocker: Nenhum — começar NOW

2. **US-PROMPT-004: Saída Estruturada** (2d)
   - JSON com: ativo, timeframe, preço, variação, drivers[], riscos[], proximos_passos[], fontes[], timestamp
   - Markdown espelhando JSON
   - Blocker: Nenhum — começar NOW

3. **US-PROMPT-006: Disclaimers + Segurança** (1d)
   - Disclaimer "Sistema em Fase Beta" obrigatório
   - Bloqueio linguagem prescritiva
   - Integração em ambos modos
   - Blocker: Nenhum — começar NOW

#### Trilha Risco
4. **US-RISCO-004: Dashboard Consolidado** (6h)
   - Exposição por moeda
   - Matriz correlação visual
   - Alavancagem tempo real
   - P&L realizado vs não realizado
   - Blocker: US-RISCO-002 ✅ (data pronta)

5. **US-RISCO-005: Alertas Críticos Auto** (8h)
   - Alerta: posições sem stop > 20%
   - Warning: alavancagem > 10x
   - Notificação: P&L não realizado > $50k
   - Configurável: email/telegram
   - Blocker: US-RISCO-004 (precedente lógico)

---

### 🟡 ALTA (Próximas 2 Semanas)

1. **US-PROMPT-005: Cache e Memória** (3d)
   - Cache por ativo/timeframe
   - Memória sessão por conversa
   - TTR esperado: <5s com cache
   - Blocker: US-PROMPT-003 + US-PROMPT-004

2. **US-DATA-002: Expansão Fontes Dados** (5d)
   - Alpha Vantage backup
   - Múltiplas APIs notícias
   - Dados econômicos oficiais
   - Fallback automático
   - Blocker: Nenhum — planejamento pré-implementação

3. **US-QUALIDADE-004: Sentimento de Notícias** (3d)
   - Análise automática (pos/neut/neg)
   - Ponderação por fonte
   - Integração confiança cenários
   - Blocker: US-DATA-002

4. **US-PROMPT-007: Métricas e Logs** (1d)
   - TTR logging
   - Contagem ferramentas
   - Taxa sucesso/falha
   - Blocker: US-PROMPT-003 + US-PROMPT-004

---

### 🟢 MÉDIA (Pós-MVP v1)

1. **US-PROMPT-008: Guia de Uso** (1d)
   - Exemplos de perguntas
   - Explicação de modos
   - Casos de uso
   - Blocker: Nenhum (mas após US-PROMPT-003/004 completas)

2. **US-QUALIDADE-005: Autoavaliação Auto** (2d)
   - Validação completude
   - Consistência interna
   - Qualidade fontes
   - Blocker: US-PROMPT-004

3. **US-RISCO-006: Integração Telegram** (3d)
   - Push notifications de alertas
   - Configuração por usuário
   - Histórico de mensagens
   - Blocker: US-RISCO-005

---

## 🚨 DECISÕES IMPORTANTES

### 1. Mudança de Prioridades (Transparência Radical Mitiga Risco)

**Antes:** "Risco deve ser fechado antes de liberar prompt"
**Agora:** "Risco está mitigado com avisos críticos + transparência radical, prompt agrega valor"

**Rationale:**
- Avisos críticos garantem usuário vê riscos ANTES de agir
- Confiança downgrade 60% → 25% elimina confiança falsa
- Disclaimers obrigatórios criam proteção legal

### 2. Paralelização de Trilhas (Eficiência)

**Alocação:**
- Engenheiro A: Templates + Saída Estruturada + Disclaimers = Prompt MVP pronto
- Engenheiro B: Dashboard + Alertas Auto = Risco MVP pronto

**Timeline:** 5 dias vs 10 dias sequencial = **50% mais rápido**

### 3. Adiamento de Features Complementares (Focus)

**Adiado para Semana 2:**
- Cache/Memória (nice-to-have, não core)
- Expansão Fontes (robustez, não urgência)
- Sentimento (melhor experiência, não crítica)

**Rationale:** MVP precisa de: Template, Estrutura, Disclaimers, Dashboard, Alertas. TUDO MAIS é complemento.

### 4. Métricas de Sucesso Redefindas

**De:** "Todos os riscos corrigidos antes de liberar prompt"
**Para:** "Riscos alertados em tempo real + Prompt agrega valor"

| Métrica | Target | Semana 1 | Semana 2 |
|---------|--------|----------|----------|
| Prompt util | >80% | Template + Estrutura + Disclaimers | + Cache + Sentiment |
| Risco alertado | 100% | Avisos críticos + Dashboard | + Alertas Auto |
| Cobertura | EUR/USD + XAU/USD | ✅ | + Outras moedas |
| Confiança | Honesta (25%) | ✅ | Aprendizado contínuo |

---

## 📑 DEPENDÊNCIAS E CRITICIDADE

### Diagrama de Dependências

```
US-PROMPT-001 ✅ ──┬─→ US-PROMPT-003 (2d) ──┬─→ US-PROMPT-005 (3d)
                   │                         │
                   ├─→ US-PROMPT-004 (2d) ──┴─→ US-PROMPT-007 (1d)
                   │                         │
                   └─→ US-PROMPT-006 (1d) ───┘

US-PROMPT-002 ✅ ──→ US-PROMPT-003/004/006 ✅ (Já integrado)

US-RISCO-002 ✅ ──→ US-RISCO-004 (6h) ──→ US-RISCO-005 (8h)

US-PROMPT-004 ──→ US-QUALIDADE-005 (2d)

US-DATA-002 ──→ US-QUALIDADE-004 (3d) ──→ US-QUALIDADE-005 (via integração)
```

### Críticas (Sem Bloqueio)

**Nenhuma.** Todas as dependências críticas estão ✅

- US-PROMPT-001/002 ✅ (base para prompt)
- US-RISCO-002 ✅ (dados para dashboard)
- Templates/Disclaimers podem começar HOJE

---

## 🎓 LIÇÕES DO SPRINT ANTERIOR

1. **Reunião de Refinamento ECONOMIZA tempo** (15 min net -2h dev)
2. **Testes durante dev PEGAM bugs cedo** (2 bugs em 5 min vs 2h debug depois)
3. **Validação pré-deploy PREVINE desastres** (0 regressões)
4. **Documentação simultânea = conhecimento preservado** (4 docs criados)
5. **Oportunidades emergentes são ouro** (5 novas US identificadas, 2 integradas)

**Aplicação ao novo sprint:**
- Refinar US-PROMPT-003 com template examples HOJE
- Iniciar TDD em US-PROMPT-003 (write tests first)
- Validador estruturado para output JSON
- Documentação inline com exemplos

---

## 📊 STATUS CONSOLIDADO

### Sprint Emergencial (Risco) — 3/5 (60%)

✅ Completo:
- US-RISCO-001: Avisos Críticos
- US-RISCO-002: Qualidade Dados
- US-RISCO-003: Radical Transparency

🔄 Próximo (Esta semana):
- US-RISCO-004: Dashboard (6h)
- US-RISCO-005: Alertas Auto (8h)

### Sprint Prompt MVP — 3/8 (38%)

✅ Completo:
- US-PROMPT-001: CLI Interativa
- US-PROMPT-002: Orquestrador Ferramentas
- US-QUALIDADE-003: Validação Consistência

🔄 Próximo (Esta semana):
- US-PROMPT-003: Templates (2d)
- US-PROMPT-004: Saída Estruturada (2d)
- US-PROMPT-006: Disclaimers (1d)

### Fundação Operacional — Suporte Contínuo

✅ Pronto:
- US-DATA-001: Validação Qualidade

🔄 Próximo (Semana 2):
- US-DATA-002: Expansão Fontes (5d)
- US-QUALIDADE-004: Sentimento (3d)
- US-QUALIDADE-005: Autoavaliação (2d)

---

## 🚀 PLANO DE EXECUÇÃO (Próximas 24h)

### Hoje (19:00 - 23:59 UTC)

1. **Refinamento US-PROMPT-003** (30 min)
   - Tech Lead define few-shots "Analista" vs "Trader Rápido"
   - Aprova exemplos de tone e estrutura
   - Aceita estimativa 2d

2. **Refinamento US-PROMPT-004** (30 min)
   - Define schema JSON final
   - Aprova estrutura Markdown
   - Aceita estimativa 2d

3. **Refinamento US-RISCO-004** (30 min)
   - Gerente de Portfólio aprova design dashboard
   - Define métricas para visualizar
   - Aceita estimativa 6h

### Amanhã (08/11 09:00-17:00)

**Engenheiro A (Prompt MVP):**
- ✅ US-PROMPT-003: Templates (dia 1)
  - Few-shot definition
  - Mode routing logic
  - Teste com EUR/USD

**Engenheiro B (Risco Management):**
- ✅ US-RISCO-004: Dashboard (6h)
  - Agregação dados por moeda
  - Visualização correlação
  - Integração dados

### Semana Seguinte

**Manter Momentum:**
- A: Finalizar US-PROMPT-003, iniciar US-PROMPT-004
- B: Iniciar US-RISCO-005 (alertas)
- Ambos: Daily standup 09:00 UTC para sincronização

---

## ✅ ASSINATURA DO PO

**Decisão:** Cenário C (Balanceado) — Trilhas paralelas
**Justificativa:** Risco mitigado + Valor rápido prompt
**Timeline:** MVP v1 pronto em 5 dias
**Aprovação:** ✅ CONFIRMADO

**Próximo Review:** 2025-11-09 17:00 UTC (Fim semana 1)

---

**Document ID:** PO-REORGANIZACAO-2025-11-07
**Status:** ATIVO — Em Execução
**Última Atualização:** 2025-11-07 19:00 UTC
