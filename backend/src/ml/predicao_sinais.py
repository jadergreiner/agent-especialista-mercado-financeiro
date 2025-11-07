"""
Sistema de Machine Learning para predição de sinais de trading.
Usa features de indicadores técnicos e padrões de preço.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any
import sqlite3
import json
from dataclasses import dataclass

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backtest.motor_backtest import CalculadorIndicadores


@dataclass
class FeatureSet:
    """Conjunto de features para ML."""
    # Features técnicas
    rsi_14: float
    rsi_9: float
    rsi_21: float

    # Médias móveis
    sma_9: float
    sma_21: float
    sma_50: float
    ema_9: float
    ema_21: float

    # Bollinger Bands
    bb_upper: float
    bb_middle: float
    bb_lower: float
    bb_width: float  # Largura das bandas (volatilidade)
    bb_position: float  # Posição do preço nas bandas (0-1)

    # MACD
    macd_line: float
    macd_signal: float
    macd_histogram: float

    # ATR e volatilidade
    atr_14: float
    atr_ratio: float  # ATR / preço (volatilidade normalizada)

    # Momentum
    roc_5: float  # Rate of Change 5 períodos
    roc_10: float

    # Volume (se disponível)
    volume_ratio: float  # Volume atual / média 20 dias

    # Padrões de preço
    distancia_maxima_dia: float  # % do preço à máxima do dia
    distancia_minima_dia: float  # % do preço à mínima do dia
    range_dia: float  # (máxima - mínima) / fechamento

    # Tendência
    tendencia_curto: int  # 1=alta, 0=neutro, -1=baixa (MA9 vs MA21)
    tendencia_medio: int  # 1=alta, 0=neutro, -1=baixa (MA21 vs MA50)

    # Target (para treinamento)
    target: int  # 1=COMPRA bem-sucedida, -1=VENDA bem-sucedida, 0=sem sinal/neutro


class ExtratorFeatures:
    """Extrai features de dados históricos para ML."""

    @staticmethod
    def extrair_features(
        dados_historicos: List[dict],
        target: int = 0
    ) -> FeatureSet | None:
        """
        Extrai features do último dia do histórico.

        Args:
            dados_historicos: Lista de dicts com dados OHLCV
            target: Label para treinamento (1=compra, -1=venda, 0=neutro)
        """
        if len(dados_historicos) < 50:
            return None

        precos = [d['ultimo'] for d in dados_historicos]
        preco_atual = precos[-1]
        dado_atual = dados_historicos[-1]

        # RSI em múltiplos períodos
        rsi_14 = CalculadorIndicadores.rsi(precos, 14) or 50
        rsi_9 = CalculadorIndicadores.rsi(precos, 9) or 50
        rsi_21 = CalculadorIndicadores.rsi(precos, 21) or 50

        # Médias móveis
        sma_9 = CalculadorIndicadores.media_movel_simples(precos, 9) or preco_atual
        sma_21 = CalculadorIndicadores.media_movel_simples(precos, 21) or preco_atual
        sma_50 = CalculadorIndicadores.media_movel_simples(precos, 50) or preco_atual
        ema_9 = CalculadorIndicadores.media_movel_exponencial(precos, 9) or preco_atual
        ema_21 = CalculadorIndicadores.media_movel_exponencial(precos, 21) or preco_atual

        # Bollinger Bands
        bandas = CalculadorIndicadores.bollinger_bands(precos, 20, 2.0)
        if bandas:
            bb_upper, bb_middle, bb_lower = bandas
            bb_width = (bb_upper - bb_lower) / bb_middle
            bb_position = (preco_atual - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        else:
            bb_upper = bb_middle = bb_lower = preco_atual
            bb_width = 0.04
            bb_position = 0.5

        # MACD (simplificado)
        ema_12 = CalculadorIndicadores.media_movel_exponencial(precos, 12) or preco_atual
        ema_26 = CalculadorIndicadores.media_movel_exponencial(precos, 26) or preco_atual
        macd_line = ema_12 - ema_26

        # Signal line (SMA do MACD - simplificado)
        macd_signal = macd_line * 0.9  # Aproximação
        macd_histogram = macd_line - macd_signal

        # ATR
        atr_14 = CalculadorIndicadores.atr(dados_historicos, 14) or (preco_atual * 0.02)
        atr_ratio = atr_14 / preco_atual

        # Rate of Change (ROC)
        if len(precos) >= 5:
            roc_5 = ((preco_atual - precos[-5]) / precos[-5]) * 100
        else:
            roc_5 = 0.0

        if len(precos) >= 10:
            roc_10 = ((preco_atual - precos[-10]) / precos[-10]) * 100
        else:
            roc_10 = 0.0

        # Volume ratio
        if 'volume' in dado_atual and dado_atual['volume']:
            volumes = [d.get('volume', 0) or 0 for d in dados_historicos[-20:]]
            volume_medio = sum(volumes) / len(volumes) if volumes else 1
            volume_ratio = dado_atual['volume'] / volume_medio if volume_medio > 0 else 1.0
        else:
            volume_ratio = 1.0

        # Padrões de preço
        maxima = dado_atual.get('maxima', preco_atual)
        minima = dado_atual.get('minima', preco_atual)

        distancia_maxima_dia = ((maxima - preco_atual) / preco_atual) * 100
        distancia_minima_dia = ((preco_atual - minima) / preco_atual) * 100
        range_dia = ((maxima - minima) / preco_atual) * 100 if preco_atual > 0 else 0

        # Tendências
        tendencia_curto = 1 if sma_9 > sma_21 else (-1 if sma_9 < sma_21 else 0)
        tendencia_medio = 1 if sma_21 > sma_50 else (-1 if sma_21 < sma_50 else 0)

        return FeatureSet(
            rsi_14=rsi_14,
            rsi_9=rsi_9,
            rsi_21=rsi_21,
            sma_9=sma_9,
            sma_21=sma_21,
            sma_50=sma_50,
            ema_9=ema_9,
            ema_21=ema_21,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
            bb_width=bb_width,
            bb_position=bb_position,
            macd_line=macd_line,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            atr_14=atr_14,
            atr_ratio=atr_ratio,
            roc_5=roc_5,
            roc_10=roc_10,
            volume_ratio=volume_ratio,
            distancia_maxima_dia=distancia_maxima_dia,
            distancia_minima_dia=distancia_minima_dia,
            range_dia=range_dia,
            tendencia_curto=tendencia_curto,
            tendencia_medio=tendencia_medio,
            target=target
        )

    @staticmethod
    def criar_dataset_de_backtests(
        db_path: Path = None,
        instrumento_padrao: str = 'WIN'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Cria dataset de treinamento a partir dos backtests salvos no banco.

        Returns:
            X: Features (n_samples, n_features)
            y: Targets (n_samples,) - 1=acertou, 0=errou
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'data' / 'recomendacoes.sqlite'

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Buscar todas as recomendações com resultados
        query = """
        SELECT
            r.timestamp,
            r.instrumento,
            r.direcao,
            r.preco_entrada,
            r.confianca,
            res.acertou,
            res.pnl_pontos
        FROM recomendacoes r
        INNER JOIN resultados res ON r.id = res.id_recomendacao
        WHERE r.estrategia_nome IS NOT NULL
            AND res.acertou IS NOT NULL
        ORDER BY r.timestamp
        """

        cursor.execute(query)
        operacoes = [dict(row) for row in cursor.fetchall()]

        X_list: List[List[float]] = []
        y_list: List[int] = []

        def carregar_dados_historicos(instr: str, data_limite: str) -> List[dict]:
            c = conn.cursor()
            c.execute(
                """
                SELECT data, instrumento, ultimo, abertura, maxima, minima, volume, variacao_pct
                FROM precos_diarios
                WHERE instrumento = ? AND data <= ?
                ORDER BY data ASC
                """,
                (instr, data_limite)
            )
            return [dict(r) for r in c.fetchall()]

        for op in operacoes:
            ts = op['timestamp']  # ISO com hora
            data_ref = ts.split('T')[0] if 'T' in ts else ts[:10]
            instr = op.get('instrumento') or instrumento_padrao

            hist = carregar_dados_historicos(instr, data_ref)
            fs = ExtratorFeatures.extrair_features(hist, target=0)
            if not fs:
                continue

            # Montar vetor de features na ordem definida
            feats = [
                fs.rsi_14, fs.rsi_9, fs.rsi_21,
                fs.sma_9, fs.sma_21, fs.sma_50, fs.ema_9, fs.ema_21,
                fs.bb_upper, fs.bb_middle, fs.bb_lower, fs.bb_width, fs.bb_position,
                fs.macd_line, fs.macd_signal, fs.macd_histogram,
                fs.atr_14, fs.atr_ratio,
                fs.roc_5, fs.roc_10,
                fs.volume_ratio,
                fs.distancia_maxima_dia, fs.distancia_minima_dia, fs.range_dia,
                fs.tendencia_curto, fs.tendencia_medio,
            ]

            X_list.append(feats)
            y_list.append(1 if (op.get('pnl_pontos') or 0) > 0 else 0)

        conn.close()

        X = np.array(X_list, dtype=float) if X_list else np.empty((0, 26), dtype=float)
        y = np.array(y_list, dtype=int) if y_list else np.empty((0,), dtype=int)

        print(f"📊 Encontradas {len(operacoes)} operações com resultados")
        print("💡 Dataset de ML criado com sucesso!")
        print(f"   Features por amostra: 26")
        print(f"   Amostras: {len(y)}")

        return X, y


class ModeloML:
    """
    Modelo de Machine Learning para predição de sinais.
    Placeholder para implementação futura com scikit-learn/XGBoost.
    """

    def __init__(self):
        self.modelo = None
        self.features_nomes = [
            'rsi_14', 'rsi_9', 'rsi_21',
            'sma_9', 'sma_21', 'sma_50', 'ema_9', 'ema_21',
            'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_position',
            'macd_line', 'macd_signal', 'macd_histogram',
            'atr_14', 'atr_ratio',
            'roc_5', 'roc_10',
            'volume_ratio',
            'distancia_maxima_dia', 'distancia_minima_dia', 'range_dia',
            'tendencia_curto', 'tendencia_medio'
        ]

    def treinar(self, X: np.ndarray, y: np.ndarray):
        """Treina um modelo simples (RandomForest) se scikit-learn estiver disponível."""
        print("🤖 Treinando modelo de Machine Learning...")
        if X is None or y is None or len(y) == 0:
            print("⚠️  Dataset vazio. Pulei o treino.")
            return

        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
            clf = RandomForestClassifier(n_estimators=300, max_depth=None, n_jobs=-1, random_state=42)
            clf.fit(X_train, y_train)
            self.modelo = clf

            y_pred = clf.predict(X_test)
            y_proba = clf.predict_proba(X_test)[:,1] if hasattr(clf, 'predict_proba') else None
            acc = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_proba) if y_proba is not None and len(set(y_test))>1 else None
            cm = confusion_matrix(y_test, y_pred)

            print(f"   Acurácia (holdout): {acc:.3f}")
            if auc is not None:
                print(f"   ROC-AUC (holdout): {auc:.3f}")
            print(f"   Matriz de confusão:\n{cm}")
        except ModuleNotFoundError:
            print(f"   Features: {X.shape[1] if X is not None else 26}")
            print(f"   Samples: {len(y)}")
            print("\n💡 scikit-learn não encontrado. Para treinar de fato, instale:")
            print("   pip install scikit-learn xgboost pandas matplotlib")
            print("\n   Então use RandomForestClassifier ou XGBClassifier")

    def prever(self, features: FeatureSet) -> Tuple[int, float]:
        """
        Prediz sinal e probabilidade (placeholder).

        Returns:
            (direcao, probabilidade) onde direcao: 1=COMPRA, -1=VENDA, 0=neutro
        """
        # Placeholder: usar regras simples
        if features.rsi_14 < 30 and features.tendencia_curto == 1:
            return (1, 0.75)  # COMPRA com 75% confiança
        elif features.rsi_14 > 70 and features.tendencia_curto == -1:
            return (-1, 0.75)  # VENDA com 75% confiança
        else:
            return (0, 0.50)  # Neutro


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🤖 SISTEMA DE MACHINE LEARNING PARA TRADING")
    print("="*80)

    # Criar dataset
    extrator = ExtratorFeatures()
    X, y = extrator.criar_dataset_de_backtests()

    # Treinar modelo
    modelo = ModeloML()
    modelo.treinar(X, y)

    print("\n" + "="*80)
    print("✅ INFRAESTRUTURA DE ML PREPARADA")
    print("="*80)
    print("\n📚 Próximos passos:")
    print("   1. Implementar feature engineering completo")
    print("   2. Treinar Random Forest / XGBoost")
    print("   3. Validação cruzada e otimização de hiperparâmetros")
    print("   4. Criar estratégia baseada em ML")
    print("   5. Backtesting da estratégia ML")
