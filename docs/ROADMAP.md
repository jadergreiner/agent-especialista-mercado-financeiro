# Roadmap (Top-Level)

Atualizado: 2025-11-06

## 🔜 Próximas entregas (1–2 semanas) — Estratégia Prompt-First

- Prompt Interativo v1 (CLI conversacional) com ajuda, histórico curto e cancelamento
- Templates de prompt e contratos mínimos de saída (Forex/Cripto) com validação leve
- Resolução de símbolo/aliases e fallback CSV manual com mensagens claras
- Fontes de dados de baixa fricção (yfinance/CSV) com cache simples
- Observabilidade: log de sessões (auditoria) e tempos de resposta

## 🔁 Curto/médio prazo (1–2 meses)

- Revalidação T+24h e métricas de assertividade automatizadas
- Dashboard inicial com visão das últimas análises e filtros básicos
- Integração com exchanges (ex.: Binance/Bybit) para preços intraday cripto e funding real
- Enriquecimento on-chain (Glassnode/CryptoQuant) com cache e limites de taxa

## 🌉 Médio prazo (3–6 meses)

- Orquestração de estratégias (Strategy Pattern) com backtesting integrado
- Feature store para sinais/indicadores normalizados (versionado)
- Pipelines de ML (scikit-learn/LightGBM) para recomendação probabilística
- Paper trading para setups priorizados (vwap_pullback_reject, breakout_sri)

## 🧭 Longo prazo (6–12 meses)

- Execução automatizada (conectores com corretoras) com gestão de risco centralizada
- Explainability dos sinais (SHAP/feature importance) na UI
- Simulador multi-ativo e rebalanceamento dinâmico de portfólio

---

Obs.: o ROADMAP é vivo — manter enxuto e atualizá-lo por entrega.
