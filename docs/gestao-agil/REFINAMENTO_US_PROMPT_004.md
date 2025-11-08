# 🎯 REFINAMENTO TÉCNICO - US-PROMPT-004: Saída Estruturada JSON+Markdown

**Data:** 2025-11-07 22:30 UTC
**Participantes:** Engenheiro Senior + Tech Lead + PO
**Objetivo:** Refinar US-PROMPT-004 antes de execução
**Duração Estimada:** 30 minutos

---

## 🔍 GATE 1: Reunião de Refinamento com Tech Lead

### Pergunta 1: Qual é o schema JSON exato esperado?

**Tech Lead:** Vamos definir estrutura clara.

```json
{
  "metadata": {
    "ativo": "EUR/USD",
    "modo": "trader",
    "timestamp_analise": "2025-11-07T22:30:00Z",
    "ttl_segundos": 3600,
    "versao_schema": "1.0"
  },
  "analise": {
    "drivers": [
      {
        "categoria": "macroeconomico|fundamental|tecnico",
        "titulo": "Descrição breve",
        "impacto": "ALTO|MÉDIO|BAIXO",
        "confianca": 0.85,
        "fonte": "URL ou description"
      }
    ],
    "riscos": [
      {
        "categoria": "politico|economico|tecnico|liquidez",
        "titulo": "Descrição",
        "probabilidade": "ALTA|MÉDIA|BAIXA",
        "impacto": "CRÍTICO|ALTO|MÉDIO|BAIXO",
        "mitigacao": "Descrição de como mitigar"
      }
    ],
    "proximos_passos": [
      {
        "prioridade": 1,
        "acao": "Monitorar dados X",
        "timeline": "Próximas 2 horas",
        "gatilho": "Se Y acontecer, então Z"
      }
    ],
    "fontes": [
      {
        "nome": "Yahoo Finance",
        "url": "https://finance.yahoo.com/...",
        "ultima_atualizacao": "2025-11-07T22:25:00Z"
      }
    ],
    "resumo_executivo": "Texto de 1-2 linhas resumindo a análise"
  }
}
```

**Engenheiro:** Clareza. Perguntas técnicas:

1. ✓ Estrutura fixa ou flexível por modo?
   - **Tech Lead:** Fixa (validação automática)

2. ✓ URLs clicáveis geram links no Markdown?
   - **Tech Lead:** Sim, markdown links auto-gerados

3. ✓ Validação antes ou depois do LLM?
   - **Tech Lead:** Depois (LLM retorna JSON, nós validamos)

---

### Pergunta 2: Como integrar com LLM sem quebrar templates existentes?

**Tech Lead:** Usar prompt customizado que force JSON output.

```python
# No template do LLM, adicionar:
"""
Retorne APENAS JSON válido sem markdown wrapping:
{
  "metadata": {...},
  "analise": {...}
}
"""
```

**Engenheiro:** Risco: LLM pode não retornar JSON puro?

**Tech Lead:**
- Usar `response_format={"type": "json_object"}` (GPT-4o)
- Fallback: parsear JSON de bloco markdown
- Validação: Rejeitar se JSON inválido

---

### Pergunta 3: Markdown Espelhado - estrutura esperada?

**Tech Lead:** Mirror JSON em seções bem-formatadas:

```markdown
# Análise: EUR/USD (Trader Mode)

**Timestamp:** 2025-11-07 22:30 UTC
**TTL:** 60 minutos
**Confiança Geral:** 85%

---

## 📊 Drivers Principais

### [ALTO] Divergência Política Monetária
- **Categoria:** Macroeconômico
- **Confiança:** 85%
- **Fonte:** [ECB Official Communication](https://ecb.europa.eu)

---

## ⚠️ Riscos Identificados

### [CRÍTICO] Eleições Europeias
- **Probabilidade:** Média
- **Impacto:** Crítico
- **Mitigação:** Reduzir posição se volatilidade >25%

---

## 🚀 Próximos Passos

1. **[ALTA]** Monitorar dados de emprego
   - **Timeline:** Próximas 2 horas
   - **Gatilho:** Se NFP > +200k, então revisar posição

---

## 📚 Fontes

- [Yahoo Finance - EUR/USD](https://...)
- [ECB Press Release](https://...)
```

---

### Pergunta 4: Performance esperada (TTR)?

**Engenheiro:** Qual é target de latência?

**Tech Lead:**
- JSON construction: <100ms
- LLM call: 2-5s (dependendo de API)
- Markdown generation: <50ms
- **Total:** ~3-6 segundos

**Engenheiro:** Dentro do aceitável. Vamos cachear JSON?

**Tech Lead:** Versão 1 sem cache. V2.0 adiciona Redis.

---

### Pergunta 5: Bloqueadores Técnicos Identificados?

**Engenheiro (checklist):**
- [ ] TemplatesAnalise integrado? ✅ SIM (US-003)
- [ ] LLM endpoint funciona? ✅ SIM (mock + real)
- [ ] JSON parser no Python? ✅ SIM (json stdlib)
- [ ] Markdown gerador? ⚠️ NÃO (precisa criar)
- [ ] Validação schema? ⚠️ PARCIAL (Pydantic pode ajudar)

**Tech Lead:** Recomendação:
1. Usar `json` stdlib (sem dependências)
2. Usar Pydantic para schema validation (já em requirements? verificar)
3. Template Markdown customizado em método estático

**Engenheiro:** Adicionar Pydantic se não existir. Confirmar com PO.

---

### Pergunta 6: Mudanças no Orquestrador?

**Tech Lead:**
```python
# Fluxo novo:
1. LLM retorna JSON (força com response_format)
2. Validar JSON com Pydantic
3. Estruturar em ResponseAnalise (modelo)
4. Gerar Markdown em paralelo
5. Retornar {json, markdown}
```

**Engenheiro:** Quebra compatibilidade com código existente?

**Tech Lead:**
- Função nova: `analisar_ativo_estruturado()`
- Função antiga: `analisar_ativo()` continua igual
- Ambas convivem até deprecação

---

## 💡 GATE 2: Oportunidades Novas Identificadas

### Oportunidade 1: Caching Inteligente
- **Descrição:** Cache JSON de mesma análise em 1h
- **Valor:** Reduz carga LLM em 30%
- **Esforço:** 2h (V2.0)
- **Prioridade:** Baixa (nice-to-have)
- **Registrar no:** Backlog V2.0

### Oportunidade 2: Validação de Coerência JSON
- **Descrição:** Validar que drivers, riscos e ações são coerentes
- **Valor:** Evita contradições nas análises
- **Esforço:** 4h
- **Prioridade:** Média (MVP+)
- **Registrar no:** Backlog para pós-MVP

### Oportunidade 3: Export para PDF
- **Descrição:** Gerar PDF a partir do Markdown
- **Valor:** Compartilhamento profissional
- **Esforço:** 3h (com biblioteca)
- **Prioridade:** Baixa (nice-to-have)
- **Registrar no:** Backlog V2.0

### Oportunidade 4: API REST para JSON
- **Descrição:** Endpoint `/api/analise/{ativo}` retorna JSON
- **Valor:** Integração com frontend
- **Esforço:** 4h (com FastAPI)
- **Prioridade:** Alta (mas pós-Trilha A/B)
- **Registrar no:** Backlog Sprint 2

---

## 🔐 GATE 3: Consulta ao PO sobre Decisões

### Decisão 1: Adicionar Pydantic?

**Engenheiro:** Pydantic não está em `requirements.txt`. Adicionar?

**PO Provisório (aprovado):**
✅ **SIM** - Pydantic é padrão para validação, reduz bugs
- Adicionar: `pydantic>=2.0.0`
- Versão: Latest stable (2.x)

### Decisão 2: Response Format JSON no LLM?

**Engenheiro:** `response_format={"type": "json_object"}` usa tokens extras (~20% mais).

**PO Provisório (aprovado):**
✅ **SIM** - Valer a pena evitar parsing de markdown
- Benefício: 100% confiável vs ~90%
- Custo: +20% tokens, +0.5s latência
- ROI: Positivo

### Decisão 3: Gerar Markdown ou apenas retornar JSON?

**Engenheiro:** Ambos, ou apenas JSON?

**PO Provisório (aprovado):**
✅ **AMBOS** - Markdown para UI, JSON para API
- Estrutura: `{json: {...}, markdown: "..."}`
- Validação: JSON é source of truth
- Geração: Markdown é determinístico (pode regenerar)

### Decisão 4: Deprecar `analisar_ativo()` ou manter?

**Engenheiro:** Função antiga vs nova?

**PO Provisório (aprovado):**
✅ **MANTER AMBAS** - Backward compatibility
- Nome: `analisar_ativo()` continua
- Nome: `analisar_ativo_estruturado()` nova
- Migration: Gradual (V2.0+)
- Aviso: Adicionar deprecation warning em V2.0

---

## 📋 GATE 4: Reorganização do Backlog (Papel PO)

### Bloqueadores Removidos
- ❌ Pydantic não incluía → ✅ Vamos incluir
- ❌ Schema não definido → ✅ Definido acima
- ❌ Markdown format não claro → ✅ Exemplo pronto

### Novas Tarefas Criadas
1. **TASK-001:** Adicionar Pydantic em requirements.txt (5 min)
2. **TASK-002:** Criar modelo Pydantic ResponseAnalise (1h)
3. **TASK-003:** Implementar markdown formatter (1.5h)
4. **TASK-004:** Refatorar LLM call para forçar JSON (1h)
5. **TASK-005:** Testes de validação (1h)

### Oportunidades para Backlog Futuro
- [ ] **V2.0-CACHE:** Sistema de caching inteligente
- [ ] **V2.0-COHERENCE:** Validação de coerência JSON
- [ ] **V2.0-PDF:** Export para PDF
- [ ] **SPRINT-2-API:** Endpoint REST para análises

### Priorização Revisada
1. **ESTA SEMANA (MVP):**
   - ✅ US-PROMPT-003 (DONE)
   - ⏳ US-PROMPT-004 (NEXT - 2d)
   - ⏳ US-PROMPT-006 (1d)
   - ⏳ US-RISCO-004 (6h)
   - ⏳ US-RISCO-005 (8h)

2. **PRÓXIMA SEMANA (MVP+):**
   - [ ] TASK-101: Validação de Coerência
   - [ ] TASK-102: API REST inicial
   - [ ] TASK-103: Testes E2E

3. **SPRINT 2 (V2.0):**
   - [ ] Caching
   - [ ] PDF Export
   - [ ] Expansão de modos

---

## ✅ GATE 5: Resumo Executivo Pós-Refinamento

### Escopo US-PROMPT-004 (CONFIRMADO)

**O QUE VAMOS FAZER:**
1. ✅ Criar schema JSON com Pydantic
2. ✅ Forçar LLM a retornar JSON puro
3. ✅ Validar JSON contra schema
4. ✅ Gerar Markdown espelhado
5. ✅ Testes de validação

**O QUE NÃO VAMOS FAZER (escopo futuro):**
- ❌ Caching (V2.0)
- ❌ PDF Export (V2.0)
- ❌ API REST (Sprint 2)
- ❌ Coerência inteligente (MVP+)

**BLOQUEADORES:** NENHUM ✅

**RISCOS IDENTIFICADOS:**
- ⚠️ LLM não segue JSON format (mitigação: fallback parser)
- ⚠️ Performance pior com JSON format (aceitável, +0.5s)

**DEPENDÊNCIAS:**
- ✅ US-PROMPT-003 (DONE)
- ✅ TemplatesAnalise (READY)
- ⚠️ Pydantic (instalar)

---

## 🚀 PRONTOS PARA EXECUÇÃO

**Status Pré-Execução:** ✅ GREEN

- ✅ Escopo claro e testável
- ✅ Schema definido e validado
- ✅ Tech stack escolhido (Pydantic)
- ✅ Markdown format especificado
- ✅ Sem bloqueadores técnicos
- ✅ Oportunidades identificadas e registradas
- ✅ PO aprovou decisões

**Estimativa de Esforço:** 2 dias de trabalho solo
**Timeline:** Nov 8-9 (2025)
**Próximo Passo:** Engenheiro assume controle → Execução

---

**Aprovado por:** PO Provisório (Engenheiro em duplo papel)
**Tech Lead:** Validado
**Engenheiro:** Pronto para executar
