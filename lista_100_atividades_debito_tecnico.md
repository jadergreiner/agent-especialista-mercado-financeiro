# Lista de 100 Atividades de Débito Técnico Sequenciais

## DT-001: Refatoração Modularização Backend (8 atividades)
1. Criar estrutura de diretórios modular (modules/portfolio_intelligence, modules/market_data, modules/shared)
2. Mover arquivos relacionados a portfolio para modules/portfolio_intelligence/dashboard/
3. Mover arquivos relacionados a recomendações IA para modules/portfolio_intelligence/ai_recommendations/
4. Mover arquivos relacionados a alertas de risco para modules/portfolio_intelligence/risk_alerts/
5. Mover arquivos relacionados a compliance para modules/portfolio_intelligence/compliance/
6. Mover arquivos de dados de mercado para modules/market_data/forex/, crypto/, integrations/
7. Mover utilitários compartilhados para modules/shared/database/, cache/, monitoring/
8. Atualizar imports em todos os arquivos para refletir nova estrutura modular

## DT-002: Implementar Framework de Testes E2E (10 atividades)
9. Instalar e configurar Playwright para testes E2E
10. Criar estrutura de testes E2E em tests/e2e/
11. Configurar ambiente de teste com banco de dados isolado
12. Criar teste E2E para fluxo completo de visualização de posições
13. Criar teste E2E para fluxo de login e autenticação
14. Criar teste E2E para atualização de P&L em tempo real
15. Criar teste E2E para heatmap de correlação
16. Criar teste E2E para alertas de risco
17. Configurar CI/CD para executar testes E2E
18. Documentar guia de execução de testes E2E

## DT-003: PostgreSQL + Docker Local (8 atividades)
19. Criar docker-compose.yml com PostgreSQL e Redis
20. Configurar volumes persistentes para dados do PostgreSQL
21. Instalar e configurar Alembic para migrations
22. Criar migration inicial do schema do banco
23. Atualizar código para suportar PostgreSQL (manter SQLite para testes)
24. Configurar conexão com PostgreSQL em desenvolvimento
25. Migrar dados existentes do SQLite para PostgreSQL
26. Testar aplicação completa com PostgreSQL local

## DT-004: Padronização de Naming (6 atividades)
27. Definir convenção de naming baseada em DDD
28. Renomear arquivos monitor_* para *_service.py
29. Renomear arquivos analisador_* para *_analyzer.py
30. Renomear arquivos consultar_* para *_repository.py
31. Atualizar imports em todos os arquivos após renomeação
32. Criar guia de convenções de naming na documentação

## DT-005: Cobertura de Testes (TDD) (12 atividades)
33. Instalar pytest e coverage
34. Configurar pytest.ini com configurações de cobertura
35. Criar estrutura de testes unitários em tests/unit/
36. Escrever testes para módulos de portfolio (20% cobertura)
37. Escrever testes para módulos de risco (20% cobertura)
38. Escrever testes para módulos de mercado (20% cobertura)
39. Escrever testes para utilitários compartilhados (20% cobertura)
40. Configurar CI/CD para validar cobertura mínima de 80%
41. Executar análise de cobertura atual
42. Identificar arquivos com baixa cobertura
43. Refatorar código para melhorar testabilidade
44. Documentar guia de escrita de testes

## DT-006: Documentação API (OpenAPI/Swagger) (8 atividades)
45. Configurar FastAPI para gerar documentação OpenAPI automática
46. Adicionar docstrings completos aos endpoints existentes
47. Documentar parâmetros de entrada e tipos de retorno
48. Documentar códigos de erro e exceções
49. Configurar exemplos de requests/responses
50. Criar documentação adicional em docs/api/
51. Configurar Swagger UI acessível
52. Testar documentação gerada automaticamente

## DT-007: Auditoria de Código Legacy (10 atividades)
53. Criar script para listar todos os arquivos Python
54. Categorizar arquivos por domínio/funcionalidade
55. Identificar arquivos não utilizados (usando análise estática)
56. Criar lista de arquivos candidatos a remoção
57. Analisar dependências entre arquivos
58. Criar plano de depreciação para arquivos legacy
59. Refatorar arquivos identificados como úteis
60. Remover arquivos não utilizados
61. Atualizar imports após remoção
62. Documentar mudanças na auditoria

## DT-008: Observabilidade (Logs + Métricas) (8 atividades)
63. Instalar e configurar logging estruturado (JSON)
64. Implementar logs com contexto em todos os módulos
65. Configurar Prometheus para métricas
66. Adicionar métricas de performance em endpoints
67. Configurar Grafana para dashboards
68. Implementar tracing com OpenTelemetry
69. Criar alertas baseados em métricas
70. Documentar guia de observabilidade

## DT-009: Business Case Detalhado (6 atividades)
71. Criar documento BUSINESS_CASE.md
72. Calcular ROI por feature implementada
73. Projetar cenários financeiros otimistas/pessimistas
74. Estimar custos de desenvolvimento por sprint
75. Calcular payback period
76. Apresentar business case para stakeholders

## DT-010: Validação de Onboarding Técnico (6 atividades)
77. Criar documento ONBOARDING_VALIDATION.md
78. Definir checklist técnico para novos devs
79. Criar script de validação automática de setup local
80. Documentar processo de onboarding
81. Testar onboarding com dev externo
82. Atualizar documentação baseada em feedback

## DT-011: Análise de Riscos por Sprint (6 atividades)
83. Mapear riscos por sprint no roadmap
84. Identificar dependências externas críticas
85. Criar plano de mitigação para cada risco
86. Estimar impacto e probabilidade de riscos
87. Definir triggers para plano de contingência
88. Revisar análise de riscos mensalmente

## DT-012: Governança Automatizada e Checks CI (8 atividades)
89. Criar .github/COPILOT_INSTRUCTIONS.md com regras obrigatórias
90. Criar docs/governanca/decisoes/decisions.json
91. Implementar workflow GitHub Actions para validação de decisões
92. Criar template de PR com checklist de conformidade
93. Configurar falha de PR sem referência DECISAO-XXX
94. Testar workflow de governança
95. Documentar processo de exceções
96. Treinar equipe sobre novas regras

## DT-013: Treinamento e Processo de Exceção (4 atividades)
97. Criar sessão de treinamento para equipe
98. Documentar processo de exceção em docs/governanca/excecoes.md
99. Registrar participação em treinamentos
100. Avaliar eficácia do treinamento após 30 dias

## DT-014: Monitoramento e Adoção das Regras de Governança (4 atividades)
101. Criar scripts para coletar métricas de adoção
102. Implementar dashboard de métricas (Metabase/Grafana)
103. Configurar relatórios semanais automáticos
104. Revisar métricas semanalmente no ritual do Tech Lead

## AG-001: Agendar validação formal (1 atividade)
105. Agendar e conduzir sessão de validação com Presidente, Jurídico e Compliance

## AG-002: Criar PR/Issue Template de Aprovação Jurídica (2 atividades)
106. Criar template de PR/Issue para aprovação jurídica
107. Configurar workflow CI para validar template/ata

## AG-003: Implementar RBAC e Autenticação Forte (6 atividades)
108. Definir papéis do sistema (admin, cliente/investidor, auditor)
109. Implementar autenticação JWT com 2FA opcional
110. Criar middleware de autorização RBAC
111. Implementar endpoints de gerenciamento de usuários
112. Criar testes unitários para RBAC
113. Criar testes E2E para autenticação

## AG-004: Implementar Audit Trails e Logging Estruturado (4 atividades)
114. Implementar logging estruturado em JSON
115. Criar tabelas de audit no banco
116. Registrar operações críticas com contexto
117. Criar endpoint para consultar audit logs

## AG-005: Criar ambiente de Staging controlado (4 atividades)
118. Provisionar ambiente de staging
119. Implementar scripts de masking/anonymize para PII
120. Carregar dados reais mascarados em staging
121. Documentar processo de staging

## AG-006: Implementar Backup Automático (3 atividades)
122. Configurar backup automático do banco
123. Criar playbook de restauração
124. Testar restauração em ambiente de teste

## AG-007: Criar E2E Checklist e Testes (5 atividades)
125. Definir checklist de critérios de aceitação
126. Escrever testes E2E para fluxo completo
127. Configurar CI para testes E2E
128. Testar fluxo Presidente→Cadastro de Operações
129. Documentar resultados dos testes

## AG-008: Definir Critérios de Aceitação e Test Plan (4 atividades)
130. Documentar Test Plan detalhado
131. Mapear cenários E2E obrigatórios
132. Criar checklist de aprovação PO + Tech Lead
133. Validar playbook de rollback em staging

## Atividades Adicionais para Completar 100 (30 atividades restantes)
134. Atualizar README.md com nova estrutura modular
135. Criar guia de contribuição para desenvolvedores
136. Implementar linting automático (black, flake8)
137. Configurar pre-commit hooks
138. Criar script de setup de ambiente de desenvolvimento
139. Implementar health checks para serviços
140. Criar documentação de arquitetura
141. Implementar rate limiting em APIs
142. Criar sistema de notificações
143. Implementar cache Redis para dados de mercado
144. Criar dashboard de monitoramento de sistema
145. Implementar compressão de responses API
146. Criar sistema de feature flags
147. Implementar paginação em endpoints de listagem
148. Criar validação de entrada com Pydantic
149. Implementar retry logic para chamadas externas
150. Criar documentação de deployment
151. Implementar circuit breaker para serviços externos
152. Criar testes de carga básicos
153. Implementar versionamento de API
154. Criar documentação de troubleshooting
155. Implementar métricas de negócio
156. Criar alertas de negócio
157. Implementar backup de configurações
158. Criar script de limpeza de dados antigos
159. Implementar rotação de logs
160. Criar documentação de segurança
161. Implementar validação de dependências
162. Criar script de atualização de dependências
163. Implementar testes de integração com APIs externas</content>
<parameter name="filePath">c:\repo\projetos\agent-especialista-mercado-financeiro\lista_100_atividades_debito_tecnico.md