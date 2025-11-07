# Resolução de Símbolos e Fallback – Prompt-First v1

Objetivo: reduzir atrito na entrada do usuário, normalizando símbolos e fornecendo instruções claras para fallback manual.

## Normalização

- Aliases comuns:
  - BTCUSD → BTCUSDT
  - ETHUSD → ETHUSDT
  - XBTUSD → BTCUSDT
- Forex: remover barra e normalizar caixa: `eur/usd` → `EURUSD`

## Mapa e mensagens

- Se símbolo não for reconhecido via fonte primária (yfinance/Exchange):
  - Procurar CSV manual em `backend/data/manual/{CLASSE}/{SIMBOLO}.csv`
  - Mensagem clara com caminho exato esperado e amostra de cabeçalho

## CSV manual (amostra PT-BR)

```csv
Data;Abertura;Máxima;Mínima;Último;Vol.
2025-10-01;68.500,00;69.000,00;67.800,00;68.700,00;1,2M
```

- BOM opcional, cabeçalhos entre aspas aceitos
- Separador `,` ou `;` aceito; decimais com vírgula tratados
- Volume com sufixo K/M aceito

## Logs de resolução

- Logar decisão de normalização
- Logar fonte final (yfinance | exchange | csv_manual)
- Logar mensagem de instrução quando faltar arquivo manual
