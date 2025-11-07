# Guia de Uso – CLI Conversacional Prompt-First v1

## Início rápido

```powershell
cd backend
python cli_prompt_first.py
```

## Comandos

- `ajuda` — exibe comandos e exemplos
- `sair` — encerra a sessão (exibe resumo)
- `analisar <par>` — análise intraday do par (Forex ou Cripto)

## Exemplos de uso

```text
> ajuda
📚 COMANDOS:
  ajuda                - Exibe esta ajuda
  sair                 - Encerra a sessão
  analisar <par>       - Análise intraday do par

EXEMPLOS:
  analisar EURUSD      - Análise Forex intraday
  analisar BTCUSDT     - Análise Cripto intraday
  analisar BTCUSD      - Normalizado para BTCUSDT

> analisar BTCUSD
  ℹ️  Normalizando: BTCUSD → BTCUSDT
  📊 Classe detectada: CRIPTO

🔍 Analisando BTCUSD...
✅ Contrato válido

======================================================================
📋 RESULTADO (Contrato Mínimo v1)
======================================================================
{
  "classe_ativo": "cripto",
  "par": "BTCUSDT",
  "timeframe": "intraday",
  "timestamp": "2025-11-06T12:34:56Z",
  "resumo": {
    "preco_atual": 68500.00,
    "operacao": "COMPRA",
    "entrada": 68400.00,
    "alvo1": 69200.00,
    "stop": 68100.00,
    "rr": "1:2.6",
    "riscos_chave": ["volatilidade_alta"],
    "proximos_passos": ["aguardar_pullback"]
  },
  "justificativas": ["momentum positivo"]
}
======================================================================

> sair

👋 Encerrando sessão...
Sessão 20251106_123456: 2/2 comandos bem-sucedidos | latência média: 1850ms
```

## Aliases de símbolos

O CLI normaliza automaticamente:

- BTCUSD → BTCUSDT
- ETHUSD → ETHUSDT
- XBTUSD → BTCUSDT
- EUR/USD → EURUSD (remove barra)

## Logs de sessão

Gravados em `backend/logs/sessoes_cli.jsonl` (formato JSONL):

```json
{"sessao_id": "20251106_123456", "timestamp": "2025-11-06T12:35:00Z", "comando": "analisar", "latencia_ms": 1850.23, "sucesso": true, "erro": null}
```

Campos:
- `sessao_id`: identificador único da sessão
- `comando`: verbo do comando (ex.: analisar, ajuda)
- `latencia_ms`: tempo de resposta em milissegundos
- `sucesso`: se comando foi bem-sucedido
- `erro`: tipo de erro se falhou (null caso contrário)

## Validação de contratos

O CLI valida automaticamente o contrato mínimo de resposta:

- Campos obrigatórios: `classe_ativo`, `par`, `timeframe`, `timestamp`, `resumo`
- Campos obrigatórios em resumo: `preco_atual`, `operacao`, `entrada`, `alvo1`, `stop`
- Operação deve ser: `COMPRA`, `VENDA` ou `ESPERAR`

Se houver problemas, exibe avisos mas continua a execução.

## Fallback CSV manual

Se símbolo não for encontrado via yfinance, o CLI usa fallback CSV existente:

- Cripto: `backend/data/manual/CRIPTO/<SIMBOLO>.csv`
- Forex: suporte em desenvolvimento

Veja `backend/data/manual/CRIPTO/README.md` para formato esperado.

## Latência

- Alvo: < 3s para consultas simples (dados locais/cache)
- Exibe tempo de resposta se > 1s

## Histórico de comandos

Mantém últimos 5 comandos executados na sessão (sem persistência entre sessões).

## Limitações v1

- Sem cache entre sessões (cada análise refaz coleta)
- Timeframe fixo: intraday
- Classes suportadas: forex e cripto
- Sem suporte a comandos compostos (ex.: múltiplos pares de uma vez)
