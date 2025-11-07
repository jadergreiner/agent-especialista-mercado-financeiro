# PROMPT: MODELO DE MACHINE LEARNING PARA PREDIÇÃO DO MINI ÍNDICE BRASILEIRO (WIN)

## 🎯 OBJETIVO PRINCIPAL

Desenvolver um modelo de machine learning capaz de prever o preço de fechamento do Mini Índice Brasileiro (WIN) para o próximo dia útil, utilizando dados históricos de mercado.

## 📊 DADOS DE ENTRADA

Utilizar os seguintes dados históricos do WIN (disponíveis via API ou fonte de dados):

- **Preço de Abertura** (Open)
- **Preço Máximo** (High)
- **Preço Mínimo** (Low)
- **Preço de Fechamento** (Close)
- **Preço de Ajuste** (Adj Close)
- **Volume** (Volume)
- **Data** (Date) - para extração de features temporais

## 🏗️ ARQUITETURA DO MODELO

### 1. PRÉ-PROCESSAMENTO DE DADOS

- **Feature Engineering**:
  - Retornos diários: (Close_t - Close_t-1) / Close_t-1
  - Volatilidade: Desvio padrão dos retornos (7 dias, 14 dias, 30 dias)
  - Volume relativo: Volume_t / Média móvel volume (20 dias)
  - Range diário: (High - Low) / Close
  - Gap de abertura: (Open - Close_t-1) / Close_t-1
  - Features temporais: Dia da semana, mês, trimestre
  - Médias móveis: SMA(5), SMA(10), SMA(20), SMA(50)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)

- **Tratamento de Dados**:
  - Remoção de outliers (Z-score > 3)
  - Tratamento de valores faltantes (forward fill)
  - Normalização/Padronização das features
  - Split temporal: 70% treino, 20% validação, 10% teste

### 2. SELEÇÃO DE ALGORITMO

Testar e comparar os seguintes algoritmos:

- **Regressão Linear** (baseline)
- **Random Forest Regressor**
- **Gradient Boosting (XGBoost/LightGBM)**
- **LSTM (Long Short-Term Memory)** - para capturar dependências temporais
- **Prophet** - para sazonalidade e tendências

### 3. AVALIAÇÃO DE PERFORMANCE

**Métricas Principais**:

- **MAE (Mean Absolute Error)**: Erro absoluto médio
- **RMSE (Root Mean Square Error)**: Raiz do erro quadrático médio
- **MAPE (Mean Absolute Percentage Error)**: Erro percentual absoluto médio
- **R² Score**: Coeficiente de determinação
- **Directional Accuracy**: % de acertos na direção do movimento

**Métricas de Validação**:

- **Walk-Forward Validation**: Simulação de uso em produção
- **Sharpe Ratio do Modelo**: Retorno ajustado ao risco
- **Maximum Drawdown**: Maior perda consecutiva

## 🔄 CICLO DE DESENVOLVIMENTO

### FASE 1: PROTOTIPAÇÃO (1-2 dias)

1. **Coleta de Dados**: Últimos 2 anos de dados WIN
2. **Feature Engineering**: Implementar features básicas
3. **Modelo Baseline**: Regressão Linear + Random Forest
4. **Avaliação Inicial**: MAE < 2% do preço médio

### FASE 2: OTIMIZAÇÃO (2-3 dias)

1. **Feature Selection**: Selecionar top 15-20 features
2. **Hyperparameter Tuning**: Grid Search/Random Search
3. **Ensemble Methods**: Combinar múltiplos modelos
4. **Cross-Validation**: 5-fold temporal

### FASE 3: VALIDAÇÃO E PRODUÇÃO (1-2 dias)

1. **Backtesting**: Simulação histórica de performance
2. **Stress Testing**: Cenários de alta volatilidade
3. **Model Persistence**: Salvar modelo treinado
4. **API de Predição**: Endpoint para predições em tempo real

## 📋 REQUISITOS TÉCNICOS

### Dependências

```bash
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.2.0
xgboost>=1.7.0
lightgbm>=3.3.0
tensorflow>=2.11.0  # Para LSTM
prophet>=1.1.0
yfinance>=0.2.0
matplotlib>=3.6.0
seaborn>=0.12.0
joblib>=1.2.0
```

### Estrutura de Arquivos

```
models/
├── win_predictor_v1.0/
│   ├── model.pkl                 # Modelo treinado
│   ├── feature_scaler.pkl        # Scaler das features
│   ├── feature_columns.pkl       # Lista de features usadas
│   └── model_metadata.json       # Metadados do modelo
src/
├── data/
│   ├── win_data_collector.py     # Coleta de dados WIN
│   └── feature_engineering.py    # Engenharia de features
├── models/
│   ├── baseline_models.py        # Modelos baseline
│   ├── ml_models.py             # Modelos de ML tradicionais
│   ├── deep_learning_models.py  # Modelos de DL (LSTM)
│   └── ensemble_models.py       # Modelos ensemble
├── evaluation/
│   ├── metrics.py               # Métricas de avaliação
│   ├── backtesting.py           # Backtesting framework
│   └── validation.py            # Validação cruzada temporal
└── api/
    └── prediction_api.py        # API de predição
```

## 🎯 CRITÉRIOS DE SUCESSO

### Métricas Mínimas de Aprovação

- **MAE**: < 1.5% do preço médio do WIN
- **Directional Accuracy**: > 55% (acima do acaso)
- **Sharpe Ratio**: > 1.0 (retorno ajustado ao risco)
- **Maximum Drawdown**: < 5% em backtesting

### Validações de Robustez

- **Estabilidade Temporal**: Performance consistente nos últimos 6 meses
- **Robustez a Volatilidade**: Manutenção de performance em períodos voláteis
- **Overfitting Check**: Diferença < 10% entre treino/validação/teste

## 🚀 IMPLEMENTAÇÃO PASSO-A-PASSO

### Passo 1: Configuração do Ambiente

```python
# Instalar dependências e configurar ambiente
# Verificar conectividade com fonte de dados WIN
```

### Passo 2: Coleta e Preparação de Dados

```python
# Coletar dados históricos WIN (2+ anos)
# Implementar feature engineering completo
# Criar datasets de treino/validação/teste
```

### Passo 3: Desenvolvimento de Modelos

```python
# Implementar modelos baseline
# Desenvolver modelos avançados
# Otimizar hyperparameters
```

### Passo 4: Avaliação e Validação

```python
# Calcular métricas de performance
# Executar backtesting
# Validar robustness
```

### Passo 5: Produção e Monitoramento

```python
# Salvar modelo otimizado
# Criar API de predição
# Implementar monitoramento contínuo
```

## ⚠️ CONSIDERAÇÕES IMPORTANTES

### Riscos e Limitações

- **Não é possível prever o mercado perfeitamente** - usar como ferramenta auxiliar
- **Dados históricos não garantem performance futura**
- **Considerar custos de transação** ao implementar estratégias
- **Validar regularmente** - retreinar modelo periodicamente

### Ética e Compliance

- **Divulgação clara**: Informar que é ferramenta auxiliar, não garantia
- **Gestão de risco**: Implementar stops e limites de perda
- **Transparência**: Documentar metodologia e limitações

### Próximas Iterações

- **Features Avançadas**: Sentimento de mercado, dados macroeconômicos
- **Modelos Ensemble**: Combinação de múltiplas abordagens
- **Predição Multi-step**: Previsão para múltiplos dias à frente
- **Inclusão de Outros Ativos**: Correlação com índices globais

---

## 📊 OUTPUT ESPERADO

Entregar:

1. **Modelo treinado** com performance documentada
2. **API de predição** funcional
3. **Relatório completo** com métricas e validações
4. **Código documentado** e testado
5. **Framework de monitoramento** para uso em produção

**PRAZO SUGERIDO**: 5-7 dias para implementação completa
**PRIORIDADE**: ALTA - Modelo WIN crítico para estratégias de trading
