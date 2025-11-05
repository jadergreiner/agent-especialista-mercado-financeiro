# CLI de Inserção Manual

Ferramenta para inserir recomendações e resultados manualmente, sem necessidade de integração com API.

## 🎯 Para Que Serve

- **Popular banco de dados** com trades históricos que você já executou
- **Testar sistema** sem depender de APIs externas
- **Entrada rápida** de dados do dia a dia
- **Aprendizado** antes de automatizar completamente

## 📝 Como Usar

### Criar Nova Recomendação

```powershell
python backend/src/cli_inserir_manual.py nova
```

O wizard interativo perguntará:

1. **Data/Hora**: Usar atual ou informar manualmente
2. **Direção**: COMPRA, VENDA ou AGUARDAR
3. **Preços**: Entrada, Stop Loss, Take Profits (TP1, TP2, TP3)
4. **Contexto de Mercado**:
   - Tendência (ALTA/BAIXA/LATERAL)
   - Melhor Spread (COMPRA/VENDA)
   - Saldo Macro (-6 a +6)
5. **Volatilidade**: ATR em pontos
6. **Confiança**: 0 a 10
7. **Validade**: Horário limite (ex: 15:30)
8. **Variação do Dia**: Percentual (ex: +1.5%)

**Exemplo de Sessão:**

```text
====================================================================
📝 NOVA RECOMENDAÇÃO MANUAL
====================================================================

🕐 Data e Hora
Usar data/hora atual? (S/n): s
   ✓ Usando: 2025-11-05T14:30:00.000000

📊 Direção do Trade
Direção (COMPRA/VENDA/AGUARDAR): COMPRA

💰 Preços
Preço de entrada: 130500
Quantidade de contratos: 2
Stop Loss: 130200

🎯 Take Profits
TP1: 130800
Tem TP2? (s/N): s
TP2: 131100
Tem TP3? (s/N): n

🌍 Contexto de Mercado
Tendência (ALTA/BAIXA/LATERAL): ALTA
Melhor Spread (COMPRA/VENDA): COMPRA

📈 Saldo Macro
   -3 = Fortemente Desfavorável
    0 = Neutro
   +3 = Favorável
   +6 = Fortemente Favorável
Saldo Macro (-6 a +6): 4

📊 Volatilidade (ATR)
ATR em pontos: 1150

✨ Confiança
Confiança (0-10): 8

⏰ Validade
Válido até (HH:MM ou deixe vazio): 16:30

📉 Variação do Dia
Variação % (ex: +1.5% ou -0.8%): +0.8%

====================================================================
📋 RESUMO
====================================================================
Direção: COMPRA
Entrada: 130,500.00 (2 contratos)
Stop: 130,200.00
TPs: 130,800.00 / 131,100.00
Tendência: ALTA | Spread: COMPRA
Saldo Macro: +4 | ATR: 1150.00
Confiança: 8/10
====================================================================

💾 Salvar recomendação? (S/n): s

✅ Recomendação salva com sucesso! ID: 3
```

### Registrar Resultado

```powershell
python backend/src/cli_inserir_manual.py resultado
```

O wizard:

1. **Lista recomendações pendentes** (até 10 mais recentes)
2. **Pede ID** da recomendação a ser atualizada
3. **Status**: executada, cancelada ou expirada
4. Se executada:
   - Acertou? (sim/não)
   - Preço de saída
   - PnL em pontos e R$
   - Motivo (tp1/tp2/tp3/stop/tempo/manual)
5. **Observações** opcionais
6. **Confirmação** antes de salvar

**Exemplo de Sessão:**

```text
====================================================================
📊 REGISTRAR RESULTADO
====================================================================

📋 Recomendações Pendentes:
   ID 3: COMPRA | Entrada: 130,500.00 | 2025-11-05T14:30:00.000000

🔢 ID da recomendação: 3

📊 Status da Execução
Status (executada/cancelada/expirada): executada

💰 Resultado Financeiro
Acertou? (sim/não/S/N): s
Preço de saída: 130800
PnL em pontos: 300
PnL em R$: 600

🎯 Motivo da Saída
Motivo (tp1/tp2/tp3/stop/tempo/manual): tp1
Observações (opcional): Trade rápido, saiu no primeiro alvo

====================================================================
📋 RESUMO DO RESULTADO
====================================================================
ID: 3
Status: EXECUTADA
Resultado: ✅ ACERTO
Saída: 130,800.00
PnL: +300.00 pontos = R$ +600.00
Motivo: TP1
====================================================================

💾 Confirmar registro? (S/n): s

✅ Resultado registrado com sucesso!
```

## 💡 Casos de Uso

### 1. Importar Histórico de Trades

Se você tem planilha com trades passados:

```powershell
# Para cada trade da planilha, rode:
python backend/src/cli_inserir_manual.py nova
# ... preencha os dados
python backend/src/cli_inserir_manual.py resultado
# ... registre o resultado
```

### 2. Registrar Trade do Dia

Durante o pregão, quando gerar sinal:

```powershell
# Criar recomendação
python backend/src/cli_inserir_manual.py nova
# Usar data/hora atual, preencher setup

# No final do dia/trade
python backend/src/cli_inserir_manual.py resultado
# Registrar o que aconteceu
```

### 3. Popular para Testes

Para testar métricas detalhadas:

```powershell
# Criar várias recomendações com diferentes:
# - Tendências (ALTA/BAIXA/LATERAL)
# - Horários (manhã/tarde/fechamento)
# - Volatilidades (ATR baixo/médio/alto)
# - Resultados variados

# Depois analisar:
python backend/src/cli_avaliacao.py metricas-detalhadas --dias 30
```

## 🔗 Integração com Sistema

Dados inseridos manualmente são **100% compatíveis** com:

- ✅ CLI de avaliação (`cli_avaliacao.py`)
- ✅ Validador automático
- ✅ Métricas detalhadas (6 dimensões)
- ✅ Sistema de aprendizado contínuo

## 🚀 Próximos Passos

Depois de popular dados manualmente, você pode:

1. Analisar métricas detalhadas
2. Identificar padrões de sucesso
3. Implementar provider de API real
4. Automatizar inserção via análise técnica
5. Sistema aprende com ambos: dados manuais + automáticos

## ⚠️ Dicas

- **Data/hora**: Use sempre horário real do trade (importante para métricas por horário)
- **ATR**: Consulte seu gráfico ou use ~1000 como padrão para volatilidade média
- **Saldo Macro**: Reflita a força dos indicadores fundamentais no momento
- **Confiança**: Seja honesto - isso ajuda a calibrar o modelo depois
- **Observações**: Anote contextos especiais (notícia importante, abertura gap, etc)
