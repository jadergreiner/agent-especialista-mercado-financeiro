"""Endpoints e utilitários para feature flags (simples, evita dependências externas)."""
from fastapi import APIRouter, HTTPException, Depends
import json
import os
from backend.api.security import require_role, Role

router = APIRouter()
FLAGS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'feature_flags.json')


def _read_flags():
    with open(FLAGS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _write_flags(d):
    with open(FLAGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2)


@router.get('/api/v1/flags')
def get_flags():
    return _read_flags()


@router.post('/api/v1/flags/set')
def set_flag(key: str, value: bool, _=Depends(require_role(Role.admin))):
    flags = _read_flags()
    if key not in flags:
        raise HTTPException(status_code=404, detail='Flag não encontrada')
    flags[key] = bool(value)
    _write_flags(flags)
    return {'status': 'ok', 'flags': flags}
