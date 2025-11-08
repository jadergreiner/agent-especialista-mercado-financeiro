 # Coletor de Métricas - scripts/collect_metrics

Este diretório contém scripts iniciais para coletar métricas de governança a partir do GitHub.

Pré-requisitos
- Python 3.9+
- Variável de ambiente `GITHUB_TOKEN` com um token que tenha permissão para ler PRs do repositório (escopo `repo` ou `public_repo`).
- `requests` (já listado em requirements ou instale via pip)

Instalação (PowerShell):

```powershell
py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Exemplo de execução (PowerShell):

```powershell
# $env:GITHUB_TOKEN = 'ghp_xxx'  # preferir setar via secrets/CI
python .\scripts\collect_metrics\github_metrics.py --owner jadergreiner --repo agent-especialista-mercado-financeiro --out metrics_report.json

# Visualizar no PowerShell
Get-Content .\metrics_report.json -Raw | ConvertFrom-Json
```

Observações
- Este é um esqueleto inicial. Para produção, recomendamos:
  - Implementar paginação robusta e cache
  - Gravar resultados em banco (Postgres) ou enviar para sistema de métricas
  - Agendar execução via CI/cron (GitHub Actions / Azure Pipelines)
