# Prompts e Regras do Agente Especialista

## Visão Geral

Este documento descreve a arquitetura de prompts e regras que guiam o comportamento do agente especialista de mercado financeiro. Os prompts são organizados por tipo de análise e mercado, garantindo respostas consistentes e de alta qualidade.

## Estrutura de Prompts

```
prompts/
├── sistema/                    # Prompts de sistema (personalidade do agente)
│   ├── especialista_base.txt
│   └── contexto_mercado.txt
├── analise/                    # Prompts de análise
│   ├── rapida/
│   │   ├── forex.txt
│   │   ├── cripto.txt
│   │   └── acoes.txt
│   ├── tecnica/
│   │   ├── indicadores.txt
│   │   └── padroes.txt
│   ├── fundamental/
│   │   ├── acoes.txt
│   │   └── macro.txt
│   └── correlacao/
│       └── multi_ativo.txt
├── coleta_dados/               # Prompts para coleta/processamento
│   ├── noticias.txt
│   ├── sentimento.txt
│   └── eventos.txt
└── decisao/                    # Prompts para tomada de decisão
    ├── timing_entrada.txt
    ├── gestao_risco.txt
    └── recomendacao.txt
```

## Tipos de Prompts

### 1. Prompts de Sistema

Define a personalidade e expertise do agente.

**Características**:
- Estabelece identidade como especialista global de mercado
- Define tom e estilo de comunicação
- Especifica área de conhecimento e limitações
- Configuração padrão que acompanha todas as análises

### 2. Prompts de Análise

Guiam análises específicas de mercado.

**Categorias**:
- **Análise Rápida**: Overview rápido com principais indicadores
- **Análise Técnica**: Indicadores, padrões, suporte/resistência
- **Análise Fundamental**: Valuation, earnings, indicadores econômicos
- **Análise de Correlação**: Relacionamentos entre ativos

### 3. Prompts de Coleta de Dados

Instruções para processar dados externos.

**Funções**:
- Análise de sentimento de notícias
- Identificação de eventos relevantes
- Processamento de dados de mercado
- Extração de insights de múltiplas fontes

### 4. Prompts de Decisão

Guiam a tomada de decisão e recomendações.

**Aspectos**:
- Timing ótimo de entrada/saída
- Níveis de stop loss e take profit
- Dimensionamento de posição
- Avaliação de risco/retorno

## Regras de Análise

### Regras Gerais

1. **Sempre Contextualizar**: Toda análise deve considerar contexto macro
2. **Múltiplos Timeframes**: Analisar curto, médio e longo prazo
3. **Gestão de Risco**: Sempre incluir análise de risco
4. **Transparência**: Explicar raciocínio e limitações
5. **Atualização**: Considerar informações mais recentes disponíveis

### Regras por Tipo de Mercado

#### Forex
- Considerar diferenciais de taxa de juros
- Analisar políticas de bancos centrais
- Avaliar fluxo de capital internacional
- Monitorar eventos geopolíticos

#### Cripto
- Analisar métricas on-chain
- Considerar sentimento de comunidade
- Avaliar adoção e casos de uso
- Monitorar regulação global

#### Ações
- Analisar fundamentalistas da empresa
- Considerar setor e comparáveis
- Avaliar earnings e guidance
- Monitorar fluxo institucional

#### Futuros
- Considerar carry e contango/backwardation
- Analisar open interest
- Avaliar spread entre contratos
- Monitorar vencimentos

### Regras de Correlação

1. **Janelas Múltiplas**: Calcular correlação em 30d, 90d, 1a
2. **Mudanças de Regime**: Identificar quebras de correlação
3. **Falsos Positivos**: Validar correlações com fundamentalistas
4. **Causalidade**: Não assumir causalidade apenas por correlação

### Regras de Timing

1. **Confluência**: Buscar confluência técnica + fundamental
2. **Volume**: Confirmar movimentos com volume
3. **Volatilidade**: Ajustar timing para regime de volatilidade
4. **Liquidez**: Considerar horários de maior liquidez

### Regras de Risco

1. **Position Sizing**: Limitar exposição por ativo (padrão 2%)
2. **Correlação de Portfólio**: Monitorar exposições correlacionadas
3. **Stop Loss**: Sempre definir stop loss técnico
4. **Relação Risco/Retorno**: Mínimo 1:2 (preferencialmente 1:3)

## Formato de Prompts

### Template de Prompt de Análise

```
[CONTEXTO]
Você é um especialista global de mercado financeiro com profundo conhecimento em:
- [área específica]
- [mercados relevantes]
- [metodologias aplicáveis]

[OBJETIVO]
Analisar [ativo/mercado] para [finalidade] considerando:
- [critério 1]
- [critério 2]
- [critério 3]

[DADOS DISPONÍVEIS]
- Preço atual: {preco}
- Período: {periodo}
- Indicadores: {indicadores}
- Notícias: {noticias}

[INSTRUÇÕES]
1. [instrução específica 1]
2. [instrução específica 2]
3. [instrução específica 3]

[FORMATO DE SAÍDA]
Estruturar resposta seguindo o modelo YAML: {modelo}

[RESTRIÇÕES]
- [restrição 1]
- [restrição 2]
```

### Exemplo: Prompt de Análise Rápida Forex

```
[CONTEXTO]
Você é um especialista em mercado Forex com 20 anos de experiência em:
- Análise técnica de pares de moedas
- Avaliação de impacto de política monetária
- Trading de curto e médio prazo em Forex

[OBJETIVO]
Fornecer análise rápida do par {par} para decisão de trading intraday/swing, considerando:
- Tendência técnica atual
- Níveis chave de suporte e resistência
- Próximos eventos econômicos relevantes
- Contexto de política monetária

[DADOS DISPONÍVEIS]
- Par: {par}
- Preço atual: {preco_atual}
- Variação 24h: {variacao_24h}
- RSI: {rsi}
- MACD: {macd}
- Próximos eventos: {eventos}

[INSTRUÇÕES]
1. Identificar tendência dominante (curto e médio prazo)
2. Determinar níveis técnicos críticos
3. Avaliar força da tendência (escala 1-10)
4. Considerar fatores fundamentais imediatos
5. Fornecer recomendação clara (comprar/vender/aguardar)
6. Definir níveis de entrada, stop loss e take profit
7. Listar principais riscos da operação

[FORMATO DE SAÍDA]
Seguir modelo: forex_rapida.yaml

[RESTRIÇÕES]
- Usar apenas dados fornecidos
- Não inventar números ou eventos
- Ser conservador em cenários de incerteza
- Sempre incluir análise de risco
```

## Variáveis de Prompt

### Variáveis de Contexto

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{ativo}` | Ticker do ativo | BTCUSD, PETR4 |
| `{mercado}` | Tipo de mercado | forex, cripto, acoes |
| `{timeframe}` | Período de análise | intraday, swing, posição |
| `{modelo_yaml}` | Modelo de saída | forex_rapida |

### Variáveis de Dados

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{preco_atual}` | Preço/cotação atual | 1.0850, 35.20 |
| `{variacao_24h}` | Variação percentual 24h | +2.5%, -1.3% |
| `{volume}` | Volume do período | 1.5M, 80K |
| `{rsi}` | RSI calculado | 65.3 |
| `{macd}` | MACD e sinal | 0.0025 / 0.0018 |

### Variáveis de Análise

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{tendencia}` | Tendência identificada | alta, baixa, lateral |
| `{suporte}` | Nível de suporte | 1.0800 |
| `{resistencia}` | Nível de resistência | 1.0920 |
| `{correlacoes}` | Ativos correlacionados | EUR/USD: 0.85 |

## Cadeia de Prompts

Para análises complexas, usar cadeia de prompts:

```
1. Prompt de Coleta → Obter e processar dados
2. Prompt de Análise Técnica → Avaliar gráficos e indicadores
3. Prompt de Análise Fundamental → Avaliar contexto macro/micro
4. Prompt de Correlação → Identificar relacionamentos
5. Prompt de Decisão → Sintetizar e recomendar
```

## Otimização de Prompts

### Princípios

1. **Especificidade**: Ser claro e específico sobre o que deseja
2. **Contexto**: Fornecer contexto adequado
3. **Exemplos**: Incluir exemplos quando relevante
4. **Formato**: Especificar formato de saída desejado
5. **Restrições**: Definir claramente limites e restrições

### Técnicas de Melhoria

1. **Few-Shot Learning**: Incluir exemplos de análises anteriores
2. **Chain-of-Thought**: Pedir raciocínio passo a passo
3. **Role-Playing**: Definir papel específico do agente
4. **Constraints**: Adicionar restrições para guiar resposta

## Versionamento de Prompts

### Convenção de Nomenclatura

```
{tipo}_{mercado}_{versao}.txt

Exemplos:
- analise_rapida_forex_v1.txt
- sistema_especialista_v2.txt
- decisao_timing_v1.txt
```

### Controle de Versão

- Manter histórico de versões anteriores
- Documentar mudanças entre versões
- Testar novas versões antes de deploy
- Realizar A/B testing quando possível

## Próximos Passos

### Para Implementação

1. **Criar Gerenciador de Prompts** (`backend/src/utils/gerenciador_prompts.py`)
2. **Definir Prompts Base** (seu conhecimento existente)
3. **Testar e Iterar** (validar qualidade das respostas)
4. **Integrar com Orquestrador** (usar prompts nas análises)
5. **Monitorar Performance** (avaliar qualidade continuamente)

### Para Documentação

1. **Catalogar Prompts Existentes** (seus prompts atuais)
2. **Documentar Regras Específicas** (por mercado/tipo)
3. **Criar Exemplos** (casos de uso reais)
4. **Estabelecer Métricas** (avaliar qualidade de análises)

---

## 📝 Como Contribuir com seus Prompts

Para adicionar seus prompts existentes:

1. **Compartilhe o Prompt**: Cole o texto do seu prompt
2. **Descreva o Uso**: Para qual tipo de análise/mercado
3. **Indique Resultados**: Que tipo de saída você espera
4. **Liste Ajustes**: Otimizações que gostaria de fazer

Vou então:
- Categorizar e estruturar o prompt
- Otimizar para uso programático
- Criar versão com variáveis
- Integrar no sistema de gerenciamento
- Testar e validar

---

**Aguardando seus prompts para começarmos a otimização! 🚀**
