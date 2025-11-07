# Backend - Agent Especialista Mercado Financeiro

Backend Python para análise de mercado financeiro global.

## 🚀 Módulos Implementados

### 1️⃣ Monitor Forex e Cripto (42 Pares)
Análise em tempo real de pares Forex e Cripto com 5 pilares (BCs, Técnico, Correlações, Sentimento, Confluência).

📄 Arquivo: `src/dados/monitor_forex.py`

### 2️⃣ Análise de Dividendos (Ações B3)
Sistema de análise de ações com foco em **sustentabilidade de dividendos**.

📄 Arquivo: `src/dados/analisador_dividendos.py`
📘 Documentação: `docs/DIVIDENDOS_ANALISE.md`
🖥️  CLI: `consultar_dividendos.py`

**Metodologia:**
- **Sustentabilidade (40%)**: Crescimento LPA, consistência dividendos, lucratividade
- **Saúde (35%)**: Liquidez corrente, geração de caixa
- **Valor (25%)**: Margem de segurança, DY, P/L

**Comandos:**
```bash
# Analisar ações individuais
python consultar_dividendos.py analisar TGMA3 GOAU4 GGBR4

# Ranking com top 3
python consultar_dividendos.py ranking TGMA3 GOAU4 KLBN11 --top 3

# Analisar setores
python consultar_dividendos.py setor siderurgia
```

### 3️⃣ Análise de FIIs (Fundos Imobiliários)
Sistema de análise de FIIs com diferenciação **Tijolo vs Papel vs FOF**.

📄 Arquivo: `src/dados/analisador_fiis.py`
🖥️  CLI: `consultar_fiis.py`

**Metodologia:**
- **Qualidade (40%)**: Vacância (Tijolo) ou Indexadores (Papel), diversificação
- **Valuation (35%)**: P/VP, desconto/prêmio
- **Rendimento (25%)**: DY 12M, consistência

**Diferenciação:**
- **Tijolo**: Foco em vacância física/financeira (ex: logística, lajes corporativas)
- **Papel**: Foco em indexadores (IPCA+, IGP-M, CDI) para CRIs/CRAs
- **FOF**: Avaliação híbrida

**Comandos:**
```bash
# Analisar FIIs
python consultar_fiis.py analisar KNRI11 MXRF11 HGLG11

# Comparar 2 FIIs
python consultar_fiis.py comparar KNRI11 HGLG11

# Ranking
python consultar_fiis.py ranking KNRI11 MXRF11 HGLG11 VISC11 --top 2

# Setor específico
python consultar_fiis.py setor logistica
```

### 4️⃣ Carteira Cripto (10 Ativos - 2 Anos)
Sistema de análise de carteira cripto com **projeções de Market Cap** e diversificação.

📄 Arquivo: `src/dados/analisador_carteira_cripto.py`

**Metodologia:**
- **Fundamentos (40%)**: Utility score + Adoption score
- **Técnico (30%)**: Volatilidade, ranges, price zones
- **Modelagem CMP (30%)**: Market Cap Projection → Múltiplo de retorno

**Categorização:**
- **Blue Chips (40%)**: BTC, ETH (25% cada)
- **Infrastructure (21%)**: LINK, SOL (11.1% cada)
- **Growth Bets (39%)**: TIA, KAS, AAVE (8.9-10% cada)

**Projeções Conservadoras (2 anos):**
- BTC: $2T (1.0x) - Store of value maduro
- ETH: $1T (2.4x) - Plataforma dominante smart contracts
- SOL: $200B (2.2x) - High throughput (65k TPS)
- LINK: $50B (4.7x) - Padrão oracle + RWA
- TIA: $25B (36.8x) - Modular blockchain revolution
- KAS: $15B (12.1x) - BlockDAG innovation

**Teste:**
```bash
python backend\src\dados\analisador_carteira_cripto.py
```

**Resultado:** R$100 → R$682 em 2 anos (6.82x retorno ponderado)

### 5️⃣ Trading Cripto Individual (AF+AT+On-Chain) 🆕
**Relatório de trading focado** para criptoativos individuais com análise integrada.

📄 Arquivo: `src/dados/analisador_trading_cripto.py`
📘 Documentação: `docs/CRIPTO_TRADING.md` (em desenvolvimento)
🖥️  CLI: `consultar_trading_cripto.py`

**Metodologia (3 Pilares):**

**A. Análise Fundamentalista (AF):**
- Notícias recentes (upgrades, parcerias, hard forks)
- Correlações macro (BTC, ETH, S&P 500, DXY)
- Sentimento de mercado (RISK_ON, RISK_OFF, NEUTRO)
- Momentum fundamental (BAIXISTA, NEUTRO, ALTISTA)

**B. Análise Técnica (AT):**
- Extremos 30 dias (máximas, mínimas, range)
- Médias Móveis (MA 100D, MA 200D)
- Posição no range (ACIMA, ABAIXO, PROXIMA)
- Suportes e resistências (níveis críticos)
- Momentum técnico (estrutura de preço)

**C. Análise On-Chain (Validação):**
- **Netflow de Exchanges**: INFLOW (pressão venda) vs OUTFLOW (acumulação)
- **Whale Accumulation**: ACUMULANDO vs DISTRIBUINDO (smart money)
- **Funding Rate**: % positivo (longs dominam) vs negativo (shorts dominam)
- **Supply nas Exchanges**: AUMENTANDO (oferta) vs DIMINUINDO (escassez)
- **Conclusão**: Absorção de volatilidade, pressão direcional

**Output (3 Partes):**
1. **Resumo Executivo**: OPERAÇÃO (COMPRA/VENDA/AGUARDAR), Momentum Consolidado, R/R ratio
2. **Análises Detalhadas**: Seções AF, AT, On-Chain completas
3. **Plano de Operação**: Entrada + TP1/TP2/TP3 + Stop Loss (com justificativas técnicas)

**Comandos:**
```bash
# Analisar um par individual
python consultar_trading_cripto.py analisar BTCUSDT

# Monitorar múltiplos pares
python consultar_trading_cripto.py monitorar BTCUSDT ETHUSDT SOLUSDT

# Buscar oportunidades automaticamente (5 pares principais)
python consultar_trading_cripto.py oportunidades
```

**Pares Suportados:**
- BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, ADAUSDT
- DOTUSDT, AVAXUSDT, LINKUSDT, MATICUSDT, NEARUSDT

**Exemplo de Output:**
```markdown
🎯 RELATÓRIO DE TRADING FOCADO: BTCUSDT

| Categoria | Descrição |
|-----------|-----------|
| OPERAÇÃO RECOMENDADA | [COMPRA] |
| Momentum Consolidado | Neutro curto prazo, Altista médio prazo |
| Risco/Recompensa | 1:2.8 |

PLANO DE OPERAÇÃO:
- PREÇO DE ENTRADA: $103,622.33
- ALVO 1: $117,187.12 (Resistência imediata)
- ALVO 2: $123,354.87 (Máxima 30d)
- ALVO 3: $129,522.61 (Swing médio prazo)
- STOP LOSS: $96,511.00 (Invalidação bullish)
```

**Diferença vs Carteira Cripto:**
| Aspecto | Carteira | Trading |
|---------|----------|---------|
| Horizonte | 2 anos (24-36 meses) | Dias/semanas (tático) |
| Ativos | 10 (diversificação) | 1 (precisão) |
| Output | Alocação % + CMP | Entrada/TPs/Stop |
| Análise | AF + AT + CMP Modeling | AF + AT + On-Chain |
| Métricas | Múltiplos, projeções | Netflow, whales, funding |
| Objetivo | Crescimento longo prazo | Profit tático curto prazo |

**Notas Sobre On-Chain:**
⚠️  Atualmente usando **mock patterns** baseados em price action. Para dados reais, considerar integração com:
- **Glassnode API** (pago ~$50/mês): Netflow, whale data, supply
- **CryptoQuant** (free tier): Métricas limitadas
- **Binance/Bybit API** (gratuito): Funding rates em tempo real

---

## Estrutura

```
backend/
├── src/
│   ├── agents/          # Lógica do agente especialista
│   ├── data/            # Coleta e gestão de dados
│   ├── analysis/        # Análise técnica, fundamental, correlações
│   ├── strategies/      # Estratégias de trading
│   ├── risk/            # Gestão de risco
│   └── api/             # REST API (FastAPI)
├── tests/               # Testes
└── requirements.txt     # Dependências
```

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Desenvolvimento

```bash
# Rodar servidor de desenvolvimento
python main.py

# Rodar testes
pytest

# Linting
flake8 src/
black src/
```
