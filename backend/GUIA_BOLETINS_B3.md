# Integração de Boletins Diários B3

## 📋 Visão Geral

Este documento descreve a estrutura de dados dos **Boletins Diários da B3** e como esses dados complementam e melhoram as estratégias de trading do WIN.

## 📊 Dados Disponíveis nos Boletins B3

### 1. Dados Básicos de Preço e Volume

**Fonte**: Boletim Diário B3 - Seção Derivativos

| Campo | Descrição | Uso na Estratégia |
|-------|-----------|-------------------|
| `abertura` | Preço de abertura do pregão | Identificar gaps, análise de força/fraqueza |
| `maxima` | Preço máximo do dia | Resistências intraday, amplitude (range) |
| `minima` | Preço mínimo do dia | Suportes intraday, amplitude (range) |
| `fechamento` | Preço de fechamento oficial | Cálculo de indicadores técnicos |
| `ajuste_diario` | Preço de ajuste (settlement) | **CRÍTICO**: base para marcação de posições |
| `variacao_pontos` | Variação em pontos vs dia anterior | Momentum diário |
| `variacao_percentual` | Variação percentual | Comparação com outros ativos |

### 2. Volume e Liquidez ⭐ ALTO VALOR

| Campo | Descrição | Uso na Estratégia |
|-------|-----------|-------------------|
| `volume_contratos` | Total de contratos negociados | **Filtro de liquidez**: evitar dias de baixa liquidez |
| `volume_financeiro` | Valor financeiro total negociado | Calcular tamanho médio de ordem |
| `numero_negocios` | Quantidade de trades executados | **Densidade de mercado**: indica interesse real |
| `contratos_abertos` | Open Interest (posições em aberto) | **CRÍTICO**: sentiment de mercado e rollover |

### 3. Microestrutura de Mercado (quando disponível)

| Campo | Descrição | Uso na Estratégia |
|-------|-----------|-------------------|
| `spread_bid_ask` | Diferença entre melhor compra e venda | **Custo de transação**: slippage esperado |
| `melhor_bid` / `melhor_ask` | Topo do book de ofertas | Preço real de execução |
| `profundidade_bid` / `profundidade_ask` | Contratos disponíveis no topo | **Liquidez instantânea**: capacidade de execução |

### 4. Participação por Tipo de Investidor (similar ao COT Report)

| Campo | Descrição | Uso na Estratégia |
|-------|-----------|-------------------|
| `posicao_pessoa_fisica` | Posição líquida de pessoas físicas | **Sentiment contrário**: PF geralmente perde |
| `posicao_investidor_institucional` | Posição líquida de fundos/gestoras | **Smart money**: seguir os profissionais |
| `posicao_investidor_estrangeiro` | Posição líquida de estrangeiros | **Fluxo global**: correlação com mercados externos |
| `posicao_investidor_nao_residente` | Não residentes (offshore) | Pressão cambial e arbitragem |

## 🎯 Como os Dados Complementam as Estratégias

### 1. Filtro de Liquidez (ESSENCIAL)

**Problema**: Estratégias técnicas falham em dias de baixa liquidez devido a slippage excessivo.

**Solução com Boletim**:
```python
# Antes de gerar sinal, verificar liquidez do dia anterior
volume_relativo = volume_hoje / media_volume_20_dias

if volume_relativo < 0.7:
    # Liquidez baixa - não operar ou reduzir tamanho
    return None

if spread_bid_ask > 10:  # spread > 10 pontos
    # Spread muito alto - custo excessivo
    return None
```

**Impacto**: Reduz drasticamente operações em dias ruins, melhorando expectativa matemática.

### 2. Análise de Open Interest (CRÍTICO para Futuros)

**Conceito**: Open Interest (contratos em aberto) revela o "interesse real" do mercado.

**Padrões a Detectar**:
- **OI Crescente + Preço Subindo** = Tendência de alta forte (compra agressiva)
- **OI Crescente + Preço Caindo** = Tendência de baixa forte (venda agressiva)
- **OI Caindo + Preço Subindo** = Rali de short covering (fraco, evitar compras)
- **OI Caindo + Preço Caindo** = Liquidação de longs (fraco, evitar vendas)

**Implementação**:
```python
def analisar_open_interest(preco_atual, preco_anterior, oi_atual, oi_anterior):
    """Retorna força da tendência baseada em OI."""
    variacao_preco = (preco_atual - preco_anterior) / preco_anterior
    variacao_oi = (oi_atual - oi_anterior) / oi_anterior

    if variacao_preco > 0 and variacao_oi > 0:
        return "ALTA_FORTE"  # Boost em sinais de compra
    elif variacao_preco < 0 and variacao_oi > 0:
        return "BAIXA_FORTE"  # Boost em sinais de venda
    elif variacao_preco > 0 and variacao_oi < 0:
        return "RALI_FRACO"  # Penalizar sinais de compra
    elif variacao_preco < 0 and variacao_oi < 0:
        return "QUEDA_FRACA"  # Penalizar sinais de venda
```

### 3. Detecção de Rollover (ESPECÍFICO para Futuros)

**Problema**: Nas últimas semanas antes do vencimento, o volume migra para o próximo vencimento, gerando distorções.

**Solução com Boletim**:
```python
dias_ate_vencimento = (data_vencimento - data_pregao).days

if dias_ate_vencimento <= 10:
    # Calcular % do volume no contrato próximo vs atual
    volume_proximo = obter_volume_proximo_vencimento()
    volume_atual = volume_contratos

    percentual_proximo = volume_proximo / (volume_proximo + volume_atual)

    if percentual_proximo > 0.5:
        # Mercado já rolou - não operar contrato antigo
        return None
```

**Impacto**: Evita armadilhas de liquidez no final do vencimento.

### 4. Sentiment de Mercado (COT-like)

**Conceito**: Monitorar posicionamento de diferentes tipos de participantes.

**Estratégia Contrária (PF)**:
```python
# Pessoas físicas geralmente são "dumb money"
variacao_pf = posicao_pf_hoje - posicao_pf_ontem

if variacao_pf > limiar_positivo:
    # PF comprando muito = topo provável
    sentiment_score -= 0.3  # Penaliza sinais de compra

if variacao_pf < limiar_negativo:
    # PF vendendo muito = fundo provável
    sentiment_score += 0.3  # Favorece sinais de compra
```

**Estratégia de Seguimento (Institucionais)**:
```python
# Institucionais são "smart money"
variacao_inst = posicao_institucional_hoje - posicao_institucional_ontem

if variacao_inst > limiar_positivo:
    # Institucionais comprando = confirma sinal de alta
    sentiment_score += 0.4
```

### 5. Correlação com Fluxo Estrangeiro

**Conceito**: Estrangeiros movem o mercado devido ao volume.

```python
fluxo_estrangeiro = posicao_estrangeiro_hoje - posicao_estrangeiro_ontem

# Fluxo positivo (comprando) = pressão de alta
# Fluxo negativo (vendendo) = pressão de baixa

if abs(fluxo_estrangeiro) > limiar_significativo:
    # Ajustar stops e targets de acordo com fluxo
    if fluxo_estrangeiro > 0:
        tp2_atr_mult += 0.5  # Aumenta target em tendências fortes
    else:
        stop_atr_mult -= 0.2  # Aperta stop em tendências contrárias
```

## 📁 Estrutura de Armazenamento Padronizada

### Diretórios

```
backend/data/boletins_b3/
├── raw/                    # Arquivos originais da B3
│   ├── 2024-01/
│   │   ├── boletim_b3_2024-01-02.txt
│   │   ├── boletim_b3_2024-01-03.txt
│   │   └── ...
│   ├── 2024-02/
│   └── ...
└── processed/              # Dados processados (CSV/JSON)
    ├── 2024-01/
    └── ...
```

### Banco de Dados SQLite

**Tabela: `boletins_diarios`**
- Armazena todos os dados brutos dos boletins
- Índices em `(data_pregao, simbolo)` para consultas rápidas
- Constraint UNIQUE para evitar duplicatas

**Tabela: `metricas_microestrutura`**
- Armazena métricas calculadas (volume relativo, sentiment, etc.)
- Atualizada diariamente após importação do boletim
- Usada pelas estratégias para filtragem e ajustes

## 🔄 Workflow Diário Recomendado

1. **08:00** - Download automático do boletim do dia anterior
2. **08:05** - Parsing e importação para `boletins_diarios`
3. **08:10** - Cálculo de `metricas_microestrutura`
4. **09:00** - Estratégias consultam métricas antes da abertura
5. **09:05** - Geração de sinais com filtros de liquidez/sentiment
6. **18:00** - Revisão pós-pregão e atualização de estatísticas

## 🚀 Próximos Passos de Implementação

### Fase 1: Estrutura Base ✅ (Concluído)
- [x] Criar diretórios `raw/` e `processed/`
- [x] Criar tabelas `boletins_diarios` e `metricas_microestrutura`
- [x] Classe `GerenciadorBoletimB3` com métodos base

### Fase 2: Parser de Arquivos (Em Andamento)
- [ ] Identificar formato exato do boletim B3 (TXT posicional, CSV, PDF)
- [ ] Implementar parser para formato identificado
- [ ] Validação de dados importados
- [ ] Testes com histórico de 2024

### Fase 3: Cálculo de Métricas
- [ ] Implementar `calcular_metricas_microestrutura()` completo
- [ ] Volume relativo (✅ implementado)
- [ ] Liquidez score (spread + depth + volume)
- [ ] Sentiment COT (posicionamento por tipo)
- [ ] Risco rollover (dias até vencimento + % volume)

### Fase 4: Integração com Estratégias
- [ ] Adicionar filtros de liquidez em `motor_backtest.py`
- [ ] Criar `EstrategiaOIConfirmacao` (confirma sinais com OI)
- [ ] Adicionar sentiment score ao `EstrategiaEnsemble`
- [ ] Backtesting com e sem filtros de boletim (comparação)

### Fase 5: Automação
- [ ] Script de download diário via API B3 (se disponível) ou scraping
- [ ] Scheduler (cron/Task Scheduler) para execução às 08:00
- [ ] Notificações em caso de falha na importação
- [ ] Dashboard de monitoramento de qualidade de dados

## 📚 Referências

- **B3 - Séries Históricas**: https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/
- **Formato de Arquivos B3**: Layout posicional disponível no site (documentação técnica)
- **COT Report (EUA)**: https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm - inspiração para análise de posicionamento

## 💡 Exemplo de Uso Final

```python
from src.dados.boletim_b3 import GerenciadorBoletimB3
from src.backtest.motor_backtest import MotorBacktest

# Inicializar
gerenciador_boletim = GerenciadorBoletimB3()

# Obter métricas do dia
metricas = gerenciador_boletim.calcular_metricas_microestrutura("WIN", date.today())

# Aplicar filtros
if metricas['volume_relativo'] < 0.7:
    print("❌ Liquidez baixa - não operar hoje")
    exit()

if metricas['risco_rollover'] > 0.8:
    print("⚠️  Rollover iminente - usar próximo vencimento")
    exit()

# Ajustar estratégia com sentiment
if metricas['sentiment_cot'] > 0.5:
    print("📈 Smart money comprada - favorecer sinais de alta")
elif metricas['sentiment_cot'] < -0.5:
    print("📉 Smart money vendida - favorecer sinais de baixa")

# Executar backtest normalmente
motor = MotorBacktest(...)
motor.executar()
```
