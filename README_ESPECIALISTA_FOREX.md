# ESPECIALISTA DE INVESTIMENTO INTERNACIONAL - FOREX

## 📊 Visão Geral

Sistema especializado para análise de oportunidades em Forex com horizonte de dias/semanas. O especialista avalia oportunidades seguindo um formato estruturado específico, considerando dados econômicos, correlações, notícias e eventos.

## 🎯 Formato Estruturado da Análise

### [INICIO] - Dados Econômicos Atuais

- **VIX**: Índice de volatilidade do mercado
- **DXY**: Índice dólar americano
- **Treasury 10Y**: Yield títulos do tesouro americano
- **S&P 500**: Índice bolsa americana
- **Ouro**: Preço spot do ouro
- **WTI**: Preço petróleo bruto
- **Taxas de Juros**: Principais bancos centrais (FED, ECB, BoE, BoJ, BRL)

### [DURANTE] - Correlação com Outros Ativos

- **Correlações Positivas**: Ativos que se movem na mesma direção
- **Correlações Negativas**: Ativos que se movem em direções opostas
- **Períodos**: 30d, 90d, 180d para análise histórica
- **Ativos**: Pares Forex + Índices + Commodities + Bonds

### [DURANTE] - Notícias e Eventos que Impactam

- **Notícias Recentes**: Desenvolvimento econômico das moedas envolvidas
- **Eventos Econômicos**: Calendário de eventos próximos (FOMC, ECB, etc.)
- **Sentimento de Mercado**: Análise de sentimento baseada em dados

### [FIM] - Parecer sobre Oportunidade

- **Decisão**: APROVAR / DESCARTAR / OBSERVAR
- **Níveis de Entrada**: Conservador e Agressivo
- **Take Profit**: Primário e Secundário
- **Stop Loss**: Conservador e Agressivo
- **Justificativa**: Análise detalhada da decisão
- **Risco/Retorno**: Ratio Reward/Risk e percentuais

### [QUANDO] - Oportunidade Correlacionada Recomendada

- **Ativo Recomendado**: Par com maior correlação identificada
- **Correlação**: Coeficiente de correlação identificado
- **Justificativa**: Por que essa oportunidade é recomendada
- **Níveis Sugeridos**: Entrada, TP e SL para o ativo recomendado

## 🚀 Como Usar

### Via CLI (Linha de Comando)

```bash
# Análise básica (horizonte dias)
python especialista_forex_cli.py EURUSD=X

# Análise com horizonte semanas
python especialista_forex_cli.py GBPUSD=X --horizonte semanas

# Saída em JSON
python especialista_forex_cli.py USDJPY=X --json
```

### Via Código Python

```python
from backend.especialista_investimento_forex import EspecialistaInvestimentoForex

# Criar especialista
especialista = EspecialistaInvestimentoForex()

# Analisar oportunidade
analise = especialista.analisar_oportunidade_forex('EURUSD=X', 'dias')

# Gerar relatório formatado
relatorio = especialista.gerar_relatorio_formatado(analise)
print(relatorio)

# Ou acessar dados estruturados
print(analise['FIM']['decisao'])  # APROVAR/DESCARTAR/OBSERVAR
print(analise['FIM']['niveis_entrada']['conservador'])  # Nível entrada
```

## 📈 Pares Forex Suportados

| Par | Descrição | Moedas |
|-----|-----------|---------|
| EURUSD=X | Euro vs Dólar | EUR/USD |
| GBPUSD=X | Libra vs Dólar | GBP/USD |
| USDJPY=X | Dólar vs Iene | USD/JPY |
| USDCAD=X | Dólar vs Dólar Canadense | USD/CAD |
| USDCHF=X | Dólar vs Franco Suíço | USD/CHF |
| AUDUSD=X | Dólar Australiano vs Dólar | AUD/USD |
| NZDUSD=X | Dólar Neozelandês vs Dólar | NZD/USD |
| USDMXN=X | Dólar vs Peso Mexicano | USD/MXN |
| USDZAR=X | Dólar vs Rand Sul-Africano | USD/ZAR |
| USDBRL=X | Dólar vs Real Brasileiro | USD/BRL |

## 🎯 Critérios de Avaliação

### Score de Oportunidade (0-10)

- **≥ 7.0**: APROVAR - Condições favoráveis
- **5.0-6.9**: OBSERVAR - Aguardar confirmação
- **< 5.0**: DESCARTAR - Condições desfavoráveis

### Fatores Considerados

1. **Análise Técnica (40%)**
   - Tendência (SMA 50 vs SMA 200)
   - RSI (sobrecompra/sobrevenda)
   - Volatilidade histórica

2. **Condições de Mercado (30%)**
   - Nível VIX (volatilidade)
   - Força relativa DXY
   - Score geral de mercado

3. **Correlações (20%)**
   - Força das correlações
   - Estabilidade temporal
   - Diversificação possível

4. **Fundamentos (10%)**
   - Eventos econômicos próximos
   - Sentimento de mercado
   - Notícias relevantes

## 📊 Interpretação dos Resultados

### Decisão APROVAR

- ✅ Probabilidade > 70%
- ✅ Múltiplos fatores positivos alinhados
- ✅ Risco/retorno favorável
- ✅ Correlações confirmam tendência

### Decisão OBSERVAR

- ⚠️ Probabilidade 50-70%
- ⚠️ Alguns fatores positivos, outros neutros
- ⚠️ Aguardar confirmação adicional
- ⚠️ Monitorar níveis chave

### Decisão DESCARTAR

- ❌ Probabilidade < 50%
- ❌ Condições desfavoráveis predominam
- ❌ Alto risco relativo ao retorno
- ❌ Correlações contrárias à entrada

## 🔧 Configuração e Dependências

### Dependências Python

```bash
pip install yfinance pandas numpy requests
```

### Estrutura de Arquivos

```text
backend/
├── especialista_investimento_forex.py    # Classe principal
└── ...

especialista_forex_cli.py                 # CLI para uso
```

## ⚠️ Avisos Importantes

### Riscos

- **Dados em Tempo Real**: Análise baseada em dados históricos recentes
- **Volatilidade**: Forex é altamente volátil, use sempre stop-loss
- **Liquidez**: Alguns pares podem ter baixa liquidez
- **Horário**: Considere sessões de mercado globais

### Limitações

- **Dados Históricos**: Análise limitada a dados disponíveis via Yahoo Finance
- **Notícias**: Simulação baseada em eventos conhecidos (não API em tempo real)
- **Sentimento**: Análise básica, não inclui redes sociais avançadas

### Recomendações

- **Capital**: Use apenas capital que pode perder
- **Position Sizing**: Siga os níveis de risco calculados
- **Diversificação**: Não concentre em um único par
- **Monitoramento**: Monitore posições ativamente

## 📈 Exemplos de Uso

### Exemplo 1: EUR/USD em Alta Volatilidade

```
[INICIO] VIX alto, DXY fraco
[DURANTE] Forte correlação com GBPUSD (+0.85)
[DURANTE] FOMC Minutes próximo
[FIM] DESCARTAR - Alto risco
[QUANDO] Recomendar USDCHF (correlação -0.90)
```

### Exemplo 2: GBP/USD em Tendência
```
[INICIO] DXY estável, Treasury em alta
[DURANTE] Correlação positiva com EURUSD (+0.75)
[DURANTE] BoE announcement
[FIM] APROVAR - Setup favorável
[QUANDO] Recomendar EURUSD (correlação +0.75)
```

## 🔄 Próximos Passos

### Melhorias Planejadas
- [ ] Integração com APIs de notícias em tempo real
- [ ] Análise de sentimento avançada (Twitter, Reddit)
- [ ] Machine Learning para predição de probabilidade
- [ ] Alertas em tempo real via Telegram/Email
- [ ] Backtesting histórico completo
- [ ] Integração com plataformas de trading

### Expansão
- [ ] Suporte a CFDs e criptomoedas
- [ ] Análise multi-timeframe avançada
- [ ] Integração com dados econômicos oficiais
- [ ] Relatórios PDF automatizados

---
*Especialista Forex - Agent Especialista Mercado Financeiro*
*Data: 2025-11-07*
