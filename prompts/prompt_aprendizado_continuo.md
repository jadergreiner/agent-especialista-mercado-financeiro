# 📚 PROMPT PARA APRENDIZADO CONTÍNUO

## 5. Prompt para Aprendizado Contínuo

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

## 🎯 Objetivo do Prompt

Este prompt é executado **após cada recomendação validada** para implementar aprendizado contínuo no sistema de análise de mercado financeiro.

## 📊 Estrutura de Entrada

### Variáveis Dinâmicas
- `{resultado_real_oportunidade}`: Resultado efetivo (ACERTOU/ERROU/CANCELADA/EXPIRADA)
- `{movimento_preco_observado}`: Movimento real de preço observado
- `{eventos_que_ocorreram}`: Eventos/notícias que efetivamente impactaram o mercado

### Exemplo de Uso
```python
dados_feedback = {
    "resultado_real_oportunidade": "ACERTOU - TP1 atingido em +380 pontos",
    "movimento_preco_observado": "WIN subiu 420 pontos em 3.5h",
    "eventos_que_ocorreram": "Dados de emprego EUA melhores que esperado + Fed hints dovish"
}
```

## 📈 Estrutura de Saída Esperada

```
## 📊 ANÁLISE DE PERFORMANCE - RECOMENDAÇÃO [ID/DATA]

### 🔍 COMPARAÇÃO PREVISTO vs REAL
- **Probabilidade**: Prevista 75% → Real: ACERTOU (100%)
- **Timeframe**: Estimado 2-4h → Real: 3.5h
- **Catalisadores**: Previstos [Dados EUA, Fed Speak] → Reais [Dados EUA, Fed Speak, Vendas institucionais]
- **Risco**: Stop R$500 → Máxima perda R$380

### ✅ O QUE FUNCIONOU BEM
- Análise técnica correta (suporte/resistência identificado)
- Timing de entrada preciso (±15min da previsão)
- Catalisador principal (dados emprego) identificado corretamente

### ⚠️ PONTOS DE MELHORIA
- Subestimou impacto do Fed Speak (peso deveria ser maior)
- Probabilidade de 75% poderia ser 65% (mais conservadora)
- Não considerou fluxo de vendas institucionais no pré-mercado

### 🔧 AJUSTES RECOMENDADOS
1. **Peso do Fator Macro**: +10% (atual: 30% → novo: 40%)
2. **Buffer de Probabilidade**: -5% para eventos de alto impacto
3. **Novos Inputs**: Adicionar análise de fluxo institucional
4. **Regras de Stop**: Aumentar distância em 15% para eventos macro

### 📈 PRÓXIMAS RECOMENDAÇÕES
- Aplicar ajustes acima nas próximas 3 recomendações
- Monitorar impacto na acurácia por 1 semana
- Revisar pesos novamente após 10 validações
```

## 🔄 Integração no Sistema

### Quando Executar
- **Após validação**: Toda recomendação que teve resultado definido
- **Frequência**: Diariamente (recomendações intraday) ou semanalmente (swing)
- **Contexto**: Parte do ciclo de feedback do sistema de aprendizado

### Como Integrar
1. **Capturar Dados**: Após validação automática/manual da recomendação
2. **Preencher Template**: Substituir variáveis com dados reais
3. **Executar Análise**: Usar LLM para gerar insights
4. **Aplicar Ajustes**: Atualizar pesos e regras no sistema
5. **Log de Aprendizado**: Registrar ajustes para auditoria

### Dependências
- Sistema de validação de recomendações (`TREINAMENTO_E_APRENDIZADO.md`)
- Banco de dados de recomendações e resultados
- Framework de pesos dinâmicos para fatores de decisão

## 📋 Checklist de Implementação

- [ ] Template do prompt criado
- [ ] Variáveis dinâmicas implementadas
- [ ] Integração com sistema de validação
- [ ] Mecanismo de ajuste de pesos
- [ ] Log de aprendizados
- [ ] Testes com dados históricos
- [ ] Validação de melhorias na performance

## 🎯 Benefícios Esperados

1. **Melhoria Contínua**: Sistema aprende com erros e acertos
2. **Adaptação**: Ajustes automáticos a mudanças de mercado
3. **Transparência**: Histórico completo de aprendizados
4. **Otimização**: Melhoria gradual da acurácia e profit factor
5. **Robustez**: Sistema mais resiliente a diferentes regimes de mercado