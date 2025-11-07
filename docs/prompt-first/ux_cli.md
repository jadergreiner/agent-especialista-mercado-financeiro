# UX do CLI Conversacional – Prompt-First v1

Objetivo: especificar comportamento mínimo do CLI interativo para validação rápida de uso.

## Comandos e fluxo

- `ajuda`: lista comandos e exemplos rápidos
- `sair`: encerra a sessão
- `analisar <par> [classe] [timeframe]`: executa análise
  - `classe` opcional: `forex`|`cripto` (default: auto)
  - `timeframe` opcional: `intraday`|`diario` (default: intraday)

## Requisitos de UX

- Latência alvo: < 3s para consultas simples com cache/dados locais
- Mensagens de erro amigáveis, com sugestão imediata de correção (ex.: como nomear CSV)
- Histórico curto de comandos (0–5 últimos)
- Log de sessão em arquivo rotativo (sem dados sensíveis)

## Exemplo de interação

```text
> ajuda
Comandos: analisar, ajuda, sair
Exemplos:
  analisar EURUSD forex intraday
  analisar BTCUSDT cripto

> analisar BTCUSD
Normalizando símbolo: BTCUSD → BTCUSDT
Coletando dados (yfinance)...
Resposta (JSON):
{ ... contrato mínimo Cripto v1 ... }
```
