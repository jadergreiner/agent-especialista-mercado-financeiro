# Registry de Schemas (Contratos JSON)

> Padrões de contrato para mensagens/relatórios do agente. Versão inicial foca no relatório intraday (Forex).

## Estrutura

```text
backend/
├── schemas/
│   └── report.intraday.v1.json      # Contrato v1 do relatório intraday
└── src/
    └── schemas/
        └── validador.py             # Loader + validador (jsonschema se disponível)
```

## Contrato: `report.intraday.v1`

- Classe de ativo: `forex` (v1)
- Objetivo: padronizar saída do analisador intraday (AF + AT + Flow/Vol) para orquestração/event-bus e persistência
- Campos principais:
  - `resumo`: operação proposta, viés, R/R
  - `analises`: eventos macro (mock/ok), técnica (VWAP proxy, range, SRIs, tendência), fluxo/vol (heurísticos)
  - `plano`: entrada, alvos, stop e justificativas
    - `qualidade`: flags de disponibilidade/qualidade de dados (ex.: `dxy: ok|fallback|indisponivel`, `calendario: ok|mock`)

Veja o schema completo em `backend/schemas/report.intraday.v1.json`.

Campos opcionais introduzidos (compatíveis via `additionalProperties` do draft-07):
- `analises.tecnica.srisDetalhado`: níveis por timeframe `{ H1, H4, D1 }`, cada um com `{ suportes[], resistencias[] }`.
- `analises.tecnica.vwapSessoes`: VWAP proxy por sessão `{ tokyo, londres, ny }` (números ou null se indisponível).

## Contrato: `report.trading.cripto.v1`

- Classe de ativo: `cripto`
- Objetivo: padronizar saída do analisador de cripto (AF + AT + On-Chain) para orquestração e persistência
- Campos principais:
  - `resumo`: operação proposta, momentum consolidado, R/R (e `viesSessao` espelhando momentum para compatibilidade de persistência)
  - `analises`:
    - `fundamentalista`: momentum, notícias, correlação BTC/ETH, sentimento macro
    - `tecnica`: momentum, extremos 30d, MA100, suportes/resistências, pontos críticos
    - `onchain`: netflow, whales, funding rate, supply, conclusão
  - `plano`: entrada, alvos (1-3), stop e justificativas

Veja o schema completo em `backend/schemas/report.trading.cripto.v1.json`.

## Validação

O validador tenta usar `jsonschema` (draft-07). Se a dependência não estiver instalada, cai para uma verificação mínima de campos obrigatórios e tipos principais.

Uso no código:

```python
from schemas.validador import validar_contra_schema
ok, erros = validar_contra_schema(payload, 'report.intraday.v1')
```

## Emissão de JSON

O analisador Forex implementa `gerar_json(...)` que retorna um `dict` no contrato v1. A CLI salva o JSON junto ao markdown e valida automaticamente:

```text
backend/relatorios_intraday/
  EURUSD_YYYYMMDD_HHMMSS.md
  EURUSD_YYYYMMDD_HHMMSS.json
```

O analisador de Cripto também implementa `gerar_json(...)` com o contrato `report.trading.cripto.v1`. A CLI salva e valida em `backend/relatorios_trading/`:

```text
backend/relatorios_trading/
  BTCUSDT_YYYYMMDD_HHMMSS.md
  BTCUSDT_YYYYMMDD_HHMMSS.json
```

## Outros contratos disponíveis

- `quote.v1` — cotações padronizadas (para uso futuro em backfill/bus)
- `signal.tech.v1` — sinais técnicos derivados dos relatórios
- `signal.macroflow.v1` — sinais macro/fluxo derivados dos relatórios
- `setup.v1` — setups operacionais detectados automaticamente (ex.: `vwap_pullback_reject`), com `direcao` (COMPRA/VENDA), `score` e `criterios` explicativos.

Os eventos publicados no diretório `backend/bus` são validados contra esses contratos e incluem um envelope com `valid`, `errors[]` e `event`.
