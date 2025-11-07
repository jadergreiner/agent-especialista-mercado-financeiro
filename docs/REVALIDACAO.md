# Sistema de Revalidação e Evolução do Modelo

## Visão Geral

O sistema de revalidação rastreia a **assertividade** das recomendações de trading após 24 horas, permitindo:

1. **Medição de performance**: Taxa de acerto das recomendações COMPRA/VENDA/ESPERAR
2. **Análise de padrões**: Identificação de condições onde o modelo acerta ou erra
3. **Evolução contínua**: Ajuste de heurísticas e parâmetros baseado em dados reais

## Arquitetura

### Banco de Dados

#### Tabela `relatorios_intraday`
- Armazena análises originais (payload completo em JSON)
- Campos: `id`, `classe_ativo`, `par`, `timestamp`, `operacao`, `vies_sessao`, `rr`, `payload_json`

#### Tabela `revalidacoes`
- Registra assertividade 24h após cada análise
- Campos principais:
  - **Linkage**: `relatorio_id` (FK), `par`, `classe_ativo`
  - **Timestamps**: `timestamp_original`, `timestamp_revalidacao`
  - **Preços originais**: `preco_entrada_original`, `preco_alvo1`, `preco_stop`
  - **Preços reais**: `preco_24h` (fetched 24h depois)
  - **Assertividade**: `acertou` (1/0), `pontos_movimento`, `pct_movimento`, `objetivo_atingido`
  - **Observações**: `observacoes` (texto livre para contexto)

### CLI de Revalidação

**Script**: `backend/cli_revalidar.py`

```bash
# Listar relatórios pendentes (sem executar)
python cli_revalidar.py --dry-run

# Revalidar todos os pendentes (>= 24h)
python cli_revalidar.py

# Revalidar até 50 relatórios
python cli_revalidar.py --limite 50

# Revalidar relatórios com 48h ou mais
python cli_revalidar.py --horas 48
```

#### Fluxo de Revalidação

1. **Busca relatórios pendentes**:
   ```sql
   SELECT * FROM relatorios_intraday r
   LEFT JOIN revalidacoes rv ON r.id = rv.relatorio_id
   WHERE r.timestamp <= NOW() - 24h
     AND rv.id IS NULL
   ```

2. **Para cada relatório**:
   - Extrai preços do payload: `entrada`, `alvo1`, `stop`, `precoAtual`
   - Calcula `timestamp_revalidacao = timestamp_original + 24h`
   - **Busca preço real 24h**:
     - **Cripto**: Carrega CSV manual de `data/manual/CRIPTO/<SIMBOLO>.csv`
     - **Forex**: (TODO: yfinance ou CSV manual)
   - **Calcula assertividade**:
     - `COMPRA`: acerta se `preco_24h > preco_entrada`
     - `VENDA`: acerta se `preco_24h < preco_entrada`
     - `ESPERAR`: acerta se `abs(pct_movimento) < 2%`
   - **Identifica objetivo atingido**:
     - `TP1`: atingiu take profit 1
     - `STOP`: atingiu stop loss
     - `PARCIAL`: moveu na direção certa mas não atingiu TP1
     - `NENHUM`: não moveu ou moveu contra
   - **Salva no banco**: INSERT INTO revalidacoes

3. **Output**:
   ```
   Revalidando relatório #15: VIRTUALUSDT (cripto)
     Timestamp original: 2025-11-06T02:13:48
     Operação original: COMPRA
     ✓ Preço 24h encontrado: $1.4500 (candle: 2025-11-07 02:00:00)
     📊 Assertividade:
        Acertou: ✅ SIM
        Movimento: +0.0900 pontos (+12.50%)
        Objetivo: PARCIAL
     ✅ Revalidação salva no banco (id=1)
   ```

## Lógica de Assertividade

### COMPRA
```python
acertou = preco_24h > preco_entrada

if preco_24h >= preco_alvo1:
    objetivo = 'TP1'  # Hit target
elif preco_24h <= preco_stop:
    objetivo = 'STOP'  # Hit stop loss
elif preco_24h > preco_entrada:
    objetivo = 'PARCIAL'  # Moved in right direction
else:
    objetivo = 'NENHUM'  # No movement or wrong direction
```

### VENDA
```python
acertou = preco_24h < preco_entrada

if preco_24h <= preco_alvo1:
    objetivo = 'TP1'
elif preco_24h >= preco_stop:
    objetivo = 'STOP'
elif preco_24h < preco_entrada:
    objetivo = 'PARCIAL'
else:
    objetivo = 'NENHUM'
```

### ESPERAR
```python
pct_movimento = ((preco_24h - preco_entrada) / preco_entrada) * 100
acertou = abs(pct_movimento) < 2.0  # Consideramos acerto se movimento < 2%
objetivo = 'NENHUM'
```

## Métricas Calculadas

### Por Revalidação
- **acertou**: Boolean (direção correta)
- **pontos_movimento**: `preco_24h - preco_entrada` (absoluto)
- **pct_movimento**: Movimento percentual
- **objetivo_atingido**: TP1 | STOP | PARCIAL | NENHUM

### Agregadas (para Dashboard)
```sql
-- Taxa de acerto global
SELECT 
    COUNT(*) as total,
    SUM(acertou) as acertos,
    ROUND(100.0 * SUM(acertou) / COUNT(*), 2) as taxa_acerto
FROM revalidacoes;

-- Por par
SELECT 
    par,
    COUNT(*) as total,
    SUM(acertou) as acertos,
    ROUND(100.0 * SUM(acertou) / COUNT(*), 2) as taxa_acerto,
    AVG(pct_movimento) as movimento_medio
FROM revalidacoes
GROUP BY par
ORDER BY taxa_acerto DESC;

-- Por operação
SELECT 
    operacao_original,
    COUNT(*) as total,
    SUM(acertou) as acertos,
    SUM(CASE WHEN objetivo_atingido = 'TP1' THEN 1 ELSE 0 END) as tp1_atingidos,
    SUM(CASE WHEN objetivo_atingido = 'STOP' THEN 1 ELSE 0 END) as stops
FROM revalidacoes
GROUP BY operacao_original;

-- Evolução temporal (rolling 30d)
SELECT 
    DATE(timestamp_revalidacao) as data,
    COUNT(*) as total,
    SUM(acertou) as acertos,
    ROUND(100.0 * SUM(acertou) / COUNT(*), 2) as taxa_acerto
FROM revalidacoes
WHERE timestamp_revalidacao >= DATE('now', '-30 days')
GROUP BY DATE(timestamp_revalidacao)
ORDER BY data;
```

## Evolução do Modelo

### 1. Coleta de Dados (Atual)
- CLI rodando diariamente (cron/Task Scheduler)
- Acumular pelo menos **50-100 revalidações** antes de tuning

### 2. Análise de Padrões
```python
import pandas as pd
import sqlite3

# Carregar revalidacoes
con = sqlite3.connect('data/trading.db')
df_rev = pd.read_sql('SELECT * FROM revalidacoes', con)
df_rel = pd.read_sql('SELECT * FROM relatorios_intraday', con)

# Join para extrair features do payload
merged = df_rev.merge(df_rel, left_on='relatorio_id', right_on='id')

# Análise de correlação: features vs acertou
# Features candidatas (extraídas do payload_json):
# - dist_vwap (distância ao VWAP no setup)
# - dist_sri (distância ao SRI no setup)
# - tendencia (ALTISTA/BAIXISTA)
# - fluxo (COMPRADOR/VENDEDOR)
# - volatilidade_sessao
# - rr (risk/reward)

# Identificar padrões:
# - COMPRA acerta mais quando dist_vwap < X?
# - VENDA acerta mais quando fluxo = VENDEDOR?
# - RR > 3 tem taxa de acerto melhor?
```

### 3. Ajuste de Heurísticas
Com base nos padrões identificados, ajustar thresholds:

**Arquivo**: `src/sinais/emissor.py`
```python
# Antes
tol_vwap = 0.00025  # 0.025% do preço
tol_sri = 0.00050   # 0.050% do preço

# Depois (exemplo: dados mostram que setups com dist_vwap < 0.0001 tem 85% acerto)
tol_vwap = 0.0001   # Mais restritivo
tol_sri = 0.00030   # Ajustado com base em análise
```

**Arquivo**: `src/dados/analisador_trading_cripto.py`
```python
# Ajustar thresholds de momentum, MA alignment, etc.
# com base em taxa de acerto por condição
```

### 4. A/B Testing
- Rodar backtest com parâmetros **antigos** vs **novos**
- Comparar taxa de acerto, RR médio, drawdown
- Implementar apenas se melhoria significativa (p < 0.05)

### 5. Ciclo Contínuo
- Re-coletar dados com novo modelo
- Re-analisar assertividade
- Iterar ajustes
- **Meta**: Convergir para taxa de acerto > 60% (excelente para trading)

## Automação

### Cron (Linux/Mac)
```bash
# Revalidar diariamente às 3h da manhã
0 3 * * * cd /caminho/backend && python cli_revalidar.py >> logs/revalidacao.log 2>&1
```

### Task Scheduler (Windows)
```powershell
# Criar tarefa agendada
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "cli_revalidar.py" -WorkingDirectory "C:\repo\projetos\agent-especialista-mercado-financeiro\backend"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "RevalidarTrading" -Description "Revalida assertividade de relatórios intraday"
```

### Docker (Se aplicável)
```yaml
# docker-compose.yml
services:
  revalidador:
    build: .
    command: sh -c "while true; do python cli_revalidar.py; sleep 86400; done"
    volumes:
      - ./data:/app/data
```

## Dashboard de Assertividade

**TODO**: Página Streamlit com:

1. **Métricas Globais**:
   - Taxa de acerto geral (%)
   - Total de revalidações
   - Movimento médio (pontos/%)

2. **Breakdown por Par**:
   - Bar chart: taxa de acerto por símbolo
   - Tabela: par | total | acertos | taxa | movimento médio

3. **Breakdown por Operação**:
   - Pie chart: distribuição COMPRA/VENDA/ESPERAR
   - Tabela: operação | taxa acerto | TP1 atingidos | stops

4. **Evolução Temporal**:
   - Line chart: taxa de acerto rolling 30 dias
   - Área chart: acertos vs erros ao longo do tempo

5. **Filtros**:
   - Range de datas
   - Classe de ativo (forex/cripto)
   - Par específico
   - Operação (COMPRA/VENDA/ESPERAR)

## Exemplo Real: VIRTUALUSDT

**Relatório Original** (2025-11-06 02:13:48):
- Operação: COMPRA
- Entrada: $0.72
- Alvo 1: $1.74
- Stop: $0.67
- Preço Atual: $1.34
- R/R: 1:22.5

**Revalidação** (2025-11-07 02:13:48):
- Preço 24h: (será obtido do CSV VIRTUALUSDT.csv)
- Se preco_24h > $0.72: **acertou = True**
- Se preco_24h >= $1.74: **objetivo = TP1** 🎯
- Se $0.72 < preco_24h < $1.74: **objetivo = PARCIAL** ✅
- Se preco_24h <= $0.67: **objetivo = STOP** ❌

## Próximos Passos

- [ ] Implementar busca de preço 24h para Forex (yfinance)
- [ ] Dashboard Streamlit com métricas de assertividade
- [ ] CLI para análise de padrões (`cli_analisar_assertividade.py`)
- [ ] Integrar revalidação com GitHub Actions (CI/CD)
- [ ] Alertas quando taxa de acerto cai abaixo de threshold (ex: < 55%)
- [ ] Export de revalidacoes para Parquet/CSV para análise em Jupyter
