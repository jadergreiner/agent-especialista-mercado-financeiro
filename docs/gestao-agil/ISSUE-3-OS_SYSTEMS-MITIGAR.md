# ISSUE-3: Mitigar uso de os.system(...) (B605)

## Contexto

Bandit sinalizou chamadas a `os.system(...)` em múltiplos scripts de monitoramento (e.g. `backend/monitor_posicao_win.py`, `backend/monitor_win_dashboard.py`, `backend/monitor_win_realtime.py`, `backend/monitoramento/monitor_win_base.py`). Chamar o shell diretamente é classificado como High quando concatenam entradas ou usam variáveis externas.

## Local (exemplos)

- `backend/monitor_posicao_win.py:110`
- `backend/monitor_win_dashboard.py:17`
- `backend/monitor_win_realtime.py:36`
- `backend/monitoramento/monitor_win_base.py:19`

## Descrição do problema

Uso de `os.system('cls' if os.name == 'nt' else 'clear')` e variações executam comandos no shell. Mesmo que a intenção seja apenas limpar a tela, em alguns contextos isso pode ser explorável se inputs forem concatenados.

## Proposta de remediação

1. Evitar `os.system` quando possível; usar `subprocess.run(['cls'])` com `shell=False` ou bibliotecas de terminal (e.g., `curses`, `rich.console` para clearing de tela).
2. Se a chamada for puramente cosmetic e não processa entradas externas, documentar o risco e marcar como aceita com justificativa.

## Tarefas

- [ ] Identificar todas as ocorrências de `os.system` no repo.
- [ ] Substituir por `subprocess.run([...], shell=False)` ou por biblioteca cross-platform.
- [ ] Se mantiver, adicionar comentário de justificação e criar teste que valide comportamento em ambiente controlado.

## Responsável sugerido

- [ ] Engenheiro(s) que mantêm os scripts de monitoramento / ferramentas internas

## Notas

- Pequenas mudanças: dividir por arquivo/PRs para facilitar review.
