# Relatório Bandit - Medium/Low (triagem)

*Gerado a partir de* `.reports/bandit_full.json`

## Resumo Geral

- Arquivos com erro de parsing: 0

## Totais (do relatório)

- Total findings MEDIUM: 20
- Total findings LOW: 173
- Totais agregados (metrics._totals): SEVERITY.HIGH=1, SEVERITY.MEDIUM=20, SEVERITY.LOW=173

## Principais tipos (top 10 tests)

- B101: 82
- B311: 35
- B110: 30
- B112: 9
- B113: 9
- B404: 8
- B608: 7
- B603: 6
- B403: 2
- B102: 2

## Findings MEDIUM (resumo)

- `.\backend\teste_api_persistencia.py` — 8 findings MEDIUM
  - L22 | B113 | Call to requests without timeout
  - L31 | B113 | Call to requests without timeout
  - L86 | B113 | Call to requests without timeout
  - L101 | B113 | Call to requests without timeout
  - L115 | B113 | Call to requests without timeout
  - ...(+3 mais)
- `.\backend\framework_assimetrico\__init__.py` — 2 findings MEDIUM
  - L155 | B102 | Use of exec detected.
  - L156 | B102 | Use of exec detected.
- `.\backend\sistema_alertas_avancado.py` — 2 findings MEDIUM
  - L686 | B608 | Possible SQL injection vector through string-based query construction.
  - L704 | B608 | Possible SQL injection vector through string-based query construction.
- `.\scripts\mask_sqlite.py` — 2 findings MEDIUM
  - L44 | B608 | Possible SQL injection vector through string-based query construction.
  - L58 | B608 | Possible SQL injection vector through string-based query construction.
- `.\backend\app_dashboard.py` — 1 findings MEDIUM
  - L38 | B608 | Possible SQL injection vector through string-based query construction.
- `.\backend\carregador_dados_historicos.py` — 1 findings MEDIUM
  - L608 | B301 | Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- `.\backend\dashboard_web.py` — 1 findings MEDIUM
  - L275 | B608 | Possible SQL injection vector through string-based query construction.
- `.\backend\main.py` — 1 findings MEDIUM
  - L45 | B104 | Possible binding to all interfaces.
- `.\backend\otimizacao_persistencia.py` — 1 findings MEDIUM
  - L344 | B608 | Possible SQL injection vector through string-based query construction.
- `.\scripts\collect_metrics\github_metrics.py` — 1 findings MEDIUM
  - L40 | B113 | Call to requests without timeout

## Findings LOW (resumo)

- Total LOW: 173

---
> Nota: arquivos substituídos por stubs temporários para permitir parsing completo. Ver branch `feature/AG-rbac-audit-masking`.