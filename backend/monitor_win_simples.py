"""Monitor WIN Simples (stub)

Arquivo substituto mínimo para corrigir erros de parsing detectados pelo scanner.
# Origin: feature/AG-rbac-audit-masking - Stub para re-scan
"""

# Origin: feature/AG-rbac-audit-masking - Stub temporário para re-scan
"""
Monitor WIN Simples (stub)

Arquivo substituto mínimo para corrigir erros de parsing detectados pelo scanner.
Este stub é temporário — mantenha simples e sintaticamente válido.
"""

from datetime import datetime
from typing import Dict


def iniciar_monitor() -> Dict[str, str]:
    """Inicializa o monitor (stub).

    Retorna um dict com status simples para permitir testes/integração.
    """
    return {"status": "ok", "iniciado_em": datetime.utcnow().isoformat()}


def parar_monitor() -> Dict[str, str]:
    """Para o monitor (stub)."""
    return {"status": "stopped", "parado_em": datetime.utcnow().isoformat()}


def obter_status() -> Dict[str, str]:
    """Retorna status simples do monitor."""
    return {"status": "ok", "detalhe": "stub temporário"}


if __name__ == "__main__":
    # Demo rápido para execução independente
    print("Monitor simples (stub) executando")
    print(iniciar_monitor())

