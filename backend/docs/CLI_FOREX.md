# CLI Forex - Manual de Uso

## 📋 Visão Geral

O CLI Forex é uma ferramenta de linha de comando para análise completa de oportunidades em Forex (Foreign Exchange). Combina análise de carry trade, política monetária, análise técnica, correlação com mercado brasileiro e sentimento de notícias.

## 🚀 Instalação

```powershell
# Já está pronto para uso no projeto
cd c:\repo\projetos\agent-especialista-mercado-financeiro
```

## 📊 Comandos Disponíveis

### 1. `taxas` - Taxas dos Bancos Centrais

Exibe as taxas de juros atuais dos principais bancos centrais globais.

```powershell
python backend\consultar_forex.py taxas
```

**Saída:**
```
TAXAS DE JUROS DOS BANCOS CENTRAIS
Moeda  BC     Taxa   Guidance     Próxima Reunião
USD    FED    5.50%  🦅 hawkish   07/11/2025
EUR    ECB    3.50%  🕊️ dovish    12/12/2025
GBP    BOE    4.00%  ⚖️ neutro    06/11/2025
JPY    BOJ    0.00%  🕊️ dovish    19/12/2025
NZD    RBNZ   2.50%  🕊️ dovish    26/11/2025
AUD    RBA    3.60%  ⚖️ neutro    03/12/2025
BRL    BCB   11.25%  🦅 hawkish   11/12/2025
```

**Indicadores:**
- 🦅 **Hawkish**: Banco central com viés de alta de juros (aperto monetário)
- 🕊️ **Dovish**: Banco central com viés de baixa de juros (afrouxamento monetário)
- ⚖️ **Neutro**: Banco central sem viés claro

---

### 2. `carry-trades` - Melhores Oportunidades de Carry

Lista as melhores oportunidades de carry trade baseadas nos diferenciais de juros.

```powershell
python backend\consultar_forex.py carry-trades --top 10
```

**Parâmetros:**
- `--top N`: Número de carry trades a exibir (padrão: 10)

**Saída:**
```
TOP 10 CARRY TRADES - OPORTUNIDADES
#    Par        Diferencial   Atratividade  Tipo
🥇 1  BRLJPY        11.25%         9.00      positivo_venda
🥈 2  BRLAUD         7.65%         7.65      positivo_venda
🥉 3  BRLGBP         7.25%         7.25      positivo_venda
   4  BRLNZD         8.75%         7.00      positivo_venda
   5  BRLUSD         5.75%         6.90      positivo_venda
```

**Interpretação:**
- **Diferencial**: Diferença de taxas de juros entre as moedas
- **Atratividade**: Score ajustado por guidance do BC (0-10)
- **Tipo**: `positivo_venda` = comprar par gera juros; `positivo_compra` = vender par gera juros

---

### 3. `analisar` - Análise Completa de Par Forex

Realiza análise completa de um par Forex específico usando metodologia de 5 pilares.

```powershell
python backend\consultar_forex.py analisar GBPNZD --operacao COMPRA
```

**Parâmetros:**
- `PAR`: Par Forex (ex: EURUSD, GBPUSD, USDJPY, GBPNZD)
- `--operacao`: Tipo de operação (COMPRA ou VENDA, padrão: COMPRA)

**Pares Suportados:**
- **Majors**: EURUSD, GBPUSD, USDJPY, USDCHF
- **Crosses**: EURGBP, EURJPY, GBPJPY, AUDUSD, NZDUSD
- **Exóticos**: USDBRL, GBPNZD, AUDNZD, EURNZD, GBPBRL, AUDBRL

**Saída:**

```
================================================================================
ANALISANDO: COMPRA GBP/NZD
================================================================================

📊 PILAR 1: Carry Trade
   Diferencial: +1.50%
   Rating: bom

🏦 PILAR 2: Política Monetária
   GBP: neutro ⚖️
   NZD: dovish 🕊️
   Divergência: moderada

📈 PILAR 3: Análise Técnica
   Preço Atual: 2.3052
   Tendência: lateral
   Entrada: 2.2937
   Stop: 2.2706
   TP1: 2.3398
   TP2: 2.3744

🔗 PILAR 4: Correlação com Brasil
   Impacto WIN: neutro
   Correlação IBOV: 0.00

📰 PILAR 5: Sentimento de Notícias
   Score: +0.02
   Notícias: 58

🎯 DECISÃO FINAL
   Recomendação: APROVAR_TÁTICO
   Confiança: 56%
   Risco/Recompensa: 1:1.00

💡 ALTERNATIVA RECOMENDADA: GBP/BRL
   Motivo: Carry Trade superior: 7.25% vs 1.50%
```

**5 Pilares de Análise:**

1. **Carry Trade** (peso 30%)
   - Diferencial de juros entre moedas
   - Rating: excelente (>4%), bom (2-4%), moderado (0.5-2%), neutro (0-0.5%), negativo (<0%)

2. **Política Monetária** (peso 25%)
   - Divergência entre guidance dos BCs
   - Forte: vieses opostos (hawkish vs dovish)
   - Moderada: um neutro
   - Fraca: ambos com mesmo viés

3. **Análise Técnica** (peso 20%)
   - Tendência (SMA 20 vs SMA 50)
   - Níveis de entrada, stop loss, take profit
   - Risco/Recompensa calculado

4. **Correlação com Brasil** (peso 15%)
   - Impacto no WIN (mini-índice)
   - Correlação com IBOV
   - Importante para traders brasileiros

5. **Sentimento de Notícias** (peso 10%)
   - Score agregado de notícias recentes (últimos 30 dias)
   - Quantidade de notícias relevantes

**Recomendações Possíveis:**
- ✅ **APROVAR_LONG**: Alta confiança (≥70%), setup favorável
- ✅ **APROVAR_SHORT**: Alta confiança (≥70%), setup favorável para venda
- ⚠️ **APROVAR_TÁTICO**: Média confiança (50-69%), pode ser tactical trade
- ❌ **DESCARTAR**: Baixa confiança (<50%), não operar

---

### 4. `comparar` - Comparação Entre Pares

Compara múltiplos pares Forex lado a lado para identificar a melhor oportunidade.

```powershell
python backend\consultar_forex.py comparar EURUSD GBPUSD USDJPY --operacao COMPRA
```

**Parâmetros:**
- `PARES`: Lista de pares para comparar (separados por espaço)
- `--operacao`: Tipo de operação (COMPRA ou VENDA, padrão: COMPRA)

**Saída:**

```
COMPARAÇÃO DE PARES FOREX

Par         Carry    Confiança    R:R  Recomendação
----------------------------------------------------
USD/JPY     5.50%       70%      1.00  ✅ APROVAR_LONG
EUR/USD    -2.00%       30%      1.00  ❌ DESCARTAR
GBP/USD    -1.50%       20%      1.00  ❌ DESCARTAR

MELHOR OPORTUNIDADE: USD/JPY - APROVAR_LONG
Confiança: 70% | Carry: 5.50%
```

Após a tabela comparativa, exibe o relatório completo do par com melhor score.

---

## 🎯 Casos de Uso

### Caso 1: Checagem Rápida de Oportunidades Diárias

```powershell
# 1. Ver situação dos bancos centrais
python backend\consultar_forex.py taxas

# 2. Identificar melhores carry trades
python backend\consultar_forex.py carry-trades --top 5

# 3. Analisar o melhor carry
python backend\consultar_forex.py analisar BRLJPY --operacao VENDA
```

### Caso 2: Análise Pré-Decisão de Banco Central

```powershell
# Comparar pares afetados por decisão do Fed
python backend\consultar_forex.py comparar EURUSD GBPUSD USDJPY USDCHF
```

### Caso 3: Verificar Correlação com Brasil

```powershell
# Analisar impacto de EUR/USD no mercado brasileiro
python backend\consultar_forex.py analisar EURUSD --operacao COMPRA
# Verificar seção "PILAR 4: Correlação com Brasil"
```

---

## 📈 Metodologia de Análise

### Sistema de Pontuação (0-100%)

Cada pilar contribui com uma pontuação ponderada:

```python
score_final = (
    carry_score      * 0.30 +  # 30%
    politica_score   * 0.25 +  # 25%
    tecnica_score    * 0.20 +  # 20%
    correlacao_score * 0.15 +  # 15%
    sentimento_score * 0.10    # 10%
)
```

### Thresholds de Decisão

- **≥70%**: APROVAR_LONG ou APROVAR_SHORT (alta confiança)
- **50-69%**: APROVAR_TÁTICO (média confiança, trade tático)
- **<50%**: DESCARTAR (baixa confiança, não operar)

### Cálculo de Risco/Recompensa

```
R/R = (Take Profit - Entrada) / (Entrada - Stop Loss)
```

Recomendação: R/R mínimo de 1:1.5 para swing trades

---

## 🔍 Fontes de Dados

### Preços e Dados Técnicos
- **Yahoo Finance** (`yfinance`)
- Atualização: Tempo real
- Dados: OHLC, volume, dados históricos

### Taxas de Juros
- **Atual**: Dados mock (taxas reais de Nov/2025)
- **Futuro**: Integração com APIs de BCs
  - FED: FRED API
  - ECB: ECB Statistical Data Warehouse
  - Outros: Trading Economics API

### Notícias e Sentimento
- **Banco de Dados Local**: `recomendacoes.sqlite`
- Tabela: `noticias`
- Análise: Score agregado de sentimento

### Correlações
- **Banco de Dados Local**: `recomendacoes.sqlite`
- Tabela: `cotacoes_correlacoes`
- Ativos: WIN, IBOV, DXY, SP500

---

## ⚙️ Configuração Técnica

### Dependências

```python
- yfinance >= 0.2.0
- sqlite3 (built-in)
- pandas >= 2.0.0
```

### Estrutura de Arquivos

```
backend/
├── consultar_forex.py           # CLI principal
├── src/
│   └── dados/
│       ├── forex_fundamentals.py    # Coleta de taxas e carry trades
│       └── analisador_forex.py      # Motor de análise (5 pilares)
├── data/
│   └── recomendacoes.sqlite     # Banco de dados SQLite
└── docs/
    └── CLI_FOREX.md             # Esta documentação
```

### Tabelas do Banco de Dados

**forex_taxas_juros**
- Armazena histórico de taxas de juros dos BCs
- Campos: banco_central, moeda, taxa_atual, forward_guidance, proxima_reuniao

**forex_indicadores_macro**
- Indicadores econômicos por país
- Campos: pais, indicador, valor_atual, periodo_referencia

**forex_carry_trade**
- Carry trades calculados
- Campos: par_forex, diferencial, tipo_carry, atratividade

---

## 🐛 Troubleshooting

### Erro: "no such column: relevancia"
**Solução**: Tabela `noticias` não possui coluna `relevancia`. Já corrigido na versão atual.

### Erro: "Import could not be resolved"
**Solução**: Execute sempre da raiz do projeto:
```powershell
# Errado
cd backend
python consultar_forex.py taxas

# Correto
python backend\consultar_forex.py taxas
```

### Preços não atualizando
**Causa**: Yahoo Finance pode ter rate limiting
**Solução**: Aguardar alguns minutos entre consultas

---

## 🚀 Roadmap

### Próximas Funcionalidades

- [ ] Integração com APIs reais de BCs
- [ ] Suporte a mais pares exóticos
- [ ] Alertas automáticos de oportunidades
- [ ] Backtesting de estratégias de carry
- [ ] Export de análises para PDF
- [ ] Dashboard web interativo
- [ ] Integração com Telegram para notificações

### Melhorias Planejadas

- [ ] Cache de dados para evitar rate limiting
- [ ] Análise de volatilidade implícita (opções)
- [ ] Integração com fluxo de ordem (COT reports)
- [ ] Machine learning para previsão de carry trades

---

## 📚 Referências

### Literatura Recomendada
- *Currency Trading for Dummies* - Kathleen Brooks, Brian Dolan
- *The Art of Currency Trading* - Brent Donnelly
- *Trading and Exchanges* - Larry Harris

### Links Úteis
- [BabyPips School of Pipsology](https://www.babypips.com/learn/forex)
- [OANDA Forex Education](https://www.oanda.com/forex-trading/learn)
- [Investopedia Forex](https://www.investopedia.com/forex-trading-4427783)

---

## 📧 Suporte

Para dúvidas ou sugestões sobre o CLI Forex, consulte a documentação principal do projeto ou abra uma issue no repositório.

---

**Versão**: 1.0.0
**Data**: Novembro 2025
**Autor**: Agent Especialista Mercado Financeiro
