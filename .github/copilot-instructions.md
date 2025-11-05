# Copilot Instructions - Agent Especialista Mercado Financeiro

## Project Overview
This project implements an AI agent that assumes the role of a **Global Financial Market Expert**. The agent possesses deep market knowledge including correlations, news impact analysis, event-driven market movements, economic indicators, and combines this with technical analysis to calculate optimal timing for opening and closing positions.

## Core Expertise Areas
- **Multi-Market Correlation Analysis**: Understanding relationships between global markets (stocks, forex, commodities, crypto)
- **News Impact Assessment**: Real-time analysis of how news affects different asset classes
- **Event-Driven Trading**: Positioning around earnings, central bank meetings, economic releases
- **Technical Analysis Integration**: Combining fundamental analysis with technical indicators
- **Risk-Adjusted Timing**: Calculating optimal entry/exit points based on market conditions

## Development Guidelines

### Architecture Patterns
- **Modular Design**: Separate concerns into distinct modules (data collection, analysis, decision making, execution)
- **Event-Driven Architecture**: Use event streams for real-time market data processing
- **Strategy Pattern**: Implement trading strategies as pluggable components
- **Repository Pattern**: Abstract data sources (APIs, databases, market feeds)

### Key Components (to be implemented)
```
src/
├── agents/
│   ├── market_expert.py        # Core financial expert logic
│   ├── correlation_analyzer.py # Cross-market relationship analysis
│   └── timing_optimizer.py     # Entry/exit point calculator
├── data/
│   ├── news_feed.py           # Real-time news ingestion
│   ├── economic_calendar.py   # Event tracking and impact assessment
│   ├── market_data.py         # Multi-asset price feeds
│   └── sentiment_analysis.py  # Market sentiment from multiple sources
├── analysis/
│   ├── technical/             # Technical indicators and patterns
│   ├── fundamental/           # Economic and financial analysis
│   ├── correlation/           # Cross-asset correlation models
│   └── impact_models/         # News/event impact prediction
├── strategies/
│   ├── momentum/              # Trend-following strategies
│   ├── mean_reversion/        # Contrarian strategies
│   ├── event_driven/          # News/earnings-based strategies
│   └── arbitrage/             # Cross-market arbitrage opportunities
├── risk/
│   ├── position_sizing.py     # Dynamic position sizing
│   ├── correlation_risk.py    # Portfolio correlation management
│   └── drawdown_control.py    # Maximum loss protection
└── utils/
    ├── market_hours.py        # Global market session tracking
    ├── currency_converter.py  # Multi-currency calculations
    └── notification_system.py # Alert system for opportunities
```

### Financial Market Expert Conventions
- **Multi-Asset Precision**: Use Decimal for all financial calculations across asset classes
- **Global Time Coordination**: All timestamps in UTC, convert for local market analysis
- **Correlation Matrices**: Maintain rolling correlation windows (30d, 90d, 1y)
- **News Impact Scoring**: Quantify news sentiment and market impact (0-100 scale)
- **Risk-Adjusted Returns**: Always calculate Sharpe ratio, Sortino ratio, and max drawdown
- **Cross-Market Analysis**: Monitor forex, commodities, bonds impact on equity positions
- **Volatility Regimes**: Identify and adapt strategies to low/medium/high volatility periods

### Market Intelligence Data Flows
- **Real-Time Feeds**: Price data, news, economic releases, central bank communications
- **Correlation Updates**: Continuous monitoring of asset relationships and regime changes
- **Sentiment Integration**: Social media, options flow, institutional positioning data
- **Event Calendar**: Earnings, dividends, ex-dates, macro events, FOMC meetings
- **Technical Signals**: Multi-timeframe analysis from 1m to monthly charts

### Data Handling
- **Real-time vs Historical**: Clearly separate live trading from backtesting data
- **Data Validation**: Always validate market data before processing
- **Rate Limiting**: Respect API limits from financial data providers
- **Caching Strategy**: Cache static data (company info) but not dynamic (prices)

### Security & Compliance
- **API Keys**: Use environment variables, never commit secrets
- **Position Limits**: Implement maximum position and loss limits
- **Regulatory Compliance**: Follow local trading regulations
- **Data Privacy**: Handle user financial data according to regulations

### Testing Patterns
- **Mock Market Data**: Use deterministic data for unit tests
- **Backtesting Framework**: Test strategies against historical data
- **Paper Trading**: Test in production environment without real money
- **Performance Metrics**: Track Sharpe ratio, max drawdown, win rate

### Common Integrations
- Market data providers (Alpha Vantage, Yahoo Finance, Bloomberg API)
- Brokerage APIs (Alpaca, Interactive Brokers, TD Ameritrade)
- Technical analysis libraries (TA-Lib, pandas-ta)
- Machine learning frameworks (scikit-learn, TensorFlow, PyTorch)

### Expert Analysis Workflows
- **Market Open Routine**: Pre-market analysis, overnight developments, gap analysis
- **Intraday Monitoring**: Real-time correlation shifts, news impact assessment
- **Position Timing**: Entry/exit optimization based on technical and fundamental confluence
- **Risk Assessment**: Continuous portfolio correlation and exposure monitoring
- **Market Close Review**: Performance attribution, lesson learning, next-day preparation

### Decision-Making Framework
- **Fundamental Layer**: Economic indicators, earnings, central bank policy
- **Technical Layer**: Price action, volume, momentum, support/resistance
- **Sentiment Layer**: Market positioning, fear/greed index, options flow
- **Correlation Layer**: Cross-asset relationships, sector rotation, global spillovers
- **Risk Layer**: Position sizing, portfolio heat, maximum adverse excursion

### Error Handling
- **Market Connectivity**: Gracefully handle API outages
- **Data Quality**: Detect and handle bad ticks/outliers
- **Order Failures**: Implement retry logic with exponential backoff
- **Portfolio Protection**: Emergency stop-loss mechanisms

## Development Notes
This is a foundational template. Update these instructions as the codebase evolves with:
- Specific API integrations implemented
- Chosen programming language and frameworks
- Actual file structure and naming conventions
- Custom business logic and trading strategies
- Performance optimization patterns discovered