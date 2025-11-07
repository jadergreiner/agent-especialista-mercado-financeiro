# 🔗 Correlações do WIN (Mini Índice Bovespa)

## 📊 Correlações Principais

### 1️⃣ Correlação DIRETA (Positiva Forte)

#### IBOV (Ibovespa à Vista)
- **Correlação**: +0.98 a +0.99 (quase perfeita)
- **Motivo**: WIN é derivativo do Ibovespa
- **Uso**: Divergências WIN vs IBOV indicam oportunidades de arbitragem
- **Symbol**: ^BVSP (Yahoo Finance)

#### WDO (Mini Dólar Futuro)
- **Correlação**: -0.70 a -0.85 (inversa forte)
- **Motivo**: Dólar forte → empresas exportadoras ganham, mas investimento estrangeiro diminui
- **Uso**: Dólar subindo forte → WIN tende a cair (risk-off)
- **Symbol**: BRL=X ou USDBRL=X

#### DOL (Dólar Futuro Cheio)
- **Correlação**: -0.70 a -0.85 (inversa forte)
- **Motivo**: Mesmo que WDO, mas contrato cheio
- **Uso**: Mesma lógica do WDO
- **Symbol**: DI1! (Bloomberg) ou via B3

### 2️⃣ Correlação INDIRETA (Positiva Moderada)

#### S&P 500
- **Correlação**: +0.60 a +0.75
- **Motivo**: Risco global → bolsas emergentes seguem EUA
- **Uso**: S&P subindo → WIN tende a subir (risk-on)
- **Symbol**: ^GSPC (Yahoo Finance)

#### Dow Jones
- **Correlação**: +0.55 a +0.70
- **Motivo**: Similar ao S&P 500
- **Uso**: Sentimento de mercado americano
- **Symbol**: ^DJI (Yahoo Finance)

#### NASDAQ
- **Correlação**: +0.50 a +0.65
- **Motivo**: Tech → menos correlação com commodities brasileiras
- **Uso**: Inovação e tech driving
- **Symbol**: ^IXIC (Yahoo Finance)

#### VIX (Índice de Volatilidade)
- **Correlação**: -0.40 a -0.60 (inversa moderada)
- **Motivo**: VIX alto → medo → fuga de emergentes
- **Uso**: VIX > 25 → WIN sob pressão vendedora
- **Symbol**: ^VIX (Yahoo Finance)

### 3️⃣ Correlação por COMMODITIES

#### Petróleo (WTI/Brent)
- **Correlação**: +0.40 a +0.60
- **Motivo**: Petrobras ~10% do Ibovespa
- **Uso**: Petróleo subindo → PETR3/PETR4 sobem → WIN sobe
- **Symbol**: CL=F (WTI) ou BZ=F (Brent)

#### Minério de Ferro
- **Correlação**: +0.50 a +0.70
- **Motivo**: Vale ~15% do Ibovespa
- **Uso**: Minério subindo → VALE3 sobe → WIN sobe
- **Symbol**: Não tem símbolo direto, usar VALE3.SA como proxy

#### Soja
- **Correlação**: +0.30 a +0.50
- **Motivo**: Agronegócio importante na economia BR
- **Uso**: Safra boa → dólar entra → bolsa sobe
- **Symbol**: ZS=F (CBOT Soybean Futures)

### 4️⃣ Correlação SETORIAL (Ações Peso-Pesado)

#### PETR4 (Petrobras PN)
- **Peso no Ibovespa**: ~8-10%
- **Correlação**: +0.75 a +0.85
- **Symbol**: PETR4.SA

#### VALE3 (Vale ON)
- **Peso no Ibovespa**: ~12-15%
- **Correlação**: +0.80 a +0.90
- **Symbol**: VALE3.SA

#### ITUB4 (Itaú PN)
- **Peso no Ibovespa**: ~7-9%
- **Correlação**: +0.70 a +0.80
- **Symbol**: ITUB4.SA

#### BBDC4 (Bradesco PN)
- **Peso no Ibovespa**: ~4-6%
- **Correlação**: +0.65 a +0.75
- **Symbol**: BBDC4.SA

#### B3SA3 (B3 ON)
- **Peso no Ibovespa**: ~3-5%
- **Correlação**: +0.70 a +0.80
- **Symbol**: B3SA3.SA

### 5️⃣ Correlação MACRO (Indicadores)

#### Taxa Selic / DI Futuro
- **Correlação**: -0.30 a -0.50 (inversa fraca)
- **Motivo**: Juros altos → renda fixa compete com bolsa
- **Uso**: Expectativa de corte de juros → WIN tende a subir
- **Symbol**: DI1F25, DI1F26 (B3)

#### Spread CDS Brasil (Risco País)
- **Correlação**: -0.50 a -0.70 (inversa moderada)
- **Motivo**: CDS alto → risco Brasil alto → fuga de capital
- **Uso**: CDS caindo → WIN tende a subir

#### EWZ (ETF Brasil nos EUA)
- **Correlação**: +0.85 a +0.95 (forte)
- **Motivo**: Replica ações brasileiras em dólar
- **Uso**: Fluxo estrangeiro, sentimento gringo sobre Brasil
- **Symbol**: EWZ (NYSE)

---

## 📈 Ativos para Coletar Cotações

### Prioridade ALTA (Essenciais)

| Ativo | Symbol | Fonte | Motivo |
|-------|--------|-------|--------|
| **Ibovespa** | ^BVSP | Yahoo Finance | Correlação 0.99 - essencial |
| **Dólar** | USDBRL=X | Yahoo Finance | Correlação -0.80 - essencial |
| **S&P 500** | ^GSPC | Yahoo Finance | Indicador risk-on/off |
| **VIX** | ^VIX | Yahoo Finance | Medo do mercado |
| **Petróleo WTI** | CL=F | Yahoo Finance | Afeta PETR (10% Ibov) |
| **VALE3** | VALE3.SA | Yahoo Finance | 15% do Ibovespa |
| **PETR4** | PETR4.SA | Yahoo Finance | 10% do Ibovespa |

### Prioridade MÉDIA (Importantes)

| Ativo | Symbol | Fonte | Motivo |
|-------|--------|-------|--------|
| **Dow Jones** | ^DJI | Yahoo Finance | Mercado americano |
| **NASDAQ** | ^IXIC | Yahoo Finance | Tech sentiment |
| **Petróleo Brent** | BZ=F | Yahoo Finance | Alternativa ao WTI |
| **ITUB4** | ITUB4.SA | Yahoo Finance | 8% do Ibovespa |
| **BBDC4** | BBDC4.SA | Yahoo Finance | 5% do Ibovespa |
| **B3SA3** | B3SA3.SA | Yahoo Finance | 4% do Ibovespa |
| **EWZ** | EWZ | Yahoo Finance | Fluxo gringo |

### Prioridade BAIXA (Complementares)

| Ativo | Symbol | Fonte | Motivo |
|-------|--------|-------|--------|
| **Minério Ferro** | Usar VALE3 | - | Proxy via Vale |
| **Soja** | ZS=F | Yahoo Finance | Agro |
| **Ouro** | GC=F | Yahoo Finance | Safe haven |
| **Bitcoin** | BTC-USD | Yahoo Finance | Risk-on extremo |
| **10Y Treasury** | ^TNX | Yahoo Finance | Juros EUA |

---

## 🔄 Estratégias de Correlação

### 1. Divergência WIN vs IBOV
```python
# Se WIN está subindo menos que IBOV → oportunidade de compra WIN
# Se WIN está subindo mais que IBOV → oportunidade de venda WIN

divergencia = (variacao_win - variacao_ibov)

if divergencia < -0.5:  # WIN 0.5% abaixo do IBOV
    sinal = "COMPRA"  # WIN deve convergir
elif divergencia > 0.5:  # WIN 0.5% acima do IBOV
    sinal = "VENDA"  # WIN deve convergir
```

### 2. Dólar vs WIN (Risk-On/Off)
```python
# Dólar subindo + WIN caindo = risk-off confirmado
# Dólar caindo + WIN subindo = risk-on confirmado

if variacao_dolar > 1.0 and variacao_win < 0:
    sentimento = "RISK_OFF"  # Evitar LONG
elif variacao_dolar < -1.0 and variacao_win > 0:
    sentimento = "RISK_ON"  # Favorável LONG
```

### 3. S&P 500 + VIX (Confirmação)
```python
# S&P subindo + VIX caindo = risk-on forte
# S&P caindo + VIX subindo = risk-off forte

if variacao_sp500 > 0.5 and vix < 20:
    ambiente = "BULLISH"  # Favorável para WIN
elif variacao_sp500 < -0.5 and vix > 25:
    ambiente = "BEARISH"  # Desfavorável para WIN
```

### 4. Commodities (Petróleo + Vale)
```python
# Commodities subindo = WIN tende a subir

commodities_score = (
    variacao_petroleo * 0.4 +  # Peso Petrobras
    variacao_vale * 0.6         # Peso Vale
)

if commodities_score > 2.0:
    boost = 1.2  # Aumentar target em 20%
elif commodities_score < -2.0:
    boost = 0.8  # Reduzir target em 20%
```

---

## 📊 Matriz de Correlação (Exemplo)

```
                WIN    IBOV   DÓLAR   S&P   VIX   PETR   VALE
WIN            1.00   0.99  -0.80   0.70 -0.50  0.80   0.85
IBOV           0.99   1.00  -0.78   0.68 -0.48  0.82   0.88
DÓLAR         -0.80  -0.78   1.00  -0.55  0.60 -0.65  -0.70
S&P 500        0.70   0.68  -0.55   1.00 -0.75  0.50   0.55
VIX           -0.50  -0.48   0.60  -0.75  1.00 -0.40  -0.45
PETR4          0.80   0.82  -0.65   0.50 -0.40  1.00   0.70
VALE3          0.85   0.88  -0.70   0.55 -0.45  0.70   1.00
```

**Interpretação**:
- **+0.80 a +1.00**: Correlação muito forte
- **+0.60 a +0.80**: Correlação forte
- **+0.40 a +0.60**: Correlação moderada
- **+0.20 a +0.40**: Correlação fraca
- **-0.20 a +0.20**: Sem correlação
- **Negativo**: Correlação inversa

---

## 🎯 Casos de Uso

### Caso 1: Filtro Pré-Operação
```python
# Verificar se ambiente macro está favorável

dolar_subindo_forte = variacao_dolar > 1.5
vix_alto = vix_atual > 25
sp500_caindo = variacao_sp500 < -1.0

if dolar_subindo_forte and vix_alto and sp500_caindo:
    print("⚠️ AMBIENTE DESFAVORÁVEL - Evitar LONG")
    pode_operar = False
```

### Caso 2: Confirmação de Sinal
```python
# Sinal técnico + correlações confirmam

sinal_tecnico = "COMPRA"

# Verificar correlações
ibov_subindo = variacao_ibov > 0.5
dolar_caindo = variacao_dolar < -0.5
commodities_positivas = (variacao_petroleo + variacao_vale) > 0

confirmacoes = sum([ibov_subindo, dolar_caindo, commodities_positivas])

if confirmacoes >= 2:
    print("✅ Sinal confirmado por correlações")
    executar_ordem()
```

### Caso 3: Ajuste de Target
```python
# Expandir/reduzir target baseado em correlações

score_correlacao = (
    (1 if variacao_ibov > 0 else -1) * 0.4 +
    (1 if variacao_dolar < 0 else -1) * 0.3 +
    (1 if variacao_sp500 > 0 else -1) * 0.2 +
    (1 if vix_atual < 20 else -1) * 0.1
)

if score_correlacao > 0.5:
    target = target_base * 1.3  # Ambiente muito favorável
elif score_correlacao < -0.5:
    target = target_base * 0.7  # Ambiente desfavorável
```

---

## 📝 Próximos Passos

1. **Criar módulo de coleta multi-ativo** ✅ Próximo
   - `src/dados/coletor_correlacoes.py`
   - Usar yfinance para pegar cotações
   - Salvar em tabela `cotacoes_correlacoes`

2. **Calcular matriz de correlação dinâmica**
   - Correlação rolante (30d, 90d, 365d)
   - Detectar mudanças de regime (correlação mudando)

3. **Integrar com estratégias**
   - Filtro de ambiente macro
   - Confirmação via correlações
   - Ajuste de targets/stops

4. **Dashboard de correlações**
   - Heatmap de correlação
   - Gráfico de dispersão WIN vs IBOV
   - Alertas de divergência

---

**Criado**: 05/11/2025
**Versão**: 1.0
