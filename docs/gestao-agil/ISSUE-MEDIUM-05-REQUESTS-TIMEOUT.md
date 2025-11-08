---
title: "ISSUE: Adicionar timeouts em chamadas HTTP de teste"
labels: [security, severity-medium]
---

# Resumo

Arquivo: `backend/teste_api_persistencia.py` (várias linhas)

Evidência: múltiplas chamadas `requests.get`/`requests.post` sem parâmetro `timeout`.

## Risco

- Chamadas sem timeout podem travar testes ou processos, afetando CI e disponibilidade.

## Remediação sugerida

1. Adicionar `timeout=5` (ou valor apropriado) nas chamadas `requests`.
2. Tratar `requests.exceptions.Timeout` explicitamente e falhar o teste com mensagem clara.

## Critérios de aceitação

- Todas as chamadas `requests` em scripts e testes possuem timeout.
- Pipeline CI não fica bloqueado por chamadas pendentes.

## Prioridade

Medium (baixa complexidade, alto ganho operacional)
