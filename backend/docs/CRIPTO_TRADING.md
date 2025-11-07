# 📊 Análise de Trading de Criptoativos Individuais

## 🎯 Visão Geral

Sistema de **análise de trading focada** para criptoativos individuais, combinando três pilares de análise profissional:

1. **Análise Fundamentalista (AF)**: Notícias, correlações macro, sentimento
2. **Análise Técnica (AT)**: Momentum, estrutura de preço, suportes/resistências
3. **Análise On-Chain**: Netflow, baleias, funding rate, supply

**Objetivo:** Identificar **setups de alta probabilidade** com pontos precisos de entrada, alvos (Take Profit) e invalidação (Stop Loss).

---

## 🆚 Trading vs Carteira de Investimento

Esta análise é **complementar** ao sistema de Carteira Cripto (2 anos), mas com foco diferente:

| Aspecto | **Carteira** (Longo Prazo) | **Trading** (Curto Prazo) |
|---------|----------------------------|---------------------------|
| **Horizonte** | 2 anos (24-36 meses) | Dias a semanas (tático) |
| **Foco** | Diversificação (10 ativos) | Precisão (1 ativo) |
| **Output** | Alocação % + Projeção CMP | Entrada/TP1/TP2/TP3/Stop |
| **Análise** | AF + AT + CMP Modeling | AF + AT + On-Chain |
| **Métricas** | Market Cap, Múltiplos, ROI | Netflow, Whales, Funding |
| **Objetivo** | Crescimento patrimonial | Profit tático de swing |
| **Risco** | Volatilidade longo prazo | Stop Loss rigoroso |

**Quando usar cada um:**
- **Carteira**: "Quero investir R$10.000 em cripto por 2 anos"
- **Trading**: "BTC está em $100k, devo comprar agora? Onde vender?"

---

## 📚 Metodologia: 3 Pilares de Análise

### 1️⃣ Análise Fundamentalista (AF)

**Objetivo:** Avaliar o **contexto macro** e sentimento de mercado.

**Componentes:**

#### A. Notícias Recentes
- **Hard forks** (ex: Bitcoin Halving, Ethereum Dencun)
- **Parcerias estratégicas** (ex: LINK + SWIFT, Solana + Visa)
- **Desenvolvimentos técnicos** (ex: Firedancer 1M TPS, Celestia TIA mainnet)
- **Adoção institucional** (ex: ETF Bitcoin, MicroStrategy compras)

**Impacto:**
- Notícia positiva + momentum técnico = **Confluência COMPRA**
- Notícia negativa + fraqueza técnica = **Confluência VENDA**

#### B. Correlações Macro
**Ativos Monitorados:**
- **BTC**: Benchmark cripto (correlação 1.0 = espelho, 0.0 = independente)
- **ETH**: Plataforma dominante smart contracts
- **S&P 500** (^GSPC): Sentimento risk-on/risk-off
- **DXY** (Dollar Index): Força do dólar (inverso ao cripto)

**Interpretação:**
- Correlação BTC > 0.7 + BTC subindo = **ALTISTA**
- Correlação BTC > 0.7 + BTC caindo = **BAIXISTA**
- Correlação BTC < 0.3 = Movimento independente (fundamentalista forte)

#### C. Sentimento Macro
- **RISK_ON**: Bolsas subindo, DXY caindo, cripto em alta → Favorável
- **RISK_OFF**: Bolsas caindo, DXY subindo, cripto em baixa → Cauteloso
- **NEUTRO**: Sem direção clara → Aguardar confirmação

#### D. Momentum Fundamental
**Classificação:**
- **ALTISTA**: Notícias positivas + RISK_ON + retorno 30d > +10%
- **NEUTRO**: Mix de sinais ou retorno 30d entre -10% e +10%
- **BAIXISTA**: Notícias negativas + RISK_OFF + retorno 30d < -10%

---

### 2️⃣ Análise Técnica (AT)

**Objetivo:** Identificar **estrutura de preço** e pontos de entrada/saída.

**Componentes:**

#### A. Extremos de 30 Dias
- **Máxima 30d**: Resistência primária (topo recente)
- **Mínima 30d**: Suporte primário (fundo recente)
- **Range**: Volatilidade do período (máxima - mínima / mínima)

**Uso:**
- Preço próximo à **mínima** = Zona de compra potencial
- Preço próximo à **máxima** = Zona de venda potencial
- Range > 30% = Alta volatilidade (ajustar stops mais largos)

#### B. Médias Móveis (MAs)
- **MA 100 Dias**: Tendência de médio prazo
- **MA 200 Dias**: Tendência de longo prazo (não implementado ainda)

**Posição no Preço:**
- **ACIMA da MA 100**: Tendência de alta (bullish)
- **ABAIXO da MA 100**: Tendência de baixa (bearish)
- **PROXIMA da MA 100**: Zona de decisão (aguardar breakout)

#### C. Suportes e Resistências
**Suportes** (níveis de demanda):
1. Mínima 30d (suporte principal)
2. Mínima 30d - 5% (suporte secundário)
3. Mínima 30d - 10% (suporte forte)

**Resistências** (níveis de oferta):
1. 95% da Máxima 30d (resistência iminente)
2. Máxima 30d (resistência principal)
3. Máxima 30d + 5% (resistência psicológica)

**Uso:**
- **COMPRA**: Entrada próximo a suportes, alvos em resistências
- **VENDA**: Entrada próximo a resistências, alvos em suportes

#### D. Pontos Críticos de Invalidação
- **Ponto Crítico Baixa**: Perda deste suporte invalida tese **bullish** (ex: Mínima 30d - 5%)
- **Ponto Crítico Alta**: Rompimento desta resistência invalida tese **bearish** (ex: Máxima 30d + 2%)

**Uso para Stop Loss:**
- Setup COMPRA: Stop abaixo do **Ponto Crítico Baixa**
- Setup VENDA: Stop acima do **Ponto Crítico Alta**

#### E. Momentum Técnico
**Classificação:**
- **ALTISTA**: Preço ACIMA MA 100 + distância da mínima > 15%
- **NEUTRO**: Preço PRÓXIMO MA 100 ou no meio do range
- **BAIXISTA**: Preço ABAIXO MA 100 + distância da máxima > 15%

---

### 3️⃣ Análise On-Chain (Validação)

**Objetivo:** Validar/invalidar teses técnicas com **dados on-chain**.

⚠️  **NOTA IMPORTANTE**: Atualmente usando **mock patterns** baseados em price action. Para produção, integrar com:
- **Glassnode API** (pago ~$50/mês): Dados profissionais
- **CryptoQuant** (free tier): Métricas limitadas
- **Binance/Bybit API** (gratuito): Funding rates

**Componentes:**

#### A. Netflow de Exchanges
**Definição:** Fluxo líquido de entrada/saída de exchanges centralizadas.

- **INFLOW** (entrada): Tokens entrando em exchanges
  - **Interpretação:** Pressão de **venda** (holders movendo para vender)
  - **Impacto:** Bearish curto prazo

- **OUTFLOW** (saída): Tokens saindo de exchanges
  - **Interpretação:** **Acumulação** (holders movendo para cold wallets)
  - **Impacto:** Bullish médio prazo (redução de oferta disponível)

**Exemplo BTC:**
- Outflow de 10.000 BTC/dia por 7 dias = Forte acumulação institucional

#### B. Whale Accumulation (Baleias)
**Definição:** Movimentação de endereços com grandes holdings (ex: > 1.000 BTC).

- **ACUMULANDO**: Baleias comprando
  - **Interpretação:** Smart money bullish
  - **Impacto:** Suporte de preço, tendência de alta

- **DISTRIBUINDO**: Baleias vendendo
  - **Interpretação:** Smart money realizando lucros
  - **Impacto:** Pressão de venda, cautela

- **NEUTRO**: Sem movimento significativo

**Fontes:** Whale Alert, Santiment, Glassnode

#### C. Funding Rate (Taxa de Financiamento)
**Definição:** Taxa paga entre traders long e short em contratos perpétuos.

- **Funding Rate Positivo** (> +0.02%):
  - **Interpretação:** Excesso de **longs** (overleveraged)
  - **Impacto:** Risco de **long squeeze** (liquidações forçadas) → Bearish

- **Funding Rate Negativo** (< -0.02%):
  - **Interpretação:** Excesso de **shorts** (overleveraged)
  - **Impacto:** Oportunidade de **short squeeze** → Bullish

- **Funding Rate Neutro** (-0.01% a +0.01%):
  - **Interpretação:** Mercado balanceado

**Exemplo:**
- BTC com funding +0.05% por 3 dias = Mercado sobreaquecido, cautela

**Fontes:** Binance API, Bybit API, Coinglass

#### D. Supply nas Exchanges
**Definição:** % do supply total de um token em exchanges centralizadas.

- **DIMINUINDO**: Supply saindo de exchanges
  - **Interpretação:** HODLing, long-term holders aumentando
  - **Impacto:** **Supply shock** potencial → Bullish

- **AUMENTANDO**: Supply entrando em exchanges
  - **Interpretação:** Holders movendo para vender
  - **Impacto:** Oferta aumentando → Bearish

**Exemplo ETH:**
- Supply em exchanges de 15% → 10% em 6 meses = Forte HODLing pós-staking

**Fontes:** Glassnode, CryptoQuant

#### E. Conclusão On-Chain
Síntese dos 4 indicadores acima em uma **conclusão direcional**:

- "Absorção de oferta por baleias, pressure buying crescente" → **BULLISH**
- "Pressure selling de baleias, cautela no curto prazo" → **BEARISH**
- "Dados on-chain limitados, análise baseada em AT/AF" → **NEUTRO**

---

## 🎯 Output: Relatório de Trading

### Estrutura do Relatório (3 Partes)

#### **Parte 1: Resumo Executivo**

Tabela com decisão rápida:

| Categoria | Descrição |
|-----------|-----------|
| **OPERAÇÃO RECOMENDADA** | **[COMPRA]**, **[VENDA]** ou **[AGUARDAR]** |
| **Momentum Consolidado** | Ex: "Neutro curto prazo, Altista médio prazo" |
| **Risco/Recompensa (R/R)** | Ex: "1:2.8" (para cada R$1 de risco, R$2.80 de recompensa) |

**Interpretação:**
- **COMPRA**: Score total ≥ 5 pontos (AF + AT + On-Chain favoráveis)
- **VENDA**: Score total ≤ -5 pontos (AF + AT + On-Chain desfavoráveis)
- **AGUARDAR**: Score total entre -4 e +4 (sinais mistos)

---

#### **Parte 2: Análises Detalhadas**

**A. Análise Fundamentalista e Correlação:**
- Momentum Fundamental (BAIXISTA/NEUTRO/ALTISTA)
- Notícias recentes (3-5 headlines)
- Correlações: BTC (X.XX), ETH (X.XX)
- Sentimento macro (RISK_ON/RISK_OFF/NEUTRO)

**B. Análise Técnica e Estrutura de Preço:**
- Momentum Técnico (BAIXISTA/NEUTRO/ALTISTA)
- Extremos 30d: Máxima ($XXX), Mínima ($XXX), Range (XX%)
- MA 100D: $XXX (ACIMA/ABAIXO/PROXIMA)
- Níveis críticos:
  - Suportes: $XX, $XX, $XX
  - Resistências: $XX, $XX, $XX
  - Pontos de invalidação: $XX (baixa), $XX (alta)

**C. Análise On-Chain e Sentimento de Mercado:**
- Netflow: INFLOW/OUTFLOW (interpretação)
- Whale Accumulation: ACUMULANDO/DISTRIBUINDO/NEUTRO
- Funding Rate: X.XXX% (overleveraged longs/shorts/balanceado)
- Supply Exchanges: AUMENTANDO/DIMINUINDO/ESTAVEL
- Conclusão: Síntese direcional

---

#### **Parte 3: Plano de Operação Refinado**

Tabela com pontos de execução:

| Detalhe da Operação | Valor (USDT) | Justificativa Refinada |
|---------------------|--------------|------------------------|
| **PREÇO DE ENTRADA** | **$XX,XXX.XX** | "Zona de consolidação próxima ao suporte $XX,XXX. On-chain: [conclusão]..." |
| **ALVO 1 (Take Profit)** | $XX,XXX.XX | "Resistência imediata / Retração Fibonacci 0.382" |
| **ALVO 2 (Take Profit)** | $XX,XXX.XX | "Máxima 30d / Retração Fibonacci 0.618" |
| **ALVO 3 (Take Profit)** | $XX,XXX.XX | "Zona psicológica / Extensão Fibonacci 1.272" |
| **INVALIDAÇÃO (Stop Loss)** | **$XX,XXX.XX** | "Perda do suporte $XX,XXX invalida tese bullish" |

**Cálculo do R/R:**
- Risco = Entrada - Stop Loss
- Recompensa (Alvo 2) = Alvo 2 - Entrada
- R/R = Recompensa / Risco

**Exemplo:**
- Entrada: $100.000
- Stop: $95.000 → Risco = $5.000
- Alvo 2: $115.000 → Recompensa = $15.000
- **R/R = 15.000 / 5.000 = 1:3**

---

## 🖥️  Como Usar

### Instalação

```bash
# Backend já deve estar instalado
cd backend
```

### Comandos CLI

#### 1. Analisar um par individual

```bash
python consultar_trading_cripto.py analisar BTCUSDT
```

**Output:**
- Relatório completo markdown (3 partes)
- Arquivo salvo em `backend/relatorios_trading/BTCUSDT_YYYYMMDD_HHMMSS.md`

#### 2. Monitorar múltiplos pares

```bash
python consultar_trading_cripto.py monitorar BTCUSDT ETHUSDT SOLUSDT
```

**Output:**
- Tabela consolidada com operações recomendadas
- Estatísticas: X COMPRAS, Y VENDAS, Z AGUARDAR
- Melhor oportunidade destacada

#### 3. Buscar oportunidades automaticamente

```bash
python consultar_trading_cripto.py oportunidades
```

**Output:**
- Análise de 5 pares principais (BTC, ETH, SOL, BNB, ADA)
- Tabela de oportunidades rankeada
- Melhor setup de COMPRA/VENDA

---

## 📈 Exemplos Práticos

### Exemplo 1: Setup de COMPRA (BTC)

**Contexto:**
- BTC caiu de $123k para $103k em 30 dias
- Notícias: ETF aprovado, halving concluído
- On-Chain: OUTFLOW de exchanges, baleias acumulando

**Análise:**
- **AF:** BAIXISTA (retorno -16% em 30d)
- **AT:** NEUTRO (no meio do range, próximo à MA 100)
- **On-Chain:** BULLISH (outflow + accumulation + funding neutro)
- **Score Total:** -3 + 1 + 4 = **+2 pontos** → **COMPRA** (momentum neutro ST, altista MT)

**Operação:**
- **Entrada:** $103,622 (perto da mínima $101,590)
- **Alvo 1:** $117,187 (resistência imediata)
- **Alvo 2:** $123,355 (máxima 30d)
- **Alvo 3:** $129,523 (extensão +5%)
- **Stop:** $96,511 (abaixo da mínima -5%)
- **R/R:** 1:2.8

**Justificativa:**
- Correção saudável após rally
- Fundamentos intactos (ETF, halving)
- On-chain mostra acumulação institucional
- Suporte técnico forte na mínima

---

### Exemplo 2: Setup de VENDA (SOL)

**Contexto:**
- SOL subiu de $147 para $229 em 30 dias
- Notícias: Firedancer testnet lançada
- On-Chain: INFLOW em exchanges, baleias distribuindo

**Análise:**
- **AF:** ALTISTA (retorno +56% em 30d)
- **AT:** ALTISTA (acima MA 100, próximo da máxima)
- **On-Chain:** BEARISH (inflow + distribuição + funding negativo)
- **Score Total:** +3 + 3 + (-4) = **+2 pontos** → Conflito

**Decisão:** **VENDA** (on-chain sugere realização de lucros)

**Operação:**
- **Entrada:** $224.52 (rejeição da máxima $229)
- **Alvo 1:** $147.63 (mínima 30d)
- **Alvo 2:** $140.25 (suporte -5%)
- **Alvo 3:** $133.17 (suporte -10%)
- **Stop:** $233.68 (rompimento da máxima +2%)
- **R/R:** 1:8.4 (altíssimo, mas risco de fake breakout)

**Justificativa:**
- Rally forte, provável correção técnica
- Baleias distribuindo (smart money saindo)
- Funding negativo (excesso de shorts, mas confirmando bearish)
- Resistência técnica forte na máxima

---

## ⚠️  Limitações e Avisos

### Limitações Técnicas

1. **Dados On-Chain Mock:**
   - Atualmente usando **heurísticas** baseadas em price action
   - Para produção: Integrar Glassnode/CryptoQuant APIs
   - Dados reais têm custo (~$50-200/mês)

2. **Notícias Não Automatizadas:**
   - Database manual de notícias por ativo
   - Para automação: Integrar CryptoPanic API, Google News RSS

3. **Correlações Simplificadas:**
   - Correlação BTC calculada em janela 30d
   - Ideal: Múltiplas janelas (7d, 30d, 90d) + correlação rolling

4. **Pares Limitados:**
   - 10 pares suportados atualmente
   - Expansão futura: Top 50 por market cap

### Avisos de Uso

⚠️  **DISCLAIMER LEGAL:**
- Esta análise é **apenas educacional**
- **NÃO constitui recomendação de investimento**
- Criptomoedas envolvem **alto risco** de perda total
- **Sempre faça sua própria pesquisa (DYOR)**
- Nunca invista mais do que pode perder

🎓 **Boas Práticas:**
- Sempre use **stop loss** (não negocie sem proteção)
- **Dimensione posição** adequadamente (ex: 1-5% do capital por trade)
- **Take profits parciais** (ex: 33% no TP1, 33% no TP2, 33% no TP3)
- **Trailing stop** após TP1 (proteger lucros)
- **Diário de trading** (registrar todas as operações)

---

## 🔧 Roadmap de Melhorias

### Curto Prazo (Q1 2025)
- [ ] Integração Glassnode API (on-chain real)
- [ ] Automação de notícias (CryptoPanic API)
- [ ] Suporte a 20 pares adicionais
- [ ] Alertas de entrada via Telegram/Discord

### Médio Prazo (Q2 2025)
- [ ] Backtesting de sinais históricos
- [ ] Dashboard Streamlit (visualização interativa)
- [ ] Integração com exchanges (Binance API para execução)
- [ ] Machine Learning (predição de R/R real)

### Longo Prazo (Q3-Q4 2025)
- [ ] Trading automatizado (grid trading, DCA)
- [ ] Portfolio management (múltiplas operações simultâneas)
- [ ] Risk management avançado (correlação entre trades)
- [ ] Mobile app (iOS/Android)

---

## 📚 Referências e Estudo

### Análise Técnica
- "Technical Analysis of the Financial Markets" - John Murphy
- "Trading in the Zone" - Mark Douglas
- TradingView (charts e indicadores)

### Análise On-Chain
- Glassnode Academy: https://academy.glassnode.com/
- CryptoQuant Blog: https://cryptoquant.com/blog
- Whale Alert: https://whale-alert.io/

### Sentimento de Mercado
- Crypto Fear & Greed Index: https://alternative.me/crypto/fear-and-greed-index/
- Santiment: https://santiment.net/
- LunarCrush: https://lunarcrush.com/

### Correlações Macro
- TradingView: Comparação BTC vs S&P 500, DXY
- Glassnode Studio: Correlações customizadas
- CoinMetrics: Dados institucionais

---

## 💡 Dicas de Especialista

### Timing de Entrada
1. **Confluência de sinais**: Espere AF + AT + On-Chain alinhados
2. **Paciência**: Aguarde preço chegar na zona de entrada (não FOMO)
3. **Volume**: Valide com volume acima da média 30d
4. **Timeframes**: Confirme em múltiplos timeframes (4h, 1d, 1w)

### Gestão de Risco
1. **Stop Loss Inviolável**: Nunca mova stop para baixo (long) ou para cima (short)
2. **Position Sizing**: Risco máximo 1-2% do capital por trade
3. **Correlação**: Não abra 5 trades em ativos correlacionados (ex: 5 altcoins)
4. **Drawdown Máximo**: Pare de tradear após -10% do capital no mês

### Psicologia de Trading
1. **Discipline Over Emotion**: Siga o plano, ignore FOMO/FUD
2. **Journal**: Registre TODAS as operações (winners e losers)
3. **Review Semanal**: Analise erros e acertos
4. **Breaks**: Não trade após 3 losses consecutivos (reset mental)

---

**Última atualização:** 2025-01-05
**Versão:** 1.0.0
**Status:** ✅ Operacional (mock on-chain data)
