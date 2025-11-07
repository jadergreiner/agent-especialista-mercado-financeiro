#!/usr/bin/env python3
"""
Sistema de Integração com Corretoras
Conectores para APIs de corretoras para execução automática e sincronização de portfólio
Autor: Agent Especialista Mercado Financeiro
Data: 2025-01-06
"""

import asyncio
import json
import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import os

# Importações específicas para cada corretora
try:
    import alpaca_trade_api as tradeapi
    ALPACA_DISPONIVEL = True
except ImportError:
    ALPACA_DISPONIVEL = False
    print("⚠️  Alpaca Trade API não disponível. Install: pip install alpaca-trade-api")

try:
    from ib_insync import IB, Stock, Order, MarketOrder, LimitOrder
    IB_DISPONIVEL = True
except ImportError:
    IB_DISPONIVEL = False
    print("⚠️  IB-insync não disponível. Install: pip install ib-insync")

import yfinance as yf
import pandas as pd

# =============================================================================
# ENUMS E CONSTANTES
# =============================================================================

class TipoCorretora(Enum):
    """Tipos de corretoras suportadas"""
    ALPACA = "alpaca"
    INTERACTIVE_BROKERS = "interactive_brokers"
    SIMULADO = "simulado"

class TipoOrdem(Enum):
    """Tipos de ordem"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class StatusOrdem(Enum):
    """Status da ordem"""
    PENDENTE = "pendente"
    PREENCHIDA = "preenchida"
    CANCELADA = "cancelada"
    REJEITADA = "rejeitada"
    PARCIALMENTE_PREENCHIDA = "parcialmente_preenchida"

class DirecaoOperacao(Enum):
    """Direção da operação"""
    COMPRA = "buy"
    VENDA = "sell"

class StatusConexao(Enum):
    """Status da conexão com a corretora"""
    CONECTADO = "conectado"
    DESCONECTADO = "desconectado"
    ERRO = "erro"
    CONECTANDO = "conectando"

# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class ConfigCorretora:
    """Configuração de uma corretora"""
    tipo: TipoCorretora
    nome: str
    api_key: str
    api_secret: str
    base_url: str = ""
    paper_trading: bool = True
    timeout: int = 30
    rate_limit: int = 200  # requests per minute
    configuracoes_extras: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.configuracoes_extras is None:
            self.configuracoes_extras = {}

@dataclass
class OrdemExecucao:
    """Ordem para execução"""
    simbolo: str
    quantidade: Decimal
    direcao: DirecaoOperacao
    tipo: TipoOrdem
    preco_limite: Optional[Decimal] = None
    preco_stop: Optional[Decimal] = None
    time_in_force: str = "day"  # day, gtc, ioc, fok
    client_order_id: Optional[str] = None
    
@dataclass
class ResultadoOrdem:
    """Resultado da execução de uma ordem"""
    ordem_id: str
    client_order_id: Optional[str]
    simbolo: str
    quantidade: Decimal
    quantidade_preenchida: Decimal
    preco_medio: Decimal
    status: StatusOrdem
    timestamp: datetime
    taxa_corretagem: Decimal = Decimal('0')
    mensagem: str = ""
    dados_raw: Dict[str, Any] = None

@dataclass
class PosicaoPortfolio:
    """Posição no portfólio"""
    simbolo: str
    quantidade: Decimal
    preco_medio: Decimal
    valor_mercado: Decimal
    pnl_realizado: Decimal
    pnl_nao_realizado: Decimal
    timestamp: datetime

@dataclass
class DadosMercado:
    """Dados de mercado em tempo real"""
    simbolo: str
    preco_bid: Decimal
    preco_ask: Decimal
    preco_ultimo: Decimal
    volume: int
    timestamp: datetime

# =============================================================================
# CLASSE BASE PARA CONECTORES
# =============================================================================

class ConectorCorretora(ABC):
    """Classe base para conectores de corretoras"""
    
    def __init__(self, config: ConfigCorretora, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.status_conexao = StatusConexao.DESCONECTADO
        self.ultima_atividade = datetime.now()
        self.ordens_pendentes: Dict[str, OrdemExecucao] = {}
        self.callbacks_ordem: Dict[str, Callable] = {}
        self.callbacks_posicao: List[Callable] = []
        self.callbacks_mercado: List[Callable] = []
        
    @abstractmethod
    async def conectar(self) -> bool:
        """Conecta com a corretora"""
        pass
        
    @abstractmethod
    async def desconectar(self) -> bool:
        """Desconecta da corretora"""
        pass
        
    @abstractmethod
    async def verificar_conexao(self) -> bool:
        """Verifica se a conexão está ativa"""
        pass
        
    @abstractmethod
    async def executar_ordem(self, ordem: OrdemExecucao) -> ResultadoOrdem:
        """Executa uma ordem"""
        pass
        
    @abstractmethod
    async def cancelar_ordem(self, ordem_id: str) -> bool:
        """Cancela uma ordem"""
        pass
        
    @abstractmethod
    async def obter_posicoes(self) -> List[PosicaoPortfolio]:
        """Obtém posições do portfólio"""
        pass
        
    @abstractmethod
    async def obter_saldo_conta(self) -> Dict[str, Decimal]:
        """Obtém saldo da conta"""
        pass
        
    @abstractmethod
    async def obter_dados_mercado(self, simbolos: List[str]) -> Dict[str, DadosMercado]:
        """Obtém dados de mercado em tempo real"""
        pass
        
    def registrar_callback_ordem(self, ordem_id: str, callback: Callable):
        """Registra callback para atualizações de ordem"""
        self.callbacks_ordem[ordem_id] = callback
        
    def registrar_callback_posicao(self, callback: Callable):
        """Registra callback para atualizações de posição"""
        self.callbacks_posicao.append(callback)
        
    def registrar_callback_mercado(self, callback: Callable):
        """Registra callback para dados de mercado"""
        self.callbacks_mercado.append(callback)

# =============================================================================
# CONECTOR ALPACA
# =============================================================================

class ConectorAlpaca(ConectorCorretora):
    """Conector para Alpaca Markets"""
    
    def __init__(self, config: ConfigCorretora, logger: logging.Logger):
        super().__init__(config, logger)
        self.api = None
        self.stream = None
        
    async def conectar(self) -> bool:
        """Conecta com Alpaca"""
        try:
            if not ALPACA_DISPONIVEL:
                raise ImportError("Alpaca Trade API não está disponível")
                
            self.status_conexao = StatusConexao.CONECTANDO
            
            base_url = self.config.base_url or (
                "https://paper-api.alpaca.markets" if self.config.paper_trading 
                else "https://api.alpaca.markets"
            )
            
            self.api = tradeapi.REST(
                key_id=self.config.api_key,
                secret_key=self.config.api_secret,
                base_url=base_url,
                api_version='v2'
            )
            
            # Verificar conexão
            conta = self.api.get_account()
            self.logger.info(f"✅ Conectado ao Alpaca - Conta: {conta.account_number}")
            
            self.status_conexao = StatusConexao.CONECTADO
            self.ultima_atividade = datetime.now()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar com Alpaca: {e}")
            self.status_conexao = StatusConexao.ERRO
            return False
            
    async def desconectar(self) -> bool:
        """Desconecta do Alpaca"""
        try:
            if self.stream:
                await self.stream.stop_ws()
                
            self.api = None
            self.stream = None
            self.status_conexao = StatusConexao.DESCONECTADO
            self.logger.info("🔌 Desconectado do Alpaca")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao desconectar do Alpaca: {e}")
            return False
            
    async def verificar_conexao(self) -> bool:
        """Verifica conexão com Alpaca"""
        try:
            if not self.api:
                return False
                
            self.api.get_clock()
            self.ultima_atividade = datetime.now()
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠️  Conexão com Alpaca perdida: {e}")
            self.status_conexao = StatusConexao.ERRO
            return False
            
    async def executar_ordem(self, ordem: OrdemExecucao) -> ResultadoOrdem:
        """Executa ordem no Alpaca"""
        try:
            # Preparar dados da ordem
            order_data = {
                'symbol': ordem.simbolo,
                'qty': float(ordem.quantidade),
                'side': ordem.direcao.value,
                'type': ordem.tipo.value,
                'time_in_force': ordem.time_in_force
            }
            
            if ordem.preco_limite:
                order_data['limit_price'] = float(ordem.preco_limite)
                
            if ordem.preco_stop:
                order_data['stop_price'] = float(ordem.preco_stop)
                
            if ordem.client_order_id:
                order_data['client_order_id'] = ordem.client_order_id
                
            # Executar ordem
            resposta = self.api.submit_order(**order_data)
            
            # Converter status
            status_map = {
                'new': StatusOrdem.PENDENTE,
                'accepted': StatusOrdem.PENDENTE,
                'filled': StatusOrdem.PREENCHIDA,
                'canceled': StatusOrdem.CANCELADA,
                'rejected': StatusOrdem.REJEITADA,
                'partially_filled': StatusOrdem.PARCIALMENTE_PREENCHIDA
            }
            
            status = status_map.get(resposta.status, StatusOrdem.PENDENTE)
            
            resultado = ResultadoOrdem(
                ordem_id=resposta.id,
                client_order_id=resposta.client_order_id,
                simbolo=resposta.symbol,
                quantidade=Decimal(str(resposta.qty)),
                quantidade_preenchida=Decimal(str(resposta.filled_qty or 0)),
                preco_medio=Decimal(str(resposta.filled_avg_price or 0)),
                status=status,
                timestamp=datetime.fromisoformat(resposta.created_at.replace('Z', '+00:00')),
                dados_raw=resposta._raw
            )
            
            self.logger.info(f"📋 Ordem executada - {ordem.simbolo}: {ordem.quantidade} x {ordem.direcao.value}")
            self.ultima_atividade = datetime.now()
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar ordem no Alpaca: {e}")
            return ResultadoOrdem(
                ordem_id="",
                client_order_id=ordem.client_order_id,
                simbolo=ordem.simbolo,
                quantidade=ordem.quantidade,
                quantidade_preenchida=Decimal('0'),
                preco_medio=Decimal('0'),
                status=StatusOrdem.REJEITADA,
                timestamp=datetime.now(),
                mensagem=str(e)
            )
            
    async def cancelar_ordem(self, ordem_id: str) -> bool:
        """Cancela ordem no Alpaca"""
        try:
            self.api.cancel_order(ordem_id)
            self.logger.info(f"🚫 Ordem cancelada: {ordem_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao cancelar ordem {ordem_id}: {e}")
            return False
            
    async def obter_posicoes(self) -> List[PosicaoPortfolio]:
        """Obtém posições do Alpaca"""
        try:
            posicoes_api = self.api.list_positions()
            posicoes = []
            
            for pos in posicoes_api:
                posicao = PosicaoPortfolio(
                    simbolo=pos.symbol,
                    quantidade=Decimal(str(pos.qty)),
                    preco_medio=Decimal(str(pos.avg_entry_price)),
                    valor_mercado=Decimal(str(pos.market_value)),
                    pnl_realizado=Decimal(str(pos.unrealized_pl)),
                    pnl_nao_realizado=Decimal(str(pos.unrealized_pl)),
                    timestamp=datetime.now()
                )
                posicoes.append(posicao)
                
            return posicoes
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter posições do Alpaca: {e}")
            return []
            
    async def obter_saldo_conta(self) -> Dict[str, Decimal]:
        """Obtém saldo da conta Alpaca"""
        try:
            conta = self.api.get_account()
            
            return {
                'capital_total': Decimal(str(conta.equity)),
                'capital_disponivel': Decimal(str(conta.buying_power)),
                'capital_investido': Decimal(str(conta.long_market_value or 0)),
                'pnl_dia': Decimal(str(conta.todays_pl or 0)),
                'pnl_total': Decimal(str(conta.unrealized_pl or 0))
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter saldo da conta Alpaca: {e}")
            return {}
            
    async def obter_dados_mercado(self, simbolos: List[str]) -> Dict[str, DadosMercado]:
        """Obtém dados de mercado do Alpaca"""
        try:
            # Para demo, usar yfinance como backup
            dados = {}
            
            for simbolo in simbolos:
                try:
                    ticker = yf.Ticker(simbolo)
                    info = ticker.fast_info
                    
                    dados[simbolo] = DadosMercado(
                        simbolo=simbolo,
                        preco_bid=Decimal(str(info.get('bid', info.get('last_price', 0)))),
                        preco_ask=Decimal(str(info.get('ask', info.get('last_price', 0)))),
                        preco_ultimo=Decimal(str(info.get('last_price', 0))),
                        volume=int(info.get('last_volume', 0)),
                        timestamp=datetime.now()
                    )
                except:
                    continue
                    
            return dados
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter dados de mercado: {e}")
            return {}

# =============================================================================
# CONECTOR SIMULADO
# =============================================================================

class ConectorSimulado(ConectorCorretora):
    """Conector simulado para testes"""
    
    def __init__(self, config: ConfigCorretora, logger: logging.Logger):
        super().__init__(config, logger)
        self.capital_inicial = Decimal('100000')  # $100k
        self.capital_atual = self.capital_inicial
        self.posicoes: Dict[str, PosicaoPortfolio] = {}
        self.historico_ordens: List[ResultadoOrdem] = []
        self.contador_ordem = 1
        
    async def conectar(self) -> bool:
        """Conecta ao modo simulado"""
        self.status_conexao = StatusConexao.CONECTADO
        self.logger.info("✅ Conectado ao modo simulado")
        return True
        
    async def desconectar(self) -> bool:
        """Desconecta do modo simulado"""
        self.status_conexao = StatusConexao.DESCONECTADO
        self.logger.info("🔌 Desconectado do modo simulado")
        return True
        
    async def verificar_conexao(self) -> bool:
        """Verifica conexão simulada"""
        return self.status_conexao == StatusConexao.CONECTADO
        
    async def executar_ordem(self, ordem: OrdemExecucao) -> ResultadoOrdem:
        """Executa ordem simulada"""
        try:
            # Obter preço atual
            ticker = yf.Ticker(ordem.simbolo)
            preco_atual = Decimal(str(ticker.fast_info.get('last_price', 100)))
            
            # Simular slippage
            slippage = Decimal('0.001')  # 0.1%
            if ordem.direcao == DirecaoOperacao.COMPRA:
                preco_execucao = preco_atual * (1 + slippage)
            else:
                preco_execucao = preco_atual * (1 - slippage)
                
            # Usar preço limite se especificado
            if ordem.preco_limite:
                if ordem.direcao == DirecaoOperacao.COMPRA and preco_execucao > ordem.preco_limite:
                    preco_execucao = ordem.preco_limite
                elif ordem.direcao == DirecaoOperacao.VENDA and preco_execucao < ordem.preco_limite:
                    preco_execucao = ordem.preco_limite
                    
            # Calcular valores
            valor_operacao = ordem.quantidade * preco_execucao
            taxa_corretagem = valor_operacao * Decimal('0.001')  # 0.1%
            
            # Verificar saldo disponível
            if ordem.direcao == DirecaoOperacao.COMPRA:
                if valor_operacao + taxa_corretagem > self.capital_atual:
                    raise ValueError("Saldo insuficiente")
                    
            # Executar operação
            ordem_id = f"SIM_{self.contador_ordem:06d}"
            self.contador_ordem += 1
            
            # Atualizar posições
            if ordem.simbolo in self.posicoes:
                posicao = self.posicoes[ordem.simbolo]
                if ordem.direcao == DirecaoOperacao.COMPRA:
                    nova_quantidade = posicao.quantidade + ordem.quantidade
                    novo_preco_medio = ((posicao.quantidade * posicao.preco_medio) + 
                                      (ordem.quantidade * preco_execucao)) / nova_quantidade
                else:
                    nova_quantidade = posicao.quantidade - ordem.quantidade
                    novo_preco_medio = posicao.preco_medio
                    
                if nova_quantidade <= 0:
                    del self.posicoes[ordem.simbolo]
                else:
                    posicao.quantidade = nova_quantidade
                    posicao.preco_medio = novo_preco_medio
                    posicao.timestamp = datetime.now()
            else:
                if ordem.direcao == DirecaoOperacao.COMPRA:
                    self.posicoes[ordem.simbolo] = PosicaoPortfolio(
                        simbolo=ordem.simbolo,
                        quantidade=ordem.quantidade,
                        preco_medio=preco_execucao,
                        valor_mercado=valor_operacao,
                        pnl_realizado=Decimal('0'),
                        pnl_nao_realizado=Decimal('0'),
                        timestamp=datetime.now()
                    )
                    
            # Atualizar capital
            if ordem.direcao == DirecaoOperacao.COMPRA:
                self.capital_atual -= (valor_operacao + taxa_corretagem)
            else:
                self.capital_atual += (valor_operacao - taxa_corretagem)
                
            resultado = ResultadoOrdem(
                ordem_id=ordem_id,
                client_order_id=ordem.client_order_id,
                simbolo=ordem.simbolo,
                quantidade=ordem.quantidade,
                quantidade_preenchida=ordem.quantidade,
                preco_medio=preco_execucao,
                status=StatusOrdem.PREENCHIDA,
                timestamp=datetime.now(),
                taxa_corretagem=taxa_corretagem
            )
            
            self.historico_ordens.append(resultado)
            self.logger.info(f"📋 Ordem simulada executada - {ordem.simbolo}: {ordem.quantidade} x {ordem.direcao.value} @ ${preco_execucao:.2f}")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"❌ Erro na ordem simulada: {e}")
            return ResultadoOrdem(
                ordem_id="",
                client_order_id=ordem.client_order_id,
                simbolo=ordem.simbolo,
                quantidade=ordem.quantidade,
                quantidade_preenchida=Decimal('0'),
                preco_medio=Decimal('0'),
                status=StatusOrdem.REJEITADA,
                timestamp=datetime.now(),
                mensagem=str(e)
            )
            
    async def cancelar_ordem(self, ordem_id: str) -> bool:
        """Cancela ordem simulada"""
        self.logger.info(f"🚫 Ordem simulada cancelada: {ordem_id}")
        return True
        
    async def obter_posicoes(self) -> List[PosicaoPortfolio]:
        """Obtém posições simuladas"""
        return list(self.posicoes.values())
        
    async def obter_saldo_conta(self) -> Dict[str, Decimal]:
        """Obtém saldo simulado"""
        valor_posicoes = sum(p.valor_mercado for p in self.posicoes.values())
        return {
            'capital_total': self.capital_atual + valor_posicoes,
            'capital_disponivel': self.capital_atual,
            'capital_investido': valor_posicoes,
            'pnl_dia': Decimal('0'),
            'pnl_total': (self.capital_atual + valor_posicoes) - self.capital_inicial
        }
        
    async def obter_dados_mercado(self, simbolos: List[str]) -> Dict[str, DadosMercado]:
        """Obtém dados de mercado simulados"""
        return await ConectorAlpaca.obter_dados_mercado(self, simbolos)

# =============================================================================
# GERENCIADOR DE CORRETORAS
# =============================================================================

class GerenciadorCorretoras:
    """Gerenciador central de todas as integrações com corretoras"""
    
    def __init__(self, arquivo_config: str = "config/corretoras.json"):
        self.arquivo_config = arquivo_config
        self.conectores: Dict[str, ConectorCorretora] = {}
        self.conector_ativo: Optional[ConectorCorretora] = None
        self.logger = self._configurar_logging()
        self.db_path = "data/integracao_corretoras.db"
        self._inicializar_database()
        
    def _configurar_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger('integracao_corretoras')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _inicializar_database(self):
        """Inicializa database SQLite"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de ordens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordem_id TEXT NOT NULL,
                corretora TEXT NOT NULL,
                simbolo TEXT NOT NULL,
                quantidade REAL NOT NULL,
                direcao TEXT NOT NULL,
                tipo TEXT NOT NULL,
                preco_medio REAL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                dados_json TEXT
            )
        ''')
        
        # Tabela de posições
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posicoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                corretora TEXT NOT NULL,
                simbolo TEXT NOT NULL,
                quantidade REAL NOT NULL,
                preco_medio REAL NOT NULL,
                valor_mercado REAL NOT NULL,
                pnl_realizado REAL NOT NULL,
                pnl_nao_realizado REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Tabela de saldos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saldos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                corretora TEXT NOT NULL,
                capital_total REAL NOT NULL,
                capital_disponivel REAL NOT NULL,
                capital_investido REAL NOT NULL,
                pnl_dia REAL NOT NULL,
                pnl_total REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def carregar_configuracoes(self) -> Dict[str, ConfigCorretora]:
        """Carrega configurações das corretoras"""
        try:
            if not os.path.exists(self.arquivo_config):
                self._criar_config_exemplo()
                
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                configs_raw = json.load(f)
                
            configs = {}
            for nome, config_data in configs_raw.items():
                configs[nome] = ConfigCorretora(
                    tipo=TipoCorretora(config_data['tipo']),
                    nome=nome,
                    api_key=config_data['api_key'],
                    api_secret=config_data['api_secret'],
                    base_url=config_data.get('base_url', ''),
                    paper_trading=config_data.get('paper_trading', True),
                    timeout=config_data.get('timeout', 30),
                    rate_limit=config_data.get('rate_limit', 200),
                    configuracoes_extras=config_data.get('configuracoes_extras', {})
                )
                
            return configs
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar configurações: {e}")
            return {}
            
    def _criar_config_exemplo(self):
        """Cria arquivo de configuração de exemplo"""
        os.makedirs(os.path.dirname(self.arquivo_config), exist_ok=True)
        
        config_exemplo = {
            "alpaca_paper": {
                "tipo": "alpaca",
                "api_key": "SEU_ALPACA_API_KEY",
                "api_secret": "SEU_ALPACA_SECRET_KEY",
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
        
        with open(self.arquivo_config, 'w', encoding='utf-8') as f:
            json.dump(config_exemplo, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"📝 Arquivo de configuração criado: {self.arquivo_config}")
        
    async def inicializar_conectores(self):
        """Inicializa todos os conectores configurados"""
        configs = self.carregar_configuracoes()
        
        for nome, config in configs.items():
            try:
                if config.tipo == TipoCorretora.ALPACA:
                    conector = ConectorAlpaca(config, self.logger)
                elif config.tipo == TipoCorretora.SIMULADO:
                    conector = ConectorSimulado(config, self.logger)
                else:
                    self.logger.warning(f"⚠️  Tipo de corretora não suportado: {config.tipo}")
                    continue
                    
                sucesso = await conector.conectar()
                if sucesso:
                    self.conectores[nome] = conector
                    if not self.conector_ativo:
                        self.conector_ativo = conector
                        
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar conector {nome}: {e}")
                
    async def definir_conector_ativo(self, nome: str) -> bool:
        """Define o conector ativo"""
        if nome in self.conectores:
            self.conector_ativo = self.conectores[nome]
            self.logger.info(f"🎯 Conector ativo definido: {nome}")
            return True
        return False
        
    async def executar_ordem(self, ordem: OrdemExecucao) -> Optional[ResultadoOrdem]:
        """Executa ordem no conector ativo"""
        if not self.conector_ativo:
            self.logger.error("❌ Nenhum conector ativo")
            return None
            
        resultado = await self.conector_ativo.executar_ordem(ordem)
        
        # Salvar no database
        self._salvar_ordem(resultado)
        
        return resultado
        
    async def obter_posicoes_todas(self) -> Dict[str, List[PosicaoPortfolio]]:
        """Obtém posições de todas as corretoras"""
        todas_posicoes = {}
        
        for nome, conector in self.conectores.items():
            try:
                posicoes = await conector.obter_posicoes()
                todas_posicoes[nome] = posicoes
                self._salvar_posicoes(nome, posicoes)
            except Exception as e:
                self.logger.error(f"❌ Erro ao obter posições de {nome}: {e}")
                todas_posicoes[nome] = []
                
        return todas_posicoes
        
    async def obter_saldos_todos(self) -> Dict[str, Dict[str, Decimal]]:
        """Obtém saldos de todas as corretoras"""
        todos_saldos = {}
        
        for nome, conector in self.conectores.items():
            try:
                saldo = await conector.obter_saldo_conta()
                todos_saldos[nome] = saldo
                self._salvar_saldo(nome, saldo)
            except Exception as e:
                self.logger.error(f"❌ Erro ao obter saldo de {nome}: {e}")
                todos_saldos[nome] = {}
                
        return todos_saldos
        
    def _salvar_ordem(self, resultado: ResultadoOrdem):
        """Salva ordem no database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ordens (
                    ordem_id, corretora, simbolo, quantidade, direcao, tipo,
                    preco_medio, status, timestamp, dados_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                resultado.ordem_id,
                self.conector_ativo.config.nome,
                resultado.simbolo,
                float(resultado.quantidade),
                "compra" if resultado.quantidade > 0 else "venda",
                "market",  # Simplificado
                float(resultado.preco_medio),
                resultado.status.value,
                resultado.timestamp.isoformat(),
                json.dumps(asdict(resultado), default=str)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar ordem: {e}")
            
    def _salvar_posicoes(self, corretora: str, posicoes: List[PosicaoPortfolio]):
        """Salva posições no database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Limpar posições antigas
            cursor.execute('DELETE FROM posicoes WHERE corretora = ?', (corretora,))
            
            # Inserir posições atuais
            for posicao in posicoes:
                cursor.execute('''
                    INSERT INTO posicoes (
                        corretora, simbolo, quantidade, preco_medio, valor_mercado,
                        pnl_realizado, pnl_nao_realizado, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    corretora,
                    posicao.simbolo,
                    float(posicao.quantidade),
                    float(posicao.preco_medio),
                    float(posicao.valor_mercado),
                    float(posicao.pnl_realizado),
                    float(posicao.pnl_nao_realizado),
                    posicao.timestamp.isoformat()
                ))
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar posições: {e}")
            
    def _salvar_saldo(self, corretora: str, saldo: Dict[str, Decimal]):
        """Salva saldo no database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO saldos (
                    corretora, capital_total, capital_disponivel, capital_investido,
                    pnl_dia, pnl_total, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                corretora,
                float(saldo.get('capital_total', 0)),
                float(saldo.get('capital_disponivel', 0)),
                float(saldo.get('capital_investido', 0)),
                float(saldo.get('pnl_dia', 0)),
                float(saldo.get('pnl_total', 0)),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar saldo: {e}")
            
    def obter_status_sistema(self) -> Dict[str, Any]:
        """Obtém status geral do sistema"""
        status = {
            'conectores': {},
            'conector_ativo': self.conector_ativo.config.nome if self.conector_ativo else None,
            'total_conectores': len(self.conectores),
            'timestamp': datetime.now().isoformat()
        }
        
        for nome, conector in self.conectores.items():
            status['conectores'][nome] = {
                'tipo': conector.config.tipo.value,
                'status': conector.status_conexao.value,
                'ultima_atividade': conector.ultima_atividade.isoformat(),
                'paper_trading': conector.config.paper_trading
            }
            
        return status

# =============================================================================
# FUNÇÕES DE TESTE E DEMONSTRAÇÃO
# =============================================================================

async def testar_sistema():
    """Testa o sistema de integração com corretoras"""
    print("🚀 Testando Sistema de Integração com Corretoras")
    print("=" * 60)
    
    # Inicializar gerenciador
    gerenciador = GerenciadorCorretoras()
    await gerenciador.inicializar_conectores()
    
    # Verificar status
    status = gerenciador.obter_status_sistema()
    print(f"📊 Conectores disponíveis: {status['total_conectores']}")
    print(f"🎯 Conector ativo: {status['conector_ativo']}")
    
    for nome, info in status['conectores'].items():
        print(f"  - {nome}: {info['tipo']} ({info['status']})")
        
    if not gerenciador.conector_ativo:
        print("❌ Nenhum conector disponível para teste")
        return
        
    print("\n💰 Testando Saldo da Conta")
    print("-" * 30)
    saldos = await gerenciador.obter_saldos_todos()
    for corretora, saldo in saldos.items():
        print(f"🏦 {corretora}:")
        for item, valor in saldo.items():
            print(f"  {item}: ${valor:,.2f}")
            
    print("\n📋 Testando Ordem de Compra")
    print("-" * 30)
    ordem_teste = OrdemExecucao(
        simbolo="AAPL",
        quantidade=Decimal('10'),
        direcao=DirecaoOperacao.COMPRA,
        tipo=TipoOrdem.MARKET,
        client_order_id="TESTE_001"
    )
    
    resultado = await gerenciador.executar_ordem(ordem_teste)
    if resultado:
        print(f"✅ Ordem executada: {resultado.simbolo}")
        print(f"   ID: {resultado.ordem_id}")
        print(f"   Quantidade: {resultado.quantidade_preenchida}")
        print(f"   Preço: ${resultado.preco_medio}")
        print(f"   Status: {resultado.status.value}")
        
    print("\n📈 Testando Posições")
    print("-" * 30)
    posicoes = await gerenciador.obter_posicoes_todas()
    for corretora, lista_posicoes in posicoes.items():
        print(f"🏦 {corretora}: {len(lista_posicoes)} posições")
        for posicao in lista_posicoes:
            print(f"  {posicao.simbolo}: {posicao.quantidade} @ ${posicao.preco_medio}")
            
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(testar_sistema())