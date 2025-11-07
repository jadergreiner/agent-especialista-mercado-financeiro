# 📋 Exemplo de Uso - CLI Gestor Fundo Completo

## 🎯 Objetivo

Este guia demonstra como usar a interface CLI para registrar operações no sistema de gestão do fundo com análise integrada.

## 🚀 Como Executar

```powershell
cd backend
python cli_gestor_fundo_completo.py
```text\n## 📝 Fluxo de Interação

### Passo 1: Tela Inicial

```text
================================================================================
🎯 GESTOR DO FUNDO - SISTEMA DE ENTRADA DE OPERAÇÕES
================================================================================

💡 Este sistema registra operações e gera análise completa com:
   ✓ Validação de gates de segurança
   ✓ Análise de risco do portfólio
   ✓ Coerência macroeconômica
   ✓ Análise de correlações
   ✓ Recomendações inteligentes

================================================================================
📊 COLETA DE DADOS DA OPERAÇÃO
================================================================================
```text\n### Passo 2: Informar Ticket Único

```text
🔖 Ticket da operação (obrigatório, ex: #OP20250107001): #OP20250107001
```text\n**⚠️ REGRA IMPORTANTE**: O ticket deve ser único no portfólio. Se já existir, o sistema retorna erro.

### Passo 3: Informar Ativo

```text
📈 Ativo (ex: EUR/USD, GBP/JPY): GBP/JPY
```text\n**Formato aceito**: Pares forex no formato XXX/YYY (3 letras, barra, 3 letras).

### Passo 4: Direção da Operação

```text
⬆️  Direção (LONG/SHORT): LONG
```text\n**Opções válidas**:

- `LONG` - Comprado (apostando na alta)
- `SHORT` - Vendido (apostando na baixa)

### Passo 5: Preço de Entrada

```text\n💵 Preço de entrada (ex: 195.25): 195.25
```text\n**Validação**: Deve ser número decimal positivo.

### Passo 6: Volume em Lotes

```text\n📊 Volume em lotes (ex: 0.01): 0.05
```text\n**Validação**: Deve ser número decimal positivo.

### Passo 7: Data e Hora

```text\n📅 Data/Hora entrada (formato: YYYY-MM-DD HH:MM:SS): 2025-01-07 14:30:00
```text\n**Formato obrigatório**: `YYYY-MM-DD HH:MM:SS`
**Exemplo**: `2025-01-07 14:30:00`

### Passo 8: Confirmação

```text\n================================================================================
📋 CONFIRMAÇÃO DOS DADOS
================================================================================

🔖 Ticket: #OP20250107001
📈 Ativo: GBP/JPY
⬆️  Direção: LONG
💵 Preço: 195.25
📊 Volume: 0.05 lotes
📅 Data: 2025-01-07 14:30:00

Os dados estão corretos? (s/n): s
```text\n**Opções**:
- `s` ou `S`: Confirma e processa operação
- `n` ou `N`: Cancela e volta ao início

### Passo 9: Processamento

```text\n================================================================================
⚙️  PROCESSANDO OPERAÇÃO...
================================================================================

[INÍCIO] Validando gates de segurança...
✅ Gates validados com sucesso
   ✓ Ticket: #OP20250107001
   ✓ Ativo: GBP/JPY
   ✓ Direção: LONG
   ✓ Preço: $195.2500
   ✓ Volume: 0.05 lotes

[DURANTE] Atualizando portfólio...
✅ Portfólio atualizado com sucesso

[FIM] Gerando relatório executivo completo...
```

### Passo 10: Relatório Executivo

```text================================================================================
💼 RELATÓRIO EXECUTIVO DO FUNDO
================================================================================
📅 Data: 07/01/2025 14:32:15

📈 RESUMO DO PORTFÓLIO
--------------------------------------------------
💰 Capital Total: $100,000.00
📊 Posições Ativas: 36
💵 P&L Total: $+325,450.12 (+325.45%)
   └─ Não Realizado: $+58,900.00
   └─ Realizado: $+266,550.12
💎 Exposição Total: $6,145,000.00
⚖️  Alavancagem: 61.45x

💱 EXPOSIÇÃO POR MOEDA
------------------------------
   XAU: +$3,983,250
   USD: $-3,150,000
   JPY: $-2,050,000
   CHF: +$360,000
   GBP: +$195,250

⚠️  ANÁLISE DE RISCO
--------------------------------------------------
🚨 Nível de Alerta: ALTO
⚠️  Alavancagem: 61.45x (Limite: 50.0x)
📊 Concentração JPY: 33.36% (Limite: 30%)

🌐 COERÊNCIA MACROECONÔMICA
--------------------------------------------------
📊 VIX: 22.6 (Volatilidade MODERADA)
💵 DXY: 99.5 (USD NEUTRO)
🎯 Cenário: NEUTRO
✅ Alinhamento: COERENTE

🔗 ANÁLISE DE CORRELAÇÃO
--------------------------------------------------
⚠️  Exposições Redundantes: EUR, USD, CHF, JPY, AUD, CAD, NZD, GBP
📊 Pares Únicos: 25

💡 RECOMENDAÇÕES INTELIGENTES
--------------------------------------------------
📋 Gestão de Posições: 36 recomendações
🆕 Novas Oportunidades: 2 identificadas
🛡️  Gestão de Risco: 3 alertas
⚖️  Balanceamento: 2 sugestões
```text\n### Passo 11: Opção de Ver Recomendações

```text\n📄 Deseja ver as recomendações detalhadas? (s/n): s
```text\n**Se responder `s`**: Mostra análise completa de todas as recomendações
**Se responder `n`**: Pula para salvamento automático

### Passo 12: Salvamento Automático

```text\n💾 Relatório salvo em: backend/relatorios/relatorio_fundo_20250107_143215.txt

================================================================================
✅ OPERAÇÃO REGISTRADA COM SUCESSO!
================================================================================

💡 Próximos passos:
   1. Verificar alertas de risco no relatório
   2. Analisar recomendações para outras posições
   3. Acompanhar evolução do portfólio
```text\n## 📊 Exemplo de Sessão Completa

```text\nC:\repo\projetos\agent-especialista-mercado-financeiro\backend> python cli_gestor_fundo_completo.py

================================================================================
🎯 GESTOR DO FUNDO - SISTEMA DE ENTRADA DE OPERAÇÕES
================================================================================

💡 Este sistema registra operações e gera análise completa com:
   ✓ Validação de gates de segurança
   ✓ Análise de risco do portfólio
   ✓ Coerência macroeconômica
   ✓ Análise de correlações
   ✓ Recomendações inteligentes

================================================================================
📊 COLETA DE DADOS DA OPERAÇÃO
================================================================================

🔖 Ticket da operação (obrigatório, ex: #OP20250107001): #OP20250107001
📈 Ativo (ex: EUR/USD, GBP/JPY): GBP/JPY
⬆️  Direção (LONG/SHORT): LONG
💵 Preço de entrada (ex: 195.25): 195.25
📊 Volume em lotes (ex: 0.01): 0.05
📅 Data/Hora entrada (formato: YYYY-MM-DD HH:MM:SS): 2025-01-07 14:30:00

================================================================================
📋 CONFIRMAÇÃO DOS DADOS
================================================================================

🔖 Ticket: #OP20250107001
📈 Ativo: GBP/JPY
⬆️  Direção: LONG
💵 Preço: 195.25
📊 Volume: 0.05 lotes
📅 Data: 2025-01-07 14:30:00

Os dados estão corretos? (s/n): s

================================================================================
⚙️  PROCESSANDO OPERAÇÃO...
================================================================================

[... processamento ...]

✅ OPERAÇÃO REGISTRADA COM SUCESSO!
```text\n## ⚠️ Validações e Erros Comuns

### ❌ Erro: Ticket Vazio

```text\n🔖 Ticket da operação (obrigatório, ex: #OP20250107001):
❌ ERRO: Ticket é obrigatório e não pode ser vazio!
```text\n### ❌ Erro: Ticket Duplicado

```text\n❌ ERRO na validação de gates: Ticket #OP20250107001 já existe no portfólio
```text\n**Solução**: Use um ticket único diferente.

### ❌ Erro: Direção Inválida

```text\n⬆️  Direção (LONG/SHORT): BUY
❌ ERRO: Direção deve ser LONG ou SHORT
```text\n**Solução**: Digite exatamente `LONG` ou `SHORT`.

### ❌ Erro: Preço Inválido

```text\n💵 Preço de entrada (ex: 195.25): abc
❌ ERRO: Preço deve ser um número decimal válido
```text\n**Solução**: Digite apenas números com ponto decimal (ex: `195.25`).

### ❌ Erro: Formato de Data Incorreto

```text\n📅 Data/Hora entrada (formato: YYYY-MM-DD HH:MM:SS): 07/01/2025
❌ ERRO: Formato de data inválido. Use: YYYY-MM-DD HH:MM:SS
```text\n**Solução**: Use o formato exato `2025-01-07 14:30:00`.

## 📁 Arquivos Gerados

O sistema salva automaticamente o relatório executivo em:

```text\nbackend/relatorios/relatorio_fundo_YYYYMMDD_HHMMSS.txt
```text\n**Exemplo**: `backend/relatorios/relatorio_fundo_20250107_143215.txt`

## 🎯 Boas Práticas

### ✅ Padrão de Tickets

Recomendamos usar um padrão consistente para tickets:

- `#OP20250107001` - Operação do dia 07/01/2025, sequencial 001
- `#OP20250107002` - Operação do dia 07/01/2025, sequencial 002
- `#SWING20250107A` - Swing trade do dia 07/01/2025, identificador A

### ✅ Validação Pré-Entrada

Antes de registrar a operação:

1. Confira o preço de entrada no gráfico
2. Valide o volume com seu gerenciamento de risco
3. Certifique-se de que o ticket é único
4. Verifique a direção (LONG/SHORT)

### ✅ Acompanhamento

Após registrar:

1. Leia os alertas de risco no relatório
2. Revise as recomendações para ajustes de posição
3. Monitore a exposição por moeda
4. Acompanhe a alavancagem total

## 🔧 Troubleshooting

### Problema: CLI não inicia

```powershell
# Verificar se está no diretório correto
pwd
# Deve mostrar: C:\repo\projetos\agent-especialista-mercado-financeiro\backend

# Verificar se o arquivo existe
ls cli_gestor_fundo_completo.py
```text\n### Problema: Erro de importação

```powershell
# Instalar dependências
pip install -r requirements.txt
```text\n### Problema: Portfólio não encontrado

O sistema cria automaticamente o arquivo `data/portfolio/portfolio_atual.json` na primeira execução.

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique o log do sistema em `logs/`
2. Revise este guia de uso
3. Consulte `GESTOR_FUNDO_APROVADO.md` para entender a arquitetura

---

**Data de Criação**: 07/01/2025
**Versão**: 1.0
**Status**: ✅ Pronto para uso

