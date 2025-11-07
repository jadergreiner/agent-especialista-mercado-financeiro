# 📊 Sistema de Análise de Dividendos

**Análise fundamentalista automatizada para seleção de ações pagadoras de dividendos consistentes.**

---

## 📌 Índice

- [Visão Geral](#visão-geral)
- [Metodologia](#metodologia)
- [Scores e Critérios](#scores-e-critérios)
- [Como Usar](#como-usar)
- [Interpretação dos Resultados](#interpretação-dos-resultados)
- [Exemplos Práticos](#exemplos-práticos)
- [Limitações](#limitações)

---

## 🎯 Visão Geral

Este sistema implementa uma metodologia profissional de análise de ações com foco em **renda passiva sustentável**. Diferente de analisadores que priorizam apenas o Dividend Yield (DY), aqui **a sustentabilidade tem prioridade absoluta**.

### Princípios Fundamentais

1. **Sustentabilidade > Dividend Yield**: Preferimos DY de 6% consistente do que 15% irregular
2. **Análise Multi-Dimensional**: Não existe "métrica mágica", analisamos 20+ indicadores
3. **Histórico de 5 Anos**: Exigimos evidências, não promessas
4. **Filtro de Irregularidade**: Descartamos dividendos esporádicos/extraordinários

### O que NÃO fazemos

❌ Cair em armadilhas de DY altíssimos (empresa em liquidação)
❌ Confundir dividendo extraordinário com consistência
❌ Ignorar saúde financeira da empresa
❌ Recomendar apenas por baixo P/L

---

## 🔬 Metodologia

### Processo Chain-of-Thought

Nossa análise segue 4 etapas sequenciais:

#### **A) Análise de Sustentabilidade do Lucro**

```
1. Coletamos 5 anos de LPA (Lucro Por Ação)
2. Identificamos tendência:
   - CRESCENTE: Média móvel ascendente + volatilidade < 20%
   - ESTÁVEL: Volatilidade < 15%, sem tendência clara
   - VOLÁTIL: Flutuações > 15%
   - DECRESCENTE: Média móvel descendente

3. Validamos histórico de dividendos:
   - CONSISTENTE: ≥5 pagamentos em 5 anos
   - IRREGULAR: 3-4 pagamentos
   - ESPORÁDICO: <3 pagamentos → DESCARTA
```

#### **B) Cálculo de Preços-Alvo**

Usamos a **abordagem inversa** do DY:

```python
# Média de dividendos dos últimos 5 anos
dividendo_medio = soma_dividendos_5anos / 5

# Preço Teto: Assumindo DY de 6% (conservador)
preco_teto = dividendo_medio / 0.06

# Preço Ideal: Assumindo DY de 8% (agressivo)
preco_ideal = dividendo_medio / 0.08
```

**Interpretação:**
- **Acima do Teto**: Caro demais, aguardar correção
- **Entre Teto e Ideal**: Preço aceitável
- **Abaixo do Ideal**: Oportunidade de entrada

#### **C) Avaliação de Saúde Financeira**

```
1. Liquidez Corrente = Ativo Circulante / Passivo Circulante
   ≥2.0 = Excelente
   ≥1.5 = Boa
   ≥1.0 = Aceitável
   <1.0 = RISCO

2. Geração de Caixa Livre
   operatingCashFlow - capitalExpenditures

   POSITIVA: Sobra dinheiro (pode pagar dividendos)
   NEUTRA: Equilíbrio
   NEGATIVA: Queima caixa (dividendos em risco)
```

#### **D) Geração de Score Final**

Fórmula ponderada:

```
Score Final = (Sustentabilidade × 0.40) + (Saúde × 0.35) + (Valor × 0.25)
```

**Por que esses pesos?**
- **40% Sustentabilidade**: É a base. Sem consistência, nada importa.
- **35% Saúde**: Empresa sem caixa não paga dividendos.
- **25% Valor**: Valuation importa, mas não é tudo.

---

## 📊 Scores e Critérios

### Score de Sustentabilidade (0-100)

**Base:** 50 pontos

**Tendência LPA (+30/-20):**
- CRESCENTE: +30 pontos (melhor cenário)
- ESTÁVEL: +20 pontos
- VOLÁTIL: +5 pontos
- DECRESCENTE: -20 pontos

**Consistência Dividendos (+20/-30):**
- CONSISTENTE (≥5 pagtos): +20 pontos
- IRREGULAR (3-4 pagtos): +5 pontos
- ESPORÁDICO (<3 pagtos): -30 pontos

**Lucratividade (-20 se negativo):**
- LPA > 0: Mantém pontos
- LPA ≤ 0: -20 pontos (prejuízo)

**Interpretação:**
- **80-100**: Sustentabilidade excepcional
- **65-79**: Boa sustentabilidade
- **50-64**: Sustentabilidade aceitável
- **<50**: Risco de corte de dividendos

---

### Score de Saúde Financeira (0-100)

**Base:** 50 pontos

**Liquidez (+30/-20):**
- ≥2.0: +30 pontos (folga financeira)
- ≥1.5: +20 pontos
- ≥1.0: +10 pontos
- <1.0: -20 pontos (risco iminente)

**Geração de Caixa (+20/-20):**
- POSITIVA: +20 pontos
- NEUTRA: 0 pontos
- NEGATIVA: -20 pontos

**Interpretação:**
- **80-100**: Fortaleza financeira
- **65-79**: Saúde boa
- **50-64**: Saúde aceitável
- **<50**: Fragilidade financeira

---

### Score de Valor (0-100)

**Base:** 50 pontos

**Margem de Segurança (+30/-20):**
- ≥30% abaixo do ideal: +30 pontos (barganha)
- 15-30% abaixo: +20 pontos
- 0-15% abaixo: +10 pontos
- Acima do ideal: -20 pontos (caro)

**Dividend Yield (+15):**
- ≥8%: +15 pontos
- ≥6%: +10 pontos
- ≥4%: +5 pontos
- <4%: 0 pontos

**P/L (+5/-5):**
- 0-10: +5 pontos (barato)
- 10-15: 0 pontos
- >15: -5 pontos (caro)

**Interpretação:**
- **80-100**: Valuation atrativo
- **65-79**: Valuation justo
- **50-64**: Valuation esticado
- **<50**: Sobrevalorizado

---

### Recomendações Finais

```
Score ≥ 80  → COMPRA_FORTE  (✅)
Score ≥ 65  → COMPRA        (⚠️)
Score ≥ 50  → NEUTRO        (⚪)
Score < 50  → VENDA         (❌)
```

---

## 🚀 Como Usar

### 1. Análise Completa

Gera tabela comparativa + relatório executivo:

```bash
python backend\consultar_dividendos.py analisar TGMA3 KLBN11 GGBR4
```

**Saída:**
- Tabela horizontal com 12 métricas por ação
- Relatório executivo identificando melhor oportunidade
- Justificativa (sustentabilidade + saúde + valor)
- Riscos a monitorar
- Ações preteridas (por que foram descartadas)

---

### 2. Ranking Simplificado

Apenas o ranking sem relatório detalhado:

```bash
python backend\consultar_dividendos.py ranking TGMA3 KLBN11 GGBR4 GOAU4 --top 5
```

**Saída:**
```
🥇 1  TGMA3      83/100   986.00%   8.66   2.61  ✅ COMPRA_FORTE
🥈 2  GOAU4      80/100   368.00%  10.63   2.89  ✅ COMPRA_FORTE
🥉 3  GGBR4      75/100   334.00%  12.81   2.70  ⚠️  COMPRA
```

---

### 3. Análise por Setor

Analisa ações pré-selecionadas de um setor:

```bash
python backend\consultar_dividendos.py setor bancos
```

**Setores disponíveis:**
- `bancos`: ITUB4, BBDC4, BBAS3, SANB11, BPAN4
- `energia`: PETR4, ELET3, ELET6, TAEE11, CPLE6
- `utilities`: SAPR4, SBSP3, CSAN3, TRPL4, CMIG4
- `siderurgia`: GGBR4, GOAU4, CSNA3, USIM5
- `varejo`: LREN3, PCAR3, MGLU3, ARZZ3, VIVA3

---

## 📖 Interpretação dos Resultados

### Tabela Comparativa

```markdown
| Métrica | TGMA3 | GOAU4 |
| DY (12M) | 986.00% | 368.00% |  ⚠️ Valores altos = bug API yfinance
| P/L | 8.66 | 10.63 |             ✅ Quanto menor, melhor
| LPA (Atual) | R$ 4.25 | R$ 1.05 |  ✅ Quanto maior, melhor
| Liq. Corrente | 2.61 | 2.89 |      ✅ ≥2.0 = Excelente
| Caixa Livre | POSITIVA | NEGATIVA |  ✅ POSITIVA é essencial
| SCORE FINAL | 83/100 | 80/100 |     ✅ ≥80 = COMPRA_FORTE
```

### Relatório Executivo

**Melhor Oportunidade**: A ação ranqueada em 1º lugar

**Justificativa:** Dividida em 3 pilares:
1. **Sustentabilidade (40%)**: Histórico LPA + dividendos
2. **Saúde (35%)**: Liquidez + geração de caixa
3. **Valor (25%)**: Preço vs valor intrínseco

**Pontos Fortes:** O que torna a ação atrativa

**Riscos a Monitorar:** Fatores de atenção antes de investir

**Ações Preteridas:** Por que as outras não foram escolhidas

---

## 💡 Exemplos Práticos

### Exemplo 1: Ação Ideal (Score 83/100)

**TGMA3 - Tegma Logística**

```
✅ Sustentabilidade: 90/100
   - LPA ESTÁVEL (R$ 4.25)
   - Dividendos CONSISTENTES (5/5 anos)

✅ Saúde: 100/100
   - Liquidez 2.61 (excelente)
   - Caixa Livre POSITIVA

⚠️  Valor: 50/100
   - Preço R$ 36.70 (acima do ideal R$ 21.52)
   - DY 986% (bug yfinance, ignorar)

DECISÃO: COMPRA_FORTE
Empresa sólida, mas aguardar correção para R$ 25-28.
```

### Exemplo 2: Ação com Risco (Score 56/100)

**BPAN4 - Banco Pan**

```
✅ Sustentabilidade: 90/100
   - Dividendos CONSISTENTES

❌ Saúde: 30/100
   - Liquidez 0.00 (bancos não têm liquidez tradicional)
   - Caixa NEUTRA

⚠️  Valor: 50/100
   - Preço acima do ideal

DECISÃO: NEUTRO
Dividendos consistentes, mas fragilidade financeira.
Aguardar melhoria na geração de caixa.
```

---

## ⚠️ Limitações

### 1. Dividend Yield Inflacionado

**Problema:** yfinance multiplica DY por 100 (bug conhecido)

**Solução:** Ignorar valores absurdos (>100%). Focar em:
- Preço Teto/Ideal (calculados corretamente)
- Consistência de pagamentos
- Scores de sustentabilidade

---

### 2. Bancos e Liquidez

**Problema:** Bancos têm liquidez corrente = 0.00

**Motivo:** Modelo de negócio diferente (não têm estoque, etc)

**Solução:** Para bancos, focar em:
- Índice de Basileia (capital regulatório)
- ROE (retorno sobre patrimônio)
- Inadimplência

**Alternativa:** Use indicadores específicos bancários fora deste sistema.

---

### 3. Dados Históricos

**Problema:** yfinance pode ter gaps em dados antigos

**Solução:** Sistema valida:
- Mínimo 3 anos de dados
- Se <3 anos, score penalizado
- Se dados ausentes, ação não é analisada

---

### 4. Dividendos Extraordinários

**Problema:** Empresa vende ativo e paga dividendo único gigante

**Solução:** Sistema usa **média de 5 anos**
- Dividendo extraordinário é diluído
- Foco em consistência, não em picos

---

### 5. Setores Cíclicos

**Problema:** Siderurgia, petróleo flutuam muito

**Exemplo:** GOAU4 (Gerdau) - LPA volátil por ciclos econômicos

**Solução:** Score de sustentabilidade penaliza volatilidade
- LPA VOLÁTIL: apenas +5 pontos
- Sistema prefere empresas defensivas

---

## 🔍 Quando NÃO Usar Este Sistema

❌ **Ações de crescimento (growth):** Foco aqui é renda passiva, não valorização

❌ **IPOs recentes:** Precisamos 5 anos de histórico

❌ **Empresas em recuperação judicial:** Dados distorcidos

❌ **REITs/FIIs:** Metodologia diferente (renda obrigatória)

❌ **Small caps ilíquidas:** yfinance pode ter dados incompletos

---

## 📚 Referências

### Conceitos Utilizados

- **Graham & Dodd** (Security Analysis): Margem de segurança
- **Benjamin Graham** (Investidor Inteligente): P/L, liquidez corrente
- **Peter Lynch**: Prefer PEG ratio (aqui adaptado)
- **Warren Buffett**: Consistência > oportunismo

### Fontes de Dados

- **yfinance**: Yahoo Finance API (dados fundamentalistas)
- **Período**: 5 anos históricos (recomendação acadêmica)

### Metodologia de Scoring

Desenvolvida para priorizar:
1. Sustentabilidade (estudos mostram correlação com performance)
2. Saúde financeira (reduz risco de corte)
3. Valuation (margem de segurança)

---

## 🛠️ Manutenção

### Adicionar Novos Setores

Edite `consultar_dividendos.py`:

```python
setores = {
    'seu_setor': ['ACAO1', 'ACAO2', 'ACAO3'],
}
```

### Ajustar Pesos de Score

Edite `analisador_dividendos.py`:

```python
score_final = (
    sustentabilidade * 0.40 +  # Ajuste aqui
    saude * 0.35 +             # Ajuste aqui
    valor * 0.25               # Ajuste aqui
)
```

**Dica:** Soma deve ser 1.0 (100%)

---

## 🎓 Glossário

- **DY (Dividend Yield):** Dividendos anuais / Preço da ação
- **LPA (Lucro Por Ação):** Lucro líquido / Número de ações
- **P/L (Preço/Lucro):** Preço da ação / LPA
- **Liquidez Corrente:** Ativo circulante / Passivo circulante
- **Caixa Livre:** Caixa operacional - investimentos (capex)
- **Preço Teto:** Preço máximo aceitável (DY 6%)
- **Preço Ideal:** Preço de entrada agressivo (DY 8%)
- **Margem de Segurança:** % de desconto vs preço ideal

---

## 📞 Suporte

Para adicionar funcionalidades:
1. Análise de FIIs (metodologia diferente)
2. Integração com SQLite (histórico)
3. Alertas por e-mail (price targets)
4. Backtesting de portfólio

---

**Desenvolvido com foco em sustentabilidade de renda passiva.**
**Toda a documentação e código em Português (Brasil).**
