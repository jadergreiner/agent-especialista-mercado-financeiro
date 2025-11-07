#!/usr/bin/env python3
"""
Script de Instalação - Integração com Corretoras
Instala todas as dependências necessárias para o sistema
Autor: Agent Especialista Mercado Financeiro
Data: 2025-01-06
"""

import subprocess
import sys
import os
from pathlib import Path

def executar_comando(comando, descricao):
    """Executa um comando e trata erros"""
    print(f"📦 {descricao}...")
    try:
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {descricao} - Concluído")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {descricao} - Erro: {e}")
        print(f"   Comando: {comando}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def criar_diretorios():
    """Cria diretórios necessários"""
    diretorios = [
        "config",
        "data", 
        "logs",
        "reports",
        "reports/trading"
    ]
    
    for diretorio in diretorios:
        path = Path(diretorio)
        path.mkdir(exist_ok=True)
        print(f"📁 Diretório criado: {diretorio}")

def instalar_dependencias():
    """Instala dependências Python necessárias"""
    print("🚀 Instalando Dependências para Integração com Corretoras")
    print("=" * 60)
    
    # Dependências principais
    dependencias_principais = [
        "yfinance>=0.2.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "requests>=2.28.0",
        "python-dateutil>=2.8.0"
    ]
    
    # Dependências para corretoras
    dependencias_corretoras = [
        "alpaca-trade-api>=3.0.0",  # Alpaca Markets
        "ib-insync>=0.9.0",         # Interactive Brokers
    ]
    
    # Dependências para análise técnica
    dependencias_analise = [
        "TA-Lib>=0.4.0",           # Indicadores técnicos
        "pandas-ta>=0.3.0",        # Pandas technical analysis
        "scikit-learn>=1.1.0",     # Machine learning
    ]
    
    # Dependências para web app
    dependencias_web = [
        "Flask>=2.2.0",
        "plotly>=5.0.0",
        "dash>=2.0.0"
    ]
    
    # Instalar por grupos
    grupos = [
        (dependencias_principais, "Dependências Principais"),
        (dependencias_corretoras, "APIs de Corretoras"),
        (dependencias_analise, "Análise Técnica"),
        (dependencias_web, "Interface Web")
    ]
    
    for dependencias, nome_grupo in grupos:
        print(f"\n📦 Instalando {nome_grupo}...")
        for dep in dependencias:
            comando = f"pip install {dep}"
            sucesso = executar_comando(comando, f"Instalando {dep}")
            if not sucesso:
                print(f"⚠️  Falha ao instalar {dep} - continuando...")

def configurar_talib():
    """Configuração especial para TA-Lib"""
    print("\n🔧 Configurando TA-Lib...")
    
    # Verificar se TA-Lib está disponível
    try:
        import talib
        print("✅ TA-Lib já está instalado e funcionando")
        return True
    except ImportError:
        print("⚠️  TA-Lib não encontrado")
        
    # Tentar instalar TA-Lib
    if os.name == 'nt':  # Windows
        print("💡 No Windows, TA-Lib requer instalação manual:")
        print("   1. Baixe o wheel apropriado de: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib")
        print("   2. Execute: pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl")
        print("   3. Ou use conda: conda install -c conda-forge ta-lib")
    else:  # Linux/Mac
        executar_comando("pip install TA-Lib", "Instalando TA-Lib")
        
    return False

def criar_arquivos_configuracao():
    """Cria arquivos de configuração de exemplo"""
    print("\n📝 Criando arquivos de configuração...")
    
    # Configuração de corretoras
    config_corretoras = {
        "alpaca_paper": {
            "tipo": "alpaca",
            "api_key": "SEU_ALPACA_API_KEY_AQUI",
            "api_secret": "SEU_ALPACA_SECRET_KEY_AQUI",
            "base_url": "https://paper-api.alpaca.markets",
            "paper_trading": True,
            "timeout": 30,
            "rate_limit": 200
        },
        "simulado": {
            "tipo": "simulado", 
            "api_key": "simulado",
            "api_secret": "simulado",
            "paper_trading": True,
            "timeout": 1,
            "rate_limit": 1000
        }
    }
    
    # Configuração de estratégias
    config_estrategias = {
        "media_movel_tech": {
            "tipo": "media_movel",
            "simbolos": ["AAPL", "MSFT", "GOOGL"],
            "ativo": True,
            "capital_alocado": 25000,
            "risco_por_operacao": 0.02,
            "stop_loss": 0.05,
            "take_profit": 0.10,
            "timeframe": "1h",
            "parametros": {
                "periodo_rapida": 10,
                "periodo_lenta": 30
            }
        },
        "rsi_oversold": {
            "tipo": "rsi_oversold",
            "simbolos": ["SPY", "QQQ", "IWM"],
            "ativo": True,
            "capital_alocado": 20000,
            "risco_por_operacao": 0.015,
            "stop_loss": 0.04,
            "take_profit": 0.08,
            "timeframe": "1d",
            "parametros": {
                "periodo_rsi": 14,
                "nivel_sobrevendido": 30,
                "nivel_sobrecomprado": 70
            }
        }
    }
    
    # Configuração do sistema
    config_sistema = {
        "sistema": {
            "nome": "Agent Especialista - Sistema Integrado de Trading",
            "versao": "1.0.0",
            "modo_debug": False,
            "intervalo_principal": 30
        },
        "componentes": {
            "corretoras": {
                "ativo": True,
                "reconectar_automaticamente": True,
                "timeout_conexao": 30
            },
            "trading_automatizado": {
                "ativo": True,
                "intervalo_analise": 60,
                "execucao_automatica": True
            },
            "monitor_portfolio": {
                "ativo": True,
                "intervalo_atualizacao": 30,
                "alertas_habilitados": True
            },
            "webapp": {
                "ativo": True,
                "host": "localhost", 
                "porta": 5001,
                "debug": False
            }
        }
    }
    
    # Salvar arquivos
    import json
    
    arquivos_config = [
        ("config/corretoras.json", config_corretoras),
        ("config/estrategias.json", config_estrategias),
        ("config/sistema_trading.json", config_sistema)
    ]
    
    for arquivo, config in arquivos_config:
        if not os.path.exists(arquivo):
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Criado: {arquivo}")
        else:
            print(f"⚠️  Já existe: {arquivo}")

def verificar_instalacao():
    """Verifica se a instalação foi bem-sucedida"""
    print("\n🔍 Verificando Instalação...")
    
    modulos_principais = [
        "yfinance",
        "pandas", 
        "numpy",
        "requests"
    ]
    
    modulos_opcionais = [
        "alpaca_trade_api",
        "ib_insync",
        "talib",
        "flask",
        "plotly"
    ]
    
    print("\n📦 Módulos Principais:")
    todos_principais_ok = True
    for modulo in modulos_principais:
        try:
            __import__(modulo)
            print(f"✅ {modulo}")
        except ImportError:
            print(f"❌ {modulo} - NECESSÁRIO")
            todos_principais_ok = False
            
    print("\n📦 Módulos Opcionais:")
    for modulo in modulos_opcionais:
        try:
            __import__(modulo)
            print(f"✅ {modulo}")
        except ImportError:
            print(f"⚠️  {modulo} - opcional")
            
    return todos_principais_ok

def main():
    """Função principal de instalação"""
    print("🏦 AGENT ESPECIALISTA - INTEGRAÇÃO COM CORRETORAS")
    print("🔧 Script de Instalação e Configuração")
    print("=" * 80)
    
    try:
        # 1. Criar diretórios
        print("\n1️⃣  Criando estrutura de diretórios...")
        criar_diretorios()
        
        # 2. Instalar dependências
        print("\n2️⃣  Instalando dependências Python...")
        instalar_dependencias()
        
        # 3. Configurar TA-Lib
        print("\n3️⃣  Configurando TA-Lib...")
        configurar_talib()
        
        # 4. Criar arquivos de configuração
        print("\n4️⃣  Criando arquivos de configuração...")
        criar_arquivos_configuracao()
        
        # 5. Verificar instalação
        print("\n5️⃣  Verificando instalação...")
        instalacao_ok = verificar_instalacao()
        
        # 6. Instruções finais
        print("\n🎉 INSTALAÇÃO CONCLUÍDA!")
        print("=" * 80)
        
        if instalacao_ok:
            print("✅ Todos os módulos principais foram instalados com sucesso!")
        else:
            print("⚠️  Alguns módulos principais falharam - verifique os erros acima")
            
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. Configure suas credenciais de API em config/corretoras.json")
        print("2. Ajuste as estratégias em config/estrategias.json") 
        print("3. Execute o sistema:")
        print("   python backend/sistema_integrado_trading.py --demo  (demonstração)")
        print("   python backend/sistema_integrado_trading.py        (sistema completo)")
        
        print("\n💡 DOCUMENTAÇÃO:")
        print("- Alpaca API: https://alpaca.markets/docs/")
        print("- Interactive Brokers: https://github.com/erdewit/ib_insync")
        print("- TA-Lib: https://ta-lib.github.io/ta-lib-python/")
        
    except Exception as e:
        print(f"❌ Erro durante a instalação: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    main()