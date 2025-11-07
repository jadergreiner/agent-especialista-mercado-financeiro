# SPRINT 0 — Plano Técnico: Prompt Interativo MVP

Data de Início: 2025-11-07
Duração: 1 sprint (1-2 semanas)
Objetivo: Entregar MVP funcional de análise interativa via prompt com fontes, transparência e estrutura

---

## Escopo do Sprint 0

Histórias incluídas:
- **US-PROMPT-001**: CLI Prompt Interativo (MVP)
- **US-PROMPT-002**: Orquestrador de Ferramentas (Preço/Indicadores/Notícias)
- **US-PROMPT-004**: Saída Estruturada + Fontes e Timestamp
- **US-PROMPT-006**: Segurança e Disclaimers
- **US-RISCO-002**: Qualidade de dados (IDs, tickets, preços) — suporte essencial

---

## Arquitetura Proposta

```
backend/
├── cli_prompt_mvp.py                    # [NOVO] CLI principal do MVP
├── orquestrador_analise.py              # [NOVO] Orquestração de ferramentas + LLM
├── ferramentas/                         # [NOVO] Módulo de ferramentas
│   ├── __init__.py
│   ├── preco_atual.py                   # obter_preco_atual(ativo)
│   ├── indicadores_tecnicos.py          # calcular_sma_rsi(ativo, timeframe)
│   └── noticias_resumidas.py            # buscar_noticias_resumidas(ativo, limit)
├── formatadores/                        # [NOVO] Formatação de saídas
│   ├── __init__.py
│   ├── json_estruturado.py              # Saída JSON padronizada
│   └── markdown_relatorio.py            # Renderização Markdown
├── validadores/                         # [NOVO] Validação e disclaimers
│   ├── __init__.py
│   ├── validador_portfolio.py           # [RISCO-002] Validação de dados
│   └── disclaimers.py                   # Textos de segurança
└── utils/
    ├── cache_simples.py                 # Cache básico para preços/notícias
    └── logger_analise.py                # Logs estruturados
```

---

## US-PROMPT-001: CLI Prompt Interativo (MVP)

### Objetivo
Comando único `python cli_prompt_mvp.py analise <ativo> [--timeframe] [--modo]` que retorna análise estruturada.

### Tarefas Técnicas

1. **Criar `backend/cli_prompt_mvp.py`**
   - Argparse com: ativo (obrigatório), --timeframe (padrão: '1D'), --modo (padrão: 'analista')
   - Validação de inputs (ticker válido, timeframe conhecido)
   - Chamada ao orquestrador
   - Exibição de saída Markdown + salvamento JSON

2. **Contratos de Entrada/Saída**
   ```python
   # Entrada CLI
   ativo: str         # Ex: "EURUSD", "XAUUSD"
   timeframe: str     # Ex: "5M", "1H", "1D"
   modo: str          # Ex: "analista", "trader_rapido"

   # Saída esperada
   {
     "ativo": str,
     "timeframe": str,
     "timestamp": str (ISO 8601),
     "preco_atual": float,
     "variacao_pct": float,
     "drivers": [str],
     "riscos": [str],
     "proximos_passos": [str],
     "fontes": [{"titulo": str, "url": str}],
     "disclaimer": str
   }
   ```

3. **Testes de Sanidade**
   - Executar com ativos válidos (EURUSD, XAUUSD)
   - Validar JSON de saída
   - Verificar presença de disclaimer

### Dependências
- Orquestrador (US-PROMPT-002)
- Formatadores (US-PROMPT-004)
- Disclaimers (US-PROMPT-006)

### Estimativa
3 dias (incluindo integração)

---

## US-PROMPT-002: Orquestrador de Ferramentas

### Objetivo
Módulo central que coordena chamadas a ferramentas e orquestra o LLM para análise.

### Tarefas Técnicas

1. **Criar `backend/orquestrador_analise.py`**
   ```python
   def orquestrar_analise(ativo: str, timeframe: str, modo: str) -> dict:
       """
       Coordena execução de ferramentas e análise.

       Fluxo:
       1. obter_preco_atual(ativo)
       2. calcular_sma_rsi(ativo, timeframe)
       3. buscar_noticias_resumidas(ativo, limit=3)
       4. Montar contexto e chamar LLM
       5. Validar resposta e aplicar disclaimer
       6. Retornar estrutura JSON
       """
   ```

2. **Criar `backend/ferramentas/preco_atual.py`**
   ```python
   def obter_preco_atual(ativo: str) -> dict:
       """
       Retorna: {
         "preco": float,
         "variacao_pct": float,
         "timestamp": str,
         "fonte": str
       }

       Fonte inicial: Alpha Vantage ou Yahoo Finance
       Tratamento de erro: raise ValueError se ativo desconhecido
       """
   ```

3. **Criar `backend/ferramentas/indicadores_tecnicos.py`**
   ```python
   def calcular_sma_rsi(ativo: str, timeframe: str, janela_sma: int = 20) -> dict:
       """
       Retorna: {
         "sma_20": float,
         "rsi_14": float,
         "preco_vs_sma": str  # "acima", "abaixo", "neutro"
       }

       Usa pandas + TA-Lib ou pandas-ta
       """
   ```

4. **Criar `backend/ferramentas/noticias_resumidas.py`**
   ```python
   def buscar_noticias_resumidas(ativo: str, limit: int = 3) -> list[dict]:
       """
       Retorna: [{
         "titulo": str,
         "resumo": str,
         "url": str,
         "data": str,
         "fonte": str
       }]

       Fonte inicial: NewsAPI ou agregador interno
       """
   ```

5. **Integração com LLM**
   - Usar OpenAI API (ou Azure OpenAI)
   - Template de prompt com few-shots para modo "analista" e "trader_rapido"
   - Parsing estruturado da resposta (JSON mode ou regex)

6. **Tratamento de Erros**
   - Timeouts de API → mensagem clara
   - Dados ausentes → placeholder "N/D" + alerta
   - Rate limiting → retry com backoff

### Dependências
- Variáveis de ambiente (ALPHA_VANTAGE_API_KEY, OPENAI_API_KEY)
- Bibliotecas: requests, pandas, ta-lib ou pandas-ta

### Estimativa
4 dias

---

## US-PROMPT-004: Saída Estruturada + Fontes e Timestamp

### Objetivo
Garantir JSON padronizado e Markdown legível com fontes rastreáveis.

### Tarefas Técnicas

1. **Criar `backend/formatadores/json_estruturado.py`**
   ```python
   def formatar_json(analise: dict) -> dict:
       """
       Valida e normaliza estrutura JSON.
       Campos obrigatórios:
       - ativo, timeframe, timestamp
       - preco_atual, variacao_pct
       - drivers[], riscos[], proximos_passos[]
       - fontes[], disclaimer
       """
   ```

2. **Criar `backend/formatadores/markdown_relatorio.py`**
   ```python
   def gerar_markdown(analise: dict) -> str:
       """
       Renderiza JSON em Markdown bonito com:
       - Header: ativo, preço, variação, timestamp
       - Seções: Drivers | Riscos | Próximos Passos
       - Footer: Fontes (com links) + Disclaimer
       """
   ```

3. **Validação de Fontes**
   - Todas as URLs devem ser válidas (regex básico)
   - Timestamp em ISO 8601
   - Preço/variação com 2-4 casas decimais

### Dependências
- Schema JSON (pode usar Pydantic para validação)

### Estimativa
2 dias

---

## US-PROMPT-006: Segurança e Disclaimers

### Objetivo
Proteger contra interpretações prescritivas e garantir conformidade.

### Tarefas Técnicas

1. **Criar `backend/validadores/disclaimers.py`**
   ```python
   DISCLAIMER_PADRAO = """
   ⚠️ AVISO IMPORTANTE:
   Esta análise é apenas informativa e educacional.
   NÃO constitui recomendação de investimento.
   Mercados financeiros envolvem risco de perda.
   Consulte um profissional qualificado antes de operar.
   """

   def aplicar_disclaimer(analise: dict) -> dict:
       """Injeta disclaimer na estrutura."""

   def validar_linguagem_prescritiva(texto: str) -> bool:
       """Detecta palavras proibidas: "compre", "venda", "garantido"."""
   ```

2. **Lista de Palavras Proibidas**
   - "compre", "venda", "recomendo"
   - "certeza", "garantido", "sem risco"
   - Alertar se detectado e reescrever automaticamente

3. **Integração no Orquestrador**
   - Aplicar disclaimer antes de retornar JSON
   - Log de auditoria se linguagem prescritiva detectada

### Dependências
- Nenhuma

### Estimativa
1 dia

---

## US-RISCO-002: Qualidade de Dados (Suporte)

### Objetivo
Validar dados de portfólio e APIs antes de análise.

### Tarefas Técnicas

1. **Criar `backend/validadores/validador_portfolio.py`**
   ```python
   def validar_portfolio_json(filepath: str) -> list[dict]:
       """
       Valida:
       - IDs únicos
       - Tickets consistentes
       - Preços > 0
       - Datas válidas

       Retorna lista de erros encontrados.
       """
   ```

2. **Validação de Dados de APIs**
   ```python
   def validar_preco_api(preco: dict) -> bool:
       """
       Checa:
       - Campo 'preco' existe e > 0
       - Timestamp recente (< 1h para forex)
       """
   ```

3. **Testes Unitários**
   - Casos de dados válidos e inválidos
   - Cobertura de edge cases (preços negativos, IDs duplicados)

### Dependências
- Schema JSON do portfólio

### Estimativa
0.5 dia (paralelo com outras tarefas)

---

## Sequência de Implementação (Incremental)

### Fase 1 (Dias 1-2): Fundação
- [ ] Criar estrutura de diretórios (`ferramentas/`, `formatadores/`, `validadores/`)
- [ ] Implementar `preco_atual.py` (fonte: Alpha Vantage ou Yahoo Finance)
- [ ] Implementar `disclaimers.py`
- [ ] Teste manual: obter preço de EURUSD e aplicar disclaimer

### Fase 2 (Dias 3-4): Ferramentas + Orquestrador
- [ ] Implementar `indicadores_tecnicos.py` (SMA/RSI)
- [ ] Implementar `noticias_resumidas.py` (NewsAPI ou scraping básico)
- [ ] Implementar `orquestrador_analise.py` (chamada LLM mock inicial)
- [ ] Teste manual: executar orquestrador com dados reais

### Fase 3 (Dias 5-6): Formatação + CLI
- [ ] Implementar `json_estruturado.py` e `markdown_relatorio.py`
- [ ] Implementar `cli_prompt_mvp.py`
- [ ] Integração completa: CLI → Orquestrador → Formatação
- [ ] Teste end-to-end: `python cli_prompt_mvp.py analise EURUSD --timeframe 1D`

### Fase 4 (Dia 7): Validação + Polimento
- [ ] Implementar `validador_portfolio.py` (US-RISCO-002)
- [ ] Testes de edge cases e tratamento de erros
- [ ] Documentação inline (docstrings)
- [ ] README de uso do MVP

---

## Riscos Técnicos e Mitigações

### Risco 1: Latência de APIs externas
- **Mitigação**: Cache simples (TTL 5min para preços, 1h para notícias)
- **Fallback**: Mensagem clara se timeout

### Risco 2: Qualidade de respostas do LLM
- **Mitigação**: Few-shots bem calibrados; validação de estrutura JSON
- **Fallback**: Modo degradado com resposta simplificada

### Risco 3: Rate limits de APIs
- **Mitigação**: Retry com exponential backoff
- **Fallback**: Alertar usuário e sugerir aguardar

### Risco 4: Dados desatualizados
- **Mitigação**: Sempre exibir timestamp; alerta se > 15min (forex)

---

## Métricas de Sucesso (Sprint 0)

- [ ] **Funcional**: CLI executa sem erros para EURUSD, XAUUSD, USDJPY
- [ ] **Latência**: < 20s sem cache, < 5s com cache
- [ ] **Qualidade**: 100% respostas com disclaimer e fontes
- [ ] **Rastreabilidade**: JSON salvo em `backend/data/analises/` com timestamp
- [ ] **Documentação**: README com exemplos de uso

---

## Próximos Passos (Pós-Sprint 0)

Após validação do MVP:
1. Sprint 1: Templates de modo (US-PROMPT-003), cache avançado (US-PROMPT-005), métricas (US-PROMPT-007)
2. Sprint 2: Guia de uso (US-PROMPT-008), indicadores técnicos adicionais
3. Validação com usuários reais e coleta de feedback
4. Evoluções: web UI, backtesting de assertividade, análise multi-timeframe

---

## Dependências Externas

- **APIs**:
  - Alpha Vantage (preços forex/ouro) — gratuito com limite
  - NewsAPI (notícias) — gratuito tier
  - OpenAI API (LLM) — custo por token
- **Bibliotecas Python**:
  - requests, pandas, ta-lib (ou pandas-ta)
  - python-dotenv, click (ou argparse)

---

## Conclusão

Este plano técnico fornece um roadmap incremental e testável para o Sprint 0.
Cada fase entrega valor parcial e permite validação antecipada.
A abordagem modular facilita extensões futuras sem reescritas.

**Status**: Pronto para implementação
**Aprovação PO**: Pendente
**Tech Lead**: Confirmar disponibilidade de APIs e credenciais
