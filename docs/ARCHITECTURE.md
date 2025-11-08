# Arquitetura do Sistema

## Visão Geral

O Agent Especialista de Mercado Financeiro é composto por duas partes principais:

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (Angular)                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Dashboard  │  │  Análise   │  │   Alertas  │            │
│  │  Market    │  │ Correlação │  │  e Timing  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└──────────────────────────────────────────────────────────────┘
                          │ REST API (JSON)
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                     BACKEND (Python)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Market Expert Agent                       │ │
│  │  - Lógica de decisão                                  │ │
│  │  - Coordenação de análises                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Data   │  │ Analysis │  │Strategies│  │   Risk   │   │
│  │ Collectors│  │  Engine  │  │  Engine  │  │  Manager │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES & DATA SOURCES                │
│  - Yahoo Finance / Alpha Vantage (preços)                   │
│  - News APIs (notícias e sentimento)                        │
│  - Economic Calendars (eventos)                             │
│  - Broker APIs (execução - futuro)                          │
└──────────────────────────────────────────────────────────────┘

## Sistema de Aprendizado Contínuo

### Visão Geral
O sistema incorpora aprendizado contínuo baseado em feedback de performance real, criando um loop de melhoria iterativa que adapta o agente às condições de mercado em evolução.

```
┌──────────────────────────────────────────────────────────────┐
│              CONTINUOUS LEARNING SYSTEM                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Performance     │  │ Dynamic Weight  │  │ Learning    │ │
│  │ Analysis Engine │  │ Adjustment      │  │ Database    │ │
│  │                 │  │ Framework       │  │             │ │
│  │ - Prompt-based  │  │ - Auto-tuning   │  │ - SQLite     │ │
│  │ - Structured    │  │ - Historical    │  │ - Metrics    │ │
│  │ - Comparative   │  │ - Confidence    │  │ - Audit      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              LEARNING FEEDBACK LOOP                  │ │
│  │  Recommendation → Validation → Analysis → Adjustment │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Componentes Principais

#### Performance Analysis Engine
- **Prompt Estruturado**: Análise sistemática previsto vs real
- **Comparação Multi-dimensional**: Probabilidade, timeframe, catalisadores, risco
- **Extração de Aprendizados**: Pontos positivos, melhorias, calibração
- **Relatórios Estruturados**: Output padronizado para tomada de decisão

#### Dynamic Weight Adjustment Framework
- **Pesos Adaptativos**: Ajuste automático baseado em performance
- **Histórico Auditável**: Registro completo de evoluções
- **Normalização Automática**: Manutenção de equilíbrio do sistema
- **Confiança Variável**: Níveis de confiança por tipo de ajuste

#### Learning Database
- **Tabela `analises_performance`**: Armazenamento estruturado de aprendizados
- **Métricas Consolidadas**: Taxa de acerto, evolução de pesos
- **Histórico Temporal**: Evolução do sistema ao longo do tempo
- **Dashboard Integrado**: Visualização de métricas de aprendizado

### Fluxo de Aprendizado

1. **Geração de Recomendação**: Sistema emite sinal baseado em pesos atuais
2. **Execução e Validação**: Trade é executado e resultado é observado
3. **Análise de Performance**: Prompt estruturado compara previsto vs real
4. **Extração de Aprendizados**: Sistema identifica pontos positivos/melhorias
5. **Ajuste de Pesos**: Framework aplica modificações baseadas em aprendizados
6. **Registro Histórico**: Todo ciclo é armazenado para auditoria futura

### Benefícios Arquiteturais

- **Adaptação Contínua**: Sistema evolui com condições de mercado
- **Auto-otimização**: Melhoria automática baseada em feedback real
- **Robustez**: Capacidade de adaptação a regimes de mercado diferentes
- **Transparência**: Histórico completo de evoluções e decisões
- **Escalabilidade**: Framework extensível para novos mercados/ativos

## Fluxo de Dados

### 1. Coleta de Dados (Data Layer)
- **Market Data**: Preços em tempo real e históricos
- **News Feed**: Notícias financeiras de múltiplas fontes
- **Economic Calendar**: Eventos econômicos agendados
- **Sentiment Data**: Análise de sentimento de mercado

### 2. Análise (Analysis Layer)
- **Technical Analysis**: Indicadores técnicos, padrões, suporte/resistência
- **Fundamental Analysis**: Análise de indicadores econômicos
- **Correlation Analysis**: Relacionamentos entre ativos
- **Sentiment Analysis**: Processamento de notícias e sentimento

### 3. Decisão (Agent Layer)
- **Market Expert Agent**: Coordena todas as análises
- **Decision Engine**: Combina inputs para gerar recomendações
- **Timing Optimizer**: Calcula pontos ótimos de entrada/saída

### 4. Execução e Apresentação
- **API Layer**: Expõe funcionalidades via REST API
- **Frontend**: Apresenta dados e permite interação
- **Alerts**: Sistema de notificações (futuro)

## Componentes Principais

### Backend Python

#### Market Expert Agent
- **Responsabilidade**: Lógica central de decisão
- **Inputs**: Dados de mercado, notícias, análises técnicas
- **Outputs**: Recomendações, análises de correlação, timing

#### Data Collectors
- **Market Data Collector**: yfinance, Alpha Vantage
- **News Collector**: RSS feeds, News APIs
- **Economic Calendar**: Calendario de eventos

#### Analysis Engine
- **Technical Analyzer**: TA-Lib, pandas-ta
- **Correlation Analyzer**: Cálculo de correlações rolling
- **Sentiment Analyzer**: NLP para análise de notícias

#### Risk Manager
- **Position Sizing**: Cálculo de tamanho de posição
- **Portfolio Correlation**: Gestão de correlações
- **Drawdown Control**: Proteção contra perdas

### Frontend Angular

#### Dashboard Component
- Visão geral do mercado
- Principais índices e ativos
- Sentimento geral

#### Analysis Components
- Gráficos de correlação
- Análise técnica visual
- Impacto de notícias

#### Alerts System
- Notificações de oportunidades
- Alertas de risco
- Eventos importantes

## Decisões de Arquitetura

### Por que FastAPI?
- Performance excelente para APIs
- Type hints nativos (integração com Pydantic)
- Documentação automática (Swagger/OpenAPI)
- Async support para websockets futuros

### Por que Angular?
- Framework completo e estruturado
- TypeScript forte (type safety)
- Ecosystem robusto para componentes financeiros
- RxJS para streaming de dados real-time

### Por que Python para Backend?
- Ecossistema rico para análise financeira
- Pandas, NumPy para manipulação de dados
- TA-Lib para análise técnica
- NLTK/spaCy para NLP
- Integração fácil com ML/AI

## Fluxo de Desenvolvimento

### Fase Atual: Prototipagem via Prompt
- Validação de conceitos
- Desenvolvimento de core logic
- Testes de estratégias

### Próximas Fases
1. **Backend MVP**: API básica + coleta de dados
2. **Analysis Engine**: Implementação de análises
3. **Frontend Setup**: Dashboard básico
4. **Integração**: Backend + Frontend
5. **Produção**: Deploy e monitoring

## Escalabilidade Futura

### Considerations
- **Caching**: Redis para dados de mercado
- **Queue System**: Celery para processamento assíncrono
- **Database**: PostgreSQL para armazenamento histórico
- **Websockets**: Para atualizações real-time
- **Microservices**: Separação por domínio quando necessário
