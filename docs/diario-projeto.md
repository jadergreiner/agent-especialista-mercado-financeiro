# 🗓️ Diário do Projeto

Registre aqui, de forma breve e objetiva, o progresso diário e marcos relevantes.

## Como usar

- Uma entrada por dia útil (ou quando houver progresso relevante)
- Tópicos curtos: o que foi feito, por que, e impacto
- Vincule Epico/Feature/História/Tarefa quando aplicável

---

## Entradas

### 2025-11-06

- Criados documentos de gestão ágil: `docs/gestao-agil/organizacao_agil.md`, `docs/diario-projeto.md`
- Unificada visão de governança: ROADMAP/BACKLOG/CHANGELOG serão mantidos em `docs/`
- Atualizado README com seção de Gestão Ágil e criado `docs/ROADMAP.md` e `docs/CHANGELOG.md`
- Pivot estratégico: foco Prompt-First para uso interativo do prompt; backlog e roadmap reorganizados
- **✅ Entrega Prompt-First v1 completa (2h de implementação)**:
  - CLI Conversacional v1 (`backend/cli_prompt_first.py`): REPL com ajuda/sair/analisar, histórico, logs de sessão e medição de latência
  - Validador de contratos mínimos (`backend/validador_contratos.py`) com validação estrutural de campos obrigatórios
  - Normalização de símbolos integrada (aliases: BTCUSD→BTCUSDT); fallback CSV já existente reutilizado
  - Documentação completa: guia de uso, especificações e relatório técnico
- Backlog atualizado com itens concluídos (v1) e próximas iterações sugeridas (v2): cache, comandos compostos, timeframes dinâmicos, aliases customizáveis, histórico persistente, testes automatizados
- **📝 Comportamento padrão de gestão de backlog estabelecido**:
  - Regra fundamental: Toda atividade pendente deve ser registrada no backlog
  - Fluxo claro: Time/Copilot registra → PO prioriza no momento estratégico adequado
  - Documentado em `docs/gestao-agil/organizacao_agil.md` e `.github/copilot-instructions.md`
  - Benefícios: nenhuma pendência perdida, backlog centralizado, decisões estratégicas pelo PO, WIP limit natural
- **✅ Entrega Prompt-First v2 completa (2h de implementação)**:
  - Módulo de cache (`backend/cache_sessoes.py`): SQLite, TTL por classe (forex 5min / cripto 2min), invalidação automática
  - CLI v2 integrado com cache: indicadores visuais (⚡ HIT / 🔄 MISS), redução de latência 80-85%
  - Comandos em batch: `analisar EURUSD GBPUSD BTCUSDT` com resumo consolidado
  - Comando `cache`: estatísticas em tempo real, taxa de acerto
  - Fix encoding UTF-8 para Windows (UnicodeEncodeError resolvido)
  - Testes de integração: cache + CLI, todos passaram ✅
  - Documentação v2: guia de uso e relatório técnico completos
