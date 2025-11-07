# Treinamento Contínuo do Agente

Este documento descreve o ciclo de melhoria contínua do agente de mercado financeiro, baseado em registro de recomendações, validação de assertividade e acompanhamento de métricas.

## Objetivo

- Guardar as recomendações emitidas diariamente
- No dia seguinte (ou após a validade), validar a assertividade e o PnL
- Construir histórico para melhoria do processo (métricas, ajustes e aprendizado)

## Arquitetura da Solução

- Armazenamento local leve via SQLite (arquivo `backend/data/recomendacoes.sqlite`)
- Módulo de persistência: `backend/src/persistencia/recomendacoes.py`
- Integração automática no analisador (`AnalisadorWinDayTrading`)
- CLI de avaliação para operação manual: `backend/src/cli_avaliacao.py`

## Fluxo Operacional

1. Geração de recomendação
   - Executar o analisador (WIN)
   - A recomendação é salva automaticamente no banco (id gerado)
2. Validação (D+0 a D+1)
   - Usar a CLI para registrar o resultado: executada/cancelada/expirada
   - Informar se acertou (TP) ou errou (STOP), PnL e motivo
3. Métricas
   - Consultar métricas dos últimos N dias (acurácia, profit factor, PnL)
4. Aprendizado/Ajustes
   - A partir das métricas, ajustar regras, pesos ou parâmetros do agente

## Como Usar

### Modo 1: Inserção Manual (sem API)

Para inserir recomendações manualmente (útil para dados históricos ou testes):

```powershell
# Criar nova recomendação via wizard interativo
python backend/src/cli_inserir_manual.py nova

# O wizard guiará você por todas as informações:
# - Data/hora
# - Direção (COMPRA/VENDA/AGUARDAR)
# - Preços (entrada, stop, TPs)
# - Contexto (tendência, spread, saldo macro)
# - Volatilidade (ATR)
# - Confiança e validade
```

**Registrar resultado de forma interativa:**

```powershell
# Wizard para registrar resultado
python backend/src/cli_inserir_manual.py resultado

# O wizard mostrará pendentes e guiará o registro:
# - Status (executada/cancelada/expirada)
# - Resultado financeiro (acerto/erro, PnL)
# - Motivo da saída (tp1/tp2/tp3/stop/tempo/manual)
```

### Modo 2: CLI Direto (avançado)

### 1) Listar recomendações pendentes

```powershell
# Na raiz do repositório
python backend/src/cli_avaliacao.py listar
```

### 2) Registrar resultado de uma recomendação

```powershell
# Exemplo: recomendação id=42 foi EXECUTADA e ACERTOU (TP1)
python backend/src/cli_avaliacao.py resultado --id 42 --status executada --acertou 1 --motivo tp1 --pnl-reais 380.00

# Exemplo: recomendação id=43 foi EXECUTADA e ERROU (STOP)
python backend/src/cli_avaliacao.py resultado --id 43 --status executada --acertou 0 --motivo stop --pnl-reais -250.00

# Exemplo: recomendação id=44 foi CANCELADA (não entrou)
python backend/src/cli_avaliacao.py resultado --id 44 --status cancelada --obs "Não bateu no preço de entrada"

# Exemplo: recomendação id=45 EXPIRADA (perdeu validade)
python backend/src/cli_avaliacao.py resultado --id 45 --status expirada --obs "Passou a janela de 2h"
```

Parâmetros opcionais úteis:

- `--preco-saida`: preço de encerramento efetivo
- `--pnl-pontos`: pontos do WIN capturados/perdidos
- `--pnl-reais`: valor financeiro do resultado

### 3) Consultar métricas

```powershell
# Últimos 30 dias (padrão)
python backend/src/cli_avaliacao.py metricas

# Últimos 90 dias
python backend/src/cli_avaliacao.py metricas --dias 90
```

Saída (exemplo):

```text
📈 Métricas Básicas
Período: 30 dias
Total resultados: 62
Executadas: 40 | Canceladas/Expiradas: 22
Acurácia: 57.5%
Profit Factor: 1.42
PNL total (R$): 3,280.50
```

### Modo 3: Importar dados manuais por CSV (preços diários)

Estrutura de diretórios padronizada para dados manuais:

```powershell
# Base
backend/data/manual/

# Um diretório por ativo (exemplos)
backend/data/manual/WIN/
backend/data/manual/IBOV-FUT/
backend/data/manual/VALE3/
backend/data/manual/PETR4/

# Salve os CSVs do ativo dentro da sua pasta
backend/data/manual/WIN/Dados Historicos - Ibovespa Futuros.csv
```

Formato esperado (colunas em PT-BR, como o exemplo anexado):

- Data (dd.mm.yyyy), Último, Abertura, Máxima, Mínima, Vol., Var%
- Exemplos de valores: "04.11.2025", "152.944", "44,99K", "0,03%"

Importar um arquivo específico (instrumento inferido pela pasta-mãe se não informado):

```powershell
python backend/src/cli_importar_csv.py importar-diario --arquivo "backend/data/manual/WIN/Dados Históricos - Ibovespa Futuros (3).csv" --fonte investing.com
```

Importar todos os CSVs do diretório do ativo (ex.: WIN):

```powershell
python backend/src/cli_importar_csv.py importar-diario --dir backend/data/manual/WIN --fonte manual
```

Importar todos os CSVs de todos os ativos (varre subpastas de data/manual):

```powershell
python backend/src/cli_importar_csv.py importar-diario --dir backend/data/manual --fonte manual
```

Regras de parsing:

- Data: "dd.mm.yyyy" → ISO "YYYY-MM-DD" (UTC)
- Números em PT-BR: remove milhar "." e troca vírgula "," por ponto "."
- Volume: "K"=mil, "M"=milhão (ex: 44,99K → 44990)
- Var%: convertido para fração (0,03% → 0.0003)

Destino dos dados: tabela `precos_diarios` no SQLite (para uso futuro em ATR, backtests e calibração).

## Validação Automática (Aprovada)

Esta etapa automatiza a verificação do resultado das recomendações pendentes usando dados intraday.

### Algoritmo (resumo)

1. Seleciona recomendações pendentes (sem resultado)
2. Define janela de validação: `[timestamp, valido_ate]`
3. Obtém barras intraday (1m/5m) do instrumento (WIN)
4. Regra de execução: preço toca o `preco_entrada` dentro da janela? Se não, marca como `expirada`
5. Após a execução, verifica o primeiro evento que ocorrer:
   - Toque em `stop_loss` → `executada`, `acertou = False`, `motivo = stop`
   - Toque em `tp1|tp2|tp3` → `executada`, `acertou = True`, `motivo = tpX`
6. Registra resultado com timestamp e PnL estimado (pontos × 0,20 × contratos)

### Pseudocódigo

```python
for rec in listar_pendentes():
    barras = provider.intraday('WIN', inicio=rec.timestamp, fim=rec.valido_ate, tf='1m')
    if not cruzou(barras, nivel=rec.preco_entrada):
        registrar_resultado(rec.id, status='expirada')
        continue
    t_execucao = primeira_cruzada(barras, rec.preco_entrada)
    evento = proximo_evento(barras, t_execucao, niveis=[stop, tp1, tp2, tp3])
    if evento in [tp1,tp2,tp3]:
        registrar_resultado(rec.id, 'executada', acertou=True, motivo=evento)
    elif evento == stop:
        registrar_resultado(rec.id, 'executada', acertou=False, motivo='stop')
```

### Implementação

- Módulo: `backend/src/avaliacao/validador_automatico.py`
- Provider mock (sem rede): gera série intraday sintética para demonstração
- CLI: `python backend/src/cli_avaliacao.py auto` (executa a validação automática nas pendentes)

## Estrutura dos Dados

### Tabela `recomendacoes`

- `id` (PK)
- `timestamp` (UTC)
- `instrumento` (ex.: WIN)
- `direcao` (COMPRA|VENDA|AGUARDAR)
- `preco_entrada`, `stop_loss`, `tp1`, `tp2`, `tp3`
- `contratos_inicio`, `reforcos_json`
- `saldo_macro`, `confianca`, `valido_ate`, `variacao_dia`, `tendencia`, `melhor_spread`
- `relatorio_json` (snapshot completo)

### Tabela `resultados`

- `id` (PK)
- `id_recomendacao` (FK -> recomendacoes.id)
- `timestamp_validacao` (UTC)
- `status` (executada|cancelada|expirada)
- `acertou` (1|0|NULL)
- `preco_saida`, `pnl_pontos`, `pnl_reais`
- `motivo_saida` (tp1|tp2|tp3|stop|tempo|manual)
- `observacoes`

## Caminho para Aprendizado

Com o histórico, podemos:

- Calibrar pesos do sistema de pontuação (ex.: dar mais peso ao spread quando VIX < 15)
- Medir quais indicadores mais contribuem para acerto (ablação por fator)
- Otimizar distâncias de stop/TPs por regime de volatilidade (ATR baixo vs alto)
- Detectar padrões de horário/sessão com maior acerto
- Implementar feedback automático (ex.: ajuste incremental dos limiares do RSI)

## Extensões Futuras

- Coleta automática do resultado (sem input manual) via dados históricos intraday
- Métricas avançadas: Sharpe, Sortino, Max Drawdown do conjunto de trades
- Relatórios diários automatizados (e-mail/Telegram)
- Painel web com gráficos e filtros
- Integração com backtesting para validação robusta

## Observações

- O sistema atual é agnóstico de corretora; não executa ordens.
- A validação pode ser manual no início e evoluir para automatizada.
- - O armazenamento local facilita início rápido; nada impede migrar para Postgres depois.

## Métricas Detalhadas por Categoria

Para entender o que realmente move o preço (e separar falsos movimentos), use o relatório detalhado:

```powershell
python backend/src/cli_avaliacao.py metricas-detalhadas --dias 90
```

O relatório apresenta, para cada categoria, as colunas:
- sinais: quantidade total de recomendações naquela categoria
- exec: quantas foram executadas (tocaram a entrada)
- acc: acurácia entre as executadas (acertos / executadas)
- PF: Profit Factor (soma dos ganhos / soma das perdas)
- PnL (R$): resultado financeiro acumulado

Categorias avaliadas:

### 1. Por Tendência (na emissão)

- ALTA, BAIXA, LATERAL
- Identifica se o modelo performa melhor seguindo ou contra tendência

### 2. Por Saldo Macro (na emissão)

- ≤ -3 (fortemente desfavorável)
- -2 a -1 (desfavorável)
- 0 a +1 (neutro)
- +2 a +3 (favorável)
- ≥ +4 (fortemente favorável)
- Revela se fundamentação macro agrega valor preditivo

### 3. Por Horário (sessões BRT aproximadas)

- Abertura (10h)
- Manhã (11–12h)
- Meio (13–14h)
- Tarde (15–16h)
- Fechamento/After (≥17h)
- Pré-abertura (<10h)
- Identifica sessões com melhor taxa de acerto

### 4. Por Spread (melhor direção identificada)

- COMPRA vs VENDA
- Detecta viés direcional do modelo (se favorece longs ou shorts)

### 5. Por Direção do Trade

- COMPRA, VENDA, AGUARDAR
- Valida efetividade das recomendações direcionais vs aguardar

### 6. Por Volatilidade (ATR)

- Baixa (<1000 pontos)
- Média (1000-1200 pontos)
- Alta (>1200 pontos)
- Determina qual regime de volatilidade favorece o modelo

Interpretação prática:

- Concentre ajustes onde PF e acurácia são maiores (o que tende a mover preço)
- Revise regras onde há muitos "sinais" e baixa execução ou PF baixo (falsos movimentos)
- **Análise multi-dimensional**: Combine categorias para identificar "zonas de ouro"
  - Exemplo: "Tendência ALTA + Saldo ≥+4 + Volatilidade Baixa + Horário 10h" pode revelar setup com 85%+ acurácia
- Use ATR para calibrar stops e TPs dinamicamente (em alta volatilidade, aumentar distâncias)
- Identifique assimetrias: se COMPRA tem PF 2.5 e VENDA 0.8, privilegie setups de compra

## Sistema de Aprendizado Contínuo (Prompt Estruturado)

### Visão Geral

Complementando o sistema quantitativo de avaliação, implementamos um **Sistema de Aprendizado Contínuo** baseado em análise qualitativa de performance individual. Este sistema utiliza um prompt estruturado para extrair aprendizados específicos de cada recomendação validada.

### Arquitetura do Sistema

- **Módulo Principal**: `backend/sistema_aprendizado_continuo.py`
- **Interface CLI**: `backend/cli_aprendizado_continuo.py`
- **Banco de Dados**: Tabela `analises_performance` no SQLite
- **Prompt Base**: `prompts/prompt_aprendizado_continuo.md`

### Fluxo de Aprendizado

1. **Coleta de Dados**: Após validação de recomendação, coletar dados de feedback
2. **Análise Estruturada**: Executar prompt para comparar previsto vs real
3. **Extração de Aprendizados**: Identificar pontos positivos e de melhoria
4. **Ajuste de Pesos**: Aplicar modificações dinâmicas aos fatores de decisão
5. **Registro Histórico**: Salvar análise para auditoria e métricas futuras

### Como Usar

#### Análise Individual

```bash
# Executar análise de uma recomendação específica
python backend/cli_aprendizado_continuo.py analisar \
  --id 42 \
  --resultado "ACERTOU - TP1 atingido em +380 pontos" \
  --movimento "WIN subiu 420 pontos em 3.5h" \
  --eventos "Dados de emprego EUA melhores que esperado, Fed hints dovish"
```

#### Ver Métricas do Sistema

```bash
# Consultar métricas consolidadas do aprendizado
python backend/cli_aprendizado_continuo.py metricas
```

#### Ajustes Manuais de Pesos

```bash
# Aplicar ajustes específicos aos pesos
python backend/cli_aprendizado_continuo.py ajustar-pesos \
  --score-macro 0.05 \
  --score-tecnico -0.02 \
  --volatilidade 0.03
```

### Estrutura do Prompt

O sistema utiliza o seguinte prompt estruturado para análise:

```
ANÁLISE DE PERFORMANCE DA RECOMENDAÇÃO ANTERIOR:

DADOS DE FEEDBACK:
{resultado_real_oportunidade}
{movimento_preco_observado}
{eventos_que_ocorreram}

COMPARE:
- Probabilidade prevista vs resultado real
- Timeframe estimado vs tempo real de movimento
- Catalisadores previstos vs eventos reais que moveram mercado
- Nível de invalidação vs maior excursão adversa

APRENDIZADOS:
1. O que funcionou bem na análise?
2. Que sinais foram subestimados/superestimados?
3. Como melhorar a calibração de probabilidades?
4. Que novos inputs poderiam ter melhorado a previsão?

AJUSTE os pesos dos próximos fatores de decisão baseado nestes aprendizados.
```

### Saída Estruturada

Cada análise gera um relatório com:

- **Comparação Previsto vs Real**: Métricas quantitativas de performance
- **Pontos Positivos**: O que funcionou bem na análise
- **Pontos de Melhoria**: Áreas que precisam de ajustes
- **Sinais Sub/Superestimados**: Calibração de indicadores
- **Novos Inputs Sugeridos**: Possíveis melhorias no modelo
- **Ajustes Recomendados**: Modificações específicas nos pesos

### Integração com Sistema Existente

O sistema de aprendizado contínuo complementa o `avaliador_assertividade.py`:

- **Avaliador Assertividade**: Foco em métricas quantitativas agregadas
- **Aprendizado Contínuo**: Foco em análise qualitativa individual e ajustes dinâmicos

### Benefícios

1. **Adaptação Contínua**: Sistema aprende com cada trade executado
2. **Calibração Dinâmica**: Pesos ajustados automaticamente baseado em performance
3. **Transparência Total**: Histórico completo de aprendizados e ajustes
4. **Melhoria Iterativa**: Performance melhora gradualmente ao longo do tempo
5. **Auditoria Completa**: Todo aprendizado é registrado e mensurável

### Monitoramento de Eficácia

O sistema gera métricas para acompanhar sua própria eficácia:

- **Taxa de Acerto das Análises**: Performance do sistema de aprendizado
- **Evolução dos Pesos**: Como os fatores evoluem ao longo do tempo
- **Histórico de Ajustes**: Registro completo de modificações aplicadas
- **Impacto na Performance**: Correlação entre ajustes e resultados futuros

### Extensões Futuras

- **Integração com LLM**: Usar IA para gerar análises mais sofisticadas
- **Ajustes Automáticos**: Sistema aplica ajustes sem intervenção manual
- **Análises Comparativas**: Comparar aprendizados entre diferentes tipos de setup
- **Dashboard Visual**: Interface web para acompanhar evolução do aprendizado
- **Alertas de Performance**: Notificações quando ajustes impactam negativamente
