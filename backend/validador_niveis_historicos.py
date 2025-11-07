"""
Sistema de Validação de Níveis com Backtesting Histórico
Engenheiro ML: Framework de validação para avaliar efetividade dos níveis calculados

Funcionalidades:
1. Framework de backtesting para níveis de suporte/resistência
2. Métricas de precisão, recall e F1-score para níveis
3. Análise de força dos níveis ao longo do tempo
4. Scoring automático baseado em performance histórica
5. Validação cruzada temporal
6. Relatórios de performance detalhados
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import warnings

# Importar nossos sistemas
try:
    from .carregador_dados_historicos import CarregadorDadosHistoricos
    from .detector_niveis_criticos_ml import DetectorNiveisCriticosML
except ImportError:
    # Importação direta quando executado como script
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from carregador_dados_historicos import CarregadorDadosHistoricos
    from detector_niveis_criticos_ml import DetectorNiveisCriticosML

warnings.filterwarnings('ignore')

class ValidadorNiveisHistoricos:
    """Sistema de validação de níveis com backtesting histórico"""

    def __init__(self, carregador_dados: CarregadorDadosHistoricos = None,
                 detector_ml: DetectorNiveisCriticosML = None):
        self.logger = self._configurar_logger()

        # Sistemas integrados
        self.carregador_dados = carregador_dados or CarregadorDadosHistoricos()
        self.detector_ml = detector_ml or DetectorNiveisCriticosML(self.carregador_dados)

        # Cache e persistência
        self.cache_dir = "data/validacao_historica"
        self.db_path = os.path.join(self.cache_dir, "validacao_niveis.db")
        self.relatorios_dir = os.path.join(self.cache_dir, "relatorios")

        # Criar estrutura
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.relatorios_dir, exist_ok=True)
        self._inicializar_database()

        # Parâmetros de validação
        self.parametros_validacao = {
            'tolerancia_nivel': 0.001,  # 0.1% tolerância para toque no nível
            'janela_validacao': 30,     # Dias para frente para validar nível
            'min_toques_valido': 2,     # Mínimo 2 toques para considerar nível válido
            'breakout_threshold': 0.005, # 0.5% para considerar breakout
            'periolos_teste': ['1M', '3M', '6M', '1Y']  # Períodos de teste
        }

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('ValidadorNiveisHistoricos')
        logger.setLevel(logging.INFO)
        return logger

    def _inicializar_database(self):
        """Inicializar database para resultados de validação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validacoes_niveis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                nivel_preco REAL NOT NULL,
                tipo_nivel TEXT NOT NULL,
                data_identificacao DATE NOT NULL,
                data_teste_inicio DATE NOT NULL,
                data_teste_fim DATE NOT NULL,
                toques_detectados INTEGER NOT NULL,
                toques_validados INTEGER NOT NULL,
                breakouts_detectados INTEGER NOT NULL,
                score_precisao REAL NOT NULL,
                score_recall REAL NOT NULL,
                score_f1 REAL NOT NULL,
                forca_nivel REAL NOT NULL,
                valido BOOLEAN NOT NULL,
                metadados TEXT,
                timestamp_validacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                periodo_teste TEXT NOT NULL,
                total_niveis INTEGER NOT NULL,
                niveis_validos INTEGER NOT NULL,
                precisao_media REAL NOT NULL,
                recall_medio REAL NOT NULL,
                f1_score_medio REAL NOT NULL,
                score_geral REAL NOT NULL,
                timestamp_teste DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_validacao ON validacoes_niveis(ticker, data_identificacao)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance ON performance_portfolio(ticker, periodo_teste)')

        conn.commit()
        conn.close()

    def validar_nivel_historico(self, dados: pd.DataFrame, nivel: float,
                               tipo_nivel: str, data_identificacao: datetime,
                               janela_teste: int = 30) -> Dict:
        """Validar um nível específico usando dados históricos futuros"""

        if dados.empty:
            return self._resultado_validacao_vazio()

        # Encontrar índice da data de identificação
        try:
            idx_inicio = dados.index.get_loc(data_identificacao)
            if isinstance(idx_inicio, slice):
                idx_inicio = idx_inicio.start
        except (KeyError, IndexError):
            # Se data exata não existe, encontrar a mais próxima
            idx_inicio = dados.index.searchsorted(data_identificacao)

        # Validar apenas dados futuros
        if idx_inicio >= len(dados) - 5:  # Precisa de pelo menos 5 períodos futuros
            return self._resultado_validacao_vazio()

        # Dados de teste (futuros)
        dados_teste = dados.iloc[idx_inicio:idx_inicio + janela_teste]

        if len(dados_teste) < 5:
            return self._resultado_validacao_vazio()

        # Análise de toques no nível
        tolerancia = self.parametros_validacao['tolerancia_nivel']

        toques_validados = 0
        breakouts_detectados = 0
        pontos_interesse = []

        for i, (timestamp, row) in enumerate(dados_teste.iterrows()):
            high, low, close = row['High'], row['Low'], row['Close']

            # Verificar toque no nível
            if tipo_nivel == 'suporte':
                # Para suporte, verificar se low tocou o nível
                if abs(low - nivel) / nivel <= tolerancia:
                    toques_validados += 1
                    pontos_interesse.append({
                        'timestamp': timestamp,
                        'tipo': 'toque',
                        'preco': low,
                        'distancia_relativa': abs(low - nivel) / nivel
                    })

                # Verificar breakout (fechamento significativamente abaixo)
                if close < nivel * (1 - self.parametros_validacao['breakout_threshold']):
                    breakouts_detectados += 1
                    pontos_interesse.append({
                        'timestamp': timestamp,
                        'tipo': 'breakout',
                        'preco': close,
                        'magnitude': (nivel - close) / nivel
                    })

            else:  # resistência
                # Para resistência, verificar se high tocou o nível
                if abs(high - nivel) / nivel <= tolerancia:
                    toques_validados += 1
                    pontos_interesse.append({
                        'timestamp': timestamp,
                        'tipo': 'toque',
                        'preco': high,
                        'distancia_relativa': abs(high - nivel) / nivel
                    })

                # Verificar breakout (fechamento significativamente acima)
                if close > nivel * (1 + self.parametros_validacao['breakout_threshold']):
                    breakouts_detectados += 1
                    pontos_interesse.append({
                        'timestamp': timestamp,
                        'tipo': 'breakout',
                        'preco': close,
                        'magnitude': (close - nivel) / nivel
                    })

        # Calcular métricas de performance
        metricas = self._calcular_metricas_nivel(toques_validados, breakouts_detectados, len(dados_teste))

        return {
            'toques_validados': toques_validados,
            'breakouts_detectados': breakouts_detectados,
            'pontos_interesse': pontos_interesse,
            'periodo_teste': {
                'inicio': dados_teste.index[0].isoformat(),
                'fim': dados_teste.index[-1].isoformat(),
                'total_periodos': len(dados_teste)
            },
            'metricas': metricas,
            'nivel_valido': toques_validados >= self.parametros_validacao['min_toques_valido'],
            'forca_nivel': self._calcular_forca_nivel(toques_validados, breakouts_detectados, len(dados_teste))
        }

    def _resultado_validacao_vazio(self) -> Dict:
        """Retorna resultado vazio para casos de erro"""
        return {
            'toques_validados': 0,
            'breakouts_detectados': 0,
            'pontos_interesse': [],
            'periodo_teste': {},
            'metricas': {'precisao': 0.0, 'recall': 0.0, 'f1_score': 0.0},
            'nivel_valido': False,
            'forca_nivel': 0.0
        }

    def _calcular_metricas_nivel(self, toques: int, breakouts: int, total_periodos: int) -> Dict:
        """Calcular métricas de precisão, recall e F1-score para um nível"""

        # Definições:
        # True Positives (TP): Toques no nível conforme esperado
        # False Positives (FP): Breakouts quando esperávamos toques
        # False Negatives (FN): Períodos sem toques quando deveriam ter

        tp = toques  # Toques corretos
        fp = breakouts  # Breakouts são "erros" do nível

        # Estimar FN baseado na expectativa de toques
        # Assumir que um nível forte deve ter pelo menos 1 toque a cada 10 períodos
        toques_esperados = max(1, total_periodos // 10)
        fn = max(0, toques_esperados - toques)

        # Calcular métricas
        precisao = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precisao * recall) / (precisao + recall) if (precisao + recall) > 0 else 0.0

        return {
            'precisao': round(precisao, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1_score, 4),
            'toques_esperados': toques_esperados,
            'tp': tp,
            'fp': fp,
            'fn': fn
        }

    def _calcular_forca_nivel(self, toques: int, breakouts: int, total_periodos: int) -> float:
        """Calcular força do nível baseado em performance histórica"""

        # Componentes da força
        score_toques = min(1.0, toques / 5.0)  # Normalizar para máximo 5 toques
        score_resistencia = max(0.0, 1.0 - (breakouts / max(1, toques)))  # Penalizar breakouts
        score_consistencia = min(1.0, toques / (total_periodos / 10))  # Consistência temporal

        # Média ponderada
        forca = (score_toques * 0.4) + (score_resistencia * 0.4) + (score_consistencia * 0.2)

        return round(max(0.0, min(1.0, forca)), 4)

    def validar_niveis_ativo(self, ticker: str, periodo_lookback: str = "2y") -> Dict:
        """Validar todos os níveis de um ativo usando backtesting"""

        self.logger.info(f"🔍 Validando níveis históricos para {ticker}")

        # Carregar dados históricos completos
        dados_completos = self.carregador_dados.carregar_dados_multi_fonte(
            ticker, periodo_lookback, ['1d']
        )

        if not dados_completos['timeframes'] or '1d' not in dados_completos['timeframes']:
            self.logger.error(f"❌ Falha ao carregar dados para {ticker}")
            return {}

        dados_diarios = dados_completos['timeframes']['1d']['dados']

        if dados_diarios.empty or len(dados_diarios) < 100:
            self.logger.error(f"❌ Dados insuficientes para {ticker}: {len(dados_diarios)} registros")
            return {}

        # Executar análise ML para identificar níveis
        resultado_ml = self.detector_ml.processar_ativo_ml_completo(ticker, periodo_lookback)

        if not resultado_ml or 'analise_consolidada' not in resultado_ml:
            self.logger.error(f"❌ Falha na análise ML para {ticker}")
            return {}

        # Preparar resultado de validação
        resultado_validacao = {
            'ticker': ticker,
            'timestamp_validacao': datetime.now().isoformat(),
            'periodo_dados': {
                'inicio': dados_diarios.index[0].isoformat(),
                'fim': dados_diarios.index[-1].isoformat(),
                'total_registros': len(dados_diarios)
            },
            'validacoes_individuais': [],
            'estatisticas_gerais': {},
            'qualidade_validacao': 0.0
        }

        # Validar cada nível identificado
        analise_consolidada = resultado_ml['analise_consolidada']
        total_validacoes = 0
        validacoes_bem_sucedidas = 0

        # Validar suportes
        for suporte in analise_consolidada.get('suportes_criticos', []):
            # Simular que o nível foi "identificado" na metade dos dados
            ponto_medio = len(dados_diarios) // 2
            data_identificacao = dados_diarios.index[ponto_medio]

            validacao = self.validar_nivel_historico(
                dados_diarios, suporte['nivel'], 'suporte',
                data_identificacao, self.parametros_validacao['janela_validacao']
            )

            validacao_completa = {
                'nivel': suporte['nivel'],
                'tipo': 'suporte',
                'score_ml_original': suporte['score_final'],
                'confluencia_timeframes': suporte['confluencia'],
                'data_identificacao': data_identificacao.isoformat(),
                'resultados_validacao': validacao
            }

            resultado_validacao['validacoes_individuais'].append(validacao_completa)
            total_validacoes += 1
            if validacao['nivel_valido']:
                validacoes_bem_sucedidas += 1

        # Validar resistências
        for resistencia in analise_consolidada.get('resistencias_criticas', []):
            ponto_medio = len(dados_diarios) // 2
            data_identificacao = dados_diarios.index[ponto_medio]

            validacao = self.validar_nivel_historico(
                dados_diarios, resistencia['nivel'], 'resistencia',
                data_identificacao, self.parametros_validacao['janela_validacao']
            )

            validacao_completa = {
                'nivel': resistencia['nivel'],
                'tipo': 'resistencia',
                'score_ml_original': resistencia['score_final'],
                'confluencia_timeframes': resistencia['confluencia'],
                'data_identificacao': data_identificacao.isoformat(),
                'resultados_validacao': validacao
            }

            resultado_validacao['validacoes_individuais'].append(validacao_completa)
            total_validacoes += 1
            if validacao['nivel_valido']:
                validacoes_bem_sucedidas += 1

        # Calcular estatísticas gerais
        if total_validacoes > 0:
            # Métricas agregadas
            todas_metricas = [v['resultados_validacao']['metricas'] for v in resultado_validacao['validacoes_individuais']]

            precisao_media = np.mean([m['precisao'] for m in todas_metricas])
            recall_medio = np.mean([m['recall'] for m in todas_metricas])
            f1_score_medio = np.mean([m['f1_score'] for m in todas_metricas])

            # Força média dos níveis
            forca_media = np.mean([v['resultados_validacao']['forca_nivel'] for v in resultado_validacao['validacoes_individuais']])

            # Taxa de sucesso
            taxa_sucesso = validacoes_bem_sucedidas / total_validacoes

            resultado_validacao['estatisticas_gerais'] = {
                'total_niveis_testados': total_validacoes,
                'niveis_validos': validacoes_bem_sucedidas,
                'taxa_sucesso': round(taxa_sucesso, 4),
                'precisao_media': round(precisao_media, 4),
                'recall_medio': round(recall_medio, 4),
                'f1_score_medio': round(f1_score_medio, 4),
                'forca_media': round(forca_media, 4)
            }

            # Score geral de qualidade (combinação de métricas)
            resultado_validacao['qualidade_validacao'] = round(
                (taxa_sucesso * 0.3) + (f1_score_medio * 0.4) + (forca_media * 0.3), 4
            )

        # Salvar no database
        self._salvar_resultados_validacao(resultado_validacao)

        self.logger.info(f"✅ {ticker}: {validacoes_bem_sucedidas}/{total_validacoes} níveis válidos, qualidade {resultado_validacao['qualidade_validacao']:.2%}")

        return resultado_validacao

    def _salvar_resultados_validacao(self, resultado: Dict):
        """Salvar resultados de validação no database"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            ticker = resultado['ticker']

            # Limpar validações anteriores
            cursor.execute('DELETE FROM validacoes_niveis WHERE ticker = ?', (ticker,))

            # Salvar validações individuais
            for validacao in resultado['validacoes_individuais']:
                nivel = validacao['nivel']
                tipo_nivel = validacao['tipo']
                data_id = validacao['data_identificacao'][:10]  # Data apenas
                resultados = validacao['resultados_validacao']

                if resultados['periodo_teste']:
                    cursor.execute('''
                        INSERT INTO validacoes_niveis
                        (ticker, nivel_preco, tipo_nivel, data_identificacao,
                         data_teste_inicio, data_teste_fim, toques_detectados, toques_validados,
                         breakouts_detectados, score_precisao, score_recall, score_f1,
                         forca_nivel, valido, metadados)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ticker, nivel, tipo_nivel, data_id,
                        resultados['periodo_teste']['inicio'][:10],
                        resultados['periodo_teste']['fim'][:10],
                        len(resultados['pontos_interesse']),
                        resultados['toques_validados'],
                        resultados['breakouts_detectados'],
                        resultados['metricas']['precisao'],
                        resultados['metricas']['recall'],
                        resultados['metricas']['f1_score'],
                        resultados['forca_nivel'],
                        resultados['nivel_valido'],
                        json.dumps(validacao.get('confluencia_timeframes', 0))
                    ))

            # Salvar estatísticas gerais
            if 'estatisticas_gerais' in resultado:
                stats = resultado['estatisticas_gerais']
                cursor.execute('''
                    INSERT INTO performance_portfolio
                    (ticker, periodo_teste, total_niveis, niveis_validos,
                     precisao_media, recall_medio, f1_score_medio, score_geral)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker, 'backtesting_completo', stats['total_niveis_testados'],
                    stats['niveis_validos'], stats['precisao_media'],
                    stats['recall_medio'], stats['f1_score_medio'],
                    resultado['qualidade_validacao']
                ))

            conn.commit()
            conn.close()

            self.logger.info(f"✅ Resultados de validação salvos para {ticker}")

        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar validação {ticker}: {e}")

    def validar_portfolio_completo(self, tickers: List[str]) -> Dict:
        """Validar portfolio completo com backtesting"""

        self.logger.info(f"🚀 Validação Histórica Portfolio: {len(tickers)} ativos")

        resultados = {}

        # Processar em paralelo (limitado para não sobrecarregar)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_ticker = {
                executor.submit(self.validar_niveis_ativo, ticker): ticker
                for ticker in tickers
            }

            for future in future_to_ticker:
                ticker = future_to_ticker[future]
                try:
                    resultado = future.result()
                    if resultado:
                        resultados[ticker] = resultado
                except Exception as e:
                    self.logger.error(f"Erro validando {ticker}: {e}")

        # Estatísticas agregadas do portfolio
        sucessos = len([r for r in resultados.values() if r and r.get('qualidade_validacao', 0) > 0.5])

        if resultados:
            qualidades = [r['qualidade_validacao'] for r in resultados.values() if r]
            qualidade_media = np.mean(qualidades) if qualidades else 0

            # Métricas agregadas
            total_niveis = sum(r['estatisticas_gerais']['total_niveis_testados']
                             for r in resultados.values() if r and 'estatisticas_gerais' in r)
            niveis_validos = sum(r['estatisticas_gerais']['niveis_validos']
                               for r in resultados.values() if r and 'estatisticas_gerais' in r)
        else:
            qualidade_media = 0
            total_niveis = 0
            niveis_validos = 0

        resumo_portfolio = {
            'timestamp_validacao': datetime.now().isoformat(),
            'total_ativos': len(tickers),
            'sucessos_validacao': sucessos,
            'taxa_sucesso_portfolio': sucessos / len(tickers) if len(tickers) > 0 else 0,
            'qualidade_media': round(qualidade_media, 4),
            'estatisticas_portfolio': {
                'total_niveis_testados': total_niveis,
                'niveis_validos_portfolio': niveis_validos,
                'taxa_validacao_geral': round(niveis_validos / total_niveis, 4) if total_niveis > 0 else 0
            },
            'resultados_individuais': resultados
        }

        self.logger.info(f"✅ Portfolio validado: {sucessos}/{len(tickers)} ativos, {niveis_validos}/{total_niveis} níveis válidos")

        return resumo_portfolio

    def gerar_relatorio_validacao(self, resultados_portfolio: Dict) -> str:
        """Gerar relatório executivo da validação histórica"""

        relatorio = []
        relatorio.append("🔍 RELATÓRIO VALIDAÇÃO HISTÓRICA - BACKTESTING")
        relatorio.append("=" * 65)

        relatorio.append(f"\n🎯 RESUMO EXECUTIVO:")
        relatorio.append(f"   Total de ativos testados: {resultados_portfolio['total_ativos']}")
        relatorio.append(f"   Sucessos na validação: {resultados_portfolio['sucessos_validacao']}")
        relatorio.append(f"   Taxa de sucesso: {resultados_portfolio['taxa_sucesso_portfolio']:.1%}")
        relatorio.append(f"   Qualidade média: {resultados_portfolio['qualidade_media']:.1%}")

        # Estatísticas de níveis
        stats = resultados_portfolio['estatisticas_portfolio']
        relatorio.append(f"\n📊 ESTATÍSTICAS DE NÍVEIS:")
        relatorio.append(f"   Total níveis testados: {stats['total_niveis_testados']}")
        relatorio.append(f"   Níveis válidos: {stats['niveis_validos_portfolio']}")
        relatorio.append(f"   Taxa de validação geral: {stats['taxa_validacao_geral']:.1%}")

        # Análise por ativo
        relatorio.append(f"\n📈 VALIDAÇÃO POR ATIVO:")
        relatorio.append("-" * 55)

        for ticker, resultado in resultados_portfolio['resultados_individuais'].items():
            if not resultado or 'estatisticas_gerais' not in resultado:
                continue

            qualidade = resultado['qualidade_validacao']
            emoji = "🟢" if qualidade >= 0.7 else "🟡" if qualidade >= 0.5 else "🔴"

            stats_ativo = resultado['estatisticas_gerais']

            relatorio.append(f"\n{emoji} {ticker}: Qualidade {qualidade:.1%}")
            relatorio.append(f"   📊 Níveis testados: {stats_ativo['total_niveis_testados']}")
            relatorio.append(f"   ✅ Níveis válidos: {stats_ativo['niveis_validos']} ({stats_ativo['taxa_sucesso']:.1%})")
            relatorio.append(f"   🎯 F1-Score médio: {stats_ativo['f1_score_medio']:.3f}")
            relatorio.append(f"   💪 Força média: {stats_ativo['forca_media']:.3f}")

        relatorio.append("\n📋 METODOLOGIA:")
        relatorio.append("   • Backtesting com dados futuros (30 dias)")
        relatorio.append("   • Tolerância de 0.1% para toques nos níveis")
        relatorio.append("   • Mínimo 2 toques para considerar nível válido")
        relatorio.append("   • Breakout definido como movimento > 0.5%")
        relatorio.append("   • Métricas: Precisão, Recall, F1-Score e Força")

        relatorio.append("\n✅ SISTEMA DE VALIDAÇÃO OPERACIONAL")
        relatorio.append("🔍 Backtesting histórico implementado")
        relatorio.append("📊 Métricas científicas de performance")
        relatorio.append("💾 Resultados persistidos para análise contínua")

        return "\n".join(relatorio)


def main():
    """Demonstração do sistema de validação histórica"""

    print("🔍 SISTEMA DE VALIDAÇÃO HISTÓRICA - BACKTESTING")
    print("=" * 65)

    # Portfolio de teste (usando tickers que funcionam melhor)
    portfolio_teste = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']

    # Inicializar sistema
    validador = ValidadorNiveisHistoricos()

    print(f"\n🔄 Executando validação histórica para {len(portfolio_teste)} ativos...")
    print("⏳ Processo pode levar alguns minutos devido ao backtesting...")

    # Validar portfolio
    resultados = validador.validar_portfolio_completo(portfolio_teste)

    # Gerar relatório
    relatorio = validador.gerar_relatorio_validacao(resultados)
    print(f"\n{relatorio}")

    # Salvar resultados
    output_path = "data/validacao_historica/relatorio_validacao.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Resultados de validação salvos em: {output_path}")

    return validador, resultados


if __name__ == "__main__":
    validador, resultados = main()