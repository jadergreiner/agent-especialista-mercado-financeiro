---
title: "ISSUE: Substituir uso dinâmico de exec por importlib"
labels: [security, severity-medium]
---

# Contexto

Localização: `backend/framework_assimetrico/__init__.py` (uso de `exec` para importar módulos dinamicamente, linhas ~154-156).

## Evidência

Trecho relevante:

```python
modulo_class = modulo.replace('modulo_', 'Modulo').replace('_', ' ').title().replace(' ', '')
exec(f"from .{modulo} import {modulo_class}")
exec(f"modulos_disponiveis['{modulo.replace('modulo_', '').replace('_', '_')}'] = {modulo_class}(self.config)")
```

## Risco

- Uso de `exec` pode permitir execução de código não intencional se variáveis de entrada forem controláveis.
- Dificulta análise estática e aumenta superfície de ataque.

## Remediação sugerida

1. Substituir `exec` por `importlib.import_module` + `getattr` para carregar a classe de forma segura:

```python
import importlib
mod = importlib.import_module(f".{modulo}", package=__package__)
cls = getattr(mod, modulo_class)
modulos_disponiveis[...] = cls(self.config)
```

2. Validar que `modulo` pertence a uma whitelist (os nomes permitidos) antes da importação.

## Critérios de aceitação

- Código removendo `exec` e usando importlib, com testes que cobrem o carregamento dinâmico.
- Revisão de segurança confirmando que nomes indiretos não podem causar import inesperado.

## Prioridade

Alta (confiança: HIGH) — substituir `exec` é relativamente simples e reduz risco.

## Sugestão de dono

backend/fundamentos (responsável designado)
