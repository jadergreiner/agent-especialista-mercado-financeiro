#!/usr/bin/env python3
# Origin: FEAT-001 - Servidor backend simples
"""
Servidor backend simples para dashboard.
Uso: python run_backend_simple.py
"""

import uvicorn
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🚀 Iniciando backend do Dashboard...")
    print("📡 API disponível em: http://localhost:8002")
    print("📚 Documentação: http://localhost:8002/docs")
    print("🛑 Pressione Ctrl+C para parar")

    try:
        uvicorn.run(
            "backend.api.dashboard:app",
            host="127.0.0.1",
            port=8002,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n👋 Backend parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)