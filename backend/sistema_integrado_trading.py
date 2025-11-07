#!/usr/bin/env python3
"""
Sistema Integrado de Trading com Corretoras
Aplicação principal que integra todos os componentes
Autor: Agent Especialista Mercado Financeiro
Data: 2025-01-06
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
import os

# Importar todos os componentes desenvolvidos
from integracao_corretoras import GerenciadorCorretoras, TipoCorretora
from trading_automatizado import GerenciadorTradingAutomatizado
from monitor_portfolio import MonitorPortfolio, WebAppPortfolio

# =============================================================================
# CLASSE PRINCIPAL DO SISTEMA
# =============================================================================

class SistemaIntegradoTrading:
    """Sistema integrado de trading com corretoras"""
    
    def __init__(self):
        self.logger = self._configurar_logging()
        self.ativo = False
        self.tasks = []
        
        # Componentes principais
        self.gerenciador_corretoras = GerenciadorCorretoras()
        self.trading_automatizado = None
        self.monitor_portfolio = None
        self.webapp = None
        
        # Configuração
        self.config = self._carregar_configuracao()
        
    def _configurar_logging(self) -> logging.Logger:
        """Configura logging do sistema"""
        # Configurar logging com arquivo
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"sistema_trading_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger('sistema_trading')
        return logger
        
    def _carregar_configuracao(self) -> dict:
        """Carrega configuração do sistema"""
        config_path = "config/sistema_trading.json"
        
        if not os.path.exists(config_path):
            self._criar_config_sistema(config_path)
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar configuração: {e}")
            return self._config_padrao()
            
    def _criar_config_sistema(self, caminho: str):
        """Cria arquivo de configuração do sistema"""
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        
        config = self._config_padrao()
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"📝 Configuração criada: {caminho}")
        
    def _config_padrao(self) -> dict:
        """Retorna configuração padrão do sistema"""
        return {
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
            },
            "limites_risco": {
                "perda_maxima_diaria": 0.05,
                "drawdown_maximo": 0.15,
                "concentracao_maxima": 0.20,
                "volatilidade_maxima": 0.25
            },
            "notificacoes": {
                "email_habilitado": False,
                "webhook_habilitado": False,
                "console_habilitado": True
            }
        }
        
    async def inicializar_componentes(self):
        """Inicializa todos os componentes do sistema"""
        self.logger.info("🚀 Inicializando Sistema Integrado de Trading")
        print("=" * 80)
        print("🏦 AGENT ESPECIALISTA - SISTEMA INTEGRADO DE TRADING")
        print("=" * 80)
        
        try:
            # 1. Inicializar Gerenciador de Corretoras
            print("\n1️⃣  Inicializando Integração com Corretoras...")
            await self.gerenciador_corretoras.inicializar_conectores()
            
            status_corretoras = self.gerenciador_corretoras.obter_status_sistema()
            print(f"✅ Corretoras conectadas: {status_corretoras['total_conectores']}")
            
            if status_corretoras['conector_ativo']:
                print(f"🎯 Conector ativo: {status_corretoras['conector_ativo']}")
            else:
                self.logger.warning("⚠️  Nenhum conector ativo - sistema funcionará em modo limitado")
                
            # 2. Inicializar Trading Automatizado
            if self.config['componentes']['trading_automatizado']['ativo']:
                print("\n2️⃣  Inicializando Trading Automatizado...")
                self.trading_automatizado = GerenciadorTradingAutomatizado(self.gerenciador_corretoras)
                self.trading_automatizado.carregar_estrategias()
                
                status_trading = self.trading_automatizado.obter_status_sistema()
                print(f"✅ Estratégias carregadas: {status_trading['total_estrategias']}")
                print(f"🎯 Estratégias ativas: {status_trading['estrategias_ativas']}")
                
            # 3. Inicializar Monitor de Portfólio
            if self.config['componentes']['monitor_portfolio']['ativo']:
                print("\n3️⃣  Inicializando Monitor de Portfólio...")
                self.monitor_portfolio = MonitorPortfolio(self.gerenciador_corretoras)
                
                # Registrar callback de alertas
                self.monitor_portfolio.registrar_callback_alerta(self._processar_alerta)
                
                status_monitor = self.monitor_portfolio.obter_status_sistema()
                print(f"✅ Monitor de portfólio: {status_monitor['ativo']}")
                
            # 4. Inicializar WebApp (opcional)
            if self.config['componentes']['webapp']['ativo'] and self.monitor_portfolio:
                print("\n4️⃣  Inicializando Interface Web...")
                self.webapp = WebAppPortfolio(self.monitor_portfolio)
                print(f"✅ WebApp configurada: http://localhost:{self.config['componentes']['webapp']['porta']}")
                
            print("\n🎉 Todos os componentes inicializados com sucesso!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            raise
            
    def _processar_alerta(self, alerta):
        """Processa alertas do sistema"""
        emoji_severidade = {
            'baixa': '💙',
            'media': '🟡', 
            'alta': '🟠',
            'critica': '🔴'
        }
        
        emoji = emoji_severidade.get(alerta.severidade, '⚪')
        
        print(f"\n{emoji} ALERTA {alerta.severidade.upper()}")
        print(f"📊 {alerta.titulo}")
        print(f"💰 {alerta.simbolo}: {alerta.descricao}")
        print(f"💡 Ação sugerida: {alerta.acao_sugerida}")
        print("-" * 50)
        
    async def executar_ciclo_principal(self):
        """Executa ciclo principal do sistema"""
        try:
            # Verificar status das conexões
            await self._verificar_conexoes()
            
            # Executar análise de trading (se ativo)
            if self.trading_automatizado and self.config['componentes']['trading_automatizado']['ativo']:
                await self.trading_automatizado.executar_ciclo_analise()
                
            # Executar monitoramento de portfólio (se ativo)
            if self.monitor_portfolio and self.config['componentes']['monitor_portfolio']['ativo']:
                await self.monitor_portfolio.executar_ciclo_monitoramento()
                
            # Log do status
            await self._log_status_sistema()
            
        except Exception as e:
            self.logger.error(f"❌ Erro no ciclo principal: {e}")
            
    async def _verificar_conexoes(self):
        """Verifica status das conexões"""
        for nome, conector in self.gerenciador_corretoras.conectores.items():
            try:
                conectado = await conector.verificar_conexao()
                if not conectado and self.config['componentes']['corretoras']['reconectar_automaticamente']:
                    self.logger.info(f"🔄 Tentando reconectar {nome}...")
                    await conector.conectar()
            except Exception as e:
                self.logger.error(f"❌ Erro ao verificar conexão {nome}: {e}")
                
    async def _log_status_sistema(self):
        """Log do status do sistema"""
        try:
            # Status das corretoras
            status_corretoras = self.gerenciador_corretoras.obter_status_sistema()
            
            # Status do trading automatizado
            status_trading = {}
            if self.trading_automatizado:
                status_trading = self.trading_automatizado.obter_status_sistema()
                
            # Status do monitor
            status_monitor = {}
            if self.monitor_portfolio:
                status_monitor = self.monitor_portfolio.obter_status_sistema()
                
            self.logger.info(
                f"📊 Sistema: Corretoras:{status_corretoras['total_conectores']} | "
                f"Estratégias:{status_trading.get('estrategias_ativas', 0)} | "
                f"Portfolio:${status_monitor.get('valor_portfolio', 0):,.0f} | "
                f"Alertas:{status_monitor.get('total_alertas_ativos', 0)}"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao fazer log do status: {e}")
            
    async def iniciar_sistema(self):
        """Inicia o sistema completo"""
        try:
            await self.inicializar_componentes()
            
            self.ativo = True
            
            # Criar tasks para componentes assíncronos
            if self.trading_automatizado and self.config['componentes']['trading_automatizado']['ativo']:
                task_trading = asyncio.create_task(self.trading_automatizado.iniciar())
                self.tasks.append(task_trading)
                
            if self.monitor_portfolio and self.config['componentes']['monitor_portfolio']['ativo']:
                task_monitor = asyncio.create_task(self.monitor_portfolio.iniciar())
                self.tasks.append(task_monitor)
                
            # Task principal
            print(f"\n🚀 Sistema iniciado - Intervalo principal: {self.config['sistema']['intervalo_principal']}s")
            print("💡 Pressione Ctrl+C para parar o sistema")
            print("=" * 80)
            
            # Loop principal
            while self.ativo:
                await asyncio.sleep(self.config['sistema']['intervalo_principal'])
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupção detectada - Parando sistema...")
            await self.parar_sistema()
        except Exception as e:
            self.logger.error(f"❌ Erro crítico no sistema: {e}")
            await self.parar_sistema()
            raise
            
    async def parar_sistema(self):
        """Para o sistema de forma segura"""
        self.logger.info("🛑 Parando Sistema Integrado de Trading")
        
        self.ativo = False
        
        # Parar componentes
        if self.trading_automatizado:
            self.trading_automatizado.parar()
            
        if self.monitor_portfolio:
            self.monitor_portfolio.parar()
            
        # Cancelar tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
                
        # Aguardar conclusão das tasks
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
        # Desconectar corretoras
        for conector in self.gerenciador_corretoras.conectores.values():
            await conector.desconectar()
            
        self.logger.info("✅ Sistema parado com sucesso")
        print("✅ Sistema parado com sucesso")

# =============================================================================
# FUNÇÃO DE DEMONSTRAÇÃO COMPLETA
# =============================================================================

async def demonstracao_sistema_completo():
    """Demonstração completa do sistema integrado"""
    print("🎬 DEMONSTRAÇÃO DO SISTEMA INTEGRADO DE TRADING")
    print("=" * 80)
    
    sistema = SistemaIntegradoTrading()
    
    try:
        # Inicializar componentes
        await sistema.inicializar_componentes()
        
        print("\n📊 DEMONSTRAÇÃO DAS FUNCIONALIDADES")
        print("-" * 50)
        
        # 1. Verificar status das corretoras
        print("\n1️⃣  Status das Corretoras:")
        status_corretoras = sistema.gerenciador_corretoras.obter_status_sistema()
        for nome, info in status_corretoras['conectores'].items():
            status_emoji = "✅" if info['status'] == 'conectado' else "❌"
            print(f"   {status_emoji} {nome}: {info['tipo']} ({info['status']})")
            
        # 2. Verificar estratégias de trading
        if sistema.trading_automatizado:
            print("\n2️⃣  Estratégias de Trading:")
            status_trading = sistema.trading_automatizado.obter_status_sistema()
            for nome, info in status_trading['estrategias'].items():
                status_emoji = "🟢" if info['status'] == 'ativa' else "🔴"
                print(f"   {status_emoji} {nome}: {info['status']} ({len(info['simbolos'])} símbolos)")
                
        # 3. Executar ciclo de análise
        print("\n3️⃣  Executando Análise de Mercado...")
        if sistema.trading_automatizado:
            await sistema.trading_automatizado.executar_ciclo_analise()
            
        # 4. Monitorar portfólio
        print("\n4️⃣  Monitorando Portfólio...")
        if sistema.monitor_portfolio:
            await sistema.monitor_portfolio.executar_ciclo_monitoramento()
            
            # Mostrar métricas se disponíveis
            if sistema.monitor_portfolio.historico_metricas:
                metrica = sistema.monitor_portfolio.historico_metricas[-1]
                print(f"   💰 Valor Total: ${metrica.valor_total:,.2f}")
                print(f"   📈 P&L: ${metrica.pnl_total:,.2f} ({metrica.percentual_retorno:.2f}%)")
                print(f"   📊 Posições: {metrica.num_posicoes}")
                print(f"   🎯 Diversificação: {metrica.diversificacao:.1%}")
                
        # 5. Verificar alertas
        if sistema.monitor_portfolio:
            alertas_ativos = [a for a in sistema.monitor_portfolio.alertas_ativos.values() if a.ativo]
            print(f"\n5️⃣  Alertas Ativos: {len(alertas_ativos)}")
            for alerta in alertas_ativos[:3]:  # Mostrar apenas os 3 primeiros
                print(f"   🚨 {alerta.titulo} ({alerta.severidade})")
                
        print("\n🎉 Demonstração concluída com sucesso!")
        print("\n💡 Para executar o sistema completo, use:")
        print("   python backend/sistema_integrado_trading.py")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await sistema.parar_sistema()

# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

async def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Modo demonstração
        await demonstracao_sistema_completo()
    else:
        # Modo normal - executar sistema completo
        sistema = SistemaIntegradoTrading()
        
        # Configurar handler para SIGINT (Ctrl+C)
        def signal_handler(signum, frame):
            print("\n🛑 Sinal de interrupção recebido...")
            sistema.ativo = False
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Iniciar sistema
        await sistema.iniciar_sistema()

if __name__ == "__main__":
    print("🚀 Iniciando Sistema Integrado de Trading...")
    asyncio.run(main())