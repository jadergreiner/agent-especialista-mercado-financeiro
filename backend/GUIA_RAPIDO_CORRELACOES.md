# Sistema de Correlações - Guia Rápido

## 📋 Visão Geral

Sistema para coleta e análise de cotações de ativos correlacionados ao WIN (Mini Índice Bovespa).

**Objetivo**: Fornecer contexto macro para decisões de trading através da análise de correlações entre WIN e outros mercados.

---

## 🚀 Instalação e Primeira Execução

### 1. Inicializar Sistema

```bash
# Inicializar com ativos de prioridade ALTA e MÉDIA
python consultar_correlacoes.py coletar --inicializar

# Incluir também ativos de prioridade BAIXA
python consultar_correlacoes.py coletar --inicializar --incluir-baixa
```

### 2. Verificar Ativos Configurados

```bash
python consultar_correlacoes.py listar
```

---

## 📊 Comandos Essenciais

### Coletar Cotações

```bash
# Coletar ativos de PRIORIDADE ALTA (últimas 24h, candles de 1h)
python consultar_correlacoes.py coletar --prioridade alta --periodo 1d --intervalo 1h

# Coletar TODOS os ativos
python consultar_correlacoes.py coletar --prioridade todas --periodo 5d --intervalo 15m

# Coletar dados diários (últimos 30 dias)
python consultar_correlacoes.py coletar --periodo 1mo --intervalo 1d
```

**Intervalos disponíveis**: `1m`, `5m`, `15m`, `1h`, `1d`
**Períodos disponíveis**: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`

### Ver Últimas Cotações

```bash
# Ver todas as últimas cotações
python consultar_correlacoes.py ultimas

# Filtrar por prioridade
python consultar_correlacoes.py ultimas --prioridade alta
```

### Calcular Variação

```bash
# Variação nos últimos 7 dias
python consultar_correlacoes.py variacao --dias 7

# Variação no último mês
python consultar_correlacoes.py variacao --dias 30
```

### Matriz de Correlação

```bash
# Calcular correlação dos últimos 30 dias
python consultar_correlacoes.py matriz --dias 30

# Calcular e salvar no banco
python consultar_correlacoes.py matriz --dias 30 --salvar
```

---

## 🎯 Ativos Coletados

### 🔴 Prioridade ALTA (7 ativos)

| Símbolo    | Nome                  | Correlação | Tipo    |
|------------|-----------------------|------------|---------|
| ^BVSP      | Ibovespa              | +0.99      | Direto  |
| USDBRL=X   | Dólar/Real            | -0.80      | Inverso |
| ^GSPC      | S&P 500               | +0.70      | Direto  |
| ^VIX       | VIX (Volatilidade)    | -0.50      | Inverso |
| CL=F       | Petróleo WTI          | +0.50      | Direto  |
| VALE3.SA   | Vale ON               | +0.85      | Direto  |
| PETR4.SA   | Petrobras PN          | +0.80      | Direto  |

### 🟡 Prioridade MÉDIA (7 ativos)

| Símbolo    | Nome                  | Correlação | Tipo    |
|------------|-----------------------|------------|---------|
| ^DJI       | Dow Jones             | +0.65      | Direto  |
| ^IXIC      | NASDAQ                | +0.60      | Direto  |
| BZ=F       | Petróleo Brent        | +0.50      | Direto  |
| ITUB4.SA   | Itaú PN               | +0.75      | Direto  |
| BBDC4.SA   | Bradesco PN           | +0.70      | Direto  |
| B3SA3.SA   | B3 ON                 | +0.75      | Direto  |
| EWZ        | ETF Brasil            | +0.90      | Direto  |

### 🟢 Prioridade BAIXA (4 ativos)

| Símbolo    | Nome                  | Correlação | Tipo    |
|------------|-----------------------|------------|---------|
| ZS=F       | Soja                  | +0.40      | Direto  |
| GC=F       | Ouro                  | -0.30      | Inverso |
| BTC-USD    | Bitcoin               | +0.35      | Direto  |
| ^TNX       | 10Y Treasury          | -0.40      | Inverso |

---

## ⏰ Workflow Recomendado

### Coleta Intraday (Trading Ativo)

```bash
# A cada 1h durante o pregão
python consultar_correlacoes.py coletar --prioridade alta --periodo 1d --intervalo 15m
python consultar_correlacoes.py ultimas --prioridade alta
```

### Coleta End-of-Day (Análise Diária)

```bash
# Após fechamento do mercado (18h)
python consultar_correlacoes.py coletar --prioridade todas --periodo 5d --intervalo 1d
python consultar_correlacoes.py variacao --dias 1
python consultar_correlacoes.py matriz --dias 30 --salvar
```

### Análise Semanal

```bash
# Sexta-feira após fechamento
python consultar_correlacoes.py variacao --dias 7
python consultar_correlacoes.py matriz --dias 90 --salvar
```

---

## 📈 Interpretação dos Resultados

### Correlações Diretas (+)

- **+0.99 (Ibovespa)**: WIN acompanha quase perfeitamente o IBOV
- **+0.85 (VALE3)**: Peso significativo no índice, movimenta o WIN
- **+0.70 (S&P 500)**: Mercado US puxa mercado BR

**Uso**: Quando esses ativos sobem, WIN tende a subir.

### Correlações Inversas (-)

- **-0.80 (Dólar)**: Quando dólar sobe forte, WIN cai (fuga de capitais)
- **-0.50 (VIX)**: Volatilidade alta nos EUA, risco-off global

**Uso**: Quando esses ativos sobem, WIN tende a cair.

### Matriz de Correlação

```
         ^BVSP  USDBRL  ^GSPC  ^VIX
^BVSP      -    🔵-0.78 🔴+0.72 🔵-0.48
USDBRL  🔵-0.78    -    🔵-0.55 🟠+0.45
^GSPC   🔴+0.72 🔵-0.55    -    🔵-0.82
^VIX    🔵-0.48 🟠+0.45 🔵-0.82    -
```

**Legenda**:
- 🔴 Forte positiva (>0.8)
- 🟠 Moderada positiva (>0.5)
- 🔵 Forte negativa (<-0.8)
- 🟦 Moderada negativa (<-0.5)
- ⚪ Fraca

---

## 🔧 Integração com Estratégias

### Exemplo 1: Filtro de Condições Macro

```python
from dados.coletor_correlacoes import ColetorCorrelacoes

def pode_operar_hoje_macro() -> bool:
    """Verifica se condições macro permitem operação."""

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Buscar variações dos últimos 30min
    cur.execute("""
        SELECT simbolo, variacao_dia
        FROM cotacoes_correlacoes
        WHERE data_hora >= datetime('now', '-30 minutes')
        AND simbolo IN ('^GSPC', '^VIX', 'USDBRL=X')
    """)

    variacoes = {row[0]: row[1] for row in cur.fetchall()}

    # Condições adversas
    if variacoes.get('^VIX', 0) > 2.0:  # VIX subindo muito
        return False

    if variacoes.get('USDBRL=X', 0) > 1.5:  # Dólar disparando
        return False

    if variacoes.get('^GSPC', 0) < -1.0:  # S&P caindo forte
        return False

    return True
```

### Exemplo 2: Confirmação de Sinal

```python
def confirmar_sinal_com_correlacoes(sinal: int) -> float:
    """
    Calcula confiança do sinal baseado em correlações.

    Returns:
        float: Multiplicador de confiança (0.5 a 1.5)
    """

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Buscar variações recentes
    cur.execute("""
        SELECT simbolo, variacao_dia
        FROM cotacoes_correlacoes
        WHERE data_hora >= datetime('now', '-1 hour')
        AND simbolo IN ('^BVSP', '^GSPC', 'VALE3.SA', 'PETR4.SA')
    """)

    variacoes = {row[0]: row[1] for row in cur.fetchall()}

    confirmacoes = 0
    total = 0

    if sinal > 0:  # Sinal de COMPRA
        # Verificar se correlações diretas estão positivas
        if variacoes.get('^BVSP', 0) > 0.3:
            confirmacoes += 1
        if variacoes.get('^GSPC', 0) > 0.2:
            confirmacoes += 1
        if variacoes.get('VALE3.SA', 0) > 0:
            confirmacoes += 1
        if variacoes.get('PETR4.SA', 0) > 0:
            confirmacoes += 1
        total = 4

    elif sinal < 0:  # Sinal de VENDA
        # Verificar se correlações diretas estão negativas
        if variacoes.get('^BVSP', 0) < -0.3:
            confirmacoes += 1
        if variacoes.get('^GSPC', 0) < -0.2:
            confirmacoes += 1
        if variacoes.get('VALE3.SA', 0) < 0:
            confirmacoes += 1
        if variacoes.get('PETR4.SA', 0) < 0:
            confirmacoes += 1
        total = 4

    # Multiplicador: 0.5 (nenhuma confirmação) a 1.5 (todas confirmam)
    return 0.5 + (confirmacoes / total)
```

### Exemplo 3: Ajuste de Target

```python
def ajustar_target_por_correlacoes(target_base: int) -> int:
    """Ajusta target conforme ambiente macro."""

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Calcular score macro
    cur.execute("""
        SELECT
            AVG(CASE WHEN simbolo IN ('^BVSP', '^GSPC', 'VALE3.SA', 'PETR4.SA')
                THEN variacao_dia ELSE 0 END) as score_positivo,
            AVG(CASE WHEN simbolo IN ('USDBRL=X', '^VIX')
                THEN -variacao_dia ELSE 0 END) as score_inverso
        FROM cotacoes_correlacoes
        WHERE data_hora >= datetime('now', '-1 hour')
    """)

    pos, inv = cur.fetchone()
    score_macro = (pos or 0) + (inv or 0)

    # Ajustar target
    if score_macro > 0.5:  # Ambiente favorável
        return int(target_base * 1.3)
    elif score_macro < -0.5:  # Ambiente adverso
        return int(target_base * 0.7)
    else:  # Neutro
        return target_base
```

---

## 🔍 Troubleshooting

### "Nenhum ativo configurado"

```bash
# Inicializar sistema
python consultar_correlacoes.py coletar --inicializar
```

### "Nenhum dado retornado"

- Verificar conexão com internet
- Símbolo pode estar incorreto no Yahoo Finance
- Mercado pode estar fechado (usar `--periodo 5d` para incluir dados históricos)

### Erro ao instalar dependências

```bash
# Instalar/atualizar yfinance
pip install --upgrade yfinance pandas numpy
```

---

## 📚 Próximos Passos

1. ✅ **Coletar dados iniciais** (últimos 30 dias)
2. ✅ **Calcular matriz de correlação** base
3. ⏳ **Integrar filtros** em estratégias existentes
4. ⏳ **Criar dashboard** visual de correlações
5. ⏳ **Implementar alertas** de divergências

---

## 📞 Arquivos Relacionados

- **Módulo principal**: `src/dados/coletor_correlacoes.py`
- **CLI**: `consultar_correlacoes.py`
- **Documentação completa**: `CORRELACOES_WIN.md`
- **Banco de dados**: `data/recomendacoes.sqlite`

---

**Última atualização**: 2025-01-24
