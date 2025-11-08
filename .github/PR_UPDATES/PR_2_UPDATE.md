# Atualização do PR: Quickfixes de segurança e Gate CI

Este PR atualiza a branch `feature/AG-rbac-audit-masking` com correções rápidas e infra de governança solicitada.

## Mudanças principais

1. Segurança / Quickfixes
   - Adicionado `timeout=10` em chamadas HTTP de teste para mitigar B113 (requests sem timeout).
   - Alterado bind uvicorn de `0.0.0.0` para `127.0.0.1` para reduzir exposição (B104).

2. Governança / CI Gate
   - Adicionado workflow `.github/workflows/pr_gates.yml` que:
     - Verifica se PRs que alteram áreas sensíveis (`backend/`, `modules/`, `docs/governanca/`) referenciam `DECISAO-002` no corpo do PR.
     - Executa Bandit no diretório `backend/` e falha o job se houver findings MEDIUM ou HIGH.
     - Executa testes unitários focados (masking + audit) para garantir comportamentos básicos.
   - Script auxiliar `.github/scripts/check_bandit.py` para analisar saída do Bandit.

3. Masking / Audit (demo)
   - `backend/utils/masking.py`: utilitário mínimo de mascaramento de PII (demo).
   - `backend/middleware/audit.py`: middleware ASGI demo que grava eventos mínimos em `.logs/audit.log`.
   - Integração condicional no `backend/main.py` (ativável via `ENABLE_DEMO_AUDIT` env var).

4. Testes adicionados
   - `backend/tests/test_masking.py` — teste unitário para `mask_dict` (caso simples e aninhado).
   - `backend/tests/test_audit_middleware.py` — testa que `AuditMiddleware` escreve evento JSON no logfile.

5. Documentação
   - `docs/gestao-agil/PLANO_GATE_CI.md` — instruções do gate CI e fluxo de exceção.

## Issues relacionadas
- #6 Remediar desserialização insegura com pickle
- #7 Substituir uso dinâmico de exec por importlib
- #8 Parametrizar queries SQL para evitar injeção
- #9 Evitar bind 0.0.0.0 em ambiente com reload=True
- #10 Adicionar timeouts em chamadas HTTP de teste

## Testes locais
- Executei localmente apenas os dois testes adicionados (para evitar dependências pesadas):

  ```bash
  pytest -q backend/tests/test_masking.py backend/tests/test_audit_middleware.py
  ```

  Resultado: ambos os testes passaram localmente.

## Notas e próximos passos sugeridos
- CI já foi atualizado para executar Bandit e os dois testes rápidos no PR gate.
- Recomendo que PR seja revisado com foco em:
  - Verificar se a alteração do host (`127.0.0.1`) é aceitável para dev/demo.
  - Revisar política de masking (é uma implementação demo, não para produção).
- Para produção: substituir audit demo por solução de logs centralizada e garantir políticas de retenção/segurança.

Origin: feature/AG-rbac-audit-masking
