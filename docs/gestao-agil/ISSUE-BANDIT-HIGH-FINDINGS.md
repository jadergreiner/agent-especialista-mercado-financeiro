# ISSUE: Findings de alta severidade (Bandit)

# Contexto

Durante a análise de segurança executada como parte da atividade `AG-005` (masking/audit), rodei o scanner Bandit contra o diretório `backend` para identificar potenciais problemas de segurança.

# Resumo executado

Comando: `bandit -r backend -lll`
Data: 2025-11-08

Sumário de findings relevantes (High): 6

Encontrados (localizações e resumo):

1. `backend/carregador_dados_historicos.py:653`
   - Plugin: B324 (hashlib)
   - Descrição: Uso de MD5 para hashing (`hashlib.md5(...).hexdigest()`), considerado fraco para propósitos de segurança.
   - Severidade: High
   - Recomendações: substituir por `hashlib.sha256(...).hexdigest()` ou usar `hashlib.pbkdf2_hmac`/`scrypt`/`bcrypt`/`argon2` dependendo do caso de uso; documentar o motivo e etapa de migração para dados já gerados.

2. `backend/instalar_integracao_corretoras.py:18`
   - Plugin: B602 (subprocess with shell=True)
   - Descrição: Uso de `subprocess.run(..., shell=True)` permite injeção se o comando contiver inputs não controlados.
   - Severidade: High
   - Recomendações: usar lista de argumentos (e.g. `['cmd', 'arg1']`) sem `shell=True`, validar/escapar entradas ou usar API específica do fornecedor.

3. `backend/monitor_posicao_win.py:110`
4. `backend/monitor_win_dashboard.py:17`
5. `backend/monitor_win_realtime.py:36`
6. `backend/monitoramento/monitor_win_base.py:19`
   - Plugin: B605 (start process with a shell / os.system)
   - Descrição: Uso de `os.system('cls' if os.name == 'nt' else 'clear')` em vários arquivos. Chamar shell pode ser inseguro em contextos onde inputs são concatenados.
   - Severidade: High
   - Recomendações: substituir por chamadas seguras (p.ex. `subprocess.run(['cls'], shell=False)` no Windows ou, preferencialmente, evitar limpar a tela via shell — usar bibliotecas cross-platform como `shutil.get_terminal_size` ou `curses` para operações de terminal). Se a limpeza da tela for puramente cosmetic e não lidar com inputs externos, documentar o risco e manter; caso contrário, eliminar ou mitigar.

# Observações adicionais

- Bandit também relatou muitos problemas de severidade baixa e média pelo repo (Low: 164; Medium: 17). Recomendo triagem por prioridade.
- Alguns arquivos foram pulados por error de parse do AST (lista no final da saída do Bandit). Aqueles devem ser revisados manualmente.

# Plano de remediação sugerido (curto prazo)

1. Criar issues separadas para cada finding de High com: arquivo, linha, proposta de fix e responsável.
2. Priorizar a substituição de MD5 (B324) e a remoção/mitigação do uso de `shell=True` / `os.system` (B602/B605) por serem alta severidade.
3. Para cada mudança, adicionar testes unitários quando aplicável e um ticket de migração para dados historicamente gerados com MD5.
4. Envolver Time de Segurança para revisão e aprovação das correções.

# Ação realizada

- Arquivo criado: `docs/gestao-agil/ISSUE-BANDIT-HIGH-FINDINGS.md` com este conteúdo.
- Posso abrir issues individuais ou criar um PR com correções de exemplo (ex.: trocar MD5 por SHA256) se você autorizar.

# Próximo passo sugerido

- Deseja que eu crie issues individuais automaticamente (um por finding High) e/ou abra um PR de correção mínima para um dos itens (recomendo começar substituindo MD5 por SHA256 em `backend/carregador_dados_historicos.py`)?
