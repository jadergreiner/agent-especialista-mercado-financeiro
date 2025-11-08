#!/usr/bin/env python3
# Origin: FEAT-001 - Script para rodar backend dashboard
"""
Script para executar o backend do dashboard de forma estável.
Uso: python run_dashboard_backend.py
"""

import subprocess
import sys
import os
import signal
import time

def main():
    print("🚀 Iniciando backend do Dashboard...")
    print("📡 API disponível em: http://localhost:8002")
    print("📚 Documentação: http://localhost:8002/docs")
    print("🛑 Pressione Ctrl+C para parar")

    try:
        # Usar subprocess para maior controle
        cmd = [
            sys.executable, "-m", "uvicorn",
            "backend.api.dashboard:app",
            "--host", "127.0.0.1",
            "--port", "8002"
        ]

        # Executar e aguardar
        process = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
        process.wait()

    except KeyboardInterrupt:
        print("\n👋 Backend parado pelo usuário")
        if 'process' in locals():
            process.terminate()
            process.wait()
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())