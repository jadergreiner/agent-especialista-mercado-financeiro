# Documentação – Estrutura Ágil

Esta pasta concentra documentos leves, vivos e práticos, voltados a decisões, backlog e roadmap. Objetivo: registrar ideias, priorizar próximas entregas e manter rastreabilidade.

## Estrutura

- ROADMAP.md — visão por horizontes (próximo, médio, longo prazo)
- BACKLOG.md — ideias e tarefas com status/priorização
- CHANGELOG.md — histórico de mudanças relevantes
- ADR/ — decisões de arquitetura (uma página por decisão)
- SCHEMAS.md — contratos JSON e validação

## Convenções

- Linguagem: Português
- Atualizações pequenas e frequentes (no mínimo por entrega)
- Cada decisão relevante deve ter um ADR com contexto → decisão → consequências
- Cada mudança em produção deve ser registrada no CHANGELOG (data + resumo)

## Fluxo sugerido

1) Criar item no BACKLOG com rascunho de valor/escopo
2) Quando aprovado, mover para ROADMAP (próximo ciclo)
3) Implementou? Registre no CHANGELOG e, se aplicável, crie/atualize ADR
4) Marcar item como concluído no BACKLOG

---

Manter estes arquivos curtos evita que a documentação fique obsoleta e incentiva ciclos ágeis de melhoria contínua.