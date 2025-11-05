# 🚀 Analisador WIN Day Trading

Sistema completo de análise para day trading do Mini Índice Brasileiro (WIN).

## 📋 Descrição

Este analisador implementa um sistema profissional de análise para day trading do contrato futuro WIN (Mini Índice Bovespa). Executa análise em **7 fases integradas** e fornece:

- ✅ Análise técnica completa (suportes, resistências, spread, volume profile)
- ✅ Análise macroeconômica (indicadores globais e Brasil)
- ✅ Análise de notícias com classificação de impacto
- ✅ Sistema de pontuação macro (+1/0/-1)
- ✅ Plano de trading estruturado com gestão de risco
- ✅ Checkpoints interativos para input do usuário
- ✅ Sistema de atualização contínua

## 🏗️ Arquitetura

### Classes Principais

#### `PontuacaoMacro`
Sistema de pontuação para avaliar cenário de mercado.

**Métodos:**
- `adicionar_ponto_tecnico()`: Adiciona ponto de análise técnica
- `adicionar_ponto_macro_global()`: Adiciona ponto de indicador global
- `adicionar_ponto_macro_brasil()`: Adiciona ponto de indicador Brasil
- `adicionar_noticia_brasil()`: Adiciona notícia do Brasil
- `adicionar_noticia_global()`: Adiciona notícia global
- `calcular_saldo_total()`: Retorna saldo e interpretação

**Sistema de Pontuação:**
```
+1 = Favorável ao índice (alta)
 0 = Neutro
-1 = Desfavorável ao índice (baixa)
```

**Interpretação do Saldo Total:**
- `>= +5`: FORTEMENTE FAVORÁVEL 🟢
- `+2 a +4`: FAVORÁVEL 🟢
- `-1 a +1`: NEUTRO 🟡
- `-4 a -2`: DESFAVORÁVEL 🔴
- `<= -5`: FORTEMENTE DESFAVORÁVEL 🔴

#### `AnalisadorWinDayTrading`
Analisador principal com pipeline de 7 fases.

**Configuração Padrão:**
```python
{
    'instrumento': 'WIN',
    'contratos_inicio': 1,
    'contratos_max': 10,
    'meta_lucro': 1000.00,
    'perfil_risco': 'conservador',
    'janela_analise_minutos': 120
}
```

## 🔄 Pipeline de Análise (7 Fases)

### Fase 1: Coleta de Dados
- Cotação atual e variação
- Máximas/mínimas do dia
- Volume negociado
- Níveis históricos (semana, mês, 52 semanas)

**TODO:** Integrar APIs reais
- TradingView
- Investing.com
- BrAPI
- IbovFinancials
- HG Brasil

### Fase 2: Análise Técnica
- **Tendência**: Alta, baixa ou lateral com força (0-10)
- **Suportes e Resistências**: 3 níveis principais
- **Análise de Spread**: Identifica melhor direção para risco/ganho
- **Indicadores**: RSI, MACD, ATR
- **Volume Profile**: Zonas de liquidez
- **Armadilhas**: Detecção de stop hunting

**Pontuação Técnica:**
- Tendência: +1 (alta), 0 (lateral), -1 (baixa)
- Spread: +1 (compra), -1 (venda)
- RSI: +1 (>65), 0 (35-65), -1 (<35)

### Fase 3: Análise Macroeconômica

**Indicadores Globais:**
- DXY (Índice do Dólar)
- VIX (Volatilidade)
- Ouro
- Juros EUA
- Emergentes

**Indicadores Brasil:**
- USD/BRL (Câmbio)
- Selic
- IPCA
- Balança comercial

**Pontuação Macro:**
- Cada indicador recebe +1, 0 ou -1
- Justificativa do impacto

### Fase 4: Análise de Notícias
- **Brasil**: Política, economia, empresas
- **Globais**: Fed, geopolítica, commodities

**Classificação:**
- Alto impacto: ±1 ou ±2 pontos
- Médio impacto: ±1 ponto
- Baixo impacto: 0 pontos

### Fase 5: Sistema de Pontuação
Consolida todas as pontuações:
```
Saldo Total = Técnico + Macro Global + Macro Brasil + Notícias
```

**Detalhamento por categoria:**
- Peso Técnico: 25%
- Peso Macro Global: 25%
- Peso Macro Brasil: 25%
- Peso Notícias: 25%

### Fase 6: Relatório Executivo
Síntese consolidada:
- Cotação e variação
- Tendência técnica
- Melhor spread (compra/venda)
- Saldo macro total
- Recomendação preliminar

**Checkpoint 1**: Permite adicionar informações antes do plano de trading.

### Fase 7: Plano de Trading

**Se direção = AGUARDAR:**
- Justificativa da espera
- Sugestão de monitoramento

**Se direção = COMPRA ou VENDA:**

1. **Entrada Inicial**
   - Preço
   - Quantidade de contratos
   - Justificativa

2. **Reforços (2 níveis)**
   - Preço de reforço
   - Contratos adicionais
   - Justificativa técnica

3. **Stop Loss**
   - Preço
   - Distância em pontos
   - Justificativa

4. **Take Profit (3 objetivos)**
   - TP1: 50% dos contratos
   - TP2: 30% dos contratos
   - TP3: 20% dos contratos (posição residual)

5. **Resumo de Risco**
   - Risco máximo (R$)
   - Lucro potencial (R$)
   - Relação risco/retorno
   - % da meta diária

## 💻 Uso Básico

### 1. Análise Simples

```python
from analisador_win_daytrading import AnalisadorWinDayTrading

# Criar analisador
analisador = AnalisadorWinDayTrading()

# Executar análise
resultado = analisador.analisar()

# Exibir relatório
print(analisador.formatar_relatorio(resultado))
```

### 2. Com Configuração Customizada

```python
config = {
    'instrumento': 'WIN',
    'contratos_inicio': 2,
    'contratos_max': 15,
    'meta_lucro': 2000.00,
    'perfil_risco': 'agressivo',
    'janela_analise_minutos': 90
}

analisador = AnalisadorWinDayTrading(config=config)
resultado = analisador.analisar()
```

### 3. Com Checkpoint Interativo

```python
analisador = AnalisadorWinDayTrading()

# Informação adicional do usuário
input_adicional = {
    'descricao': 'Copom sinaliza corte de juros mais agressivo',
    'categoria': 'noticia_brasil',
    'pontos': 2,  # +2 = fortemente favorável
    'impacto': 'alto'
}

resultado = analisador.analisar(dados_adicionais=input_adicional)
```

### 4. Análise Contínua (Updates)

```python
analisador = AnalisadorWinDayTrading()

# Análise a cada 30 minutos
import time
while True:
    resultado = analisador.analisar()
    print(analisador.formatar_relatorio(resultado))
    time.sleep(1800)  # 30 minutos
```

## 🧪 Testes

Execute a suite de testes:

```bash
cd backend/src/agents
python teste_analisador_win.py
```

**Testes disponíveis:**
1. Análise Básica
2. Análise com Checkpoint Interativo
3. Configuração Customizada
4. Análises Múltiplas (Updates)
5. Compatibilidade YAML
6. Executar TODOS os testes

## 📊 Estrutura do Resultado

```python
{
    'timestamp': '05/11/2025 13:08:53',
    'dados_mercado': {
        'cotacao': {...},
        'niveis_historicos': {...}
    },
    'analise_tecnica': {
        'tendencia': {...},
        'suportes': {...},
        'resistencias': {...},
        'spread_analysis': {...},
        'indicadores': {...}
    },
    'analise_macro': {
        'indicadores_globais': {...},
        'indicadores_brasil': {...}
    },
    'noticias': {
        'brasil': [...],
        'globais': [...]
    },
    'pontuacao': {
        'detalhamento': {...},
        'saldo_total': 6,
        'interpretacao': 'FORTEMENTE FAVORÁVEL',
        'emoji': '🟢'
    },
    'relatorio_executivo': {...},
    'plano_trading': {
        'direcao': 'COMPRA',
        'confianca': 10,
        'entrada_inicial': {...},
        'reforcos': [...],
        'gestao_saida': {...},
        'resumo_risco': {...}
    }
}
```

## 📈 Exemplo de Saída

```
======================================================================
📊 RELATÓRIO EXECUTIVO - WIN DAY TRADE
======================================================================
⏰ 05/11/2025 13:08:53
💰 WIN: 131,333.69 (-0.66%)

🎯 VISÃO TÉCNICA
  Tendência: LATERAL
  Melhor Spread: COMPRA (657 pontos)

📈 SALDO MACRO
  Técnico: +1
  Macro Global: +0
  Macro Brasil: +1
  Notícias: +4
  ▶ TOTAL: +6 - FORTEMENTE FAVORÁVEL 🟢

💼 PLANO DE TRADING
  Direção: COMPRA
  Confiança: 10/10
  Válido até: 15:08

  📍 ENTRADA
    Preço: 131,202.36
    Contratos: 1

  ➕ REFORÇOS
    1. 130,677.02 (2 contratos)
    2. 129,757.69 (3 contratos)

  🛑 STOP LOSS
    129,368.42

  🎯 TAKE PROFIT
    1. 131,990.36 (3 ct) = R$ 472.80
    2. 132,909.69 (2 ct) = R$ 682.93
    3. 133,960.36 (1 ct) = R$ 551.60

  💵 RESUMO DE RISCO
    Risco: R$ 366.79
    Lucro Potencial: R$ 1,707.33
    Relação R/R: 1:4.65
    % da Meta: 170.7%
======================================================================
```

## ⚙️ Configuração

### Perfis de Risco

**Conservador:**
- Contratos inicial: 1
- Contratos máximo: 5
- Stop loss: Mais próximo
- Take profits: Parciais mais cedo

**Moderado:**
- Contratos inicial: 1-2
- Contratos máximo: 10
- Stop loss: Médio
- Take profits: Balanceados

**Agressivo:**
- Contratos inicial: 2-3
- Contratos máximo: 15+
- Stop loss: Mais distante
- Take profits: Objetivos mais ambiciosos

## 🔄 Sistema de Atualização

O analisador suporta atualização contínua via trigger:

```python
# Trigger de atualização
if input_usuario == "ATUALIZAR":
    resultado = analisador.analisar()
```

**Janela de Validade:**
- Padrão: 120 minutos (2 horas)
- Após esse período, recomenda-se nova análise completa

## 🎯 Gestão de Risco

### Cálculo de Risco
```
1 ponto WIN = R$ 0.20

Risco = (Preço Entrada - Stop Loss) × Contratos × 0.20
Lucro = (Take Profit - Preço Entrada) × Contratos × 0.20
```

### Dimensionamento de Posição
```
Contratos Máximos = (Capital × % Risco) / Risco por Contrato
```

### Saída Escalonada
- **TP1**: Realiza 50% no primeiro alvo (mais conservador)
- **TP2**: Realiza 30% no segundo alvo
- **TP3**: Posição residual (20%) no alvo final

## 📚 Conceitos-Chave

### Spread
Diferença entre entrada e suporte/resistência mais próximo. O lado com **maior spread** oferece melhor relação risco/ganho.

### Stop Hunting
Movimento de mercado que busca stops de traders antes de seguir na direção real. O analisador identifica essas zonas.

### Volume Profile
Análise de volume por nível de preço. Identifica zonas de:
- **Alta liquidez**: Onde há muito volume (difícil atravessar)
- **Baixa liquidez**: Onde há pouco volume (movimento rápido)

### Macro Scoring
Sistema quantitativo de avaliação do cenário macro:
- Transforma análise qualitativa em pontos (+1/0/-1)
- Permite somar impactos de múltiplos fatores
- Facilita decisão objetiva

## 🚀 Próximos Passos

### Fase 1: Integração de Dados Reais
- [ ] Implementar coletor TradingView
- [ ] Integrar Investing.com API
- [ ] Conectar BrAPI
- [ ] Scraper IbovFinancials
- [ ] Integrar HG Brasil API

### Fase 2: Checkpoints Interativos
- [ ] Sistema de pausa para input
- [ ] Interface CLI interativa
- [ ] Salvamento de contexto

### Fase 3: Backtesting
- [ ] Engine de backtesting
- [ ] Métricas de performance
- [ ] Relatório de resultados

### Fase 4: Interface Web
- [ ] Dashboard em tempo real
- [ ] Gráficos interativos
- [ ] Alertas push
- [ ] Histórico de análises

### Fase 5: Paper Trading
- [ ] Simulador de operações
- [ ] Tracking de P&L
- [ ] Estatísticas de acertos

## 📝 Notas Importantes

⚠️ **ESTE É UM SISTEMA DE ANÁLISE**
- NÃO executa ordens automaticamente
- NÃO se conecta com corretoras
- NÃO substitui análise e decisão humana
- Sempre opere com stop loss
- Respeite seu plano de gestão de risco

## 📞 Suporte

Para dúvidas ou sugestões:
- Consulte documentação completa: `docs/PROMPT_WIN_DAYTRADING.md`
- Veja arquitetura de prompts: `docs/PROMPTS_E_REGRAS.md`

---

**Versão:** 1.0.0  
**Última atualização:** 05/11/2025
