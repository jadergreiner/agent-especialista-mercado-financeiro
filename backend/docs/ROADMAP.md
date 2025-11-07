# Roadmap

Atualizado: 2025-11-06

## 🔜 Próximas entregas (1–2 semanas)
- Revalidação T+24h (CLI/cron) consolidada para Forex e Cripto com métricas de assertividade
- Dashboard: destacar setups (setup.v1) com score/confluências e filtro por par/timeframe
- Fallback manual estendido para Forex/Ações/Índices/Commodities (mesmo padrão de CRIPTO)
- Métricas de qualidade de dados: flags visíveis em relatórios e no event-bus

## 🔁 Curto/médio prazo (1–2 meses)
- Integração com exchanges (ex.: Binance/Bybit) para preços intraday cripto e funding real
- Enriquecimento on-chain (Glassnode/CryptoQuant) com cache e limites de taxa
- Avaliação automatizada de modelos: tracking de precisão por classe de ativo/timeframe/setup
- Paper trading para setups priorizados (vwap_pullback_reject, breakout_sri)

## 🌉 Médio prazo (3–6 meses)
- Orquestração de estratégias (Strategy Pattern) com backtesting integrado
- Feature store para sinais/indicadores normalizados (versionado)
- Pipelines de ML (scikit-learn/LightGBM) para recomendação probabilística

## 🧭 Longo prazo (6–12 meses)
- Execução automatizada (conectores com corretoras) com gestão de risco centralizada
- Explainability dos sinais (SHAP/feature importance) na UI
- Simulador multi-ativo e rebalanceamento dinâmico de portfólio

---

Obs.: o ROADMAP é vivo — manter enxuto e atualizá-lo por entrega.