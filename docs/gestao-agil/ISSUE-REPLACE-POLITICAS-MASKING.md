Título: Substituir `politicas-masking.md` por versão limpa

Contexto
-------
O arquivo `docs/gestao-agil/politicas-masking.md` na branch `feature/AG-rbac-audit-masking` contém múltiplas duplicações e formatações que disparam o markdown-linter (MD022/MD024/MD025 e outros). Isso impede a aprovação do PR relacionado ao trabalho de masking.

Proposta
-------
1. Revisar e aprovar o rascunho limpo localizado em `docs/gestao-agil/politicas-masking-clean.md`.
2. Após aprovação, substituir `politicas-masking.md` pela versão limpa e garantir que o markdown-linter passe.
3. Registrar no changelog/PR a referência a `DECISAO-002` conforme política do repositório.

Observações
-------
- Mantive um rascunho limpo em `docs/gestao-agil/politicas-masking-clean.md` para revisão rápida.
- Preferi não sobrescrever automaticamente o arquivo original devido a múltiplas tentativas de patch que geraram conteúdo duplicado; a PR deve fazer a substituição de forma controlada.

Checklist de aceitação
-------
- [ ] `politicas-masking-clean.md` revisado pelo time de Segurança/PO
- [ ] `politicas-masking.md` substituído e linter verde para markdown
- [ ] Commit com mensagem clara e referência `AG-005` e `DECISAO-002`
