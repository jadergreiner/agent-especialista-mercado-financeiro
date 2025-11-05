# Template de Análise - Guia de Uso

## 🎯 Visão Geral

O sistema de template de análise permite que você execute análises completas de mercado com comandos simples. Basta fornecer o ticker do ativo e o sistema dispara automaticamente todas as regras de análise relevantes.

## 🚀 Como Usar

### Modo 1: CLI Interativo

Execute o CLI e interaja diretamente:

```bash
cd backend
python cli.py
```

Interface interativa:
```
======================================================================
🚀 AGENT ESPECIALISTA DE MERCADO FINANCEIRO
======================================================================
Versão: 0.1.0
Digite 'ajuda' para ver comandos disponíveis
Digite 'sair' para encerrar
======================================================================

💬 Digite o ativo para análise: BTCUSD
```

### Modo 2: Comando Único

Execute análise direta via linha de comando:

```bash
# Análise completa
python backend/cli.py BTCUSD

# Análise rápida
python backend/cli.py PETR4 rapida

# Análise técnica
python backend/cli.py AAPL tecnica
```

### Modo 3: Uso Programático

Use diretamente no código Python:

```python
from backend.src.agents.orquestrador_analise import OrquestradorAnalise, TipoAnalise

# Criar orquestrador
orquestrador = OrquestradorAnalise()

# Análise simples - apenas o ticker
resultado = orquestrador.analisar("BTCUSD")
print(resultado['recomendacao_geral'])

# Análise rápida
resultado = orquestrador.analisar("PETR4", TipoAnalise.RAPIDA)
print(resultado['recomendacao'])

# Análise técnica detalhada
resultado = orquestrador.analisar("AAPL", TipoAnalise.TECNICA, periodo_dias=30)
print(resultado['analise_tecnica'])
```

## 📋 Tipos de Análise

### 1. COMPLETA (padrão)
Executa todas as análises disponíveis:
- ✅ Análise técnica completa
- ✅ Análise de correlações
- ✅ Análise de sentimento e notícias
- ✅ Identificação de suportes/resistências
- ✅ Pontos ótimos de entrada/saída
- ✅ Gestão de risco

**Exemplo:**
```python
resultado = orquestrador.analisar("BTCUSD")
```

### 2. RAPIDA
Análise expressa com principais indicadores:
- ✅ Preço atual e variação
- ✅ RSI e MACD
- ✅ Tendência de curto prazo
- ✅ Recomendação simples

**Exemplo:**
```python
resultado = orquestrador.analisar("PETR4", TipoAnalise.RAPIDA)
```

### 3. TECNICA
Foco em análise técnica:
- ✅ Tendências (primária, secundária, terciária)
- ✅ Indicadores técnicos completos
- ✅ Padrões de candlestick
- ✅ Suportes e resistências

**Exemplo:**
```python
resultado = orquestrador.analisar("AAPL", TipoAnalise.TECNICA)
```

### 4. CORRELACAO
Foco em correlações com outros ativos:
- ✅ Ativos correlacionados
- ✅ Mudanças de regime
- ✅ Impacto de índices

**Exemplo:**
```python
resultado = orquestrador.analisar("VALE3", TipoAnalise.CORRELACAO)
```

### 5. SENTIMENTO
Foco em análise de sentimento:
- ✅ Notícias recentes
- ✅ Sentimento geral do mercado
- ✅ Impacto estimado

**Exemplo:**
```python
resultado = orquestrador.analisar("TSLA", TipoAnalise.SENTIMENTO)
```

### 6. FUNDAMENTAL
Foco em análise fundamentalista:
- ✅ Indicadores fundamentais
- ✅ Eventos próximos
- ✅ Valuation

**Exemplo:**
```python
resultado = orquestrador.analisar("PETR4", TipoAnalise.FUNDAMENTAL)
```

## 📊 Estrutura de Resposta

### Análise Rápida

```python
{
    "ativo": "BTCUSD",
    "timestamp": "2025-11-05T10:30:00",
    "tipo_analise": "rapida",
    "periodo_dias": 90,
    "status": "concluido",

    "preco_atual": 67500.00,
    "variacao_dia": 2.5,
    "variacao_periodo": 15.8,
    "tendencia": "alta",
    "forca_tendencia": 0.75,

    "indicadores_chave": {
        "rsi": 65.5,
        "macd": {
            "linha": 450.0,
            "sinal": 380.0,
            "histograma": 70.0
        },
        "volume_relativo": 1.2
    },

    "recomendacao": "comprar",
    "confianca": 0.72,
    "observacoes": ["Tendência de alta confirmada", "Volume acima da média"]
}
```

### Análise Completa

```python
{
    "ativo": "PETR4",
    "timestamp": "2025-11-05T10:30:00",
    "tipo_analise": "completa",
    "periodo_dias": 90,
    "status": "concluido",

    "analise_tecnica": {
        "tendencia_primaria": "alta",
        "indicadores": {...},
        "padroes_identificados": [...],
        "sinais": [...]
    },

    "analise_correlacao": {
        "correlacoes_principais": [...],
        "ativos_relacionados": [...],
        "impacto_indices": {...}
    },

    "analise_sentimento": {
        "sentimento_geral": "positivo",
        "pontuacao_sentimento": 72.5,
        "noticias_recentes": [...]
    },

    "niveis_importantes": {
        "suportes": [38.50, 37.80, 36.90],
        "resistencias": [40.20, 41.50, 42.80]
    },

    "timing": {
        "ponto_entrada_otimo": 39.10,
        "stop_loss_sugerido": 38.20,
        "take_profit_sugerido": 41.00,
        "risco_retorno": 2.5
    },

    "gestao_risco": {
        "tamanho_posicao_sugerido": 0.05,
        "exposicao_maxima": 0.02,
        "probabilidade_sucesso": 0.68
    },

    "recomendacao_geral": {
        "acao": "comprar",
        "confianca": 0.75,
        "timeframe_sugerido": "medio_prazo",
        "justificativa": [
            "Tendência de alta consolidada",
            "Rompimento de resistência com volume",
            "Sentimento positivo do mercado"
        ],
        "alertas": [],
        "proximos_passos": [
            "Aguardar pullback para nível de 39.10",
            "Monitorar volume na entrada",
            "Definir stop-loss em 38.20"
        ]
    }
}
```

## 🎨 Exemplos de Uso

### Exemplo 1: Análise Rápida de Criptomoeda
```python
orquestrador = OrquestradorAnalise()
resultado = orquestrador.analisar("BTCUSD", TipoAnalise.RAPIDA)

print(f"Recomendação: {resultado['recomendacao']}")
print(f"Confiança: {resultado['confianca'] * 100:.1f}%")
print(f"Tendência: {resultado['tendencia']}")
```

### Exemplo 2: Análise Completa de Ação Brasileira
```python
resultado = orquestrador.analisar("PETR4", TipoAnalise.COMPLETA, periodo_dias=120)

# Verificar recomendação
rec = resultado['recomendacao_geral']
if rec['acao'] == 'comprar' and rec['confianca'] > 0.7:
    print(f"✅ Sinal de compra forte!")
    print(f"Entrada sugerida: R$ {resultado['timing']['ponto_entrada_otimo']:.2f}")
    print(f"Stop-loss: R$ {resultado['timing']['stop_loss_sugerido']:.2f}")
```

### Exemplo 3: Monitoramento de Correlações
```python
resultado = orquestrador.analisar("VALE3", TipoAnalise.CORRELACAO)

print("Ativos correlacionados:")
for corr in resultado['analise_correlacao']['correlacoes_principais']:
    print(f"  {corr['ativo']}: {corr['correlacao']:.2f}")
```

## 🔧 Personalização

### Ajustar Período de Análise
```python
# Análise de curto prazo (30 dias)
resultado = orquestrador.analisar("AAPL", periodo_dias=30)

# Análise de longo prazo (365 dias)
resultado = orquestrador.analisar("AAPL", periodo_dias=365)
```

### Excluir Análise de Notícias
```python
resultado = orquestrador.analisar(
    "TSLA",
    TipoAnalise.COMPLETA,
    incluir_noticias=False
)
```

## 📝 Notas Importantes

1. **Status Atual**: Sistema em desenvolvimento - alguns módulos retornam dados mock
2. **Implementação Futura**: Integração com APIs reais de dados de mercado
3. **Extensibilidade**: Fácil adicionar novos tipos de análise
4. **Performance**: Análise rápida ~1s, Completa ~5s (quando implementado)

## 🚀 Próximos Passos

1. ✅ Template de análise criado
2. ⏳ Implementar coleta de dados real (yfinance)
3. ⏳ Implementar cálculos de indicadores técnicos
4. ⏳ Implementar análise de correlações
5. ⏳ Integrar análise de sentimento
6. ⏳ Adicionar cache para otimização
