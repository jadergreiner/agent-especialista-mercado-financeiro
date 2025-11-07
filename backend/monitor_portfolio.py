#!/usr/bin/env python3
"""
Monitor de Portfólio em Tempo Real
Sistema de monitoramento e sincronização de portfólio com corretoras
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
    GerenciadorCorretoras, PosicaoPortfolio, DadosMercado,
    StatusConexao
)

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    from flask import Flask, render_template, jsonify
    import plotly.graph_objs as go
    import plotly.utils
    WEBAPP_DISPONIVEL = True
except ImportError:
    WEBAPP_DISPONIVEL = False
    print("⚠️  Bibliotecas para webapp não disponíveis")

# =============================================================================
# ENUMS E CONFIGURAÇÕES
# =============================================================================

class TipoAlerta(Enum):
    """Tipos de alertas do portfólio"""
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    LIMITE_RISCO = "limite_risco"
    MARGEM_CALL = "margem_call"
    VOLATILIDADE_ALTA = "volatilidade_alta"

class StatusPortfolio(Enum):
    """Status do portfólio"""
    SAUDAVEL = "saudavel"
    ATENCAO = "atencao"
    RISCO_ALTO = "risco_alto"
    CRITICO = "critico"

# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class MetricasPortfolio:
    """Métricas consolidadas do portfólio"""
    valor_total: Decimal
    valor_investido: Decimal
    valor_disponivel: Decimal
    pnl_realizado: Decimal
    pnl_nao_realizado: Decimal
    pnl_total: Decimal
    percentual_retorno: Decimal
    num_posicoes: int
    diversificacao: float  # 0-1
    exposicao_por_setor: Dict[str, Decimal]
    exposicao_por_ativo: Dict[str, Decimal]
    risco_concentracao: float  # 0-1
    volatilidade_portfolio: float
    sharpe_ratio: float
    drawdown_atual: Decimal
    timestamp: datetime

@dataclass
class AlertaPortfolio:
    """Alerta do portfólio"""
    id: str
    tipo: TipoAlerta
    simbolo: str
    titulo: str
    descricao: str
    severidade: str  # baixa, media, alta, critica
    valor_atual: Decimal
    valor_limite: Decimal
    acao_sugerida: str
    timestamp: datetime
    ativo: bool = True

@dataclass
class AnaliseRisco:
    """Análise de risco do portfólio"""
    var_95: Decimal  # Value at Risk 95%
    var_99: Decimal  # Value at Risk 99%
    beta_portfolio: float
    correlacao_mercado: float
    concentracao_risco: float
    liquidez_score: float
    stress_test_resultados: Dict[str, Decimal]
    recomendacoes: List[str]
    timestamp: datetime

# =============================================================================
# MONITOR DE PORTFÓLIO
# =============================================================================

class MonitorPortfolio:
    """Monitor principal do portfólio em tempo real"""
    
    def __init__(self, gerenciador_corretoras: GerenciadorCorretoras):
        self.gerenciador_corretoras = gerenciador_corretoras
        self.logger = self._configurar_logging()
        self.ativo = False
        self.intervalo_atualizacao = 30  # segundos
        self.db_path = "data/monitor_portfolio.db"
        self.cache_dados_mercado: Dict[str, DadosMercado] = {}
        self.historico_metricas: List[MetricasPortfolio] = []
        self.alertas_ativos: Dict[str, AlertaPortfolio] = {}
        self.callbacks_alertas: List[Callable] = []
        self._inicializar_database()
        
        # Configurações de limites
        self.limite_concentracao = 0.20  # 20% max por ativo
        self.limite_perda_diaria = Decimal('-0.05')  # -5%
        self.limite_drawdown = Decimal('-0.15')  # -15%
        self.limite_volatilidade = 0.25  # 25%
        
    def _configurar_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger('monitor_portfolio')
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
        
        # Tabela de métricas históricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metricas_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valor_total REAL NOT NULL,
                valor_investido REAL NOT NULL,
                valor_disponivel REAL NOT NULL,
                pnl_realizado REAL NOT NULL,
                pnl_nao_realizado REAL NOT NULL,
                pnl_total REAL NOT NULL,
                percentual_retorno REAL NOT NULL,
                num_posicoes INTEGER NOT NULL,
                volatilidade_portfolio REAL,
                sharpe_ratio REAL,
                drawdown_atual REAL,
                timestamp TEXT NOT NULL,
                dados_json TEXT
            )
        ''')
        
        # Tabela de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                simbolo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                severidade TEXT NOT NULL,
                valor_atual REAL NOT NULL,
                valor_limite REAL NOT NULL,
                acao_sugerida TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ativo BOOLEAN NOT NULL
            )
        ''')
        
        # Tabela de análises de risco
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analises_risco (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                var_95 REAL NOT NULL,
                var_99 REAL NOT NULL,
                beta_portfolio REAL NOT NULL,
                correlacao_mercado REAL NOT NULL,
                concentracao_risco REAL NOT NULL,
                liquidez_score REAL NOT NULL,
                timestamp TEXT NOT NULL,
                dados_json TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def atualizar_dados_mercado(self, simbolos: List[str]):
        """Atualiza dados de mercado para os símbolos"""
        try:
            dados = await self.gerenciador_corretoras.conector_ativo.obter_dados_mercado(simbolos)
            self.cache_dados_mercado.update(dados)
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar dados de mercado: {e}")
            
    async def calcular_metricas_portfolio(self) -> Optional[MetricasPortfolio]:
        """Calcula métricas consolidadas do portfólio"""
        try:
            # Obter posições de todas as corretoras
            todas_posicoes = await self.gerenciador_corretoras.obter_posicoes_todas()
            todos_saldos = await self.gerenciador_corretoras.obter_saldos_todos()
            
            # Consolidar posições
            posicoes_consolidadas: Dict[str, PosicaoPortfolio] = {}
            for corretora, posicoes in todas_posicoes.items():
                for posicao in posicoes:
                    if posicao.simbolo in posicoes_consolidadas:
                        pos_existente = posicoes_consolidadas[posicao.simbolo]
                        # Somar quantidades e calcular preço médio ponderado
                        total_valor = (pos_existente.quantidade * pos_existente.preco_medio + 
                                     posicao.quantidade * posicao.preco_medio)
                        total_quantidade = pos_existente.quantidade + posicao.quantidade
                        
                        pos_existente.quantidade = total_quantidade
                        pos_existente.preco_medio = total_valor / total_quantidade if total_quantidade > 0 else Decimal('0')
                        pos_existente.valor_mercado += posicao.valor_mercado
                        pos_existente.pnl_realizado += posicao.pnl_realizado
                        pos_existente.pnl_nao_realizado += posicao.pnl_nao_realizado
                    else:
                        posicoes_consolidadas[posicao.simbolo] = posicao
                        
            # Consolidar saldos
            valor_total = sum(saldo.get('capital_total', Decimal('0')) for saldo in todos_saldos.values())
            valor_disponivel = sum(saldo.get('capital_disponivel', Decimal('0')) for saldo in todos_saldos.values())
            valor_investido = sum(saldo.get('capital_investido', Decimal('0')) for saldo in todos_saldos.values())
            pnl_total = sum(saldo.get('pnl_total', Decimal('0')) for saldo in todos_saldos.values())
            
            # Calcular métricas de diversificação
            exposicao_por_ativo = {}
            for simbolo, posicao in posicoes_consolidadas.items():
                if valor_total > 0:
                    exposicao_por_ativo[simbolo] = posicao.valor_mercado / valor_total
                else:
                    exposicao_por_ativo[simbolo] = Decimal('0')
                    
            # Risco de concentração (índice Herfindahl)
            concentracoes = [float(exp) for exp in exposicao_por_ativo.values()]
            risco_concentracao = sum(c**2 for c in concentracoes) if concentracoes else 0
            
            # Diversificação (1 - concentração)
            diversificacao = 1 - risco_concentracao
            
            # Calcular volatilidade do portfólio (simplificado)
            volatilidade_portfolio = self._calcular_volatilidade_portfolio(posicoes_consolidadas)
            
            # Calcular Sharpe ratio (simplificado)
            sharpe_ratio = self._calcular_sharpe_ratio(pnl_total, valor_total)
            
            # Calcular drawdown atual
            drawdown_atual = self._calcular_drawdown_atual()
            
            # Análise por setor (simplificado - usar primeiro caractere como setor)
            exposicao_por_setor = self._calcular_exposicao_setor(posicoes_consolidadas, valor_total)
            
            metricas = MetricasPortfolio(
                valor_total=valor_total,
                valor_investido=valor_investido,
                valor_disponivel=valor_disponivel,
                pnl_realizado=sum(p.pnl_realizado for p in posicoes_consolidadas.values()),
                pnl_nao_realizado=sum(p.pnl_nao_realizado for p in posicoes_consolidadas.values()),
                pnl_total=pnl_total,
                percentual_retorno=pnl_total / valor_total * 100 if valor_total > 0 else Decimal('0'),
                num_posicoes=len(posicoes_consolidadas),
                diversificacao=diversificacao,
                exposicao_por_setor=exposicao_por_setor,
                exposicao_por_ativo=exposicao_por_ativo,
                risco_concentracao=risco_concentracao,
                volatilidade_portfolio=volatilidade_portfolio,
                sharpe_ratio=sharpe_ratio,
                drawdown_atual=drawdown_atual,
                timestamp=datetime.now()
            )
            
            # Adicionar ao histórico
            self.historico_metricas.append(metricas)
            if len(self.historico_metricas) > 1000:  # Limitar histórico
                self.historico_metricas = self.historico_metricas[-1000:]
                
            # Salvar no database
            self._salvar_metricas(metricas)
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular métricas: {e}")
            return None
            
    def _calcular_volatilidade_portfolio(self, posicoes: Dict[str, PosicaoPortfolio]) -> float:
        """Calcula volatilidade do portfólio (simplificado)"""
        try:
            if not posicoes:
                return 0.0
                
            # Para simplicidade, usar média das volatilidades individuais
            # Em produção, deveria calcular matriz de covariância
            volatilidades = []
            
            for simbolo in posicoes.keys():
                try:
                    ticker = yf.Ticker(simbolo)
                    hist = ticker.history(period="30d")
                    if len(hist) > 5:
                        returns = hist['Close'].pct_change().dropna()
                        vol = returns.std() * np.sqrt(252)  # Anualizada
                        volatilidades.append(vol)
                except:
                    continue
                    
            return np.mean(volatilidades) if volatilidades else 0.0
            
        except Exception:
            return 0.0
            
    def _calcular_sharpe_ratio(self, pnl_total: Decimal, capital_total: Decimal) -> float:
        """Calcula Sharpe ratio simplificado"""
        try:
            if capital_total <= 0:
                return 0.0
                
            # Retorno anualizado (assumindo dados anuais)
            retorno = float(pnl_total / capital_total)
            
            # Taxa livre de risco (assumir 2% anual)
            taxa_livre_risco = 0.02
            
            # Volatilidade (usar histórico se disponível)
            if len(self.historico_metricas) > 30:
                retornos_hist = [float(m.percentual_retorno / 100) for m in self.historico_metricas[-30:]]
                volatilidade = np.std(retornos_hist) * np.sqrt(252) if retornos_hist else 0.1
            else:
                volatilidade = 0.1  # Assumir 10% se não houver histórico
                
            if volatilidade > 0:
                return (retorno - taxa_livre_risco) / volatilidade
            return 0.0
            
        except Exception:
            return 0.0
            
    def _calcular_drawdown_atual(self) -> Decimal:
        """Calcula drawdown atual"""
        try:
            if len(self.historico_metricas) < 2:
                return Decimal('0')
                
            # Encontrar pico máximo nos últimos 252 dias (1 ano)
            historico_recente = self.historico_metricas[-252:]
            valor_maximo = max(m.valor_total for m in historico_recente)
            valor_atual = self.historico_metricas[-1].valor_total
            
            if valor_maximo > 0:
                drawdown = (valor_atual - valor_maximo) / valor_maximo
                return drawdown
                
            return Decimal('0')
            
        except Exception:
            return Decimal('0')
            
    def _calcular_exposicao_setor(self, posicoes: Dict[str, PosicaoPortfolio], 
                                 valor_total: Decimal) -> Dict[str, Decimal]:
        """Calcula exposição por setor (simplificado)"""
        try:
            setores = {
                'A': 'Tech',      # AAPL, AMZN, etc
                'M': 'Tech',      # MSFT
                'G': 'Tech',      # GOOGL
                'T': 'Telecom',   # T
                'S': 'Financial', # SPY (diversificado)
                'Q': 'Tech',      # QQQ
                'I': 'Financial'  # IWM
            }
            
            exposicao_setor = {}
            
            for simbolo, posicao in posicoes.items():
                setor = setores.get(simbolo[0], 'Outros')
                if setor not in exposicao_setor:
                    exposicao_setor[setor] = Decimal('0')
                    
                if valor_total > 0:
                    exposicao_setor[setor] += posicao.valor_mercado / valor_total
                    
            return exposicao_setor
            
        except Exception:
            return {}
            
    async def verificar_alertas(self, metricas: MetricasPortfolio):
        """Verifica e gera alertas baseados nas métricas"""
        novos_alertas = []
        
        # Verificar concentração por ativo
        for simbolo, exposicao in metricas.exposicao_por_ativo.items():
            if exposicao > self.limite_concentracao:
                alerta_id = f"concentracao_{simbolo}"
                if alerta_id not in self.alertas_ativos:
                    alerta = AlertaPortfolio(
                        id=alerta_id,
                        tipo=TipoAlerta.LIMITE_RISCO,
                        simbolo=simbolo,
                        titulo=f"Alta Concentração em {simbolo}",
                        descricao=f"Exposição de {exposicao:.1%} excede limite de {self.limite_concentracao:.1%}",
                        severidade="media",
                        valor_atual=Decimal(str(exposicao)),
                        valor_limite=Decimal(str(self.limite_concentracao)),
                        acao_sugerida="Considere reduzir posição ou diversificar",
                        timestamp=datetime.now()
                    )
                    novos_alertas.append(alerta)
                    
        # Verificar drawdown
        if metricas.drawdown_atual < self.limite_drawdown:
            alerta_id = "drawdown_alto"
            if alerta_id not in self.alertas_ativos:
                alerta = AlertaPortfolio(
                    id=alerta_id,
                    tipo=TipoAlerta.LIMITE_RISCO,
                    simbolo="PORTFOLIO",
                    titulo="Drawdown Elevado",
                    descricao=f"Drawdown atual de {metricas.drawdown_atual:.1%} excede limite",
                    severidade="alta",
                    valor_atual=metricas.drawdown_atual,
                    valor_limite=self.limite_drawdown,
                    acao_sugerida="Revisar estratégias e considerar redução de risco",
                    timestamp=datetime.now()
                )
                novos_alertas.append(alerta)
                
        # Verificar volatilidade
        if metricas.volatilidade_portfolio > self.limite_volatilidade:
            alerta_id = "volatilidade_alta"
            if alerta_id not in self.alertas_ativos:
                alerta = AlertaPortfolio(
                    id=alerta_id,
                    tipo=TipoAlerta.VOLATILIDADE_ALTA,
                    simbolo="PORTFOLIO",
                    titulo="Volatilidade Elevada",
                    descricao=f"Volatilidade de {metricas.volatilidade_portfolio:.1%} acima do limite",
                    severidade="media",
                    valor_atual=Decimal(str(metricas.volatilidade_portfolio)),
                    valor_limite=Decimal(str(self.limite_volatilidade)),
                    acao_sugerida="Considere hedging ou redução de exposição",
                    timestamp=datetime.now()
                )
                novos_alertas.append(alerta)
                
        # Adicionar novos alertas
        for alerta in novos_alertas:
            self.alertas_ativos[alerta.id] = alerta
            self._salvar_alerta(alerta)
            self._notificar_alerta(alerta)
            
    def _notificar_alerta(self, alerta: AlertaPortfolio):
        """Notifica sobre um novo alerta"""
        self.logger.warning(f"🚨 {alerta.titulo}: {alerta.descricao}")
        
        # Chamar callbacks registrados
        for callback in self.callbacks_alertas:
            try:
                callback(alerta)
            except Exception as e:
                self.logger.error(f"❌ Erro em callback de alerta: {e}")
                
    def registrar_callback_alerta(self, callback: Callable):
        """Registra callback para notificações de alerta"""
        self.callbacks_alertas.append(callback)
        
    def _salvar_metricas(self, metricas: MetricasPortfolio):
        """Salva métricas no database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO metricas_portfolio (
                    valor_total, valor_investido, valor_disponivel, pnl_realizado,
                    pnl_nao_realizado, pnl_total, percentual_retorno, num_posicoes,
                    volatilidade_portfolio, sharpe_ratio, drawdown_atual, timestamp, dados_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                float(metricas.valor_total),
                float(metricas.valor_investido),
                float(metricas.valor_disponivel),
                float(metricas.pnl_realizado),
                float(metricas.pnl_nao_realizado),
                float(metricas.pnl_total),
                float(metricas.percentual_retorno),
                metricas.num_posicoes,
                metricas.volatilidade_portfolio,
                metricas.sharpe_ratio,
                float(metricas.drawdown_atual),
                metricas.timestamp.isoformat(),
                json.dumps(asdict(metricas), default=str)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar métricas: {e}")
            
    def _salvar_alerta(self, alerta: AlertaPortfolio):
        """Salva alerta no database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO alertas (
                    id, tipo, simbolo, titulo, descricao, severidade,
                    valor_atual, valor_limite, acao_sugerida, timestamp, ativo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alerta.id,
                alerta.tipo.value,
                alerta.simbolo,
                alerta.titulo,
                alerta.descricao,
                alerta.severidade,
                float(alerta.valor_atual),
                float(alerta.valor_limite),
                alerta.acao_sugerida,
                alerta.timestamp.isoformat(),
                alerta.ativo
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar alerta: {e}")
            
    async def executar_ciclo_monitoramento(self):
        """Executa um ciclo de monitoramento"""
        try:
            self.logger.info("🔄 Iniciando ciclo de monitoramento")
            
            # Calcular métricas atuais
            metricas = await self.calcular_metricas_portfolio()
            
            if metricas:
                # Verificar alertas
                await self.verificar_alertas(metricas)
                
                # Log das métricas principais
                self.logger.info(
                    f"📊 Portfolio: ${metricas.valor_total:,.2f} | "
                    f"P&L: {metricas.percentual_retorno:.2f}% | "
                    f"Posições: {metricas.num_posicoes} | "
                    f"Drawdown: {metricas.drawdown_atual:.2f}%"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Erro no ciclo de monitoramento: {e}")
            
    async def iniciar(self):
        """Inicia o monitor de portfólio"""
        self.ativo = True
        self.logger.info("🚀 Monitor de Portfólio iniciado")
        
        while self.ativo:
            try:
                await self.executar_ciclo_monitoramento()
                await asyncio.sleep(self.intervalo_atualizacao)
            except Exception as e:
                self.logger.error(f"❌ Erro no monitor: {e}")
                await asyncio.sleep(10)
                
    def parar(self):
        """Para o monitor de portfólio"""
        self.ativo = False
        self.logger.info("🛑 Monitor de Portfólio parado")
        
    def obter_status_sistema(self) -> Dict[str, Any]:
        """Obtém status do sistema de monitoramento"""
        ultima_metrica = self.historico_metricas[-1] if self.historico_metricas else None
        
        return {
            'ativo': self.ativo,
            'ultima_atualizacao': ultima_metrica.timestamp.isoformat() if ultima_metrica else None,
            'total_alertas_ativos': len([a for a in self.alertas_ativos.values() if a.ativo]),
            'valor_portfolio': float(ultima_metrica.valor_total) if ultima_metrica else 0,
            'pnl_total': float(ultima_metrica.pnl_total) if ultima_metrica else 0,
            'num_posicoes': ultima_metrica.num_posicoes if ultima_metrica else 0,
            'intervalo_atualizacao': self.intervalo_atualizacao,
            'timestamp': datetime.now().isoformat()
        }

# =============================================================================
# WEBAPP PARA VISUALIZAÇÃO (OPCIONAL)
# =============================================================================

class WebAppPortfolio:
    """Aplicação web para visualização do portfólio"""
    
    def __init__(self, monitor: MonitorPortfolio):
        self.monitor = monitor
        self.app = Flask(__name__)
        self._configurar_rotas()
        
    def _configurar_rotas(self):
        """Configura rotas da aplicação"""
        
        @self.app.route('/')
        def dashboard():
            """Dashboard principal"""
            return render_template('portfolio_dashboard.html')
            
        @self.app.route('/api/metricas')
        def api_metricas():
            """API para obter métricas atuais"""
            if self.monitor.historico_metricas:
                ultima = self.monitor.historico_metricas[-1]
                return jsonify(asdict(ultima))
            return jsonify({})
            
        @self.app.route('/api/alertas')
        def api_alertas():
            """API para obter alertas ativos"""
            alertas = [asdict(a) for a in self.monitor.alertas_ativos.values() if a.ativo]
            return jsonify(alertas)
            
        @self.app.route('/api/historico/<int:dias>')
        def api_historico(dias):
            """API para obter histórico de métricas"""
            agora = datetime.now()
            data_limite = agora - timedelta(days=dias)
            
            historico_filtrado = [
                asdict(m) for m in self.monitor.historico_metricas
                if m.timestamp >= data_limite
            ]
            
            return jsonify(historico_filtrado)
            
    def executar(self, host='localhost', port=5001, debug=False):
        """Executa a aplicação web"""
        self.app.run(host=host, port=port, debug=debug)

# =============================================================================
# FUNÇÃO DE TESTE E DEMONSTRAÇÃO
# =============================================================================

async def testar_monitor_portfolio():
    """Testa o sistema de monitor de portfólio"""
    print("📊 Testando Monitor de Portfólio")
    print("=" * 60)
    
    # Importar gerenciador de corretoras
    from integracao_corretoras import GerenciadorCorretoras
    
    # Inicializar componentes
    gerenciador_corretoras = GerenciadorCorretoras()
    await gerenciador_corretoras.inicializar_conectores()
    
    monitor = MonitorPortfolio(gerenciador_corretoras)
    
    # Executar um ciclo de monitoramento
    print("🔄 Executando ciclo de monitoramento...")
    await monitor.executar_ciclo_monitoramento()
    
    # Verificar métricas
    if monitor.historico_metricas:
        ultima_metrica = monitor.historico_metricas[-1]
        print(f"\n📊 Métricas do Portfólio:")
        print(f"  Valor Total: ${ultima_metrica.valor_total:,.2f}")
        print(f"  P&L Total: ${ultima_metrica.pnl_total:,.2f} ({ultima_metrica.percentual_retorno:.2f}%)")
        print(f"  Posições: {ultima_metrica.num_posicoes}")
        print(f"  Diversificação: {ultima_metrica.diversificacao:.2%}")
        print(f"  Volatilidade: {ultima_metrica.volatilidade_portfolio:.2%}")
        print(f"  Sharpe Ratio: {ultima_metrica.sharpe_ratio:.2f}")
        print(f"  Drawdown: {ultima_metrica.drawdown_atual:.2%}")
        
        # Exposição por ativo
        print(f"\n📈 Exposição por Ativo:")
        for simbolo, exposicao in ultima_metrica.exposicao_por_ativo.items():
            print(f"  {simbolo}: {exposicao:.1%}")
            
    # Verificar alertas
    alertas_ativos = [a for a in monitor.alertas_ativos.values() if a.ativo]
    print(f"\n🚨 Alertas Ativos: {len(alertas_ativos)}")
    for alerta in alertas_ativos:
        print(f"  - {alerta.titulo} ({alerta.severidade})")
        
    # Status do sistema
    status = monitor.obter_status_sistema()
    print(f"\n🎯 Status do Sistema:")
    print(f"  Ativo: {status['ativo']}")
    print(f"  Alertas: {status['total_alertas_ativos']}")
    print(f"  Intervalo: {status['intervalo_atualizacao']}s")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(testar_monitor_portfolio())