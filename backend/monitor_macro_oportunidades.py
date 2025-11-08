"""
Sistema de Monitoramento Macroeconômico e Identificação de Oportunidades
Engenheiro ML: Monitor integrado de tendências macro e níveis de preço para oportunidades reais

Funcionalidades Principais:
1. Monitoramento de tendências macroeconômicas (política fiscal, carry trade)
2. Coleta de indicadores econômicos em tempo real
3. Cruzamento com níveis de preço para identificar oportunidades
4. Sistema de alertas com scoring de probabilidade
5. Avaliação de assertividade de oportunidades passadas
6. Aprimoramento automático do modelo baseado em performance
"""

import pandas as pd
import numpy as np
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
import warnings
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
from dataclasses import dataclass
import time

# Importar sistemas já desenvolvidos
try:
    from .carregador_dados_historicos import CarregadorDadosHistoricos
    from .detector_niveis_criticos_ml import DetectorNiveisCriticosML
    from .validador_niveis_historicos import ValidadorNiveisHistoricos
except ImportError:
    from carregador_dados_historicos import CarregadorDadosHistoricos
    from detector_niveis_criticos_ml import DetectorNiveisCriticosML
    from validador_niveis_historicos import ValidadorNiveisHistoricos

warnings.filterwarnings('ignore')

@dataclass
class IndicadorMacro:
    """Classe para representar um indicador macroeconômico"""
    nome: str
    simbolo: str
    valor_atual: float
    valor_anterior: float
    variacao_pct: float
    timestamp: datetime
    fonte: str
    importancia: float  # 0-1, peso na análise
    tendencia: str  # 'alta', 'baixa', 'estavel'

@dataclass
class OportunidadeTrade:
    """Classe para representar uma oportunidade de trade"""
    ticker: str
    tipo_oportunidade: str  # 'entrada_suporte', 'entrada_resistencia', 'breakout', etc
    nivel_preco: float
    preco_atual: float
    distancia_nivel: float
    score_macro: float  # Score baseado em fatores macro (0-1)
    score_tecnico: float  # Score baseado em níveis técnicos (0-1)
    score_final: float  # Score combinado (0-1)
    fatores_macro: List[str]
    confluencias_tecnicas: List[str]
    stop_loss: float
    take_profit: List[float]  # Múltiplos alvos
    risco_recompensa: float
    timestamp_identificacao: datetime
    validade_horas: int
    status: str  # 'ativa', 'executada', 'expirada', 'invalidada'

class MonitorMacroOportunidades:
    """Sistema integrado de monitoramento macro e identificação de oportunidades"""

    def __init__(self):
        self.logger = self._configurar_logger()

        # Sistemas integrados
        self.carregador_dados = CarregadorDadosHistoricos()
        self.detector_niveis = DetectorNiveisCriticosML(self.carregador_dados)
        self.validador = ValidadorNiveisHistoricos(self.carregador_dados, self.detector_niveis)

        # Estrutura de dados
        self.base_dir = "data/macro_oportunidades"
        self.db_path = os.path.join(self.base_dir, "macro_oportunidades.db")
        self.alertas_dir = os.path.join(self.base_dir, "alertas")
        self.historico_dir = os.path.join(self.base_dir, "historico")

        # Criar diretórios
        for dir_path in [self.base_dir, self.alertas_dir, self.historico_dir]:
            os.makedirs(dir_path, exist_ok=True)

        self._inicializar_database()

        # Configurações do monitor
        self.config_macro = {
            'indicadores_importantes': [
                {'simbolo': '^VIX', 'nome': 'VIX (Volatilidade)', 'peso': 0.25, 'inversao': True},
                {'simbolo': '^TNX', 'nome': 'Treasury 10Y', 'peso': 0.20, 'inversao': False},
                {'simbolo': 'DX-Y.NYB', 'nome': 'Dólar Index', 'peso': 0.20, 'inversao': False},
                {'simbolo': 'GC=F', 'nome': 'Ouro', 'peso': 0.15, 'inversao': True},
                {'simbolo': '^GSPC', 'nome': 'S&P 500', 'peso': 0.10, 'inversao': False},
                {'simbolo': 'CL=F', 'nome': 'Petróleo', 'peso': 0.10, 'inversao': False}
            ],
            'carry_trade_pares': [
                {'par': 'JPYUSD=X', 'carry_rate': 0.02, 'peso': 0.3},
                {'par': 'CHFUSD=X', 'carry_rate': 0.015, 'peso': 0.25},
                {'par': 'EURUSD=X', 'carry_rate': 0.035, 'peso': 0.25},
                {'par': 'GBPUSD=X', 'carry_rate': 0.045, 'peso': 0.2}
            ],
            'thresholds_oportunidade': {
                'score_minimo': 0.65,
                'distancia_nivel_max': 0.02,  # 2% máximo do nível
                'risco_recompensa_min': 1.5,
                'confluencias_min': 2
            }
        }

        # Cache de indicadores
        self.cache_indicadores = {}
        self.ultima_atualizacao_cache = None

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('MonitorMacroOportunidades')
        logger.setLevel(logging.INFO)
        return logger

    def _inicializar_database(self):
        """Inicializar estrutura do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabela de indicadores macroeconômicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicadores_macro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                simbolo TEXT NOT NULL,
                valor_atual REAL NOT NULL,
                valor_anterior REAL,
                variacao_pct REAL NOT NULL,
                tendencia TEXT NOT NULL,
                importancia REAL NOT NULL,
                fonte TEXT NOT NULL,
                timestamp_coleta DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de oportunidades identificadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS oportunidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                tipo_oportunidade TEXT NOT NULL,
                nivel_preco REAL NOT NULL,
                preco_atual REAL NOT NULL,
                distancia_nivel REAL NOT NULL,
                score_macro REAL NOT NULL,
                score_tecnico REAL NOT NULL,
                score_final REAL NOT NULL,
                fatores_macro TEXT NOT NULL,
                confluencias_tecnicas TEXT NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit TEXT NOT NULL,
                risco_recompensa REAL NOT NULL,
                validade_horas INTEGER NOT NULL,
                status TEXT DEFAULT 'ativa',
                timestamp_identificacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                timestamp_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de avaliação de assertividade
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS avaliacoes_assertividade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oportunidade_id INTEGER NOT NULL,
                resultado TEXT NOT NULL,
                preco_execucao REAL,
                preco_fechamento REAL,
                retorno_pct REAL,
                tempo_execucao_horas REAL,
                fatores_sucesso TEXT,
                fatores_fracasso TEXT,
                timestamp_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (oportunidade_id) REFERENCES oportunidades(id)
            )
        ''')

        # Tabela de aprendizado do modelo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modelo_aprendizado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fator_modelo TEXT NOT NULL,
                peso_anterior REAL NOT NULL,
                peso_novo REAL NOT NULL,
                motivo_ajuste TEXT NOT NULL,
                performance_anterior REAL,
                performance_nova REAL,
                timestamp_ajuste DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oportunidades_ticker ON oportunidades(ticker, timestamp_identificacao)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oportunidades_status ON oportunidades(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicadores_simbolo ON indicadores_macro(simbolo, timestamp_coleta)')

        conn.commit()
        conn.close()

    def coletar_indicadores_macro(self) -> Dict[str, IndicadorMacro]:
        """Coletar indicadores macroeconômicos em tempo real"""

        # Verificar cache (atualizar a cada 15 minutos)
        agora = datetime.now()
        if (self.ultima_atualizacao_cache and
            (agora - self.ultima_atualizacao_cache).seconds < 900):
            return self.cache_indicadores

        self.logger.info("🌐 Coletando indicadores macroeconômicos")

        indicadores = {}

        # Processar cada indicador configurado
        for config_ind in self.config_macro['indicadores_importantes']:
            try:
                ticker = yf.Ticker(config_ind['simbolo'])
                dados = ticker.history(period="5d", interval="1d")

                if not dados.empty:
                    valor_atual = float(dados['Close'].iloc[-1])
                    valor_anterior = float(dados['Close'].iloc[-2]) if len(dados) > 1 else valor_atual

                    variacao_pct = ((valor_atual - valor_anterior) / valor_anterior) * 100

                    # Determinar tendência
                    if variacao_pct > 0.5:
                        tendencia = 'alta'
                    elif variacao_pct < -0.5:
                        tendencia = 'baixa'
                    else:
                        tendencia = 'estavel'

                    indicador = IndicadorMacro(
                        nome=config_ind['nome'],
                        simbolo=config_ind['simbolo'],
                        valor_atual=valor_atual,
                        valor_anterior=valor_anterior,
                        variacao_pct=variacao_pct,
                        timestamp=agora,
                        fonte='yfinance',
                        importancia=config_ind['peso'],
                        tendencia=tendencia
                    )

                    indicadores[config_ind['simbolo']] = indicador

                    self.logger.info(f"✅ {config_ind['nome']}: {valor_atual:.2f} ({variacao_pct:+.2f}%)")

            except Exception as e:
                self.logger.warning(f"⚠️ Erro coletando {config_ind['simbolo']}: {e}")
                continue

        # Salvar no banco de dados
        self._salvar_indicadores_macro(indicadores)

        # Atualizar cache
        self.cache_indicadores = indicadores
        self.ultima_atualizacao_cache = agora

        return indicadores

    def _salvar_indicadores_macro(self, indicadores: Dict[str, IndicadorMacro]):
        """Salvar indicadores no banco de dados"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for indicador in indicadores.values():
                cursor.execute('''
                    INSERT INTO indicadores_macro
                    (nome, simbolo, valor_atual, valor_anterior, variacao_pct,
                     tendencia, importancia, fonte)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    indicador.nome, indicador.simbolo, indicador.valor_atual,
                    indicador.valor_anterior, indicador.variacao_pct,
                    indicador.tendencia, indicador.importancia, indicador.fonte
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"❌ Erro salvando indicadores macro: {e}")

    def analisar_ambiente_macro(self, indicadores: Dict[str, IndicadorMacro]) -> Dict:
        """Analisar ambiente macroeconômico e gerar score"""

        if not indicadores:
            return {'score_macro': 0.5, 'ambiente': 'neutro', 'fatores': []}

        self.logger.info("📊 Analisando ambiente macroeconômico")

        # Calcular scores por categoria
        score_volatilidade = self._calcular_score_volatilidade(indicadores)
        score_juros = self._calcular_score_juros(indicadores)
        score_moeda = self._calcular_score_moeda(indicadores)
        score_commodities = self._calcular_score_commodities(indicadores)
        score_equity = self._calcular_score_equity(indicadores)

        # Score macro consolidado (média ponderada)
        pesos = {'volatilidade': 0.25, 'juros': 0.25, 'moeda': 0.2, 'commodities': 0.15, 'equity': 0.15}

        score_macro = (
            score_volatilidade * pesos['volatilidade'] +
            score_juros * pesos['juros'] +
            score_moeda * pesos['moeda'] +
            score_commodities * pesos['commodities'] +
            score_equity * pesos['equity']
        )

        # Determinar ambiente
        if score_macro >= 0.7:
            ambiente = 'otimista'
        elif score_macro >= 0.4:
            ambiente = 'neutro'
        else:
            ambiente = 'pessimista'

        # Identificar fatores principais
        fatores = self._identificar_fatores_macro(indicadores, score_macro)

        return {
            'score_macro': round(score_macro, 4),
            'ambiente': ambiente,
            'fatores': fatores,
            'scores_componentes': {
                'volatilidade': round(score_volatilidade, 4),
                'juros': round(score_juros, 4),
                'moeda': round(score_moeda, 4),
                'commodities': round(score_commodities, 4),
                'equity': round(score_equity, 4)
            }
        }

    def _calcular_score_volatilidade(self, indicadores: Dict[str, IndicadorMacro]) -> float:
        """Calcular score baseado em volatilidade (VIX)"""

        vix = indicadores.get('^VIX')
        if not vix:
            return 0.5

        # VIX baixo = ambiente favorável (score alto)
        # VIX > 30 = alto medo, VIX < 15 = baixo medo
        if vix.valor_atual < 15:
            return 0.8  # Volatilidade baixa = bom
        elif vix.valor_atual < 20:
            return 0.6
        elif vix.valor_atual < 30:
            return 0.4
        else:
            return 0.2  # Volatilidade alta = ruim

    def _calcular_score_juros(self, indicadores: Dict[str, IndicadorMacro]) -> float:
        """Calcular score baseado em taxa de juros (Treasury 10Y)"""

        treasury = indicadores.get('^TNX')
        if not treasury:
            return 0.5

        # Analisar tendência dos juros
        if treasury.tendencia == 'baixa':
            return 0.7  # Juros caindo = favorável para ativos
        elif treasury.tendencia == 'estavel':
            return 0.5  # Estável = neutro
        else:
            return 0.3  # Juros subindo = desfavorável

    def _calcular_score_moeda(self, indicadores: Dict[str, IndicadorMacro]) -> float:
        """Calcular score baseado em USD (DXY)"""

        dxy = indicadores.get('DX-Y.NYB')
        if not dxy:
            return 0.5

        # USD forte demais pode prejudicar emergentes e commodities
        if dxy.valor_atual > 105:
            return 0.3 if dxy.tendencia == 'alta' else 0.4
        elif dxy.valor_atual < 95:
            return 0.7 if dxy.tendencia == 'baixa' else 0.6
        else:
            return 0.5

    def _calcular_score_commodities(self, indicadores: Dict[str, IndicadorMacro]) -> float:
        """Calcular score baseado em commodities (Ouro, Petróleo)"""

        ouro = indicadores.get('GC=F')
        petroleo = indicadores.get('CL=F')

        scores = []

        if ouro:
            # Ouro subindo pode indicar aversão ao risco
            if ouro.tendencia == 'alta':
                scores.append(0.4)  # Aversão ao risco
            else:
                scores.append(0.6)  # Apetite por risco

        if petroleo:
            # Petróleo subindo moderadamente = economia saudável
            if petroleo.variacao_pct > 2:
                scores.append(0.4)  # Subida excessiva = inflação
            elif petroleo.variacao_pct < -2:
                scores.append(0.3)  # Queda excessiva = recessão
            else:
                scores.append(0.7)  # Estabilidade = saudável

        return np.mean(scores) if scores else 0.5

    def _calcular_score_equity(self, indicadores: Dict[str, IndicadorMacro]) -> float:
        """Calcular score baseado em índices de ações (S&P 500)"""

        sp500 = indicadores.get('^GSPC')
        if not sp500:
            return 0.5

        # Tendência de alta = ambiente favorável
        if sp500.tendencia == 'alta' and sp500.variacao_pct > 0.5:
            return 0.8
        elif sp500.tendencia == 'baixa' and sp500.variacao_pct < -1:
            return 0.2
        else:
            return 0.5

    def _identificar_fatores_macro(self, indicadores: Dict[str, IndicadorMacro], score_macro: float) -> List[str]:
        """Identificar principais fatores que influenciam o ambiente macro"""

        fatores = []

        # Analisar cada indicador
        for indicador in indicadores.values():
            if abs(indicador.variacao_pct) > 1:  # Variações significativas
                if indicador.variacao_pct > 0:
                    fatores.append(f"{indicador.nome} em alta (+{indicador.variacao_pct:.1f}%)")
                else:
                    fatores.append(f"{indicador.nome} em baixa ({indicador.variacao_pct:.1f}%)")

        # Fatores baseados no score geral
        if score_macro > 0.7:
            fatores.append("Ambiente macro favorável para risco")
        elif score_macro < 0.3:
            fatores.append("Ambiente macro de aversão ao risco")

        return fatores[:5]  # Máximo 5 fatores principais

    def identificar_oportunidades_portfolio(self, tickers: List[str]) -> List[OportunidadeTrade]:
        """Identificar oportunidades cruzando macro com níveis técnicos"""

        self.logger.info(f"🔍 Identificando oportunidades para {len(tickers)} ativos")

        # Coletar dados macro
        indicadores_macro = self.coletar_indicadores_macro()
        analise_macro = self.analisar_ambiente_macro(indicadores_macro)

        oportunidades = []

        # Processar cada ticker
        for ticker in tickers:
            try:
                oportunidades_ticker = self._analisar_oportunidades_ticker(
                    ticker, analise_macro, indicadores_macro
                )
                oportunidades.extend(oportunidades_ticker)

            except Exception as e:
                self.logger.warning(f"⚠️ Erro analisando {ticker}: {e}")
                continue

        # Filtrar oportunidades por qualidade
        oportunidades_qualificadas = self._filtrar_oportunidades(oportunidades)

        # Salvar no banco
        self._salvar_oportunidades(oportunidades_qualificadas)

        self.logger.info(f"✅ Identificadas {len(oportunidades_qualificadas)} oportunidades qualificadas")

        return oportunidades_qualificadas

    def _analisar_oportunidades_ticker(self, ticker: str, analise_macro: Dict,
                                     indicadores_macro: Dict[str, IndicadorMacro]) -> List[OportunidadeTrade]:
        """Analisar oportunidades para um ticker específico"""

        oportunidades = []

        # Obter preço atual
        try:
            ativo = yf.Ticker(ticker)
            hist_recente = ativo.history(period="2d")

            if hist_recente.empty:
                return oportunidades

            preco_atual = float(hist_recente['Close'].iloc[-1])

        except Exception as e:
            self.logger.warning(f"❌ Erro obtendo preço de {ticker}: {e}")
            return oportunidades

        # Obter níveis técnicos do nosso sistema
        try:
            resultado_niveis = self.detector_niveis.processar_ativo_ml_completo(ticker, "6mo")

            if not resultado_niveis or 'analise_consolidada' not in resultado_niveis:
                return oportunidades

            analise_consolidada = resultado_niveis['analise_consolidada']

        except Exception as e:
            self.logger.warning(f"❌ Erro obtendo níveis de {ticker}: {e}")
            return oportunidades

        # Analisar suportes próximos
        for suporte in analise_consolidada.get('suportes_criticos', []):
            oportunidade = self._avaliar_oportunidade_suporte(
                ticker, suporte, preco_atual, analise_macro, indicadores_macro
            )
            if oportunidade:
                oportunidades.append(oportunidade)

        # Analisar resistências próximas
        for resistencia in analise_consolidada.get('resistencias_criticas', []):
            oportunidade = self._avaliar_oportunidade_resistencia(
                ticker, resistencia, preco_atual, analise_macro, indicadores_macro
            )
            if oportunidade:
                oportunidades.append(oportunidade)

        return oportunidades

    def _avaliar_oportunidade_suporte(self, ticker: str, suporte: Dict, preco_atual: float,
                                     analise_macro: Dict, indicadores_macro: Dict) -> Optional[OportunidadeTrade]:
        """Avaliar oportunidade de entrada em suporte"""

        nivel_preco = suporte['nivel']
        distancia_nivel = abs(preco_atual - nivel_preco) / preco_atual

        # Verificar se preço está próximo do suporte (dentro de 2%)
        if distancia_nivel > 0.02 or preco_atual > nivel_preco * 1.01:
            return None

        # Score técnico baseado no detector de níveis
        score_tecnico = suporte.get('score_final', 0.5)

        # Score macro
        score_macro = analise_macro['score_macro']

        # Score combinado (60% macro, 40% técnico para suportes)
        score_final = (score_macro * 0.6) + (score_tecnico * 0.4)

        # Calcular stop loss e take profit
        stop_loss = nivel_preco * 0.98  # 2% abaixo do suporte
        take_profit = [
            nivel_preco * 1.02,  # TP1: 2%
            nivel_preco * 1.04,  # TP2: 4%
            nivel_preco * 1.06   # TP3: 6%
        ]

        risco_recompensa = (take_profit[0] - preco_atual) / (preco_atual - stop_loss)

        # Confluências técnicas
        confluencias = [f"Score técnico: {score_tecnico:.2f}"]
        if suporte.get('confluencia', 0) > 1:
            confluencias.append(f"Confluência {suporte['confluencia']} timeframes")

        # Fatores macro positivos
        fatores_macro = []
        if score_macro > 0.6:
            fatores_macro.extend(analise_macro['fatores'])

        return OportunidadeTrade(
            ticker=ticker,
            tipo_oportunidade='entrada_suporte',
            nivel_preco=nivel_preco,
            preco_atual=preco_atual,
            distancia_nivel=distancia_nivel,
            score_macro=score_macro,
            score_tecnico=score_tecnico,
            score_final=score_final,
            fatores_macro=fatores_macro,
            confluencias_tecnicas=confluencias,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risco_recompensa=risco_recompensa,
            timestamp_identificacao=datetime.now(),
            validade_horas=24,  # Válida por 24h
            status='ativa'
        )

    def _avaliar_oportunidade_resistencia(self, ticker: str, resistencia: Dict, preco_atual: float,
                                        analise_macro: Dict, indicadores_macro: Dict) -> Optional[OportunidadeTrade]:
        """Avaliar oportunidade de entrada em resistência (short ou breakout)"""

        nivel_preco = resistencia['nivel']
        distancia_nivel = abs(preco_atual - nivel_preco) / preco_atual

        # Verificar se preço está próximo da resistência
        if distancia_nivel > 0.02:
            return None

        score_tecnico = resistencia.get('score_final', 0.5)
        score_macro = analise_macro['score_macro']

        # Decidir tipo de oportunidade baseado no ambiente macro
        if score_macro > 0.65:  # Ambiente otimista = buscar breakout
            tipo_oportunidade = 'breakout_resistencia'
            score_final = (score_macro * 0.7) + (score_tecnico * 0.3)  # Mais peso no macro

            # Setup para breakout
            stop_loss = nivel_preco * 0.98
            take_profit = [nivel_preco * 1.03, nivel_preco * 1.06, nivel_preco * 1.10]

        else:  # Ambiente neutro/pessimista = resistência pode segurar
            tipo_oportunidade = 'rejeicao_resistencia'
            score_final = (score_macro * 0.4) + (score_tecnico * 0.6)  # Mais peso no técnico

            # Setup para rejeição (short)
            stop_loss = nivel_preco * 1.02
            take_profit = [nivel_preco * 0.98, nivel_preco * 0.95, nivel_preco * 0.92]

        risco_recompensa = abs(take_profit[0] - preco_atual) / abs(preco_atual - stop_loss)

        confluencias = [f"Score técnico: {score_tecnico:.2f}"]
        if resistencia.get('confluencia', 0) > 1:
            confluencias.append(f"Confluência {resistencia['confluencia']} timeframes")

        fatores_macro = analise_macro['fatores']

        return OportunidadeTrade(
            ticker=ticker,
            tipo_oportunidade=tipo_oportunidade,
            nivel_preco=nivel_preco,
            preco_atual=preco_atual,
            distancia_nivel=distancia_nivel,
            score_macro=score_macro,
            score_tecnico=score_tecnico,
            score_final=score_final,
            fatores_macro=fatores_macro,
            confluencias_tecnicas=confluencias,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risco_recompensa=risco_recompensa,
            timestamp_identificacao=datetime.now(),
            validade_horas=24,
            status='ativa'
        )

    def _filtrar_oportunidades(self, oportunidades: List[OportunidadeTrade]) -> List[OportunidadeTrade]:
        """Filtrar oportunidades por critérios de qualidade"""

        thresholds = self.config_macro['thresholds_oportunidade']
        oportunidades_qualificadas = []

        for oportunidade in oportunidades:
            # Critérios de filtragem
            if (oportunidade.score_final >= thresholds['score_minimo'] and
                oportunidade.distancia_nivel <= thresholds['distancia_nivel_max'] and
                oportunidade.risco_recompensa >= thresholds['risco_recompensa_min'] and
                len(oportunidade.confluencias_tecnicas) >= thresholds['confluencias_min']):

                oportunidades_qualificadas.append(oportunidade)

        # Ordenar por score final (melhores primeiro)
        oportunidades_qualificadas.sort(key=lambda x: x.score_final, reverse=True)

        return oportunidades_qualificadas

    def _salvar_oportunidades(self, oportunidades: List[OportunidadeTrade]):
        """Salvar oportunidades no banco de dados"""

        if not oportunidades:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for oportunidade in oportunidades:
                cursor.execute('''
                    INSERT INTO oportunidades
                    (ticker, tipo_oportunidade, nivel_preco, preco_atual, distancia_nivel,
                     score_macro, score_tecnico, score_final, fatores_macro, confluencias_tecnicas,
                     stop_loss, take_profit, risco_recompensa, validade_horas, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    oportunidade.ticker,
                    oportunidade.tipo_oportunidade,
                    oportunidade.nivel_preco,
                    oportunidade.preco_atual,
                    oportunidade.distancia_nivel,
                    oportunidade.score_macro,
                    oportunidade.score_tecnico,
                    oportunidade.score_final,
                    json.dumps(oportunidade.fatores_macro),
                    json.dumps(oportunidade.confluencias_tecnicas),
                    oportunidade.stop_loss,
                    json.dumps(oportunidade.take_profit),
                    oportunidade.risco_recompensa,
                    oportunidade.validade_horas,
                    oportunidade.status
                ))

            conn.commit()
            conn.close()

            self.logger.info(f"✅ {len(oportunidades)} oportunidades salvas no banco")

        except Exception as e:
            self.logger.error(f"❌ Erro salvando oportunidades: {e}")

    def gerar_alertas_oportunidades(self, oportunidades: List[OportunidadeTrade]) -> str:
        """Gerar relatório de alertas de oportunidades"""

        if not oportunidades:
            return "📊 Nenhuma oportunidade identificada no momento."

        relatorio = []
        relatorio.append("🚨 ALERTAS DE OPORTUNIDADES - ANÁLISE MACRO + TÉCNICA")
        relatorio.append("=" * 65)

        relatorio.append(f"\n🎯 RESUMO:")
        relatorio.append(f"   Total de oportunidades: {len(oportunidades)}")

        # Agrupar por tipo
        tipos = {}
        for op in oportunidades:
            if op.tipo_oportunidade not in tipos:
                tipos[op.tipo_oportunidade] = []
            tipos[op.tipo_oportunidade].append(op)

        for tipo, ops in tipos.items():
            relatorio.append(f"   {tipo.replace('_', ' ').title()}: {len(ops)}")

        relatorio.append(f"\n🔥 TOP OPORTUNIDADES:")
        relatorio.append("-" * 45)

        # Mostrar top 5 oportunidades
        for i, oportunidade in enumerate(oportunidades[:5], 1):
            emoji_tipo = {
                'entrada_suporte': '📈',
                'breakout_resistencia': '🚀',
                'rejeicao_resistencia': '📉'
            }.get(oportunidade.tipo_oportunidade, '💹')

            relatorio.append(f"\n{emoji_tipo} {i}. {oportunidade.ticker} - {oportunidade.tipo_oportunidade.upper()}")
            relatorio.append(f"   💰 Preço atual: ${oportunidade.preco_atual:.2f}")
            relatorio.append(f"   🎯 Nível: ${oportunidade.nivel_preco:.2f}")
            relatorio.append(f"   📊 Score Final: {oportunidade.score_final:.1%}")
            relatorio.append(f"   ⚖️ R/R: {oportunidade.risco_recompensa:.1f}")
            relatorio.append(f"   🛑 Stop Loss: ${oportunidade.stop_loss:.2f}")
            relatorio.append(f"   🎁 Take Profit: ${oportunidade.take_profit[0]:.2f}")

            if oportunidade.fatores_macro:
                relatorio.append(f"   🌐 Fatores Macro: {', '.join(oportunidade.fatores_macro[:2])}")

        relatorio.append(f"\n📊 ANÁLISE DE SCORING:")
        score_medio = np.mean([op.score_final for op in oportunidades])
        rr_medio = np.mean([op.risco_recompensa for op in oportunidades])

        relatorio.append(f"   Score médio: {score_medio:.1%}")
        relatorio.append(f"   R/R médio: {rr_medio:.1f}")

        relatorio.append(f"\n⚠️ IMPORTANTE:")
        relatorio.append(f"   • Sempre usar stop loss definido")
        relatorio.append(f"   • Monitorar ambiente macro continuamente")
        relatorio.append(f"   • Oportunidades válidas por 24h")
        relatorio.append(f"   • Considerar gestão de risco do portfolio")

        return "\n".join(relatorio)


def main():
    """Demonstração do sistema de monitoramento macro e oportunidades"""

    print("🌐 SISTEMA DE MONITORAMENTO MACRO E OPORTUNIDADES")
    print("=" * 65)

    # Portfolio de teste
    portfolio_teste = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']

    # Inicializar sistema
    monitor = MonitorMacroOportunidades()

    print(f"\n🔄 Coletando dados macro e analisando oportunidades...")
    print(f"📊 Portfolio: {', '.join(portfolio_teste)}")

    # Identificar oportunidades
    oportunidades = monitor.identificar_oportunidades_portfolio(portfolio_teste)

    # Gerar alertas
    relatorio_alertas = monitor.gerar_alertas_oportunidades(oportunidades)
    print(f"\n{relatorio_alertas}")

    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/macro_oportunidades/alertas/alertas_{timestamp}.txt"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(relatorio_alertas)

    print(f"\n✅ Relatório de alertas salvo: {output_path}")

    return monitor, oportunidades


if __name__ == "__main__":
    monitor, oportunidades = main()