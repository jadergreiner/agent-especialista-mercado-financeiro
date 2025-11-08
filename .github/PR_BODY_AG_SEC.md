Resumo:
- Substituição de MD5 por SHA-256 em `backend/carregador_dados_historicos.py` (Origin: AG-SEC-001).
- Evitação de `shell=True` em `instalar_integracao_corretoras.py` (executar_comando usa agora shlex.split + shell=False) (Origin: AG-SEC-002).
- Substituição de `os.system('clear'/'cls')` por utilitário `backend/utils/terminal.py::limpar_tela()` em scripts de monitoramento.

Arquivos alterados (principais):
- backend/carregador_dados_historicos.py
- backend/instalar_integracao_corretoras.py
- backend/utils/terminal.py
- backend/monitor_posicao_win.py
- backend/monitor_win_dashboard.py
- backend/monitor_win_realtime.py
- backend/monitoramento/monitor_win_base.py
- docs/gestao-agil/ISSUE-BANDIT-HIGH-FINDINGS.md
- docs/gestao-agil/ISSUE-1-MD5-SUBSTITUIR.md
- docs/gestao-agil/ISSUE-2-SUBPROCESS-SHELL_TRUE.md
- docs/gestao-agil/ISSUE-3-OS_SYSTEMS-MITIGAR.md

Verificações executadas:
- Bandit re-run (local): High findings = 0

Notas:
- Comentários `# Origin:` foram adicionados nas alterações de código conforme a política do repositório.
- Há 7 arquivos ignorados pelo Bandit por erro de parsing; sugiro revisão manual desses arquivos.

Solicito revisão de segurança e aprovação para merge. Obrigado.