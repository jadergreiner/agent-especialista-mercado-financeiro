# Taxonomia e Modelo de Dados (v1)

Responsável: Arquiteto de Dados — Define e mantém a taxonomia de domínios, contratos de dados (JSON-schemas), e padrões de qualidade/linhagem.

---

## 1. AssetId e Domínios

Formato: `<dominio>:<simbolo>`

- forex:EURUSD
- cripto:BTCUSDT
- eq:B3:PETR4
- fii:B3:KNRI11

Regras:

- Sempre minúsculo para o domínio; símbolo conforme convenção do mercado.
- Para ações/fiis, prefixo de bolsa (ex.: B3:) obrigatório.

---

## 2. Enums (Glossário)

- operacao: [COMPRA, VENDA, ESPERAR]
- tendencia: [ALTISTA, NEUTRO, BAIXISTA]
- fluxo: [COMPRA, VENDA, NEUTRO]
- vol: [ALTA, MEDIA, BAIXA]
- regimeVol: [BAIXA, MEDIA, ALTA]
- timeframe: [1m, 5m, 15m, 60m, D1]
- sessao: [TOQUIO, LONDRES, NOVA_YORK]

---

## 3. Padrões de Tempo e Números

- Timestamps sempre em UTC (ISO 8601; ex.: `2025-11-06T12:34:56Z`).
- Preços e métricas financeiras: usar Decimal no processamento; persistência como número com 5–8 casas conforme o ativo.
- Unidades explícitas nos contratos (ex.: `%` para variações, `pct` no campo) quando aplicável.

---

## 4. Contratos (Especificações v1)

### 4.1 quote.v1

```json
{
  "schema": "quote.v1",
  "assetId": "forex:EURUSD",
  "ts": "2025-11-06T12:34:56Z",
  "o": 1.1501, "h": 1.1512, "l": 1.1497, "c": 1.1510,
  "tf": "5m",
  "extras": {"vwap": 1.1507, "ema20": 1.1508, "ema50": 1.1504}
}
```

### 4.2 signal.tech.v1

```json
{
  "schema": "signal.tech.v1",
  "assetId": "forex:EURUSD",
  "ts": "2025-11-06T12:35:00Z",
  "features": {
    "trend15m": "ALTISTA",
    "rangePct": 0.13,
    "sris": {"sup": [1.1477], "res": [1.1668]}
  },
  "score": 0.62
}
```

### 4.3 signal.macroflow.v1

```json
{
  "schema": "signal.macroflow.v1",
  "assetId": "forex:EURUSD",
  "ts": "2025-11-06T12:36:00Z",
  "macro": {"dxyDaily": 0.0, "riskRegime": "Risco-On"},
  "flow": {"orderflow5m": "NEUTRO", "volRealizada": "BAIXA"},
  "confidence": 0.55
}
```

### 4.4 report.intraday.v1

```json
{
  "schema": "report.intraday.v1",
  "assetId": "forex:EURUSD",
  "ts": "2025-11-06T12:37:00Z",
  "operacao": "ESPERAR",
  "viesSessao": "Dólar estável",
  "rr": "1:1.5",
  "partes": {
    "macro": {"eventos": ["EUR: Discurso BCE"], "dxy": 0.0},
    "tecnica": {
      "vwap": 1.1507,
      "range": {"max": 1.1511, "min": 1.1497, "ampPct": 0.13},
      "sris": {"sup": [], "res": []},
      "tendencia15m": "ALTISTA",
      "invalidacao": 1.1507
    },
    "fluxo": {"orderflow": "NEUTRO", "vol": "BAIXA", "cot": "NEUTRO"}
  },
  "plano": {"entrada": 1.1507, "alvo1": 1.1511, "alvo2": 1.1497, "stop": 1.1507}
}
```

---

## 5. Qualidade, Linhagem e Retenção

- Validações: esquemas obrigatórios, campos numéricos finitos, quedas de NaN tratadas.
- Flags de confiabilidade: `dataQuality` no payload (ex.: `{"quotes": "ok", "dxy": "fallback"}`).
- Linhagem: registrar origem (provedor, endpoint, parâmetros) e transformações chave (features aplicadas).
- Retenção:
  - bronze (raw): 7–14 dias intraday (SQLite/arquivos por ora)
  - prata (curado): 30–90 dias (SQLite/PostgreSQL)
  - ouro (agregado p/ relatórios): 1–2 anos (PostgreSQL)

---

## 6. Convenções e Naming

- Campos curtos e consistentes em séries intraday (o,h,l,c,tf).
- Campos explicativos nas camadas prata/ouro.
- Prefixos para percentuais (`pct`) e variações (`delta`).
- Timeframes em camel-case curto (5m, 15m, 60m, D1).

---

## 7. Roadmap de Dados

1) Publicar os contratos v1 (quote/signal.tech/signal.macroflow/report.intraday) no registry.
2) Adotar validação de schema na saída dos analisadores (Forex/Cripto).
3) Incluir flags de confiabilidade e origem (source) nos payloads.
4) Introduzir partições por data/assetId na persistência.
5) Evoluir para JSON Schema formal e testes de compatibilidade em CI.
