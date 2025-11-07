# Templates de Prompt – Prompt-First v1

Objetivo: garantir consistência e reduzir latência criando templates curtos e focados para cada classe de ativo.

## Regras gerais

- Prompts curtos, sem redundância
- Saída sempre no contrato mínimo correspondente
- Pedir apenas o essencial para v1; confluências adicionais como notas

## Forex – template (exemplo)

```text
Contexto: Você é um especialista de Forex. Gere uma análise intraday para {par}.

Regras:
- Utilize dados recentes (fonte principal: yfinance; fallback: CSV manual)
- Timeframe: intraday
- Foque em preço atual, operação, entrada, alvo1, stop e RR
- Liste 1–3 riscos chave e próximos passos operacionais
- Responda no contrato mínimo Forex v1 em JSON

Saída esperada:
{CONTRATO_JSON}
```

## Cripto – template (exemplo)

```text
Contexto: Você é um especialista de Cripto. Gere uma análise intraday para {par}.

Regras:
- Fonte primaria: yfinance ou exchange disponível; fallback: CSV manual
- Timeframe: intraday
- Forneça preço atual, operação, entrada, alvo1, stop e RR
- Liste 1–3 riscos chave e próximos passos
- Responda no contrato mínimo Cripto v1 em JSON

Saída esperada:
{CONTRATO_JSON}
```

## Exemplos de substituição

- {par} → "EURUSD" ou "BTCUSDT"
- {CONTRATO_JSON} → JSON conforme docs/prompt-first/contratos_resposta.md
