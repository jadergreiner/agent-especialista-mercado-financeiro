# Origin: DECISAO-002
# Instruções Obrigatórias do Repositório para Assistentes (Copilot)

**Data de vigência:** 2025-11-07
**Referências principais:** DECISAO-002, docs/gestao-agil/ROADMAP_DEBITO_TECNICO.md, docs/governanca/decisoes/*

> Estas instruções são OBRIGATÓRIAS para qualquer assistente automatizado (Copilot) que gere código, patches, PRs ou sugestões dentro deste repositório. Qualquer exceção deve ser explicitamente aprovada por um membro do comitê (PO/CTO/Financeiro) e documentada em um PR com a tag `EXCECAO-DECISAO`.

## Regras Obrigatórias (Precedência)

1. Em caso de conflito entre um pedido do usuário e uma decisão registrada em `docs/governanca/decisoes/`, a **DECISAO** prevalece. Se não for possível aplicar automaticamente, o assistente deve solicitar clarificação e NÃO executar mudanças que contrariem a decisão.

2. TODO patch, PR ou resposta que altere arquitetura, infra, modelos de IA, políticas de governança, custos ou decisões estratégicas deve mencionar explicitamente o(s) ID(s) da(s) decisão(ões) aplicadas (ex.: `DECISAO-002`) no cabeçalho do patch ou no corpo do PR.

   - Formato recomendado no topo de um patch/arquivo: `# Origin: DECISAO-002`

3. Idioma: TODOS os artefatos relacionados a decisões (código que altera comportamento, documentação, mensagens de commit relacionadas a decisões) devem estar em **Português**.

4. Segurança: Nunca exfiltrar segredos; use variáveis de ambiente para chaves e documente permissões necessárias em `docs/seguranca.md`.

5. Observability & Tests: Qualquer mudança que afete execução em produção deve incluir um plano mínimo de testes (unitários + integração) e métricas para monitoramento (Prometheus/Grafana) — documentar métricas e SLOs no PR.

6. Modelos IA: Se o assistente for solicitado a escolher ou recomendar um modelo IA, seguir a `DECISAO-002` (usar GitHub Copilot Business e os modelos aprovados) e os critérios de fallback documentados no diretório de decisões.

7. Em caso de incerteza técnica que possa afetar a arquitetura ou custos, o assistente deve gerar uma "Nota de Exceção" no PR com contexto, riscos, mitigação proposta e responsável técnico.

## Requisitos de PR / Merge

- Todos os PRs que tocam em caminhos sensíveis (ex.: `docs/governanca`, `docs/gestao-agil`, `backend/`, `models/`, `infra/`, `scripts/`) devem incluir no corpo do PR:
  - Referência a decisão(s) aplicável(is) (ex.: `DECISAO-002`)
  - Checklist de conformidade (checkboxes) com itens mínimos:
    - [ ] Referência a DECISAO(s) incluída
    - [ ] Plano de testes mínimo adicionado
    - [ ] Métricas/SLOs documentados (se aplicável)
    - [ ] Nota de Exceção (se houver desvios)

- Falha em cumprir estes requisitos deve bloquear a aprovação/merge até correção.

## Processo de Exceção

- Exceções só podem ser aprovadas pelo comitê: PO + CTO + Diretor Financeiro (registro de aprovação deve estar no PR como comentário estruturado).
- Registrar qualquer exceção em `docs/governanca/excecoes.md` com UID e link para o PR.

## Automação Recomendadas (implementadas por CI)

- Job que verifica a presença de `DECISAO-` em PRs que alteram caminhos sensíveis.
- Linter para garantir que arquivos de documentação e commits relacionados a decisões estejam em Português.
- Bot que anexe checklist automático ao PR quando detecta mudanças em áreas sensíveis.

## Responsabilidades

- Tech Lead: monitorar conformidade técnica e executar POCs exigidos por decisões.
- PO: validar impactos de produto e prioridades.
- Diretor Financeiro: validar custos orçamentários antes de execuções que impliquem despesas.

## Notas Finais

- Estas instruções têm prioridade sobre instruções ad-hoc de assistentes. Elas foram aprovadas e derivam da `DECISAO-002` e das atas/roadmaps associados.
- Para alterações nesta política, abrir PR contra `docs/governanca/` e obter aprovação do comitê.

---

*Arquivo gerado automaticamente por solicitação de governança em 2025-11-07.*
