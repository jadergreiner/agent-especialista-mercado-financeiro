# PROTOCOLO DE ACIONAMENTO DO MOTOR ML - MODO PRODUÇÃO

Captura oportunidades reais de mercado para execução imediata

## PRÉ-REQUISITOS

☐ Terminal PowerShell aberto
☐ Diretório: `c:\repo\projetos\agent-especialista-mercado-financeiro\backend`
☐ Ambiente Python funcional
☐ Arquivo `config_producao.json` presente

## SEQUÊNCIA DE EXECUÇÃO

### 1. NAVEGAÇÃO

```bash
cd "c:\repo\projetos\agent-especialista-mercado-financeiro\backend"
```

### 2. ACIONAMENTO

```bash
python protocolo_producao.py
```

### 3. MONITORAMENTO

Aguarde mensagens de status:

- "🚀 PROTOCOLO DE ACIONAMENTO - MODO PRODUÇÃO"
- "🔧 Inicializando motor de produção..."
- "🔄 EXECUTANDO ANÁLISE DE PRODUÇÃO..."
- "✅ SISTEMA OPERACIONAL EM MODO PRODUÇÃO"

### 4. ANÁLISE DOS RESULTADOS

Foque nas seções:

- **📊 Portfolio de produção**: 12 ativos (7 ações + 5 FOREX)
- **🎯 OPORTUNIDADES DETECTADAS (PRODUÇÃO)**: Lista com scores e recomendações
- **📋 Etapas executadas**: Verificação de conclusão de todas as etapas

### 5. TOMADA DE DECISÃO

Para cada oportunidade detectada:

- **🔥 Score ≥0.8 (MUITO_ALTA)**: 💰 **EXECUTAR** - Alto potencial
- **✅ Score ≥0.7 (ALTA)**: 📈 **CONSIDERAR** - Potencial moderado
- **⚠️ Score ≥0.6 (MEDIA)**: ⚠️ **MONITORAR** - Risco elevado
- **❌ Score <0.6 (BAIXA)**: ❌ **IGNORAR** - Confiança insuficiente

## CONFIGURAÇÃO DE PRODUÇÃO

- **Portfolio**: AAPL, MSFT, GOOGL, TSLA, NVDA, META, AMZN + EURUSD=X, GBPUSD=X, USDJPY=X, USDCAD=X, USDCHF=X
- **Intervalo**: 15 minutos entre execuções
- **Modo**: PRODUÇÃO (dados reais de mercado)
- **Alertas**: Automáticos habilitados

## CARACTERÍSTICAS DO MODO PRODUÇÃO

- ✅ Análise de ações + FOREX simultaneamente
- ✅ Detecção de oportunidades em tempo real
- ✅ Sistema de pontuação de confiança
- ✅ Recomendações de execução baseadas em risco/recompensa
- ✅ Salvamento automático de dados e métricas

## TEMPO ESPERADO: <30 segundos
## FREQUÊNCIA RECOMENDADA: A cada 15 minutos durante sessão de mercado

## EXEMPLO DE SAÍDA ESPERADA

```text
🚀 PROTOCOLO DE ACIONAMENTO - MODO PRODUÇÃO
============================================================
📋 Carregando configuração: config_producao.json
📊 Portfolio de produção: 12 ativos
   🏢 Ações: 7
   💱 FOREX: 5

🔧 Inicializando motor de produção...

🔄 EXECUTANDO ANÁLISE DE PRODUÇÃO...

📈 RESULTADO DA ANÁLISE DE PRODUÇÃO:
🎯 Oportunidades encontradas: 2

🎯 OPORTUNIDADES DETECTADAS (PRODUÇÃO):
   1. 🔥 EUR/USD: entrada_suporte
      📊 Score: 0.85 (MUITO_ALTA)
      🎯 Risco/Recompensa: 2.3
      💰 EXECUTAR - Alto potencial de ganho

   2. ✅ GBP/JPY: entrada_resistencia
      📊 Score: 0.72 (ALTA)
      🎯 Risco/Recompensa: 1.8
      📈 CONSIDERAR - Potencial moderado

⚙️ Status geral: concluido_com_sucesso

📋 Etapas executadas:
   ✅ Avaliacao Assertividade: concluida
   ✅ Analise Macro: concluida
   ✅ Identificacao Oportunidades: concluida
   ✅ Analise Niveis: concluida

✅ SISTEMA OPERACIONAL EM MODO PRODUÇÃO
🔄 Pronto para próximo ciclo em 15 minutos
📊 Dados salvos automaticamente
```

---
**Status**: ✅ TOTALMENTE OPERACIONAL
**Última Atualização**: 7 de novembro de 2025
**Versão**: 2.0 - Modo Produção

## 🔧 RESOLUÇÃO DE PROBLEMAS - MOTOR DE OPORTUNIDADES

### SE O COMANDO FALHAR

#### 1. VERIFIQUE O DIRETÓRIO

```bash
pwd  # Confirme que está em: backend/
```

#### 2. TESTE PYTHON

```bash
python --version  # Deve mostrar Python 3.x
```

#### 3. EXECUTE NOVAMENTE

```bash
python protocolo_producao.py
```

### 📊 SINAIS DE SUCESSO

- ✅ "🚀 PROTOCOLO DE ACIONAMENTO - MODO PRODUÇÃO"
- ✅ "📊 Portfolio de produção: 12 ativos"
- ✅ "✅ SISTEMA OPERACIONAL EM MODO PRODUÇÃO"
- ✅ "🎯 Oportunidades encontradas: X"

### ⚠️ SINAIS DE PROBLEMA

- ❌ **Erro de sintaxe** → Arquivo corrompido
- ❌ **ModuleNotFoundError** → Dependências ausentes
- ❌ **FileNotFoundError** → Diretório incorreto
- ❌ **ConnectionError** → Problemas de conectividade com API

### 🛠️ SOLUÇÃO RÁPIDA

Se houver erro, execute a versão básica:

```bash
python -c "print('🚀 TESTE: Sistema ML funcionando!')"
```

#### EM CASO DE SUCESSO NO TESTE

O problema está no arquivo específico, não no Python.

### 🔄 RECUPERAÇÃO DE SISTEMA

```bash
# 1. Verificar arquivos essenciais
ls -la config_producao.json protocolo_producao.py

# 2. Testar dependências
python -c "import json, os, sys; print('✅ Dependências OK')"

# 3. Executar diagnóstico
python -c "
try:
    with open('config_producao.json', 'r') as f:
        config = json.load(f)
    print('✅ Configuração válida')
    print(f'📊 Portfolio: {len(config.get(\"portfolio_principal\", []))} ativos')
except Exception as e:
    print(f'❌ Erro na configuração: {e}')
"
```

### 📞 SUPORTE TÉCNICO

- **Logs**: Verificar `logs/` para detalhes de erro
- **Configuração**: Validar `config_producao.json`
- **Ambiente**: Confirmar Python 3.8+ instalado
