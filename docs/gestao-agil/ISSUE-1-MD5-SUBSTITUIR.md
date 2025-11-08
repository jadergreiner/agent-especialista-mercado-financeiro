# ISSUE-1: Substituir MD5 por algoritmo seguro (B324)

## Contexto

Scanner de segurança (Bandit) identificou uso de MD5 em `backend/carregador_dados_historicos.py` (linha ~653). MD5 é considerado criptograficamente fraco e foi marcado como High (B324).

## Local

- Arquivo: `backend/carregador_dados_historicos.py`
- Linha aproximada: 653

## Descrição do problema

O código calcula um hash dos bytes serializados do cache usando MD5. MD5 não é seguro para funções de integridade sensível nem para derivação/assinatura de dados.

## Proposta de remediação

1. Substituir `hashlib.md5(...).hexdigest()` por `hashlib.sha256(...).hexdigest()`.
2. Adicionar comentário/nota de origem e motivo no código.
3. Se houver dependência funcional no tamanho ou formato do hash — documentar e criar um plano de migração para dados previamente gerados (mapeamento/remoção de duplicatas, re-hash progressivo).

## Tarefas

- [ ] Revisar o PR de correção e aprovar.
- [ ] Executar testes que dependam do hash (se existirem).
- [ ] Gerar ticket de migração se necessário para dados históricos.

## Responsável sugerido

- [ ] Engenheiro responsável pelo componente de carregamento de dados (sugestão: @time-data)

## Notas

- Alteração já aplicada localmente na branch `feature/AG-rbac-audit-masking` (commit: substituição por sha256). Verificar CI/testes.
