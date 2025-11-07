# Changelog (Top-Level)

Todas as mudanças relevantes neste projeto.

## [2025-11-06]

### Adicionado

- CLI de revalidação T+24h (`backend/cli_revalidar.py`) com persistência de assertividade em SQLite
- Documentos ágeis: `docs/gestao-agil/organizacao_agil.md`, `docs/diario-projeto.md`, `docs/ROADMAP.md`, `docs/CHANGELOG.md`
- Documentação Prompt-First: `docs/prompt-first/contratos_resposta.md`, `docs/prompt-first/templates_prompt.md`, `docs/prompt-first/ux_cli.md`, `docs/prompt-first/resolucao_simbolos.md`
- CLI Conversacional v1 (`backend/cli_prompt_first.py`): REPL interativo com comandos ajuda/sair/analisar, histórico de comandos (últimos 5), logs de sessão em JSONL e medição de latência
- Validador de contratos mínimos (`backend/validador_contratos.py`): validação estrutural de campos obrigatórios e tipos básicos
- **[v2]** Módulo de cache (`backend/cache_sessoes.py`): SQLite com TTL por classe de ativo (forex 5min, cripto 2min), invalidação automática, estatísticas
- **[v2]** CLI v2 com cache integrado: indicadores visuais (⚡ HIT / 🔄 MISS), redução de latência 80-85% em cache hits
- **[v2]** Comandos em batch: suporte a múltiplos pares (`analisar EURUSD GBPUSD BTCUSDT`) com resumo consolidado
- **[v2]** Comando `cache`: estatísticas em tempo real (total, válidas, expiradas, taxa de acerto)
- **[v2]** Testes de integração v2 (`backend/test_integracao_v2.py`): validação de cache + CLI
- **[v2]** Documentação v2: `backend/GUIA_CLI_PROMPT_FIRST_V2.md` e `docs/RELATORIO_PROMPT_FIRST_V2.md`
 - **[v3]** Timeframes dinâmicos (MVP): CLI aceita `intraday|diario|semanal|mensal`, contrato e cache com `timeframe`
 - **[v3]** Histórico persistente (MVP): arquivo `backend/logs/historico_cli.txt` + comando `historico [N]`

### Melhorado

- Emissor de sinais passou a publicar `setup.v1` (vwap_pullback_reject) com sufixo correto no nome do arquivo
- Loader de CSV manual (`backend/src/utils/dados_manuais.py`) compatível com formatos PT-BR (BOM, cabeçalhos com aspas, decimais com vírgula)

### Corrigido

- Fallback robusto para símbolos cripto não mapeados (ex.: `VIRTUALUSDT`) com mensagens de orientação
- **[v2]** Fix encoding UTF-8 para Windows: resolvido UnicodeEncodeError com emojis no console
