# Changelog - Agent Especialista Mercado Financeiro

Histórico de melhorias e evoluções do sistema.

---

## [Hotfix / Gate CI] - 2025-11-08

### ✅ PR #2 - Gate CI e Mitigações Rápidas (Minimal Safe-to-Demonstrate)

- Adicionado workflow de PR gate para exigir referência a `DECISAO-002` quando áreas sensíveis mudarem
- Banda de segurança: Execução de Bandit (falha em MEDIUM/HIGH) e execução de testes rápidos de masking/audit
- Quickfixes aplicados: timeouts em requests (`timeout=10`) e bind do servidor para `127.0.0.1` para reduzir exposição
- Artefatos entregues: `backend/utils/masking.py`, `backend/middleware/audit.py` (demo), testes unitários focados e scripts de triagem Bandit
- Issue(s) criadas: #6, #7, #8, #9, #10 (Medium findings prioritizados)

**Motivação:** reduzir custo da falha e fornecer mecanismo de revisão segura para mudanças em áreas sensíveis, conforme DECISAO-002.

## [Sprint Emergencial] - 2025-11-07

### 🚨 DESCOBERTA CRÍTICA - Gestão de Risco e Transparência Radical

**Contexto**: Autoavaliação crítica do sistema revelou risco sistêmico grave no portfólio.

#### 🔴 Problemas Identificados (CRÍTICO)

**Gestão de Risco**:
- ❌ 78% das posições (25/32) **sem stop loss** configurado
- ❌ Alavancagem de **32x** ($3.2M exposição em $100k capital)
- ❌ **$63k de ganhos não realizados** sem proteção
- ❌ Concentração: 8 posições AUD (25%), 5 posições JPY (15.6%)

**Qualidade de Dados**:
- ❌ IDs duplicados: `pos_032` e `pos_036` (2x cada)
- ❌ Formato inconsistente de tickets
- ❌ Preços sem timestamp de atualização
- ❌ Sem validação de schema

**UX Enganosa**:
- ❌ Confiança de ⭐⭐⭐ (60%) **sem backtesting**
- ❌ Mensagem "Risco: 0.0%" tecnicamente correta mas **contexto enganoso**
- ❌ "✅ POSIÇÃO SAUDÁVEL" em posições **sem proteção**
- ❌ Foco em estética ao invés de **transparência de risco**

#### ✅ Soluções Implementadas

**Documentação**:
- ✅ [Conversa PO ↔ Gerente Portfólio](./gestao-agil/conversas/2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md)
- ✅ [Resumo Executivo Sprint Emergencial](./gestao-agil/RESUMO_EXECUTIVO_SPRINT_EMERGENCIAL_RISCO.md)
- ✅ [11 Histórias de Usuário no Backlog](./gestao-agil/backlog.md)

**Princípios Estabelecidos**:
- ✅ **"Radical Transparency"**: Honestidade > Estética
- ✅ **"Bonito e quebrado não é produto, é cilada"**
- ✅ Gestão de Risco como **pré-requisito**, não feature

#### 📋 Roadmap Atualizado

**Sprint 0 - HOJE** (3 tarefas, ~5h):
- [ ] US-RISCO-001: Avisos críticos no relatório HTML
- [ ] US-RISCO-002: Correção de qualidade de dados
- [ ] US-RISCO-003: Documentação de riscos (✅ parcial)

**Sprint 1 - Semana 1-2** (4 histórias, ~26 dias):
- [ ] US-UX-001: Interface "Radical Transparency"
- [ ] US-RISCO-004: Sistema de alertas críticos
- [ ] US-RISCO-005: Dashboard de risco consolidado
- [ ] US-DATA-001: Validação automatizada

**Sprint 2 - Semana 3-4** (4 histórias, ~36 dias):
- [ ] US-RISCO-006: Stop loss automatizado
- [ ] US-RISCO-007: Gestão de alavancagem
- [ ] US-RISCO-008: Realização parcial de ganhos
- [ ] US-RISCO-009: Backtesting para calibração

**Médio Prazo - Mês 2**:
- [ ] US-RISCO-010: Análise de concentração
- [ ] US-RISCO-011: Stress testing

#### 📊 Métricas de Sucesso

**KPIs Críticos**:
- Target: 0/32 posições sem stop loss (atual: 25/32)
- Target: Alavancagem ≤15x (atual: 32x)
- Target: P&L realizado >30% (atual: $0 de $63k)
- Target: 0 IDs duplicados (atual: 4)
- Target: Confiança calibrada em dados (atual: 60% sem base)

**Validação de UX**:
- Target: 100% usuários entendem riscos
- Target: NPS Transparência 9-10/10
- Target: Usuário honestamente inseguro se portfolio arriscado

#### 🎓 Lições Aprendidas

1. **UX Excelente ≠ Interface Bonita**: Em finance, UX = usuário INFORMADO, não feliz
2. **Confiança Sem Dados = Charlatanismo**: ⭐⭐⭐ sem backtesting é desonesto
3. **"Tecnicamente Correto" Pode Ser Moralmente Errado**: Contexto importa
4. **Estética Não Substitui Gestão de Risco**: Feature killer = proteção, não gráfico bonito
5. **Transparência É Feature, Não Bug**: "Sistema beta" honesto > "Sistema perfeito" falso

#### 💼 Impacto Estratégico

**Features PAUSADAS** (até risco sólido):
- ⏸️ Novas estratégias ML
- ⏸️ Integrações exchanges
- ⏸️ Copy trading
- ⏸️ Dashboard performance histórica

**Features ACELERADAS** (prioridade absoluta):
- ⚡ Alertas críticos real-time
- ⚡ Stop loss obrigatório
- ⚡ Dashboard risco consolidado
- ⚡ Backtesting calibração

**Justificativa**:
> *"Sistema com gestão de risco sólida que faz menos é melhor que sistema cheio de features que quebra contas."*

---

## [v2.0] - 2025-11-06

### ✨ Melhorias no Relatório HTML

#### Added
- Campo `ticket` exibido no título das recomendações
- Seção "Informações da Posição" com:
  - Direção (LONG/SHORT) com emoji visual
  - Data de entrada formatada
  - Preço de entrada vs preço atual
  - Variação percentual calculada
  - P&L parcial colorizado (verde/vermelho)
- Documentação em `MELHORIAS_RELATORIO_HTML.md`

#### Changed
- Método `_gerar_lista_recomendacoes()` expandido
- Cards de recomendação com mais contexto visual
- Color coding: Verde (#10b981) LONG, Vermelho (#ef4444) SHORT

#### Improved
- UX mais informativa para traders
- Decisões baseadas em dados completos de posição
- Histórico de operações rastreável por ticket

---

## [v1.5] - 2025-11-06

### 🧹 Limpeza de Dados do Portfólio

#### Removed
- Posições de teste removidas:
  - `pos_002`: EUR/USD SHORT (teste)
  - `pos_003`: CHF/JPY LONG (teste)
  - `pos_004`: GC=F LONG (ouro - teste)

#### Fixed
- Metadados atualizados:
  - `open_positions`: 35 → 32
  - `total_realized_pnl`: $265,660.01 → $0

#### Standardized
- Posição `pos_007` (AUD/CAD):
  - Adicionado `ticket: "#5307183178"`
  - Campos `stop_loss` e `take_profit` padronizados
  - Formato de notas consistente

---

## Convenções de Versionamento

Este projeto segue princípios de versionamento semântico adaptado:

- **Major** (X.0.0): Mudanças arquiteturais significativas
- **Minor** (0.X.0): Novas features ou melhorias substanciais
- **Patch** (0.0.X): Bug fixes e melhorias incrementais
- **[Sprint]**: Descobertas críticas que mudam prioridades

---

## Tags e Categorias

- 🚨 **CRÍTICO**: Riscos sistêmicos, segurança
- ✨ **Feature**: Nova funcionalidade
- 🐛 **Bug Fix**: Correção de erro
- 🧹 **Cleanup**: Refatoração, limpeza
- 📊 **UX**: Melhorias de interface
- 📝 **Docs**: Documentação
- 🎓 **Learning**: Lições aprendidas
- ⚡ **Performance**: Otimizações

---

**Última Atualização**: 2025-11-07
**Responsável**: Product Owner + Time de Desenvolvimento

