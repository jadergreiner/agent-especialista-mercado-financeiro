"""
Sistema de Tracking e Aprendizado Contínuo
Monitoramento de Assertividade e Auto-Aprimoramento do Modelo ML

Funcionalidades:
1. Tracking de oportunidades passadas vs resultados reais
2. Cálculo de métricas de assertividade
3. Sistema de feedback automático
4. Re-treinamento do modelo baseado em performance
5. Sugestão de novos inputs para aprimorar o modelo
6. Alertas inteligentes com learning adaptativo
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import yfinance as yf
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

class SistemaTracking:
    """Sistema de monitoramento de oportunidades e performance"""

    def __init__(self):
        self.logger = self._configurar_logger()
        self.caminho_tracking = "data/tracking"
        self.caminho_oportunidades = "data/oportunidades"
        self.caminho_performance = "data/performance"

        # Criar diretórios
        os.makedirs(self.caminho_tracking, exist_ok=True)
        os.makedirs(self.caminho_performance, exist_ok=True)

        # Métricas de performance
        self.metricas_atuais = {}
        self.historico_performance = []

        # Configurações
        self.janela_avaliacao = 24  # 24 horas para avaliar resultado
        self.threshold_movimento = 0.5  # 0.5% de movimento para considerar sucesso

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('SistemaTracking')
        logger.setLevel(logging.INFO)
        return logger

    def carregar_oportunidades_historicas(self) -> List[Dict]:
        """Carregar todas as oportunidades detectadas historicamente"""
        try:
            oportunidades = []

            if not os.path.exists(self.caminho_oportunidades):
                return []

            arquivos = [f for f in os.listdir(self.caminho_oportunidades)
                       if f.startswith('oportunidades_') and f.endswith('.json')]

            for arquivo in sorted(arquivos):
                caminho = os.path.join(self.caminho_oportunidades, arquivo)

                with open(caminho, 'r', encoding='utf-8') as f:
                    dados = json.load(f)

                # Adicionar cada oportunidade individual
                for op in dados.get('oportunidades_detectadas', []):
                    op['arquivo_origem'] = arquivo
                    op['timestamp_deteccao'] = dados.get('timestamp_deteccao')
                    oportunidades.append(op)

            self.logger.info(f"Carregadas {len(oportunidades)} oportunidades históricas")
            return oportunidades

        except Exception as e:
            self.logger.error(f"Erro ao carregar oportunidades históricas: {e}")
            return []

    def avaliar_resultado_oportunidade(self, oportunidade: Dict) -> Dict:
        """Avaliar se uma oportunidade se concretizou"""
        try:
            timestamp_deteccao = oportunidade.get('timestamp')
            if not timestamp_deteccao:
                return {'erro': 'Timestamp não encontrado'}

            # Converter timestamp para datetime
            dt_deteccao = datetime.fromisoformat(timestamp_deteccao.replace('Z', '+00:00'))

            # Verificar se já passou tempo suficiente para avaliação
            agora = datetime.now()
            if (agora - dt_deteccao).total_seconds() < self.janela_avaliacao * 3600:
                return {'status': 'AGUARDANDO', 'motivo': 'Muito recente para avaliar'}

            # Obter dados de preço
            par = oportunidade['par']
            ticker_yahoo = self._converter_par_para_ticker(par)

            if not ticker_yahoo:
                return {'erro': 'Ticker não reconhecido'}

            # Buscar preços históricos
            ticker = yf.Ticker(ticker_yahoo)

            # Período: desde detecção até agora
            inicio = dt_deteccao.date()
            fim = agora.date()

            dados = ticker.history(start=inicio, end=fim, interval='1h')

            if dados.empty:
                return {'erro': 'Dados de preço não disponíveis'}

            # Preço na detecção (aproximado)
            preco_deteccao = oportunidade.get('dados_posicao', {}).get('current_price')
            if not preco_deteccao:
                return {'erro': 'Preço de detecção não encontrado'}

            # Analisar movimento nas próximas 24h
            dt_limite = dt_deteccao + timedelta(hours=self.janela_avaliacao)
            dados_periodo = dados[dados.index <= dt_limite]

            if dados_periodo.empty:
                return {'erro': 'Dados insuficientes para período de avaliação'}

            # Calcular movimento
            preco_max = dados_periodo['High'].max()
            preco_min = dados_periodo['Low'].min()

            movimento_max = ((preco_max / preco_deteccao) - 1) * 100
            movimento_min = ((preco_min / preco_deteccao) - 1) * 100

            # Determinar se oportunidade foi bem-sucedida
            recomendacao = oportunidade.get('recomendacao', {})
            acao = recomendacao.get('acao', '')

            sucesso = self._avaliar_sucesso_baseado_acao(
                acao, movimento_max, movimento_min,
                oportunidade.get('dados_posicao', {}).get('direction')
            )

            resultado = {
                'par': par,
                'timestamp_deteccao': timestamp_deteccao,
                'preco_deteccao': preco_deteccao,
                'movimento_max_pct': round(movimento_max, 3),
                'movimento_min_pct': round(movimento_min, 3),
                'acao_recomendada': acao,
                'sucesso': sucesso,
                'probabilidade_prevista': oportunidade.get('probabilidade_sucesso'),
                'score_confianca': oportunidade.get('score_confianca'),
                'avaliado_em': agora.isoformat()
            }

            return resultado

        except Exception as e:
            self.logger.error(f"Erro ao avaliar oportunidade: {e}")
            return {'erro': str(e)}

    def _converter_par_para_ticker(self, par: str) -> Optional[str]:
        """Converter par de moedas para ticker Yahoo"""
        conversoes = {
            'GBP/JPY': 'GBPJPY=X', 'EUR/USD': 'EURUSD=X', 'CHF/JPY': 'CHFJPY=X',
            'EUR/CHF': 'EURCHF=X', 'AUD/CHF': 'AUDCHF=X', 'AUD/JPY': 'AUDJPY=X',
            'AUD/NZD': 'AUDNZD=X', 'AUD/USD': 'AUDUSD=X', 'CAD/CHF': 'CADCHF=X',
            'CAD/JPY': 'CADJPY=X', 'EUR/GBP': 'EURGBP=X', 'EUR/JPY': 'EURJPY=X',
            'NZD/CAD': 'NZDCAD=X', 'USD/CHF': 'USDCHF=X', 'XAU/USD': 'GC=F',
            'USD/JPY': 'USDJPY=X', 'GBP/USD': 'GBPUSD=X', 'USD/CAD': 'USDCAD=X'
        }
        return conversoes.get(par)

    def _avaliar_sucesso_baseado_acao(self, acao: str, mov_max: float,
                                    mov_min: float, direcao: str) -> bool:
        """Avaliar sucesso baseado na ação recomendada"""

        if acao == "MANTER_POSICAO":
            # Sucesso se movimento favorável à posição
            if direcao == "LONG":
                return mov_max >= self.threshold_movimento
            else:
                return abs(mov_min) >= self.threshold_movimento

        elif acao == "CONSIDERAR_TAKE_PROFIT":
            # Sucesso se houve movimento significativo
            return max(abs(mov_max), abs(mov_min)) >= self.threshold_movimento

        elif acao == "MONITORAR_PROXIMAMENTE":
            # Sucesso se houve volatilidade significativa
            return (mov_max - mov_min) >= self.threshold_movimento * 2

        else:  # AGUARDAR_CONFIRMACAO
            # Sucesso se não houve movimento excessivo
            return max(abs(mov_max), abs(mov_min)) <= self.threshold_movimento

    def calcular_metricas_performance(self) -> Dict:
        """Calcular métricas de performance do modelo"""
        try:
            oportunidades = self.carregar_oportunidades_historicas()

            if not oportunidades:
                return {'erro': 'Nenhuma oportunidade histórica encontrada'}

            resultados_avaliados = []

            for op in oportunidades:
                resultado = self.avaliar_resultado_oportunidade(op)

                if 'erro' not in resultado and resultado.get('status') != 'AGUARDANDO':
                    resultados_avaliados.append(resultado)

            if not resultados_avaliados:
                return {'aviso': 'Nenhuma oportunidade pode ser avaliada ainda'}

            # Calcular métricas
            total_oportunidades = len(resultados_avaliados)
            sucessos = sum(1 for r in resultados_avaliados if r['sucesso'])

            taxa_acerto = (sucessos / total_oportunidades) * 100

            # Análise por nível de confiança
            analise_confianca = {}
            for nivel in ['MUITO_ALTA', 'ALTA', 'MEDIA', 'BAIXA']:
                ops_nivel = [r for r in resultados_avaliados
                           if r['score_confianca'] == nivel]

                if ops_nivel:
                    sucessos_nivel = sum(1 for r in ops_nivel if r['sucesso'])
                    analise_confianca[nivel] = {
                        'total': len(ops_nivel),
                        'sucessos': sucessos_nivel,
                        'taxa_acerto': (sucessos_nivel / len(ops_nivel)) * 100
                    }

            # Análise por ação recomendada
            analise_acoes = {}
            acoes_unicas = set(r['acao_recomendada'] for r in resultados_avaliados)

            for acao in acoes_unicas:
                ops_acao = [r for r in resultados_avaliados
                          if r['acao_recomendada'] == acao]

                sucessos_acao = sum(1 for r in ops_acao if r['sucesso'])
                analise_acoes[acao] = {
                    'total': len(ops_acao),
                    'sucessos': sucessos_acao,
                    'taxa_acerto': (sucessos_acao / len(ops_acao)) * 100
                }

            # Correlação probabilidade vs sucesso
            probs = [r['probabilidade_prevista'] for r in resultados_avaliados]
            sucessos_bin = [1 if r['sucesso'] else 0 for r in resultados_avaliados]

            correlacao = np.corrcoef(probs, sucessos_bin)[0, 1] if len(probs) > 1 else 0

            metricas = {
                'resumo_geral': {
                    'total_avaliadas': total_oportunidades,
                    'sucessos': sucessos,
                    'taxa_acerto_geral': round(taxa_acerto, 2)
                },
                'analise_por_confianca': analise_confianca,
                'analise_por_acao': analise_acoes,
                'correlacao_prob_sucesso': round(correlacao, 3),
                'oportunidades_avaliadas': resultados_avaliados,
                'timestamp_calculo': datetime.now().isoformat()
            }

            # Salvar métricas
            self._salvar_metricas_performance(metricas)

            return metricas

        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas: {e}")
            return {'erro': str(e)}

    def _salvar_metricas_performance(self, metricas: Dict):
        """Salvar métricas de performance"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"metricas_performance_{timestamp}.json"
        caminho = os.path.join(self.caminho_performance, arquivo)

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(metricas, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Métricas salvas: {caminho}")


class SistemaAprendizadoContinuo:
    """Sistema de auto-aprimoramento do modelo ML"""

    def __init__(self):
        self.logger = logging.getLogger('AprendizadoContinuo')
        self.sistema_tracking = SistemaTracking()
        self.caminho_modelos = "data/ml_models"
        self.caminho_sugestoes = "data/sugestoes_melhoria"

        os.makedirs(self.caminho_sugestoes, exist_ok=True)

        # Thresholds para re-treinamento
        self.threshold_taxa_acerto = 70.0  # % mínimo esperado
        self.min_amostras_retreino = 50    # Mínimo de amostras para re-treinar

    def avaliar_necessidade_retreino(self) -> Dict:
        """Avaliar se o modelo precisa ser re-treinado"""
        try:
            metricas = self.sistema_tracking.calcular_metricas_performance()

            if 'erro' in metricas:
                return {'necessita_retreino': False, 'motivo': 'Métricas indisponíveis'}

            resumo = metricas.get('resumo_geral', {})
            taxa_acerto = resumo.get('taxa_acerto_geral', 0)
            total_amostras = resumo.get('total_avaliadas', 0)

            necessita_retreino = False
            motivos = []

            # Critério 1: Taxa de acerto baixa
            if taxa_acerto < self.threshold_taxa_acerto:
                necessita_retreino = True
                motivos.append(f"Taxa de acerto baixa: {taxa_acerto}% < {self.threshold_taxa_acerto}%")

            # Critério 2: Amostras suficientes
            if total_amostras >= self.min_amostras_retreino:
                if not necessita_retreino:
                    necessita_retreino = True
                    motivos.append(f"Amostras suficientes para retreino: {total_amostras}")

            # Critério 3: Correlação fraca
            correlacao = metricas.get('correlacao_prob_sucesso', 0)
            if correlacao < 0.3:
                necessita_retreino = True
                motivos.append(f"Correlação fraca probabilidade vs sucesso: {correlacao}")

            return {
                'necessita_retreino': necessita_retreino,
                'motivos': motivos,
                'metricas_atuais': resumo,
                'sugestao_acao': self._sugerir_acao_retreino(metricas)
            }

        except Exception as e:
            self.logger.error(f"Erro ao avaliar necessidade de retreino: {e}")
            return {'erro': str(e)}

    def _sugerir_acao_retreino(self, metricas: Dict) -> str:
        """Sugerir ação baseada nas métricas"""
        taxa_acerto = metricas.get('resumo_geral', {}).get('taxa_acerto_geral', 0)

        if taxa_acerto < 60:
            return "RETREINO_URGENTE"
        elif taxa_acerto < 70:
            return "RETREINO_RECOMENDADO"
        else:
            return "MONITORAMENTO_CONTINUO"

    def sugerir_novos_inputs(self) -> Dict:
        """Sugerir novos inputs para aprimorar o modelo"""
        try:
            # Analisar patterns de erro nas previsões
            metricas = self.sistema_tracking.calcular_metricas_performance()

            if 'erro' in metricas:
                return {'erro': 'Métricas indisponíveis'}

            sugestoes = []

            # Análise 1: Performance por ação
            analise_acoes = metricas.get('analise_por_acao', {})

            pior_acao = None
            menor_taxa = 100

            for acao, dados in analise_acoes.items():
                taxa = dados.get('taxa_acerto', 0)
                if taxa < menor_taxa:
                    menor_taxa = taxa
                    pior_acao = acao

            if pior_acao and menor_taxa < 60:
                sugestoes.append({
                    'categoria': 'MELHORIA_ACOES',
                    'problema': f"Baixa assertividade na ação '{pior_acao}': {menor_taxa}%",
                    'sugestao': f"Adicionar features específicas para detectar quando recomendar '{pior_acao}'",
                    'inputs_sugeridos': self._sugerir_features_para_acao(pior_acao)
                })

            # Análise 2: Performance por confiança
            analise_confianca = metricas.get('analise_por_confianca', {})

            if 'MUITO_ALTA' in analise_confianca:
                taxa_muito_alta = analise_confianca['MUITO_ALTA'].get('taxa_acerto', 0)
                if taxa_muito_alta < 80:
                    sugestoes.append({
                        'categoria': 'CALIBRACAO_CONFIANCA',
                        'problema': f"Taxa de acerto em confiança MUITO_ALTA apenas {taxa_muito_alta}%",
                        'sugestao': "Recalibrar thresholds de confiança ou adicionar features de confirmação",
                        'inputs_sugeridos': ['volatilidade_realizada', 'spreads_bid_ask', 'liquidez_mercado']
                    })

            # Análise 3: Correlação geral
            correlacao = metricas.get('correlacao_prob_sucesso', 0)

            if correlacao < 0.5:
                sugestoes.append({
                    'categoria': 'FEATURES_GERAIS',
                    'problema': f"Correlação fraca entre probabilidade e sucesso: {correlacao}",
                    'sugestao': "Adicionar features macroeconômicas mais granulares",
                    'inputs_sugeridos': [
                        'sentimento_mercado_agregado',
                        'fluxo_institucional_real',
                        'posicionamento_cot_report',
                        'correlacao_cross_assets',
                        'seasonality_patterns'
                    ]
                })

            # Análise 4: Features temporais
            sugestoes.append({
                'categoria': 'FEATURES_TEMPORAIS',
                'problema': "Modelo pode não capturar padrões temporais",
                'sugestao': "Adicionar features baseadas em tempo e sazonalidade",
                'inputs_sugeridos': [
                    'hora_do_dia',
                    'dia_da_semana',
                    'sessao_trading',
                    'proximidade_eventos_macro',
                    'tempo_desde_ultimo_evento_bc'
                ]
            })

            # Análise 5: Features de contexto
            sugestoes.append({
                'categoria': 'CONTEXTO_MERCADO',
                'problema': "Falta contexto de mercado mais amplo",
                'sugestao': "Incluir indicadores de regime de mercado",
                'inputs_sugeridos': [
                    'vix_percentil',
                    'termo_structure_juros',
                    'yield_curve_slope',
                    'credit_spreads',
                    'commodity_momentum'
                ]
            })

            resultado = {
                'total_sugestoes': len(sugestoes),
                'sugestoes_detalhadas': sugestoes,
                'prioridade_implementacao': self._priorizar_sugestoes(sugestoes),
                'timestamp_analise': datetime.now().isoformat()
            }

            # Salvar sugestões
            self._salvar_sugestoes(resultado)

            return resultado

        except Exception as e:
            self.logger.error(f"Erro ao sugerir novos inputs: {e}")
            return {'erro': str(e)}

    def _sugerir_features_para_acao(self, acao: str) -> List[str]:
        """Sugerir features específicas para uma ação problemática"""
        sugestoes_por_acao = {
            'MANTER_POSICAO': [
                'momentum_price_action',
                'volume_confirmacao',
                'strength_nivel_suporte'
            ],
            'CONSIDERAR_TAKE_PROFIT': [
                'pressao_vendedora',
                'divergencia_rsi',
                'proximity_resistance_cluster'
            ],
            'MONITORAR_PROXIMAMENTE': [
                'volatilidade_iminente',
                'order_flow_imbalance',
                'news_sentiment_score'
            ],
            'AGUARDAR_CONFIRMACAO': [
                'market_uncertainty_index',
                'cross_pair_divergence',
                'institutional_positioning'
            ]
        }

        return sugestoes_por_acao.get(acao, ['feature_generica_1', 'feature_generica_2'])

    def _priorizar_sugestoes(self, sugestoes: List[Dict]) -> List[str]:
        """Priorizar implementação das sugestões"""
        prioridades = {
            'MELHORIA_ACOES': 1,
            'CALIBRACAO_CONFIANCA': 2,
            'FEATURES_GERAIS': 3,
            'FEATURES_TEMPORAIS': 4,
            'CONTEXTO_MERCADO': 5
        }

        return sorted([s['categoria'] for s in sugestoes],
                     key=lambda x: prioridades.get(x, 99))

    def _salvar_sugestoes(self, sugestoes: Dict):
        """Salvar sugestões de melhoria"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"sugestoes_melhoria_{timestamp}.json"
        caminho = os.path.join(self.caminho_sugestoes, arquivo)

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(sugestoes, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Sugestões salvas: {caminho}")


def main():
    """Demonstração completa do sistema de tracking e aprendizado"""
    print("🔄 SISTEMA DE TRACKING E APRENDIZADO CONTÍNUO")
    print("=" * 70)

    # Inicializar sistemas
    tracking = SistemaTracking()
    aprendizado = SistemaAprendizadoContinuo()

    # 1. Calcular métricas de performance
    print("\n📊 CALCULANDO MÉTRICAS DE PERFORMANCE...")
    metricas = tracking.calcular_metricas_performance()

    if 'erro' not in metricas and 'aviso' not in metricas:
        resumo = metricas['resumo_geral']
        print(f"   ✅ Oportunidades avaliadas: {resumo['total_avaliadas']}")
        print(f"   ✅ Taxa de acerto geral: {resumo['taxa_acerto_geral']}%")
        print(f"   ✅ Sucessos: {resumo['sucessos']}")

        # Mostrar análise por confiança
        print("\n   📈 PERFORMANCE POR CONFIANÇA:")
        for nivel, dados in metricas.get('analise_por_confianca', {}).items():
            print(f"      {nivel}: {dados['taxa_acerto']:.1f}% ({dados['sucessos']}/{dados['total']})")

    else:
        print(f"   ⚠️ {metricas.get('aviso', metricas.get('erro'))}")

    # 2. Avaliar necessidade de retreino
    print(f"\n🔍 AVALIANDO NECESSIDADE DE RE-TREINAMENTO...")
    avaliacao = aprendizado.avaliar_necessidade_retreino()

    if 'erro' not in avaliacao:
        necessita = avaliacao['necessita_retreino']
        print(f"   {'🔴' if necessita else '🟢'} Necessita retreino: {necessita}")

        if avaliacao['motivos']:
            print("   📋 Motivos:")
            for motivo in avaliacao['motivos']:
                print(f"      • {motivo}")

        print(f"   💡 Ação sugerida: {avaliacao['sugestao_acao']}")

    # 3. Gerar sugestões de melhoria
    print(f"\n💡 SUGESTÕES PARA APRIMORAMENTO...")
    sugestoes = aprendizado.sugerir_novos_inputs()

    if 'erro' not in sugestoes:
        print(f"   📊 Total de sugestões: {sugestoes['total_sugestoes']}")

        print("\n   🎯 PRIORIDADES DE IMPLEMENTAÇÃO:")
        for i, categoria in enumerate(sugestoes['prioridade_implementacao'][:3], 1):
            sugestao = next(s for s in sugestoes['sugestoes_detalhadas']
                          if s['categoria'] == categoria)
            print(f"      {i}. {categoria}")
            print(f"         Problema: {sugestao['problema']}")
            print(f"         Inputs: {', '.join(sugestao['inputs_sugeridos'][:3])}...")

    print(f"\n✅ ANÁLISE COMPLETA FINALIZADA")
    print("📁 Dados salvos em:")
    print("   • data/performance/ - Métricas de performance")
    print("   • data/sugestoes_melhoria/ - Sugestões de aprimoramento")

    return tracking, aprendizado, metricas, sugestoes


if __name__ == "__main__":
    tracking, aprendizado, metricas, sugestoes = main()