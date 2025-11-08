# ISSUE-2: Remover/mitigar uso de subprocess.run(..., shell=True) (B602)

## Contexto

Bandit reportou uso de `subprocess.run(..., shell=True)` em `backend/instalar_integracao_corretoras.py` (linha ~18). Execução via shell com inputs dinâmicos pode permitir injeção de comandos.

## Local

- Arquivo: `backend/instalar_integracao_corretoras.py`
- Linha aproximada: 18

## Descrição do problema

Chamadas a `subprocess.run` com `shell=True` executam string no shell do sistema; se alguma parte da string for controlável por usuário/ambiente, há risco de injeção de comandos.

## Proposta de remediação

1. Usar lista de argumentos (e.g. `['comando', 'arg1']`) e `shell=False`.
2. Validar/escapar entradas provenientes de fontes externas.
3. Quando a chamada for necessária por wrapper de ferramenta, documentar o risco e isolar entrada.

## Tarefas

- [ ] Identificar todas as chamadas ao wrapper/instalador e avaliar origem dos inputs.
- [ ] Substituir chamadas por `subprocess.run([...], shell=False)` onde possível.
- [ ] Revisar com time de infra/ops se necessário.

## Responsável sugerido

- [ ] Engenheiro responsável pela integração de corretoras / DevOps

## Notas

- Esta issue deve ser tratada com prioridade alta se as chamadas processarem entradas externas.
