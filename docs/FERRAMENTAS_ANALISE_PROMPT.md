# Ferramentas de Análise - Sprint Prompt Interativo

Documentação das ferramentas implementadas para US-PROMPT-002: Orquestrador de Ferramentas.

## 📋 Visão Geral

O módulo de ferramentas fornece dados estruturados para análise de ativos financeiros, integrando-se ao orquestrador de análise LLM.

```text
ferramentas/
├── __init__.py
├── preco_atual.py          # Preços em tempo real
├── indicadores_tecnicos.py # SMA, RSI, sinais técnicos
└── noticias_resumidas.py   # Notícias e sentimento
```

## 🛠️ Ferramentas Implementadas

### 1. Preço Atual (`preco_atual.py`)

**Função:** `obter_preco_atual(ativo, incluir_historico=False)`

**Fonte:** Yahoo Finance via yfinance

**Dados Fornecidos:**

- Preço atual e variação percentual
- Timestamp e frescor dos dados
- Status do mercado (aberto/fechado/pre_mercado)
- Idade dos dados em minutos

**Exemplo:**

```python
from ferramentas.preco_atual import obter_preco_atual

dados = obter_preco_atual("AAPL")
# {
#   "ativo": "AAPL",
#   "preco": 267.73,
#   "variacao_pct": -0.76,
#   "timestamp": "2025-11-07T20:28:48.401000+00:00",
#   "frescor": "tempo_real",
#   "mercado_status": "aberto"
# }
```

**Resiliência:**

- Retry automático (3 tentativas, backoff exponencial)
- Alertas para mercado fechado
- Validação de frescor (<15min)

### 2. Indicadores Técnicos (`indicadores_tecnicos.py`)

**Função:** `calcular_sma_rsi(ativo, periodo_sma=20, periodo_rsi=14, periodo_historico=100)`

**Fonte:** Yahoo Finance + pandas-ta

**Indicadores Calculados:**

- **SMA (Simple Moving Average)**: Média móvel simples
- **RSI (Relative Strength Index)**: Índice de força relativa

**Dados Fornecidos:**

- Valores atuais dos indicadores
- Sinais de análise (ACIMA_SMA/ABAIXO_SMA, SOBRECOMPRADO/SOBREVENDIDO)
- Diferenças percentuais e interpretação técnica
- Metadados de cálculo (períodos, timestamps)

**Exemplo:**

```python
from ferramentas.indicadores_tecnicos import calcular_sma_rsi

dados = calcular_sma_rsi("AAPL")
# {
#   "indicadores": {
#     "sma": {
#       "periodo": 20,
#       "valor": 262.3035,
#       "sinal": "ACIMA_SMA",
#       "diferenca_pct": 2.04
#     },
#     "rsi": {
#       "periodo": 14,
#       "valor": 61.47,
#       "sinal": "NEUTRO",
#       "interpretacao": "Zona neutra - sem sinal claro de momentum"
#     }
#   }
# }
```

**Sinais Técnicos:**

- **SMA**: ACIMA_SMA (bullish), ABAIXO_SMA (bearish)
- **RSI**: SOBRECOMPRADO (>70), SOBREVENDIDO (<30), NEUTRO (30-70)

### 3. Notícias Resumidas (`noticias_resumidas.py`)

**Função:** `buscar_noticias_resumidas(ativo, limite_noticias=5, dias_atras=7)`

**Status:** PLACEHOLDER - Implementação mockada estruturada

**Dados Fornecidos:**

- Lista de notícias com título, resumo, sentimento
- Análise de sentimento geral (POSITIVO/NEGATIVO/NEUTRO)
- Avaliação de impacto (ALTO/MÉDIO/BAIXO)
- Resumo consolidado e estatísticas

**Estrutura Futura:**

```python
# Integração planejada com:
# - NewsAPI (newsapi.org)
# - Alpha Vantage News
# - Twitter API (sentimento social)
# - Google News via RSS
```

**Exemplo Atual (Mock):**

```python
from ferramentas.noticias_resumidas import buscar_noticias_resumidas

dados = buscar_noticias_resumidas("AAPL")
# {
#   "noticias": [
#     {
#       "titulo": "Apple announces new product line",
#       "resumo": "Company unveils latest innovations...",
#       "sentimento": "POSITIVO",
#       "impacto": "ALTO",
#       "timestamp": "2025-11-07T...",
#       "relevancia_score": 0.95
#     }
#   ],
#   "resumo_geral": {
#     "sentimento_geral": "POSITIVO",
#     "impacto_geral": "ALTO",
#     "resumo": "Notícias predominantemente positivas..."
#   }
# }
```

## 🔄 Integração com Orquestrador

As ferramentas são automaticamente integradas no `orquestrador_analise.py`:

1. **Coleta Sequencial:** Preço → Indicadores → Notícias
2. **Tratamento de Erro:** Continua análise mesmo se ferramenta falhar
3. **Contexto LLM:** Dados incluídos no prompt de análise
4. **Resposta Estruturada:** Dados disponíveis em JSON final

**Fluxo de Integração:**

```text
Orquestrador.analisar_ativo()
├── obter_preco_atual() ✅
├── calcular_sma_rsi() ⚠️ (pode falhar)
├── buscar_noticias_resumidas() ⚠️ (pode falhar)
├── _preparar_contexto_analise() 📝
├── _chamar_llm_analise() 🤖
└── _estruturar_resposta_final() 📋
```

## 📊 Métricas de Qualidade

### Preço Atual

- **Disponibilidade:** >99% (Yahoo Finance)
- **Frescor:** <15min para mercado aberto
- **Precisão:** Dados oficiais da bolsa

### Indicadores Técnicos

- **Precisão:** Cálculos pandas-ta validados
- **Histórico:** 100 dias padrão (configurável)
- **Sinais:** Interpretação técnica consistente

### Notícias (Placeholder)

- **Estrutura:** Schema definido para integração futura
- **Sentimento:** Classificação mockada realista
- **Escalabilidade:** Preparado para múltiplas fontes

## 🚀 Próximos Passos

### Curto Prazo

- [ ] Configurar APIs de notícias reais
- [ ] Implementar cache Redis para indicadores
- [ ] Adicionar mais indicadores (MACD, Bandas de Bollinger)

### Médio Prazo

- [ ] Análise de sentimento com NLP
- [ ] Correlação entre notícias e preço
- [ ] Alertas automáticos baseados em indicadores

### Integração com US Próximos

- **US-PROMPT-003:** Templates podem usar dados das ferramentas
- **US-PROMPT-004:** Saída JSON já inclui estrutura das ferramentas
- **US-PROMPT-005:** Cache pode ser implementado por ferramenta

## 🧪 Testes Executados

### Cenários Validados

- ✅ AAPL: Preço + Indicadores + Notícias funcionais
- ✅ Mercado aberto: Status correto, frescor tempo_real
- ✅ Erro handling: Continua análise se ferramenta falhar
- ✅ JSON estruturado: Dados incluídos na resposta final

### Comandos de Teste

```bash
# Teste completo
python orquestrador_analise.py AAPL trader

# Teste JSON
python orquestrador_analise.py AAPL analista --json

# Teste ferramentas individuais
python -c "from ferramentas.indicadores_tecnicos import calcular_sma_rsi; print(calcular_sma_rsi('AAPL')['indicadores']['sma']['valor'])"
```

## 📝 Notas de Implementação

- **Dependências:** pandas-ta instalado e funcional
- **Encoding:** Tratamento de caracteres especiais no JSON
- **Performance:** ~2-3s por análise completa (preço + indicadores + notícias)
- **Resiliência:** Sistema continua funcionando mesmo com falhas parciais
- **Extensibilidade:** Arquitetura preparada para novas ferramentas
