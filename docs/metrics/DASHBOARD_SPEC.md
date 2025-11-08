# Especificação do Dashboard de Métricas de Governança

Origin: DT-014 / LA-018 - Especificação de métricas e queries

Objetivo
- Fornecer visão semanal da adoção das regras de governança (DECISAO-002) e eficácia do treinamento.

Modelo de dados sugerido (tabela Postgres `governance_metrics_weekly`):

| coluna | tipo | descrição |
|---|---|---|
| id | serial PK | Identificador
| week_start | date | Data do início da semana (segunda-feira)
| repo | text | Repositório (owner/repo)
| total_prs | integer | Total de PRs no periodo
| decision_prs | integer | PRs que referenciam a decisão (DECISAO-002)
| template_prs | integer | PRs que usam o template de PR
| exceptions_count | integer | Número de exceções registradas (semana)
| avg_exception_approval_hours | numeric | Tempo médio (horas) para aprovação de exceções
| training_attendance | integer | Número de participantes no workshop/treinamento
| generated_at | timestamptz | Timestamp da coleta

ETL / Ingestão
- O script `scripts/collect_metrics/github_metrics.py` gera um JSON resumido. A etapa ETL deve:
  1. Ler JSON e validar campos
  2. Inserir/atualizar registro na tabela `governance_metrics_weekly`
  3. Opcional: exportar para CSV e enviar ao Metabase/Grafana

Queries de exemplo (Postgres):

1) Percentual de PRs que referenciam DECISAO-002 na última semana

```sql
select repo,
  decision_prs::float / nullif(total_prs,0) * 100 as pct_decision_prs
from governance_metrics_weekly
where week_start = current_date - ((extract(dow from current_date)::int + 6) % 7)
;
```

2) Tendência de adesão ao template (últimas 12 semanas)

```sql
select week_start,
  sum(template_prs) as template_prs,
  sum(total_prs) as total_prs,
  (sum(template_prs)::float / nullif(sum(total_prs),0)) * 100 as pct_template
from governance_metrics_weekly
group by week_start
order by week_start desc
limit 12;
```

3) Alertas: semanas com pct_decision_prs < 30%

```sql
select week_start, repo, (decision_prs::float/ nullif(total_prs,0))*100 as pct_decision
from governance_metrics_weekly
where (decision_prs::float / nullif(total_prs,0)) * 100 < 30
order by week_start desc;
```

Visuais sugeridos
- KPI cards: % PRs com DECISAO-002, % PRs com template, participação em treinamento
- Time series: Tendência semanal das métricas (12-24 semanas)
- Tabela: Lista de exceções abertas e tempo médio de aprovação

Integração com Grafana/Metabase
- Metabase: criar pergunta SQL baseada nas queries acima e montar dashboard
- Grafana: ingestão via Postgres datasource ou Prometheus (expor métricas via pushgateway)

Segurança e privacidade
- Não exibir dados sensíveis (bodies completos de PRs). Expor apenas contadores e IDs públicos.
