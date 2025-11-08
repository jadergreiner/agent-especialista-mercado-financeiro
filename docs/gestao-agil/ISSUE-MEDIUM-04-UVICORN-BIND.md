---
title: "ISSUE: Evitar bind 0.0.0.0 em ambiente com reload=True"
labels: [security, severity-medium]
---

# Resumo

Arquivo: `backend/main.py` (linha ~45)

Evidência:

```python
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

## Risco

- `reload=True` em conjunto com bind `0.0.0.0` pode expor instâncias de desenvolvimento com comportamento inesperado em ambientes compartilhados.

## Remediação sugerida

1. Fazer o host/porta configuráveis via variáveis de ambiente; por padrão usar `127.0.0.1` em desenvolvimento.
2. Garantir que `reload=True` só seja usado em ambientes de desenvolvimento controlados (p.ex. checar `ENV` antes de setar o flag).

## Critérios de aceitação

- Configuração externa (env var) para host/porta/reload e documentação atualizada.
- Teste de smoke que valida a aplicação inicia com as configurações definidas.

## Prioridade

Medium
