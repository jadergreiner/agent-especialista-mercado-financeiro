# Arquitetura e Orquestração de Mercados

Objetivo: Maximizar o valor do agente avaliando o mercado como um todo (Forex, Cripto, Ações/Dividendos, FIIs), padronizando sinais, relatórios e decisões sob uma orquestração única e orientada a eventos.

---

## Visão Geral (Target Operating Model)

- Camadas
  - Ingestão de Dados: preços, notícias, calendário econômico, COT, on-chain, fundamentals.
  - Engenharia de Sinais: normalização, features (VWAP, SRIs, EMAs, volatilidade), detecção de regimes.
  - Núcleo de Mercado (Fusão): correlações cross-mercado, viés global (DXY, taxas, commodities, crypto cap), consistência entre sinais.
  - Estratégias & Decisão: repositório de estratégias (Strategy Registry) e seletor dinâmico por regime.
  - Risco & Exposição: guardrails (limites de posição, correlação, drawdown, VAR simplificado), sizing, heat do portfólio.
  - Execução & Relatório: plano 4–8h, ordens (paper/real), relatórios markdown, alertas.
  - Observabilidade & Aprendizado: métricas (Sharpe, Sortino, hit-rate), feedback loop (pós-mortem), storage histórico.

- Padrões
  - Arquitetura orientada a eventos (Event-Driven): barramento de sinais; produtores (ingestão) e consumidores (estratégias/risco/relatório).
  - Contratos de dados (Data Contracts): JSON-schemas por tipo de sinal e relatório; versionamento (v1, v1.1…).
  - Orquestração por Sessões de Mercado: pré-abertura, intraday (janelas 4–8h), pós-fechamento.

---

### Diagramas (Visão Visual)

Para diagramas end-to-end (layers, orquestração, barramento e contratos), acesse:

- [ARQUITETURA_MERCADO_DIAGRAMA.md](./ARQUITETURA_MERCADO_DIAGRAMA.md)

---

## Orquestração de Sessões (Macros e Intraday)

- Pré-Abertura (T-1h → T0)
  - Baixar calendário do dia (CPI, NFP, FOMC, earnings relevantes) e mapear criticidade por mercado.
  - Atualizar viés macro: DXY, UST 2/10Y, Commodities (WTI, Ouro), Crypto Total Cap.
  - Inicializar cache de dados intraday e SRIs (H1/H4) por ativo monitorado.

- Loop Intraday (T0 → T+8h)
  - Frequência: 1–5 min (forex/cripto); 5–15 min (ações/FIIs intraday leve).
  - Pipeline: Ingestão → Features → Fusão de Sinais → Score Estratégias → Risco → Decisão/Plano → Relatório/Alerta → Persistência.
  - Gatilhos de Alta Prioridade: eventos de calendário (CPI, NFP, FOMC), spikes de volatilidade, quebras de SRIs chave, desvios significativos de VWAP.

- Pós-Fechamento
  - Atribuição de performance por sinal/estratégia/mercado.
  - Aprendizado: atualizar pesos/thresholds, identificar estratégias por regime de volatilidade.
  - Higienização: rotação de caches, snapshots para histórico (SQLite → futuro PostgreSQL).

---

## Barramento de Sinais (Signal Bus)

- Tipos de eventos
  - market.tick (preço intraday)
  - macro.calendar (evento agendado)
  - macro.news (headline classificada)
  - vol.spike (mudança abrupta de σ)
  - tech.breakout (quebra de SRI/padrão)
  - flow.orderflow (heurística fluxo)
  - onchain.metric (picos de liquidação/funding)

- Regras gerais
  - Cada evento possui: id, tipo, timestamp UTC, origem, payload (JSON), prioridade, TTL.
  - Consumidores assíncronos (estratégias/risco/relatórios) filtram por tipo e prioridade.

---

## Modelo de Dados Unificado (v1)

- AssetId: namespace + símbolo (ex.: forex:EURUSD, cripto:BTCUSDT, eq:B3:PETR4, fii:B3:KNRI11)
- Quote
  ```json
  {
    "schema": "quote.v1",
    "assetId": "forex:EURUSD",
    "ts": "2025-11-06T12:34:56Z",
    "o": 1.1501, "h": 1.1512, "l": 1.1497, "c": 1.1510,
    "tf": "5m",
    "extras": {"vwap": 1.1507, "ema20": 1.1508, "ema50": 1.1504}
  }
  ```
- Sinal Técnico
  ```json
  {
    "schema": "signal.tech.v1",
    "assetId": "forex:EURUSD",
    "ts": "2025-11-06T12:35:00Z",
    "features": {"trend15m": "ALTISTA", "rangePct": 0.13, "sris": {"sup": [1.1477], "res": [1.1668]}},
    "score": 0.62
  }
  ```
- Sinal Macro/Fluxo
  ```json
  {
    "schema": "signal.macroflow.v1",
    "assetId": "forex:EURUSD",
    "ts": "2025-11-06T12:36:00Z",
    "macro": {"dxyDaily": 0.0, "riskRegime": "Risco-On"},
    "flow": {"orderflow5m": "NEUTRO", "volRealizada": "BAIXA"}
  }
  ```
- Relatório Intraday (Contrato)
  ```json
  {
    "schema": "report.intraday.v1",
    "assetId": "forex:EURUSD",
    "ts": "2025-11-06T12:37:00Z",
    "operacao": "ESPERAR",
    "viesSessao": "Dólar estável",
    "rr": "1:1.5",
    "partes": {
      "macro": {"eventos": ["EUR: Discurso BCE"], "dxy": 0.0},
      "tecnica": {"vwap": 1.1507, "range": {"max": 1.1511, "min": 1.1497, "ampPct": 0.13}, "sris": {"sup": [], "res": []}, "tendencia15m": "ALTISTA", "invalidacao": 1.1507},
      "fluxo": {"orderflow": "NEUTRO", "vol": "BAIXA", "cot": "NEUTRO"}
    },
    "plano": {"entrada": 1.1507, "alvo1": 1.1511, "alvo2": 1.1497, "stop": 1.1507}
  }
  ```

---

## Núcleo de Mercado (Fusão de Sinais)

- Inputs: sinais técnicos (multi-timeframe), macro (DXY, yields), fluxo (orderflow/IV), on-chain (cripto), fundamentals (dividendos/FIIs).
- Processos
  - Normalização e ponderação por regime (volatilidade baixa/média/alta).
  - Correlação e conflito: se sinais conflitarem (macro vs técnica), reduzir confiança (score) e recomendar ESPERAR.
  - Bias globais: risk-on/off; USD forte/fraco; commodities em alta/baixa; crypto em aceleração/desaceleração.
- Output: score consolidado por ativo + justificativas.

---

## Estratégias e Seleção Dinâmica

- Registry de Estratégias
  - momentum.intraday, meanreversion.intraday, eventos.macro, breakout.sri, vwap.reversion.
- Seleção por Regime
  - Vol baixa: mean-reversion, vwap.
  - Vol alta: breakout/event-driven.
  - Conflito de sinais: degradar alocação ou esperar.
- Contrato de Estratégia
  - Entradas: sinais normalizados (tech/macro/flow).
  - Saídas: direção, pontos (entrada/TPs/stop), confiança, R/R esperado.

---

## Risco, Exposição e Governança

- Guardrails
  - Limites por classe (forex/cripto/ações/FIIs) e por ativo.
  - Heat por correlação: evitar somar exposição em ativos altamente correlacionados.
  - VAR simplificado por janela 4–8h; max drawdown intraday; stops obrigatórios.
- Sizing
  - Função do risco (distância ao stop) e confiança do sinal.
- Conformidade
  - Registros de decisões; justificativas anexadas aos relatórios; auditoria simplificada.

---

## Observabilidade e Feedback Loop

- KPIs
  - Sharpe/Sortino intraday, hit-rate por estratégia, R/R efetivo, latência de geração de relatório/alerta, precisão de alertas.
- Alertas de Saúde
  - Falhas em provedores (yfinance/COT/agenda); quedas de ingestão; aumento de latência; buracos de dados.
- Pós-Mortem
  - Para perdas acima de limiar: registrar contexto de sinais, comparar com decisões alternativas.

---

## Playbooks de Eventos

- CPI/NFP/FOMC
  - Congelar entradas 10–15 min antes; usar volatilidade implícita proxy para alargar stops/targets ou evitar trade.
- Quebra de SRI Major
  - Elevar prioridade do evento tech.breakout e reavaliar todos ativos correlatos.
- Liquidações massivas (Cripto)
  - Checar funding e book; operar reversão com stops curtos ou evitar se fluxo segue direcional.

---

## Roteiro de Implementação (Sprints)

1. Padronização de Contratos (v1)
   - JSON-schemas (quote, signal.tech, signal.macroflow, report.intraday).
   - Adaptar analisadores existentes (forex/cripto) para publicar no barramento.
2. Orquestrador de Sessões (MVP)
   - Loop async: agenda → ingestão → features → fusão → decisão → relatório → persistência.
   - Prioridades por evento de calendário.
3. Núcleo de Mercado (Fusão)
   - Ponderação por regime; detecção de conflito; bias globais.
4. Guardrails de Risco
   - Limites por classe/ativo; sizing por risco; heat por correlação.
5. Observabilidade
   - Métricas e logs estruturados; dashboards mínimos; alertas de saúde.
6. Execução e Paper Trading Integrado
   - Mock de ordens; simulação de custos; atribuição de performance por estratégia.

---

## Integração com o Código Atual

- Forex Intraday (pronto): ajustar saída para o contrato report.intraday.v1 e publicar no barramento.
- Cripto Intraday (pronto): alinhar contrato e publicar.
- Dividendos/FIIs (planejado): produzir sinais semanais/diários (não intraday) para bias cross-mercado.
- Persistência: SQLite como base (analises_*) e migração futura para PostgreSQL.

---

## Papéis de Agentes (Governança de Decisão)

- Arquiteto de Negócios
  - Define a arquitetura alvo, contratos de dados e padrões de orquestração.
  - Prioriza entregas por impacto e risco; cuida de SLOs e observabilidade.
  - Zela por compliance, versionamento e interoperabilidade entre mercados.

- Especialista em Mercado Financeiro Global
  - Interpreta o contexto macro global (USD/DXY, curvas, commodities, risco sistêmico) e spillovers entre classes.
  - Ajusta as heurísticas/limiares por regime de volatilidade e por sessão (Tóquio/Londres/NY).
  - Revisa SRIs multi-timeframe (H1/H4/D1), regras de VWAP por sessão e exceções em eventos (CPI/NFP/FOMC).

- Arquiteto de Dados
  - Lidera a taxonomia e a modelagem de dados do agente (nomeação, domínios e entidades).
  - Mantém o catálogo/registry de contratos (JSON-schemas), versionamento semântico e compatibilidade backward.
  - Define padrões de tempo/unidades (UTC sempre; Decimal para valores monetários; convenções de timeframe/sessão).
  - Estabelece controles de qualidade (validações, preenchimento de buracos, flags de confiabilidade) e data lineage.
  - Desenha camadas de persistência (bronze/prata/ouro) e retenção (SQLite → PostgreSQL), além de partições por tempo/assetId.
  - Padroniza enums/glossário (operacao, tendencia, fluxo, vol, regimes) e o formato único de assetId.

Ambos participam de comitês rápidos (15–20 min) de revisão do plano operacional intraday quando gatilhos de alta prioridade ocorrem.

---

## Especificação do Orquestrador (pseudo)

```
while session.open:
  eventos = agenda.hoje_priorizados()
  for asset in watchlist:
    quotes = ingest(asset)
    feats  = features(quotes)
    sinais = fusao(asset, feats, macro, flow)
    plano  = estrategias.apply(asset, sinais)
    if risco.aprova(asset, plano):
      rel = reporter.gerar(asset, sinais, plano)
      persist(rel)
      alert(rel)
  sleep(cadencia(asset))
```

---

## Benefícios Esperados

- Decisões consistentes entre mercados e regimes.
- Reuso de componentes (features, fusão, risco, reporter) e contratos comuns.
- Observabilidade e evolução contínua via feedback loop.
- Facilidade para adicionar novas classes de ativos e estratégias sob o mesmo barramento de sinais.
