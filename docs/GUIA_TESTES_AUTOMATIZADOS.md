# Guia Rápido de Testes Automatizados

## Objetivo
Padronizar a criação, execução e documentação de testes automatizados no projeto.

## Estrutura Recomendada

- Scripts de teste devem ser nomeados como `test_<nome_do_modulo>.py`.
- Devem ficar na raiz de `backend/` ou em uma pasta `backend/tests/`.
- Cada teste deve conter docstring explicativa.

## Como Executar Todos os Testes

```bash
# Executar todos os testes na raiz do backend
pytest backend/
```

## Como Executar um Teste Específico

```bash
pytest backend/test_nome_modulo.py
```

# Guia Rápido de Testes Automatizados

## Objetivo
Padronizar a criação, execução e documentação de testes automatizados no projeto.

## Estrutura Recomendada

## Como Executar Todos os Testes
```bash
# Executar todos os testes na raiz do backend
pytest backend/
```

## Como Executar um Teste Específico
```bash
pytest backend/test_nome_modulo.py
```

## Exemplo de Teste Simples
```python
import pytest
from backend.<modulo> import <funcao>

## Exemplo de Teste Simples

```python
import pytest
from backend.<modulo> import <funcao>

def test_funcao():
    resultado = <funcao>(<entrada>)
    assert resultado == <esperado>
```

## Boas Práticas

- Use dados determinísticos e mocks para evitar dependência de APIs externas.
- Separe claramente testes unitários de integração.
- Documente o objetivo de cada teste.
- Utilize o template de documentação para scripts de teste.

## Dependências

- pytest


## Autor e Histórico

- Autor: <nome>
- Data de criação: <data>
- Última atualização: <data>

---

> Mantenha este guia atualizado conforme novas práticas e ferramentas forem adotadas.
```

## Boas Práticas

## Dependências

## Autor e Histórico

> Mantenha este guia atualizado conforme novas práticas e ferramentas forem adotadas.

# Guia Rápido de Testes Automatizados

## Objetivo

Padronizar a criação, execução e documentação de testes automatizados no projeto.

## Estrutura Recomendada

- Scripts de teste devem ser nomeados como `test_<nome_do_modulo>.py`.
- Devem ficar na raiz de `backend/` ou em uma pasta `backend/tests/`.
- Cada teste deve conter docstring explicativa.

## Como Executar Todos os Testes

```bash
# Executar todos os testes na raiz do backend
pytest backend/
```

## Como Executar um Teste Específico

```bash
pytest backend/test_nome_modulo.py
```

## Exemplo de Teste Simples

```python
import pytest
from backend.<modulo> import <funcao>

def test_funcao():
    resultado = <funcao>(<entrada>)
    assert resultado == <esperado>
```

## Boas Práticas

- Use dados determinísticos e mocks para evitar dependência de APIs externas.
- Separe claramente testes unitários de integração.
- Documente o objetivo de cada teste.
- Utilize o template de documentação para scripts de teste.

## Dependências

- pytest

## Autor e Histórico

- Autor: <nome>
- Data de criação: <data>
- Última atualização: <data>

---

> Mantenha este guia atualizado conforme novas práticas e ferramentas forem adotadas.
