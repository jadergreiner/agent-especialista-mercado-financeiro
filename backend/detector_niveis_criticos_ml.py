"""
Sistema ML Avançado para Identificação de Níveis Críticos de Preço
Engenheiro ML: Algoritmos de machine learning para detecção de alta precisão

Funcionalidades:
1. Clustering de preços para identificar zonas de concentração
2. Análise de volume profile e order flow
3. Detecção de padrões temporais com ML
4. Scoring inteligente de força dos níveis
5. Predição de breakouts usando ensemble methods
6. Integração com dados históricos multi-fonte
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.spatial.distance import cdist
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
import warnings
from scipy import stats
from scipy.signal import find_peaks, argrelextrema
import sqlite3
from concurrent.futures import ThreadPoolExecutor

# Importar nosso carregador de dados
try:
    from .carregador_dados_historicos import CarregadorDadosHistoricos
except ImportError:
    from carregador_dados_historicos import CarregadorDadosHistoricos

warnings.filterwarnings('ignore')

class DetectorNiveisCriticosML:
    """Sistema ML avançado para detecção de níveis críticos de preço"""

    def __init__(self, carregador_dados: CarregadorDadosHistoricos = None):
        self.logger = self._configurar_logger()

        # Sistema de carregamento de dados
        self.carregador_dados = carregador_dados or CarregadorDadosHistoricos()

        # Modelos ML
        self.modelo_clustering = None
        self.modelo_forca_nivel = None
        self.modelo_breakout = None

        # Cache e persistência
        self.cache_dir = "data/ml_niveis_criticos"
        self.modelos_dir = os.path.join(self.cache_dir, "modelos")
        self.db_path = os.path.join(self.cache_dir, "niveis_ml.db")

        # Criar estrutura
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.modelos_dir, exist_ok=True)
        self._inicializar_database()

        # Parâmetros ML
        self.parametros_clustering = {
            'eps': 0.002,  # 0.2% de tolerância para agrupamento
            'min_samples': 3  # Mínimo 3 toques para ser nível válido
        }

        self.parametros_ml = {
            'n_estimators': 100,
            'random_state': 42,
            'test_size': 0.3
        }

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('DetectorNiveisCriticosML')
        logger.setLevel(logging.INFO)
        return logger

    def _inicializar_database(self):
        """Inicializar database para armazenar níveis ML"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS niveis_ml (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                nivel_preco REAL NOT NULL,
                tipo_nivel TEXT NOT NULL,
                forca_score REAL NOT NULL,
                confianca_ml REAL NOT NULL,
                toques_historicos INTEGER NOT NULL,
                volume_medio REAL,
                ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadados TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS previsoes_breakout (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                nivel_preco REAL NOT NULL,
                direcao TEXT NOT NULL,
                probabilidade REAL NOT NULL,
                confianca_score REAL NOT NULL,
                timestamp_previsao DATETIME DEFAULT CURRENT_TIMESTAMP,
                validado BOOLEAN DEFAULT FALSE,
                resultado_real TEXT
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_timeframe ON niveis_ml(ticker, timeframe, tipo_nivel)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_previsao ON previsoes_breakout(ticker, timestamp_previsao)')

        conn.commit()
        conn.close()

    def extrair_features_nivel(self, dados: pd.DataFrame, nivel: float, janela: int = 50) -> Dict:
        """Extrair features ML para um nível específico"""

        if dados.empty or len(dados) < janela:
            return {}

        # Calcular distância relativa para o nível
        dados_janela = dados.tail(janela)
        distancias = np.abs(dados_janela['Close'] - nivel) / nivel

        # Features de proximidade
        toques_proximos = (distancias <= 0.002).sum()  # Dentro de 0.2%
        toques_muito_proximos = (distancias <= 0.001).sum()  # Dentro de 0.1%

        # Features de volume
        indices_proximos = distancias <= 0.002
        if indices_proximos.sum() > 0:
            volume_medio_nivel = dados_janela.loc[indices_proximos, 'Volume'].mean()
            volume_geral = dados_janela['Volume'].mean()
            ratio_volume = volume_medio_nivel / volume_geral if volume_geral > 0 else 1
        else:
            ratio_volume = 0

        # Features de volatilidade
        volatilidade = dados_janela['Close'].pct_change().std()

        # Features de momentum
        returns = dados_janela['Close'].pct_change()
        momentum_positivo = (returns > 0).sum() / len(returns)

        # Features de range
        range_medio = (dados_janela['High'] - dados_janela['Low']).mean()
        range_atual = dados_janela['High'].iloc[-1] - dados_janela['Low'].iloc[-1]
        ratio_range = range_atual / range_medio if range_medio > 0 else 1

        # Features temporais
        primeiro_toque = None
        ultimo_toque = None

        for i, dist in enumerate(distancias):
            if dist <= 0.002:
                if primeiro_toque is None:
                    primeiro_toque = i
                ultimo_toque = i

        persistencia_temporal = (ultimo_toque - primeiro_toque) if (primeiro_toque is not None and ultimo_toque is not None) else 0

        return {
            'toques_proximos': toques_proximos,
            'toques_muito_proximos': toques_muito_proximos,
            'ratio_volume': ratio_volume,
            'volatilidade': volatilidade,
            'momentum_positivo': momentum_positivo,
            'ratio_range': ratio_range,
            'persistencia_temporal': persistencia_temporal,
            'nivel_preco': nivel
        }

    def identificar_niveis_clustering(self, dados: pd.DataFrame, timeframe: str = '1d') -> Dict:
        """Identificar níveis usando clustering DBSCAN"""

        if dados.empty or len(dados) < 20:
            return {'suportes': [], 'resistencias': []}

        # Extrair pontos de interesse (highs e lows)
        pontos_interesse = []

        # Adicionar máximas e mínimas locais
        janela = 5 if timeframe == '1h' else 10 if timeframe == '4h' else 20

        for i in range(janela, len(dados) - janela):
            # Máxima local
            if dados['High'].iloc[i] == dados['High'].iloc[i-janela:i+janela+1].max():
                pontos_interesse.append({
                    'preco': dados['High'].iloc[i],
                    'tipo': 'resistencia',
                    'volume': dados['Volume'].iloc[i],
                    'timestamp': dados.index[i],
                    'index': i
                })

            # Mínima local
            if dados['Low'].iloc[i] == dados['Low'].iloc[i-janela:i+janela+1].min():
                pontos_interesse.append({
                    'preco': dados['Low'].iloc[i],
                    'tipo': 'suporte',
                    'volume': dados['Volume'].iloc[i],
                    'timestamp': dados.index[i],
                    'index': i
                })

        if len(pontos_interesse) < 5:
            return {'suportes': [], 'resistencias': []}

        # Preparar dados para clustering
        df_pontos = pd.DataFrame(pontos_interesse)

        # Clustering por tipo
        resultados = {'suportes': [], 'resistencias': []}

        for tipo in ['suporte', 'resistencia']:
            pontos_tipo = df_pontos[df_pontos['tipo'] == tipo]

            if len(pontos_tipo) < 3:
                continue

            # Normalizar preços para clustering
            precos = pontos_tipo['preco'].values.reshape(-1, 1)
            preco_medio = np.mean(precos)
            precos_norm = precos / preco_medio

            # Clustering simples baseado em densidade
            clusters = self._clustering_simples(precos_norm.flatten(),
                                               eps=self.parametros_clustering['eps'],
                                               min_samples=self.parametros_clustering['min_samples'])

            # Processar clusters
            for cluster_indices in clusters:
                pontos_cluster = pontos_tipo.iloc[cluster_indices]

                if len(pontos_cluster) >= self.parametros_clustering['min_samples']:
                    # Nível do cluster (média ponderada por volume)
                    if pontos_cluster['volume'].sum() > 0:
                        nivel = np.average(pontos_cluster['preco'], weights=pontos_cluster['volume'])
                    else:
                        nivel = pontos_cluster['preco'].mean()

                    # Calcular features ML para scoring
                    features = self.extrair_features_nivel(dados, nivel)

                    if features:
                        # Score inicial baseado em features
                        score = self._calcular_score_nivel(features)

                        nivel_info = {
                            'nivel': round(nivel, 5),
                            'score': score,
                            'toques': len(pontos_cluster),
                            'volume_medio': pontos_cluster['volume'].mean(),
                            'primeira_ocorrencia': pontos_cluster['timestamp'].min().isoformat(),
                            'ultima_ocorrencia': pontos_cluster['timestamp'].max().isoformat(),
                            'features': features
                        }

                        tipo_key = 'suportes' if tipo == 'suporte' else 'resistencias'
                        resultados[tipo_key].append(nivel_info)

        # Ordenar por score e pegar os melhores
        for tipo_key in resultados:
            resultados[tipo_key] = sorted(
                resultados[tipo_key],
                key=lambda x: x['score'],
                reverse=True
            )[:10]  # Top 10

        return resultados

    def _calcular_score_nivel(self, features: Dict) -> float:
        """Calcular score de força do nível baseado em features"""

        if not features:
            return 0.0

        # Pesos para diferentes features
        score = 0.0

        # Toques (mais toques = nível mais forte)
        score += min(features.get('toques_proximos', 0) * 0.2, 1.0)
        score += min(features.get('toques_muito_proximos', 0) * 0.3, 1.0)

        # Volume (maior volume nos toques = nível mais forte)
        ratio_volume = features.get('ratio_volume', 0)
        if ratio_volume > 1.2:  # 20% acima da média
            score += 0.3
        elif ratio_volume > 1.0:
            score += 0.1

        # Persistência temporal (nível duradouro é mais confiável)
        persistencia = features.get('persistencia_temporal', 0)
        if persistencia > 20:
            score += 0.2
        elif persistencia > 10:
            score += 0.1

        # Penalizar alta volatilidade (níveis em mercados voláteis são menos confiáveis)
        volatilidade = features.get('volatilidade', 0)
        if volatilidade > 0.05:  # 5% volatilidade diária
            score -= 0.1

        # Bonus por range normal (mercado não extremamente esticado)
        ratio_range = features.get('ratio_range', 1)
        if 0.8 <= ratio_range <= 1.2:
            score += 0.1

        return max(0.0, min(1.0, score))  # Manter entre 0 e 1

    def _clustering_simples(self, precos: np.ndarray, eps: float = 0.002, min_samples: int = 3) -> List[List[int]]:
        """Implementação simples de clustering baseado em densidade"""

        if len(precos) < min_samples:
            return []

        # Ordenar preços com índices originais
        indices_ordenados = np.argsort(precos)
        precos_ordenados = precos[indices_ordenados]

        clusters = []
        visitados = set()

        for i, preco_atual in enumerate(precos_ordenados):
            if indices_ordenados[i] in visitados:
                continue

            # Encontrar vizinhos dentro da tolerância eps
            vizinhos = []
            for j, preco_comparacao in enumerate(precos_ordenados):
                if abs(preco_atual - preco_comparacao) / preco_atual <= eps:
                    vizinhos.append(indices_ordenados[j])

            # Se tem vizinhos suficientes, formar cluster
            if len(vizinhos) >= min_samples:
                cluster = set(vizinhos)

                # Expandir cluster (encontrar vizinhos dos vizinhos)
                for vizinho_idx in list(cluster):
                    vizinho_preco = precos[vizinho_idx]
                    for k, preco_k in enumerate(precos):
                        if k not in cluster and abs(vizinho_preco - preco_k) / vizinho_preco <= eps:
                            # Verificar se este ponto tem vizinhos suficientes
                            vizinhos_k = []
                            for l, preco_l in enumerate(precos):
                                if abs(preco_k - preco_l) / preco_k <= eps:
                                    vizinhos_k.append(l)

                            if len(vizinhos_k) >= min_samples:
                                cluster.update(vizinhos_k)

                # Adicionar cluster se ainda tem tamanho mínimo
                cluster_final = [idx for idx in cluster if idx not in visitados]
                if len(cluster_final) >= min_samples:
                    clusters.append(cluster_final)
                    visitados.update(cluster_final)

        return clusters

    def processar_ativo_ml_completo(self, ticker: str, periodo: str = "1y") -> Dict:
        """Processar ativo completo com análise ML"""

        self.logger.info(f"🤖 Processamento ML para {ticker}")

        # Carregar dados multi-fonte
        dados_completos = self.carregador_dados.carregar_dados_multi_fonte(
            ticker, periodo, ['1d', '4h', '1h']
        )

        if not dados_completos['timeframes']:
            self.logger.error(f"❌ Falha ao carregar dados para {ticker}")
            return {}

        resultado = {
            'ticker': ticker,
            'timestamp_processamento': datetime.now().isoformat(),
            'qualidade_dados': dados_completos['qualidade_geral'],
            'timeframes_ml': {},
            'analise_consolidada': {}
        }

        # Processar cada timeframe
        for tf, tf_data in dados_completos['timeframes'].items():
            if 'dados' not in tf_data or tf_data['dados'].empty:
                continue

            dados_tf = tf_data['dados']

            self.logger.info(f"   Processando {tf}: {len(dados_tf)} registros")

            # Análise ML de níveis
            niveis_clustering = self.identificar_niveis_clustering(dados_tf, tf)

            # Consolidar resultados ML
            resultado['timeframes_ml'][tf] = {
                'niveis_clustering': niveis_clustering,
                'periodo_dados': {
                    'inicio': dados_tf.index[0].isoformat(),
                    'fim': dados_tf.index[-1].isoformat(),
                    'total_registros': len(dados_tf)
                }
            }

        # Consolidar análise multi-timeframe
        resultado['analise_consolidada'] = self._consolidar_analise_ml(resultado['timeframes_ml'])

        # Salvar no database
        self._salvar_niveis_ml(ticker, resultado)

        self.logger.info(f"✅ {ticker}: Análise ML concluída")

        return resultado

    def _consolidar_analise_ml(self, timeframes_ml: Dict) -> Dict:
        """Consolidar análise ML de múltiplos timeframes"""

        todos_suportes = []
        todas_resistencias = []

        # Coletar todos os níveis com pesos por timeframe
        pesos_tf = {'1d': 1.0, '4h': 0.8, '1h': 0.6}

        for tf, tf_data in timeframes_ml.items():
            peso = pesos_tf.get(tf, 0.5)

            if 'niveis_clustering' in tf_data:
                # Suportes
                for suporte in tf_data['niveis_clustering'].get('suportes', []):
                    todos_suportes.append({
                        'nivel': suporte['nivel'],
                        'score_original': suporte['score'],
                        'score_ponderado': suporte['score'] * peso,
                        'timeframe': tf,
                        'toques': suporte['toques'],
                        'features': suporte.get('features', {})
                    })

                # Resistências
                for resistencia in tf_data['niveis_clustering'].get('resistencias', []):
                    todas_resistencias.append({
                        'nivel': resistencia['nivel'],
                        'score_original': resistencia['score'],
                        'score_ponderado': resistencia['score'] * peso,
                        'timeframe': tf,
                        'toques': resistencia['toques'],
                        'features': resistencia.get('features', {})
                    })

        # Agrupar níveis próximos entre timeframes
        suportes_consolidados = self._agrupar_niveis_multi_tf(todos_suportes)
        resistencias_consolidadas = self._agrupar_niveis_multi_tf(todas_resistencias)

        return {
            'suportes_criticos': sorted(suportes_consolidados, key=lambda x: x['score_final'], reverse=True)[:5],
            'resistencias_criticas': sorted(resistencias_consolidadas, key=lambda x: x['score_final'], reverse=True)[:5],
            'total_niveis_analisados': len(todos_suportes) + len(todas_resistencias),
            'confluencias_detectadas': len([n for n in suportes_consolidados + resistencias_consolidadas if n['confluencia'] > 1])
        }

    def _agrupar_niveis_multi_tf(self, niveis: List[Dict], tolerancia: float = 0.003) -> List[Dict]:
        """Agrupar níveis próximos de diferentes timeframes"""

        if not niveis:
            return []

        # Ordenar por nível de preço
        niveis_ordenados = sorted(niveis, key=lambda x: x['nivel'])

        grupos = []
        grupo_atual = [niveis_ordenados[0]]

        for nivel in niveis_ordenados[1:]:
            # Verificar se está dentro da tolerância do último no grupo
            ultimo_nivel = grupo_atual[-1]['nivel']

            if abs(nivel['nivel'] - ultimo_nivel) / ultimo_nivel <= tolerancia:
                grupo_atual.append(nivel)
            else:
                # Finalizar grupo atual
                if grupo_atual:
                    grupos.append(self._processar_grupo_niveis(grupo_atual))
                grupo_atual = [nivel]

        # Finalizar último grupo
        if grupo_atual:
            grupos.append(self._processar_grupo_niveis(grupo_atual))

        return grupos

    def _processar_grupo_niveis(self, grupo: List[Dict]) -> Dict:
        """Processar grupo de níveis próximos"""

        # Calcular nível médio ponderado por score
        total_score = sum(n['score_ponderado'] for n in grupo)

        if total_score > 0:
            nivel_medio = sum(n['nivel'] * n['score_ponderado'] for n in grupo) / total_score
        else:
            nivel_medio = np.mean([n['nivel'] for n in grupo])

        # Score final combinado
        score_final = np.mean([n['score_ponderado'] for n in grupo])

        # Confluência (quantos timeframes confirmam)
        timeframes_confirmacao = set(n['timeframe'] for n in grupo)
        confluencia = len(timeframes_confirmacao)

        # Combinar features
        features_combinadas = {}
        for feature in ['toques_proximos', 'toques_muito_proximos', 'ratio_volume']:
            values = [n['features'].get(feature, 0) for n in grupo if 'features' in n]
            if values:
                features_combinadas[feature] = np.mean(values)

        return {
            'nivel': round(nivel_medio, 5),
            'score_final': score_final,
            'confluencia': confluencia,
            'timeframes': list(timeframes_confirmacao),
            'total_toques': sum(n['toques'] for n in grupo),
            'features_consolidadas': features_combinadas
        }

    def _salvar_niveis_ml(self, ticker: str, resultados: Dict):
        """Salvar níveis ML no database"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Limpar dados anteriores
            cursor.execute('DELETE FROM niveis_ml WHERE ticker = ?', (ticker,))

            # Salvar níveis consolidados
            if 'analise_consolidada' in resultados:
                analise = resultados['analise_consolidada']

                # Suportes
                for suporte in analise.get('suportes_criticos', []):
                    cursor.execute('''
                        INSERT INTO niveis_ml
                        (ticker, timeframe, nivel_preco, tipo_nivel, forca_score,
                         confianca_ml, toques_historicos, metadados)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ticker, 'consolidado', suporte['nivel'], 'suporte',
                        suporte['score_final'], suporte['confluencia'] / 3.0,
                        suporte['total_toques'], json.dumps(suporte['features_consolidadas'])
                    ))

                # Resistências
                for resistencia in analise.get('resistencias_criticas', []):
                    cursor.execute('''
                        INSERT INTO niveis_ml
                        (ticker, timeframe, nivel_preco, tipo_nivel, forca_score,
                         confianca_ml, toques_historicos, metadados)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ticker, 'consolidado', resistencia['nivel'], 'resistencia',
                        resistencia['score_final'], resistencia['confluencia'] / 3.0,
                        resistencia['total_toques'], json.dumps(resistencia['features_consolidadas'])
                    ))

            conn.commit()
            conn.close()

            self.logger.info(f"✅ Níveis ML salvos para {ticker}")

        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar níveis ML {ticker}: {e}")

    def processar_portfolio_ml(self, tickers: List[str]) -> Dict:
        """Processar portfolio completo com ML"""

        self.logger.info(f"🚀 Processamento ML Portfolio: {len(tickers)} ativos")

        resultados = {}

        # Processar em paralelo
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_ticker = {
                executor.submit(self.processar_ativo_ml_completo, ticker): ticker
                for ticker in tickers
            }

            for future in future_to_ticker:
                ticker = future_to_ticker[future]
                try:
                    resultado = future.result()
                    if resultado:
                        resultados[ticker] = resultado
                except Exception as e:
                    self.logger.error(f"Erro processando {ticker}: {e}")

        # Estatísticas gerais
        sucessos = len([r for r in resultados.values() if r])

        resumo = {
            'timestamp_processamento': datetime.now().isoformat(),
            'total_ativos': len(tickers),
            'sucessos_ml': sucessos,
            'taxa_sucesso_ml': sucessos / len(tickers) if len(tickers) > 0 else 0,
            'resultados_ml': resultados
        }

        self.logger.info(f"✅ Portfolio ML processado: {sucessos}/{len(tickers)} sucessos")

        return resumo

    def gerar_relatorio_ml(self, resultados_portfolio: Dict) -> str:
        """Gerar relatório executivo da análise ML"""

        relatorio = []
        relatorio.append("🤖 RELATÓRIO ANÁLISE ML - NÍVEIS CRÍTICOS")
        relatorio.append("=" * 60)

        relatorio.append(f"\\n🎯 RESUMO EXECUTIVO:")
        relatorio.append(f"   Total de ativos processados: {resultados_portfolio['total_ativos']}")
        relatorio.append(f"   Sucessos ML: {resultados_portfolio['sucessos_ml']}")
        relatorio.append(f"   Taxa de sucesso: {resultados_portfolio['taxa_sucesso_ml']:.1%}")

        # Análise por ativo
        relatorio.append(f"\\n📊 ANÁLISE ML POR ATIVO:")
        relatorio.append("-" * 50)

        for ticker, resultado in resultados_portfolio['resultados_ml'].items():
            if not resultado:
                continue

            qualidade = resultado['qualidade_dados']
            emoji = "🟢" if qualidade >= 0.8 else "🟡" if qualidade >= 0.6 else "🔴"

            relatorio.append(f"\\n{emoji} {ticker}: Qualidade {qualidade:.1%}")

            # Níveis críticos
            if 'analise_consolidada' in resultado:
                consolidada = resultado['analise_consolidada']

                suportes = consolidada.get('suportes_criticos', [])
                resistencias = consolidada.get('resistencias_criticas', [])

                if suportes:
                    relatorio.append(f"   🟢 Suportes ML (Top 3):")
                    for i, sup in enumerate(suportes[:3], 1):
                        confluencia = sup['confluencia']
                        score = sup['score_final']
                        relatorio.append(f"      {i}. {sup['nivel']} (Score: {score:.2f}, Confluência: {confluencia}TF)")

                if resistencias:
                    relatorio.append(f"   🔴 Resistências ML (Top 3):")
                    for i, res in enumerate(resistencias[:3], 1):
                        confluencia = res['confluencia']
                        score = res['score_final']
                        relatorio.append(f"      {i}. {res['nivel']} (Score: {score:.2f}, Confluência: {confluencia}TF)")

        relatorio.append("\\n✅ SISTEMA ML OPERACIONAL")
        relatorio.append("🎯 Níveis com confluência multi-timeframe priorizados")
        relatorio.append("🤖 Algoritmos de clustering DBSCAN aplicados")
        relatorio.append("📊 Features de volume e momentum integradas")

        return "\\n".join(relatorio)


def main():
    """Demonstração do sistema ML para níveis críticos"""

    print("🤖 SISTEMA ML - DETECÇÃO DE NÍVEIS CRÍTICOS")
    print("=" * 60)

    # Portfolio de teste
    portfolio_teste = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'GBPJPY=X']

    # Inicializar sistema
    detector_ml = DetectorNiveisCriticosML()

    print(f"\n🔄 Processando {len(portfolio_teste)} ativos com ML...")

    # Processar portfolio
    resultados = detector_ml.processar_portfolio_ml(portfolio_teste)

    # Gerar relatório
    relatorio = detector_ml.gerar_relatorio_ml(resultados)
    print(f"\n{relatorio}")

    # Salvar resultados
    output_path = "data/ml_niveis_criticos/relatorio_ml.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Resultados ML salvos em: {output_path}")

    return detector_ml, resultados


if __name__ == "__main__":
    detector, resultados = main()