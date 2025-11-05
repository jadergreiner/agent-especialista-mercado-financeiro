"""
Agent Especialista Mercado Financeiro - Ponto de Entrada do Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Agent Especialista de Mercado Financeiro",
    description="Agente de IA para análise global de mercado financeiro",
    version="0.1.0"
)

# Configuração CORS para frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Porta padrão do Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def raiz():
    """Endpoint de verificação de saúde"""
    return {
        "status": "online",
        "servico": "Agent Especialista de Mercado Financeiro",
        "versao": "0.1.0"
    }

@app.get("/api/v1/saude")
async def verificacao_saude():
    """Verificação detalhada de saúde"""
    return {
        "status": "saudavel",
        "servicos": {
            "api": "operacional",
            "feeds_dados": "pendente",
            "motor_analise": "pendente"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
