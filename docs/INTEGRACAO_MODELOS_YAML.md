# Integração com Modelos YAML

## Visão Geral

O sistema de análise agora está integrado com modelos YAML flexíveis que definem a estrutura de saída para diferentes tipos de análise e mercados. Esta arquitetura permite:

- **Flexibilidade**: Adicionar novos tipos de análise sem modificar código
- **Padronização**: Garantir que todas as análises sigam estruturas consistentes
- **Escalabilidade**: Facilitar expansão para novos mercados e produtos
- **Manutenibilidade**: Separar configuração de modelo de lógica de negócio

## Arquitetura

```
modelos/                          # Templates YAML de saída
├── forex_rapida.yaml            # Forex - Análise Rápida
├── cripto_futuros_tecnica.yaml  # Cripto/Futuros - Análise Técnica
├── acoes_fundamental.yaml       # Ações - Análise Fundamental
└── cripto_completa.yaml         # Cripto - Análise Completa

backend/src/
├── utils/
│   └── gerenciador_modelos.py   # Carrega e gerencia modelos YAML
└── agents/
    └── orquestrador_analise.py  # Usa modelos para estruturar respostas
```

## Componentes

### 1. Gerenciador de Modelos

**Arquivo**: `backend/src/utils/gerenciador_modelos.py`

**Responsabilidades**:
- Carregar todos os modelos YAML na inicialização
- Cachear modelos em memória para performance
- Mapear combinações de (mercado + tipo_analise) → modelo apropriado
- Preparar cópias de modelos com timestamps e valores padrão

**Uso**:
```python
from utils.gerenciador_modelos import gerenciador_modelos

# Obter modelo específico
modelo = gerenciador_modelos.obter_modelo('forex', 'rapida')

# Listar modelos disponíveis
modelos = gerenciador_modelos.listar_modelos_disponiveis()

# Recarregar modelos do disco
gerenciador_modelos.recarregar_modelos()
```

### 2. Identificação Automática de Mercado

O orquestrador identifica automaticamente o mercado do ativo baseado em padrões:

- **Forex**: Pares de 6 caracteres com 'USD' (EURUSD, GBPUSD, etc)
- **Cripto**: Termina com USD, USDT, BTC, ETH, BNB
- **Ações**: Termina com número (PETR4, VALE3, etc)
- **Futuros**: Contém códigos de mês/ano (WINZ24, DOLH25, etc)

### 3. Integração no Orquestrador

**Fluxo de Análise**:
1. Normalizar prompt do usuário
2. Identificar mercado do ativo
3. Obter modelo YAML apropriado
4. Usar modelo como estrutura base da resposta
5. Preencher campos com dados de análise
6. Retornar resposta estruturada

## Modelos Disponíveis

### Forex - Análise Rápida
- **Arquivo**: `modelos/forex_rapida.yaml`
- **Mercado**: Forex
- **Tipo**: Rápida
- **Campos**: par, cotacao_atual, variacao_24h, tendencia_curto_prazo, recomendacao_trading, riscos

### Cripto/Futuros - Análise Técnica
- **Arquivo**: `modelos/cripto_futuros_tecnica.yaml`
- **Mercado**: Cripto, Futuros
- **Tipo**: Técnica
- **Campos**: ativo, preco_atual, analise_tecnica, recomendacao, gestao_risco

### Ações - Análise Fundamental
- **Arquivo**: `modelos/acoes_fundamental.yaml`
- **Mercado**: Ações
- **Tipo**: Fundamental
- **Campos**: ticker, preco_atual, analise_fundamental, analise_tecnica, recomendacao, projecoes

### Cripto - Análise Completa
- **Arquivo**: `modelos/cripto_completa.yaml`
- **Mercado**: Cripto
- **Tipo**: Completa
- **Campos**: ativo, preco_spot, analise_onchain, analise_tecnica, correlacoes, sentimento, recomendacao

## Expandindo o Sistema

### Adicionar Novo Modelo

1. **Criar arquivo YAML** em `modelos/`:
```yaml
# modelos/forex_completa.yaml
mercado: forex
tipo_analise: completa
par: EUR/USD
timestamp_analise: ""

analise_macro:
  pib_zona_euro: ""
  taxa_juros_bce: ""
  inflacao: ""

# ... outros campos
```

2. **Atualizar mapeamento** em `gerenciador_modelos.py`:
```python
mapeamento_modelos = {
    # ... mapeamentos existentes
    ("forex", "completa"): "forex_completa",
}
```

3. **Testar**:
```bash
python cli.py EURUSD completa
```

### Adicionar Novo Mercado

1. **Criar modelos YAML** para o mercado
2. **Atualizar** `_identificar_mercado()` no orquestrador
3. **Adicionar** padrões de identificação específicos

## Exemplos de Uso

### CLI
```bash
# Análise rápida de Forex
python cli.py BTCUSD rapida

# Análise de ações
python cli.py PETR4 rapida

# Análise técnica
python cli.py WINFEB25 tecnica
```

### Programático
```python
from src.agents.orquestrador_analise import OrquestradorAnalise, TipoAnalise

orquestrador = OrquestradorAnalise()

# Análise usando modelo YAML apropriado
resultado = orquestrador.analisar(
    prompt="BTCUSD",
    tipo_analise=TipoAnalise.RAPIDA,
    periodo_dias=90
)

# Resultado está estruturado conforme modelo YAML
print(resultado['recomendacao'])
print(resultado['analise_tecnica'])
```

## Estado Atual

### ✅ Implementado
- Gerenciador de modelos YAML com cache
- Carregamento automático de todos os modelos
- Identificação automática de mercado
- Mapeamento mercado + tipo → modelo
- Integração com orquestrador
- CLI formatado para novos modelos

### 🔄 Em Desenvolvimento (Mock)
- Preenchimento de campos com dados mock
- Análise técnica simulada
- Recomendações baseadas em valores aleatórios

### 📋 Próximos Passos
1. **Integração com Dados Reais**:
   - yfinance para preços históricos
   - TA-Lib para indicadores técnicos
   - APIs de notícias para sentimento

2. **Análises Avançadas**:
   - Correlações entre ativos
   - Análise fundamentalista real
   - Sentimento de mercado

3. **Performance**:
   - Cache de dados de mercado
   - Análise assíncrona
   - Otimização de consultas

## Benefícios da Arquitetura

1. **Desacoplamento**: Lógica de análise separada de estrutura de saída
2. **Testabilidade**: Fácil criar testes com diferentes modelos
3. **Versionamento**: Modelos YAML podem ser versionados independentemente
4. **Documentação**: Modelos servem como documentação da API
5. **Validação**: Possível adicionar validação de schema YAML

## Configuração

### Diretório de Modelos
O sistema procura modelos YAML em:
```
<raiz_projeto>/modelos/
```

Relativo ao arquivo `gerenciador_modelos.py`:
```python
self.diretorio_modelos = Path(__file__).parent.parent.parent.parent / "modelos"
```

### Recarregar Modelos
Para recarregar modelos sem reiniciar o sistema:
```python
gerenciador_modelos.recarregar_modelos()
```

## Troubleshooting

### Modelo não encontrado
**Sintoma**: Análise retorna estrutura padrão em vez de usar modelo YAML

**Solução**:
1. Verificar se arquivo existe em `modelos/`
2. Conferir mapeamento em `gerenciador_modelos.py`
3. Verificar logs de carregamento na inicialização

### Campos faltando
**Sintoma**: Campos do modelo YAML não aparecem na resposta

**Solução**:
1. Verificar se `analise.update(dados)` está sendo chamado
2. Confirmar que método `_analise_*()` retorna dict
3. Verificar conflitos de nomes de campos

## Manutenção

### Adicionar Campo a Modelo Existente
1. Editar arquivo YAML em `modelos/`
2. Atualizar método `_analise_*()` correspondente
3. Testar com CLI

### Remover Campo Obsoleto
1. Remover do arquivo YAML
2. Atualizar código que preenche o campo
3. Atualizar testes

### Renomear Campo
1. Atualizar YAML
2. Atualizar código de preenchimento
3. Atualizar formatação no CLI
4. Manter compatibilidade se necessário (alias)

## Recursos

- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [YAML Specification](https://yaml.org/spec/)
- Modelos de exemplo em `modelos/`
- Código fonte em `backend/src/utils/gerenciador_modelos.py`
