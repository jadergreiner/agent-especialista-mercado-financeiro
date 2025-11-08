# ETL: Ingestão das métricas para Postgres

Origin: DT-014 - Documentação de deploy do ETL

Pré-requisitos

- Banco Postgres acessível (crie database / usuário conforme política do time)
- Executar o script SQL `docs/metrics/create_table_governance_metrics.sql` para criar a tabela
- Variáveis de ambiente para conexão PostgreSQL: `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

Instalação (PowerShell)

```powershell
# Crie e ative virtualenv
py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r scripts/collect_metrics/requirements.txt

# Executar coletor (gera JSON)
python .\scripts\collect_metrics\github_metrics.py --owner jadergreiner --repo agent-especialista-mercado-financeiro --out metrics_report.json

# Rodar ETL que insere no Postgres
python .\scripts\collect_metrics\etl_to_postgres.py --in metrics_report.json
```

Recomendações

- Agendar execução semanal via GitHub Actions ou cron e salvar relatórios como artefatos ou inserir diretamente via ETL.
- Monitorar falhas (alertas) e criar retry/backoff.
