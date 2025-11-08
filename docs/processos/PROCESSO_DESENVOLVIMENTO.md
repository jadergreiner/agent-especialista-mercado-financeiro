# Processo de Desenvolvimento - Agent Especialista Mercado Financeiro

## Visão Geral

Este documento define o **processo obrigatório** para desenvolvimento de features no projeto Agent Especialista Mercado Financeiro.

**Objetivo:** Garantir qualidade, evitar retrabalho e manter rastreabilidade completa.

**Aplicabilidade:** TODAS as User Stories do backlog

---

## 🔄 Workflow de Desenvolvimento

### **FASE 0: Sincronização Pré-Execução** (5-10 min) 🔴 OBRIGATÓRIA

**Objetivo:** Confirmar que feature está realmente pendente e não foi executada

**Checklist:**

```bash
# 1. Verificar contexto atual
git branch --show-current
git log --oneline -5
git status

# 2. Identificar features completadas recentemente
ls -lt backend/ENTREGA_*.md | head -5
ls -lt backend/CONCLUSAO_*.md | head -5

# 3. Ler relatório de progresso
cat docs/gestao-agil/RELATORIO_PROGRESSO_DAY*.md | tail -50

# 4. Verificar status no backlog
grep -A 10 "US-XXXX" docs/gestao-agil/backlog.md

# 5. Confirmar que feature NÃO tem entrega
ls backend/ENTREGA_US-XXXX.md 2>/dev/null || echo "✅ Feature pendente confirmada"

# 6. Rodar testes existentes (se houver)
python backend/teste_us_*.py 2>/dev/null || echo "Sem testes prévios"
```

**Critérios de Aprovação:**

- [ ] Nenhum arquivo `ENTREGA_US-XXXX.md` ou `CONCLUSAO_US-XXXX.md` existe
- [ ] Relatório de progresso NÃO marca como DONE/COMPLETADA
- [ ] Backlog mostra status PENDENTE (🔄)
- [ ] Dependências satisfeitas (✅)

**Se REPROVADO:** Feature já está completa → Ir para próxima feature do backlog

---

### **FASE 1: Refinamento Técnico** (30-60 min)

**Objetivo:** Destrinchar feature e identificar bloqueadores técnicos

#### 1.1 Leitura da User Story

**Ações:**

```bash
# Abrir backlog e ler seção completa da US
code docs/gestao-agil/backlog.md
# Buscar: US-XXXX

# Extrair:
# - Critérios de aceitação
# - Dependências
# - Estimativa
# - Prioridade
```

**Perguntas a Responder:**

- [ ] Qual o valor de negócio desta feature?
- [ ] Quais são os critérios de aceitação mensuráveis?
- [ ] Quais dependências técnicas existem?
- [ ] Há bloqueadores conhecidos?

#### 1.2 Simulação de Reunião com Tech Lead

**Formato:** Diálogo estruturado (pode ser autodiálogo)

**Tópicos Obrigatórios:**

1. **Arquitetura:**
   - Quais componentes serão modificados?
   - Há risco de regressão?
   - Padrão de design a ser usado?

2. **Integrações:**
   - Quais módulos serão impactados?
   - Há contratos/interfaces a manter?

3. **Testes:**
   - Que tipos de teste são necessários?
   - Cobertura mínima esperada?

4. **Validação:**
   - Como validar que está funcionando?
   - Há métricas de qualidade?

**Output:** Lista de decisões técnicas documentadas

#### 1.3 Consulta ao PO (se necessário)

**Quando Consultar:**

- Critérios de aceitação ambíguos
- Trade-offs de escopo vs tempo
- Oportunidades identificadas fora do escopo

**Formato:**

```markdown
## Consulta ao PO: [Tópico]

**Contexto:** [Situação atual]
**Dúvida:** [Pergunta específica]
**Opções:** 
  A) [Opção 1 + Prós/Contras]
  B) [Opção 2 + Prós/Contras]
**Recomendação Técnica:** [Opção preferida e justificativa]
```

---

### **FASE 2: Planejamento da Implementação** (30 min)

**Objetivo:** Criar plano executável e testável

#### 2.1 Estrutura do Plano

**Template:**

```markdown
# Plano de Implementação: US-XXXX

## 1. Arquivos a Criar
- [ ] `backend/novo_modulo.py` - Descrição
- [ ] `backend/teste_us_xxxx.py` - Testes unitários

## 2. Arquivos a Modificar
- [ ] `backend/orquestrador.py` - Integrar novo módulo (linha ~150)
- [ ] `docs/README.md` - Adicionar referência

## 3. Dependências Externas
- [ ] Instalar: `pip install nova-lib==1.2.3`
- [ ] Configurar: Adicionar variável ENV_VAR em .env

## 4. Passos de Implementação (Ordem)
1. Criar classe base em `novo_modulo.py`
2. Implementar métodos principais
3. Adicionar testes unitários
4. Integrar com orquestrador
5. Rodar testes completos
6. Atualizar documentação

## 5. Critérios de Validação
- [ ] Testes passando: `python backend/teste_us_xxxx.py`
- [ ] Integração funcional: `python backend/orquestrador.py --demo`
- [ ] Lint clean: markdownlint, flake8
- [ ] Critérios de aceitação atendidos

## 6. Riscos Identificados
- Risco 1: [Descrição] - Mitigação: [Como resolver]
- Risco 2: [Descrição] - Mitigação: [Como resolver]
```

#### 2.2 Aprovação do Plano

**Revisar:**

- [ ] Todos os critérios de aceitação estão cobertos?
- [ ] Plano é executável em tempo estimado?
- [ ] Riscos têm mitigação?
- [ ] Testes estão incluídos?

**Se APROVADO:** Prosseguir para FASE 3

---

### **FASE 3: Execução** (Tempo Estimado da US)

**Objetivo:** Implementar feature com qualidade

#### 3.1 Desenvolvimento Iterativo

**Princípios:**

- **TDD (Test-Driven Development):** Escrever testes ANTES do código (quando possível)
- **Commits Atômicos:** 1 commit por mudança lógica
- **Padrão de Commit:** `tipo(escopo): descricao` (sem acentos)

**Tipos de Commit:**

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `test`: Adição/modificação de testes
- `refactor`: Refatoração sem mudança funcional
- `chore`: Tarefas de manutenção

**Exemplo:**

```bash
git commit -m "feat(analise): Adicionar template modo trader"
git commit -m "test(analise): Adicionar testes US-PROMPT-003"
git commit -m "docs(readme): Atualizar guia de uso"
```

#### 3.2 Checklist de Qualidade

**Antes de Marcar como Completo:**

- [ ] **Código:**
  - [ ] Nomes de variáveis/funções em português
  - [ ] Docstrings em português
  - [ ] Sem hardcoded values (usar config)
  - [ ] Tratamento de erros adequado

- [ ] **Testes:**
  - [ ] Testes unitários passando
  - [ ] Cobertura ≥ 80% (se aplicável)
  - [ ] Casos de erro cobertos

- [ ] **Documentação:**
  - [ ] README atualizado (se necessário)
  - [ ] Docstrings completas
  - [ ] Exemplos de uso (se API pública)

- [ ] **Integração:**
  - [ ] Módulo integrado corretamente
  - [ ] Sem quebra de funcionalidades existentes
  - [ ] Testes de integração rodando

---

### **FASE 4: Validação e Entrega** (30 min)

**Objetivo:** Confirmar que feature atende todos os critérios

#### 4.1 Validação Técnica

**Checklist:**

```bash
# 1. Rodar todos os testes
python backend/teste_us_xxxx.py
pytest backend/tests/ -v

# 2. Validar integração
python backend/orquestrador_analise.py --ativo EURUSD --modo analista

# 3. Verificar lint
markdownlint docs/**/*.md
flake8 backend/

# 4. Verificar commits
git log --oneline --grep="US-XXXX" -10
```

#### 4.2 Validação de Critérios de Aceitação

**Processo:**

1. Abrir backlog e ler critérios originais
2. Para cada critério, executar teste específico
3. Marcar ✅ ou ❌
4. Se ❌, voltar para FASE 3

**Exemplo:**

```markdown
## Critérios de Aceitação: US-PROMPT-003

- [✅] Sistema suporta 2 modos: Analista e Trader
  - Teste: `python backend/teste_us_prompt_003.py::test_modos_disponiveis`
  - Resultado: PASS

- [✅] Cada modo tem 2 exemplos few-shot
  - Teste: `python backend/teste_us_prompt_003.py::test_exemplos_analista`
  - Resultado: PASS
  
- [✅] Templates geram contexto correto para LLM
  - Teste: Manual - análise EURUSD modo analista
  - Resultado: Contexto completo com 4000+ chars
```

#### 4.3 Criação de Documentação de Entrega

**Arquivos Obrigatórios:**

1. **`backend/ENTREGA_US-XXXX.md`** (Resumo executivo)

   ```markdown
   # ✅ ENTREGA: US-XXXX - [Título]
   
   ## Resumo
   - Status: ✅ CONCLUÍDA
   - Data: YYYY-MM-DD
   - Tempo: Xh (estimativa: Yd)
   - Testes: X/X PASSANDO
   
   ## Arquivos Entregues
   - `backend/modulo.py` (X linhas)
   - `backend/teste_us_xxxx.py` (Y linhas)
   
   ## Funcionalidades
   - Feature 1: Descrição
   - Feature 2: Descrição
   
   ## Validação
   - [✅] Critério 1
   - [✅] Critério 2
   ```

2. **`backend/CONCLUSAO_US-XXXX.md`** (Detalhes técnicos)

   ```markdown
   # 🎯 US-XXXX - [Título] [✅ COMPLETADA]
   
   ## Contexto Técnico
   [Detalhes da implementação]
   
   ## Arquitetura
   [Diagramas, classes, fluxos]
   
   ## Exemplos de Uso
   [Código exemplo]
   
   ## Métricas
   - Tempo: X vs Y estimado
   - Linhas de código: X
   - Cobertura: X%
   
   ## Extensibilidade
   [Como estender no futuro]
   
   ## Lições Aprendidas
   [Insights técnicos]
   ```

#### 4.4 Atualização do Backlog

**Modificar:** `docs/gestao-agil/backlog.md`

**Mudanças:**

```markdown
### ✅ **US-XXXX: [Título]** - COMPLETADO

- **Status:** ✅ Implementado e validado (YYYY-MM-DD)
- **Entrega:** [Resumo executivo]
- **Validação:** [Testes e métricas]
- **Funcionalidades:** [Lista]
- **Arquivos:** [Links para arquivos criados]
- **Impacto:** [Métricas de valor]
- **Próximo Passo:** [Próxima US recomendada]
```

#### 4.5 Commit Final

```bash
# Stage todos os arquivos
git add backend/modulo.py backend/teste_us_xxxx.py
git add backend/ENTREGA_US-XXXX.md backend/CONCLUSAO_US-XXXX.md
git add docs/gestao-agil/backlog.md

# Commit com mensagem padronizada
git commit -m "feat(us-xxxx): Concluir [Titulo da US] - docs + testes + integracao"

# Push (se aprovado)
git push origin feature/sprint-X-nome
```

---

### **FASE 5: Registro de Aprendizados** (15 min)

**Objetivo:** Capturar insights para melhorias futuras

#### 5.1 Identificação de Oportunidades

**Durante desenvolvimento, você identificou:**

- Melhorias fora do escopo?
- Bugs não relacionados?
- Débitos técnicos?
- Novas features valiosas?

**Ação:** Registrar em `docs/gestao-agil/backlog.md` seção "Oportunidades Futuras"

#### 5.2 Lições Aprendidas

**Houve problemas no processo?**

- Bloqueio técnico inesperado?
- Estimativa muito errada?
- Falta de documentação?
- Processo ineficiente?

**Ação:** Registrar em `docs/LICOES_APRENDIDAS.md`

**Template:**

```markdown
### LA-XXX: [Título]

- **Data:** YYYY-MM-DD
- **Contexto:** [Durante US-XXXX]
- **Problema:** [Descrição]
- **Solução Proposta:** [Como melhorar]
- **Status:** Proposta
```

---

## 📊 Métricas de Processo

### Indicadores de Qualidade

- **TTD (Time to Delivery):** Tempo real vs estimado
- **Test Coverage:** % de cobertura de testes
- **Retrabalho:** Features que precisaram correção pós-entrega
- **Bloqueadores:** Tempo perdido em bloqueios

### Metas

- ✅ **TTD Variance:** ±20% da estimativa
- ✅ **Test Coverage:** ≥80%
- ✅ **Retrabalho:** <10%
- ✅ **Bloqueadores:** <15% do tempo total

---

## 🚨 Sinais de Alerta

### Quando o Processo Não Está Sendo Seguido

**Sintomas:**

- [ ] Features "completadas" sem documentação de entrega
- [ ] Commits sem padrão de nomenclatura
- [ ] Testes não executados antes de commit
- [ ] Backlog desatualizado
- [ ] Retrabalho frequente

**Ação Corretiva:**

1. Parar desenvolvimento
2. Revisar este documento
3. Aplicar checklist retroativamente
4. Registrar lição aprendida

---

## 📚 Referências

- **Backlog:** `docs/gestao-agil/backlog.md`
- **Lições Aprendidas:** `docs/LICOES_APRENDIDAS.md`
- **Padrões de Código:** `.github/copilot-instructions.md`
- **Relatórios de Progresso:** `docs/gestao-agil/RELATORIO_PROGRESSO_*.md`

---

## 🔄 Histórico de Revisões

| Versão | Data       | Mudanças                                  | Responsável |
|--------|------------|-------------------------------------------|-------------|
| 1.0    | 2025-11-07 | Criação inicial baseada em LA-011 e LA-014 | Eng. Senior |

---

**Última Atualização:** 2025-11-07 22:30 UTC  
**Status:** ✅ APROVADO (baseado em lições LA-011, LA-012, LA-013, LA-014)  
**Aplicabilidade:** TODAS as US do projeto
