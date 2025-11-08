# Origin: FEAT-001 - MVP Dashboard Público

# Dashboard Executivo - Meu Home

Este é o MVP do dashboard público do Agent Especialista Mercado Financeiro.

## Funcionalidades

- 📊 **Métricas Principais**: Valor total do portfólio, P&L total e número de posições ativas
- 📈 **Gráfico P&L**: Evolução do lucro/prejuízo nos últimos 30 dias
- 📋 **Tabela de Posições**: Lista detalhada de todas as posições com P&L individual

## Como Executar Localmente

### Pré-requisitos

- Python 3.8+
- Dependências instaladas: `pip install -r requirements.txt`

### Passos

1. **Iniciar Backend API**:

   ```bash
   cd backend/api
   python dashboard.py
   ```

   A API ficará disponível em `http://localhost:8000`

2. **Iniciar Frontend Dashboard**:

   ```bash
   streamlit run frontend/dashboard.py
   ```

   O dashboard ficará disponível em `http://localhost:8501`

3. **Acessar**: Abra `http://localhost:8501` no navegador

## API Endpoints

- `GET /api/v1/dashboard/summary`: Retorna dados do dashboard (posições, P&L, histórico)

## Testes

Para executar testes E2E:

```bash
# Instalar dependências de teste
pip install pytest-playwright
playwright install chromium

# Executar testes
pytest tests/e2e/test_dashboard.py -v
```

## Arquitetura

- **Backend**: FastAPI com dados mock (para MVP)
- **Frontend**: Streamlit para interface rápida
- **Dados**: Mock estáticos (substituir por dados reais em produção)

## Próximos Passos

- Integrar com dados reais do backend
- Adicionar autenticação
- Melhorar UI/UX
- Adicionar mais gráficos e métricas