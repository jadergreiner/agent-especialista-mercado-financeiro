# 🎯 REUNIÃO DE REFINAMENTO - US-RISCO-003: Radical Transparency na Interface

**Data:** 07/11/2025 16:15 UTC
**Sprint:** Sprint Emergencial - Gestão de Risco
**Prioridade:** 🔴 CRÍTICA
**Facilitador:** Tech Lead / Product Owner
**Participantes:** Engenheiro Senior, Tech Lead, PO

---

## 📋 PAUTA DA REUNIÃO

### 1. ALINHAMENTO DE CONTEXTO

#### Situação Atual
- ✅ **US-RISCO-001** Concluído: Avisos críticos implementados no HTML
- ✅ **US-RISCO-002** Concluído: Qualidade de dados corrigida e validação automática
- 🔄 **US-RISCO-003** Pendente: Radical Transparency na interface
- 🔄 **US-RISCO-004** Pendente: Dashboard consolidado de exposição
- 🔄 **US-RISCO-005** Pendente: Alertas críticos automatizados

#### Descobertas Críticas
- 78% das posições sem stop loss (25/32 posições)
- Alavancagem total: 32x (EXTREMAMENTE PERIGOSA)
- P&L não realizado: $63k em exposição
- Interface otimista que mascara riscos (confiança 60% quando deveria ser 20-30%)

#### Princípio Norteador
**"Interface bonita que esconde risco crítico não é UX excelente, é negligência profissional"**

---

### 2. ENTENDIMENTO TÉCNICO DA FEATURE

#### Objective Statement (User Story)
```
COMO:      Gerente de Portfólio
QUERO:     Interface que grita riscos na cara do usuário
PARA QUÊ:  Evitar confiança falsa baseada em estética
```

#### Critérios de Aceitação (Atuais)
- [ ] Substituir "⭐⭐⭐ Confiança Média (60%)" por "⭐ Confiança: BAIXA (20-30%)"
- [ ] Adicionar "⚠️ SISTEMA EM FASE BETA - SEM VALIDAÇÃO HISTÓRICA"
- [ ] Mostrar "Risco Atual: ILIMITADO (sem stop loss)" em vermelho
- [ ] Botões de ação para configuração urgente de proteções

#### Onde Implementar (Questionário para Tech Lead)
1. **No HTML Report** (já existe seção 🚨 ALERTAS CRÍTICOS)?
   - Sim, aproveitar e expandir
   - Status: US-RISCO-001 criou a base

2. **Na CLI Prompt Interativo**?
   - Possível adicionar disclaimers/avisos no início de cada análise
   - Status: Orquestrador tem estrutura pronta

3. **Na Web UI** (se existe)?
   - Avaliar caso a caso
   - Status: Verificar se `backend/app_dashboard.py` usa HTML gerado

#### Arquitetura de Implementação (Questões Técnicas)

**Q1: Onde vive a "confiança" do sistema?**
- A: Existe em `calibrador_confianca.py` - componente que computa score
- A: Também em `validador_consistencia.py` - score de qualidade
- **Ação:** Downgrade forçado em ambos para 20-30%

**Q2: Qual componente gera o HTML/Interface?**
- A: `backend/gerador_relatorio_html.py` - já tem alertas críticos
- A: `backend/orquestrador_analise.py` - prepara dados para análise
- **Ação:** Expandir seção de alertas no HTML report

**Q3: Precisa de novo componente ou apenas modificações?**
- A: Modificações em componentes existentes + integração
- **Ação:** Criar `backend/sistema_transparency_radical.py` para centralizar lógica

**Q4: Que metricas usar para "Risco Atual"?**
- A: Usar dados já coletados (posições sem stop, alavancagem, P&L não realizado)
- **Ação:** Integrar validador_dados com gerador_relatorio

---

### 3. DÚVIDAS TÉCNICAS DO TIME

#### Dúvida 1: Impacto no UX
**Pergunta:** Se você força confiança baixa (20-30%), o usuário não vai desconfiar de qualquer insight positivo?

**Resposta (PO):** Exatamente! Isto é CORRETO. Preferimos desconfiança saudável sobre confiança falsa. O objetivo é mudar a narrativa de "sistema confiável" para "sistema conservador que aprende com validação de histórico". Depois, com backtesting realizado, a confiança sobe organicamente.

**Ação Tech Lead:** Incluir meta na histórico de tarefas: "Confiança sobe para 60%+ apenas após validação histórica (backtest ≥90% acurácia)"

#### Dúvida 2: Impacto no Prompt MVP
**Pergunta:** Se colocamos muito disclaimer/alerta, a análise fica poluída?

**Resposta (Tech Lead):** Separar responsabilidades:
- **Seção de ALERTAS CRÍTICOS:** Separada visualmente (topo do documento)
- **Análise em si:** Mantém clareza, apenas adiciona fontes + timestamp
- **Disclaimers legais:** Rodapé do documento com "SEM RECOMENDAÇÃO INVESTIMENTO"

**Ação Tech Lead:** Criar template estruturado com 3 seções bem demarcadas

#### Dúvida 3: Validação Automática - Quando Rejeitar Análise?
**Pergunta:** Se dados estão velhos ou inconsistentes, devemos rejeitar a análise?

**Resposta (PO + Tech Lead):** Sim, com fallback gracioso:
- Dados > 1h: Alerta amarelo "dados desatualizados, use com cautela"
- Dados > 4h: Bloqueia análise, sugere refresh
- Inconsistência > 80%: Bloqueia análise

**Ação Engenheiro:** Implementar sistema de gates de qualidade antes de gerar análise

---

### 4. BLOQUEIOS E DESAFIOS

#### Bloqueio 1: Dados Incompletos
- **Problema:** Nem todas as posições têm histórico de preço
- **Resolução (Tech Lead):** Usar último preço conhecido + alerta vermelho
- **Ação:** Implementar fallback com timestamp claro

#### Bloqueio 2: Confiança "Hardjcoded" vs Componente Legado
- **Problema:** Código antigo pode ter confiança 60% hardcoded em strings
- **Resolução (Engenheiro):** Grep por "60%" + "Confiança" e substituir dinamicamente
- **Ação:** Script de validação antes de deploy

#### Bloqueio 3: API OpenAI Pode Falhar
- **Problema:** Se LLM não responde, que mostramos?
- **Resolução (Tech Lead):** Fallback para análise determinística + alerta de serviço limitado
- **Ação:** Implementar circuit breaker com resposta segura

---

### 5. OPORTUNIDADES IDENTIFICADAS (FORA DESTA FEATURE)

#### Oportunidade 1: Audit Trail
- **O quê:** Registrar TODAS as análises (input + output + timestamp + versão modelo)
- **Por quê:** Compliance + learning + validação histórica
- **Quando:** Próximo sprint (Fundação Operacional)
- **Registro:** Backlog como US-QUALIDADE-006

#### Oportunidade 2: Modo "Cético"
- **O quê:** Modo CLI que questiona automaticamente a confiança da análise
- **Por quê:** Aumentar questionamento do usuário
- **Quando:** Pós-MVP (após validação utilidade)
- **Registro:** Backlog como US-PROMPT-007

#### Oportunidade 3: Integração com Telegram
- **O quê:** Alertas críticos por Telegram quando risco ultrapassa threshold
- **Por quê:** Notificação real-time sem abrir interface
- **Quando:** Sprint Alertas Críticos (US-RISCO-005)
- **Registro:** Já planejado

---

### 6. DEFINIÇÃO CLARA DE DONE

#### Requisitos Funcionais
- [ ] Confiança do sistema downgrade 60% → 20-30%
- [ ] Disclaimer "SISTEMA EM FASE BETA" visível em TODAS as análises
- [ ] Alerta "RISCO ILIMITADO (sem stop loss)" em vermelho se aplicável
- [ ] Botões de ação para "CONFIGURAR PROTEÇÕES" clicáveis no HTML
- [ ] Gates de qualidade de dados (rejeita se dados > 1h ou inconsistência > 80%)
- [ ] Fallback gracioso se API OpenAI falhar

#### Requisitos Não-Funcionais
- [ ] Zero hard-coded "60%" confiança no código
- [ ] Latência de análise < 25s (mesmo com validações adicionais)
- [ ] 100% das análises com timestamp e versão do modelo
- [ ] Logs de auditoria em arquivo (rotativo, max 7 dias)

#### Testes Mínimos Viáveis
- [ ] EURUSD com histórico positivo (deve mostrar alertas + análise clara)
- [ ] EURUSD com dados velhos (> 1h, deve alertar)
- [ ] EURUSD com inconsistência (deve rejeitar com mensagem clara)
- [ ] Sem API OpenAI (deve fallback gracioso)

---

### 7. ESTIMATIVA E ALOCAÇÃO

#### Esforço Estimado
- **Implementação:** 4h
- **Testes:** 2h
- **Documentação:** 1h
- **Integração:** 1h
- **Total:** 8h ≈ 1 dia de trabalho

#### Sequência de Execução
1. **Fase 1 (2h):** Criar `sistema_transparency_radical.py` + downgrade confiança
2. **Fase 2 (2h):** Integrar validators + gates de qualidade em orquestrador
3. **Fase 3 (2h):** Atualizar templates HTML + CLI com disclaimers
4. **Fase 4 (2h):** Testes + fallback + documentação

---

### 8. DEFINIÇÃO DO PRÓXIMO PASSO

#### Micro-Decisões Confirmadas pelo Time
1. ✅ **Confiança 20-30%:** Downgrade forçado, sem exceções
2. ✅ **Disclaimers separados:** Seção própria no documento
3. ✅ **Gates de qualidade:** Rejeita análise se dados > 1h ou inconsistência > 80%
4. ✅ **Audit trail:** Registro planejado para próximo sprint
5. ✅ **Telegram:** Integrado em US-RISCO-005

#### Responsáveis por Fase
- **Fase 1-4:** Engenheiro Senior (hoje)
- **Code Review:** Tech Lead (ainda hoje)
- **Validação:** PO (amanhã com dados reais)

#### Próxima Reunião
- **Quando:** Assim que fase 2 concluída (≈ em 4h)
- **Tipo:** Tech Review (validar design de gates + fallback)
- **Participantes:** Tech Lead + Engenheiro

---

## ✅ AÇÕES CONFIRMADAS

| Ação | Responsável | Prazo | Status |
|------|-------------|-------|--------|
| Criar `sistema_transparency_radical.py` | Engenheiro | Hoje | ⏳ |
| Downgrade confiança 60% → 20-30% | Engenheiro | Hoje | ⏳ |
| Integrar validators em orquestrador | Engenheiro | Hoje | ⏳ |
| Atualizar templates HTML + CLI | Engenheiro | Hoje | ⏳ |
| Code Review + validação | Tech Lead | Hoje | ⏳ |
| Testar com dados reais | PO | Amanhã | ⏳ |
| Registrar oportunidades no backlog | PO | Hoje | ⏳ |

---

## 📝 NOTAS ADICIONAIS

### Princípios Confirmados
- "Transparência Radical" > "UX Bonita"
- "Desconfiança Saudável" > "Confiança Falsa"
- "Dados Válidos" > "Análise Rápida"

### Contexto da Organização
- Projeto passou por pivot crítico após descoberta de riscos sistêmicos
- Prioridade máxima: proteger capital do usuário
- Confiança ganha através de validação histórica, não promessas

### Referência para Próximas Reuniões
- Ver também: `docs/ANALISE_GERAL_PROJETO.md` (contexto completo)
- Ver também: `docs/gestao-agil/backlog.md` (roadmap atualizado)
- Ver também: `2025-11-07_PO_GerentePortfolio_Melhorias_UX_Risco.md` (descobertas originais)

---

**Reunião concluída com alinhamento 100%**
**Próxima ação: Implementação começando agora**
