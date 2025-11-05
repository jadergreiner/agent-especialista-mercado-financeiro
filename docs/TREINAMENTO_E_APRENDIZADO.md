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

````
