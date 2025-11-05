# Padrões de Documentação e Código

## 🌐 Idioma Universal: PORTUGUÊS

**REGRA ABSOLUTA**: Todo código, documentação, comentários, commits, issues, PRs e comunicações DEVEM ser em Português do Brasil.

## 📝 Nomenclatura de Código

### Classes
```python
# ✅ CORRETO - PascalCase em Português
class AnalisadorMercado:
    pass

class GerenciadorRisco:
    pass

class EspecialistaMercadoFinanceiro:
    pass

# ❌ ERRADO - Inglês
class MarketAnalyzer:  # NÃO FAZER
    pass
```

### Funções e Métodos
```python
# ✅ CORRETO - snake_case em Português
def calcular_correlacao(ativo1: str, ativo2: str) -> float:
    pass

def obter_dados_mercado(ticker: str) -> dict:
    pass

def analisar_impacto_noticia(manchete: str) -> dict:
    pass

# ❌ ERRADO - Inglês
def calculate_correlation():  # NÃO FAZER
    pass
```

### Variáveis
```python
# ✅ CORRETO - snake_case em Português
preco_ativo = 150.50
indice_correlacao = 0.85
lista_ativos = ["PETR4", "VALE3", "ITUB4"]
dados_mercado = {}

# Booleanos devem ser claros
mercado_aberto = True
possui_dados = False
esta_ativo = True

# ❌ ERRADO
asset_price = 150.50  # NÃO FAZER
isActive = True       # NÃO FAZER (inglês + camelCase)
```

### Constantes
```python
# ✅ CORRETO - UPPER_CASE em Português
PERIODO_PADRAO_DIAS = 90
LIMITE_RISCO_MAXIMO = 0.02
TAXA_CORRETAGEM = 0.0003
MERCADOS_SUPORTADOS = ["BOVESPA", "NYSE", "NASDAQ"]

# ❌ ERRADO
DEFAULT_PERIOD = 90  # NÃO FAZER
```

### Parâmetros de Funções
```python
# ✅ CORRETO - Nomes descritivos em português com type hints
def analisar_ativo(
    ticker: str,
    periodo_dias: int = 30,
    incluir_volume: bool = True,
    tipo_analise: str = "completa"
) -> dict:
    """
    Analisa um ativo do mercado financeiro.
    
    Args:
        ticker: Código do ativo (ex: 'PETR4', 'AAPL')
        periodo_dias: Quantidade de dias para análise histórica
        incluir_volume: Se deve incluir análise de volume
        tipo_analise: Tipo de análise ('completa', 'tecnica', 'fundamental')
        
    Returns:
        Dicionário com resultados da análise
        
    Raises:
        ValueError: Se ticker inválido ou período negativo
    """
    pass
```

## 📄 Docstrings

### Formato Padrão (Google Style em Português)
```python
def calcular_sharpe_ratio(
    retornos: list[float], 
    taxa_livre_risco: float = 0.0
) -> float:
    """
    Calcula o índice de Sharpe para uma série de retornos.
    
    O índice de Sharpe mede o retorno ajustado ao risco de um investimento,
    comparando o excesso de retorno com a volatilidade.
    
    Args:
        retornos: Lista de retornos percentuais do ativo
        taxa_livre_risco: Taxa livre de risco anualizada (padrão 0.0)
        
    Returns:
        Valor do índice de Sharpe (retorno/risco)
        
    Raises:
        ValueError: Se a lista de retornos estiver vazia
        ZeroDivisionError: Se o desvio padrão for zero
        
    Example:
        >>> retornos = [0.01, 0.02, -0.01, 0.03]
        >>> calcular_sharpe_ratio(retornos)
        1.2247
    """
    pass
```

### Classes
```python
class AnalisadorCorrelacao:
    """
    Analisa correlações entre múltiplos ativos de mercado.
    
    Esta classe implementa análise de correlação rolante, matriz de correlação
    e identificação de mudanças de regime em relacionamentos entre ativos.
    
    Attributes:
        ativos: Lista de tickers dos ativos sendo analisados
        periodo_dias: Janela de tempo para cálculo de correlação
        matriz_correlacao: Matriz numpy com correlações atuais
        
    Example:
        >>> analisador = AnalisadorCorrelacao(['PETR4', 'VALE3'])
        >>> analisador.calcular_matriz()
        >>> print(analisador.matriz_correlacao)
    """
    
    def __init__(self, ativos: list[str], periodo_dias: int = 90):
        """
        Inicializa o analisador de correlação.
        
        Args:
            ativos: Lista com códigos dos ativos
            periodo_dias: Período para cálculo (padrão 90 dias)
        """
        pass
```

## 💬 Comentários

### Comentários de Linha
```python
# ✅ CORRETO - Explicações em português
# Calcula a média móvel exponencial de 20 períodos
ema_20 = calcular_ema(precos, periodo=20)

# Verifica se o preço rompeu a resistência
if preco_atual > nivel_resistencia:
    sinal_compra = True

# TODO: Implementar cálculo de correlação com lag
# FIXME: Corrigir bug no cálculo de volume financeiro
# NOTE: Este método é computacionalmente intensivo

# ❌ ERRADO - Inglês
# Calculate the exponential moving average  # NÃO FAZER
```

### Comentários de Bloco
```python
"""
Módulo de Análise Técnica

Este módulo implementa indicadores técnicos comuns para análise
de mercado financeiro, incluindo:
- Médias móveis (SMA, EMA, WMA)
- Indicadores de momentum (RSI, MACD, Stochastic)
- Bandas de volatilidade (Bollinger, Keltner)
- Identificação de padrões de candlestick

Autor: [Nome]
Data: 2025-11-05
"""
```

## 📋 Commits

### Formato de Mensagem
```bash
# Formato: <tipo>: <descrição curta>
# 
# <corpo detalhado (opcional)>
# 
# <footer (opcional)>

# Tipos:
# feat: Nova funcionalidade
# fix: Correção de bug
# docs: Mudanças em documentação
# style: Formatação, ponto e vírgula, etc (sem mudança de código)
# refactor: Refatoração de código
# perf: Melhorias de performance
# test: Adição ou correção de testes
# chore: Tarefas de build, configuração, etc

# ✅ EXEMPLOS CORRETOS:

feat: Adicionar cálculo de correlação entre ativos

Implementa análise de correlação de Pearson com janela rolante
para identificar relacionamentos entre múltiplos ativos.

- Suporte a correlação com lag temporal
- Matriz de correlação para múltiplos ativos
- Testes unitários incluídos

---

fix: Corrigir cálculo incorreto do índice de Sharpe

O cálculo estava usando desvio padrão populacional ao invés
de amostral, resultando em valores subestimados.

Closes #123

---

docs: Atualizar README com exemplos de uso

---

refactor: Reorganizar estrutura de módulos de análise

Move análise técnica e fundamental para submódulos separados
para melhor organização do código.

# ❌ ERRADO - Inglês:
feat: Add correlation calculation  # NÃO FAZER
fix: Fix bug in sharpe ratio      # NÃO FAZER
```

## 📚 Documentação Markdown

### Estrutura de README
```markdown
# Nome do Projeto

Breve descrição em português do que o projeto faz.

## 🎯 Objetivo

Descrição mais detalhada do propósito do projeto.

## 🚀 Começando

### Pré-requisitos

```bash
python >= 3.11
pip install -r requirements.txt
```

### Instalação

Passo a passo em português...

## 📖 Uso

Exemplos práticos de como usar...

## 🏗️ Arquitetura

Explicação da estrutura do projeto...

## 🤝 Contribuindo

Diretrizes de contribuição...

## 📄 Licença

Informações de licença...
```

## 🔧 Configurações e Variáveis de Ambiente

```python
# ✅ CORRETO - .env em português
CHAVE_API_MERCADO=sua_chave_aqui
URL_BASE_API=https://api.exemplo.com
PERIODO_ATUALIZACAO_SEGUNDOS=60
LIMITE_REQUISICOES_HORA=100
MODO_DEBUG=true

# ❌ ERRADO
API_KEY=test  # NÃO FAZER
```

## 📊 Logs e Mensagens

```python
import logging

logger = logging.getLogger(__name__)

# ✅ CORRETO - Logs em português
logger.info("Iniciando coleta de dados de mercado")
logger.warning("Taxa de requisições próxima do limite: 95/100")
logger.error("Falha ao conectar com API de mercado: timeout")
logger.debug(f"Correlação calculada: {correlacao:.4f}")

# ❌ ERRADO
logger.info("Starting market data collection")  # NÃO FAZER
```

## 🧪 Testes

```python
import pytest

def test_calcular_correlacao_retorna_valor_entre_menos_um_e_um():
    """
    Testa se a correlação calculada está no intervalo válido [-1, 1].
    
    A correlação de Pearson deve sempre retornar valores entre -1 e 1,
    onde -1 indica correlação negativa perfeita e 1 correlação positiva perfeita.
    """
    # Arrange (Preparar)
    dados_ativo1 = [1, 2, 3, 4, 5]
    dados_ativo2 = [2, 4, 6, 8, 10]
    
    # Act (Agir)
    resultado = calcular_correlacao(dados_ativo1, dados_ativo2)
    
    # Assert (Verificar)
    assert -1 <= resultado <= 1, "Correlação deve estar entre -1 e 1"


def test_analisar_ativo_levanta_erro_para_ticker_invalido():
    """Testa se exceção é levantada para ticker inválido."""
    with pytest.raises(ValueError, match="Ticker inválido"):
        analisar_ativo("INVALID123")
```

## 🎨 Formatação de Código

### Configuração Black
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']
```

### Configuração Flake8
```ini
# .flake8
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203, W503
```

## ✅ Checklist de Review

Antes de fazer commit, verifique:

- [ ] Todo código está em português (variáveis, funções, classes)
- [ ] Todos os comentários estão em português
- [ ] Todas as docstrings estão em português
- [ ] Mensagem de commit está em português
- [ ] Logs e mensagens de erro estão em português
- [ ] Documentação atualizada está em português
- [ ] Type hints estão presentes onde apropriado
- [ ] Testes foram adicionados/atualizados
- [ ] Código passa no linting (black, flake8)

---

**Lembre-se**: A consistência no idioma facilita a colaboração e manutenção do código!
