# Contratos de Resposta – Prompt-First v1

Objetivo: padronizar a estrutura mínima de saída das respostas do agente no modo interativo (CLI conversacional), garantindo previsibilidade e validação leve.

## Convenções gerais

- Campos em português, snake_case
- Timestamps em UTC (ISO 8601)
- Valores monetários como float simples (v1), com futura migração para Decimal
- Níveis de recomendação: `COMPRA`, `VENDA`, `ESPERAR`
- Timeframe textual (ex.: `intraday`, `diario`)

## Forex – contrato mínimo (v1)

```json
{
  "classe_ativo": "forex",
  "par": "EURUSD",
  "timeframe": "intraday",
  "timestamp": "2025-11-06T12:34:56Z",
  "resumo": {
    "preco_atual": 1.0765,
    "operacao": "COMPRA",
    "entrada": 1.0750,
    "alvo1": 1.0800,
    "stop": 1.0720,
    "rr": "1:1.6",
    "riscos_chave": ["volatilidade_elevada", "evento_macro_proximo"],
    "proximos_passos": ["aguardar_pullback", "confirmar_fluxo"]
  },
  "justificativas": [
    "DXY em recuo intraday",
    "suporte em SRI H1"
  ]
}
```

Campos obrigatórios: `classe_ativo`, `par`, `timeframe`, `timestamp`, `resumo.preco_atual`, `resumo.operacao`, `resumo.entrada`, `resumo.alvo1`, `resumo.stop`.

## Cripto – contrato mínimo (v1)

```json
{
  "classe_ativo": "cripto",
  "par": "BTCUSDT",
  "timeframe": "intraday",
  "timestamp": "2025-11-06T12:34:56Z",
  "resumo": {
    "preco_atual": 68500.00,
    "operacao": "VENDA",
    "entrada": 68620.00,
    "alvo1": 67800.00,
    "stop": 68950.00,
    "rr": "1:2.2",
    "riscos_chave": ["funding_positivo", "alta_dominancia_btc"],
    "proximos_passos": ["aguardar_reteste_vwap", "monitorar_open_interest"]
  },
  "justificativas": [
    "falha em topo intraday",
    "divergência de momentum"
  ]
}
```

Observações:
- `par` aceita aliases (ex.: `BTCUSD` → normalizar para `BTCUSDT` quando aplicável)
- Quando fonte for CSV manual, registrar metadado de origem no log (v1: não obrigatório no payload)

## Validação leve (v1)

- Estrutural: presença de campos obrigatórios e tipos básicos (string/float/array)
- Semântica mínima: `operacao` ∈ {COMPRA, VENDA, ESPERAR}
- RR pode ser string “1:N”, sem parsing rígido na v1
