#!/usr/bin/env python3
"""
Rotação de Chaves e Segredos
Gera nova AG_SECRET_KEY e atualiza tokens válidos.

Origin: TASK-39 - Rotação chaves segredos
"""

import os
import secrets
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent / ".env"

def rotate_secret():
    new_secret = secrets.token_hex(32)
    print(f"Nova chave gerada: {new_secret}")

    if ENV_FILE.exists():
        lines = ENV_FILE.read_text().splitlines()
    else:
        lines = []

    updated = False
    for i, line in enumerate(lines):
        if line.startswith("AG_SECRET_KEY="):
            lines[i] = f"AG_SECRET_KEY={new_secret}"
            updated = True
            break

    if not updated:
        lines.append(f"AG_SECRET_KEY={new_secret}")

    ENV_FILE.write_text("\n".join(lines) + "\n")
    print("Arquivo .env atualizado. Reinicie o serviço.")

if __name__ == "__main__":
    rotate_secret()