
# Origin: DT-013 - Plano de Treinamento e Comunicacao sobre Governanca

Status: rascunho

## Objetivo

Comunicar a equipe sobre as novas regras de governanca (DECISAO-002 e artefatos correlatos) e executar um treinamento pratico sobre: PR template, excecoes, e como responder ao workflow de checagem.

## Publico-alvo

- Desenvolvedores
- Revisores de PR
- Time de DevOps / CI
- Product Owner / Donos de decisoes

## Agenda sugerida (90 minutos)

1. 15 min - Motivacao e panorama (por que as decisoes sao mandatorias)
2. 20 min - Arquitetura das regras (decisions.json, COPILOT_INSTRUCTIONS.md, workflow)
3. 20 min - Demonstracao pratica: criar PR que passa e PR que falha (simulacao local)
4. 20 min - Como solicitar excecoes e usar o template de excecao
5. 15 min - Q&A e proximos passos

## Materiais

- `docs/governanca/EXEMPLO_PR_DEMO.md` (exemplo de PR correto)
- `docs/governanca/excecoes.md` (processo de excecoes)
- Script de simulacao local: `scripts/simulate_pr_check.ps1`

## Checklist antes da sessao

- Verificar que os participantes tem acesso ao repositorio
- Enviar pre-leitura com `EXEMPLO_PR_DEMO.md`
- Preparar duas PRs de demonstracao (uma com referencia a DECISAO-002, outra sem)

## Comunicacao

- Criar uma Issue no repositorio `docs/gestao-agil/` anunciando a mudanca e linkando os materiais.
- Enviar e-mail/Slack com resumo e data do treinamento.

## Metricas de sucesso

- Percentual de PRs que tocam caminhos sensiveis que incluem referencia a `DECISAO-` no corpo (alvo inicial: 95%).
- Tempo medio de aprovacao de excecoes (alvo: < 48 horas).
