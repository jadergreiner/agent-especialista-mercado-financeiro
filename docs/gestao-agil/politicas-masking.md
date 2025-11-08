# Políticas de Masking de Dados Pessoais Identificáveis (PII)

## Visão Geral
Este documento descreve as políticas de masking implementadas no sistema para proteger dados pessoais identificáveis (PII) durante desenvolvimento, testes e staging. O masking é aplicado automaticamente em cópias de bancos de dados para garantir conformidade com regulamentações de privacidade (LGPD, GDPR).

## Campos Sujetos a Masking
Os seguintes campos são identificados como PII e são mascarados:

- **email**: Substituído por formato `userXXX@domain.com` onde XXX é um hash simples.
- **nome**: Substituído por `Nome Mascardo`.
- **cpf**: Substituído por `XXX.XXX.XXX-XX` (formato preservado, valores aleatórios).
- **telefone**: Substituído por `(XX) XXXXX-XXXX` (formato preservado, valores aleatórios).

## Justificativas de Negócio e Compliance
- **Privacidade**: Evita exposição acidental de dados reais em ambientes não-produtivos.
- **Conformidade**: Atende requisitos de LGPD (Lei Geral de Proteção de Dados) para tratamento de dados pessoais.
- **Segurança**: Reduz risco de vazamentos durante desenvolvimento e testes.

## Implementação Técnica
- **Ferramenta**: Script `scripts/mask_sqlite.py`.
- **Execução**: Aplicado em cópias de DB, não no original.
- **Reversibilidade**: Masking é irreversível por design para segurança.

## Exemplos
### Antes do Masking
```json
{
  "email": "presidente@empresa.com",
  "nome": "João Silva",
  "cpf": "123.456.789-00",
  "telefone": "(11) 99999-9999"
}
```

### Após Masking
```json
{
  "email": "userABC@empresa.com",
  "nome": "Nome Mascardo",
  "cpf": "987.654.321-99",
  "telefone": "(21) 88888-8888"
}
```

## Responsabilidades
- **Desenvolvedores**: Garantir que novos campos PII sejam adicionados à lista de masking.
- **Compliance**: Revisar periodicamente a lista de campos e políticas.

Origin: TASK-15 - Documentar políticas de masking