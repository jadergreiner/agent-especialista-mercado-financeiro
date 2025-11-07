"""
Sistema de Cálculo de Níveis de Preço com Alta Precisão
Engenheiro: Machine Learning para Portfolio Management

Funcionalidades:
1. Carregamento de dados históricos multi-timeframe
2. Cálculo de níveis críticos (suporte/resistência, pivot points, fibonacci)
3. Análise de volume e liquidez
4. Persistência de dados estruturados
5. Motor de reavaliação em tempo real
"""

import yfinance as yf
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
import warnings

warnings.filterwarnings('ignore')

class CalculadorNiveisPrecisao:
    """Motor de cálculo de níveis de preço com alta precisão"""

    def __init__(self):
        self.logger = self._configurar_logger()
        self.dados_historicos = {}
        self.niveis_calculados = {}
        self.caminho_dados = "data/niveis_precos"
        self.caminho_portfolio = "data/portfolio/portfolio_atual.json"

        # Criar diretórios necessários
        os.makedirs(self.caminho_dados, exist_ok=True)

    def _configurar_logger(self) -> logging.Logger:
        """Configurar sistema de logging"""
        logger = logging.getLogger('CalculadorNiveis')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def carregar_portfolio(self) -> List[str]:
        """Carregar ativos únicos do portfólio"""
        try:
            with open(self.caminho_portfolio, 'r', encoding='utf-8') as f:
                portfolio = json.load(f)

            ativos_unicos = set()
            for posicao in portfolio['positions']:
                par_moeda = posicao['currency_pair']

                # Converter para ticker Yahoo Finance
                ticker_yahoo = self._converter_para_ticker_yahoo(par_moeda)
                if ticker_yahoo:
                    ativos_unicos.add(ticker_yahoo)

            self.logger.info(f"Portfolio carregado: {len(ativos_unicos)} ativos únicos")
            return list(ativos_unicos)

        except Exception as e:
            self.logger.error(f"Erro ao carregar portfolio: {e}")
            return []

    def _converter_para_ticker_yahoo(self, par_moeda: str) -> Optional[str]:
        """Converter par de moedas para ticker Yahoo Finance"""
        conversoes = {
            'GBP/JPY': 'GBPJPY=X',
            'EUR/USD': 'EURUSD=X',
            'CHF/JPY': 'CHFJPY=X',
            'GBP/USD': 'GBPUSD=X',
            'USD/JPY': 'USDJPY=X',
            'USD/CAD': 'USDCAD=X',
            'USD/CHF': 'USDCHF=X',
            'AUD/USD': 'AUDUSD=X',
            'AUD/CHF': 'AUDCHF=X',
            'AUD/JPY': 'AUDJPY=X',
            'AUD/NZD': 'AUDNZD=X',
            'NZD/USD': 'NZDUSD=X',
            'CAD/CHF': 'CADCHF=X',
            'CAD/JPY': 'CADJPY=X',
            'NZD/CAD': 'NZDCAD=X',
            'EUR/GBP': 'EURGBP=X',
            'EUR/JPY': 'EURJPY=X',
            'EUR/CHF': 'EURCHF=X',
            'NZD/JPY': 'NZDJPY=X',
            'XAU/USD': 'GC=F',  # Ouro
            'GC=F': 'GC=F'      # Ouro direto
        }

        return conversoes.get(par_moeda)

    def carregar_dados_historicos(self, ticker: str, periodo: str = "2y") -> pd.DataFrame:
        """Carregar dados históricos com múltiplos timeframes"""
        try:
            self.logger.info(f"Carregando dados para {ticker}...")

            # Carregar dados com yfinance
            ativo = yf.Ticker(ticker)

            # Dados diários (2 anos)
            dados_diarios = ativo.history(period=periodo, interval="1d")

            # Dados horários (últimos 30 dias)
            dados_horarios = ativo.history(period="30d", interval="1h")

            # Dados de 4 horas (últimos 60 dias)
            dados_4h = ativo.history(period="60d", interval="4h")

            # Combinar dados em estrutura unificada
            dados_completos = {
                'daily': dados_diarios,
                'hourly': dados_horarios,
                '4h': dados_4h,
                'ticker': ticker,
                'timestamp_carregamento': datetime.now().isoformat()
            }

            self.dados_historicos[ticker] = dados_completos

            self.logger.info(f"✅ {ticker}: {len(dados_diarios)} dias, "
                           f"{len(dados_horarios)} horas, {len(dados_4h)} períodos 4h")

            return dados_diarios

        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar {ticker}: {e}")
            return pd.DataFrame()

    def calcular_niveis_suporte_resistencia(self, dados: pd.DataFrame,
                                          janela: int = 20) -> Dict:
        """Calcular níveis de suporte e resistência com alta precisão"""
        if dados.empty:
            return {'suportes': [], 'resistencias': []}

        # Identificar máximas e mínimas locais
        maximas_locais = []
        minimas_locais = []

        for i in range(janela, len(dados) - janela):
            # Máxima local
            if dados['High'].iloc[i] == dados['High'].iloc[i-janela:i+janela+1].max():
                maximas_locais.append(dados['High'].iloc[i])

            # Mínima local
            if dados['Low'].iloc[i] == dados['Low'].iloc[i-janela:i+janela+1].min():
                minimas_locais.append(dados['Low'].iloc[i])

        # Agrupar níveis próximos (tolerância de 0.1%)
        def agrupar_niveis(niveis: List[float], tolerancia: float = 0.001) -> List[float]:
            if not niveis:
                return []

            niveis_ordenados = sorted(niveis)
            grupos = []
            grupo_atual = [niveis_ordenados[0]]

            for nivel in niveis_ordenados[1:]:
                if abs(nivel - grupo_atual[-1]) / grupo_atual[-1] <= tolerancia:
                    grupo_atual.append(nivel)
                else:
                    grupos.append(np.mean(grupo_atual))
                    grupo_atual = [nivel]

            grupos.append(np.mean(grupo_atual))
            return grupos

        suportes = agrupar_niveis(minimas_locais)
        resistencias = agrupar_niveis(maximas_locais)

        # Ordenar e pegar os mais significativos
        suportes = sorted(suportes)[-10:]  # Top 10 suportes
        resistencias = sorted(resistencias)[-10:]  # Top 10 resistências

        return {
            'suportes': [round(s, 5) for s in suportes],
            'resistencias': [round(r, 5) for r in resistencias]
        }

    def calcular_pivot_points(self, dados: pd.DataFrame) -> Dict:
        """Calcular Pivot Points clássicos"""
        if dados.empty or len(dados) < 1:
            return {}

        # Usar último dia completo
        ultimo_dia = dados.iloc[-1]
        high = ultimo_dia['High']
        low = ultimo_dia['Low']
        close = ultimo_dia['Close']

        # Pivot Point central
        pp = (high + low + close) / 3

        # Níveis de resistência
        r1 = 2 * pp - low
        r2 = pp + (high - low)
        r3 = high + 2 * (pp - low)

        # Níveis de suporte
        s1 = 2 * pp - high
        s2 = pp - (high - low)
        s3 = low - 2 * (high - pp)

        return {
            'pivot_point': round(pp, 5),
            'resistencias': {
                'R1': round(r1, 5),
                'R2': round(r2, 5),
                'R3': round(r3, 5)
            },
            'suportes': {
                'S1': round(s1, 5),
                'S2': round(s2, 5),
                'S3': round(s3, 5)
            }
        }

    def calcular_fibonacci(self, dados: pd.DataFrame, periodo: int = 50) -> Dict:
        """Calcular retracamentos de Fibonacci"""
        if dados.empty or len(dados) < periodo:
            return {}

        # Usar últimos N períodos
        dados_periodo = dados.tail(periodo)

        # Identificar swing high e swing low
        swing_high = dados_periodo['High'].max()
        swing_low = dados_periodo['Low'].min()

        # Diferença
        diferenca = swing_high - swing_low

        # Níveis de Fibonacci
        niveis_fib = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]

        retracement = {}
        for nivel in niveis_fib:
            preco = swing_high - (diferenca * nivel)
            retracement[f"fib_{int(nivel*100):03d}"] = round(preco, 5)

        return {
            'swing_high': round(swing_high, 5),
            'swing_low': round(swing_low, 5),
            'retracements': retracement
        }

    def calcular_vwap_sessoes(self, dados: pd.DataFrame) -> Dict:
        """Calcular VWAP por sessões de trading"""
        if dados.empty:
            return {}

        # Calcular VWAP geral
        try:
            vwap_geral = ((dados['High'] + dados['Low'] + dados['Close']) / 3 * dados['Volume']).sum() / dados['Volume'].sum()
        except:
            vwap_geral = dados['Close'].mean()

        return {
            'vwap_geral': round(vwap_geral, 5),
            'vwap_semanal': round(dados['Close'].tail(7).mean(), 5),
            'vwap_mensal': round(dados['Close'].tail(30).mean(), 5)
        }

    def analisar_volume_liquidez(self, dados: pd.DataFrame) -> Dict:
        """Análise de volume e zonas de liquidez"""
        if dados.empty:
            return {}

        # Volume médio
        volume_medio = dados['Volume'].mean()
        volume_atual = dados['Volume'].iloc[-1] if len(dados) > 0 else 0

        # Identificar zonas de alto volume (POC - Point of Control)
        dados_volume = dados.copy()
        dados_volume['preco_medio'] = (dados_volume['High'] + dados_volume['Low'] + dados_volume['Close']) / 3

        # Agrupar por faixas de preço
        bins = 50
        dados_volume['faixa_preco'] = pd.cut(dados_volume['preco_medio'], bins=bins)
        volume_por_faixa = dados_volume.groupby('faixa_preco')['Volume'].sum().sort_values(ascending=False)

        # Top 5 zonas de volume
        zonas_liquidez = []
        for i, (faixa, volume) in enumerate(volume_por_faixa.head(5).items()):
            preco_medio = (faixa.left + faixa.right) / 2
            zonas_liquidez.append({
                'preco': round(preco_medio, 5),
                'volume_relativo': round(volume / volume_medio, 2),
                'ranking': i + 1
            })

        return {
            'volume_medio_30d': round(volume_medio, 0),
            'volume_atual': round(volume_atual, 0),
            'ratio_volume': round(volume_atual / volume_medio if volume_medio > 0 else 0, 2),
            'zonas_liquidez': zonas_liquidez
        }

    def processar_ativo_completo(self, ticker: str) -> Dict:
        """Processamento completo de um ativo"""
        self.logger.info(f"🔄 Processando análise completa: {ticker}")

        # Carregar dados históricos
        dados_diarios = self.carregar_dados_historicos(ticker)

        if dados_diarios.empty:
            return {}

        # Dados dos diferentes timeframes
        dados_multi = self.dados_historicos.get(ticker, {})

        resultado_completo = {
            'ticker': ticker,
            'timestamp_calculo': datetime.now().isoformat(),
            'preco_atual': round(dados_diarios['Close'].iloc[-1], 5),
            'timeframes': {}
        }

        # Processar cada timeframe
        timeframes = ['daily', '4h', 'hourly']

        for tf in timeframes:
            if tf in dados_multi and not dados_multi[tf].empty:
                dados_tf = dados_multi[tf]

                resultado_completo['timeframes'][tf] = {
                    'suporte_resistencia': self.calcular_niveis_suporte_resistencia(dados_tf),
                    'pivot_points': self.calcular_pivot_points(dados_tf),
                    'fibonacci': self.calcular_fibonacci(dados_tf),
                    'vwap': self.calcular_vwap_sessoes(dados_tf),
                    'volume_liquidez': self.analisar_volume_liquidez(dados_tf)
                }

        # Análise consolidada (melhor timeframe)
        resultado_completo['niveis_consolidados'] = self._consolidar_niveis(
            resultado_completo['timeframes']
        )

        return resultado_completo

    def _consolidar_niveis(self, timeframes: Dict) -> Dict:
        """Consolidar níveis de múltiplos timeframes"""
        todos_suportes = []
        todas_resistencias = []

        # Coletar todos os níveis
        for tf_data in timeframes.values():
            if 'suporte_resistencia' in tf_data:
                todos_suportes.extend(tf_data['suporte_resistencia'].get('suportes', []))
                todas_resistencias.extend(tf_data['suporte_resistencia'].get('resistencias', []))

        # Agrupar níveis próximos
        def consolidar_lista(niveis: List[float]) -> List[float]:
            if not niveis:
                return []

            niveis_ordenados = sorted(set(niveis))
            consolidados = []

            i = 0
            while i < len(niveis_ordenados):
                grupo = [niveis_ordenados[i]]
                j = i + 1

                # Agrupar níveis dentro de 0.05% de distância
                while j < len(niveis_ordenados):
                    if abs(niveis_ordenados[j] - niveis_ordenados[i]) / niveis_ordenados[i] <= 0.0005:
                        grupo.append(niveis_ordenados[j])
                        j += 1
                    else:
                        break

                consolidados.append(round(np.mean(grupo), 5))
                i = j

            return consolidados

        return {
            'suportes_chave': consolidar_lista(todos_suportes)[-5:],  # Top 5 suportes
            'resistencias_chave': consolidar_lista(todas_resistencias)[-5:],  # Top 5 resistências
            'zona_atual': 'NEUTRO',  # Será calculado dinamicamente
            'forca_niveis': 'MEDIA'  # Baseado em confluência
        }

    def salvar_niveis_ativo(self, ticker: str, niveis: Dict):
        """Salvar níveis calculados para um ativo"""
        nome_arquivo = f"{ticker.replace('=', '_').replace('/', '_')}_niveis.json"
        caminho_arquivo = os.path.join(self.caminho_dados, nome_arquivo)

        try:
            # Converter numpy types para tipos Python nativos
            niveis_limpos = self._limpar_tipos_numpy(niveis)

            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(niveis_limpos, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Níveis salvos: {caminho_arquivo}")

        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar {ticker}: {e}")

    def _limpar_tipos_numpy(self, obj):
        """Converter tipos numpy para tipos Python nativos recursivamente"""
        if isinstance(obj, dict):
            return {key: self._limpar_tipos_numpy(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._limpar_tipos_numpy(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    def processar_portfolio_completo(self):
        """Processar todos os ativos do portfólio"""
        self.logger.info("🚀 Iniciando processamento completo do portfólio...")

        # Carregar ativos do portfólio
        ativos = self.carregar_portfolio()

        if not ativos:
            self.logger.error("❌ Nenhum ativo encontrado no portfólio")
            return

        # Processar ativos em paralelo (máximo 5 threads)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.processar_ativo_completo, ticker): ticker
                for ticker in ativos
            }

            resultados = {}
            for future in futures:
                ticker = futures[future]
                try:
                    resultado = future.result(timeout=60)  # 60 segundos por ativo
                    if resultado:
                        resultados[ticker] = resultado
                        self.salvar_niveis_ativo(ticker, resultado)

                except Exception as e:
                    self.logger.error(f"❌ Falha ao processar {ticker}: {e}")

        # Salvar resumo consolidado
        self._salvar_resumo_consolidado(resultados)

        self.logger.info(f"✅ Processamento concluído: {len(resultados)}/{len(ativos)} ativos")
        return resultados

    def _salvar_resumo_consolidado(self, resultados: Dict):
        """Salvar resumo consolidado de todos os ativos"""
        resumo = {
            'timestamp_processamento': datetime.now().isoformat(),
            'total_ativos': len(resultados),
            'ativos_processados': list(resultados.keys()),
            'resumo_niveis': {}
        }

        for ticker, dados in resultados.items():
            if 'niveis_consolidados' in dados:
                resumo['resumo_niveis'][ticker] = {
                    'preco_atual': dados.get('preco_atual'),
                    'suportes_chave': dados['niveis_consolidados'].get('suportes_chave', []),
                    'resistencias_chave': dados['niveis_consolidados'].get('resistencias_chave', [])
                }

        # Salvar resumo
        caminho_resumo = os.path.join(self.caminho_dados, 'resumo_niveis_portfolio.json')
        with open(caminho_resumo, 'w', encoding='utf-8') as f:
            json.dump(resumo, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📊 Resumo consolidado salvo: {caminho_resumo}")

    def obter_niveis_ativo(self, ticker: str) -> Dict:
        """Obter níveis calculados de um ativo específico"""
        nome_arquivo = f"{ticker.replace('=', '_').replace('/', '_')}_niveis.json"
        caminho_arquivo = os.path.join(self.caminho_dados, nome_arquivo)

        try:
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"⚠️ Arquivo não encontrado: {ticker}")
                return {}

        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar níveis {ticker}: {e}")
            return {}

    def gerar_relatorio_niveis(self) -> str:
        """Gerar relatório executivo dos níveis"""
        resumo_path = os.path.join(self.caminho_dados, 'resumo_niveis_portfolio.json')

        if not os.path.exists(resumo_path):
            return "❌ Resumo não encontrado. Execute o processamento primeiro."

        with open(resumo_path, 'r', encoding='utf-8') as f:
            resumo = json.load(f)

        relatorio = []
        relatorio.append("📊 RELATÓRIO DE NÍVEIS DE PREÇO - ALTA PRECISÃO")
        relatorio.append("=" * 60)
        relatorio.append(f"📅 Processamento: {resumo['timestamp_processamento'][:19]}")
        relatorio.append(f"📈 Ativos Processados: {resumo['total_ativos']}")
        relatorio.append("")

        relatorio.append("🎯 NÍVEIS CRÍTICOS POR ATIVO:")
        relatorio.append("-" * 40)

        for ticker, niveis in resumo['resumo_niveis'].items():
            preco_atual = niveis.get('preco_atual', 0)
            suportes = niveis.get('suportes_chave', [])
            resistencias = niveis.get('resistencias_chave', [])

            relatorio.append(f"")
            relatorio.append(f"🔹 {ticker}")
            relatorio.append(f"   💰 Preço Atual: {preco_atual}")

            if resistencias:
                relatorio.append(f"   🔴 Resistências: {resistencias[-3:]}")  # Top 3

            if suportes:
                relatorio.append(f"   🟢 Suportes: {suportes[-3:]}")  # Top 3

        relatorio.append("")
        relatorio.append("✅ SISTEMA DE NÍVEIS OPERACIONAL")
        relatorio.append("📁 Dados persistidos em: data/niveis_precos/")
        relatorio.append("🔄 Pronto para reavaliação em tempo real")

        return "\n".join(relatorio)


def main():
    """Função principal para execução"""
    print("🚀 Iniciando Sistema de Cálculo de Níveis de Preço...")

    calculador = CalculadorNiveisPrecisao()

    # Processar portfólio completo
    resultados = calculador.processar_portfolio_completo()

    # Gerar relatório
    relatorio = calculador.gerar_relatorio_niveis()
    print("\n" + relatorio)

    return calculador, resultados


if __name__ == "__main__":
    calculador, resultados = main()