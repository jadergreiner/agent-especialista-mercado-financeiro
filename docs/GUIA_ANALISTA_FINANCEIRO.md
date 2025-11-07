# Guia do Analista Financeiro

Orientações práticas para usar o agente no dia a dia, sem necessidade de conhecimentos técnicos.

## Objetivo

Permitir que o Analista:

- Inicie/pare o agente
- Acompanhe métricas e alertas
- Interprete sinais de trading
- Execute um checklist básico de saúde do sistema

## Antes de começar

- Confirme com o time técnico se o ambiente está configurado (venv, dependências, credenciais).
- Verifique se você usará Modo Simulado (paper) ou Produção (live).

## Como Iniciar o Agente

1) Abra o PowerShell na pasta do projeto

```powershell
cd c:\repo\projetos\agent-especialista-mercado-financeiro
.\.venv\Scripts\Activate
python backend/sistema_integrado_trading.py
```

2) Aguarde o log inicial de “conectado” e “estratégias carregadas”.

3) Para encerrar, use Ctrl+C na janela do PowerShell.

## Verificando o Status

- Console: mensagens de progresso, execução de estratégias e monitoramento
- Bancos de dados: registros em `data/*.db` (acesso via time técnico)
- (Opcional) Dashboard Web: http://localhost:5001/ (se habilitado) 
  - /api/metricas → métricas atuais
  - /api/alertas → alertas ativos

## Interpretando Sinais e Alertas

- Sinais de Compra/Venda: gerados por estratégias (ex.: média móvel, RSI)
- Alertas de Risco: concentração, drawdown, volatilidade, stop loss
- Ação Recomendada: 
  - Paper: validar coerência dos sinais antes de qualquer operação real
  - Live: conferir limites de risco e confirmar execução

## Rotina Sugerida (Dia de Mercado)

1) Pré-abertura (10–15 min)
   - Rodar uma demo rápida: `python backend/sistema_integrado_trading.py --demo`
   - Conferir se há alertas pendentes de risco

2) Durante o pregão
   - Acompanhar alertas e métricas a cada 30–60 min
   - Validar sinais fora do horário de eventos macro relevantes

3) Fechamento
   - Registrar P&L do dia e maiores contribuições
   - Verificar drawdown e exposição por ativo

## Boas Práticas

- Mantenha o agente em modo paper até que os resultados sejam consistentes
- Em caso de comportamento inesperado, pause (Ctrl+C) e comunique o time técnico
- Não compartilhe credenciais; use `.env` gerenciado pela equipe

## Perguntas Frequentes

1) “Não vejo sinais; está tudo certo?”
   - Sim, pode não haver sinais dependendo do mercado. Verifique se estratégias estão ativas e símbolos corretos.

2) “Os números do portfólio estão zerados; é erro?”
   - Em modo simulado, sem posições abertas, métricas podem iniciar em zero.

3) “Como saber se estou em live ou paper?”
   - Verifique com o time técnico e confirme no arquivo `config/corretoras.json`.
