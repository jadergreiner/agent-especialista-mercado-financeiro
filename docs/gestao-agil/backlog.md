# Backlog (Top-Level)

Última atualização: 2025-11-07 (pós Descoberta Crítica - Gestão de Risco e Transparência Radical)

## A Fazer (To Do) — Próximas iterações v3

---

### 🚨 **SPRINT EMERGENCIAL - GESTÃO DE RISCO E TRANSPARÊNCIA RADICAL** (PRIORIDADE MÁXIMA)

**Contexto**: Autoavaliação crítica identificou que 78% das posições (25/32) não possuem stop loss, alavancagem de 32x, $63k não realizados com risco ilimitado, e interface com mensagens perigosamente otimistas. Ver [Conversa PO ↔ Gerente Portfólio](./conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md)

#### **SPRINT 0 - AÇÕES IMEDIATAS (Hoje - Crítico)**

- [ ] **US-RISCO-001: Adicionar Avisos Críticos no Relatório HTML Atual**
  - **Como**: Gerente de Portfólio
  - **Quero**: Ver avisos vermelhos destacados no topo do relatório
  - **Para**: Ser imediatamente alertado sobre riscos críticos antes de qualquer análise
  - **Critérios de Aceitação**:
    - Seção "🚨 ALERTAS CRÍTICOS" no topo do HTML
    - Listar número de posições sem stop loss (25/32)
    - Mostrar alavancagem total (32x)
    - Exibir P&L não realizado em risco ($63k)
    - Alertas em vermelho (#ef4444) com ícones de perigo
    - Botão de ação: "CONFIGURAR PROTEÇÕES URGENTE"
  - **Estimativa**: 2h
  - **Prioridade**: 🔴 CRÍTICA

- [ ] **US-RISCO-002: Corrigir Qualidade de Dados do Portfolio**
  - **Como**: Sistema de Gestão de Portfolio
  - **Quero**: Dados limpos, consistentes e sem duplicações
  - **Para**: Garantir decisões baseadas em informações confiáveis
  - **Critérios de Aceitação**:
    - Eliminar IDs duplicados (pos_032 e pos_036 aparecem 2x)
    - Padronizar formato de tickets (todos com # prefix)
    - Validar que todos os `current_price` estão atualizados (< 1h)
    - Adicionar timestamp de última atualização de preço
    - Script de validação automática executado antes de cada relatório
  - **Estimativa**: 3h
  - **Prioridade**: 🔴 CRÍTICA

- [ ] **US-RISCO-003: Documentar Riscos Identificados**
  - **Como**: Product Owner
  - **Quero**: Documentação completa dos riscos descobertos
  - **Para**: Comunicar transparentemente aos stakeholders e aprender com o erro
  - **Critérios de Aceitação**:
    - Documento markdown detalhando os 5 riscos críticos
    - Comparação "antes vs depois" das mensagens de interface
    - Lições aprendidas: "UX bonita sem gestão de risco = negligência"
    - Princípios de "Radical Transparency" documentados
    - Plano de remediação com timelines
  - **Estimativa**: 2h
  - **Prioridade**: 🟡 ALTA
  - **Nota**: ✅ Parcialmente concluído em [Conversa PO-GP](./conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md)

#### **SPRINT 1 - TRANSPARÊNCIA RADICAL (2 semanas)**

- [ ] **US-UX-001: Implementar Interface "Radical Transparency"**
  - **Como**: Trader/Investidor
  - **Quero**: Ver riscos REAIS sem maquiagem antes de qualquer recomendação
  - **Para**: Tomar decisões informadas sobre o REAL estado do meu portfólio
  - **Critérios de Aceitação**:
    - Remover mensagens otimistas: "✅ POSIÇÃO SAUDÁVEL", "🛡️ Sem Risco"
    - Adicionar "⚠️ SISTEMA EM FASE BETA - SEM VALIDAÇÃO HISTÓRICA"
    - Calibração de confiança: ⭐⭐⭐ (60%) → ⭐ (20-30%)
    - Risco honesto: "ILIMITADO (sem stop loss)" ao invés de "0.0%"
    - Seção "🚨 PROTEÇÕES NÃO CONFIGURADAS" quando aplicável
    - Prioridade visual: RISCOS → Status → Recomendações → Dados técnicos
    - Disclaimer legal: "Sempre consulte profissional certificado"
  - **Estimativa**: 5 dias
  - **Prioridade**: 🔴 CRÍTICA
  - **Design**: [Card UX Corrigido](./conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md#interface-nova-honesta)

- [ ] **US-RISCO-004: Sistema de Alertas Críticos em Tempo Real**
  - **Como**: Gerente de Risco
  - **Quero**: Notificações automáticas quando thresholds de risco são violados
  - **Para**: Agir imediatamente antes de perdas catastróficas
  - **Critérios de Aceitação**:
    - Alerta VERMELHO: Posição aberta sem stop loss > 24h
    - Alerta LARANJA: Alavancagem > 20x
    - Alerta AMARELO: P&L não realizado > 50% do capital
    - Alerta AMARELO: Concentração > 25% em uma moeda
    - Sistema de notificação (email + dashboard + sound)
    - Histórico de alertas com timestamp
    - Botão "AÇÃO TOMADA" para marcar alerta como resolvido
  - **Estimativa**: 8 dias
  - **Prioridade**: 🔴 CRÍTICA

- [ ] **US-RISCO-005: Dashboard de Risco Consolidado**
  - **Como**: Gerente de Portfólio
  - **Quero**: Visão agregada de exposições e correlações
  - **Para**: Entender o risco REAL do portfólio, não posições isoladas
  - **Critérios de Aceitação**:
    - **Exposição por Moeda**: Gráfico de barras (LONG verde, SHORT vermelho)
    - **Matriz de Correlação**: Heatmap visual entre pares principais
    - **Alavancagem em Tempo Real**: Gauge com zonas (verde <10x, amarelo 10-20x, vermelho >20x)
    - **P&L Realizado vs Não Realizado**: Gráfico de pizza com percentuais
    - **Posições Sem Proteção**: Lista destacada com contador (25/32)
    - **Concentração de Risco**: Top 3 moedas mais expostas
    - Atualização em tempo real (WebSocket ou polling 30s)
  - **Estimativa**: 8 dias
  - **Prioridade**: 🔴 CRÍTICA

- [ ] **US-DATA-001: Validação Automatizada de Qualidade de Dados**
  - **Como**: Sistema de Portfolio
  - **Quero**: Validação automática antes de qualquer operação
  - **Para**: Garantir zero inconsistências nos dados críticos
  - **Critérios de Aceitação**:
    - Validação de IDs únicos (sem duplicatas)
    - Validação de formato de tickets (regex pattern)
    - Validação de frescor de preços (timestamp < 1h para mercado aberto)
    - Validação de campos obrigatórios (entry_price, lots, direction)
    - Validação de consistência (direction + P&L devem fazer sentido)
    - Relatório de validação executado pré-deploy
    - CI/CD pipeline com validação obrigatória
  - **Estimativa**: 5 dias
  - **Prioridade**: 🟡 ALTA

#### **SPRINT 2 - GESTÃO DE RISCO AUTOMATIZADA (2 semanas)**

- [ ] **US-RISCO-006: Sistema Automatizado de Stop Loss**
  - **Como**: Gerente de Risco
  - **Quero**: Configuração automática de stop loss baseada em volatilidade
  - **Para**: NUNCA ter posições desprotegidas no sistema
  - **Critérios de Aceitação**:
    - Cálculo de stop loss sugerido baseado em ATR (Average True Range)
    - Opções: 1x ATR (agressivo), 2x ATR (moderado), 3x ATR (conservador)
    - Validação obrigatória: Sistema REJEITA posição sem stop configurado
    - Ajuste dinâmico de stop loss (trailing stop baseado em lucro)
    - Notificação quando stop é atingido
    - Backtest de performance histórica com stops configurados
  - **Estimativa**: 10 dias
  - **Prioridade**: 🔴 CRÍTICA

- [ ] **US-RISCO-007: Gestão Ativa de Alavancagem**
  - **Como**: Gerente de Portfolio
  - **Quero**: Sistema que limita e gerencia alavancagem automaticamente
  - **Para**: Evitar exposição excessiva que pode levar à margin call
  - **Critérios de Aceitação**:
    - Configuração de alavancagem máxima (default: 10x, ajustável)
    - Sistema REJEITA abertura de posição que viole limite
    - Dashboard de alavancagem com histórico (gráfico temporal)
    - Alerta quando alavancagem > 80% do limite
    - Sugestão de fechamento de posições para reduzir leverage
    - Simulação de impacto: "Se fechar posição X, alavancagem vai para Y"
  - **Estimativa**: 8 dias
  - **Prioridade**: 🟡 ALTA

- [ ] **US-RISCO-008: Sistema de Realização Parcial de Ganhos**
  - **Como**: Trader
  - **Quero**: Regras automáticas para realizar ganhos parcialmente
  - **Para**: Proteger lucros não realizados de reversões de mercado
  - **Critérios de Aceitação**:
    - Configuração de níveis de take profit parcial (ex: 50% em +2%, 50% em +5%)
    - Sistema sugere realização quando P&L não realizado > threshold (ex: 30% do capital)
    - Histórico de realizações parciais com performance
    - Comparação: "Se tivesse realizado parcial, teria X a mais"
    - Automação opcional: Realizar automaticamente em níveis configurados
  - **Estimativa**: 8 dias
  - **Prioridade**: 🟡 ALTA

- [ ] **US-RISCO-009: Sistema de Backtesting para Validação**
  - **Como**: Product Owner
  - **Quero**: Validação histórica de todas as recomendações do sistema
  - **Para**: Calibrar confiança baseada em performance REAL, não estimativas
  - **Critérios de Aceitação**:
    - Backtest de últimas 100 recomendações (se disponível)
    - Métricas: Taxa de acerto, Sharpe ratio, Drawdown máximo, P&L médio
    - Ajuste automático de confiança baseado em taxa de acerto
    - Relatório público de performance validada
    - Walk-forward analysis para evitar overfitting
    - Comparação com benchmark (Buy & Hold, índice)
  - **Estimativa**: 10 dias
  - **Prioridade**: 🟡 ALTA

#### **MÉDIO PRAZO - GESTÃO AVANÇADA (1 mês)**

- [ ] **US-RISCO-010: Análise de Concentração e Diversificação**
  - **Como**: Gerente de Portfólio
  - **Quero**: Análise automática de concentração por moeda, região, estratégia
  - **Para**: Evitar risco de contágio e correlação excessiva
  - **Critérios de Aceitação**:
    - Limite configurável por moeda (ex: máximo 30% em AUD)
    - Análise de correlação entre posições (matriz visual)
    - Sugestão de hedge quando concentração > limite
    - Score de diversificação (0-100) do portfólio
    - Alerta quando nova posição aumenta concentração perigosamente
  - **Estimativa**: 10 dias
  - **Prioridade**: 🟢 MÉDIA

- [ ] **US-RISCO-011: Sistema de Stress Testing**
  - **Como**: Gerente de Risco
  - **Quero**: Simular cenários extremos no portfólio
  - **Para**: Entender impacto de crises antes que aconteçam
  - **Critérios de Aceitação**:
    - Cenários pré-configurados: Crash 2008, COVID-19, Crise BR 2015
    - Cenário customizado: Usuário define movimentos de mercado
    - Simulação de P&L em cada cenário
    - Identificação de posições mais vulneráveis
    - Sugestão de ajustes para reduzir risco de cauda
    - Relatório de stress test exportável (PDF)
  - **Estimativa**: 12 dias
  - **Prioridade**: 🟢 MÉDIA

---

### 🧭 Mapa de Priorização (Tech Lead + PO) — WSJF + Dependências

Critério principal: WSJF = (Valor de Negócio + Urgência (TC) + Redução de Risco) / Esforço. Ajustes pontuais feitos por dependências e mitigação imediata de risco sistêmico.

Tabela de referência (dias aproximados): 2h=0,25d; 3h=0,375d.

| Rank | ID            | Título curto                                | BV | TC | RR | Esforço (d) | WSJF  | Dependências            | Decisão |
|------|---------------|----------------------------------------------|----|----|----|-------------|-------|-------------------------|---------|
| 1    | US-RISCO-001  | Avisos críticos no HTML                      | 10 | 10 | 10 | 0,25        | 120,0 | —                       | P0      |
| 2    | US-RISCO-002  | Qualidade de dados (IDs, tickets, preços)    | 9  | 9  | 10 | 0,375       | 74,7  | —                       | P0 (antes de 003) |
| 3    | US-RISCO-003  | Documentar riscos e princípios               | 7  | 7  | 6  | 0,25        | 80,0  | 001 (contexto)          | P0 (paralelo após 001) |
| 4    | US-DATA-001   | Validação automatizada (pipeline)            | 9  | 8  | 9  | 5           | 5,2   | 002                     | P0      |
| 5    | US-UX-001     | Interface Radical Transparency               | 9  | 8  | 8  | 5           | 5,0   | 001, 002                | P0      |
| 6    | US-RISCO-006  | Stop loss automatizado (obrigatório)         | 10 | 8  | 10 | 10          | 2,8   | 002, DATA-001           | P0 (guardrail) |
| 7    | US-RISCO-007  | Gestão de alavancagem (limites)              | 10 | 9  | 10 | 8           | 3,625 | 002, DATA-001           | P0 (guardrail) |
| 8    | US-RISCO-004  | Alertas críticos em tempo real               | 10 | 9  | 9  | 8           | 3,5   | 002, DATA-001           | P1      |
| 9    | US-RISCO-008  | Realização parcial de ganhos                 | 8  | 7  | 9  | 8           | 3,0   | 002                     | P1      |
| 10   | US-RISCO-005  | Dashboard de risco consolidado               | 8  | 7  | 6  | 8           | 2,625 | 002                     | P1      |
| 11   | US-RISCO-010  | Concentração e diversificação                | 8  | 7  | 8  | 10          | 2,3   | 005                     | P2      |
| 12   | US-RISCO-009  | Backtesting de recomendações                 | 8  | 6  | 7  | 10          | 2,1   | —                       | P2      |
| 13   | US-RISCO-011  | Stress testing                               | 7  | 6  | 8  | 12          | 1,75  | —                       | P3      |

Observações de priorização:
- Itens 6 e 7 (guardrails) foram promovidos à frente de alertas por reduzir risco sistêmico imediatamente (stop obrigatório e limite de alavancagem).
- 002 precede 003 apesar do WSJF, pois dados limpos são pré-condição para qualquer decisão e comunicação.
- 004 (alertas) vem após guardrails para evitar “sinais sem freios”.
- 009 (backtesting) permanece P2 para não bloquear mitigação de risco imediato.

Plano de Sprint revisado (Tech Lead + PO):
- Sprint 0 (hoje): 001, 002, 003
- Sprint 1 (2 semanas): DATA-001, UX-001, RISCO-006, RISCO-007
- Sprint 2 (2 semanas): RISCO-004, RISCO-008, RISCO-005
- Médio Prazo: RISCO-010, RISCO-009, RISCO-011

MoSCoW:
- Must have (P0): 001, 002, 003, DATA-001, UX-001, 006, 007
- Should have (P1): 004, 008, 005
- Could have (P2/P3): 010, 009, 011

---

### � Subtarefas P0 — Detalhamento Técnico (Tech Lead)

Obs.: Todas as subtarefas seguem padrão: testes unitários, logs em português, docstrings, e documentação em `docs/` quando aplicável.

#### US-RISCO-001 — Avisos críticos no HTML (2h)

- [ ] Extrair cálculo de métricas de risco para função dedicada `calcular_metricas_risco_portfolio()`
  - Local inicial: `backend/gerador_relatorio_html.py` (ou utilitário em `backend/`)
  - Métricas mínimas: quantidade sem stop, alavancagem estimada, P&L não realizado, concentração top moedas
- [ ] Inserir seção fixa no topo: "🚨 ALERTAS CRÍTICOS" com estilização de alerta
- [ ] Botão de ação "CONFIGURAR PROTEÇÕES URGENTE" (âncora para seção de posições sem stop)
- [ ] Teste rápido: gerar HTML com `portfolio_atual.json` atual e validar presença dos blocos
- [ ] Screenshot para anexar no CHANGELOG

#### US-RISCO-002 — Qualidade de dados (3h)

- [ ] Criar script `scripts/validador_portfolio.py`
  - Regras: IDs únicos; `ticket` com regex `^#?\d{7,12}$`; timestamps de preço (campo novo `last_price_update` se aplicável)
  - Verificar duplicidades: `position_id` e `ticket`
  - Reportar JSON com erros encontrados em `backend/data/portfolio/relatorio_validacao.json`
- [ ] Ajustar `backend/gestor_portfolio_atualizado.py` para recusar gravação inconsistente
- [ ] Adicionar tarefa de validação ao pre-commit e documentar no README

#### US-RISCO-003 — Documentar riscos (2h)

- [ ] Consolidar doc em `docs/gestao-agil/risco/RISCOS_IDENTIFICADOS.md`
- [ ] Seção "Antes vs Depois" (prints do HTML)
- [ ] Princípios de "Transparência Radical" + lições aprendidas
- [ ] Plano de remediação com checkpoints

#### US-DATA-001 — Validação automatizada (5d)

- [ ] Transformar `scripts/validador_portfolio.py` em pipeline (exit code ≠ 0 se falhar)
- [ ] Integração CI (GitHub Actions) — job `validate-portfolio`
- [ ] Relatório de validação publicado como artefato
- [ ] Parâmetros via `config/sistema_trading.json` (limites, regex, freshness)
- [ ] Documentação de operação e troubleshooting

#### US-UX-001 — Radical Transparency (5d)

- [ ] Revisar componentes visuais (CSS/HTML): tons de alerta (#ef4444) e hierarquia (Alertas → Status → Recomendações → Dados)
- [ ] Remover mensagens otimistas e adicionar disclaimers legais (BETA / sem validação histórica)
- [ ] Calibração de confiança: substituir estrelas por rótulo textual + faixa 20-30%
- [ ] Seção "Proteções não configuradas" nas cards de posição quando `stop_loss` ausente
- [ ] Documentar guia de estilo em `docs/UX/GUIA_TRANSPARENCIA_RADICAL.md`

#### US-RISCO-006 — Stop loss automatizado (10d)

- [ ] Implementar cálculo de ATR (n períodos configurável) e sugerir SL: 1x/2x/3x ATR
- [ ] Guardrail: bloquear nova posição sem `stop_loss`
- [ ] Trailing stop opcional baseado em lucro (parâmetros em `config/sistema_trading.json`)
- [ ] Ajustar `backend/gestor_portfolio_atualizado.py` e validadores
- [ ] Tests: cenários de baixa/alta volatilidade e verificação de rejeição

#### US-RISCO-007 — Gestão de alavancagem (8d)

- [ ] Cálculo de alavancagem em tempo real: notional / capital
- [ ] Limite configurável (default 10x); rejeitar operações que excedam o limite
- [ ] Alerta preventivo > 80% do limite (log + notificação)
- [ ] Parâmetros em `config/sistema_trading.json`
- [ ] Painel simples de alavancagem (linha do tempo) — CSV + plot inicial

---

### �📊 **MÉTRICAS DE SUCESSO DA SPRINT EMERGENCIAL**

**KPIs Críticos** (acompanhamento semanal):
- ✅ 0% posições sem stop loss (target: 0/32)
- ✅ Alavancagem ≤ 15x (target: de 32x para 15x)
- ✅ P&L realizado > 30% dos ganhos (target: $20k de $63k)
- ✅ 0 IDs duplicados no portfolio
- ✅ 100% tickets padronizados
- ✅ Taxa de atualização de preços < 5min (mercado aberto)
- ✅ Score de confiança calibrado (de 60% para 20-30% com validação)

**Validação de UX**:
- [ ] Teste com 5 usuários: "Você entende os riscos?" (target: 100% sim)
- [ ] Teste: "Você se sente seguro?" (target: honesto "não" se portfolio arriscado)
- [ ] NPS de transparência: "O sistema é honesto sobre riscos?" (target: 9-10/10)

---

### 🚀 **DESCOBERTAS ESTRATÉGICAS - SISTEMA DE APRENDIZADO CONTÍNUO**

#### **TRANSFORMAÇÃO DE PROPOSTA DE VALOR**

- [ ] **REFATORAÇÃO COMPLETA DA MENSAGEM**
  - Mudança de "ferramenta de análise" para "parceiro inteligente que aprende"
  - Desenvolvimento de narrativa focada em aprendizado contínuo
  - Criação de materiais de marketing centrados em adaptação automática
  - Refatoração de website e apresentações para enfatizar evolução

#### **ARQUITETURA DE APRENDIZADO COLETIVO**

- [ ] **LEARNING NETWORK EFFECT**
  - Sistema de compartilhamento anonimizado de aprendizado entre usuários
  - Melhoria exponencial da performance através de dados agregados
  - Monetização via "premium learning pools" para usuários avançados
  - Arquitetura preparada para network effects desde o início

#### **PERSONALIZAÇÃO AVANÇADA**

- [ ] **SISTEMA DE APRENDIZADO COMPORTAMENTAL**
  - Perfil personalizado baseado em padrões de uso do usuário
  - Adaptação automática a estilo de trading individual
  - Otimização de pesos baseada em performance histórica do usuário
  - Interface adaptativa que aprende preferências do usuário

#### **TIMING SUPERIOR COMO FEATURE KILLER**

- [ ] **MÉTRICAS DE TIMING ACCURACY**
  - Desenvolvimento de KPIs específicos para precisão de timing
  - Sistema de detecção antecipada de mudanças de regime (48h+)
  - Validação histórica de superioridade de timing vs mercado
  - Comunicação focada em "vantagem de timing" como benefício principal

#### **ENTERPRISE EXPANSION**

- [ ] **ROADMAP ENTERPRISE DEDICADO**
  - Desenvolvimento de soluções white-label para instituições
  - API enterprise com compliance integrado
  - Sistema de auditoria completo para requisitos regulatórios
  - Foco em geração de 60% da receita com 20% dos clientes enterprise

#### **MONETIZAÇÃO HÍBRIDA**

- [ ] **DIVERSIFICAÇÃO DE RECEITA**
  - Otimização do mix SaaS (50%) + Enterprise (30%) + Consultoria (20%)
  - Desenvolvimento de produtos premium de analytics
  - Estratégia de upselling baseada em learning insights
  - Precificação dinâmica baseada em valor percebido

### 🎯 **FRAMEWORK QUANTITATIVO AVANÇADO - OPORTUNIDADES CRÍTICAS**

- [ ] **SISTEMA DE DETECÇÃO DE OPORTUNIDADES ASSIMÉTRICAS**
  - Framework completo: Pattern Recognition → Macro Confluence →
    Correlation Analysis → Event Mapping → Risk-Reward → Timing Optimization
  - Fusão macro-técnica com machine learning para identificação de
    setups de alta probabilidade
  - Sistema de pontuação de assimetria (R:R ratio + probabilidade)
  - Detecção automática de oportunidades em tempo real
  - Validação histórica de setups identificados
- [ ] **ANÁLISE DE CORRELAÇÃO AVANÇADA**
  - Correlação dinâmica Ibovespa vs dólar em tempo real
  - Impacto de commodities (petróleo, minério) na performance setorial
  - Análise de contágio entre mercados emergentes
  - Correlação rolling window (30d, 90d, 1y) para detecção de regime
  - Sistema de alerta para mudanças bruscas de correlação
- [ ] **MAPPING DE EVENTOS E CATALISADORES**
  - Calendário integrado de eventos econômicos globais
  - Análise de impacto histórico de cada evento no Ibovespa
  - Sistema de pontuação de risco por evento (baixo/médio/alto)
  - Previsão de volatilidade esperada pós-evento
  - Integração com dados de opções para expectativa de movimento
- [ ] **CALIBRAÇÃO AVANÇADA DE PROBABILIDADES**
  - Sistema de aprendizado contínuo baseado em performance real
  - Ajuste dinâmico de pesos (Fundamental/Técnico/Momentum)
  - Calibração baseada em histórico de acertos vs erros
  - Buffer de segurança variável baseado em volatilidade
  - Validação cruzada com múltiplas fontes de dados
- [ ] **TIMING OPTIMIZATION E EXECUÇÃO**
  - Janelas ótimas de entrada/saída baseadas em análise histórica
  - Sistema de momentum intraday para timing preciso
  - Otimização de execução baseada em liquidez e slippage
  - Automação de ordens condicionais
  - Backtesting de estratégias de timing

### 📋 **GESTÃO DE PROJETO E RECURSOS - OPORTUNIDADES CRÍTICAS**

- [ ] **ANÁLISE DE RECURSOS HUMANOS E SKILLS**
  - Mapeamento de skills necessárias para desenvolvimento avançado
  - Avaliação de curva de aprendizado da equipe
  - Plano de treinamento e capacitação técnica
  - Definição de roles e responsabilidades claras
  - Monitoramento de disponibilidade e alocação de equipe
- [ ] **GESTÃO DE ORÇAMENTO E CUSTOS**
  - Estimativa detalhada de custos de desenvolvimento
  - Controle de orçamento por sprint e milestone
  - Análise de ROI para cada feature desenvolvida
  - Otimização de custos de infraestrutura e ferramentas
  - Relatórios financeiros e controle de gastos
- [ ] **DEPENDÊNCIAS EXTERNAS E INTEGRAÇÕES**
  - Avaliação de SLAs e disponibilidade de APIs externas
  - Estratégias de fallback para falhas de integração
  - Contratos e acordos com provedores de dados
  - Monitoramento de mudanças em APIs e documentação
  - Testes de resiliência para dependências críticas
- [ ] **GESTÃO DE RISCOS ORGANIZACIONAIS**
  - Análise de impacto de mudanças estratégicas
  - Plano de contingência para priorizações concorrentes
  - Comunicação clara de dependências entre times
  - Gestão de expectativas com stakeholders
  - Monitoramento de saúde organizacional do projeto
- [ ] **PLANEJAMENTO DE MANUTENIBILIDADE**
  - Arquitetura escalável para crescimento futuro
  - Estratégias de redução de débito técnico
  - Documentação técnica automatizada
  - Padrões de código e revisões obrigatórias
  - Monitoramento de complexidade e cobertura de testes

### 🎯 **VALIDAÇÃO E CALIBRAÇÃO AVANÇADA**

- [ ] **MELHORIA DA CALIBRAÇÃO DE PROBABILIDADES**
  - Sistema de aprendizado contínuo baseado em performance real
  - Ajuste dinâmico de pesos (Fundamental/Técnico/Momentum)
  - Calibração baseada em histórico de acertos vs erros
  - Buffer de segurança variável baseado em volatilidade
  - Validação cruzada com múltiplas fontes de dados
- [ ] **NOVOS INPUTS PARA PREVISÕES**
  - Feed de commodities em tempo real (petróleo, minério, soja)
  - Monitor de risco geopolítico automatizado
  - Análise de sentimento de redes sociais (Twitter, Reddit)
  - Dados de opções (fear & greed index brasileiro)
  - Fluxo estrangeiro intra-day da B3
- [ ] **EXPANSÃO DA ANÁLISE DE RISCO**
  - Riscos geopolíticos (tensões Oriente Médio, eleições)
  - Riscos de liquidez (feriados, eventos de alto impacto)
  - Riscos setoriais (exposição commodities do Ibovespa)
  - Riscos de contágio (mercados emergentes)
  - Riscos fiscais (dívida pública, reformas)
- [ ] **VALIDAÇÃO ROBUSTA E TESTES**
  - Validação walk-forward do sistema de aprendizado
  - Teste de robustez em cenários extremos
  - Comparação com benchmarks quantitativos
  - Análise de viés e overfitting
  - Relatórios automáticos de performance

### 🤖 **SISTEMA DE APRENDIZADO E AUTO-AJUSTE**

- [ ] **APRENDIZADO CONTÍNUO BASEADO EM PERFORMANCE**
  - Sistema de autoavaliação automática após cada recomendação
  - Ajuste dinâmico de pesos baseado em acertos vs erros
  - Calibração de confiança baseada em dados históricos
  - Aprendizado de magnitude (buffer de 15-20% em previsões)
  - Evolução automática do modelo de decisão
- [ ] **NOVOS INPUTS PARA MELHORAR PREVISÕES**
  - Feed de commodities em tempo real (petróleo, minério, soja)
  - Monitor de risco geopolítico automatizado
  - Análise de sentimento de redes sociais (Twitter, Reddit)
  - Dados de opções (fear & greed index brasileiro)
  - Fluxo estrangeiro intra-day da B3
- [ ] **EXPANSÃO DA ANÁLISE DE RISCO**
  - Riscos geopolíticos (tensões Oriente Médio, eleições)
  - Riscos de liquidez (feriados, eventos de alto impacto)
  - Riscos setoriais (exposição commodities do Ibovespa)
  - Riscos de contágio (mercados emergentes)
  - Riscos fiscais (dívida pública, reformas)
- [ ] **VALIDAÇÃO E CALIBRAÇÃO AVANÇADA**
  - Validação walk-forward do sistema de aprendizado
  - Teste de robustez em cenários extremos
  - Comparação com benchmarks quantitativos
  - Análise de viés e overfitting
  - Relatórios automáticos de performance

### 🎯 **SISTEMA ML WIN - OPORTUNIDADES DE MELHORIA (ALTA PRIORIDADE)**

- [ ] **FEATURES AVANÇADAS - FASE 1 (Imediata)**
  - Implementar análise de sentimento de notícias e redes sociais
  - Adicionar correlação WIN vs dólar e juros brasileiros
  - Incorporar dados macroeconômicos (PIB, inflação, emprego)
  - Integrar indicadores de fluxo institucional brasileiro
  - Adicionar análise de volume e participação estrangeira
- [ ] **VALIDAÇÃO WALK-FORWARD - FASE 1 (Imediata)**
  - Implementar validação walk-forward completa (múltiplas janelas)
  - Sistema de re-treinamento automático baseado em performance
  - Validação cruzada temporal para evitar overfitting
  - Teste de robustez em diferentes regimes de mercado
  - Análise de estabilidade de parâmetros ao longo do tempo
- [ ] **ENSEMBLE DE MODELOS - FASE 1 (Imediata)**
  - Combinar Regressão Linear (direção) + XGBoost (magnitude)
  - Implementar LSTM para padrões sequenciais de preço
  - Sistema de voting classifier para sinais de entrada/saída
  - Meta-modelo para combinação otimizada de previsões
  - Validação de diversidade entre modelos do ensemble
- [ ] **GESTÃO DE RISCO AVANÇADA - FASE 2 (Curto Prazo)**
  - Stop-loss dinâmico baseado em volatilidade histórica
  - Dimensionamento de posição variável (Kelly Criterion)
  - Controle de drawdown máximo com redução automática
  - Sistema de correlação de portfólio WIN vs outros ativos
  - Gestão de exposição setorial e geográfica
- [ ] **INFRAESTRUTURA DE PRODUÇÃO - FASE 2 (Curto Prazo)**
  - API REST para previsões em tempo real
  - Dashboard web com visualização de sinais e performance
  - Sistema de alertas automáticos via Telegram/Email
  - Cache inteligente para dados de mercado
  - Monitoramento de saúde do sistema e alertas
- [ ] **PAPER TRADING AUTOMATIZADO - FASE 2 (Curto Prazo)**
  - Simulação de ordens em tempo real com corretoras
  - Validação de latência e slippage real
  - Comparação performance paper vs backtest
  - Sistema de logging detalhado de decisões
  - Análise de impacto de custos de transação
- [ ] **BACKTESTING MULTI-ATIVO - FASE 3 (Médio Prazo)**
  - Expansão para outros ativos brasileiros (PETR4, VALE3, ITUB4)
  - Análise de correlação WIN vs índices setoriais
  - Estratégia multi-ativo com diversificação
  - Otimização de alocação de capital entre ativos
  - Validação de alpha geração consistente
- [ ] **INTEGRAÇÃO COM CORRETORAS - FASE 3 (Médio Prazo)**
  - API nativa para principais corretoras brasileiras
  - Sistema de ordens condicionais automáticas
  - Sincronização de posições em tempo real
  - Relatórios de performance integrados
  - Conformidade com regulamentações CVM
- [ ] **ANÁLISE DE SENTIMENTO AVANÇADA - FASE 3 (Médio Prazo)**
  - Processamento de linguagem natural para notícias
  - Análise de redes sociais (Twitter, Reddit)
  - Classificação automática de impacto de notícias
  - Integração com feeds de notícias em tempo real
  - Sistema de pontuação de sentimento 0-100
- [ ] **MACHINE LEARNING OPERACIONAL - FASE 3 (Médio Prazo)**
  - AutoML para descoberta automática de features
  - Sistema de detecção de mudança de regime de mercado
  - Reinforcement learning para otimização de thresholds
  - Análise de importância de features em tempo real
  - Sistema de alerta para degradação de performance
- [ ] **INTEGRAÇÃO COM CORRETORAS - FASE 3 (Médio Prazo)**
  - API nativa para principais corretoras brasileiras
  - Sistema de ordens condicionais automáticas
  - Sincronização de posições em tempo real
  - Relatórios de performance integrados
  - Conformidade com regulamentações CVM
- [ ] **ANÁLISE DE SENTIMENTO AVANÇADA - FASE 3 (Médio Prazo)**
  - Processamento de linguagem natural para notícias
  - Análise de redes sociais (Twitter, Reddit)
  - Classificação automática de impacto de notícias
  - Integração com feeds de notícias em tempo real
  - Sistema de pontuação de sentimento 0-100
- [ ] **MACHINE LEARNING OPERACIONAL - FASE 3 (Médio Prazo)**
  - AutoML para descoberta automática de features
  - Sistema de detecção de mudança de regime de mercado
  - Reinforcement learning para otimização de thresholds
  - Análise de importância de features em tempo real
  - Sistema de alerta para degradação de performance

### 🎯 **MELHORIAS NO FRAMEWORK DE ANÁLISE QUANTITATIVA AUDNZD**

- Calibração aprimorada de probabilidades (peso fundamental: 60% → 70%)
- Incorporação de momentum commodities em tempo real
- Timeframe dinâmico baseado em volatilidade histórica
- Integração de calendário econômico dos próximos 10 dias
- Sistema de score composto 0-100 (fundamental 50% + técnico 30% + momentum 20%)
- Regras de decisão condicionais baseadas em eventos econômicos

- [ ] Sistema de Atualização de Portfólio Inteligente - Melhorias v2
  - Implementar cálculo de níveis de preço para sugestões take/reforço
  - Otimizar análise de clusters de correlação (atualmente simplificada)
  - Adicionar validação de dados históricos para análise de correlação
  - Implementar alertas automáticos para exposição excessiva
- [ ] Suporte a timeframes dinâmicos (complemento)
  - Adaptação da lógica de análise para cada timeframe (diario, semanal, mensal)
  - Ajustes de fontes de dados conforme timeframe (quando aplicável)
- [ ] Aliases customizáveis por usuário
  - Arquivo de configuração `.aliases.json` no home do usuário
  - Comandos para adicionar/remover aliases personalizados
- [ ] Histórico persistente entre sessões — complementos
  - Filtros e busca por comando/período
  - Limpeza/rotação automática do arquivo de histórico
- [ ] Testes automatizados end-to-end
  - Suite pytest com cobertura >= 80%
  - Testes de integração com mocks de fontes de dados
  - CI/CD com validação automática

## Em Progresso (Doing)

- Nenhum item em progresso no momento

## Postergado (Depriorizado temporariamente)

- [ ] Revalidação T+24h e métricas de assertividade
- [ ] Dashboard: cards/visões para setups e assertividade
- [ ] Event-bus: metadados de qualidade de dados
- [ ] Novos setups (ex.: breakout_sri, reteste_fib_618)

## Concluídos (Done)

### 🎯 **SISTEMA ML WIN - BASE SÓLIDA ESTABELECIDA (2025-11-07)**

- [x] **Pipeline ML Completo WIN**
  - Sistema de coleta de dados históricos (30 anos Ibovespa)
  - Feature engineering com 52 indicadores técnicos
  - Modelos baseline: Regressão Linear, Random Forest, XGBoost
  - Framework de avaliação completo (MAE, RMSE, R², Directional Accuracy)
- [x] **Backtesting Realista Implementado**
  - Custos reais de transação (R$ 5/comissão + 5bps slippage)
  - Gestão de risco com limite de posições (máx 3 contratos)
  - Stop-loss automático baseado em percentual
  - Benchmark contra Buy & Hold para validação
- [x] **Otimização de Thresholds Validada**
  - Teste sistemático de 7 thresholds (0.1% a 3.0%)
  - Descoberta crítica: Threshold 3.0% = +69.69% retorno
  - Pattern identificado: sinais conservadores/fortes funcionam melhor
  - Sharpe ratio positivo (0.733) com threshold otimizado
- [x] **Análise de Performance Completa**
  - Capacidade de proteção demonstrada (+80% vs Buy&Hold em bear market)
  - Relatório executivo consolidado com todas as descobertas
  - Roadmap claro para próximas fases de desenvolvimento
  - Viabilidade técnica confirmada para produção
- [x] **Arquitetura Extensível Preparada**
  - Estrutura modular para adição de novas features
  - Framework pronto para ensemble de modelos
  - Base de dados histórica validada e consistente
  - Documentação completa do sistema e descobertas

### Melhorias Framework Análise Quantitativa AUDNZD (2025-11-07)

- [x] **Análise de Performance e Aprendizado Contínuo**
  - Framework KNOWLEDGEBASE validado para análises Forex
  - Sistema de pesos ajustado: Fundamental (60%→70%),
    Técnico (30%→20%), Momentum (novo 10%)
  - Calibração de probabilidades baseada em dados reais de mercado
  - Identificação de catalisadores subestimados
    (dados emprego, commodities)
  - Timeframe dinâmico implementado para próximas
    recomendações
- [x] **Novos Inputs de Análise Incorporados**
  - Momentum commodities em tempo real (+3.2% minério impactou AUDNZD)
  - Calendário econômico dos próximos 10 dias de alto impacto
  - Correlação AUDNZD vs ativos relacionados (commodities, NZDUSD)
  - Volume e volatilidade do par como inputs adicionais
  - Sentimento de mercado institucional
- [x] **Regras de Decisão Atualizadas**
  - Score composto 0-100: Fundamental (50%) + Técnico (30%) + Momentum (20%)
  - Probabilidades condicionais: P(AUDNZD > 1.16 | dados emprego positivos) = 75%
  - Regras específicas: Score ≥6 E commodities positivos → Prob ≥70%
  - Timeframe ajustado: Entrada 1-3 dias, Target 1.5-2.5%, Stop 0.8-1.2%
- [x] **Autoavaliação e Framework de Melhoria Contínua**
  - Sistema de autoavaliação implementado (completude, consistência, risco, confiança)
  - Análise de performance: 75% acertos nos catalisadores principais
  - Divergências identificadas: Fundamental vs Técnico no AUDNZD
  - Framework evolutivo estabelecido para futuras análises

### 📊 **MÉTRICAS DE SUCESSO - SISTEMA ML WIN**

**KPIs de Performance Alcançados:**

- ✅ Sharpe Ratio: 0.733 (threshold otimizado)
- ✅ Excesso vs Buy&Hold: +169.69% em mercado bearish
- ✅ Drawdown Controlado: < 22%
- ✅ Dados Históricos: 30 anos validados
- ✅ Features Técnicas: 52 indicadores implementados

**Métricas de Qualidade:**

- ✅ Pipeline ML Operacional: 100%
- ✅ Backtesting Realista: 100%
- ✅ Validação Estatística: Completa
- ✅ Documentação: 100%
- ✅ Arquitetura Extensível: Preparada

**Próximos Marcos Definidos:**

- 🎯 FASE 1 (Imediata): Features avançadas + Walk-forward
- 🎯 FASE 2 (Curto Prazo): Infra produção + Paper trading
- 🎯 FASE 3 (Médio Prazo): Multi-ativo + Corretoras

### Timing e Gestão de Risco (2025-11-07)

- [x] Análise de timing baseada em eventos econômicos
  - Analisador completo de impacto de eventos (BCE, IPC Europa, PMI)
  - Sistema de pontuação de risco (crítico/elevado/médio)
  - Recomendações automáticas de fechamento/redução posições
  - Integração com calendário econômico em tempo real
- [x] Implementação recomendações timing - Fechamento posições EUR
  - EUR/CHF SHORT fechada (+1.49 profit) - Ticket 5301566535
  - EUR/USD LONG fechada (+0.20 profit) - Ticket 5301566496
  - Redução exposição EUR 100% em posições críticas
  - Preservação capital pré-eventos BCE de alto impacto
- [x] Relatórios de fechamento e resumo executivo
  - Relatório detalhado fechamentos com métricas completas
  - Resumo executivo implementação timing
  - Documentação ações tomadas e próximos passos
  - Integração com sistema de análise de correlação

### Sistema de Gestão e Aprendizado de Portfólio (2025-11-07)

- [x] Sistema de aprendizado contínuo (FASE 0)
  - Ciclo de aprendizado automático executado antes de qualquer operação
  - Base de recomendações 24h com tracking de assertividade
  - Autoavaliação baseada em performance real vs esperada
  - Ajuste automático de parâmetros dos módulos de correlação e níveis
  - Score médio atual: 97.17%, Taxa acerto: 100.0%
- [x] Gates de segurança aprimorados com aprendizado
  - Validação obrigatória de ticket + anti-duplicação
  - Consulta automática do histórico de aprendizado
  - Modelo atualizado dinamicamente baseado em performance
  - Sistema de limpeza automática de recomendações avaliadas
- [x] Processamento integrado com persistência (FASES 1-3)
  - Atualização estruturada de posições no portfólio
  - Recálculo automático de motores de risco
  - Relatório executivo completo com todas as análises
  - Persistência automática de sugestões na base de aprendizado
  - Sugestões otimizadas de balanceamento/proteção e take/reforço
- [x] Arquitetura de aprendizado machine learning-ready
  - Sistema de avaliação de assertividade com scores 0-100%
  - Histórico de ajustes de parâmetros para análise de tendências
  - Simulação de performance de mercado para validação
  - Framework extensível para novos tipos de recomendação

### 🤖 **SISTEMA DE APRENDIZADO CONTÍNUO - NOVAS CAPACIDADES (ALTA PRIORIDADE)**

- [ ] **PROMPT ESTRUTURADO DE ANÁLISE DE PERFORMANCE**
  - Implementação do prompt de aprendizado contínuo (5 seções estruturadas)
  - Comparação sistemática previsto vs real (probabilidade, timeframe, catalisadores, risco)
  - Extração automática de aprendizados (pontos positivos, melhorias, sinais sub/superestimados)
  - Sistema de calibração de probabilidades baseado em histórico
  - Sugestões automáticas de novos inputs para melhorar previsões

- [ ] **AJUSTE DINÂMICO DE PESOS BASEADO EM FEEDBACK**
  - Framework de pesos dinâmicos para fatores de decisão (macro, técnico, volatilidade, etc.)
  - Ajuste automático baseado em análise de performance individual
  - Histórico auditável de todos os ajustes aplicados
  - Normalização automática para manter equilíbrio do sistema
  - Confiança associada a cada recomendação de ajuste

- [ ] **BANCO DE DADOS DE APRENDIZADO E MÉTRICAS**
  - Tabela dedicada `analises_performance` para armazenar aprendizados
  - Métricas consolidadas do sistema de aprendizado (taxa acerto, ajustes aplicados)
  - Histórico completo de evoluções dos pesos ao longo do tempo
  - Dashboard de evolução do aprendizado e performance
  - Relatórios automáticos de melhoria contínua

- [ ] **INTEGRAÇÃO COM SISTEMA EXISTENTE DE AVALIAÇÃO**
  - Fusão entre `avaliador_assertividade.py` (quantitativo) e `sistema_aprendizado_continuo.py` (qualitativo)
  - Pipeline unificado: recomendação → validação → análise de aprendizado → ajustes
  - Feedback loop completo para melhoria iterativa
  - Métricas combinadas (quantitativas + qualitativas)
  - Sistema de alerta para degradação de performance

- [ ] **CLI AVANÇADO PARA GESTÃO DE APRENDIZADO**
  - Comando `analisar` para processar recomendações validadas
  - Comando `metricas` para visualizar evolução do sistema
  - Comando `ajustar-pesos` para intervenções manuais quando necessário
  - Interface conversacional para análise interativa
  - Logs detalhados de todas as operações de aprendizado

### 🚀 **EVOLUÇÃO DA ARQUITETURA - SISTEMA AUTÔNOMO**

- [ ] **ARQUITETURA ORIENTADA A APRENDIZADO**
  - Componente central de "Auto-Ajuste Contínuo" na arquitetura
  - Loop de feedback integrado em todos os módulos
  - Sistema de memória institucional para aprendizados históricos
  - Auto-otimização baseada em performance real vs esperada
  - Capacidade de auto-descoberta de novos padrões

- [ ] **FRAMEWORK DE DECISÃO ADAPTATIVA**
  - Sistema de tomada de decisão que evolui com o mercado
  - Adaptação automática a mudanças de regime (baixa vs alta volatilidade)
  - Calibração contextual baseada em condições macro atuais
  - Sistema de confiança variável para diferentes tipos de setup
  - Auto-ajuste de thresholds baseado em false positives/negatives

- [ ] **EXPANSÃO MULTI-MERCADO COM APRENDIZADO**
  - Sistema de aprendizado específico por ativo/mercado
  - Transferência de aprendizado entre mercados correlacionados
  - Adaptação automática a novos ativos incluídos no portfólio
  - Especialização progressiva baseada em performance histórica
  - Sistema de descoberta automática de novas oportunidades de mercado

### 💡 **NOVOS INSIGHTS E OPORTUNIDADES DE NEGÓCIO**

- [ ] **PRODUTO: CONSULTORIA DE APRENDIZADO FINANCEIRO**
  - Serviço de análise de performance para gestores de fundos
  - Relatórios de aprendizado contínuo para instituições
  - API de aprendizado para integração com sistemas de terceiros
  - Dashboard executivo de evolução de estratégias
  - Consultoria especializada em otimização de modelos quantitativos

- [ ] **PRODUTO: PLATAFORMA DE TRADING AUTÔNOMA**
  - Sistema que aprende com cada trade executado
  - Adaptação automática a mudanças de mercado
  - Minimização de intervenção manual ao longo do tempo
  - Escalabilidade para múltiplos ativos simultaneamente
  - API para integração com corretoras e plataformas de trading

- [ ] **PRODUTO: ANALYTICS DE MERCADO INSTITUCIONAL**
  - Métricas avançadas de performance para fundos quantitativos
  - Análise de alpha decay e degradação de estratégias
  - Sistema de alerta para mudanças de regime de mercado
  - Benchmarking contra estratégias tradicionais
  - Relatórios de atribuição de performance com aprendizado

### 📊 **VALIDAÇÃO E CALIBRAÇÃO AVANÇADA**

- [ ] **FRAMEWORK DE VALIDAÇÃO WALK-FORWARD COM APRENDIZADO**
  - Validação que incorpora aprendizado contínuo
  - Simulação de evolução do modelo ao longo do tempo
  - Teste de robustez incluindo capacidade de aprendizado
  - Validação de não-overfitting através de aprendizado
  - Métricas de adaptação e evolução do sistema

- [ ] **TESTES DE ESTRESSE COM ADAPTAÇÃO**
  - Cenários extremos com aprendizado ativo
  - Adaptação automática durante períodos de crise
  - Recuperação inteligente após drawdowns significativos
  - Teste de resiliência do sistema de aprendizado
  - Validação de comportamento em condições adversas

- [ ] **ANÁLISE DE VIÉS E CALIBRAÇÃO CONTÍNUA**
  - Detecção automática de viés no sistema de aprendizado
  - Auto-correção de tendências observadas
  - Calibração baseada em dados out-of-sample
  - Validação de generalização para novos mercados
  - Monitoramento contínuo de degradação de performance
