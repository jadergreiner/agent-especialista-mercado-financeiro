# Lições Aprendidas - Agent Especialista Mercado Financeiro

## Formato de Registro

```markdown
### LA-[ID]: [Título da Lição]

- **Data:** YYYY-MM-DD
- **Contexto:** [Situação que gerou o aprendizado]
- **Problema:** [Descrição concisa do problema ou desafio]
- **Solução Proposta:** [Ação corretiva ou melhoria sugerida]
- **Impacto:** [Consequências se não for aplicado]
- **Status:** [Proposta | Aprovada | Rejeitada | Implementada]
```

---

## Checklist Obrigatório para Execução de Features (2025-11-08)

- Toda feature deve seguir checklist de execução (LA-011) e calibração de confiança (LA-012) antes de iniciar desenvolvimento.
- Validar status real da feature, progresso, entregas e cobertura de testes.
- Registrar validação no backlog e roadmap.
- Nível de confiança só pode ser elevado após validação dos stakeholders e cobertura de testes >80%.

---

## 📚 Lições Registradas

### LA-011: Validação de Status de Feature Antes de Execução

- **Data:** 2025-11-07
- **Contexto:** Durante processo de execução de feature priorizada (US-PROMPT-003), não foi verificado o status real da feature antes de iniciar refinamento e planejamento
- **Problema:**
  - Feature US-PROMPT-003 já estava 100% implementada, testada e documentada
  - Tempo desperdiçado em simulação de refinamento desnecessário
  - Risco de duplicação de esforço e sobrescrita de código funcional
  - Análise realizada com 95% confiança quando deveria ser 40% (overconfidence crítica)
- **Impacto Observado:**
  - ~30 minutos de trabalho redundante
  - Confusão no backlog com atualizações duplicadas
  - Risco de regressão funcional se execução tivesse prosseguido
- **Solução Proposta:** Implementar checklist obrigatório pré-execução:
  1. **SEMPRE ler relatório de progresso** (`docs/gestao-agil/RELATORIO_PROGRESSO_*.md`)
  2. **SEMPRE verificar arquivos de entrega** (`backend/ENTREGA_*.md`, `backend/CONCLUSAO_*.md`)
  3. **SEMPRE consultar checklist de sprint** antes de assumir status
  4. **SEMPRE sincronizar com time** sobre o que já foi feito
  5. **SEMPRE rodar testes** para confirmar funcionalidade atual
- **Métricas de Validação:**
  - [ ] Arquivo de entrega existe?
  - [ ] Testes estão passando?
  - [ ] Backlog mostra status COMPLETADO?
  - [ ] Relatório de progresso confirma conclusão?
- **Status:** ✅ **IMPLEMENTADA** (checklist criado)
- **Prioridade:** 🔴 CRÍTICA (previne desperdício de recursos)
- **Aplicabilidade:** TODAS as features futuras

---

### LA-012: Calibração Realista de Nível de Confiança

- **Data:** 2025-11-07
- **Contexto:** Análise de feature com nível de confiança 95% sem validação completa dos dados
- **Problema:**
  - Overconfidence baseada em dados incompletos
  - Não foram consultados:
    - Relatórios de progresso (30% dos dados)
    - Documentação de entrega (20% dos dados)
    - Checklists atualizados (10% dos dados)
  - Confiança deveria ser 40%, não 95%
- **Impacto:**
  - Decisões baseadas em análise enviesada
  - Risco de ações incorretas com alta convicção
  - Perda de credibilidade quando erro descoberto
- **Solução Proposta:** Fórmula de calibração de confiança:

  ```text
  Confiança Base = 100%

  Penalizações:
  - Dados incompletos: -30% (relatórios não lidos)
  - Validação insuficiente: -20% (testes não rodados)
  - Contexto desatualizado: -10% (backlog contraditório)
  - Sem sincronização com time: -10%
  - Sem verificação de arquivos de entrega: -10%

  Confiança Final = Base - Σ(Penalizações)
  ```

- **Aplicação:**
  - ✅ Dados completos (100%) = Confiança 90-100%
  - ⚠️ Dados parciais (60-90%) = Confiança 50-70%
  - ❌ Dados incompletos (<60%) = Confiança 20-40%
- **Status:** ✅ **IMPLEMENTADA** (fórmula documentada)
- **Prioridade:** 🔴 CRÍTICA (essencial para tomada de decisão)
- **Aplicabilidade:** TODAS as análises técnicas

---

### LA-013: Aprendizados da Autoavaliação de Análise

- **Data:** 2025-11-07
- **Contexto:** Durante a autoavaliação de análise técnica para o roadmap e backlog, foram identificados gaps e oportunidades de melhoria.
- **Problema:**
  - Gaps não identificados previamente (e.g., Business Case, Onboarding, Riscos).
  - Falta de métricas de sucesso claras para cada fase.
  - Confiança inicial superestimada (90% ao invés de 80%).
- **Impacto:**
  - Planejamento incompleto pode levar a atrasos e retrabalho.
  - Riscos não mapeados podem comprometer entregas futuras.
  - Confiança desalinhada pode gerar decisões enviesadas.
- **Solução Proposta:**
  1. Incorporar validação contínua de gaps no planejamento.
  2. Adicionar seção de riscos como padrão em todos os roadmaps.
  3. Definir KPIs claros para cada sprint e fase.
  4. Ajustar confiança com base em dados completos e validados.
- **Impacto Esperado:**
  - Redução de retrabalho e atrasos.
  - Melhor previsibilidade e alinhamento estratégico.
  - Decisões mais embasadas e confiáveis.
- **Status:** ✅ **IMPLEMENTADA** (roadmap e backlog atualizados)
- **Prioridade:** 🟡 ALTA (aplicável a todos os projetos futuros)
- **Aplicabilidade:** Planejamento de roadmaps e backlogs futuros.

---

### LA-016: Uso de Dados Reais por Stakeholders (Presidente)

- **Data:** 2025-11-08
- **Contexto:** Preparação para o Presidente usar o sistema com dados reais (MVP Cliente/Investidor).
- **Problema:** Risco alto de exposição de PII, ausência de políticas de consentimento documentadas, falta de auditoria e ausência de validação legal pré-deploy.
- **Solução Proposta:** Antes de qualquer exposição de dados reais:
  1. Bloquear deploy em produção até aprovação formal do Presidente, Jurídico e Compliance.
  2. Criar ambiente de staging controlado para testes com dados reais com políticas de mascaramento/anonimização quando aplicável.
  3. Implementar audit trails e retenção definida; registrar aceite/consentimento do presidente.
  4. Executar testes E2E com casos reais e plano de rollback validado.
- **Impacto Esperado:** Minimização de risco legal e reputacional; maior segurança sobre dados sensíveis; confiança calibrada antes do rollout.
- **Status:** ✅ **REGISTRADA** (Backlog e Roadmap atualizados; milestone criado)

---

### LA-014: Implementação de Governança Automatizada e Checks CI

- **Data:** 2025-11-08
- **Contexto:** Após a autoavaliação e atualização do backlog/roadmap, foram implementadas instruções obrigatórias ao Copilot, um arquivo machine-readable de decisões e um workflow CI para verificar conformidade em PRs.
- **Problema:** Falta de mecanismo automático para garantir que decisões estratégicas (ex.: DECISAO-002) sejam referenciadas em mudanças críticas levou a riscos de inconsistência e desvios não autorizados.
- **Solução Proposta:** Implementar políticas obrigatórias no repositório:
  1. `.github/COPILOT_INSTRUCTIONS.md` com regras obrigatórias derivadas das decisões
  2. `docs/governanca/decisoes/decisions.json` com decisões em formato machine-readable
  3. Workflow GitHub Actions (`.github/workflows/check-decisao.yml`) que falha em PRs que alteram áreas sensíveis sem referência a `DECISAO-XXX`
  4. Template de PR com checklist de conformidade e exemplo de PR
  5. Criar processo de exceção formal e comunicar time
- **Impacto Esperado:** Redução de riscos operacionais e alinhamento obrigatório entre decisões e implementações; bloqueio automático de merges não conformes.
- **Status:** ✅ **IMPLEMENTADA** (arquivos e workflow criados)
- **Prioridade:** 🔴 CRÍTICA (governança deve preceder mudanças sensíveis)
- **Aplicabilidade:** Todas as equipes que atuam em áreas sensíveis (backend, infra, IA, docs de governança)

### LA-015: Processo de Sincronização Pré-Execução

- **Data:** 2025-11-07
- **Contexto:** Execução de feature sem sincronização prévia com estado real do projeto
- **Problema:** Falta de processo formal de sincronização antes de iniciar trabalho
- **Solução Proposta:** Ritual de Sincronização (5-10 minutos):

**FASE 1: Contexto Geral (2 min)**

```bash
# 1. Ver branch atual e últimos commits
git branch --show-current
git log --oneline -5

# 2. Ver status do working tree
git status
```

**FASE 2: Status do Sprint (3 min)**

```bash
# 3. Ler relatório de progresso
cat docs/gestao-agil/RELATORIO_PROGRESSO_DAY*.md | grep "US-PROMPT"

# 4. Verificar features completadas hoje
ls -lt backend/ENTREGA_*.md | head -5
ls -lt backend/CONCLUSAO_*.md | head -5
```

**FASE 3: Próxima Feature (5 min)**

```bash
# 5. Identificar próxima pendente no backlog
grep -A 5 "PENDENTE" docs/gestao-agil/backlog.md | head -20

# 6. Verificar dependências satisfeitas
grep -B 2 "Dependências:" docs/gestao-agil/backlog.md

# 7. Confirmar que não existe entrega
ls backend/ENTREGA_US-PROMPT-004.md 2>/dev/null || echo "Feature pendente confirmada"
```

- **Benefícios:**
  - Evita duplicação de esforço
  - Identifica bloqueadores cedo

  ```bash
  git branch --show-current
  git log --oneline -5

  git status

  **FASE 2: Status do Sprint (3 min)**

  ```bash
  # 3. Ler relatório de progresso
  cat docs/gestao-agil/RELATORIO_PROGRESSO_DAY*.md | grep "US-PROMPT"

  # 4. Verificar features completadas hoje
  ls -lt backend/ENTREGA_*.md | head -5
  ls -lt backend/CONCLUSAO_*.md | head -5
  ```

  **FASE 3: Próxima Feature (5 min)**

  ```bash
  # 5. Identificar próxima pendente no backlog
  grep -A 5 "PENDENTE" docs/gestao-agil/backlog.md | head -20

  # 6. Verificar dependências satisfeitas
  grep -B 2 "Dependências:" docs/gestao-agil/backlog.md

  # 7. Confirmar que não existe entrega
  ls backend/ENTREGA_US-PROMPT-004.md 2>/dev/null || echo "Feature pendente confirmada"
  ```

- **Benefícios:**
  - Evita duplicação de esforço
  - Identifica bloqueadores cedo
  - Confirma trabalho realmente necessário
  - Reduz risco de regressão
- **Status:** 🔄 **PROPOSTA** (aguardando aprovação)
- **Prioridade:** 🟡 ALTA
- **Custo:** 5-10 min por feature
- **ROI:** Previne 30+ min de retrabalho

---

### LA-015: Validação de Contexto Multi-Projeto em Documentação

- **Data:** 2025-11-07
- **Contexto:** Criação de ESTRUTURA_ORGANIZACIONAL.md sem verificar governança de projetos relacionados (Hub Financeiro Inteligente)
- **Problema:**
  - Documento criado sem consultar ATA_DIRETORIA_EXECUTIVA.md do Hub
  - Estrutura organizacional incompleta (omitiu cargo de Presidente)
  - Relação hierárquica entre projetos não documentada
  - Confiança superestimada (90% quando deveria ser 60%)
- **Impacto Observado:**
  - Documento oficial incompleto desde criação
  - Confusão sobre autoridade final (Presidente vs PO)
  - Risco de decisões desalinhadas entre projetos
  - Necessidade de correção imediata (2 commits no mesmo dia)
- **Solução Proposta:** Checklist adicional para documentação organizacional:

  ```bash
  # 1. Identificar projetos relacionados
  ls -d c:\repo\projetos\*

  # 2. Buscar documentos de governança em TODOS os projetos
  grep -r "Presidente\|Diretoria\|Governança\|ATA" */docs/**/*.md

  # 3. Verificar se há estrutura formal superior
  find . -name "*ATA*" -o -name "*DIRETORIA*" -o -name "*GOVERNANCA*"

  # 4. Validar alinhamento hierárquico
  # - Este projeto é independente ou módulo de outro?
  # - Quem tem autoridade final de decisão?
  # - Há reportes cruzados entre estruturas?
  ```

- **Penalidades Aplicadas à Confiança:**
  - Dados incompletos (Hub não consultado): -20%
  - Validação insuficiente (não busquei Presidente/ATA): -10%
  - Contexto multi-projeto ignorado: -10%
  - **Confiança Real:** 60% (não 90%)
- **Novos Riscos Identificados:**
  - **Risco 3:** Falta de alinhamento de governança entre projetos (MÉDIO)
  - **Risco 4:** Ausência de Presidente documentado (BAIXO - mitigado)
- **Status:** ✅ **IMPLEMENTADA** (documento corrigido v1.1)
- **Prioridade:** 🟡 ALTA (previne desalinhamento estratégico)
- **Aplicabilidade:** Documentação de estrutura/governança

---

### LA-016: Validação de Código Existente Antes de Propor Novas Features

- **Data:** 2025-11-07
- **Contexto:** Simulação de reunião estratégica propôs US-DASH-001 (Dashboard Streamlit) sem verificar código existente
- **Problema:**
  - Dashboard Streamlit já existe (`backend/app_dashboard.py`, 236 linhas)
  - Proposta de criar algo já implementado
  - Geraria retrabalho e confusão se executado
  - Simulação sem disclaimer de que era exercício, não decisão real
- **Impacto Observado:**
  - Risco de duplicação de código
  - Perda de credibilidade (propor o que já existe)
  - Tempo desperdiçado implementando funcionalidade existente
  - Confusão sobre o que é real vs simulado
- **Solução Proposta:** Checklist obrigatório antes de propor novas features:

  ```bash
  # 1. Buscar funcionalidade similar no código
  grep -r "dashboard\|streamlit\|flask" backend/

  # 2. Listar arquivos relevantes
  ls -la backend/*dashboard* backend/*web*

  # 3. Verificar se há ADR sobre decisão de stack
  ls docs/03-REFERENCIAS/ADRs/ 2>/dev/null

  # 4. Consultar backlog para features similares
  grep -i "dashboard\|frontend\|gui" docs/gestao-agil/backlog.md

  # 5. Ler README do módulo
  cat backend/README.md 2>/dev/null
  ```

- **Penalidades à Confiança:**
  - Código não validado: -20%
  - Features duplicadas propostas: -15%
  - Simulação sem disclaimer: -10%
- **Disclaimer Obrigatório para Simulações:**

  ```markdown
  ⚠️ SIMULAÇÃO: Esta reunião é um EXERCÍCIO de estruturação de pensamento.
  Todas as decisões são PROPOSTAS e requerem aprovação formal de:
  - Presidente (decisões estratégicas)
  - PO (priorização)
  - Tech Lead (viabilidade técnica)
  - CTO (arquitetura)
  ```

- **Status:** ✅ **IMPLEMENTADA** (checklist documentado)
- **Prioridade:** � CRÍTICA (previne duplicação e confusão)
- **Aplicabilidade:** Todas as propostas de novas features

---

### LA-017: Organização de Módulos por Persona e Valor (Não por Camada Técnica)

- **Data:** 2025-11-07
- **Contexto:** Discussão sobre estrutura de módulos do sistema focou inicialmente em camadas técnicas (frontend/backend/dados)
- **Problema:**
  - Organização técnica dificulta priorização de valor
  - Backlog estruturado por camada horizontal (ex: "todo frontend", "todo backend")
  - Cliente não vê valor até integração completa (múltiplos sprints)
  - Difícil comunicar roadmap para stakeholders não-técnicos
- **Solução Proposta:** Estrutura modular por **PERSONA** e **VALOR ENTREGUE**:

  ```text
  VISÃO CLIENTE (Investidor):
  ├── Meu Home (dashboard consolidado)
  ├── Forex (28 pares tempo real)
  ├── Dividendos (renda variável BR)
  ├── Criptomoedas (spot)
  ├── Cripto Futuros (derivativos)
  └── Renda Fixa (tesouro/CDB)

  VISÃO ADMINISTRADOR (Gestão):
  ├── Gestão Clientes
  ├── Gestão Licenças
  └── Gestão Financeira

  VISÃO DESENVOLVEDOR (Infra):
  ├── Motores de Cálculo
  ├── Gestor de Regras
  ├── Dashboard Padrão (template)
  └── Relatório Padrão (scheduler)
  ```

- **Benefícios:**
  - **Priorização clara:** "Forex P0, Dividendos P1" (linguagem de negócio)
  - **Entrega vertical:** Cada módulo = frontend + backend + dados + docs + testes
  - **Comunicação eficaz:** Stakeholder entende "Módulo Forex Sprint 2"
  - **Roadmap visual:** Mermaid com 3 cores (Cliente/Admin/Dev)
- **Metodologia de Entrega:**

  ```text
  US-CLIENTE-001: [Forex] Cotações Tempo Real
  ├── Frontend: Lista 28 pares + WebSocket
  ├── Backend: API + streaming + cache Redis
  ├── Dados: Tabela + histórico + índices
  ├── Docs: Tutorial + API docs + troubleshooting
  ├── Testes: E2E + unit + integration + performance
  └── Produção: Deploy + feature flag + monitoring

  = Cliente USA em produção ao final do sprint!
  ```

- **Comparação com Abordagem Horizontal (Errada):**
  - ❌ Sprint 1: Todo frontend Forex (sem backend = não funciona)
  - ❌ Sprint 2: Todo backend Forex (sem integração)
  - ❌ Sprint 3: Banco de dados
  - ❌ Sprint 4-5: Integração e bugs
  - ❌ Sprint 6: Cliente finalmente vê valor (6 sprints!)
  - ✅ vs 1 sprint na abordagem vertical
- **Status:** ✅ **IMPLEMENTADA** (proposta documentada)
- **Prioridade:** 🟡 ALTA (impacta toda estrutura de backlog)
- **Aplicabilidade:** Organização de backlog, roadmap, comunicação com stakeholders

---

## �📊 Resumo Executivo

### Lições por Criticidade

- 🔴 **CRÍTICA:** 3 lições (LA-011, LA-012, LA-016)
- 🟡 **ALTA:** 3 lições (LA-013, LA-014, LA-015)

### Status de Implementação

- ✅ **IMPLEMENTADAS:** 5 (LA-011, LA-012, LA-013, LA-015, LA-016)
- 🔄 **PROPOSTAS:** 1 (LA-014)

### Impacto Esperado

- **Redução de retrabalho:** 80-90%
- **Melhoria de confiança:** +50-60 pontos (40%→90%)
- **Economia de tempo:** 30+ min por feature
- **Redução de risco:** Eliminação de duplicação e regressão
- **Alinhamento estratégico:** Documentação multi-projeto consistente
- **Prevenção duplicação código:** Validação obrigatória de features existentes

---

## 🎯 Próximos Passos

1. ✅ Aplicar LA-011 (checklist) na próxima feature
2. ✅ Usar LA-012 (calibração) em todas as análises
3. ✅ Seguir LA-013 (sinais) para detectar trabalho completo
4. 🔄 Aprovar LA-014 (sincronização) como processo padrão
5. ✅ Aplicar LA-015 (multi-projeto) em docs organizacionais
6. ✅ Aplicar LA-016 (validar código) antes de propor features

---

**Última Atualização:** 2025-11-07 23:45 UTC
**Responsável:** Engenheiro Senior (Autoavaliação)
**Aprovação PO:** Pendente para LA-014

---

### LA-017: Organização de Módulos por Persona e Valor (Não por Camada Técnica)

- **Data:** 2025-11-07
- **Contexto:** Discussão sobre estrutura de módulos do sistema focou inicialmente em camadas técnicas (frontend/backend/dados)
- **Problema:**
  - Organização técnica dificulta priorização de valor
  - Backlog estruturado por camada horizontal (ex: "todo frontend", "todo backend")
  - Cliente não vê valor até integração completa (múltiplos sprints)
  - Difícil comunicar roadmap para stakeholders não-técnicos
- **Solução Proposta:** Estrutura modular por **PERSONA** e **VALOR ENTREGUE**:

  ```text
  VISÃO CLIENTE (Investidor):
  ├── Meu Home (dashboard consolidado)
  ├── Forex (28 pares tempo real)
  ├── Dividendos (renda variável BR)
  ├── Criptomoedas (spot)
  ├── Cripto Futuros (derivativos)
  └── Renda Fixa (tesouro/CDB)

  VISÃO ADMINISTRADOR (Gestão):
  ├── Gestão Clientes
  ├── Gestão Licenças
  └── Gestão Financeira

  VISÃO DESENVOLVEDOR (Infra):
  ├── Motores de Cálculo
  ├── Gestor de Regras
  ├── Dashboard Padrão (template)
  └── Relatório Padrão (scheduler)
  ```

- **Benefícios:**
  - **Priorização clara:** "Forex P0, Dividendos P1" (linguagem de negócio)
  - **Entrega vertical:** Cada módulo = frontend + backend + dados + docs + testes
  - **Comunicação eficaz:** Stakeholder entende "Módulo Forex Sprint 2"
  - **Roadmap visual:** Mermaid com 3 cores (Cliente/Admin/Dev)
- **Metodologia de Entrega:**

  ```text
  US-CLIENTE-001: [Forex] Cotações Tempo Real
  ├── Frontend: Lista 28 pares + WebSocket
  ├── Backend: API + streaming + cache Redis
  ├── Dados: Tabela + histórico + índices
  ├── Docs: Tutorial + API docs + troubleshooting
  ├── Testes: E2E + unit + integration + performance
  └── Produção: Deploy + feature flag + monitoring

  = Cliente USA em produção ao final do sprint!
  ```

- **Comparação com Abordagem Horizontal (Errada):**
  - ❌ Sprint 1: Todo frontend Forex (sem backend = não funciona)
  - ❌ Sprint 2: Todo backend Forex (sem integração)
  - ❌ Sprint 3: Banco de dados
  - ❌ Sprint 4-5: Integração e bugs
  - ❌ Sprint 6: Cliente finalmente vê valor (6 sprints!)
  - ✅ vs 1 sprint na abordagem vertical
- **Status:** ✅ **IMPLEMENTADA** (proposta documentada)
- **Prioridade:** 🟡 ALTA (impacta toda estrutura de backlog)
- **Aplicabilidade:** Organização de backlog, roadmap, comunicação com stakeholders

---

## 📊 Resumo Executivo (Atualizado)

### Lições por Criticidade

- 🔴 **CRÍTICA:** 3 lições (LA-011, LA-012, LA-016)
- 🟡 **ALTA:** 4 lições (LA-013, LA-014, LA-015, LA-017)

### Status de Implementação

- ✅ **IMPLEMENTADAS:** 6 (LA-011, LA-012, LA-013, LA-015, LA-016, LA-017)
- 🔄 **PROPOSTAS:** 1 (LA-014)

### Impacto Esperado

- **Redução de retrabalho:** 80-90%
- **Melhoria de confiança:** +50-60 pontos (40%→90%)
- **Economia de tempo:** 30+ min por feature
- **Redução de risco:** Eliminação de duplicação e regressão
- **Alinhamento estratégico:** Documentação multi-projeto consistente
- **Prevenção duplicação código:** Validação obrigatória de features existentes
- **Clareza de valor:** Backlog orientado a persona (não camada técnica)

---

## 🎯 Próximos Passos (Atualizado)

1. ✅ Aplicar LA-011 (checklist) na próxima feature
2. ✅ Usar LA-012 (calibração) em todas as análises
3. ✅ Seguir LA-013 (sinais) para detectar trabalho completo
4. 🔄 Aprovar LA-014 (sincronização) como processo padrão
5. ✅ Aplicar LA-015 (multi-projeto) em docs organizacionais
6. ✅ Aplicar LA-016 (validar código) antes de propor features
7. ✅ Aplicar LA-017 (módulos por persona) em organização de backlog

---

**Última Atualização:** 2025-11-07 23:55 UTC
**Responsável:** Engenheiro Senior (Autoavaliação + Ajustes)
**Aprovação PO:** Pendente para LA-014

---

### LA-020: Autoavaliação e Correção de Gaps Operacionais

- **Data:** 2025-11-08
- **Contexto:** Realizada autoavaliação da análise dos documentos mestres (ROADMAP, BACKLOG, PROPOSTA) que identificou lacunas operacionais e de evidência, em especial ausência de Test Plan formal e métricas automáticas de governança.
- **Problema:**
  - Falta de um Test Plan e critérios de aceitação formal para fluxos que expõem dados reais (Presidente).
  - Métricas automáticas de adoção de governança (PRs que referenciam decisões, uso de template) não estavam sendo coletadas.
  - Falta de gate explícito no roadmap para requerer aprovação de testes e evidenciação antes do rollout.
- **Solução Proposta:**
  1. Inserir gate "Test Plan & Acceptance Criteria" no Roadmap (bloqueador antes de rollout em staging com dados reais).
  2. Adicionar tarefa no Backlog para definir Critérios de Aceitação e Test Plan (E2E + rollback) e criar issue AG-008.
  3. Implementar scripts de coleta de métricas de governança e expor em dashboard (FEAT-005 / LA-018).
  4. Registrar a aprovação formal (ata / assinatura eletrônica) no backlog e vincular ao milestone.
- **Impacto Esperado:** Redução de risco legal e operacional, evidência objetiva para liberar exposição de dados reais, maior confiança nas decisões.
- **Status:** ✅ REGISTRADA e aplicada no Roadmap/Backlog (gate criado; tarefa de critérios/test plan adicionada)
- **Prioridade:** 🔴 CRÍTICA


### LA-018: Métricas de Adoção de Governança e Feedback

- **Data:** 2025-11-08
- **Contexto:** Após implementação inicial das políticas de governança e do workflow CI, foi identificado que falta monitoramento contínuo para avaliar adoção e efetividade.
- **Problema:**
  - Sem métricas automáticas, não há visibilidade sobre adoção ou regressões relacionadas a compliance.
  - Treinamentos podem ocorrer, mas sem dados de participação e impacto.
- **Solução Proposta:**
  1. Implementar scripts que coletem semanalmente:
     - Percentual de PRs que citam decisões (e.g., DECISAO-002)
     - Percentual de PRs que utilizam o template padrão
     - Contagem e categoria de exceções abertas
     - Tempo médio de aprovação de exceções
     - Taxa de participação em sessões de treinamento
  2. Expor as métricas em dashboard (Metabase/Grafana) com relatórios semanais e alertas para queda de adesão.
  3. Revisão semanal no ritual do Tech Lead com ações corretivas registradas no backlog (DT-014).
- **Impacto Esperado:** Visibilidade operacional, correção rápida de gaps e prova de eficiência do treinamento.
- **Status:** 🔄 PROPOSTA (scripts iniciais em desenvolvimento)
- **Prioridade:** 🔴 CRÍTICA
- **Responsável:** Engenheiro Senior + DevOps

---

### LA-019: Autoavaliação Sistemática de Análises Técnicas

- **Data:** 2025-11-08
- **Contexto:** Após autoavaliação da análise de docs mestres (roadmap, backlog, proposta estratégica, lições aprendidas), identificados gaps em completude e calibração de confiança.
- **Problema:**
  - Gaps em dados quantitativos (métricas de PRs, feedback do time) não considerados, levando a confiança superestimada.
  - Riscos adicionais não mapeados (dependência de aprovações, conflitos entre velocidade e governança, escopo creep).
  - Análise macro consistente, mas confiança ajustada de 80% para 70% devido à falta de validação prática.
- **Solução Proposta:**
  - Implementar checklist obrigatório de autoavaliação para TODAS as análises: completude (dados considerados?), consistência (alinhamento macro-técnico?), riscos omitidos (lista adicional), confiança calibrada (ajuste baseado em qualidade de dados).
  - Adicionar seção de métricas quantitativas no backlog para rastrear adoção prática.
  - Estruturar oportunidade nova: FEAT-005 - Dashboard de Métricas de Governança (vertical slice para visualizar PRs, templates, treinamentos).
- **Impacto:** Previne decisões enviesadas, reduz riscos não mapeados, aumenta precisão de confiança.
- **Status:** ✅ **IMPLEMENTADA** (lição registrada; checklist proposto)
- **Prioridade:** 🔴 CRÍTICA (essencial para qualidade de decisões)
- **Aplicabilidade:** TODAS as análises futuras

---

### Referência Explícita a Propostas Estratégicas

- **Aprendizado:** Propostas estratégicas, como a de 2025-11-07, devem ser explicitamente referenciadas nos artefatos atualizados para garantir rastreabilidade e alinhamento.
- **Ação:** Incorporar referências diretas em Backlog, Roadmap e outros documentos relevantes.

---
