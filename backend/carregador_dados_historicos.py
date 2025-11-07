"""
Sistema de Carregamento de Dados Históricos de Alta Precisão
Engenheiro ML: Estruturação de dados para análise de níveis de preço

Funcionalidades:
1. Multi-fonte de dados (Yahoo Finance, Alpha Vantage, APIs alternativas)
2. Validação e limpeza automática de dados
3. Estruturação multi-timeframe com sincronização
4. Detecção de gaps, outliers e inconsistências
5. Cache inteligente e compressão de dados
6. Metadados de qualidade e completude
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
import sqlite3
import gzip
import pickle
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

class CarregadorDadosHistoricos:
    """Sistema avançado de carregamento e estruturação de dados históricos"""

    def __init__(self, api_key_alpha_vantage: Optional[str] = None):
        self.logger = self._configurar_logger()
        self.api_key_av = api_key_alpha_vantage or os.getenv('ALPHA_VANTAGE_API_KEY')

        # Diretórios de cache
        self.cache_dir = "data/cache_dados_historicos"
        self.db_path = os.path.join(self.cache_dir, "dados_historicos.db")

        # Criar estrutura
        os.makedirs(self.cache_dir, exist_ok=True)
        self._inicializar_database()

        # Configurações de qualidade
        self.min_periodo_dados = 365  # dias mínimos
        self.max_gap_permitido = 5    # dias máximos de gap
        self.outlier_threshold = 5.0  # desvios padrão para outliers

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('CarregadorDados')
        logger.setLevel(logging.INFO)
        return logger

    def _inicializar_database(self):
        """Inicializar database SQLite para cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dados_historicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                fonte TEXT NOT NULL,
                hash_dados TEXT UNIQUE NOT NULL,
                qualidade_score REAL NOT NULL,
                metadados TEXT,
                dados_comprimidos BLOB NOT NULL,
                timestamp_cache DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, timeframe, data_inicio, data_fim, fonte)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ticker_timeframe
            ON dados_historicos(ticker, timeframe)
        ''')

        conn.commit()
        conn.close()

    def carregar_dados_multi_fonte(self, ticker: str,
                                  periodo: str = "2y",
                                  timeframes: List[str] = None) -> Dict:
        """Carregar dados de múltiplas fontes com validação"""

        if timeframes is None:
            timeframes = ['1d', '1h', '4h', '1wk']

        self.logger.info(f"🔄 Carregando dados para {ticker}")

        resultado = {
            'ticker': ticker,
            'timestamp_carregamento': datetime.now().isoformat(),
            'timeframes': {},
            'qualidade_geral': 0.0,
            'fontes_utilizadas': [],
            'metadados': {}
        }

        for tf in timeframes:
            self.logger.info(f"   Processando timeframe {tf}...")

            # Tentar cache primeiro
            dados_cache = self._obter_do_cache(ticker, tf, periodo)

            if dados_cache and self._validar_cache_atual(dados_cache):
                resultado['timeframes'][tf] = dados_cache
                self.logger.info(f"   ✅ Dados do cache utilizados para {tf}")
                continue

            # Carregar de fontes externas
            dados_tf = self._carregar_timeframe_multi_fonte(ticker, tf, periodo)

            if dados_tf['dados'] is not None:
                # Validar e processar dados
                dados_processados = self._processar_dados_brutos(dados_tf['dados'], tf)

                # Calcular score de qualidade
                qualidade = self._calcular_qualidade_dados(dados_processados)

                resultado_tf = {
                    'dados': dados_processados,
                    'fonte_primaria': dados_tf['fonte'],
                    'qualidade_score': qualidade,
                    'periodo_real': self._calcular_periodo_real(dados_processados),
                    'gaps_detectados': self._detectar_gaps(dados_processados),
                    'outliers_corrigidos': dados_tf.get('outliers_corrigidos', 0),
                    'metadados': dados_tf.get('metadados', {})
                }

                # Salvar no cache se qualidade boa
                if qualidade >= 0.8:
                    self._salvar_no_cache(ticker, tf, periodo, resultado_tf)

                resultado['timeframes'][tf] = resultado_tf
                resultado['fontes_utilizadas'].append(dados_tf['fonte'])

                self.logger.info(f"   ✅ {tf}: {len(dados_processados)} registros, qualidade {qualidade:.2%}")
            else:
                self.logger.warning(f"   ❌ Falha ao carregar dados para {tf}")

        # Calcular qualidade geral
        if resultado['timeframes']:
            qualidades = [tf['qualidade_score'] for tf in resultado['timeframes'].values()]
            resultado['qualidade_geral'] = np.mean(qualidades)

        resultado['fontes_utilizadas'] = list(set(resultado['fontes_utilizadas']))

        self.logger.info(f"✅ Carregamento concluído para {ticker}: qualidade {resultado['qualidade_geral']:.2%}")

        return resultado

    def _carregar_timeframe_multi_fonte(self, ticker: str, timeframe: str, periodo: str) -> Dict:
        """Carregar dados de um timeframe específico tentando múltiplas fontes"""

        fontes = [
            ('yahoo_finance', self._carregar_yahoo_finance),
            ('alpha_vantage', self._carregar_alpha_vantage)
        ]

        for nome_fonte, funcao_fonte in fontes:
            try:
                dados = funcao_fonte(ticker, timeframe, periodo)

                if dados is not None and not dados.empty:
                    # Validação básica
                    if self._validar_dados_basicos(dados):
                        return {
                            'dados': dados,
                            'fonte': nome_fonte,
                            'metadados': {
                                'registros_originais': len(dados),
                                'periodo_cobertura': f"{dados.index[0]} a {dados.index[-1]}"
                            }
                        }

            except Exception as e:
                self.logger.warning(f"Erro na fonte {nome_fonte} para {ticker}: {e}")
                continue

        return {'dados': None, 'fonte': None}

    def _carregar_yahoo_finance(self, ticker: str, timeframe: str, periodo: str) -> pd.DataFrame:
        """Carregar dados do Yahoo Finance"""

        # Mapear timeframes para Yahoo Finance
        tf_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '2h': '2h', '4h': '4h',
            '1d': '1d', '1wk': '1wk', '1mo': '1mo'
        }

        if timeframe not in tf_map:
            return None

        try:
            # Converter ticker para formato Yahoo se necessário
            ticker_yahoo = self._converter_ticker_yahoo(ticker)

            # Definir período de dados baseado no timeframe
            if timeframe in ['1m', '5m']:
                periodo_yf = "7d"   # Limitação do Yahoo para dados intraday
            elif timeframe in ['15m', '30m', '1h']:
                periodo_yf = "60d"  # ~2 meses para timeframes maiores
            else:
                periodo_yf = periodo  # Usar período original para daily+

            ticker_obj = yf.Ticker(ticker_yahoo)
            dados = ticker_obj.history(
                period=periodo_yf,
                interval=tf_map[timeframe],
                auto_adjust=True,
                prepost=True
            )

            if dados.empty:
                return None

            # Padronizar colunas
            dados = self._padronizar_colunas(dados)

            return dados

        except Exception as e:
            self.logger.error(f"Erro Yahoo Finance {ticker}: {e}")
            return None

    def _carregar_alpha_vantage(self, ticker: str, timeframe: str, periodo: str) -> pd.DataFrame:
        """Carregar dados do Alpha Vantage (se API key disponível)"""

        if not self.api_key_av:
            return None

        # Mapeamento de timeframes para Alpha Vantage
        av_functions = {
            '1d': 'TIME_SERIES_DAILY',
            '1wk': 'TIME_SERIES_WEEKLY',
            '1mo': 'TIME_SERIES_MONTHLY'
        }

        if timeframe not in av_functions:
            return None

        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': av_functions[timeframe],
                'symbol': ticker.replace('=X', ''),  # Remover sufixo Yahoo
                'outputsize': 'full',
                'apikey': self.api_key_av
            }

            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            # Extrair dados da resposta
            if 'Time Series' in str(data):
                # Encontrar chave dos dados temporais
                key = [k for k in data.keys() if 'Time Series' in k][0]
                time_series = data[key]

                # Converter para DataFrame
                df = pd.DataFrame.from_dict(time_series, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()

                # Renomear colunas
                rename_map = {
                    '1. open': 'Open',
                    '2. high': 'High',
                    '3. low': 'Low',
                    '4. close': 'Close',
                    '5. volume': 'Volume'
                }
                df = df.rename(columns=rename_map)
                df = df.astype(float)

                return df

        except Exception as e:
            self.logger.error(f"Erro Alpha Vantage {ticker}: {e}")

        return None

    def _converter_ticker_yahoo(self, ticker: str) -> str:
        """Converter ticker para formato Yahoo Finance"""
        # Mapeamentos comuns
        conversoes = {
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'USDJPY': 'USDJPY=X',
            'AUDUSD': 'AUDUSD=X',
            'USDCAD': 'USDCAD=X',
            'USDCHF': 'USDCHF=X',
            'NZDUSD': 'NZDUSD=X',
            'EURJPY': 'EURJPY=X',
            'GBPJPY': 'GBPJPY=X',
            'AUDJPY': 'AUDJPY=X',
            'CADJPY': 'CADJPY=X',
            'CHFJPY': 'CHFJPY=X',
            'EURGBP': 'EURGBP=X',
            'EURAUD': 'EURAUD=X',
            'EURCHF': 'EURCHF=X',
            'AUDCHF': 'AUDCHF=X',
            'AUDNZD': 'AUDNZD=X',
            'GBPAUD': 'GBPAUD=X',
            'GBPCHF': 'GBPCHF=X',
            'GBPCAD': 'GBPCAD=X',
            'CADCHF': 'CADCHF=X',
            'NZDCAD': 'NZDCAD=X',
            'NZDJPY': 'NZDJPY=X',
            'GOLD': 'GC=F',
            'XAUUSD': 'GC=F',
            'SILVER': 'SI=F',
            'OIL': 'CL=F',
            'SPX': '^GSPC',
            'DXY': 'DX-Y.NYB'
        }

        return conversoes.get(ticker.upper(), ticker)

    def _padronizar_colunas(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Padronizar nomes de colunas"""
        colunas_padrao = ['Open', 'High', 'Low', 'Close', 'Volume']

        # Mapear colunas existentes
        rename_map = {}
        for col in dados.columns:
            col_lower = col.lower()
            if 'open' in col_lower:
                rename_map[col] = 'Open'
            elif 'high' in col_lower:
                rename_map[col] = 'High'
            elif 'low' in col_lower:
                rename_map[col] = 'Low'
            elif 'close' in col_lower:
                rename_map[col] = 'Close'
            elif 'volume' in col_lower:
                rename_map[col] = 'Volume'

        dados = dados.rename(columns=rename_map)

        # Garantir que Volume existe (zeros se não disponível)
        if 'Volume' not in dados.columns:
            dados['Volume'] = 0

        return dados[colunas_padrao]

    def _validar_dados_basicos(self, dados: pd.DataFrame) -> bool:
        """Validação básica da qualidade dos dados"""
        if dados.empty or len(dados) < 10:
            return False

        # Verificar colunas essenciais
        colunas_obrigatorias = ['Open', 'High', 'Low', 'Close']
        if not all(col in dados.columns for col in colunas_obrigatorias):
            return False

        # Verificar valores válidos
        for col in colunas_obrigatorias:
            if dados[col].isna().sum() / len(dados) > 0.1:  # >10% NAs
                return False
            if (dados[col] <= 0).sum() > len(dados) * 0.05:  # >5% zeros/negativos
                return False

        # Validar OHLC lógico: High >= Low, Close/Open entre High/Low
        if not ((dados['High'] >= dados['Low']).all() and
                (dados['Close'] >= dados['Low']).all() and
                (dados['Close'] <= dados['High']).all() and
                (dados['Open'] >= dados['Low']).all() and
                (dados['Open'] <= dados['High']).all()):
            return False

        return True

    def _processar_dados_brutos(self, dados: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Processar e limpar dados brutos"""

        # Cópia para não alterar original
        dados_limpos = dados.copy()

        # 1. Remover duplicatas de timestamp
        dados_limpos = dados_limpos[~dados_limpos.index.duplicated(keep='first')]

        # 2. Ordenar por timestamp
        dados_limpos = dados_limpos.sort_index()

        # 3. Detectar e corrigir outliers
        dados_limpos = self._corrigir_outliers(dados_limpos)

        # 4. Preencher gaps pequenos
        dados_limpos = self._preencher_gaps(dados_limpos, timeframe)

        # 5. Calcular campos derivados
        dados_limpos = self._calcular_campos_derivados(dados_limpos)

        # 6. Validação final
        dados_limpos = self._validacao_final(dados_limpos)

        return dados_limpos

    def _corrigir_outliers(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Detectar e corrigir outliers usando múltiplos métodos"""

        dados_corrigidos = dados.copy()

        for col in ['Open', 'High', 'Low', 'Close']:
            if col not in dados.columns:
                continue

            serie = dados[col]

            # Método 1: Z-score
            z_scores = np.abs((serie - serie.mean()) / serie.std())
            outliers_z = z_scores > self.outlier_threshold

            # Método 2: IQR
            q1, q3 = serie.quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers_iqr = (serie < q1 - 1.5 * iqr) | (serie > q3 + 1.5 * iqr)

            # Método 3: Variação percentual extrema
            pct_change = serie.pct_change().abs()
            outliers_pct = pct_change > 0.2  # >20% variação

            # Combinar detecções
            outliers = outliers_z | outliers_iqr | outliers_pct

            if outliers.sum() > 0:
                # Corrigir usando interpolação
                dados_corrigidos.loc[outliers, col] = np.nan
                dados_corrigidos[col] = dados_corrigidos[col].interpolate(method='linear')

                self.logger.info(f"Corrigidos {outliers.sum()} outliers em {col}")

        return dados_corrigidos

    def _preencher_gaps(self, dados: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Preencher gaps de dados usando forward fill limitado"""

        # Definir limite baseado no timeframe
        limite_map = {
            '1m': 5, '5m': 3, '15m': 2, '30m': 2,
            '1h': 2, '2h': 1, '4h': 1,
            '1d': 3, '1wk': 1, '1mo': 1
        }

        limite = limite_map.get(timeframe, 2)

        # Preencher gaps pequenos
        dados_preenchidos = dados.fillna(method='ffill', limit=limite)

        return dados_preenchidos

    def _calcular_campos_derivados(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Calcular campos derivados úteis"""

        dados_expandidos = dados.copy()

        # Typical Price (usado em muitos indicadores)
        dados_expandidos['Typical'] = (dados['High'] + dados['Low'] + dados['Close']) / 3

        # True Range
        dados_expandidos['TrueHigh'] = np.maximum(dados['High'], dados['Close'].shift(1))
        dados_expandidos['TrueLow'] = np.minimum(dados['Low'], dados['Close'].shift(1))
        dados_expandidos['TrueRange'] = dados_expandidos['TrueHigh'] - dados_expandidos['TrueLow']

        # Returns
        dados_expandidos['Returns'] = dados['Close'].pct_change()
        dados_expandidos['LogReturns'] = np.log(dados['Close'] / dados['Close'].shift(1))

        # Volatilidade realizada (janela móvel)
        dados_expandidos['Volatilidade20'] = dados_expandidos['LogReturns'].rolling(20).std()

        # Volume médio (se disponível)
        if dados['Volume'].sum() > 0:
            dados_expandidos['VolumeMA20'] = dados['Volume'].rolling(20).mean()
            dados_expandidos['VolumeRatio'] = dados['Volume'] / dados_expandidos['VolumeMA20']

        return dados_expandidos

    def _validacao_final(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Validação final e limpeza"""

        # Remover linhas com muitos NaNs
        threshold = len(dados.columns) * 0.5  # >50% NaN
        dados_finais = dados.dropna(thresh=threshold)

        # Remover primeiras linhas se tiverem NaNs nos campos principais
        campos_principais = ['Open', 'High', 'Low', 'Close']
        while len(dados_finais) > 0 and dados_finais[campos_principais].iloc[0].isna().any():
            dados_finais = dados_finais.iloc[1:]

        return dados_finais

    def _calcular_qualidade_dados(self, dados: pd.DataFrame) -> float:
        """Calcular score de qualidade dos dados (0-1)"""

        if dados.empty:
            return 0.0

        score = 0.0

        # Componente 1: Completude (30%)
        campos_principais = ['Open', 'High', 'Low', 'Close']
        completude = 1 - (dados[campos_principais].isna().sum().sum() /
                          (len(dados) * len(campos_principais)))
        score += completude * 0.3

        # Componente 2: Consistência OHLC (25%)
        ohlc_valido = ((dados['High'] >= dados['Low']) &
                      (dados['Close'] >= dados['Low']) &
                      (dados['Close'] <= dados['High']) &
                      (dados['Open'] >= dados['Low']) &
                      (dados['Open'] <= dados['High'])).mean()
        score += ohlc_valido * 0.25

        # Componente 3: Continuidade temporal (20%)
        gaps = self._detectar_gaps(dados)
        continuidade = max(0, 1 - len(gaps) / max(1, len(dados) * 0.05))
        score += continuidade * 0.2

        # Componente 4: Volume de dados (15%)
        tamanho_esperado = 252 if '1d' in str(dados.index.freq) else len(dados)
        volume_score = min(1.0, len(dados) / max(1, tamanho_esperado))
        score += volume_score * 0.15

        # Componente 5: Variabilidade (10%)
        if len(dados) > 1:
            cv = dados['Close'].std() / dados['Close'].mean()
            variabilidade = min(1.0, cv * 10)  # Normalizar
        else:
            variabilidade = 0
        score += variabilidade * 0.1

        return min(1.0, score)

    def _detectar_gaps(self, dados: pd.DataFrame) -> List[Dict]:
        """Detectar gaps nos dados temporais"""

        if len(dados) < 2:
            return []

        gaps = []
        timestamps = dados.index

        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i-1]

            # Definir gap esperado baseado na frequência
            if hasattr(timestamps, 'freq') and timestamps.freq:
                gap_esperado = timestamps.freq
            else:
                # Estimar frequência
                gaps_comuns = pd.Series([timestamps[j] - timestamps[j-1] for j in range(1, min(10, len(timestamps)))])
                gap_esperado = gaps_comuns.mode()[0] if not gaps_comuns.empty else pd.Timedelta(days=1)

            # Detectar se gap é anormal
            if diff > gap_esperado * 3:  # 3x maior que esperado
                gaps.append({
                    'inicio': timestamps[i-1],
                    'fim': timestamps[i],
                    'duracao': diff,
                    'posicao': i
                })

        return gaps

    def _calcular_periodo_real(self, dados: pd.DataFrame) -> Dict:
        """Calcular período real dos dados"""
        if dados.empty:
            return {}

        return {
            'inicio': dados.index[0].isoformat(),
            'fim': dados.index[-1].isoformat(),
            'total_registros': len(dados),
            'total_dias': (dados.index[-1] - dados.index[0]).days
        }

    def _obter_do_cache(self, ticker: str, timeframe: str, periodo: str) -> Optional[Dict]:
        """Obter dados do cache local"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Buscar entrada mais recente
            cursor.execute('''
                SELECT dados_comprimidos, qualidade_score, metadados, timestamp_cache
                FROM dados_historicos
                WHERE ticker = ? AND timeframe = ?
                ORDER BY timestamp_cache DESC LIMIT 1
            ''', (ticker, timeframe))

            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                dados_comprimidos, qualidade, metadados_json, timestamp = resultado

                # Descomprimir dados
                dados_bytes = gzip.decompress(dados_comprimidos)
                dados_dict = pickle.loads(dados_bytes)

                return {
                    'dados': pd.DataFrame(dados_dict['dados']),
                    'qualidade_score': qualidade,
                    'metadados': json.loads(metadados_json) if metadados_json else {},
                    'timestamp_cache': timestamp
                }

        except Exception as e:
            self.logger.warning(f"Erro ao acessar cache: {e}")

        return None

    def _validar_cache_atual(self, dados_cache: Dict) -> bool:
        """Validar se dados do cache ainda são atuais"""

        timestamp_cache = datetime.fromisoformat(dados_cache['timestamp_cache'])
        idade_horas = (datetime.now() - timestamp_cache).total_seconds() / 3600

        # Cache válido por diferentes períodos baseado na qualidade
        if dados_cache['qualidade_score'] >= 0.9:
            limite_horas = 24  # 1 dia para alta qualidade
        elif dados_cache['qualidade_score'] >= 0.7:
            limite_horas = 12  # 12 horas para boa qualidade
        else:
            limite_horas = 6   # 6 horas para qualidade baixa

        return idade_horas < limite_horas

    def _salvar_no_cache(self, ticker: str, timeframe: str, periodo: str, dados: Dict):
        """Salvar dados no cache comprimido"""
        try:
            # Preparar dados para serialização
            dados_para_cache = {
                'dados': dados['dados'].to_dict(),
                'fonte_primaria': dados['fonte_primaria'],
                'periodo_real': dados['periodo_real']
            }

            # Comprimir dados
            dados_bytes = pickle.dumps(dados_para_cache)
            dados_comprimidos = gzip.compress(dados_bytes)

            # Calcular hash
            hash_dados = hashlib.md5(dados_bytes).hexdigest()

            # Salvar no database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO dados_historicos
                (ticker, timeframe, data_inicio, data_fim, fonte, hash_dados,
                 qualidade_score, metadados, dados_comprimidos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticker, timeframe,
                dados['periodo_real']['inicio'][:10],  # Data apenas
                dados['periodo_real']['fim'][:10],
                dados['fonte_primaria'],
                hash_dados,
                dados['qualidade_score'],
                json.dumps(dados['metadados']),
                dados_comprimidos
            ))

            conn.commit()
            conn.close()

            self.logger.info(f"Dados salvos no cache: {ticker} {timeframe}")

        except Exception as e:
            self.logger.error(f"Erro ao salvar cache: {e}")

    def processar_portfolio_completo(self, tickers: List[str],
                                   periodo: str = "2y",
                                   timeframes: List[str] = None) -> Dict:
        """Processar portfolio completo em paralelo"""

        self.logger.info(f"🚀 Processando portfolio com {len(tickers)} ativos")

        resultados = {}

        # Processar em paralelo para eficiência
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {
                executor.submit(self.carregar_dados_multi_fonte, ticker, periodo, timeframes): ticker
                for ticker in tickers
            }

            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    resultado = future.result()
                    resultados[ticker] = resultado
                except Exception as e:
                    self.logger.error(f"Erro processando {ticker}: {e}")
                    resultados[ticker] = None

        # Estatísticas gerais
        sucessos = sum(1 for r in resultados.values() if r and r['qualidade_geral'] > 0.5)
        qualidade_media = np.mean([r['qualidade_geral'] for r in resultados.values()
                                  if r and r['qualidade_geral'] > 0])

        resumo = {
            'timestamp_processamento': datetime.now().isoformat(),
            'total_ativos': len(tickers),
            'sucessos': sucessos,
            'taxa_sucesso': sucessos / len(tickers),
            'qualidade_media': qualidade_media,
            'resultados': resultados
        }

        self.logger.info(f"✅ Portfolio processado: {sucessos}/{len(tickers)} sucessos, qualidade média {qualidade_media:.2%}")

        return resumo

    def gerar_relatorio_qualidade(self, dados_portfolio: Dict) -> str:
        """Gerar relatório de qualidade dos dados"""

        relatorio = []
        relatorio.append("📊 RELATÓRIO DE QUALIDADE DOS DADOS HISTÓRICOS")
        relatorio.append("=" * 70)

        resultados = dados_portfolio['resultados']

        relatorio.append(f"\n🎯 RESUMO EXECUTIVO:")
        relatorio.append(f"   Total de ativos: {dados_portfolio['total_ativos']}")
        relatorio.append(f"   Sucessos: {dados_portfolio['sucessos']}")
        relatorio.append(f"   Taxa de sucesso: {dados_portfolio['taxa_sucesso']:.1%}")
        relatorio.append(f"   Qualidade média: {dados_portfolio['qualidade_media']:.1%}")

        # Análise por ativo
        relatorio.append(f"\n📈 QUALIDADE POR ATIVO:")
        relatorio.append("-" * 40)

        for ticker, dados in resultados.items():
            if dados:
                qualidade = dados['qualidade_geral']
                emoji = "🟢" if qualidade >= 0.8 else "🟡" if qualidade >= 0.6 else "🔴"

                relatorio.append(f"{emoji} {ticker}: {qualidade:.1%}")

                # Detalhar timeframes
                for tf, tf_data in dados['timeframes'].items():
                    registros = len(tf_data['dados'])
                    tf_qualidade = tf_data['qualidade_score']
                    relatorio.append(f"   {tf}: {registros} registros, {tf_qualidade:.1%}")
            else:
                relatorio.append(f"🔴 {ticker}: FALHA NO CARREGAMENTO")

        # Estatísticas de fontes
        todas_fontes = []
        for dados in resultados.values():
            if dados:
                todas_fontes.extend(dados['fontes_utilizadas'])

        if todas_fontes:
            relatorio.append(f"\n🔌 FONTES UTILIZADAS:")
            from collections import Counter
            contagem_fontes = Counter(todas_fontes)
            for fonte, count in contagem_fontes.items():
                relatorio.append(f"   {fonte}: {count} utilizações")

        return "\n".join(relatorio)


def main():
    """Demonstração do sistema de carregamento"""
    print("📊 SISTEMA DE CARREGAMENTO DE DADOS HISTÓRICOS")
    print("=" * 70)

    # Inicializar carregador
    carregador = CarregadorDadosHistoricos()

    # Portfolio de teste
    portfolio_teste = [
        'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X',
        'GBPJPY=X', 'EURJPY=X', 'GC=F'
    ]

    timeframes_teste = ['1d', '4h', '1h']

    print(f"\n🔄 Carregando dados para {len(portfolio_teste)} ativos...")

    # Processar portfolio
    resultados = carregador.processar_portfolio_completo(
        portfolio_teste,
        periodo="1y",
        timeframes=timeframes_teste
    )

    # Gerar relatório
    print(f"\n" + carregador.gerar_relatorio_qualidade(resultados))

    # Salvar resultados
    output_path = "data/cache_dados_historicos/relatorio_carregamento.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        # Converter DataFrames para dict para serialização
        resultados_serializaveis = {}
        for ticker, dados in resultados['resultados'].items():
            if dados:
                dados_copia = dados.copy()
                for tf in dados_copia['timeframes']:
                    df = dados_copia['timeframes'][tf]['dados']
                    # Converter index datetime para string
                    df_dict = df.to_dict('index')
                    df_dict_str_keys = {str(k): v for k, v in df_dict.items()}
                    dados_copia['timeframes'][tf]['dados'] = df_dict_str_keys
                resultados_serializaveis[ticker] = dados_copia

        resultados_copy = resultados.copy()
        resultados_copy['resultados'] = resultados_serializaveis
        json.dump(resultados_copy, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Resultados salvos em: {output_path}")

    return carregador, resultados


if __name__ == "__main__":
    carregador, resultados = main()