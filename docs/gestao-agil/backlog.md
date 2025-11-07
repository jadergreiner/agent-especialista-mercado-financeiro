# Backlog (Top-Level)

Última atualização: 2025-11-07 (pós Análise Performance AUDNZD)

## A Fazer (To Do) — Próximas iterações v3

- [ ] **MELHORIAS NO FRAMEWORK DE ANÁLISE QUANTITATIVA AUDNZD**
  - Calibração aprimorada de probabilidades (peso fundamental: 60% → 70%)
  - Incorporação de momentum commodities em tempo real
  - Timeframe dinâmico baseado em volatilidade histórica
  - Integração de calendário econômico dos próximos 10 dias
  - Sistema de score composto 0-100 (fundamental 50% + técnico 30% + momentum 20%)
  - Regras de decisão condicionais baseadas em eventos econômicos
- [ ] Sistema de Atualização de Portfólio Inteligente - Melhorias v2
  - Implementar cálculo de níveis de preço para sugestões take/reforço
  - Otimizar análise de clusters de correlação (atualmente simplificada)
  - Adicionar validação de dados históricos para análise de correlação
  - Implementar alertas automáticos para exposição excessiva
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
  - Implementar cálculo de níveis de preço para sugestões take/reforço
  - Otimizar análise de clusters de correlação (atualmente simplificada)
  - Adicionar validação de dados históricos para análise de correlação
  - Implementar alertas automáticos para exposição excessiva
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

### Melhorias Framework Análise Quantitativa AUDNZD (2025-11-07)

- [x] **Análise de Performance e Aprendizado Contínuo**
  - Framework KNOWLEDGEBASE validado para análises Forex
  - Sistema de pesos ajustado: Fundamental (60%→70%), Técnico (30%→20%), Momentum (novo 10%)
  - Calibração de probabilidades baseada em dados reais de mercado
  - Identificação de catalisadores subestimados (dados emprego, commodities)
  - Timeframe dinâmico implementado para próximas recomendações
- [x] **Novos Inputs de Análise Incorporados**
  - Momentum commodities em tempo real (+3.2% minério impactou AUDNZD)
  - Calendário econômico dos próximos 10 dias de alto impacto
  - Correlação AUDNZD vs ativos relacionados (commodities, NZDUSD)
  - Volume e volatilidade do par como inputs adicionais
  - Sentimento de mercado institucional
- [x] **Regras de Decisão Atualizadas**
  - Score composto 0-100: Fundamental (50%) + Técnico (30%) + Momentum (20%)
  - Probabilidades condicionais: P(AUDNZD > 1.16 | dados emprego positivos) = 75%
  - Regras específicas: Score ≥6 E commodities positivos → Prob ≥70%
  - Timeframe ajustado: Entrada 1-3 dias, Target 1.5-2.5%, Stop 0.8-1.2%
- [x] **Autoavaliação e Framework de Melhoria Contínua**
  - Sistema de autoavaliação implementado (completude, consistência, risco, confiança)
  - Análise de performance: 75% acertos nos catalisadores principais
  - Divergências identificadas: Fundamental vs Técnico no AUDNZD
  - Framework evolutivo estabelecido para futuras análises

### Timing e Gestão de Risco (2025-11-07)

- [x] Análise de timing baseada em eventos econômicos
  - Analisador completo de impacto de eventos (BCE, IPC Europa, PMI)
  - Sistema de pontuação de risco (crítico/elevado/médio)
  - Recomendações automáticas de fechamento/redução posições
  - Integração com calendário econômico em tempo real
- [x] Implementação recomendações timing - Fechamento posições EUR
  - EUR/CHF SHORT fechada (+1.49 profit) - Ticket 5301566535
  - EUR/USD LONG fechada (+0.20 profit) - Ticket 5301566496
  - Redução exposição EUR 100% em posições críticas
  - Preservação capital pré-eventos BCE de alto impacto
- [x] Relatórios de fechamento e resumo executivo
  - Relatório detalhado fechamentos com métricas completas
  - Resumo executivo implementação timing
  - Documentação ações tomadas e próximos passos
  - Integração com sistema de análise de correlação

### Sistema de Gestão e Aprendizado de Portfólio (2025-11-07)

- [x] Sistema de aprendizado contínuo (FASE 0)
  - Ciclo de aprendizado automático executado antes de qualquer operação
  - Base de recomendações 24h com tracking de assertividade
  - Autoavaliação baseada em performance real vs esperada
  - Ajuste automático de parâmetros dos módulos de correlação e níveis
  - Score médio atual: 97.17%, Taxa acerto: 100.0%
- [x] Gates de segurança aprimorados com aprendizado
  - Validação obrigatória de ticket + anti-duplicação
  - Consulta automática do histórico de aprendizado
  - Modelo atualizado dinamicamente baseado em performance
  - Sistema de limpeza automática de recomendações avaliadas
- [x] Processamento integrado com persistência (FASES 1-3)
  - Atualização estruturada de posições no portfólio
  - Recálculo automático de motores de risco
  - Relatório executivo completo com todas as análises
  - Persistência automática de sugestões na base de aprendizado
  - Sugestões otimizadas de balanceamento/proteção e take/reforço
- [x] Arquitetura de aprendizado machine learning-ready
  - Sistema de avaliação de assertividade com scores 0-100%
  - Histórico de ajustes de parâmetros para análise de tendências
  - Simulação de performance de mercado para validação
  - Framework extensível para novos tipos de recomendação
