# Backlog (Top-Level)

Última atualização: 2025-11-06 (pós Prompt-First v2)

## A Fazer (To Do) — Próximas iterações v3

- [ ] Suporte a timeframes dinâmicos (complemento)
	- Adaptação da lógica de análise para cada timeframe (diario, semanal, mensal)
	- Ajustes de fontes de dados conforme timeframe (quando aplicável)
- [ ] Aliases customizáveis por usuário
	- Arquivo de configuração `.aliases.json` no home do usuário
	- Comandos para adicionar/remover aliases personalizados
- [ ] Histórico persistente entre sessões — complementos
	- Filtros e busca por comando/período
	- Limpeza/rotação automática do arquivo de histórico
- [ ] Testes automatizados end-to-end
	- Suite pytest com cobertura >= 80%
	- Testes de integração com mocks de fontes de dados
	- CI/CD com validação automática

## Em Progresso (Doing)

- Nenhum item em progresso no momento

## Postergado (Depriorizado temporariamente)

- [ ] Revalidação T+24h e métricas de assertividade
- [ ] Dashboard: cards/visões para setups e assertividade
- [ ] Event-bus: metadados de qualidade de dados
- [ ] Novos setups (ex.: breakout_sri, reteste_fib_618)

## Concluídos (Done)

### Fase Prompt-First v2 (2025-11-06)

- [x] Cache de resultados entre sessões (`backend/cache_sessoes.py`)
	- SQLite como storage (leve, sem dependências externas)
	- TTL configurável por classe: Forex (5min), Cripto (2min)
	- Invalidação automática por expiração
	- Métodos: obter, armazenar, invalidar, limpar_expirados, estatisticas
	- Redução de latência: 80-85% em cache hits (<500ms vs 2-5s)
- [x] Comandos compostos e batch
	- Suporte a múltiplos pares: `analisar EURUSD GBPUSD BTCUSDT`
	- Processamento sequencial (não paralelo na v2)
	- Saída diferenciada: JSON completo para único / resumo consolidado para batch
- [x] Comando `cache` para observabilidade
	- Estatísticas em tempo real (total, válidas, expiradas, por classe)
	- Taxa de acerto (cache hits/misses)
- [x] Integração cache no CLI
	- Indicadores visuais (⚡ HIT / 🔄 MISS)
	- Limpeza automática de expirados ao sair
	- Contadores de hits/misses por sessão
- [x] Fix encoding UTF-8 para Windows
	- Solução para UnicodeEncodeError com emojis
	- Configuração automática de stdout/stderr
- [x] Testes de integração v2
	- Teste unitário do cache (5 casos)
	- Teste de integração CLI + cache
	- Todos os testes passaram ✅
- [x] Documentação v2
	- Guia de uso v2: `backend/GUIA_CLI_PROMPT_FIRST_V2.md`
	- Relatório técnico: `docs/RELATORIO_PROMPT_FIRST_V2.md`

### Fase Prompt-First v3 (em andamento)

- [x] Timeframes dinâmicos (MVP)
	- Parser do CLI aceita `intraday|diario|semanal|mensal`
	- Campo `timeframe` no contrato e chave do cache
	- Mantido motor intraday (adaptação da lógica ficará no complemento)

- [x] Histórico persistente (MVP)
	- Armazenamento dos comandos em `backend/logs/historico_cli.txt` (timestamp UTC + comando)
	- Carregamento dos últimos comandos na inicialização (mantém histórico curto do REPL)
	- Novo comando `historico [N]` para consulta dos últimos N (padrão 10, máx. 100)

### Fase Prompt-First v1 (2025-11-06)

- [x] CLI Conversacional v1 (`backend/cli_prompt_first.py`)
	- Loop REPL interativo com comandos: ajuda, sair, analisar
	- Histórico de comandos (últimos 5)
	- Log de sessões em JSONL com latência e status
	- Tempo de resposta < 3s para consultas simples
- [x] Resolução de símbolos e normalização
	- Aliases automáticos: BTCUSD→BTCUSDT, ETHUSD→ETHUSDT, EUR/USD→EURUSD
	- Inferência automática de classe (forex vs cripto)
	- Mensagens claras de normalização
- [x] Templates e contratos mínimos v1
	- Contratos padronizados (Forex/Cripto) em JSON
	- Validador estrutural (`backend/validador_contratos.py`)
	- Validação de campos obrigatórios e tipos básicos
- [x] Fontes de dados integradas
	- yfinance como fonte primária
	- Fallback CSV manual (reutilizado infra existente)
	- Conversão de relatórios completos para contratos mínimos
- [x] Observabilidade básica
	- Log estruturado JSONL em `backend/logs/sessoes_cli.jsonl`
	- Medição de latência por comando
	- Resumo de sessão ao encerrar
- [x] Testes mínimos
	- Validador testado com casos válidos e inválidos
	- Smoke test criado (`backend/test_smoke_cli.py`)
- [x] Documentação completa
	- Guia de uso: `backend/GUIA_CLI_PROMPT_FIRST.md`
	- Especificações: `docs/prompt-first/` (4 arquivos)
	- Relatório técnico: `docs/RELATORIO_PROMPT_FIRST_V1.md`

### Fases anteriores

- [x] `setup.v1` e emissão no emissor de sinais
- [x] Fallback CSV PT-BR para CRIPTO e análise VIRTUALUSDT end-to-end
- [x] Persistência em SQLite: relatórios e revalidações
- [x] Estrutura de documentação ágil em `docs/` (diário, organização, roadmap/changelog)
