# 📋 BACKLOG REORGANIZADO - PÓS DECISÕES DE ARQUITETURA

**Data:** 2025-11-07
**Baseado em:** Pivot Estratégico para Prompt Interativo + Arquitetura Modular
**Status:** REORGANIZADO PARA EXECUÇÃO

---

## 🎯 CONTEXTO DAS DECISÕES DE ARQUITETURA

### 1. **PIVOT ESTRATÉGICO: Foco em Prompt Interativo**
- **Antes:** Gestão de portfólio automatizada completa
- **Depois:** MVP de análise sob demanda via linguagem natural
- **Justificativa:** Ciclo de descoberta/valor mais rápido, menor dependência de integrações complexas
- **Impacto:** Priorização de US-PROMPT-001 a 008 como núcleo do MVP

### 2. **ARQUITETURA MODULAR: Separação de Responsabilidades**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Prompt    │ -> │ Orquestrador     │ -> │   LLM OpenAI    │
│  (Interface)    │    │  (Coordenação)   │    │  (Análise)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Ferramentas      │
                       │ - Preço Atual    │
                       │ - Indicadores*   │
                       │ - Notícias*      │
                       └──────────────────┘
```

### 3. **APRENDIZADO CONTÍNUO: Sistema Adaptativo**
- **Framework:** Auto-ajuste baseado em feedback de performance
- **Benefício:** Evolução automática com condições de mercado
- **Impacto:** US futuras devem considerar métricas de aprendizado

### 4. **TRANSPARÊNCIA RADICAL: Riscos em Primeiro Plano**
- **Descoberta Crítica:** 78% posições sem stop loss, alavancagem 32x
- **Impacto:** US-RISCO-* priorizados como críticos de segurança

---

## 📊 ANÁLISE GERAL DO PROJETO

### **FORÇAS (Strengths)**
✅ **Arquitetura Modular:** Separação clara entre dados, análise, estratégias, risco
✅ **Pivot Pragmático:** Foco em valor percebido rápido via CLI
✅ **Aprendizado Contínuo:** Capacidade de evolução baseada em feedback
✅ **Transparência Radical:** Abordagem honesta sobre riscos e limitações

### **OPORTUNIDADES (Opportunities)**
🎯 **Diferencial Competitivo:** Sistema que aprende e se adapta automaticamente
🎯 **Escalabilidade:** Framework extensível para múltiplos mercados
🎯 **Monetização:** Novos produtos baseados em analytics de aprendizado

### **AMEAÇAS (Threats)**
⚠️ **Dependência Externa:** APIs não-oficiais (Yahoo Finance), custos OpenAI
⚠️ **Riscos Operacionais:** Gestão de risco inadequada descoberta recentemente
⚠️ **Complexidade Técnica:** Integração de aprendizado contínuo

### **DESAFIOS (Challenges)**
🔧 **Qualidade de Dados:** Inconsistências descobertas (IDs duplicados, dados desatualizados)
🔧 **Performance:** Latência <20s sem cache, <5s com cache
🔧 **Conformidade:** Disclaimers obrigatórios, linguagem não-prescritiva

---

## 🎪 SPRINTS REORGANIZADOS

### **SPRINT ATUAL: PROMPT INTERATIVO MVP** (Prioridade Máxima)
**Duração:** 2-3 semanas
**Objetivo:** Entregar valor via análise sob demanda
**Métricas de Sucesso:**
- TTR: <20s sem cache, <5s com cache
- Utilidade: ≥80% respostas consideradas úteis
- Cobertura: FX (EURUSD, USDJPY, GBPJPY, AUDNZD), XAUUSD

#### **US-PROMPT-001: CLI Prompt Interativo** ✅ COMPLETADO
- **Status:** ✅ Implementado e testado
- **Entrega:** `orquestrador_analise.py` funcional
- **Validação:** EURUSD/XAUUSD em modos trader/analista

#### **US-PROMPT-002: Orquestrador de Ferramentas** ✅ COMPLETADA
- **Status:** ✅ Implementada e integrada (2025-11-07)
- **Entrega:** Sistema orquestra preço, indicadores e notícias automaticamente
- **Validação:** EURUSD com dados reais de todas as ferramentas
- **Funcionalidades:**
  - Preço atual (Yahoo Finance) com retry e validação mercado
  - Indicadores técnicos (SMA20, RSI14) com pandas-ta
  - Notícias resumidas (mock estruturado) com sentimento
  - Integração completa no orquestrador de análise
- **Correções Implementadas:**
  - Normalização de símbolos forex (EURUSD → EURUSD=X)
  - Tratamento de erros resiliente por ferramenta
  - Estrutura JSON completa com todos os dados
  - Remoção caracteres Unicode para compatibilidade CLI
- **Arquivos Modificados:**
  - `backend/orquestrador_analise.py` - Integração ferramentas
  - `backend/ferramentas/indicadores_tecnicos.py` - Normalização símbolos
  - `backend/ferramentas/noticias_resumidas.py` - Estrutura dados
- **Testes Validados:** CLI trader/analista com saída JSON completa

#### **US-PROMPT-003: Templates e Modos de Análise** 🔄 PENDENTE
- **Como:** Usuário
- **Quero:** Escolher "Analista" (explicativo) vs "Trader Rápido" (objetivo)
- **Para:** Adaptação ao contexto e preferências

#### **US-PROMPT-004: Saída Estruturada + Fontes** 🔄 PENDENTE
- **Como:** Usuário
- **Quero:** JSON padronizado + Markdown com fontes clicáveis
- **Para:** Reuso, auditoria e confiança

#### **US-PROMPT-005: Cache e Memória de Sessão** 🔄 PENDENTE
- **Como:** Usuário recorrente
- **Quero:** Respostas rápidas e contexto preservado
- **Para:** Iteração eficiente

#### **US-PROMPT-006: Segurança e Disclaimers** 🔄 PENDENTE
- **Como:** PO/Compliance
- **Quero:** Mensagens claras de não-recomendação
- **Para:** Evitar interpretações prescritivas

#### **US-PROMPT-007: Métricas de Latência e Logs** 🔄 PENDENTE
- **Como:** Tech Lead
- **Quero:** Medir TTR e erros
- **Para:** Melhorar performance

#### **US-PROMPT-008: Guia de Uso do Prompt** 🔄 PENDENTE
- **Como:** Usuário novo
- **Quero:** Aprender rapidamente como perguntar
- **Para:** Maximizar utilidade

---

### 🧪 **SPRINT DE QUALIDADE: AUTOAVALIAÇÃO E CALIBRAÇÃO** (Prioridade Alta)
**Duração:** 1 semana
**Objetivo:** Corrigir gaps críticos de qualidade identificados na autoavaliação
**Contexto:** Análise EURUSD revelou confiança inflada (90%→65%) devido a dados não integrados

#### **US-QUALIDADE-001: Integração Completa de Dados nos Templates** 🔴 CRÍTICO
- **Como:** Sistema de análise
- **Quero:** Templates que considerem todos os dados disponíveis (preço, indicadores, notícias)
- **Para:** Análises completas e consistentes
- **Problema Atual:** Análise mock ignora preço abaixo SMA e notícias negativas
- **Entrega:** Templates atualizados com seções específicas para cada fonte

#### **US-QUALIDADE-002: Sistema de Calibração Automática de Confiança** ✅ COMPLETADA
- **Como:** Sistema de análise
- **Quero:** Confiança ajustada automaticamente pela qualidade dos dados
- **Para:** Recomendações calibradas ao risco real
- **Problema Atual:** Cenários têm confiança fixa apesar de contexto negativo
- **Entrega:** Algoritmo que reduz confiança baseado em divergências e qualidade
- **Status:** ✅ COMPLETADA (2025-11-07)

#### **US-QUALIDADE-003: Validação de Consistência Entre Fontes** 🔴 CRÍTICO
- **Como:** Sistema de análise
- **Quero:** Alertas quando análise técnica diverge do fundamental
- **Para:** Transparência sobre riscos de divergência
- **Problema Atual:** Preço abaixo SMA (bearish) vs cenários equilibrados
- **Entrega:** Sistema de detecção e alerta de divergências

#### **US-QUALIDADE-004: Incorporação de Sentimento de Notícias** 🟡 ALTA
- **Como:** Sistema de análise
- **Quero:** Cenários ponderados pelo impacto e sentimento das notícias
- **Para:** Análises contextualmente relevantes
- **Problema Atual:** Notícias ALTO/NEGATIVO não influenciam cenários
- **Entrega:** Ponderação automática baseada em sentimento de notícias

#### **US-QUALIDADE-005: Framework de Autoavaliação Automática** 🟡 ALTA
- **Como:** Sistema de qualidade
- **Quero:** Checklist automático de qualidade em cada análise
- **Para:** Consistência e detecção de gaps
- **Entrega:** Sistema que executa autoavaliação automaticamente

---

### **SPRINT EMERGENCIAL: GESTÃO DE RISCO E TRANSPARÊNCIA** (Prioridade Crítica)
**Duração:** 1-2 semanas
**Objetivo:** Corrigir descobertas críticas de risco
**Contexto:** 78% posições sem stop loss, alavancagem 32x, $63k em risco

#### **SPRINT 0: AÇÕES IMEDIATAS** (Hoje - Crítico)

##### **US-RISCO-001: Avisos Críticos no Relatório HTML** 🔴 CRÍTICO
- **Como:** Gerente de Portfólio
- **Quero:** Ver avisos vermelhos destacados no topo
- **Para:** Ser alertado sobre riscos antes de qualquer análise
- **Entrega:** Seção "🚨 ALERTAS CRÍTICOS" com contador 25/32

##### **US-RISCO-002: Corrigir Qualidade de Dados** 🔴 CRÍTICO
- **Como:** Sistema de Portfolio
- **Quero:** Dados limpos e consistentes
- **Para:** Decisões baseadas em informações confiáveis
- **Entrega:** Eliminar duplicatas, padronizar formato tickets

##### **US-RISCO-003: Documentar Riscos Identificados** 🟡 ALTA
- **Como:** Product Owner
- **Quero:** Documentação completa dos 5 riscos críticos
- **Para:** Transparência e aprendizado organizacional

#### **SPRINT 1: TRANSPARÊNCIA RADICAL** (2 semanas)

##### **US-UX-001: Interface "Radical Transparency"** 🔴 CRÍTICO
- **Como:** Trader/Investidor
- **Quero:** Ver riscos REAIS sem maquiagem
- **Para:** Decisões informadas sobre estado real do portfólio
- **Entrega:** Remover mensagens otimistas, adicionar avisos reais

##### **US-RISCO-004: Alertas Críticos em Tempo Real** 🔴 CRÍTICO
- **Como:** Gerente de Risco
- **Quero:** Notificações automáticas quando thresholds violados
- **Para:** Agir antes de perdas catastróficas

##### **US-RISCO-005: Dashboard de Risco Consolidado** 🔴 CRÍTICO
- **Como:** Gerente de Portfólio
- **Quero:** Visão agregada de exposições e correlações
- **Para:** Entender risco REAL do portfólio

##### **US-DATA-001: Validação Automatizada de Qualidade** 🟡 ALTA
- **Como:** Sistema de Portfolio
- **Quero:** Validação automática antes de operações
- **Para:** Zero inconsistências em dados críticos

---

### **SPRINTS FUTUROS: EVOLUÇÃO E ESCALA** (Pós-MVP)

#### **SPRINT APRENDIZADO CONTÍNUO** (3-4 semanas)
- Sistema de aprendizado baseado em feedback de performance
- Framework de ajuste dinâmico de pesos
- Banco de dados de aprendizado com métricas

#### **SPRINT EXPANSÃO MULTI-MERCADO** (4-6 semanas)
- Suporte a índices, ações, cripto, além de FX
- Estratégias específicas por mercado/ativo
- Validação walk-forward com aprendizado

#### **SPRINT PRODUTOS E MONETIZAÇÃO** (6-8 semanas)
- Produto: Consultoria de Aprendizado Financeiro
- Produto: Plataforma de Trading Autônoma
- API Enterprise para instituições

---

## 📈 MÉTRICAS DE SUCESSO POR SPRINT

### **SPRINT PROMPT INTERATIVO MVP**
- **Funcionalidade:** 100% US-PROMPT-* implementadas
- **Performance:** TTR <20s, utilidade ≥80%
- **Qualidade:** 100% respostas com fontes/timestamp
- **Confiabilidade:** Zero alucinações, dados frescos

### **SPRINT GESTÃO DE RISCO**
- **Segurança:** 100% posições com stop loss
- **Transparência:** Calibração confiança 20-30%
- **Qualidade Dados:** Zero duplicatas, 100% validação
- **Monitoramento:** Alertas funcionais 24/7

### **SPRINT APRENDIZADO CONTÍNUO**
- **Adaptação:** Melhoria automática baseada em feedback
- **Robustez:** Performance consistente em diferentes regimes
- **Escalabilidade:** Suporte a múltiplos mercados simultaneamente

---

## 🔄 DEPENDÊNCIAS E SEQUÊNCIA

### **Dependências Técnicas**
1. **OpenAI API Key:** Crítico para LLM (US-PROMPT-001 a 008)
2. **Yahoo Finance:** Dados preço (US-PROMPT-002)
3. **pandas-ta:** Indicadores técnicos (US-PROMPT-002)
4. **SQLite:** Persistência aprendizado (futuro)

### **Sequência de Implementação**
```
SPRINT PROMPT MVP
    ↓ (depende de dados limpos)
SPRINT GESTÃO RISCO
    ↓ (depende de estabilidade)
SPRINT APRENDIZADO CONTÍNUO
    ↓ (depende de feedback)
SPRINT EXPANSÃO MULTI-MERCADO
```

### **Riscos de Dependência**
- **API OpenAI:** Rate limits, custos, disponibilidade
- **Dados Externos:** Qualidade Yahoo Finance, bloqueios
- **Complexidade:** Aprendizado contínuo adiciona complexidade significativa

---

## 💡 RECOMENDAÇÕES ESTRATÉGICAS

### **Para Execução Imediata**
1. **Configurar OpenAI API Key** real para testes LLM
2. **Implementar US-PROMPT-002** (ferramentas) como próximo passo natural
3. **Paralelizar** US-RISCO-* com desenvolvimento funcional

### **Para Arquitetura de Longo Prazo**
1. **Manter Modularidade:** Facilita testes e evolução independente
2. **Priorizar Transparência:** Diferencial competitivo sustentável
3. **Framework de Aprendizado:** Base para produtos premium

### **Para Gestão de Produto**
1. **Métricas de Valor:** Focar em utilidade percebida, não automação
2. **Feedback Loops:** Incorporar aprendizado desde o início
3. **Riscos Primeiro:** Nunca comprometer segurança por funcionalidade

---

## 📋 CHECKLIST DE PRONTO PARA PRÓXIMO SPRINT

### **Técnico**
- [x] Arquitetura modular definida
- [x] Interfaces entre módulos especificadas
- [x] Pipeline de dados estabelecido
- [ ] OpenAI API key configurada
- [ ] Dependências instaladas (pandas-ta, etc.)

### **Produto**
- [x] Pivot estratégico validado
- [x] MVP scope definido claramente
- [ ] Métricas de sucesso estabelecidas
- [ ] Critérios de aceitação documentados

### **Risco**
- [ ] Plano de contingência para APIs externas
- [ ] Estratégia de cache para reduzir dependências
- [ ] Monitoramento de custos OpenAI
- [ ] Backup para fontes de dados

---

**Conclusão:** Backlog reorganizado com foco no valor percebido rápido via Prompt Interativo, mantendo arquitetura modular e priorizando correção dos riscos críticos descobertos. O caminho está claro para entrega incremental de valor com base sólida para evolução futura.</content>
<parameter name="filePath">c:\repo\projetos\agent-especialista-mercado-financeiro\docs\gestao-agil\backlog_reorganizado.md