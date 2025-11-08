# Origin: AG-SEC-002 - utilitário de terminal para evitar uso inseguro de shell/os.system
"""Utilities para operações de terminal.

Fornece uma função segura para limpar a tela sem usar `os.system` ou invocar o shell.
"""
import sys
import os


def limpar_tela():
    """Limpa a tela do terminal de forma cross-platform sem chamar o shell.

    Estratégia:
    - Tenta usar sequências ANSI para limpeza (funciona em terminais modernos, inclusive Windows 10+ com ANSI habilitado).
    - Se não suportado, faz fallback para imprimir várias novas linhas.
    """
    try:
        # Sequência ANSI para limpar a tela e posicionar o cursor no topo
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()
    except Exception:
        # Fallback simples
        print('\n' * 100)
