---
title: "Plano: Gate CI - Segurança e DECISAO-002"
---

# Gate CI proposto

Resumo rápido das regras implementadas:

- PRs que modificam áreas sensíveis (`backend/`, `modules/`, `docs/governanca/`) devem referenciar `DECISAO-002` no corpo do PR. O workflow `pr_gates.yml` falhará caso não haja referência.
- Bandit é executado no diretório `backend/`. Se houver findings com severidade MEDIUM ou HIGH, o job falhará e bloqueará a PR.

Como solicitar exceção:

1. Abrir issue do tipo `governance-exception` e referenciar a PR.
2. Owner (Tech Lead) aprova a exceção no issue com motivo e tempo de validade.

Origin: feature/AG-rbac-audit-masking
