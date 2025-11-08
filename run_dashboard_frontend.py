#!/usr/bin/env python3
# Origin: FEAT-001 - Script para rodar frontend dashboard
"""
Script para executar o frontend do dashboard.
Uso: python run_dashboard_frontend.py
"""

import subprocess
import sys
import os

def main():
    print("🚀 Iniciando frontend do Dashboard...")
    print("🌐 Interface disponível em: http://localhost:8501")
    print("🛑 Pressione Ctrl+C para parar")

    try:
        # Executar streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "frontend/dashboard.py"]
        subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    except KeyboardInterrupt:
        print("\n👋 Frontend parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())