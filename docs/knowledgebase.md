# KNOWLEDGEBASE

> Padrão obrigatório para linguagem e dados do projeto

## Padrão de Linguagem e Dados

- Chats e dados devem estar SEMPRE em Português.
- Este padrão é obrigatório e se aplica a todas as interações e saídas do sistema.
- Escopo: prompts, respostas de chat, código, comentários, documentação, logs, mensagens de erro, relatórios e quaisquer datasets textuais gerados.

## Integração com Instruções do Projeto

- Este KNOWLEDGEBASE complementa e referencia o documento `.github/copilot-instructions.md`.
- Em caso de conflito, prevalece a "⚠️ REGRA FUNDAMENTAL" de que todo o conteúdo do projeto deve ser em Português.

## Boas Práticas de Redação

- Use terminologia financeira em Português, preservando tickers, siglas técnicas e termos consagrados (ex.: VIX, DXY, carry trade).
- Comentários e docstrings devem explicar o "porquê" em Português; nomes de variáveis, funções e classes também devem ser em Português.
- Ao citar conteúdo externo (papers, docs), adicione uma breve síntese em Português.

## Validação e Conformidade

- Commits que adicionem/alterem arquivos de documentação (.md) serão validados por um pre-commit hook para indícios mínimos de Português.
- Em caso de falha, ajuste o texto para Português antes de prosseguir com o commit.

## Exemplos do que é Aceito

- "Atualiza análise macro do VIX e DXY"
- "Adiciona cálculo de risco de cauda em posições de forex"

## Exemplos do que NÃO é Aceito

- Textos descritivos em outro idioma sem explicação em Português
- Mensagens de commit em outro idioma

---

Mantido por: Engenharia de Prompt / Especialista Macro
