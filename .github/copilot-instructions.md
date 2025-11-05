# Instruções Copilot - Agent Especialista Mercado Financeiro

## ⚠️ REGRA FUNDAMENTAL
**TODO O CÓDIGO, DOCUMENTAÇÃO, COMENTÁRIOS, COMMITS E INTERAÇÕES DEVEM SER EM PORTUGUÊS.**
- Nomes de variáveis, funções, classes: Português
- Docstrings e comentários: Português
- Mensagens de commit: Português
- Documentação: Português
- Logs e mensagens de erro: Português

## Visão Geral do Projeto
Este projeto implementa um agente de IA que assume o papel de **Especialista Global de Mercado Financeiro**. O agente possui conhecimento profundo do mercado incluindo correlações, análise de impacto de notícias, movimentos de mercado orientados por eventos, indicadores econômicos, e combina isso com análise técnica para calcular o timing ótimo para abertura e fechamento de posições.

## Áreas de Especialização Central
- **Análise de Correlação Multi-Mercado**: Compreensão de relacionamentos entre mercados globais (ações, forex, commodities, crypto)
- **Avaliação de Impacto de Notícias**: Análise em tempo real de como notícias afetam diferentes classes de ativos
- **Trading Orientado por Eventos**: Posicionamento em torno de earnings, reuniões de bancos centrais, releases econômicos
- **Integração de Análise Técnica**: Combinando análise fundamental com indicadores técnicos
- **Timing Ajustado ao Risco**: Calculando pontos ótimos de entrada/saída baseados em condições de mercado

## Diretrizes de Desenvolvimento

### Padrões de Nomenclatura
```python
# Classes: PascalCase em Português
class AnalisadorCorrelacao:
    pass

# Funções e métodos: snake_case em Português
def calcular_correlacao_mercado():
    pass

# Variáveis: snake_case em Português
preco_ativo = 100.50
indice_correlacao = 0.85

# Constantes: UPPER_CASE em Português
PERIODO_PADRAO_DIAS = 90
LIMITE_RISCO_MAXIMO = 0.02
```

### Padrões de Arquitetura
- **Design Modular**: Separar responsabilidades em módulos distintos (coleta de dados, análise, tomada de decisão, execução)
- **Arquitetura Orientada a Eventos**: Usar streams de eventos para processamento de dados de mercado em tempo real
- **Padrão Strategy**: Implementar estratégias de trading como componentes plugáveis
- **Padrão Repository**: Abstrair fontes de dados (APIs, databases, feeds de mercado)

### Componentes Principais (a serem implementados)
```
src/
├── agentes/
│   ├── especialista_mercado.py        # Lógica central do especialista financeiro
│   ├── analisador_correlacao.py      # Análise de relacionamentos entre mercados
│   └── otimizador_timing.py          # Calculador de pontos de entrada/saída
├── dados/
│   ├── feed_noticias.py              # Ingestão de notícias em tempo real
│   ├── calendario_economico.py       # Rastreamento e avaliação de impacto de eventos
│   ├── dados_mercado.py              # Feeds de preços multi-ativos
│   └── analise_sentimento.py        # Sentimento de mercado de múltiplas fontes
├── analise/
│   ├── tecnica/                      # Indicadores técnicos e padrões
│   ├── fundamentalista/              # Análise econômica e financeira
│   ├── correlacao/                   # Modelos de correlação entre ativos
│   └── modelos_impacto/              # Predição de impacto de notícias/eventos
├── estrategias/
│   ├── momentum/                     # Estratégias de seguimento de tendência
│   ├── reversao_media/               # Estratégias contrárias
│   ├── orientadas_eventos/           # Estratégias baseadas em notícias/earnings
│   └── arbitragem/                   # Oportunidades de arbitragem entre mercados
├── risco/
│   ├── dimensionamento_posicao.py    # Dimensionamento dinâmico de posição
│   ├── risco_correlacao.py           # Gestão de correlação de portfólio
│   └── controle_drawdown.py          # Proteção contra perda máxima
└── utils/
    ├── horarios_mercado.py           # Rastreamento de sessões de mercado globais
    ├── conversor_moeda.py            # Cálculos multi-moeda
    └── sistema_notificacao.py        # Sistema de alertas para oportunidades
```

### Convenções do Especialista de Mercado Financeiro
- **Precisão Multi-Ativos**: Usar Decimal para todos os cálculos financeiros entre classes de ativos
- **Coordenação de Tempo Global**: Todos os timestamps em UTC, converter para análise de mercado local
- **Matrizes de Correlação**: Manter janelas de correlação rolantes (30d, 90d, 1a)
- **Pontuação de Impacto de Notícias**: Quantificar sentimento de notícias e impacto no mercado (escala 0-100)
- **Retornos Ajustados ao Risco**: Sempre calcular índice de Sharpe, índice de Sortino e drawdown máximo
- **Análise Entre Mercados**: Monitorar impacto de forex, commodities, bonds em posições de ações
- **Regimes de Volatilidade**: Identificar e adaptar estratégias a períodos de baixa/média/alta volatilidade

### Fluxos de Inteligência de Mercado
- **Feeds em Tempo Real**: Dados de preço, notícias, releases econômicos, comunicações de bancos centrais
- **Atualizações de Correlação**: Monitoramento contínuo de relacionamentos de ativos e mudanças de regime
- **Integração de Sentimento**: Redes sociais, fluxo de opções, dados de posicionamento institucional
- **Calendário de Eventos**: Earnings, dividendos, ex-dates, eventos macro, reuniões do FOMC
- **Sinais Técnicos**: Análise multi-timeframe de 1m até gráficos mensais

### Tratamento de Dados
- **Tempo Real vs Histórico**: Separar claramente trading ao vivo de dados de backtesting
- **Validação de Dados**: Sempre validar dados de mercado antes do processamento
- **Limitação de Taxa**: Respeitar limites de API dos provedores de dados financeiros
- **Estratégia de Cache**: Cachear dados estáticos (info de empresas) mas não dinâmicos (preços)

### Segurança e Conformidade
- **Chaves de API**: Usar variáveis de ambiente, nunca commitar secrets
- **Limites de Posição**: Implementar limites máximos de posição e perda
- **Conformidade Regulatória**: Seguir regulamentações locais de trading
- **Privacidade de Dados**: Tratar dados financeiros do usuário de acordo com regulamentações

### Padrões de Teste
- **Dados de Mercado Mock**: Usar dados determinísticos para testes unitários
- **Framework de Backtesting**: Testar estratégias contra dados históricos
- **Paper Trading**: Testar em ambiente de produção sem dinheiro real
- **Métricas de Performance**: Rastrear índice de Sharpe, drawdown máximo, taxa de acerto

### Integrações Comuns
- Provedores de dados de mercado (Alpha Vantage, Yahoo Finance, Bloomberg API)
- APIs de corretoras (Alpaca, Interactive Brokers, TD Ameritrade)
- Bibliotecas de análise técnica (TA-Lib, pandas-ta)
- Frameworks de machine learning (scikit-learn, TensorFlow, PyTorch)

### Fluxos de Trabalho de Análise Expert
- **Rotina de Abertura do Mercado**: Análise pré-mercado, desenvolvimentos noturnos, análise de gaps
- **Monitoramento Intraday**: Mudanças de correlação em tempo real, avaliação de impacto de notícias
- **Timing de Posições**: Otimização de entrada/saída baseada em confluência técnica e fundamental
- **Avaliação de Risco**: Monitoramento contínuo de correlação e exposição do portfólio
- **Revisão de Fechamento**: Atribuição de performance, aprendizado de lições, preparação para o próximo dia

### Framework de Tomada de Decisão
- **Camada Fundamental**: Indicadores econômicos, earnings, política de bancos centrais
- **Camada Técnica**: Price action, volume, momentum, suporte/resistência
- **Camada de Sentimento**: Posicionamento de mercado, índice de medo/ganância, fluxo de opções
- **Camada de Correlação**: Relacionamentos entre ativos, rotação setorial, spillovers globais
- **Camada de Risco**: Dimensionamento de posição, calor do portfólio, excursão adversa máxima

### Tratamento de Erros
- **Conectividade de Mercado**: Tratar graciosamente quedas de API
- **Qualidade de Dados**: Detectar e tratar ticks ruins/outliers
- **Falhas de Ordem**: Implementar lógica de retry com backoff exponencial
- **Proteção de Portfólio**: Mecanismos de stop-loss emergenciais

## Notas de Desenvolvimento
Este é um template fundacional. Atualize estas instruções conforme o código evolui com:
- Integrações de API específicas implementadas
- Linguagem de programação e frameworks escolhidos
- Estrutura de arquivos e convenções de nomenclatura reais
- Lógica de negócio customizada e estratégias de trading
- Padrões de otimização de performance descobertos