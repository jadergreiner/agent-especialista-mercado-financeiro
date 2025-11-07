# -*- coding: utf-8 -*-
"""
Validador de contratos JSON (Schema Registry simples)

- Usa jsonschema se disponível; caso contrário, faz checagem mínima de campos obrigatórios
- Schemas ficam em backend/schemas/*.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple, List, Dict, Any


def _pasta_backend() -> Path:
    # Este arquivo está em backend/src/schemas/validador.py
    # parents[0]=schemas, [1]=src, [2]=backend
    return Path(__file__).resolve().parents[2]


def carregar_schema(contrato: str) -> Dict[str, Any]:
    """Carrega o schema JSON pelo nome do contrato (ex: 'report.intraday.v1')."""
    base = _pasta_backend() / 'schemas'
    caminho = base / f'{contrato}.json'
    if not caminho.exists():
        raise FileNotFoundError(f"Schema não encontrado: {caminho}")
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)


def validar_contra_schema(payload: Dict[str, Any], contrato: str) -> Tuple[bool, List[str]]:
    """Valida um payload contra o schema do contrato.

    Retorna (ok, erros)
    """
    erros: List[str] = []
    schema = carregar_schema(contrato)

    # Tenta validar com jsonschema se disponível
    try:
        import jsonschema  # type: ignore
        from jsonschema import Draft7Validator  # type: ignore
        v = Draft7Validator(schema)
        problems = sorted(v.iter_errors(payload), key=lambda e: e.path)
        for e in problems:
            caminho = "/".join([str(p) for p in e.path])
            erros.append(f"{caminho}: {e.message}")
        return (len(erros) == 0, erros)
    except Exception:
        # Fallback simples: checar campos obrigatórios de topo
        required = schema.get('required', [])
        for campo in required:
            if campo not in payload:
                erros.append(f"Campo obrigatório ausente: {campo}")
        # Checagem mínima de tipos principais
        tipos = schema.get('properties', {})
        for k, spec in tipos.items():
            if k in payload:
                esperado = spec.get('type')
                if isinstance(esperado, list):
                    # Aceita qualquer um
                    continue
                if esperado == 'object' and not isinstance(payload[k], dict):
                    erros.append(f"Campo '{k}' deveria ser objeto")
                if esperado == 'array' and not isinstance(payload[k], list):
                    erros.append(f"Campo '{k}' deveria ser lista")
        return (len(erros) == 0, erros)
