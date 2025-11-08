---
title: "ISSUE: Parametrizar queries SQL para evitar injeção"
labels: [security, severity-medium]
---

# Resumo

Arquivos afetados (exemplos):
- `backend/app_dashboard.py` (linha ~38)
- `backend/dashboard_web.py` (linha ~275)
- `backend/otimizacao_persistencia.py` (linha ~344)
- `backend/sistema_alertas_avancado.py` (linhas ~686 e ~704)

O scanner identificou construções de query usando formatação de string (f-strings ou `.format`) que podem levar a injeção SQL se valores interpolados vierem de fontes externas.

## Evidência

Exemplo (app_dashboard.py):

```python
df = pd.read_sql_query(
    f"SELECT id, classe_ativo, par, timestamp, operacao, vies_sessao, rr FROM relatorios_intraday ORDER BY timestamp DESC LIMIT {int(limit)}",
    con
)
```

## Remediação sugerida

1. Usar consultas parametrizadas (p.ex. `?` no sqlite3 ou parâmetros do driver) em vez de interpolar valores diretamente.
2. Validar e sanitizar quaisquer valores que ainda precisem ser incorporados em posições não parametrizáveis (p.ex. nomes de colunas ou ORDER BY) através de listas brancas.
3. Adicionar testes que tentem injetar conteúdo para garantir que o sistema rejeite entradas maliciosas.

## Critérios de aceitação

- Todas as queries que atualmente concatenam/formatam strings com entradas externas devem ser migradas para parametrização.
- Testes automatizados mostrando resistência a payloads básicos de injeção.

## Prioridade

Alta — potencial de injeção em módulos que lidam com dados analíticos.

## Sugestão de dono

backend/db-team
