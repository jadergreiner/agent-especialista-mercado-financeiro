#!/usr/bin/env python3
# Origin: FEAT-001 - Script para rodar dashboard completo
"""
Script para executar o dashboard completo (backend + frontend).
Uso: python run_dashboard.py
"""

import subprocess
import sys
import os
import signal
import time
import threading

def run_backend():
    """Executa o backend FastAPI."""
    print("🚀 Iniciando backend...")
    import uvicorn
    uvicorn.run(
        "backend.api.dashboard:app",
        host="127.0.0.1",
        port=8002,
        log_level="info",
        reload=False
    )

def run_frontend():
    """Executa o frontend Streamlit."""
    print("🌐 Iniciando frontend...")
    time.sleep(3)  # Aguardar backend iniciar
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join(os.getcwd(), "frontend", "dashboard.py"),
        "--server.port", "8501",
        "--server.address", "127.0.0.1",
        "--server.headless", "true"
    ]
    return subprocess.Popen(cmd, cwd=os.getcwd())

def main():
    """Executa dashboard completo."""
    print("🎯 Iniciando Dashboard MVP...")
    print("📊 Backend API: http://localhost:8002")
    print("🌐 Frontend: http://localhost:8501")
    print("📚 API Docs: http://localhost:8002/docs")
    print("🛑 Pressione Ctrl+C para parar tudo")

    processes = []

    try:
        # Iniciar backend em thread separada
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()

        # Aguardar um pouco para backend iniciar
        time.sleep(5)

        # Iniciar frontend
        frontend_process = run_frontend()
        processes.append(frontend_process)

        # Aguardar frontend
        for process in processes:
            process.wait()

    except KeyboardInterrupt:
        print("\n👋 Parando dashboard...")
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            process.wait()
        print("✅ Dashboard parado com sucesso")

    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())