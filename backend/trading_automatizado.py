#!/usr/bin/env python3
"""
Sistema de Trading Automatizado
Execução automática de estratégias usando integração com corretoras
Autor: Agent Especialista Mercado Financeiro
Data: 2025-01-06
"""

import asyncio
import json
import logging
import sqlite3
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import os

# Importar componentes do sistema
from integracao_corretoras import (
    GerenciadorCorretoras, OrdemExecucao, TipoOrdem, DirecaoOperacao,
    StatusOrdem, PosicaoPortfolio, ResultadoOrdem
)

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import talib
    INDICADORES_DISPONIVEL = True
except ImportError:
    INDICADORES_DISPONIVEL = False
    print("⚠️  Bibliotecas de análise técnica não disponíveis")

# =============================================================================
# ENUMS E CONFIGURAÇÕES
# =============================================================================

class StatusEstrategia(Enum):
    """Status da estratégia de trading"""
    ATIVA = "ativa"
    PAUSADA = "pausada"
    PARADA = "parada"
    ERRO = "erro"

class TipoSinal(Enum):
    """Tipo de sinal de trading"""
    COMPRA = "compra"
    VENDA = "venda"
    MANUTENCAO = "manutencao"

class TipoEstrategia(Enum):
    """Tipos de estratégias disponíveis"""
    MEDIA_MOVEL = "media_movel"
    RSI_OVERSOLD = "rsi_oversold"
    BREAKOUT = "breakout"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"

# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class ConfigEstrategia:
    """Configuração de uma estratégia de trading"""
    nome: str
    tipo: TipoEstrategia
    simbolos: List[str]
    ativo: bool = True
    capital_alocado: Decimal = Decimal('10000')
    risco_por_operacao: Decimal = Decimal('0.02')  # 2%
    stop_loss: Decimal = Decimal('0.05')  # 5%
    take_profit: Decimal = Decimal('0.10')  # 10%
    timeframe: str = "1d"
    parametros: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parametros is None:
            self.parametros = {}

@dataclass
class SinalTrading:
    """Sinal de trading gerado por uma estratégia"""
    estrategia: str
    simbolo: str
    tipo: TipoSinal
    confianca: float  # 0-1
    preco_entrada: Decimal
    preco_stop: Optional[Decimal]
    preco_alvo: Optional[Decimal]
    tamanho_posicao: Decimal
    timestamp: datetime
    dados_contexto: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dados_contexto is None:
            self.dados_contexto = {}

@dataclass
class ResultadoOperacao:
    """Resultado de uma operação de trading"""
    id_operacao: str
    estrategia: str
    simbolo: str
    direcao: DirecaoOperacao
    quantidade: Decimal
    preco_entrada: Decimal
    preco_saida: Optional[Decimal]
    timestamp_entrada: datetime
    timestamp_saida: Optional[datetime]
    pnl_bruto: Decimal
    pnl_liquido: Decimal
    taxa_corretagem: Decimal
    status: str  # aberta, fechada, cancelada
    motivo_fechamento: str = ""  # stop_loss, take_profit, sinal_saida, manual

# =============================================================================
# CLASSE BASE PARA ESTRATÉGIAS
# =============================================================================

class EstrategiaBase:
    """Classe base para estratégias de trading"""
    
    def __init__(self, config: ConfigEstrategia, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.status = StatusEstrategia.PAUSADA
        self.posicoes_abertas: Dict[str, ResultadoOperacao] = {}
        self.historico_sinais: List[SinalTrading] = []
        self.historico_operacoes: List[ResultadoOperacao] = []
        
    def ativar(self):
        """Ativa a estratégia"""
        self.status = StatusEstrategia.ATIVA
        self.logger.info(f"✅ Estratégia {self.config.nome} ativada")
        
    def pausar(self):
        """Pausa a estratégia"""
        self.status = StatusEstrategia.PAUSADA
        self.logger.info(f"⏸️  Estratégia {self.config.nome} pausada")
        
    def parar(self):
        """Para a estratégia"""
        self.status = StatusEstrategia.PARADA
        self.logger.info(f"🛑 Estratégia {self.config.nome} parada")
        
    def obter_dados_mercado(self, simbolo: str, periodo: str = "90d") -> pd.DataFrame:
        """Obtém dados de mercado para análise"""
        try:
            ticker = yf.Ticker(simbolo)
            dados = ticker.history(period=periodo, interval=self.config.timeframe)
            return dados
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter dados de {simbolo}: {e}")
            return pd.DataFrame()
            
    def calcular_tamanho_posicao(self, preco_entrada: Decimal, preco_stop: Decimal) -> Decimal:
        """Calcula tamanho da posição baseado no risco"""
        risco_monetario = self.config.capital_alocado * self.config.risco_por_operacao
        risco_por_acao = abs(preco_entrada - preco_stop)
        
        if risco_por_acao > 0:
            tamanho = risco_monetario / risco_por_acao
            return min(tamanho, self.config.capital_alocado / preco_entrada)
        return Decimal('0')
        
    def gerar_sinal(self, simbolo: str) -> Optional[SinalTrading]:
        """Método abstrato para gerar sinais - deve ser implementado pelas subclasses"""
        raise NotImplementedError("Método deve ser implementado pela subclasse")
        
    def analisar_todos_simbolos(self) -> List[SinalTrading]:
        """Analisa todos os símbolos da estratégia"""
        sinais = []
        
        if self.status != StatusEstrategia.ATIVA:
            return sinais
            
        for simbolo in self.config.simbolos:
            try:
                sinal = self.gerar_sinal(simbolo)
                if sinal:
                    sinais.append(sinal)
                    self.historico_sinais.append(sinal)
            except Exception as e:
                self.logger.error(f"❌ Erro ao analisar {simbolo}: {e}")
                
        return sinais

# =============================================================================
# ESTRATÉGIAS ESPECÍFICAS
# =============================================================================

class EstrategiaMediaMovel(EstrategiaBase):
    """Estratégia baseada em cruzamento de médias móveis"""
    
    def __init__(self, config: ConfigEstrategia, logger: logging.Logger):
        super().__init__(config, logger)
        self.periodo_rapida = config.parametros.get('periodo_rapida', 10)
        self.periodo_lenta = config.parametros.get('periodo_lenta', 30)
        
    def gerar_sinal(self, simbolo: str) -> Optional[SinalTrading]:
        """Gera sinal baseado em cruzamento de médias"""
        dados = self.obter_dados_mercado(simbolo)
        
        if len(dados) < self.periodo_lenta + 5:
            return None
            
        # Calcular médias móveis
        dados['MA_Rapida'] = dados['Close'].rolling(window=self.periodo_rapida).mean()
        dados['MA_Lenta'] = dados['Close'].rolling(window=self.periodo_lenta).mean()
        
        # Verificar cruzamento
        atual = dados.iloc[-1]
        anterior = dados.iloc[-2]
        
        preco_atual = Decimal(str(atual['Close']))
        ma_rapida_atual = atual['MA_Rapida']
        ma_lenta_atual = atual['MA_Lenta']
        ma_rapida_anterior = anterior['MA_Rapida']
        ma_lenta_anterior = anterior['MA_Lenta']
        
        # Sinal de compra: média rápida cruza acima da lenta
        if (ma_rapida_anterior <= ma_lenta_anterior and 
            ma_rapida_atual > ma_lenta_atual and
            simbolo not in self.posicoes_abertas):
            
            preco_stop = preco_atual * (1 - self.config.stop_loss)
            preco_alvo = preco_atual * (1 + self.config.take_profit)
            tamanho = self.calcular_tamanho_posicao(preco_atual, preco_stop)
            
            return SinalTrading(
                estrategia=self.config.nome,
                simbolo=simbolo,
                tipo=TipoSinal.COMPRA,
                confianca=0.7,
                preco_entrada=preco_atual,
                preco_stop=preco_stop,
                preco_alvo=preco_alvo,
                tamanho_posicao=tamanho,
                timestamp=datetime.now(),
                dados_contexto={
                    'ma_rapida': ma_rapida_atual,
                    'ma_lenta': ma_lenta_atual,
                    'volume': atual['Volume']
                }
            )
            
        # Sinal de venda: média rápida cruza abaixo da lenta
        elif (ma_rapida_anterior >= ma_lenta_anterior and 
              ma_rapida_atual < ma_lenta_atual and
              simbolo in self.posicoes_abertas):
            
            return SinalTrading(
                estrategia=self.config.nome,
                simbolo=simbolo,
                tipo=TipoSinal.VENDA,
                confianca=0.6,
                preco_entrada=preco_atual,
                preco_stop=None,
                preco_alvo=None,
                tamanho_posicao=self.posicoes_abertas[simbolo].quantidade,
                timestamp=datetime.now(),
                dados_contexto={
                    'ma_rapida': ma_rapida_atual,
                    'ma_lenta': ma_lenta_atual,
                    'motivo': 'cruzamento_baixa'
                }
            )
            
        return None

class EstrategiaRSI(EstrategiaBase):
    """Estratégia baseada em RSI para sobrevendido/sobrecomprado"""
    
    def __init__(self, config: ConfigEstrategia, logger: logging.Logger):
        super().__init__(config, logger)
        self.periodo_rsi = config.parametros.get('periodo_rsi', 14)
        self.nivel_sobrevendido = config.parametros.get('nivel_sobrevendido', 30)
        self.nivel_sobrecomprado = config.parametros.get('nivel_sobrecomprado', 70)
        
    def gerar_sinal(self, simbolo: str) -> Optional[SinalTrading]:
        """Gera sinal baseado em RSI"""
        if not INDICADORES_DISPONIVEL:
            return None
            
        dados = self.obter_dados_mercado(simbolo)
        
        if len(dados) < self.periodo_rsi + 5:
            return None
            
        # Calcular RSI
        rsi = talib.RSI(dados['Close'].values, timeperiod=self.periodo_rsi)
        dados['RSI'] = rsi
        
        atual = dados.iloc[-1]
        preco_atual = Decimal(str(atual['Close']))
        rsi_atual = atual['RSI']
        
        # Sinal de compra: RSI saindo de sobrevendido
        if (rsi_atual > self.nivel_sobrevendido and 
            rsi_atual < self.nivel_sobrevendido + 10 and
            simbolo not in self.posicoes_abertas):
            
            preco_stop = preco_atual * (1 - self.config.stop_loss)
            preco_alvo = preco_atual * (1 + self.config.take_profit)
            tamanho = self.calcular_tamanho_posicao(preco_atual, preco_stop)
            
            confianca = 0.8 if rsi_atual < 25 else 0.6
            
            return SinalTrading(
                estrategia=self.config.nome,
                simbolo=simbolo,
                tipo=TipoSinal.COMPRA,
                confianca=confianca,
                preco_entrada=preco_atual,
                preco_stop=preco_stop,
                preco_alvo=preco_alvo,
                tamanho_posicao=tamanho,
                timestamp=datetime.now(),
                dados_contexto={
                    'rsi': rsi_atual,
                    'volume': atual['Volume'],
                    'motivo': 'rsi_sobrevendido'
                }
            )
            
        # Sinal de venda: RSI em sobrecomprado
        elif (rsi_atual > self.nivel_sobrecomprado and
              simbolo in self.posicoes_abertas):
            
            return SinalTrading(
                estrategia=self.config.nome,
                simbolo=simbolo,
                tipo=TipoSinal.VENDA,
                confianca=0.7,
                preco_entrada=preco_atual,
                preco_stop=None,
                preco_alvo=None,
                tamanho_posicao=self.posicoes_abertas[simbolo].quantidade,
                timestamp=datetime.now(),
                dados_contexto={
                    'rsi': rsi_atual,
                    'motivo': 'rsi_sobrecomprado'
                }
            )
            
        return None

# =============================================================================
# GERENCIADOR DE TRADING AUTOMATIZADO
# =============================================================================

class GerenciadorTradingAutomatizado:
    """Gerenciador principal do sistema de trading automatizado"""
    
    def __init__(self, gerenciador_corretoras: GerenciadorCorretoras):
        self.gerenciador_corretoras = gerenciador_corretoras
        self.estrategias: Dict[str, EstrategiaBase] = {}
        self.logger = self._configurar_logging()
        self.ativo = False
        self.intervalo_analise = 60  # segundos
        self.db_path = "data/trading_automatizado.db"
        self._inicializar_database()
        
    def _configurar_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger('trading_automatizado')
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
        
        # Tabela de sinais
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sinais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estrategia TEXT NOT NULL,
                simbolo TEXT NOT NULL,
                tipo TEXT NOT NULL,
                confianca REAL NOT NULL,
                preco_entrada REAL NOT NULL,
                preco_stop REAL,
                preco_alvo REAL,
                tamanho_posicao REAL NOT NULL,
                timestamp TEXT NOT NULL,
                dados_json TEXT
            )
        ''')
        
        # Tabela de operações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_operacao TEXT NOT NULL,
                estrategia TEXT NOT NULL,
                simbolo TEXT NOT NULL,
                direcao TEXT NOT NULL,
                quantidade REAL NOT NULL,
                preco_entrada REAL NOT NULL,
                preco_saida REAL,
                timestamp_entrada TEXT NOT NULL,
                timestamp_saida TEXT,
                pnl_bruto REAL,
                pnl_liquido REAL,
                taxa_corretagem REAL,
                status TEXT NOT NULL,
                motivo_fechamento TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def carregar_estrategias(self, arquivo_config: str = "config/estrategias.json"):
        """Carrega estratégias do arquivo de configuração"""
        try:
            if not os.path.exists(arquivo_config):
                self._criar_config_estrategias_exemplo(arquivo_config)
                
            with open(arquivo_config, 'r', encoding='utf-8') as f:
                configs = json.load(f)
                
            for nome, config_data in configs.items():
                config = ConfigEstrategia(
                    nome=nome,
                    tipo=TipoEstrategia(config_data['tipo']),
                    simbolos=config_data['simbolos'],
                    ativo=config_data.get('ativo', True),
                    capital_alocado=Decimal(str(config_data.get('capital_alocado', 10000))),
                    risco_por_operacao=Decimal(str(config_data.get('risco_por_operacao', 0.02))),
                    stop_loss=Decimal(str(config_data.get('stop_loss', 0.05))),
                    take_profit=Decimal(str(config_data.get('take_profit', 0.10))),
                    timeframe=config_data.get('timeframe', '1d'),
                    parametros=config_data.get('parametros', {})
                )
                
                # Criar instância da estratégia
                if config.tipo == TipoEstrategia.MEDIA_MOVEL:
                    estrategia = EstrategiaMediaMovel(config, self.logger)
                elif config.tipo == TipoEstrategia.RSI_OVERSOLD:
                    estrategia = EstrategiaRSI(config, self.logger)
                else:
                    self.logger.warning(f"⚠️  Tipo de estratégia não suportado: {config.tipo}")
                    continue
                    
                self.estrategias[nome] = estrategia
                
                if config.ativo:
                    estrategia.ativar()
                    
                self.logger.info(f"📈 Estratégia carregada: {nome}")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar estratégias: {e}")
            
    def _criar_config_estrategias_exemplo(self, arquivo: str):
        """Cria arquivo de configuração de estratégias de exemplo"""
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)
        
        config_exemplo = {
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
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(config_exemplo, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"📝 Arquivo de estratégias criado: {arquivo}")
        
    async def executar_sinal(self, sinal: SinalTrading) -> Optional[ResultadoOperacao]:
        """Executa um sinal de trading"""
        try:
            # Determinar direção da ordem
            if sinal.tipo == TipoSinal.COMPRA:
                direcao = DirecaoOperacao.COMPRA
            elif sinal.tipo == TipoSinal.VENDA:
                direcao = DirecaoOperacao.VENDA
            else:
                return None
                
            # Criar ordem
            ordem = OrdemExecucao(
                simbolo=sinal.simbolo,
                quantidade=sinal.tamanho_posicao,
                direcao=direcao,
                tipo=TipoOrdem.MARKET,
                client_order_id=f"{sinal.estrategia}_{sinal.simbolo}_{int(time.time())}"
            )
            
            # Executar ordem
            resultado = await self.gerenciador_corretoras.executar_ordem(ordem)
            
            if resultado and resultado.status == StatusOrdem.PREENCHIDA:
                # Criar registro de operação
                operacao = ResultadoOperacao(
                    id_operacao=resultado.ordem_id,
                    estrategia=sinal.estrategia,
                    simbolo=sinal.simbolo,
                    direcao=direcao,
                    quantidade=resultado.quantidade_preenchida,
                    preco_entrada=resultado.preco_medio,
                    preco_saida=None,
                    timestamp_entrada=resultado.timestamp,
                    timestamp_saida=None,
                    pnl_bruto=Decimal('0'),
                    pnl_liquido=-resultado.taxa_corretagem,
                    taxa_corretagem=resultado.taxa_corretagem,
                    status="aberta"
                )
                
                # Atualizar estratégia
                estrategia = self.estrategias[sinal.estrategia]
                if direcao == DirecaoOperacao.COMPRA:
                    estrategia.posicoes_abertas[sinal.simbolo] = operacao
                else:
                    # Remover posição aberta
                    estrategia.posicoes_abertas.pop(sinal.simbolo, None)
                    operacao.status = "fechada"
                    operacao.timestamp_saida = datetime.now()
                    
                # Salvar no database
                self._salvar_operacao(operacao)
                
                self.logger.info(f"✅ Sinal executado: {sinal.simbolo} {direcao.value} {resultado.quantidade_preenchida}")
                return operacao
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar sinal: {e}")
            
        return None
        
    def _salvar_sinal(self, sinal: SinalTrading):
        """Salva sinal no database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sinais (
                    estrategia, simbolo, tipo, confianca, preco_entrada,
                    preco_stop, preco_alvo, tamanho_posicao, timestamp, dados_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sinal.estrategia,
                sinal.simbolo,
                sinal.tipo.value,
                sinal.confianca,
                float(sinal.preco_entrada),
                float(sinal.preco_stop) if sinal.preco_stop else None,
                float(sinal.preco_alvo) if sinal.preco_alvo else None,
                float(sinal.tamanho_posicao),
                sinal.timestamp.isoformat(),
                json.dumps(sinal.dados_contexto, default=str)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar sinal: {e}")
            
    def _salvar_operacao(self, operacao: ResultadoOperacao):
        """Salva operação no database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO operacoes (
                    id_operacao, estrategia, simbolo, direcao, quantidade,
                    preco_entrada, preco_saida, timestamp_entrada, timestamp_saida,
                    pnl_bruto, pnl_liquido, taxa_corretagem, status, motivo_fechamento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                operacao.id_operacao,
                operacao.estrategia,
                operacao.simbolo,
                operacao.direcao.value,
                float(operacao.quantidade),
                float(operacao.preco_entrada),
                float(operacao.preco_saida) if operacao.preco_saida else None,
                operacao.timestamp_entrada.isoformat(),
                operacao.timestamp_saida.isoformat() if operacao.timestamp_saida else None,
                float(operacao.pnl_bruto),
                float(operacao.pnl_liquido),
                float(operacao.taxa_corretagem),
                operacao.status,
                operacao.motivo_fechamento
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar operação: {e}")
            
    async def executar_ciclo_analise(self):
        """Executa um ciclo de análise das estratégias"""
        self.logger.info("🔄 Iniciando ciclo de análise")
        
        total_sinais = 0
        
        for nome, estrategia in self.estrategias.items():
            if estrategia.status == StatusEstrategia.ATIVA:
                sinais = estrategia.analisar_todos_simbolos()
                
                for sinal in sinais:
                    # Salvar sinal
                    self._salvar_sinal(sinal)
                    
                    # Executar sinal se confiança suficiente
                    if sinal.confianca >= 0.6:
                        await self.executar_sinal(sinal)
                        total_sinais += 1
                        
        self.logger.info(f"📊 Ciclo concluído: {total_sinais} sinais executados")
        
    async def iniciar(self):
        """Inicia o sistema de trading automatizado"""
        self.ativo = True
        self.logger.info("🚀 Sistema de Trading Automatizado iniciado")
        
        while self.ativo:
            try:
                await self.executar_ciclo_analise()
                await asyncio.sleep(self.intervalo_analise)
            except Exception as e:
                self.logger.error(f"❌ Erro no ciclo de trading: {e}")
                await asyncio.sleep(10)
                
    def parar(self):
        """Para o sistema de trading automatizado"""
        self.ativo = False
        self.logger.info("🛑 Sistema de Trading Automatizado parado")
        
    def obter_status_sistema(self) -> Dict[str, Any]:
        """Obtém status do sistema de trading"""
        total_posicoes = sum(len(e.posicoes_abertas) for e in self.estrategias.values())
        estrategias_ativas = sum(1 for e in self.estrategias.values() if e.status == StatusEstrategia.ATIVA)
        
        return {
            'ativo': self.ativo,
            'total_estrategias': len(self.estrategias),
            'estrategias_ativas': estrategias_ativas,
            'total_posicoes_abertas': total_posicoes,
            'intervalo_analise': self.intervalo_analise,
            'timestamp': datetime.now().isoformat(),
            'estrategias': {
                nome: {
                    'status': e.status.value,
                    'posicoes_abertas': len(e.posicoes_abertas),
                    'total_sinais': len(e.historico_sinais),
                    'simbolos': e.config.simbolos
                }
                for nome, e in self.estrategias.items()
            }
        }

# =============================================================================
# FUNÇÃO DE TESTE E DEMONSTRAÇÃO
# =============================================================================

async def testar_trading_automatizado():
    """Testa o sistema de trading automatizado"""
    print("🤖 Testando Sistema de Trading Automatizado")
    print("=" * 60)
    
    # Importar gerenciador de corretoras
    from integracao_corretoras import GerenciadorCorretoras
    
    # Inicializar componentes
    gerenciador_corretoras = GerenciadorCorretoras()
    await gerenciador_corretoras.inicializar_conectores()
    
    trading_manager = GerenciadorTradingAutomatizado(gerenciador_corretoras)
    trading_manager.carregar_estrategias()
    
    # Verificar status
    status = trading_manager.obter_status_sistema()
    print(f"📊 Total de estratégias: {status['total_estrategias']}")
    print(f"🎯 Estratégias ativas: {status['estrategias_ativas']}")
    
    for nome, info in status['estrategias'].items():
        print(f"  - {nome}: {info['status']} ({len(info['simbolos'])} símbolos)")
        
    # Executar um ciclo de análise
    print("\n🔄 Executando ciclo de análise...")
    await trading_manager.executar_ciclo_analise()
    
    # Verificar status após análise
    status_final = trading_manager.obter_status_sistema()
    print(f"\n📈 Posições abertas: {status_final['total_posicoes_abertas']}")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(testar_trading_automatizado())