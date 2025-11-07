# 📚 Índice de Documentação - Sprint Emergencial de Risco

**Data**: 2025-11-07
**Tema**: Descoberta Crítica em Gestão de Risco e Transparência Radical

# Índice de Documentação — Sprint Emergencial de Risco
> Atualização Estratégica: Veja também `docs/gestao-agil/estrategia/2025-11-07_PIVOT_PROMPT_INTERATIVO.md` para o pivot de foco em Prompt Interativo (MVP).

---

## 🎯 VISÃO GERAL

Este índice organiza toda a documentação gerada após a descoberta crítica de riscos sistêmicos no portfólio (78% posições sem stop loss, 32x alavancagem, $63k não realizados).

---

## 📄 DOCUMENTOS PRINCIPAIS

### 1. 🗣️ Conversa PO ↔ Gerente Portfólio
**Arquivo**: [`docs/gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md`](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md)

**Conteúdo**:
- 🚨 Contexto da reunião emergencial
- 📊 5 descobertas críticas detalhadas
- 💡 Proposta de "Radical Transparency"
- 🎯 Decisões tomadas e próximos passos
- 🎓 Princípio aprendido: "Bonito e quebrado não é produto, é cilada"

**Por que ler**: Entenda o contexto completo da descoberta e a conversa que gerou as 11 histórias de usuário.

**Tempo de leitura**: ~8 minutos

---

### 2. 📋 Backlog Atualizado
**Arquivo**: [`docs/gestao-agil/backlog.md`](./gestao-agil/backlog.md)

**Conteúdo**:
- 🚨 Sprint Emergencial (PRIORIDADE MÁXIMA)
- ✅ 11 Histórias de Usuário detalhadas:
  - **Sprint 0** (Hoje): US-RISCO-001, 002, 003
  - **Sprint 1** (Semana 1-2): US-UX-001, US-RISCO-004, 005, US-DATA-001
  - **Sprint 2** (Semana 3-4): US-RISCO-006, 007, 008, 009
  - **Médio Prazo**: US-RISCO-010, 011
- 📊 Métricas de sucesso e validação de UX

**Por que ler**: Todas as tarefas prioritárias estão aqui com critérios de aceitação, estimativas e prioridades.

**Tempo de leitura**: ~15 minutos (seção Sprint Emergencial)

---

### 3. 📊 Resumo Executivo
**Arquivo**: [`docs/gestao-agil/RESUMO_EXECUTIVO_SPRINT_EMERGENCIAL_RISCO.md`](./gestao-agil/RESUMO_EXECUTIVO_SPRINT_EMERGENCIAL_RISCO.md)

**Conteúdo**:
- 🎯 Resumo de 1 minuto para executivos
- 📊 Descobertas críticas em tabelas
- 💡 Solução "Radical Transparency" explicada
- 📋 Plano de ação detalhado (Sprint 0, 1, 2)
- 📈 Métricas de sucesso e KPIs
- 🎓 5 Lições aprendidas
- 💼 Impacto no roadmap (features pausadas vs aceleradas)
- 🎯 Call to action para cada stakeholder

**Por que ler**: Visão completa e estruturada para apresentar a stakeholders.

**Tempo de leitura**: ~12 minutos

---

### 4. 📝 Changelog
**Arquivo**: [`CHANGELOG.md`](../CHANGELOG.md)

**Conteúdo**:
- 🚨 [Sprint Emergencial] - 2025-11-07
- ✨ [v2.0] - Melhorias relatório HTML (2025-11-06)
- 🧹 [v1.5] - Limpeza dados portfólio (2025-11-06)
- 📋 Convenções de versionamento
- 🏷️ Tags e categorias

**Por que ler**: Histórico completo de evoluções do sistema.

**Tempo de leitura**: ~5 minutos

---

### 5. 📁 Portfolio Atual
**Arquivo**: [`backend/data/portfolio/portfolio_atual.json`](../backend/data/portfolio/portfolio_atual.json)

**Conteúdo**:
- 32 posições ativas
- Metadados do portfólio
- Problemas identificados:
  - 25/32 sem stop_loss
  - IDs duplicados (pos_032, pos_036)
  - Tickets inconsistentes

**Por que analisar**: Fonte primária dos problemas identificados.

---

## 🗂️ ESTRUTURA DE ARQUIVOS

```
agent-especialista-mercado-financeiro/
├── 📝 CHANGELOG.md ← Histórico de mudanças
├── 📚 (este arquivo) INDICE_DOCUMENTACAO_SPRINT_EMERGENCIAL.md
│
├── docs/gestao-agil/
│   ├── 📋 backlog.md ← 11 histórias de usuário
│   ├── 📊 RESUMO_EXECUTIVO_SPRINT_EMERGENCIAL_RISCO.md
│   │
│   └── conversas/
│       └── 🗣️ 2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md
│
└── backend/
    ├── data/portfolio/
    │   └── 📁 portfolio_atual.json ← 32 posições com problemas
    │
    └── gerador_relatorio_html.py ← (será atualizado com US-RISCO-001)
```

---

## 🚀 ROADMAP RÁPIDO

### Hoje (Sprint 0) - ~5h
1. ✅ Documentação completa (FEITO)
2. ⏰ US-RISCO-001: Avisos críticos no HTML (2h)
3. ⏰ US-RISCO-002: Correção de dados (3h)

### Semana 1-2 (Sprint 1) - ~26 dias
- Interface "Radical Transparency"
- Sistema de alertas críticos
- Dashboard de risco consolidado
- Validação automatizada

### Semana 3-4 (Sprint 2) - ~36 dias
- Stop loss obrigatório
- Gestão de alavancagem
- Realização parcial de ganhos
- Backtesting calibração

---

## 🎯 PARA QUEM É CADA DOCUMENTO

### 👨‍💼 **Executivos / Stakeholders**
**Leia primeiro**: [Resumo Executivo](./gestao-agil/RESUMO_EXECUTIVO_SPRINT_EMERGENCIAL_RISCO.md)
- Seção "Resumo de 1 minuto"
- Descobertas críticas em tabelas
- Impacto no roadmap

**Tempo**: 3 minutos

---

### 👨‍💻 **Desenvolvedores**
**Leia primeiro**: [Backlog](./gestao-agil/backlog.md)
- Sprint Emergencial completo
- 11 histórias de usuário com critérios de aceitação
- Estimativas e prioridades

**Depois**: [Conversa PO-GP](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md) para contexto

**Tempo**: 20 minutos

---

### 📊 **Product Owner**
**Leia tudo nesta ordem**:
1. [Conversa PO-GP](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md) - Contexto
2. [Backlog](./gestao-agil/backlog.md) - Histórias detalhadas
3. [Resumo Executivo](./gestao-agil/RESUMO_EXECUTIVO_SPRINT_EMERGENCIAL_RISCO.md) - Para apresentação
4. [Changelog](../CHANGELOG.md) - Histórico

**Tempo**: 35 minutos

---

### 💼 **Gerente de Portfólio**
**Leia primeiro**: [Conversa PO-GP](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md)
- Entenda os 5 problemas críticos
- Veja suas ações urgentes (configurar stops, reduzir alavancagem)

**Depois**: Analise [portfolio_atual.json](../backend/data/portfolio/portfolio_atual.json)

**Tempo**: 15 minutos

---

### 🎨 **Designer UX/UI**
**Leia primeiro**: [Conversa PO-GP](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md)
- Seção "Interface Antiga vs Nova"
- Princípio de "Radical Transparency"

**Depois**: [Backlog](./gestao-agil/backlog.md)
- US-UX-001: Interface Radical Transparency (Sprint 1)

**Tempo**: 12 minutos

---

## 🏷️ TAGS E FILTROS

### Por Prioridade
- 🔴 **CRÍTICA**: US-RISCO-001, 002, 004, 005, 006, US-UX-001
- 🟡 **ALTA**: US-RISCO-003, 007, 008, 009, US-DATA-001
- 🟢 **MÉDIA**: US-RISCO-010, 011

### Por Sprint
- **Sprint 0** (Hoje): 3 tarefas
- **Sprint 1** (Semana 1-2): 4 histórias
- **Sprint 2** (Semana 3-4): 4 histórias
- **Médio Prazo** (Mês 2): 2 histórias

### Por Tipo
- 🚨 **Gestão de Risco**: US-RISCO-001 até 011
- 📊 **UX/Interface**: US-UX-001
- 🔧 **Qualidade de Dados**: US-DATA-001, US-RISCO-002

---

## 💡 CONCEITOS-CHAVE

### Radical Transparency
**O que é**: Priorizar honestidade brutal sobre estética agradável.

**Antes**: "✅ POSIÇÃO SAUDÁVEL | Risco: 0.0%"
**Depois**: "⚠️ PROTEÇÕES NÃO CONFIGURADAS | Risco: ILIMITADO"

### Os 5 Riscos Críticos Identificados
1. **78% sem stop loss** (25/32 posições)
2. **32x alavancagem** ($3.2M em $100k)
3. **$63k não realizados** (100% exposto a reversão)
4. **Concentração excessiva** (8 AUD, 5 JPY)
5. **Qualidade de dados** (IDs duplicados, tickets inconsistentes)

### Princípio Aprendido
> **"Interface bonita que esconde risco crítico não é UX excelente, é negligência profissional. Bonito e quebrado não é produto, é cilada."**

---

## 📞 CONTATOS E RESPONSÁVEIS

**Product Owner**: Responsável por backlog e priorização
**Gerente de Portfólio**: Responsável por configuração manual de stops (Sprint 0)
**Time de Desenvolvimento**: Responsável por implementação das 11 histórias
**UX Designer**: Responsável por implementar "Radical Transparency"

---

## 🔄 PRÓXIMAS ATUALIZAÇÕES

Este índice será atualizado conforme:
- [ ] US-RISCO-001 implementada → Adicionar screenshot do novo HTML
- [ ] Sprint 1 iniciada → Adicionar relatório de progresso
- [ ] Backtesting concluído → Adicionar métricas de calibração real
- [ ] Sistema em produção → Adicionar guia de usuário final

---

## 📎 LINKS EXTERNOS

- [Portfolio Atual (JSON)](../backend/data/portfolio/portfolio_atual.json)
- [Gerador Relatório HTML (Python)](../backend/gerador_relatorio_html.py)
- [Instruções Copilot](../.github/copilot-instructions.md)

---

**Última Atualização**: 2025-11-07
**Versão**: 1.0
**Mantenedor**: Product Owner + Time de Documentação

---

## ⚡ ACESSO RÁPIDO (Quick Links)

| Eu sou... | Leia isto primeiro | Tempo |
|-----------|-------------------|-------|
| 👨‍💼 Executivo | [Resumo - Seção "1 minuto"](./gestao-agil/RESUMO_EXECUTIVO_SPRINT_EMERGENCIAL_RISCO.md#-resumo-executivo-1-minuto) | 3min |
| 👨‍💻 Dev | [Backlog - Sprint Emergencial](./gestao-agil/backlog.md#-sprint-emergencial---gestão-de-risco-e-transparência-radical-prioridade-máxima) | 15min |
| 📊 PO | [Conversa PO-GP](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md) | 8min |
| 💼 Gerente Portfolio | [Conversa - Seção Riscos](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md#-descobertas-críticas) | 5min |
| 🎨 Designer | [Proposta UX](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md#-proposta-de-solução) | 6min |

