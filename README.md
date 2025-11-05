# Agent Especialista Mercado Financeiro 📈

Agente de IA especializado em análise de mercado financeiro global, com capacidade de análise de correlações, impacto de notícias, eventos econômicos e análise técnica para otimizar timing de posições.

## 🎯 Visão Geral

Este projeto implementa um especialista financeiro que combina:
- **Análise Fundamental**: Indicadores econômicos, earnings, política de bancos centrais
- **Análise Técnica**: Price action, volume, momentum, suporte/resistência
- **Análise de Correlações**: Relacionamentos entre mercados globais
- **Análise de Sentimento**: Notícias, redes sociais, posicionamento institucional
- **Gestão de Risco**: Position sizing, correlação de portfólio, controle de drawdown

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────┐
│          Frontend (Angular)                 │
│  - Dashboard de mercado                     │
│  - Visualização de correlações             │
│  - Alertas e recomendações                 │
└─────────────────────────────────────────────┘
                    ↕ REST API
┌─────────────────────────────────────────────┐
│          Backend (Python)                   │
│  - Coleta de dados de mercado              │
│  - Análise de correlações                  │
│  - Processamento de notícias               │
│  - Cálculo de indicadores técnicos         │
│  - Engine de decisão                       │
└─────────────────────────────────────────────┘
```

## 📁 Estrutura do Projeto

```
├── backend/                 # Backend Python
│   ├── src/
│   │   ├── agents/         # Lógica do agente especialista
│   │   ├── data/           # Coleta e gestão de dados
│   │   ├── analysis/       # Módulos de análise
│   │   ├── strategies/     # Estratégias de trading
│   │   ├── risk/           # Gestão de risco
│   │   └── api/            # REST API
│   ├── tests/              # Testes unitários e integração
│   ├── requirements.txt    # Dependências Python
│   └── main.py            # Entry point
│
├── frontend/               # Frontend Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # Componentes UI
│   │   │   ├── services/   # Serviços e API calls
│   │   │   └── models/     # Models TypeScript
│   │   └── assets/        # Assets estáticos
│   ├── package.json
│   └── angular.json
│
├── docs/                   # Documentação
├── .github/                # GitHub configs e workflows
└── README.md
```

## 🚀 Roadmap de Desenvolvimento

### Fase 1: Prototipagem (Atual)
- [x] Configuração inicial do repositório
- [x] Definição de arquitetura
- [ ] Interação via prompt para validação de conceitos
- [ ] Desenvolvimento de módulos core em Python

### Fase 2: Backend
- [ ] API de coleta de dados de mercado
- [ ] Sistema de análise de correlações
- [ ] Feed de notícias e análise de sentimento
- [ ] Calendário econômico
- [ ] Engine de análise técnica
- [ ] REST API

### Fase 3: Frontend
- [ ] Setup do projeto Angular
- [ ] Dashboard de mercado
- [ ] Visualização de correlações
- [ ] Sistema de alertas
- [ ] Gráficos interativos

### Fase 4: Integração e Produção
- [ ] Integração backend/frontend
- [ ] Sistema de autenticação
- [ ] Deploy e CI/CD
- [ ] Monitoring e logs

## 🛠️ Tecnologias

### Backend
- Python 3.11+
- FastAPI (REST API)
- Pandas, NumPy (análise de dados)
- TA-Lib (indicadores técnicos)
- yfinance, Alpha Vantage (dados de mercado)
- NLTK/spaCy (processamento de notícias)

### Frontend
- Angular 17+
- TypeScript
- Chart.js / TradingView (gráficos)
- RxJS (streams de dados)
- Material Design

## 📝 Fluxo de Desenvolvimento

- **Branch `develop`**: Desenvolvimento contínuo
- **Branch `main`**: Releases estáveis

```bash
# Trabalho diário
git checkout develop
git add .
git commit -m "descrição"

# Quando pacote está pronto
git checkout main
git merge develop
git checkout develop
```

## 🎓 Começando

### Uso via CLI (Recomendado)

O sistema possui uma interface de linha de comando intuitiva onde você pode fazer análises com comandos simples:

```bash
cd backend
python cli.py
```

Então basta digitar o ticker do ativo:
```
💬 Digite o ativo para análise: BTCUSD
```

**Exemplos de comandos:**
- `BTCUSD` - Análise completa de Bitcoin
- `PETR4 rapida` - Análise rápida de Petrobras
- `AAPL tecnica` - Análise técnica de Apple
- `ajuda` - Ver todos os comandos disponíveis

### Uso Programático

```python
from backend.src.agents.orquestrador_analise import OrquestradorAnalise, TipoAnalise

orquestrador = OrquestradorAnalise()

# Análise simples - apenas o ticker
resultado = orquestrador.analisar("BTCUSD")
print(resultado['recomendacao_geral'])

# Análise rápida
resultado = orquestrador.analisar("PETR4", TipoAnalise.RAPIDA)
```

Ver documentação completa em: [`docs/TEMPLATE_ANALISE.md`](docs/TEMPLATE_ANALISE.md)

## 📊 Casos de Uso

1. **Análise Rápida**: Digite apenas o ticker (ex: `BTCUSD`) e receba análise completa
2. **Análise Técnica**: Indicadores, tendências, suportes e resistências
3. **Análise de Correlação**: Relacionamentos entre ativos e mudanças de regime
4. **Timing de Posição**: Pontos ótimos de entrada/saída com gestão de risco
5. **Sentimento de Mercado**: Impacto de notícias e sentimento geral

## 📄 Licença

MIT License

---

**Status**: 🚧 Em Desenvolvimento - Fase de Prototipagem
