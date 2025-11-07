# Agent Especialista Mercado Financeiro

Plataforma de IA que atua como Especialista Global de Mercado Financeiro: integra dados de mercado, estratégias de trading, execução em corretoras e monitoramento de portfólio com foco em timing ótimo e gestão de risco.

## ✅ Principais Capacidades

- Integração com Corretoras (Alpaca, IB, Simulado)
- Trading Automatizado (estratégias plugáveis: média móvel, RSI, etc.)
- Monitor de Portfólio (P&L, Sharpe, drawdown, volatilidade, alertas)
- Dashboard Web (Flask + Plotly) opcional
- Persistência (SQLite) e configuração por JSON

## 🏗️ Arquitetura (alto nível)

```text
src/backend
├── integracao_corretoras.py       # Conectores e gerenciador (APIs e ordens)
├── trading_automatizado.py        # Estratégias e execução de sinais
├── monitor_portfolio.py           # Métricas, alertas e (opcional) Web
└── sistema_integrado_trading.py   # Orquestrador

config
├── corretoras.json                # Credenciais e endpoints
├── estrategias.json               # Parâmetros de estratégias
└── sistema_trading.json           # Configuração geral

data
├── integracao_corretoras.db
├── trading_automatizado.db
└── monitor_portfolio.db
```

Referências detalhadas:

- docs/INTEGRACAO_CORRETORAS.md — Guia completo da integração com corretoras
- docs/USO_EM_PRODUCAO.md — Passo a passo de uso em produção (Windows)
- docs/GUIA_ANALISTA_FINANCEIRO.md — Guia prático para o Analista

## ⚡ Início Rápido (Windows)

1) Crie e ative o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2) Instale as dependências mínimas

```powershell
pip install -r requirements.txt
```

3) Gere/valide configuração e rode uma demo

```powershell
python backend/instalar_integracao_corretoras.py
python backend/sistema_integrado_trading.py --demo
```

4) Execute o sistema completo

```powershell
python backend/sistema_integrado_trading.py
```

Observação: para uso de corretoras reais, edite `config/corretoras.json` e ative paper/live conforme a política da sua conta.

## 🔧 Configuração e Segredos

- Configuração padrão em JSON (pasta `config/`).
- Segredos devem ficar em variáveis de ambiente (.env). Exemplo: `config/.env.example`.
- Em breve: leitura de `.env` priorizada pelo sistema (ver backlog).

## 🛡️ Risco e Conformidade

- Use paper trading antes de operar em produção.
- Defina limites de risco (stop loss, take profit, perda diária).
- Siga a conformidade de sua jurisdição e da corretora.

## 📦 Scripts Úteis

- `backend/sistema_integrado_trading.py --demo` — Demonstrar fluxo ponta-a-ponta em modo simulado
- `backend/instalar_integracao_corretoras.py` — Verificar/instalar dependências e criar configs

## 🧭 Próximos Passos

Consulte:

- docs/USO_EM_PRODUCAO.md — Guia para colocar no ar (serviço/tarefa agendada)
- docs/GUIA_ANALISTA_FINANCEIRO.md — Como o Analista usa o agente no dia a dia

## 📄 Licença

Projeto educacional/experimental. Avalie requisitos regulatórios antes de uso real.
# 💰 Agent Especialista Mercado Financeiro

**Sistema multi-agente de análise de investimentos com foco em renda passiva sustentável.**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## 🎯 Visão Geral

Este projeto implementa agentes de IA especializados em análise de mercado financeiro, combinando:
- 🌍 **Análise Multi-Mercado**: Forex, Ações, Commodities, Crypto
- 📊 **Análise Fundamentalista**: Dividendos, lucros, saúde financeira
- 🔄 **Análise de Correlação**: Relacionamentos entre ativos
- ⏰ **Timing de Entrada/Saída**: Pontos ótimos de operação

**Diferencial:** Todos os agentes priorizam **sustentabilidade** e **gestão de risco**, não apenas retorno máximo.

---

## 🚀 Módulos Disponíveis

### 1. 💵 Forex Multi-Par (42 Pares)

Análise de 42 pares de moedas com 5 pilares fundamentalistas.

**Comando:**
```bash
python backend\monitor_forex.py --top 10 --categorias
```

**Saída:**
```
🥇 USD/JPY: 70% confiança (Diferencial +250 bps, Risco OFF, Inflação divergente)
🥈 AUD/JPY: 67% confiança
🥉 GBP/JPY: 67% confiança
```

**Documentação:** [FOREX_SISTEMA_COMPLETO.md](backend/docs/FOREX_SISTEMA_COMPLETO.md)

---

### 2. 📈 Análise de Dividendos (Ações B3)

Seleção de ações pagadoras de dividendos com base em **sustentabilidade**, não apenas yield.

**Comando:**
```bash
python backend\consultar_dividendos.py analisar TGMA3 GOAU4 GGBR4
```

**Saída:**
```
🥇 TGMA3: 83/100 (COMPRA_FORTE)
   - Sustentabilidade: 90/100 (LPA ESTÁVEL, dividendos CONSISTENTES)
   - Saúde: 100/100 (Liquidez 2.61, caixa POSITIVA)
   - Valor: 50/100 (Preço acima do ideal)
```

**Documentação:** [DIVIDENDOS_ANALISE.md](backend/docs/DIVIDENDOS_ANALISE.md)

---

### 3. 🏢 Análise de FIIs (Fundos Imobiliários)

Análise de FIIs priorizando **qualidade dos ativos** e **sustentabilidade dos rendimentos**.

**Comando:**
```bash
python backend\consultar_fiis.py analisar KNRI11 HGLG11 MXRF11
```

**Saída:**
```
🥇 KNRI11: 82/100 (COMPRA_FORTE)
   - Qualidade: 80/100 (Papel, IPCA+, diversificação MÉDIA)
   - Valuation: 80/100 (P/VP 0.91 - desconto 9.1%)
   - Rendimento: 90/100 (DY 8.24%, CONSISTENTE)
```

**Documentação:** [FIIS_ANALISE.md](backend/docs/FIIS_ANALISE.md)

---

## 📖 Guia de Uso Rápido

### Forex: Monitor 42 Pares

```powershell
# Top 15 oportunidades
python backend\monitor_forex.py --top 15

# Análise por categoria (Majors, Crosses, Exóticos)
python backend\monitor_forex.py --categorias

# Exportar para CSV
python backend\monitor_forex.py --top 10 --exportar
```

### Dividendos: Análise Comparativa

```powershell
# Análise completa (tabela + relatório)
python backend\consultar_dividendos.py analisar TGMA3 KLBN11 GGBR4

# Ranking simples
python backend\consultar_dividendos.py ranking TGMA3 KLBN11 GGBR4 --top 5

# Análise por setor
python backend\consultar_dividendos.py setor bancos
```

### FIIs: Análise de Fundos Imobiliários

```powershell
# Análise completa (tabela + relatório)
python backend\consultar_fiis.py analisar KNRI11 HGLG11 MXRF11

# Ranking com top 5
python backend\consultar_fiis.py ranking KNRI11 HGLG11 MXRF11 VISC11 --top 5

# Comparação direta de 2 FIIs
python backend\consultar_fiis.py comparar KNRI11 MXRF11

# Análise por setor
python backend\consultar_fiis.py setor logistica
```

---

## 🔬 Metodologia

### Forex (5 Pilares Fundamentalistas)

1. **Diferencial de Juros**: BCs elevam/reduzem taxas → impacto na moeda
2. **Inflação Relativa**: Inflação alta degrada moeda
3. **Saldo Comercial**: Superávit fortalece moeda
4. **PIB Relativo**: Crescimento atrai investimento
5. **Sentimento de Risco**: Risk ON/OFF global

**Peso:** 20% cada pilar = 100%

**Documentação:** [forex_fundamentals.py](backend/src/dados/forex_fundamentals.py)

---

### Dividendos (3 Pilares)

1. **Sustentabilidade (40%)**: Histórico LPA + consistência dividendos
2. **Saúde Financeira (35%)**: Liquidez corrente + geração caixa
3. **Valor (25%)**: Margem de segurança + DY + P/L

**Preços-Alvo:**
```
Preço Teto = dividendos_medio_5anos / 0.06  (DY 6%)
Preço Ideal = dividendos_medio_5anos / 0.08 (DY 8%)
```

**Documentação:** [analisador_dividendos.py](backend/src/dados/analisador_dividendos.py)

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
│   │   │   ├── especialista_mercado.py
│   │   │   └── orquestrador_analise.py
│   │   ├── utils/          # Utilitários
│   │   │   └── gerenciador_modelos.py  # Gerencia templates YAML
│   │   ├── data/           # Coleta e gestão de dados (futuro)
│   │   ├── analysis/       # Módulos de análise (futuro)
│   │   ├── strategies/     # Estratégias de trading (futuro)
│   │   └── risk/           # Gestão de risco (futuro)
│   ├── cli.py              # Interface linha de comando
│   ├── main.py             # API FastAPI
│   └── requirements.txt    # Dependências Python
│
├── modelos/                 # Templates YAML de saída
│   ├── forex_rapida.yaml
│   ├── cripto_futuros_tecnica.yaml
│   ├── acoes_fundamental.yaml
│   └── cripto_completa.yaml
│
├── docs/                   # Documentação
│   ├── TEMPLATE_ANALISE.md           # Guia de uso do sistema
│   ├── PADROES_DOCUMENTACAO.md       # Padrões de código
│   └── INTEGRACAO_MODELOS_YAML.md    # Arquitetura de modelos
│
├── frontend/               # Frontend Angular (futuro)
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

## � Arquitetura de Modelos

O sistema utiliza templates YAML para definir a estrutura de saída de cada tipo de análise:

- **Flexibilidade**: Adicionar novos tipos sem modificar código
- **Padronização**: Estruturas consistentes para todas as análises
- **Escalabilidade**: Fácil expansão para novos mercados

Ver documentação completa: [`docs/INTEGRACAO_MODELOS_YAML.md`](docs/INTEGRACAO_MODELOS_YAML.md)

## �📄 Licença

MIT License

---

**Status**: 🚧 Em Desenvolvimento - Fase de Prototipagem

**Última atualização**: Sistema integrado com modelos YAML flexíveis ✅

---

## 📋 Gestão Ágil e Documentação

Sempre que uma História de Usuário for concluída, atualizar:

- `docs/diario-projeto.md` — progresso diário e marcos
- `docs/CHANGELOG.md` — mudanças relevantes por data
- `docs/ROADMAP.md` — visão curto/médio/longa
- `docs/gestao-agil/backlog.md` — tarefas priorizadas e status
- `docs/gestao-agil/organizacao_agil.md` — hierarquia ágil e políticas de busca/uso de tokens

Referência rápida:

- Organização Ágil: [`docs/gestao-agil/organizacao_agil.md`](docs/gestao-agil/organizacao_agil.md)
- Backlog: [`docs/gestao-agil/backlog.md`](docs/gestao-agil/backlog.md)
- Roadmap: [`docs/ROADMAP.md`](docs/ROADMAP.md)
- Changelog: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
