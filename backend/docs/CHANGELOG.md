# Changelog

Todas as mudanças relevantes neste projeto.

## [2025-11-06]
### Adicionado
- CLI de revalidação T+24h (`backend/cli_revalidar.py`) com persistência de assertividade em SQLite
- Documentos ágeis: `ROADMAP.md`, `BACKLOG.md`, `CHANGELOG.md`

### Melhorado
- Emissor de sinais passou a publicar `setup.v1` (vwap_pullback_reject) com sufixo correto no nome do arquivo
- Loader de CSV manual (`utils/dados_manuais.py`) compatível com formatos PT-BR (BOM, cabeçalhos com aspas, decimais com vírgula)

### Corrigido
- Fallback robusto para símbolos cripto não mapeados (ex.: `VIRTUALUSDT`) com mensagens de orientação