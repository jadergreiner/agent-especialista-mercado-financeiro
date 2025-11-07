# Uso em Produção (Windows)

Guia operacional para colocar o agente em produção no Windows, com foco em estabilidade, repetibilidade e segurança.

## Requisitos

- Windows 10/11
- Python 3.10+ instalado (em PATH)
- Acesso à internet e às APIs das corretoras
- Credenciais válidas (paper/live) nas corretoras desejadas

## Passo 1 — Preparar Ambiente

1) Abra o PowerShell na pasta do projeto

```powershell
cd c:\repo\projetos\agent-especialista-mercado-financeiro
```

2) Crie e ative o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

3) (Opcional) Forçar UTF-8 no Python (evita erros com emojis no Windows)

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
```

## Passo 2 — Instalar Dependências

```powershell
pip install -r requirements.txt
```

Dependências opcionais:

- Alpaca: `pip install alpaca-trade-api`
- Interactive Brokers: `pip install ib-insync`
- Indicadores (fallback): `pip install pandas-ta`

TA-Lib no Windows: recomenda-se instalar via wheels (Gohlke) ou usar `pandas-ta` como alternativa.

## Passo 3 — Configurar o Sistema

1) Gere arquivos de configuração (se ainda não existirem)

```powershell
python backend/instalar_integracao_corretoras.py
```

2) Edite `config/corretoras.json` com suas credenciais e endpoints

3) Revise `config/estrategias.json` (símbolos, parâmetros, risco)

4) Ajuste `config/sistema_trading.json` (intervalos de ciclo, logs, porta Web)

5) (Opcional) Crie `.env` a partir de `config/.env.example` para segredos

## Passo 4 — Validação (Smoke Test)

```powershell
python backend/sistema_integrado_trading.py --demo
```

Verifique no console:

- Conector ativo: simulado ou corretora escolhida
- Estratégias carregadas e sinais processados (mesmo que 0)
- Métricas do portfólio calculadas

## Passo 5 — Execução em Produção

Execução direta (foreground):

```powershell
python backend/sistema_integrado_trading.py
```

Execução em segundo plano (Tarefa Agendada):

1) Abra o Agendador de Tarefas (Task Scheduler)
2) Crie uma Tarefa Básica → Disparador “Ao iniciar o computador” ou “Diariamente”
3) Ação: Iniciar um programa
4) Programa/script:

```text
Powershell.exe
```

5) Adicionar argumentos (ajuste caminhos conforme necessário):

```text
-NoProfile -ExecutionPolicy Bypass -Command "cd C:\repo\projetos\agent-especialista-mercado-financeiro; .\.venv\Scripts\Activate; $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; python backend/sistema_integrado_trading.py"
```

6) Marque “Executar com privilégios mais altos” se necessário

Alternativa: utilizar NSSM para rodar como serviço do Windows.

## Logs e Observabilidade

- Logs: por padrão no console; bancos SQLite em `data/` registram ordens, sinais e métricas.
- Recomenda-se redirecionar logs do console para arquivo quando rodar em produção.
- Próximos passos: logs estruturados e endpoints de saúde (ver backlog).

## Segurança e Conformidade

- Nunca comite credenciais. Use `.env` e variáveis de ambiente.
- Teste sempre em paper trading antes do live.
- Respeite limitações/regulamentos de sua corretora e jurisdição.

## Troubleshooting

- UnicodeEncodeError no Windows: use `PYTHONUTF8=1` e `PYTHONIOENCODING=utf-8`.
- `dashboard_web.py` falha (Exit Code 1): verifique Flask/Plotly e porta; rode `pip install Flask plotly`.
- Sem dados de mercado: verifique conectividade e `yfinance`.
- Erros de autenticação na corretora: confirme API keys, permissões de paper/live e IP/segurança.
