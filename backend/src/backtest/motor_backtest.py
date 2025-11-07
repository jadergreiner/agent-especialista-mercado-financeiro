"""
Sistema de Backtesting para o Agente Especialista de Mercado Financeiro.

Este módulo implementa estratégias de trading e simula recomendações usando dados históricos,
validando automaticamente os resultados e calculando métricas de performance.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import sqlite3

# Garantir que possamos importar módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.persistencia.recomendacoes import (
    salvar_recomendacao,
    registrar_resultado,
    calcular_metricas_detalhadas,
)


@dataclass
class SinalTecnico:
    """Representa um sinal técnico calculado."""
    data: str
    tipo: str  # 'COMPRA', 'VENDA', 'NEUTRO'
    preco_entrada: float
    stop_loss: float
    take_profit: float
    confianca: float  # 0.0 a 1.0
    indicadores: dict  # Valores dos indicadores técnicos
    razao: str  # Explicação do sinal


class CalculadorIndicadores:
    """Calcula indicadores técnicos a partir de dados históricos."""

    @staticmethod
    def media_movel_simples(precos: List[float], periodo: int) -> Optional[float]:
        """Calcula média móvel simples."""
        if len(precos) < periodo:
            return None
        return sum(precos[-periodo:]) / periodo

    @staticmethod
    def media_movel_exponencial(precos: List[float], periodo: int) -> Optional[float]:
        """Calcula média móvel exponencial."""
        if len(precos) < periodo:
            return None

        multiplicador = 2 / (periodo + 1)
        ema = precos[0]

        for preco in precos[1:]:
            ema = (preco * multiplicador) + (ema * (1 - multiplicador))

        return ema

    @staticmethod
    def rsi(precos: List[float], periodo: int = 14) -> Optional[float]:
        """Calcula Relative Strength Index (RSI)."""
        if len(precos) < periodo + 1:
            return None

        ganhos = []
        perdas = []

        for i in range(1, len(precos)):
            mudanca = precos[i] - precos[i-1]
            if mudanca > 0:
                ganhos.append(mudanca)
                perdas.append(0)
            else:
                ganhos.append(0)
                perdas.append(abs(mudanca))

        ganho_medio = sum(ganhos[-periodo:]) / periodo
        perda_media = sum(perdas[-periodo:]) / periodo

        if perda_media == 0:
            return 100

        rs = ganho_medio / perda_media
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def bollinger_bands(precos: List[float], periodo: int = 20, num_std: float = 2.0) -> Optional[Tuple[float, float, float]]:
        """Calcula Bandas de Bollinger (superior, média, inferior)."""
        if len(precos) < periodo:
            return None

        ultimos = precos[-periodo:]
        media = sum(ultimos) / periodo
        variancia = sum((x - media) ** 2 for x in ultimos) / periodo
        desvio_padrao = variancia ** 0.5

        banda_superior = media + (num_std * desvio_padrao)
        banda_inferior = media - (num_std * desvio_padrao)

        return (banda_superior, media, banda_inferior)

    @staticmethod
    def atr(dados: List[dict], periodo: int = 14) -> Optional[float]:
        """Calcula Average True Range (ATR)."""
        if len(dados) < periodo + 1:
            return None

        true_ranges = []
        for i in range(1, len(dados)):
            high = dados[i]['maxima']
            low = dados[i]['minima']
            prev_close = dados[i-1]['ultimo']

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)

        return sum(true_ranges[-periodo:]) / periodo


class EstrategiaCruzamentoMedias:
    """Estratégia baseada em cruzamento de médias móveis."""

    def __init__(self, periodo_curto: int = 9, periodo_longo: int = 21):
        self.periodo_curto = periodo_curto
        self.periodo_longo = periodo_longo
        self.nome = f"Cruzamento MA{periodo_curto}/{periodo_longo}"

    def gerar_sinal(self, dados_historicos: List[dict]) -> Optional[SinalTecnico]:
        """Gera sinal de trading baseado em cruzamento de médias."""
        if len(dados_historicos) < self.periodo_longo + 1:
            return None

        precos = [d['ultimo'] for d in dados_historicos]

        # Calcular médias atuais e anteriores
        ma_curta_atual = CalculadorIndicadores.media_movel_simples(precos, self.periodo_curto)
        ma_longa_atual = CalculadorIndicadores.media_movel_simples(precos, self.periodo_longo)

        ma_curta_anterior = CalculadorIndicadores.media_movel_simples(precos[:-1], self.periodo_curto)
        ma_longa_anterior = CalculadorIndicadores.media_movel_simples(precos[:-1], self.periodo_longo)

        if None in [ma_curta_atual, ma_longa_atual, ma_curta_anterior, ma_longa_anterior]:
            return None

        dado_atual = dados_historicos[-1]
        preco_atual = dado_atual['ultimo']

        # Calcular ATR para stop loss e take profit
        atr = CalculadorIndicadores.atr(dados_historicos, 14)
        if atr is None:
            atr = preco_atual * 0.02  # 2% como fallback

        # Detectar cruzamento
        cruzamento_alta = ma_curta_anterior <= ma_longa_anterior and ma_curta_atual > ma_longa_atual
        cruzamento_baixa = ma_curta_anterior >= ma_longa_anterior and ma_curta_atual < ma_longa_atual

        # Calcular RSI para confirmar
        rsi = CalculadorIndicadores.rsi(precos, 14) or 50

        # Gerar sinal
        if cruzamento_alta and rsi < 70:
            # Sinal de COMPRA
            distancia_percentual = ((ma_curta_atual - ma_longa_atual) / ma_longa_atual) * 100
            confianca = min(0.5 + (distancia_percentual / 2), 0.95)

            return SinalTecnico(
                data=dado_atual['data'],
                tipo='COMPRA',
                preco_entrada=preco_atual,
                stop_loss=preco_atual - (atr * 2),
                take_profit=preco_atual + (atr * 3),
                confianca=confianca,
                indicadores={
                    'ma_curta': ma_curta_atual,
                    'ma_longa': ma_longa_atual,
                    'rsi': rsi,
                    'atr': atr,
                },
                razao=f"Cruzamento de alta: MA{self.periodo_curto} ({ma_curta_atual:.2f}) cruzou acima MA{self.periodo_longo} ({ma_longa_atual:.2f}). RSI em {rsi:.1f}."
            )

        elif cruzamento_baixa and rsi > 30:
            # Sinal de VENDA
            distancia_percentual = ((ma_longa_atual - ma_curta_atual) / ma_longa_atual) * 100
            confianca = min(0.5 + (distancia_percentual / 2), 0.95)

            return SinalTecnico(
                data=dado_atual['data'],
                tipo='VENDA',
                preco_entrada=preco_atual,
                stop_loss=preco_atual + (atr * 2),
                take_profit=preco_atual - (atr * 3),
                confianca=confianca,
                indicadores={
                    'ma_curta': ma_curta_atual,
                    'ma_longa': ma_longa_atual,
                    'rsi': rsi,
                    'atr': atr,
                },
                razao=f"Cruzamento de baixa: MA{self.periodo_curto} ({ma_curta_atual:.2f}) cruzou abaixo MA{self.periodo_longo} ({ma_longa_atual:.2f}). RSI em {rsi:.1f}."
            )

        return None


class EstrategiaRSI:
    """Estratégia baseada em RSI (Relative Strength Index) - sobrecompra/sobrevenda."""

    def __init__(self, periodo_rsi: int = 14, nivel_sobrecompra: float = 70, nivel_sobrevenda: float = 30):
        self.periodo_rsi = periodo_rsi
        self.nivel_sobrecompra = nivel_sobrecompra
        self.nivel_sobrevenda = nivel_sobrevenda
        self.nome = f"RSI {periodo_rsi} ({nivel_sobrevenda}/{nivel_sobrecompra})"

    def gerar_sinal(self, dados_historicos: List[dict]) -> Optional[SinalTecnico]:
        """Gera sinal baseado em níveis de RSI."""
        if len(dados_historicos) < self.periodo_rsi + 2:
            return None

        precos = [d['ultimo'] for d in dados_historicos]

        # Calcular RSI atual e anterior
        rsi_atual = CalculadorIndicadores.rsi(precos, self.periodo_rsi)
        rsi_anterior = CalculadorIndicadores.rsi(precos[:-1], self.periodo_rsi)

        if rsi_atual is None or rsi_anterior is None:
            return None

        dado_atual = dados_historicos[-1]
        preco_atual = dado_atual['ultimo']

        # Calcular ATR
        atr = CalculadorIndicadores.atr(dados_historicos, 14)
        if atr is None:
            atr = preco_atual * 0.02

        # Sinal de COMPRA: RSI saindo de sobrevenda
        if rsi_anterior <= self.nivel_sobrevenda and rsi_atual > self.nivel_sobrevenda:
            confianca = 0.6 + ((self.nivel_sobrevenda - rsi_anterior) / 100)

            return SinalTecnico(
                data=dado_atual['data'],
                tipo='COMPRA',
                preco_entrada=preco_atual,
                stop_loss=preco_atual - (atr * 2),
                take_profit=preco_atual + (atr * 3),
                confianca=min(confianca, 0.95),
                indicadores={'rsi': rsi_atual, 'atr': atr},
                razao=f"RSI saindo de sobrevenda: {rsi_anterior:.1f} → {rsi_atual:.1f} (limite: {self.nivel_sobrevenda})"
            )

        # Sinal de VENDA: RSI saindo de sobrecompra
        elif rsi_anterior >= self.nivel_sobrecompra and rsi_atual < self.nivel_sobrecompra:
            confianca = 0.6 + ((rsi_anterior - self.nivel_sobrecompra) / 100)

            return SinalTecnico(
                data=dado_atual['data'],
                tipo='VENDA',
                preco_entrada=preco_atual,
                stop_loss=preco_atual + (atr * 2),
                take_profit=preco_atual - (atr * 3),
                confianca=min(confianca, 0.95),
                indicadores={'rsi': rsi_atual, 'atr': atr},
                razao=f"RSI saindo de sobrecompra: {rsi_anterior:.1f} → {rsi_atual:.1f} (limite: {self.nivel_sobrecompra})"
            )

        return None


class EstrategiaBollinger:
    """Estratégia baseada em Bandas de Bollinger - reversão à média."""

    def __init__(self, periodo: int = 20, num_desvios: float = 2.0):
        self.periodo = periodo
        self.num_desvios = num_desvios
        self.nome = f"Bollinger {periodo} ({num_desvios}σ)"

    def gerar_sinal(self, dados_historicos: List[dict]) -> Optional[SinalTecnico]:
        """Gera sinal baseado em toque nas bandas de Bollinger."""
        if len(dados_historicos) < self.periodo + 1:
            return None

        precos = [d['ultimo'] for d in dados_historicos]

        # Calcular bandas
        bandas = CalculadorIndicadores.bollinger_bands(precos, self.periodo, self.num_desvios)
        if bandas is None:
            return None

        banda_superior, banda_media, banda_inferior = bandas

        dado_atual = dados_historicos[-1]
        preco_atual = dado_atual['ultimo']
        preco_anterior = dados_historicos[-2]['ultimo']

        # Calcular ATR
        atr = CalculadorIndicadores.atr(dados_historicos, 14)
        if atr is None:
            atr = preco_atual * 0.02

        # Calcular RSI para confirmar
        rsi = CalculadorIndicadores.rsi(precos, 14) or 50

        # Sinal de COMPRA: Preço toca banda inferior e RSI em sobrevenda
        if preco_anterior <= banda_inferior and preco_atual > banda_inferior and rsi < 40:
            distancia_banda = ((banda_media - preco_atual) / preco_atual) * 100
            confianca = 0.6 + (distancia_banda / 10)

            return SinalTecnico(
                data=dado_atual['data'],
                tipo='COMPRA',
                preco_entrada=preco_atual,
                stop_loss=preco_atual - (atr * 2),
                take_profit=banda_media,  # Objetivo: retornar à média
                confianca=min(confianca, 0.95),
                indicadores={
                    'banda_superior': banda_superior,
                    'banda_media': banda_media,
                    'banda_inferior': banda_inferior,
                    'rsi': rsi,
                    'atr': atr
                },
                razao=f"Toque na banda inferior ({banda_inferior:.2f}) com RSI em {rsi:.1f}. Objetivo: média {banda_media:.2f}"
            )

        # Sinal de VENDA: Preço toca banda superior e RSI em sobrecompra
        elif preco_anterior >= banda_superior and preco_atual < banda_superior and rsi > 60:
            distancia_banda = ((preco_atual - banda_media) / preco_atual) * 100
            confianca = 0.6 + (distancia_banda / 10)

            return SinalTecnico(
                data=dado_atual['data'],
                tipo='VENDA',
                preco_entrada=preco_atual,
                stop_loss=preco_atual + (atr * 2),
                take_profit=banda_media,  # Objetivo: retornar à média
                confianca=min(confianca, 0.95),
                indicadores={
                    'banda_superior': banda_superior,
                    'banda_media': banda_media,
                    'banda_inferior': banda_inferior,
                    'rsi': rsi,
                    'atr': atr
                },
                razao=f"Toque na banda superior ({banda_superior:.2f}) com RSI em {rsi:.1f}. Objetivo: média {banda_media:.2f}"
            )

        return None


class EstrategiaMACD:
    """Estratégia baseada em MACD (Moving Average Convergence Divergence)."""

    def __init__(self, rapida: int = 12, lenta: int = 26, sinal: int = 9):
        self.rapida = rapida
        self.lenta = lenta
        self.sinal = sinal
        self.nome = f"MACD ({rapida},{lenta},{sinal})"

    def calcular_macd(self, precos: List[float]) -> Optional[Tuple[float, float, float]]:
        """Calcula MACD, Signal e Histograma."""
        if len(precos) < self.lenta + self.sinal:
            return None

        # EMA rápida e lenta
        ema_rapida = CalculadorIndicadores.media_movel_exponencial(precos, self.rapida)
        ema_lenta = CalculadorIndicadores.media_movel_exponencial(precos, self.lenta)

        if ema_rapida is None or ema_lenta is None:
            return None

        # Linha MACD
        macd_line = ema_rapida - ema_lenta

        # Calcular Signal Line (EMA do MACD)
        # Simplificado: usar média móvel simples do MACD
        if len(precos) < self.lenta + self.sinal + 1:
            return None

        macds = []
        for i in range(len(precos) - self.lenta - self.sinal + 1, len(precos) + 1):
            ema_r = CalculadorIndicadores.media_movel_exponencial(precos[:i], self.rapida)
            ema_l = CalculadorIndicadores.media_movel_exponencial(precos[:i], self.lenta)
            if ema_r and ema_l:
                macds.append(ema_r - ema_l)

        if len(macds) < self.sinal:
            return None

        signal_line = sum(macds[-self.sinal:]) / self.sinal
        histogram = macd_line - signal_line

        return (macd_line, signal_line, histogram)

    def gerar_sinal(self, dados_historicos: List[dict]) -> Optional[SinalTecnico]:
        """Gera sinal baseado em cruzamento do MACD."""
        if len(dados_historicos) < self.lenta + self.sinal + 2:
            return None

        precos = [d['ultimo'] for d in dados_historicos]

        # Calcular MACD atual e anterior
        macd_atual = self.calcular_macd(precos)
        macd_anterior = self.calcular_macd(precos[:-1])

        if macd_atual is None or macd_anterior is None:
            return None

        macd_line, signal_line, histogram = macd_atual
        macd_line_ant, signal_line_ant, histogram_ant = macd_anterior

        dado_atual = dados_historicos[-1]
        preco_atual = dado_atual['ultimo']

        # Calcular ATR
        atr = CalculadorIndicadores.atr(dados_historicos, 14)
        if atr is None:
            atr = preco_atual * 0.02

        # Detectar cruzamento
        cruzamento_alta = histogram_ant <= 0 and histogram > 0
        cruzamento_baixa = histogram_ant >= 0 and histogram < 0

        # Sinal de COMPRA: MACD cruza acima da Signal
        if cruzamento_alta:
            confianca = 0.65 + min(abs(histogram) / 100, 0.25)

            return SinalTecnico(
                data=dado_atual['data'],
                tipo='COMPRA',
                preco_entrada=preco_atual,
                stop_loss=preco_atual - (atr * 2),
                take_profit=preco_atual + (atr * 3),
                confianca=min(confianca, 0.95),
                indicadores={
                    'macd': macd_line,
                    'signal': signal_line,
                    'histogram': histogram,
                    'atr': atr
                },
                razao=f"MACD cruzou acima da Signal. Histograma: {histogram:.2f}"
            )

        # Sinal de VENDA: MACD cruza abaixo da Signal
        elif cruzamento_baixa:
            confianca = 0.65 + min(abs(histogram) / 100, 0.25)

            return SinalTecnico(
                data=dado_atual['data'],
                tipo='VENDA',
                preco_entrada=preco_atual,
                stop_loss=preco_atual + (atr * 2),
                take_profit=preco_atual - (atr * 3),
                confianca=min(confianca, 0.95),
                indicadores={
                    'macd': macd_line,
                    'signal': signal_line,
                    'histogram': histogram,
                    'atr': atr
                },
                razao=f"MACD cruzou abaixo da Signal. Histograma: {histogram:.2f}"
            )

        return None


class BacktestEngine:
    """Motor de backtesting para simular e avaliar estratégias."""

    def __init__(self, caminho_bd: Optional[Path] = None):
        self.caminho_bd = caminho_bd or Path(__file__).parent.parent.parent / 'data' / 'recomendacoes.sqlite'

    def carregar_dados_historicos(self, instrumento: str, data_inicio: str, data_fim: str) -> List[dict]:
        """Carrega dados históricos do banco."""
        conn = sqlite3.connect(self.caminho_bd)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute(
            """
            SELECT data, instrumento, ultimo, abertura, maxima, minima, volume, variacao_pct
            FROM precos_diarios
            WHERE instrumento = ? AND data >= ? AND data <= ?
            ORDER BY data ASC
            """,
            (instrumento, data_inicio, data_fim)
        )

        dados = [dict(row) for row in c.fetchall()]
        conn.close()

        return dados

    def executar_backtest(
        self,
        estrategia: EstrategiaCruzamentoMedias,
        instrumento: str,
        data_inicio: str,
        data_fim: str,
        salvar_recomendacoes: bool = True
    ) -> dict:
        """
        Executa backtest de uma estratégia em um período específico.

        Args:
            estrategia: Estratégia a ser testada
            instrumento: Código do instrumento (ex: WIN)
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
            salvar_recomendacoes: Se True, salva recomendações e resultados no banco

        Returns:
            Dicionário com estatísticas do backtest
        """
        print(f"\n🔬 INICIANDO BACKTEST")
        print(f"=" * 80)
        print(f"📊 Estratégia: {estrategia.nome}")
        print(f"📈 Instrumento: {instrumento}")
        print(f"📅 Período: {data_inicio} até {data_fim}")

        # Carregar todos os dados do período
        dados = self.carregar_dados_historicos(instrumento, data_inicio, data_fim)

        if not dados:
            print("❌ Nenhum dado encontrado para o período especificado.")
            return {}

        print(f"✅ Carregados {len(dados)} dias de histórico")

        # Simular trading dia a dia
        sinais_gerados = 0
        recomendacoes_salvas = 0

        # Precisamos de histórico suficiente para calcular indicadores
        # Detectar janela mínima baseado no tipo de estratégia
        if hasattr(estrategia, 'periodo_curto') and hasattr(estrategia, 'periodo_longo'):
            # EstrategiaCruzamentoMedias
            janela_minima = max(estrategia.periodo_curto, estrategia.periodo_longo) + 14
        elif hasattr(estrategia, 'periodo_rsi'):
            # EstrategiaRSI
            janela_minima = estrategia.periodo_rsi + 14
        elif hasattr(estrategia, 'periodo'):
            # EstrategiaBollinger
            janela_minima = estrategia.periodo + 14
        elif hasattr(estrategia, 'lenta'):
            # EstrategiaMACD
            janela_minima = estrategia.lenta + estrategia.sinal + 14
        else:
            # Padrão: assumir 50 dias
            janela_minima = 50

        for i in range(janela_minima, len(dados)):
            # Dados até o dia atual (simulando que não conhecemos o futuro)
            historico_ate_hoje = dados[:i+1]

            # Gerar sinal para o dia
            sinal = estrategia.gerar_sinal(historico_ate_hoje)

            if sinal and salvar_recomendacoes:
                # Pegar dado atual
                dado_atual = historico_ate_hoje[-1]

                # Converter sinal para formato esperado pela persistência
                # Calcular TP1/TP2 e contratos para saídas parciais
                entrada = sinal.preco_entrada
                stop = sinal.stop_loss
                tp_base = sinal.take_profit
                atr_val = float(sinal.indicadores.get('atr', 0) or 0)

                # Definir TP1/TP2 de forma robusta com fallback quando não houver ATR
                if sinal.tipo == 'COMPRA':
                    if atr_val > 0:
                        tp1_preco = entrada + (2.0 * atr_val)
                        tp2_preco = entrada + (3.0 * atr_val)
                    else:
                        delta = max(tp_base - entrada, 0)
                        tp2_preco = entrada + delta
                        tp1_preco = entrada + (delta * 0.5)
                    # Garantir ordem
                    tp1_preco, tp2_preco = min(tp1_preco, tp2_preco), max(tp1_preco, tp2_preco)
                else:  # VENDA
                    if atr_val > 0:
                        tp1_preco = entrada - (2.0 * atr_val)
                        tp2_preco = entrada - (3.0 * atr_val)
                    else:
                        delta = max(entrada - tp_base, 0)
                        tp2_preco = entrada - delta
                        tp1_preco = entrada - (delta * 0.5)
                    # Garantir ordem (tp2 deve ser mais distante do que tp1)
                    tp1_preco, tp2_preco = max(tp1_preco, tp2_preco), min(tp1_preco, tp2_preco)

                dados_recomendacao = {
                    'timestamp': sinal.data + 'T09:00:00',
                    'estrategia_nome': estrategia.nome,  # Nome da estratégia
                    'relatorio_executivo': {
                        'variacao_dia': f"{dado_atual['variacao_pct']:.2f}%" if dado_atual.get('variacao_pct') else '0.00%',
                        'sintese': {
                            'saldo_macro': '+1 - BACKTEST',
                            'tendencia': sinal.tipo,
                            'melhor_spread': 'N/A - Backtest',
                            'estrategia': estrategia.nome,  # Também no relatório
                        }
                    },
                    'plano_trading': {
                        'direcao': sinal.tipo,
                        'entrada_inicial': {
                            'preco': entrada,
                            'contratos': 2  # 2 contratos para permitir saídas parciais (TP1/TP2)
                        },
                        'gestao_saida': {
                            'stop_loss': {'preco': stop},
                            'take_profit': [
                                {'preco': tp1_preco, 'contratos': 1},
                                {'preco': tp2_preco, 'contratos': 1},
                            ]
                        },
                        'reforcos': [],
                        'confianca': int(sinal.confianca * 100),
                        'valido_ate': sinal.data + ' 17:00'
                    },
                    'analise_tecnica': {
                        'indicadores': {
                            'atr': {'valor': atr_val}
                        }
                    }
                }

                try:
                    id_rec = salvar_recomendacao(dados_recomendacao, caminho_bd=self.caminho_bd)

                    # Simular validação no dia seguinte (se houver dados)
                    if i + 1 < len(dados):
                        dado_dia_seguinte = dados[i + 1]
                        preco_close = dado_dia_seguinte['ultimo']
                        maxima = dado_dia_seguinte['maxima']
                        minima = dado_dia_seguinte['minima']

                        # Reutilizar valores calculados
                        stop = stop
                        tp1 = tp1_preco
                        tp2 = tp2_preco
                        entrada = entrada

                        # Lógica de execução com TP parcial e trailing para D+1 (simulação intradiária conservadora)
                        preco_saida_medio = preco_close
                        pnl_pontos = 0.0
                        motivo_saida = "Fechamento D+1"

                        if sinal.tipo == 'COMPRA':
                            stop_hit = minima <= stop
                            tp2_hit = maxima >= tp2
                            tp1_hit = maxima >= tp1

                            if stop_hit and tp1_hit:
                                # Conservador: assume stop primeiro
                                preco_saida_medio = stop
                                pnl_pontos = stop - entrada
                                motivo_saida = "Stop Loss"
                            elif tp2_hit:
                                # Atingiu TP2 (implica TP1)
                                preco_saida_medio = 0.5 * tp1 + 0.5 * tp2
                                pnl_pontos = 0.5 * (tp1 - entrada) + 0.5 * (tp2 - entrada)
                                motivo_saida = "tp2"
                            elif tp1_hit:
                                # Realiza 50% no TP1 e ativa trailing para BE
                                be = entrada
                                if minima <= be:
                                    # Resto saiu no breakeven
                                    preco_saida_medio = 0.5 * tp1 + 0.5 * be
                                    pnl_pontos = 0.5 * (tp1 - entrada)
                                    motivo_saida = "tp1"
                                else:
                                    # Resto sai no fechamento
                                    preco_saida_medio = 0.5 * tp1 + 0.5 * preco_close
                                    pnl_pontos = 0.5 * (tp1 - entrada) + 0.5 * (preco_close - entrada)
                                    motivo_saida = "tp1"
                            elif stop_hit:
                                preco_saida_medio = stop
                                pnl_pontos = stop - entrada
                                motivo_saida = "Stop Loss"
                            else:
                                preco_saida_medio = preco_close
                                pnl_pontos = preco_close - entrada
                                motivo_saida = "Fechamento D+1"
                        else:  # VENDA
                            stop_hit = maxima >= stop
                            tp2_hit = minima <= tp2
                            tp1_hit = minima <= tp1

                            if stop_hit and tp1_hit:
                                # Conservador: assume stop primeiro
                                preco_saida_medio = stop
                                pnl_pontos = entrada - stop
                                motivo_saida = "Stop Loss"
                            elif tp2_hit:
                                preco_saida_medio = 0.5 * tp1 + 0.5 * tp2
                                pnl_pontos = 0.5 * (entrada - tp1) + 0.5 * (entrada - tp2)
                                motivo_saida = "tp2"
                            elif tp1_hit:
                                be = entrada
                                if maxima >= be:
                                    # Resto saiu no breakeven
                                    preco_saida_medio = 0.5 * tp1 + 0.5 * be
                                    pnl_pontos = 0.5 * (entrada - tp1)
                                    motivo_saida = "tp1"
                                else:
                                    preco_saida_medio = 0.5 * tp1 + 0.5 * preco_close
                                    pnl_pontos = 0.5 * (entrada - tp1) + 0.5 * (entrada - preco_close)
                                    motivo_saida = "tp1"
                            elif stop_hit:
                                preco_saida_medio = stop
                                pnl_pontos = entrada - stop
                                motivo_saida = "Stop Loss"
                            else:
                                preco_saida_medio = preco_close
                                pnl_pontos = entrada - preco_close
                                motivo_saida = "Fechamento D+1"

                        acertou = pnl_pontos > 0

                        # Registrar resultado com preço médio de saída
                        registrar_resultado(
                            id_recomendacao=id_rec,
                            status='FECHADA',
                            acertou=acertou,
                            preco_saida=preco_saida_medio,
                            pnl_pontos=pnl_pontos,
                            pnl_reais=pnl_pontos * 0.20,  # Fator de conversão aproximado WIN
                            motivo_saida=motivo_saida,
                            observacoes=f"Backtest automático: {estrategia.nome}",
                            caminho_bd=self.caminho_bd
                        )

                        recomendacoes_salvas += 1

                    sinais_gerados += 1

                except Exception as e:
                    print(f"⚠️  Erro ao salvar recomendação para {sinal.data}: {e}")

        print(f"\n📊 RESULTADOS DO BACKTEST:")
        print(f"=" * 80)
        print(f"✨ Sinais gerados: {sinais_gerados}")
        print(f"💾 Recomendações salvas e validadas: {recomendacoes_salvas}")

        if salvar_recomendacoes and recomendacoes_salvas > 0:
            # Calcular métricas usando o sistema existente
            print(f"\n📈 CALCULANDO MÉTRICAS DE PERFORMANCE...")
            metricas = calcular_metricas_detalhadas(caminho_bd=self.caminho_bd)

            if metricas and 'metricas_gerais' in metricas:
                mg = metricas['metricas_gerais']
                print(f"\n🎯 MÉTRICAS GERAIS:")
                print(f"   Taxa de acerto: {mg.get('taxa_acerto', 0):.1f}%")
                print(f"   Lucro médio: {mg.get('lucro_medio', 0):.2f}")
                print(f"   Prejuízo médio: {mg.get('prejuizo_medio', 0):.2f}")
                print(f"   Payoff ratio: {mg.get('payoff_ratio', 0):.2f}")
                print(f"   Total de operações: {mg.get('total_operacoes', 0)}")

        return {
            'sinais_gerados': sinais_gerados,
            'recomendacoes_salvas': recomendacoes_salvas,
            'periodo': (data_inicio, data_fim),
            'instrumento': instrumento,
            'estrategia': estrategia.nome
        }


if __name__ == '__main__':
    # Exemplo de uso
    engine = BacktestEngine()
    estrategia = EstrategiaCruzamentoMedias(periodo_curto=9, periodo_longo=21)

    # Testar em um período recente (último ano com dados completos)
    resultado = engine.executar_backtest(
        estrategia=estrategia,
        instrumento='WIN',
        data_inicio='2024-01-01',
        data_fim='2024-12-31',
        salvar_recomendacoes=True
    )
