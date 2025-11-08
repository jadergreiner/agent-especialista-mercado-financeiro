# Checklist de Revisão — PR #2

Resumo rápido: este PR adiciona quickfixes de segurança, um Gate CI mínimo (DECISAO-002) e testes unitários focados.

Checklist para revisores:

- [ ] Verificar que o PR body referencia `DECISAO-002` (obrigatório para alterações em `backend/`, `modules/`, `docs/governanca/`).
- [ ] Revisar mudanças em `backend/main.py` para garantir que `ENABLE_DEMO_AUDIT` permanece apenas em ambientes demo.
- [ ] Confirmar que `backend/utils/masking.py` é apenas para demonstração e não vaza dados reais em logs.
- [ ] Revisar `.github/workflows/pr_gates.yml` para confirmar o comportamento esperado do gate (Bandit + testes rápidos).
- [ ] Confirmar que os testes adicionados (`test_masking`, `test_audit_middleware`) cobrem os cenários mínimos e são rápidos.
- [ ] Verificar links para as issues relacionadas (#6–#10) e atribuir owners conforme necessário.
- [ ] Aprovar ou solicitar exceção documentada caso seja necessário manter `FRONTEND-FIRST` sem remediação completa.

Changelog curto:

- `backend/teste_api_persistencia.py` — adicionar `timeout=10` em chamadas HTTP de teste.
- `backend/main.py` — bind alterado para `127.0.0.1` em execução local (reduzir exposição).
- `backend/utils/masking.py` — utilitário demo para mascaramento de PII.
- `backend/middleware/audit.py` — middleware ASGI demo que grava `.logs/audit.log`.
- `.github/workflows/pr_gates.yml` — novo workflow de gate PR (DECISAO-002 + Bandit + testes rápidos).
- `backend/tests/*` — dois testes unitários adicionados (masking + audit).

Origin: feature/AG-rbac-audit-masking
