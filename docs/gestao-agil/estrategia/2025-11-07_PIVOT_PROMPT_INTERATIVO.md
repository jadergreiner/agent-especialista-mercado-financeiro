# PIVOT ESTRATÉGICO — Foco em Prompt Interativo para Análise de Ativos

Data: 2025-11-07
Responsável: Product Owner (PO)
Stakeholders: Tech Lead, Gerente de Portfólio, UX, Dados

---

## Contexto e Motivação

Decidimos priorizar a entrega de valor via **uso interativo do prompt para solicitar análise de ativos** (multi-mercado: FX, índices, ouro, eventualmente ações/fundos). A motivação é acelerar o ciclo de descoberta/valor para o usuário com:
- Tempo de aprendizado e feedback mais rápido (curva de adoção menor)
- Menor dependência de integrações complexas iniciais
- Alto impacto percebido com análises sob demanda e linguagem natural
- Base sólida para evoluir para automação (somente após validação de valor)

---

## Mudança de Estratégia

Antes: foco em gestão de portfólio automatizada, dashboards e execução/guardrails avançados.
Depois: foco em **MVP de Prompt Interativo** com respostas estruturadas, fontes e explicabilidade.

Regras de ouro:
- Sem promessas de performance; **sem execução automática** nesta fase
- Transparência radical: riscos, limitações, fontes, timestamp
- Saída estruturada: hipótese, drivers, riscos, próximos passos
- Latência sob controle e logs de auditoria

---

## Objetivos do MVP

1. Usuário realizar perguntas do tipo: "Analise EUR/USD no diário e me diga drivers, riscos e próximos passos"
2. Sistema responder com:
   - Preço atual, variação e contexto temporal
   - 2-3 drivers/fundamentais relevantes + 2-3 sinais técnicos simples (SMA/RSI)
   - Riscos e contranarrativas (ex.: eventos macro, volatilidade)
   - Próximos passos acionáveis (ex.: o que monitorar)
   - Fontes/citações (URLs) e timestamp
   - JSON estruturado + renderização Markdown

---

## Decisões de Arquitetura

- Orquestrador de Prompt (LLM) com "tool selection" para:
  - Cotação atual/histórico (fonte simples inicial)
  - Indicadores técnicos leves (SMA/RSI)
  - Notícias/catalisadores (resumo e links)
- Templates de prompt com few-shots (modos: Analista, Trader Rápido)
- Saída dupla: Markdown (humano) + JSON (máquina)
- Cache e memória de sessão para acelerar iterações
- Disclaimers e política de linguagem: SEM recomendações de investimento
- Logs de latência e auditoria de chamadas

---

## Métricas de Sucesso (MVP)

- TTR (Time-to-Response):
  - < 5s com cache / < 20s sem cache
- Utilidade percebida (survey rápida no CLI):
  - "Resposta foi útil?" ≥ 80% SIM
- Cobertura de ativos prioritários:
  - FX (EURUSD, USDJPY, GBPJPY, AUDNZD), XAUUSD
- Confiança/rastrabilidade:
  - 100% respostas com fontes e timestamp

---

## Riscos e Mitigações

- Alucinações do modelo → Sempre exigir fontes e checagens básicas
- Dados desatualizados → Timestamp e alerta se > X minutos
- Over-promises → Disclaimers claros; evitar linguagem prescritiva
- Desempenho/latência → Cache, escolha de ferramentas mínimas viáveis

---

## Roadmap de Produto (Pivot)

1) SPRINT PROMPT INTERATIVO — MVP v1 (prioridade máxima)
- CLI Prompt Interativo (reusar `backend/cli_prompt_first.py` como base)
- Orquestrador de ferramentas (preço, indicadores leves, notícias)
- Templates e modos de análise (Analista / Trader Rápido)
- Saída JSON + Markdown; fontes e timestamp
- Cache/memória de sessão
- Guia de Uso do Prompt (docs)

2) Fundação Operacional (suporte contínuo)
- Qualidade de dados (validador + schema)
- Logs/telemetria e métricas de latência
- Disclaimers e políticas de linguagem

3) Evoluções (pós-MVP)
- Web UI leve (dashboard de conversas)
- Indicadores técnicos adicionais e filtros de regime
- Painéis de risco agregados e correlação
- Backtesting de "assertividade" textual em histórico

---

## Dependências e Artefatos Relacionados

- Reuso: `backend/cli_prompt_first.py`, `backend/cli.py`, `backend/avaliar_portfolio_html.py`
- Guias: `backend/GUIA_CLI_PROMPT_FIRST.md`, `backend/GUIA_CLI_PROMPT_FIRST_V2.md`
- Backlog: `docs/gestao-agil/backlog.md` (histórias US-PROMPT-*)

---

## Conclusão

Este pivot coloca o usuário no centro via **conversas produtivas e transparentes**.
Com um MVP enxuto e bem explicado, maximizamos valor e aprendizado, pavimentando o caminho para automação responsável depois.
