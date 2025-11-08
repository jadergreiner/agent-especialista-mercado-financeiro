# Origin: DT-013 - Processo de Excecao de Decisoes de Governanca

Status: rascunho

## Objetivo

Este documento descreve o processo formal para solicitar, avaliar e aprovar exceções às decisões de governança registradas em `docs/governanca/decisoes/decisions.json` (ex.: DECISAO-002). O objetivo é permitir flexibilidade controlada quando há justificativa técnica/operacional válida.

## Quando usar

- Mudancas que toquem caminhos sensiveis (ex.: `.github/`, `docs/governanca/`, `docs/gestao-agil/`) e para as quais o autor da PR nao consegue referenciar a decisao aplicavel.

- Situacoes de emergencia operacional que exigem alteracao temporaria de um workflow.

## Como solicitar uma excecao

1. Abra uma PR normalmente que contenha a mudanca requerida.
2. No corpo da PR inclua a secao "Excecao Solicitada" usando o template abaixo.
3. Marque o(s) revisor(es) responsaveis pelo dominio (ex.: owner do workflow, responsavel de governanca).

### Template minimo para solicitacao de excecao (colocar no corpo da PR)


---

#### Excecao Solicitada

- Decisao relacionada: (ex.: DECISAO-002) ou `N/A` quando nao aplicavel
- Motivo (resumo): Descrever em 1-3 linhas por que a excecao e necessaria
- Impacto e mitigacao: Riscos, duracao esperada da excecao, e plano de mitigacao
- Dono da excecao (quem aprova): @usuario-responsavel
- Prazo de revisao: 48 horas (padrao) ou justificar urgencia

## Avaliacao e aprovacao

- A solicitacao de excecao sera avaliada por ao menos 1 responsavel tecnico e 1 responsavel de governanca.
- Aprovacao deve ser registrada como comentario na PR e tambem como uma entrada em `docs/governanca/excecoes_registro.md` (manual).
- Excecoes temporarias deverao incluir um plano de reversao e uma data de expiracao obrigatoria.

## Registro

- Todas as excecoes aprovadas devem ser registradas em `docs/governanca/excecoes_registro.md` com: ID da PR, solicitante, decisao referenciada (se houver), duracao e revisor(es).

## SLA e auditoria

- Revisoes padrao: 48 horas.
- Excecoes nao revertidas no prazo serao escaladas ao comite de governanca.

## Notas finais

- Este documento e parte da politica de governanca do repositorio e deve ser citado nas PRs que requerem excecao.
