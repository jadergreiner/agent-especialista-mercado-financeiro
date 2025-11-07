# Backlog

Última atualização: 2025-11-06

## A Fazer (To Do)
- [ ] Forex: implementação da busca de preço T+24h (yfinance + fallback CSV) em `cli_revalidar.py`
- [ ] Dashboard: cards para assertividade por par, classe e setup (últimos 7/30 dias)
- [ ] Event-bus: incluir metadados de qualidade de dados (ex.: fonte=fallback_csv)
- [ ] Monitor: alerta quando setup disparar e houver confluência forte (score ≥ 80)
- [ ] Testes: unitários para `dados_manuais.carregar_ohlcv_csv` e `cli_revalidar.calcular_assertividade`

## Em Progresso (Doing)
- [ ] Normalização de setups adicionais (ex.: breakout_sri, reteste_fib_618)

## Concluídos (Done)
- [x] `setup.v1` e emissão no emissor de sinais
- [x] Fallback CSV PT-BR para CRIPTO e análise VIRTUALUSDT end-to-end
- [x] Persistência em SQLite: relatórios e revalidações
- [x] Estrutura de documentação ágil (README_DOCS + ROADMAP)