# Convenções de Nomenclatura - Especialista Mercado Financeiro

## Padrão Geral

- **Linguagem**: Português
- **Estilo**: snake_case para variáveis/funções, PascalCase para classes
- **Prefixos/Sufixos**: Evitar, usar nomes descritivos

## Arquivos Python

### Estrutura de Nomenclatura

```bash
# ✅ CORRETO
portfolio_service.py      # Serviço de negócio
position_repository.py    # Acesso a dados
risk_calculator.py        # Lógica de cálculo
market_data_client.py     # Integração externa

# ❌ ERRADO
monitor_portfolio.py      # Muito genérico
analisador_risco.py       # Verbo no nome
consultar_posicoes.py     # Ação no nome
```

### Classes
```python
# ✅ Serviços de Negócio
class PortfolioIntelligenceService:
    pass

class RiskAssessmentService:
    pass

# ✅ Repositórios
class PositionRepository:
    pass

class AlertRepository:
    pass

# ✅ Utilitários
class MarketDataClient:
    pass

class CacheManager:
    pass
```

### Funções e Métodos
```python
# ✅ Ações claras
def calcular_retorno_total():
    pass

def obter_posicoes_abertas():
    pass

def validar_parametros_entrada():
    pass

# ❌ Genérico
def processar():
    pass

def fazer_algo():
    pass
```

### Variáveis
```python
# ✅ Descritivas
preco_atual = 100.50
quantidade_posicao = 1000
retorno_diario = 0.025

# ❌ Abreviações
prc_at = 100.50
qtd_pos = 1000
ret_dia = 0.025
```

## Banco de Dados

### Tabelas
```sql
-- ✅ Correto
users
portfolio_positions
risk_alerts
market_data_feeds

-- ❌ Errado
tbl_users
POSITIONS
riskAlerts
```

### Colunas
```sql
-- ✅ Correto
user_id
created_at
updated_at
is_active

-- ❌ Errado
userid
date_created
active_flag
```

## APIs REST

### Endpoints
```
/api/v1/portfolio/positions    # ✅
/api/v1/users/{id}/alerts      # ✅
/api/v1/market-data/quotes     # ✅

/api/getPositions             # ❌
/api/userAlerts               # ❌
```

### Parâmetros
```python
# ✅ Query Parameters
?user_id=123&limit=50&offset=0

# ✅ Path Parameters
/users/{user_id}/positions/{position_id}
```

## Testes

### Arquivos de Teste
```
test_portfolio_service.py
test_risk_calculator.py
test_position_repository.py
```

### Funções de Teste
```python
def test_calcular_retorno_positivo():
    pass

def test_validar_parametros_invalidos():
    pass
```

## Constantes
```python
# ✅ Grupo de constantes
class PortfolioConstants:
    LIMITE_POSICAO_MAXIMA = 1000000
    TAXA_OPERACIONAL_PADRAO = 0.001
    HORARIO_MERCADO_ABERTURA = "09:00"
    HORARIO_MERCADO_FECHAMENTO = "18:00"

# ✅ Prefixo descritivo
RISCO_MAXIMO_PERMITIDO = 0.02
PERIODO_ANALISE_PADRAO = 90  # dias
```

## Exceções Personalizadas
```python
class PortfolioError(Exception):
    pass

class RiskThresholdExceededError(PortfolioError):
    pass

class InsufficientFundsError(PortfolioError):
    pass
```

## Logs e Mensagens
```python
# ✅ Estruturado
logger.info("Posição aberta: ticker=%s, quantidade=%d, preço=%.2f",
           ticker, quantity, price)

# ✅ Categorias claras
logger.warning("Alerta de risco: posição %s excedeu limite", position_id)
logger.error("Falha na integração: %s", error_message)
```

## Configurações
```python
# config/settings.py
class DatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str

class APISettings:
    base_url: str
    timeout: int
    retries: int
```

## Validação de Conformidade

### Ferramentas Automáticas
- **Black**: Formatação automática
- **Flake8**: Lint de estilo
- **MyPy**: Verificação de tipos
- **Pre-commit hooks**: Validação pré-commit

### Checklist de Code Review
- [ ] Nomes seguem convenções estabelecidas
- [ ] Não há abreviações desnecessárias
- [ ] Funções têm uma responsabilidade clara
- [ ] Classes representam conceitos de negócio bem definidos
- [ ] Testes seguem mesmo padrão de nomenclatura

## Migração Gradual

### Fase 1: Documentação
- Criar este guia
- Treinar equipe
- Identificar arquivos prioritários

### Fase 2: Refatoração Core
- Renomear arquivos críticos primeiro
- Atualizar imports relacionados
- Validar testes passam

### Fase 3: Expansão
- Renomear arquivos restantes
- Padronizar novos desenvolvimentos
- Code review rigoroso

### Fase 4: Manutenção
- Monitorar novos códigos
- Atualizar guia conforme necessário
- Reforçar em treinamentos