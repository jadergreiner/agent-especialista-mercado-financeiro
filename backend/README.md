# Backend - Agent Especialista Mercado Financeiro

Backend Python para análise de mercado financeiro global.

## Estrutura

```
backend/
├── src/
│   ├── agents/          # Lógica do agente especialista
│   ├── data/            # Coleta e gestão de dados
│   ├── analysis/        # Análise técnica, fundamental, correlações
│   ├── strategies/      # Estratégias de trading
│   ├── risk/            # Gestão de risco
│   └── api/             # REST API (FastAPI)
├── tests/               # Testes
└── requirements.txt     # Dependências
```

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Desenvolvimento

```bash
# Rodar servidor de desenvolvimento
python main.py

# Rodar testes
pytest

# Linting
flake8 src/
black src/
```
