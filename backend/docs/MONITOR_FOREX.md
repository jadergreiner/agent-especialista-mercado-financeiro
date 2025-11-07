# 🌐 Monitor Forex - Documentação

## 📋 Visão Geral

**Monitor Forex** é um sistema automatizado que analisa **42 pares** simultaneamente (39 Forex + 3 Crypto) usando a metodologia de 5 pilares, gerando rankings de oportunidades em tempo real.

---

## 🎯 Cobertura de Mercado

### 📊 Distribuição dos 42 Pares Monitorados

| Categoria | Quantidade | Pares |
|-----------|------------|-------|
| **Majors** | 8 | USD/BRL, EUR/USD, USD/JPY, GBP/USD, USD/CHF, USD/CAD, AUD/USD, NZD/USD |
| **Crosses Principais** | 11 | EUR/JPY, GBP/JPY, EUR/GBP, EUR/CHF, AUD/JPY, CHF/JPY, EUR/CAD, AUD/CAD, CAD/JPY, NZD/JPY, AUD/NZD |
| **Crosses Secundários** | 10 | GBP/AUD, EUR/AUD, GBP/CHF, EUR/NZD, AUD/CHF, GBP/NZD, GBP/CAD, CAD/CHF, NZD/CAD, NZD/CHF |
| **Exóticos** | 9 | USD/INR, USD/CNY, USD/SGD, USD/HKD, USD/DKK, USD/SEK, USD/TRY, USD/MXN, USD/ZAR |
| **Ouro** | 1 | XAU/USD |
| **Crypto** | 3 | BTC/USD, BTC/EUR, ETH/USD |
| **TOTAL** | **42** | Cobertura global |

---

## 🚀 Como Usar

### Comando Básico
```powershell
python backend\monitor_forex.py
```
Analisa todos os 42 pares e exibe TOP 10 oportunidades.

### Comandos Avançados

#### 1️⃣ Definir Número de Oportunidades
```powershell
python backend\monitor_forex.py --top 15
```
Exibe TOP 15 em vez de 10.

#### 2️⃣ Modo Verbose (Progresso Detalhado)
```powershell
python backend\monitor_forex.py --verbose
```
Mostra progresso par a par com análise completa.

#### 3️⃣ Relatório por Categoria
```powershell
python backend\monitor_forex.py --categorias
```
Agrupa resultados por Majors, Crosses, Exóticos, Ouro, Crypto.

#### 4️⃣ Exportar para CSV
```powershell
python backend\monitor_forex.py --exportar
```
Gera arquivo `monitor_forex_resultado.csv` com todos os dados.

#### 5️⃣ Combinar Opções
```powershell
python backend\monitor_forex.py --top 20 --categorias --exportar
```
TOP 20 + relatório por categoria + exportação CSV.

#### 6️⃣ Análise para VENDA
```powershell
python backend\monitor_forex.py --operacao VENDA --top 10
```
Analisa oportunidades de venda (short).

---

## 📊 Exemplo de Saída

### Ranking Padrão
```
================================================================================
🌐 MONITOR FOREX - 42 PARES
================================================================================
Operação: COMPRA
Timestamp: 2025-11-05 23:27:44
================================================================================

..................... 20/42
..................... 40/42
..

================================================================================
✅ Analisados com sucesso: 42
❌ Erros: 0
================================================================================

================================================================================
🏆 TOP 10 OPORTUNIDADES FOREX
================================================================================

📊 Oportunidades Aprovadas: 5
================================================================================

#    Par           Carry   Conf.     R:R Recomendação
--------------------------------------------------------------------------------
🥇 1  USD/JPY       5.50%      70%    1.00  ✅ APROVAR_LONG
🥈 2  AUD/JPY       3.60%      67%    1.00  ⚠️  APROVAR_TÁTICO
🥉 3  GBP/JPY       4.00%      67%    1.00  ⚠️  APROVAR_TÁTICO
   4  EUR/JPY       3.50%      56%    1.00  ⚠️  APROVAR_TÁTICO
   5  GBP/NZD       1.50%      56%    1.00  ⚠️  APROVAR_TÁTICO
```

### Relatório por Categoria
```
================================================================================
📋 RELATÓRIO POR CATEGORIA
================================================================================

================================================================================
📊 MAJORS
================================================================================
Total analisados: 8
Aprovados (≥50%): 1
Confiança média: 27.5%
Melhor oportunidade: USD/JPY (70%, Carry 5.50%)

================================================================================
📊 CROSSES
================================================================================
Total analisados: 21
Aprovados (≥50%): 4
Confiança média: 34.5%
Melhor oportunidade: AUD/JPY (67%, Carry 3.60%)

================================================================================
📊 EXÓTICOS
================================================================================
Total analisados: 9
Aprovados (≥50%): 0
Confiança média: 20.0%
```

---

## 📈 Metodologia de Análise

### 5 Pilares (Idêntico ao Analisador Individual)

1. **Carry Trade** (30%): Diferencial de juros
2. **Política Monetária** (25%): Divergência BCs
3. **Análise Técnica** (20%): Níveis e tendências
4. **Correlação Brasil** (15%): Impacto WIN/IBOV
5. **Sentimento** (10%): Notícias recentes

### Classificação de Oportunidades

| Confiança | Emoji | Recomendação |
|-----------|-------|--------------|
| ≥ 70% | ✅ | APROVAR_LONG/SHORT |
| 50-69% | ⚠️ | APROVAR_TÁTICO |
| < 50% | ❌ | DESCARTAR |

---

## 🔍 Casos de Uso

### 1. Varredura Diária de Mercado
```powershell
# Executar toda manhã para identificar oportunidades
python backend\monitor_forex.py --top 15 --categorias
```

**Objetivo**: Encontrar melhores setups do dia em menos de 1 minuto.

### 2. Análise Multi-Mercado
```powershell
# Ver onde está a melhor oportunidade (Forex, Ouro ou Crypto)
python backend\monitor_forex.py --categorias
```

**Objetivo**: Decidir qual classe de ativo operar hoje.

### 3. Pesquisa e Backtesting
```powershell
# Exportar dados para análise posterior
python backend\monitor_forex.py --exportar
```

**Objetivo**: Criar histórico de oportunidades para backtesting.

### 4. Estratégia Short
```powershell
# Buscar oportunidades de venda
python backend\monitor_forex.py --operacao VENDA --top 10
```

**Objetivo**: Identificar pares sobre-valorizados.

### 5. Monitoramento Intraday
```powershell
# Executar a cada 1-2 horas
python backend\monitor_forex.py --top 5
```

**Objetivo**: Acompanhar mudanças nas oportunidades ao longo do dia.

---

## 📁 Arquivo CSV Exportado

### Estrutura do CSV

Arquivo: `monitor_forex_resultado.csv`

**Colunas (19 campos)**:
- `Par`: Par Forex (ex: USD/JPY)
- `Moeda_Base`: Moeda base (USD)
- `Moeda_Cotada`: Moeda cotada (JPY)
- `Carry_%`: Diferencial de juros (5.50)
- `Carry_Rating`: Rating (excelente/bom/neutro)
- `Divergencia_Politica`: Forte/moderada/fraca
- `Preco_Atual`: Preço atual do par
- `Entrada`: Nível de entrada sugerido
- `Stop`: Stop loss
- `TP1`: Take profit 1
- `TP2`: Take profit 2
- `Tendencia`: Alta/baixa/lateral
- `R_R`: Risco/Recompensa
- `Correlacao_WIN`: Impacto no WIN
- `Sentimento`: Score de sentimento
- `Confianca_%`: Nível de confiança (0-100)
- `Recomendacao`: APROVAR_LONG/TÁTICO/DESCARTAR
- `Par_Alternativo`: Sugestão alternativa
- `Timestamp`: Data/hora da análise

### Uso do CSV

```python
import pandas as pd

# Ler dados
df = pd.read_csv('backend/monitor_forex_resultado.csv')

# Filtrar aprovados
aprovados = df[df['Confianca_%'] >= 50]

# Melhor carry
melhor_carry = df.nlargest(5, 'Carry_%')

# Análise por moeda
pares_usd = df[df['Moeda_Base'] == 'USD']
```

---

## ⚙️ Performance

### Tempo de Execução

| Pares | Modo Normal | Modo Verbose |
|-------|-------------|--------------|
| 42 pares | ~45 segundos | ~2 minutos |
| Por par | ~1 segundo | ~3 segundos |

**Nota**: Delay de 0.1s entre requisições para evitar rate limiting do Yahoo Finance.

### Recursos

- **CPU**: Baixo (processamento sequencial)
- **RAM**: ~100 MB
- **Rede**: ~500 KB de dados (preços + taxas)
- **Disco**: CSV ~20 KB (42 pares)

---

## 🎯 Insights Gerados

### 1. Convergência de Oportunidades
Quando múltiplos pares de uma mesma moeda aparecem no TOP 10:

**Exemplo**: USD/JPY, EUR/JPY, GBP/JPY, AUD/JPY
→ **Insight**: JPY está fraco em todas as frentes (divergência forte de política monetária)

### 2. Força Relativa de Moedas
Ranquear moedas por frequência no TOP 10:

**Exemplo TOP 5**:
1. USD/JPY (70%)
2. AUD/JPY (67%)
3. GBP/JPY (67%)
4. EUR/JPY (56%)

→ **Ranking de Força**: USD > AUD = GBP > EUR >> JPY

### 3. Correlação de Risco
Se múltiplos exóticos aparecem, pode indicar "risk-on" ou "risk-off" global.

**Risk-On**: Exóticos aprovados, majors neutros
**Risk-Off**: Majors aprovados, exóticos descartados

---

## 🔄 Integração com Outros Sistemas

### 1. Integração com Alertas
```python
from monitor_forex import MonitorForex

monitor = MonitorForex()
analises = monitor.monitorar_todos()

aprovadas = [a for a in analises if a.confianca >= 70]

if aprovadas:
    # Enviar alerta (Telegram, Email, etc)
    enviar_alerta(f"🚨 {len(aprovadas)} oportunidades HIGH!")
```

### 2. Dashboard em Tempo Real
```python
import streamlit as st

st.title("Monitor Forex - Real Time")

if st.button("Atualizar"):
    monitor = MonitorForex()
    analises = monitor.monitorar_todos()

    st.dataframe(analises)
```

### 3. Scheduler Automático
```powershell
# Windows Task Scheduler
# Executar a cada 2 horas durante pregão
schtasks /create /tn "Monitor Forex" /tr "python backend\monitor_forex.py --exportar" /sc hourly /mo 2
```

---

## 📊 Estatísticas de Teste

### Teste Real - 42 Pares (05/11/2025)

| Métrica | Valor |
|---------|-------|
| **Total analisados** | 42 |
| **Sucesso** | 42 (100%) |
| **Erros** | 0 |
| **Tempo total** | 45 segundos |
| **Aprovados (≥50%)** | 5 (12%) |
| **Alta confiança (≥70%)** | 1 (2%) |
| **Confiança média** | 28.1% |

### Distribuição por Categoria

| Categoria | Total | Aprovados | Melhor |
|-----------|-------|-----------|--------|
| Majors | 8 | 1 (12%) | USD/JPY 70% |
| Crosses | 21 | 4 (19%) | AUD/JPY 67% |
| Exóticos | 9 | 0 (0%) | - |
| Ouro | 1 | 0 (0%) | - |
| Crypto | 3 | 0 (0%) | - |

### Melhor Oportunidade
**USD/JPY**: 70% confiança, Carry 5.50%, Divergência forte (USD hawkish vs JPY dovish)

---

## 🚨 Limitações e Considerações

### 1. Rate Limiting
Yahoo Finance pode bloquear requisições excessivas. Solução:
- Delay de 0.1s entre pares (já implementado)
- Não executar mais de 1x por minuto

### 2. Dados Mock de BCs
Sistema usa taxas mock. Para produção:
- Integrar APIs reais (FRED, ECB, etc)
- Atualizar dados antes do monitor

### 3. Horário de Mercado
Análise técnica mais precisa durante:
- Sessão Europeia: 08:00-17:00 GMT
- Sessão Americana: 13:00-22:00 GMT
- Overlap: 13:00-17:00 GMT (melhor liquidez)

### 4. Pares Exóticos
Spreads maiores e menor liquidez:
- Exigir confiança ≥ 80% (vs 70% para majors)
- Ajustar position sizing
- Considerar custos de rollover

---

## 🔧 Troubleshooting

### Erro: "Could not download data"
**Causa**: Yahoo Finance indisponível ou símbolo incorreto

**Solução**:
1. Verificar conexão internet
2. Aguardar alguns minutos (rate limiting)
3. Verificar se símbolo existe no Yahoo Finance

### Erro: "No data found"
**Causa**: Par não disponível no Yahoo Finance

**Solução**: Remover par de `PARES_MONITORADOS` ou usar fonte alternativa

### CSV vazio
**Causa**: Nenhum par analisado com sucesso

**Solução**: Verificar erros no output do monitor (modo verbose)

---

## 📚 Próximos Passos

### Melhorias Planejadas

- [ ] **Cache de Dados**: Evitar re-análises desnecessárias
- [ ] **Alertas Automáticos**: Telegram/Email quando confiança > 70%
- [ ] **Dashboard Web**: Interface visual com gráficos
- [ ] **Heatmap de Correlação**: Visualizar força relativa de moedas
- [ ] **Machine Learning**: Previsão de probabilidade de sucesso
- [ ] **Backtesting**: Testar estratégia "seguir o monitor"
- [ ] **API REST**: Expor monitor como serviço
- [ ] **WebSockets**: Stream de oportunidades em tempo real

---

## 📞 Suporte

Para dúvidas sobre o monitor:
1. Ver `CLI_FOREX.md` para comandos individuais
2. Ver `FOREX_RESUMO_EXECUTIVO.md` para metodologia
3. Testar modo verbose: `--verbose` para debug

---

**Versão**: 1.0.0
**Data**: Novembro 2025
**Autor**: Agent Especialista Mercado Financeiro
**Status**: ✅ Operacional (42 pares, 100% sucesso)
