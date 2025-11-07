# 🧩 Organização de Trabalho e Ágil

## Hierarquia Ágil

| Nivel Hierarquico | Foco Principal | Padrao Aplicado | Exemplo de Foco |
| :---: | :--- | :--- | :--- |
| **1. Epico** | Objetivo Estrategico | Alto Nivel | Direcao de meses/trimestres |
| **2. Feature** | Funcionalidade Completa | Tatico | Quebra o Epico em partes tangiveis |
| **3. Historia** | Valor para o Usuario | SPIN Selling | Implicacao do Problema e Necessidade |
| **4. Tarefa** | Passos Tecnicos | Modelo SMART | Clareza e Executabilidade Tecnica |

## Atualizações por História Entregue

Sempre que uma História de Usuário for concluída, atualizar:

- `docs/diario-projeto.md` — Progresso diário e marcos
- `docs/CHANGELOG.md`
- `docs/ROADMAP.md` — Visão de curto/médio/longo prazo
- `docs/gestao-agil/backlog.md` — Tarefas priorizadas e status
- `README.md` — Guia/ponte para decisões de arquitetura e links principais (mantendo lint de Markdown)

## 📝 Comportamento Padrão: Gestão de Atividades Pendentes

### Regra Fundamental

**TODAS as atividades pendentes devem ser registradas no backlog.**

### Fluxo de Trabalho

1. **Identificação de Pendência**
   - Durante desenvolvimento, análise ou discussão
   - Limitações descobertas em entregas
   - Melhorias sugeridas (v2, v3, etc.)
   - Bugs ou débitos técnicos
   - Novas funcionalidades propostas

2. **Registro Imediato**
   - Adicionar item no backlog (`docs/gestao-agil/backlog.md`)
   - Seção: "A Fazer (To Do)"
   - Incluir: descrição clara, contexto, critérios de aceitação
   - **NÃO priorizar imediatamente**

3. **Priorização pelo PO**
   - Apenas o Product Owner (PO) define prioridades
   - PO avalia no momento estratégico adequado
   - Considera: valor de negócio, urgência, dependências, ROI

4. **Responsabilidades**
   - **Time de Desenvolvimento**: Registrar todas as pendências no backlog
   - **Product Owner**: Priorizar e decidir o "quando" executar
   - **Scrum Master/Facilitador**: Garantir que nada fique sem registro

### Benefícios

- ✅ Nenhuma pendência é perdida ou esquecida
- ✅ Backlog centralizado e organizado
- ✅ PO tem visão completa para decisões estratégicas
- ✅ Time foca em execução, não em priorização prematura
- ✅ Reduz work-in-progress desnecessário (WIP limit natural)

## 📋 Princípios de Decisão para Backlog

Ao avaliar e priorizar itens do backlog:

### Conceitos Aplicados

- **YAGNI** — Não implementar funcionalidades desnecessárias; focar no essencial
- **KISS** — Manter soluções simples; evitar complexidade
- **Incremental Delivery** — Entregar valor em incrementos pequenos para feedback rápido
- **Data-Driven Design** — Decisões baseadas em dados, não suposições

---

## ⚡ Política de Otimização de Tokens e Rate Limits

### Sempre Aplicar

#### Limites de Consulta Padrão

- Listar issues/PRs: máximo 20 itens (usar paginação se o usuário solicitar mais)
- Buscar arquivos: priorizar top 5 mais relevantes
- Mostrar código: limite inicial de 100 linhas (oferecer expandir se necessário)
- Listar commits: máximo 15 commits mais recentes
- Discussões/comentários: máximo 10 itens

#### Hierarquia de Busca (Eficiência)

1. Primeiro: contexto da conversa atual
2. Segundo: busca lexical (exata, menor custo)
3. Terceiro: busca semântica (contextual, maior custo)
4. Último recurso: análise profunda com múltiplas chamadas

#### Consolidação de Requisições

- Agrupar múltiplas queries relacionadas em uma única chamada
- Usar filtros nativos das APIs (labels, state, author, date range)
- Preferir endpoints agregados vs. múltiplas chamadas individuais
- Exemplo: `state:open label:bug author:jadergreiner` vs 3 chamadas separadas

#### Reutilização de Contexto (Cache)

- Verificar se a informação já foi obtida na conversa atual
- Referenciar dados anteriores: "Conforme arquivo mencionado anteriormente..."
- Armazenar metadados do repositório consultados (estrutura, branches, arquivos principais)
- Não refazer buscas idênticas em intervalo menor que 5 minutos

### Nunca Fazer

- Buscar arquivos inteiros sem necessidade específica
- Listar TODOS os issues/PRs sem filtro de status, label ou data
- Fazer busca lexical e semântica para a mesma query
- Chamar integrações se os dados já estiverem no contexto atual
- Expandir contexto com informações não solicitadas
- Buscar histórico completo de commits (sem limite de data)

### Perguntar ao Usuário Antes de

- Operações que requeiram mais de 3 chamadas de API
- Buscas em repositórios com mais de 1000 arquivos sem escopo definido
- Análises que podem ser feitas localmente (grep, find, git log)
- Listar mais de 50 itens de qualquer tipo
- Buscas sem filtro temporal em repositórios com mais de 2 anos

### Estratégia de Busca por Tipo

Para Código (Funções, Classes, Implementações)

```text
1. Usuário: "Onde está a função authenticateUser?"
2. Ação: busca lexical com symbol:authenticateUser
3. Se não encontrar: busca semântica "função de autenticação de usuário"
```

Para Conceitos (Como funciona X, Explicar Y)

```text
1. Usuário: "Como funciona a autenticação?"
2. Ação: busca semântica "como funciona a autenticação"
3. Limitar aos 5 resultados mais relevantes
```

Para Arquivos Específicos

```text
1. Usuário: "Mostre o arquivo auth.py"
2. Ação: leitura direta com path exato
3. Se path desconhecido: busca lexical path:auth.py
```
