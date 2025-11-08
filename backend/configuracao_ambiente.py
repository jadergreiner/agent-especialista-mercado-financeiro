#!/usr/bin/env python3
"""
CONFIGURAÇÃO CENTRAL DO SISTEMA - AMBIENTE DE OPERAÇÃO
Define se o sistema roda em modo DEMO ou PRODUÇÃO

Este arquivo controla:
- Modo de operação (demo/producao)
- Corretoras ativas
- APIs e conexões
- Limites de risco
- Fontes de dados

IMPORTANTE: Nunca commite chaves reais no repositório!
"""

import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class AmbienteOperacao(Enum):
    """Ambientes de operação disponíveis"""
    DEMO = "demo"
    PRODUCAO = "producao"
    HOMOLOGACAO = "homologacao"

class TipoCorretora(Enum):
    """Tipos de corretora suportados"""
    ALPACA_PAPER = "alpaca_paper"
    ALPACA_LIVE = "alpaca_live"
    INTERACTIVE_BROKERS_PAPER = "ib_paper"
    INTERACTIVE_BROKERS_LIVE = "ib_live"
    SIMULADO = "simulado"

@dataclass
class ConfiguracaoSistema:
    """Configuração central do sistema"""
    ambiente: AmbienteOperacao
    corretora_ativa: TipoCorretora
    usar_dados_reais: bool
    executar_ordens_reais: bool
    limites_risco_ativos: bool

    # Configurações específicas por ambiente
    alpaca_api_key: str = ""
    alpaca_api_secret: str = ""
    alpaca_base_url: str = ""

    ib_host: str = "127.0.0.1"
    ib_port: int = 7497
    ib_client_id: int = 1

    # Limites de risco
    risco_maximo_diario: float = 0.02  # 2%
    drawdown_maximo: float = 0.10      # 10%
    concentracao_maxima: float = 0.20   # 20%

def carregar_configuracao_ambiente() -> ConfiguracaoSistema:
    """
    Carrega configuração baseada no ambiente definido
    Verifica variáveis de ambiente e arquivos de configuração
    """

    # Determinar ambiente (padrão: DEMO)
    ambiente_str = os.getenv('AMBIENTE', 'demo').lower()
    try:
        ambiente = AmbienteOperacao(ambiente_str)
    except ValueError:
        print(f"⚠️ Ambiente '{ambiente_str}' inválido. Usando DEMO.")
        ambiente = AmbienteOperacao.DEMO

    print(f"🔧 Ambiente de operação: {ambiente.value.upper()}")

    # Configurações baseadas no ambiente
    if ambiente == AmbienteOperacao.DEMO:
        config = ConfiguracaoSistema(
            ambiente=ambiente,
            corretora_ativa=TipoCorretora.SIMULADO,
            usar_dados_reais=False,  # Dados históricos, não tempo real
            executar_ordens_reais=False,  # Apenas simulação
            limites_risco_ativos=True,  # Mesmo em demo, manter limites
            risco_maximo_diario=0.05,  # 5% em demo (mais permissivo)
            drawdown_maximo=0.20,      # 20% em demo
            concentracao_maxima=0.30    # 30% em demo
        )

    elif ambiente == AmbienteOperacao.PRODUCAO:
        config = ConfiguracaoSistema(
            ambiente=ambiente,
            corretora_ativa=TipoCorretora.ALPACA_LIVE,  # ou IB_LIVE
            usar_dados_reais=True,   # Dados tempo real
            executar_ordens_reais=True,  # ORDENS REAIS!
            limites_risco_ativos=True,  # Sempre ativo em produção
            risco_maximo_diario=0.02,  # 2% em produção (conservador)
            drawdown_maximo=0.10,      # 10% em produção
            concentracao_maxima=0.20    # 20% em produção
        )

        # Carregar chaves de produção (NUNCA commitar!)
        config.alpaca_api_key = os.getenv('ALPACA_API_KEY', '')
        config.alpaca_api_secret = os.getenv('ALPACA_API_SECRET', '')
        config.alpaca_base_url = "https://api.alpaca.markets"  # Live trading

        # Verificar se chaves foram fornecidas
        if not config.alpaca_api_key or not config.alpaca_api_secret:
            raise ValueError("❌ ERRO: Chaves ALPACA não encontradas para PRODUÇÃO!")

    else:  # HOMOLOGACAO
        config = ConfiguracaoSistema(
            ambiente=ambiente,
            corretora_ativa=TipoCorretora.ALPACA_PAPER,
            usar_dados_reais=True,   # Dados reais para teste
            executar_ordens_reais=False,  # Paper trading
            limites_risco_ativos=True,
            risco_maximo_diario=0.03,  # 3% em homologação
            drawdown_maximo=0.15,      # 15% em homologação
            concentracao_maxima=0.25    # 25% em homologação
        )

        # Carregar chaves de paper trading
        config.alpaca_api_key = os.getenv('ALPACA_API_KEY', '')
        config.alpaca_api_secret = os.getenv('ALPACA_API_SECRET', '')
        config.alpaca_base_url = "https://paper-api.alpaca.markets"

    # Validações de segurança
    _validar_configuracao_segura(config)

    return config

def _validar_configuracao_segura(config: ConfiguracaoSistema) -> None:
    """Validações de segurança da configuração"""

    # Em produção, sempre exigir limites de risco
    if config.ambiente == AmbienteOperacao.PRODUCAO:
        if not config.limites_risco_ativos:
            raise ValueError("❌ ERRO: Limites de risco devem estar ATIVOS em PRODUÇÃO!")

        if config.risco_maximo_diario > 0.05:  # Máximo 5% em produção
            raise ValueError("❌ ERRO: Risco máximo diário muito alto para PRODUÇÃO!")

    # Avisos importantes
    if config.executar_ordens_reais and config.ambiente != AmbienteOperacao.PRODUCAO:
        print("⚠️ AVISO: Executando ordens reais fora do ambiente de PRODUÇÃO!")

    if config.usar_dados_reais and config.ambiente == AmbienteOperacao.DEMO:
        print("ℹ️ INFO: Usando dados reais em ambiente DEMO (OK para testes)")

def obter_configuracao_corretora(config_sistema: ConfiguracaoSistema) -> Dict[str, Any]:
    """
    Retorna configuração específica da corretora baseada no tipo ativo
    """

    corretora_config = {
        "tipo": config_sistema.corretora_ativa.value,
        "paper_trading": not config_sistema.executar_ordens_reais,
        "timeout": 30,
        "rate_limit": 200
    }

    if "alpaca" in config_sistema.corretora_ativa.value:
        corretora_config.update({
            "api_key": config_sistema.alpaca_api_key,
            "api_secret": config_sistema.alpaca_api_secret,
            "base_url": config_sistema.alpaca_base_url
        })

    elif "ib" in config_sistema.corretora_ativa.value:
        corretora_config.update({
            "host": config_sistema.ib_host,
            "port": config_sistema.ib_port,
            "client_id": config_sistema.ib_client_id
        })

    return corretora_config

def salvar_configuracao_producao():
    """
    Salva template de configuração para produção
    Este arquivo deve ser criado manualmente com chaves reais
    """

    template = """
# CONFIGURAÇÃO PARA PRODUÇÃO
# COPIE ESTE CONTEÚDO PARA UM ARQUIVO .env NA RAIZ DO PROJETO

# Ambiente
AMBIENTE=producao

# Alpaca Live Trading (NUNCA COMMITAR!)
ALPACA_API_KEY=SUA_CHAVE_REAL_AQUI
ALPACA_API_SECRET=SUA_CHAVE_SECRETA_REAL_AQUI

# Interactive Brokers (se usado)
IB_HOST=127.0.0.1
IB_PORT=7496
IB_CLIENT_ID=1

# Risco (sempre conservador em produção)
RISCO_MAXIMO_DIARIO=0.02
DRAWNDOWN_MAXIMO=0.10
CONCENTRACAO_MAXIMA=0.20

# Logs detalhados em produção
LOG_LEVEL=INFO
"""

    arquivo_template = Path(".env.production.template")
    with open(arquivo_template, 'w', encoding='utf-8') as f:
        f.write(template.strip())

    print(f"📄 Template salvo em: {arquivo_template}")
    print("⚠️ IMPORTANTE: Configure suas chaves reais e renomeie para .env")

# =============================================================================
# FUNÇÃO PRINCIPAL PARA USO NOS SCRIPTS
# =============================================================================

def configurar_ambiente_producao():
    """
    Função principal para configurar o sistema para produção
    Retorna configuração completa do sistema
    """
    config = carregar_configuracao_ambiente()

    print("\n🔧 CONFIGURAÇÃO DO SISTEMA:")
    print(f"   Ambiente: {config.ambiente.value.upper()}")
    print(f"   Corretora: {config.corretora_ativa.value}")
    print(f"   Dados Reais: {'✅' if config.usar_dados_reais else '❌'}")
    print(f"   Ordens Reais: {'✅' if config.executar_ordens_reais else '❌'}")
    print(f"   Limites Risco: {'✅' if config.limites_risco_ativos else '❌'}")

    if config.executar_ordens_reais:
        print("\n🚨 ALERTA: SISTEMA CONFIGURADO PARA EXECUTAR ORDENS REAIS!")
        print("   Verifique se todas as configurações estão corretas!")

    return config

if __name__ == "__main__":
    # Quando executado diretamente, salva template de produção
    salvar_configuracao_producao()
    print("\nPara usar em produção:")
    print("1. Configure suas chaves reais no arquivo .env")
    print("2. Execute: export AMBIENTE=producao")
    print("3. Rode seus scripts normalmente")