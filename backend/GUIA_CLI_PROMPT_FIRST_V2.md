# 📦 Guia CLI Prompt-First v2

## Novidades da v2


### ⚡ Cache de Sessões


- **Storage**: SQLite (leve, sem dependências externas)

- **TTL por classe**: Forex (5min), Cripto (2min)

- **Cache automático**: Resultados são armazenados automaticamente

- **Transparente**: Indicadores visuais de cache HIT/MISS


### 🎯 Comandos em Batch


- Analise múltiplos pares em um único comando

- Processamento sequencial otimizado

- Resumo consolidado ao final


### 📊 Comando `cache`


- Exibe estatísticas em tempo real

- Total de entradas, válidas, expiradas

- Taxa de acerto (hit rate)

- Distribuição por classe de ativo

### 🕘 Histórico persistente (MVP)

- Armazena todos os comandos em `backend/logs/historico_cli.txt`
- Novo comando `historico [N]` para listar os últimos N comandos (padrão 10)
- Compatível entre sessões (persiste após encerrar)

## Comandos Disponíveis


### `ajuda`

Exibe a lista de comandos e exemplos.


### `analisar <par> [<par2> <par3> ...] [intraday|diario|semanal|mensal]`

Analisa um ou mais pares de ativos.

**Exemplos:**

```bash
analisar EURUSD                      # Análise única (Forex)
analisar BTCUSDT                     # Análise única (Cripto)
analisar EURUSD GBPUSD              # Batch com 2 pares
analisar BTCUSDT ETHUSDT BNBUSDT   # Batch com 3 pares
analisar EURUSD diario              # Análise com timeframe diário
analisar EURUSD GBPUSD semanal      # Batch com timeframe semanal
```


**Comportamento:**

- **Análise única**: Exibe contrato completo em JSON
- **Análise batch**: Exibe resumo consolidado de todos os pares
- **Timeframe (MVP)**: Aplica-se ao cache e ao campo `timeframe` do contrato; o motor de análise ainda é o mesmo do intraday

### `historico [N]`

Exibe os últimos N comandos persistidos (padrão 10; máximo 100).

**Exemplos:**

```bash
historico           # Lista os últimos 10
historico 25        # Lista os últimos 25
```


### `cache`

Exibe estatísticas do cache.

**Informações exibidas:**

- Total de entradas armazenadas

- Entradas válidas vs expiradas

- Distribuição por classe (forex, cripto)

- Cache hits e misses da sessão atual

- Taxa de acerto percentual


### `sair`

Encerra a sessão e limpa cache expirado.

**Ao encerrar:**

- Exibe resumo da sessão (comandos executados, latência média)

- Remove automaticamente entradas expiradas do cache

- Salva log da sessão em `backend/logs/sessoes_cli.jsonl`

## Normalização de Símbolos

Aliases automáticos aplicados:

- `BTCUSD` → `BTCUSDT`

- `ETHUSD` → `ETHUSDT`

- `XBTUSD` → `BTCUSDT`

- `EUR/USD` → `EURUSD`

## Performance


### Latência Esperada

**Sem cache (cache MISS):**

- Forex: 2-4 segundos

- Cripto: 2-5 segundos (depende da fonte)

**Com cache (cache HIT):**

- Qualquer ativo: < 500ms ⚡


### TTL (Time-to-Live)

| Classe | TTL | Justificativa |
|--------|-----|---------------|
| Forex | 5 minutos | Menor volatilidade |
| Cripto | 2 minutos | Alta volatilidade |
| Ações | 5 minutos | Mercado regular |

## Observabilidade


### Logs de Sessão

Localização: `backend/logs/sessoes_cli.jsonl`

**Estrutura:**

```json
{
  "sessao_id": "20251106_143022",
  "timestamp": "2025-11-06T14:30:25Z",
  "comando": "analisar",
  "latencia_ms": 2450.5,
  "sucesso": true,
  "erro": null
}

```



### Indicadores Visuais


- `⚡ Cache HIT!` - Resultado recuperado do cache

- `🔄 Cache MISS` - Consultando fonte de dados

- `⏱️ Tempo de resposta: X.Xs` - Exibido se latência > 1s

## Exemplo de Sessão


```bash
> analisar EURUSD
🔍 Analisando EURUSD...
  📊 Classe detectada: FOREX
  🔄 Cache MISS - consultando fonte de dados...

✅ Contrato válido
📋 RESULTADO (Contrato Mínimo v2)
{...}
⏱️ Tempo de resposta: 2.8s

> analisar EURUSD
🔍 Analisando EURUSD...
  📊 Classe detectada: FOREX
  ⚡ Cache HIT! (latência reduzida)
✅ Contrato válido
📋 RESULTADO (Contrato Mínimo v2)
{...}

> cache
📊 ESTATÍSTICAS DO CACHE:
  Total de entradas: 1
  Válidas: 1
  Expiradas: 0
  Por classe: {'forex': 1}

  Cache hits: 1
  Cache misses: 1
  Taxa de acerto: 50.0%

> analisar BTCUSDT ETHUSDT
🔍 Analisando 2 pares em batch...

[1/2] Processando BTCUSDT...
  📊 Classe detectada: CRIPTO
  🔄 Cache MISS - consultando fonte de dados...

[2/2] Processando ETHUSDT...
  📊 Classe detectada: CRIPTO
  🔄 Cache MISS - consultando fonte de dados...

📋 RESULTADOS BATCH (2/2 bem-sucedidos)
BTCUSDT:
  Operação: COMPRA
  Preço atual: 45230.50
  Entrada: 45100.00
  Stop: 44850.00
  Alvo: 45600.00
  R:R: 2.0:1

ETHUSDT:
  Operação: ESPERAR
  Preço atual: 2890.30

> sair
👋 Encerrando sessão...
Sessão 20251106_143022: 4/4 comandos bem-sucedidos | latência média: 1850ms
🧹 0 entradas expiradas removidas do cache

```


## Limitações Conhecidas (v2)

1. **Timeframes dinâmicos (MVP)**: `diario|semanal|mensal` são aceitos e registrados no contrato/cache, mas usam o mesmo motor de análise do intraday
2. **Aliases fixos**: Não é possível customizar aliases (planejado para v3)
3. **Histórico persistente (MVP)**: Persistência simples em arquivo texto; sem filtros/ busca ainda
4. **Processamento sequencial**: Batch não é paralelo (otimização futura)

## Próximas Iterações

Veja `docs/gestao-agil/backlog.md` para roadmap completo:

- v3: Timeframes dinâmicos (diario, semanal, mensal)

- v3: Aliases customizáveis por usuário

- v3: Histórico persistente entre sessões

- v3: Testes end-to-end automatizados

## Troubleshooting


### Cache não funciona

**Sintoma**: Sempre exibe "Cache MISS"
**Causa**: TTL muito curto ou símbolo diferente
**Solução**: Verifique se o símbolo está normalizado corretamente


### Latência alta

**Sintoma**: Tempo de resposta > 5s
**Causa**: Fonte de dados lenta ou instável
**Solução**: Resultado será cacheado para próximas consultas


### Erro de encoding (Windows)

**Sintoma**: `UnicodeEncodeError`
**Causa**: Console Windows com encoding CP1252
**Solução**: CLI v2 já configura UTF-8 automaticamente

