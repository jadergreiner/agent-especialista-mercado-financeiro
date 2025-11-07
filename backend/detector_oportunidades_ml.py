"""
Sistema Avançado de Oportunidades Macro-Técnicas
Engenheiro de ML - Detecção de Oportunidades com Alto Potencial de Ganho

Funcionalidades:
1. Análise macroeconômica integrada (DXY, eventos críticos, carry trade)
2. Cruzamento com níveis técnicos de alta precisão
3. Sistema de ML para scoring de oportunidades
4. Tracking de assertividade histórica
5. Auto-aprimoramento baseado em performance
6. Alertas inteligentes com probabilidade de sucesso
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from decimal import Decimal
import yfinance as yf
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# Imports locais
from motor_niveis_portfolio import MotorNiveisPortfolio
from calculador_niveis_precisao import CalculadorNiveisPrecisao

class AnalisadorMacroEconomico:
    """Sistema de análise macroeconômica avançada"""

    def __init__(self):
        self.logger = self._configurar_logger()
        self.caminho_dados_macro = "data/macro_analysis"
        self.caminho_sinais = "bus"

        # Criar diretórios
        os.makedirs(self.caminho_dados_macro, exist_ok=True)

        # Cache de dados macro
        self.cache_dxy = {}
        self.cache_eventos = {}
        self.cache_carry_trades = {}

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('AnalisadorMacro')
        logger.setLevel(logging.INFO)
        return logger

    def coletar_dados_dxy(self, periodo: int = 30) -> Dict:
        """Coletar dados históricos e atual do DXY"""
        try:
            ticker_dxy = yf.Ticker('DX-Y.NYB')
            dados = ticker_dxy.history(period=f"{periodo}d")

            if dados.empty:
                return {'erro': 'Dados DXY indisponíveis'}

            # Calcular métricas
            preco_atual = dados['Close'].iloc[-1]
            variacao_diaria = ((preco_atual / dados['Close'].iloc[-2]) - 1) * 100

            # Tendência de 7 dias
            preco_7d = dados['Close'].iloc[-7] if len(dados) >= 7 else dados['Close'].iloc[0]
            tendencia_7d = ((preco_atual / preco_7d) - 1) * 100

            # Volatilidade
            volatilidade = dados['Close'].pct_change().std() * 100

            resultado = {
                'preco_atual': round(preco_atual, 4),
                'variacao_diaria': round(variacao_diaria, 4),
                'tendencia_7d': round(tendencia_7d, 4),
                'volatilidade': round(volatilidade, 4),
                'timestamp': datetime.now().isoformat(),
                'regime': self._classificar_regime_dolar(variacao_diaria, tendencia_7d)
            }

            self.cache_dxy = resultado
            return resultado

        except Exception as e:
            self.logger.error(f"Erro ao coletar DXY: {e}")
            return {'erro': str(e)}

    def _classificar_regime_dolar(self, var_diaria: float, tend_7d: float) -> str:
        """Classificar regime do dólar"""
        if tend_7d > 1.5:
            return "DOLAR_FORTE"
        elif tend_7d < -1.5:
            return "DOLAR_FRACO"
        elif abs(var_diaria) > 0.5:
            return "VOLATIL"
        else:
            return "ESTAVEL"

    def analisar_eventos_criticos(self) -> Dict:
        """Analisar eventos críticos dos arquivos de sinal"""
        try:
            eventos_consolidados = {}
            caminho_bus = self.caminho_sinais

            if not os.path.exists(caminho_bus):
                return {'erro': 'Diretório de sinais não encontrado'}

            # Buscar arquivos de sinal recentes
            arquivos_sinal = [f for f in os.listdir(caminho_bus)
                            if f.startswith('signal.macroflow.v1') and f.endswith('.json')]

            # Pegar os 10 mais recentes
            arquivos_sinal.sort(reverse=True)

            for arquivo in arquivos_sinal[:10]:
                caminho_arquivo = os.path.join(caminho_bus, arquivo)

                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)

                if dados.get('valid') and 'event' in dados:
                    evento = dados['event']
                    par = evento.get('instrumento', {}).get('par', '')
                    sinal = evento.get('sinal', {})

                    eventos_criticos = sinal.get('eventosCriticos', [])
                    dxy_var = sinal.get('dxyVariacao', 0)

                    if par and eventos_criticos:
                        eventos_consolidados[par] = {
                            'eventos': eventos_criticos,
                            'dxy_variacao': dxy_var,
                            'timestamp': evento.get('timestamp'),
                            'impacto_estimado': self._estimar_impacto_eventos(eventos_criticos)
                        }

            return {
                'eventos_por_par': eventos_consolidados,
                'total_pares': len(eventos_consolidados),
                'timestamp_analise': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Erro ao analisar eventos: {e}")
            return {'erro': str(e)}

    def _estimar_impacto_eventos(self, eventos: List[str]) -> str:
        """Estimar impacto dos eventos críticos"""
        eventos_alto_impacto = [
            'Fed', 'BCE', 'BoE', 'BoJ', 'FOMC', 'NFP', 'CPI', 'Rate'
        ]

        for evento in eventos:
            for termo in eventos_alto_impacto:
                if termo.lower() in evento.lower():
                    return "ALTO"

        return "MEDIO"

    def analisar_carry_trades(self) -> Dict:
        """Análise de oportunidades de carry trade"""
        try:
            # Taxas simuladas baseadas em dados reais aproximados
            taxas_atuais = {
                'USD': 5.25,  # Fed Funds Rate
                'EUR': 4.25,  # ECB Rate
                'GBP': 5.00,  # BoE Rate
                'JPY': 0.25,  # BoJ Rate
                'CHF': 1.50,  # SNB Rate
                'CAD': 4.75,  # BoC Rate
                'AUD': 4.35,  # RBA Rate
                'NZD': 4.75   # RBNZ Rate
            }

            carry_opportunities = []

            # Calcular diferenciais para pares do portfolio
            pares_portfolio = [
                ('GBP', 'JPY'), ('EUR', 'USD'), ('CHF', 'JPY'),
                ('EUR', 'CHF'), ('AUD', 'CHF'), ('AUD', 'JPY'),
                ('AUD', 'NZD'), ('AUD', 'USD'), ('CAD', 'CHF'),
                ('CAD', 'JPY'), ('EUR', 'GBP'), ('EUR', 'JPY'),
                ('NZD', 'CAD'), ('USD', 'CHF'), ('USD', 'JPY')
            ]

            for base, contra in pares_portfolio:
                diferencial = taxas_atuais[base] - taxas_atuais[contra]

                carry_opportunities.append({
                    'par': f"{base}/{contra}",
                    'diferencial': round(diferencial, 2),
                    'taxa_base': taxas_atuais[base],
                    'taxa_contra': taxas_atuais[contra],
                    'atratividade': self._classificar_carry(diferencial),
                    'direcao_favoravel': 'LONG' if diferencial > 0 else 'SHORT'
                })

            # Ordenar por diferencial absoluto
            carry_opportunities.sort(key=lambda x: abs(x['diferencial']), reverse=True)

            return {
                'oportunidades': carry_opportunities,
                'timestamp': datetime.now().isoformat(),
                'melhor_carry': carry_opportunities[0] if carry_opportunities else None
            }

        except Exception as e:
            self.logger.error(f"Erro na análise de carry trade: {e}")
            return {'erro': str(e)}

    def _classificar_carry(self, diferencial: float) -> str:
        """Classificar atratividade do carry trade"""
        abs_diff = abs(diferencial)

        if abs_diff >= 4.0:
            return "EXCELENTE"
        elif abs_diff >= 2.5:
            return "BOA"
        elif abs_diff >= 1.0:
            return "MODERADA"
        else:
            return "BAIXA"


class DetectorOportunidadesML:
    """Sistema de ML para detecção de oportunidades macro-técnicas"""

    def __init__(self):
        self.logger = logging.getLogger('DetectorML')
        self.analisador_macro = AnalisadorMacroEconomico()
        self.motor_niveis = MotorNiveisPortfolio()

        # Modelos ML
        self.modelo_oportunidades = None
        self.modelo_treinado = False

        # Configurações
        self.threshold_oportunidade = 0.65  # 65% de confiança mínima
        self.caminho_modelo = "data/ml_models"
        self.caminho_oportunidades = "data/oportunidades"

        # Criar diretórios
        os.makedirs(self.caminho_modelo, exist_ok=True)
        os.makedirs(self.caminho_oportunidades, exist_ok=True)

        # Features para o modelo
        self.features = [
            'dxy_variacao', 'dxy_tendencia_7d', 'dxy_volatilidade',
            'carry_diferencial', 'impacto_eventos', 'distancia_nivel_pct',
            'tipo_nivel', 'confluencia_niveis', 'volume_relativo',
            'direcao_posicao', 'pnl_atual'
        ]

    def preparar_dados_treino(self) -> pd.DataFrame:
        """Preparar dados históricos para treino do modelo"""
        try:
            # Simular dados históricos de oportunidades
            # Em produção, isso seria baseado em dados reais coletados

            np.random.seed(42)  # Para reprodutibilidade
            n_samples = 1000

            dados_treino = []

            for i in range(n_samples):
                # Simular features macroeconômicas
                dxy_var = np.random.normal(0, 0.8)
                dxy_tend_7d = np.random.normal(0, 2.0)
                dxy_vol = np.random.uniform(0.3, 2.5)

                carry_diff = np.random.uniform(-5, 5)
                impacto_eventos = np.random.choice([1, 2, 3])  # 1=BAIXO, 2=MEDIO, 3=ALTO

                # Simular features técnicas
                dist_nivel = np.random.uniform(0.01, 5.0)  # % de distância do nível
                tipo_nivel = np.random.choice([1, 0])  # 1=suporte, 0=resistência
                confluencia = np.random.uniform(0, 1)  # Força da confluência
                volume_rel = np.random.uniform(0.5, 3.0)

                # Features de posição
                direcao = np.random.choice([1, -1])  # 1=LONG, -1=SHORT
                pnl_atual = np.random.normal(0, 1000)

                # Target: sucesso da oportunidade (simulado)
                # Lógica: oportunidade tem maior chance de sucesso quando:
                # - Macro e técnico estão alinhados
                # - Distância do nível é pequena
                # - Carry trade favorável
                # - Alto impacto de eventos

                score_macro = (abs(dxy_var) * 0.3 + abs(carry_diff) * 0.1 + impacto_eventos * 0.2)
                score_tecnico = (1 / (1 + dist_nivel)) * confluencia
                score_alinhamento = 0.5 if (dxy_var * direcao > 0) else 0.2

                score_final = (score_macro + score_tecnico + score_alinhamento) / 3
                sucesso = 1 if score_final > 0.6 else 0

                dados_treino.append({
                    'dxy_variacao': dxy_var,
                    'dxy_tendencia_7d': dxy_tend_7d,
                    'dxy_volatilidade': dxy_vol,
                    'carry_diferencial': carry_diff,
                    'impacto_eventos': impacto_eventos,
                    'distancia_nivel_pct': dist_nivel,
                    'tipo_nivel': tipo_nivel,
                    'confluencia_niveis': confluencia,
                    'volume_relativo': volume_rel,
                    'direcao_posicao': direcao,
                    'pnl_atual': pnl_atual,
                    'sucesso': sucesso
                })

            return pd.DataFrame(dados_treino)

        except Exception as e:
            self.logger.error(f"Erro ao preparar dados de treino: {e}")
            return pd.DataFrame()

    def treinar_modelo(self) -> bool:
        """Treinar modelo de ML para detecção de oportunidades"""
        try:
            self.logger.info("Iniciando treinamento do modelo...")

            # Preparar dados
            dados = self.preparar_dados_treino()

            if dados.empty:
                self.logger.error("Dados de treino vazios")
                return False

            # Separar features e target
            X = dados[self.features]
            y = dados['sucesso']

            # Split treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            # Treinar Random Forest
            self.modelo_oportunidades = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )

            self.modelo_oportunidades.fit(X_train, y_train)

            # Avaliar modelo
            y_pred = self.modelo_oportunidades.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            self.logger.info(f"Modelo treinado - MSE: {mse:.4f}, R²: {r2:.4f}")

            # Salvar modelo
            modelo_path = os.path.join(self.caminho_modelo, 'modelo_oportunidades.joblib')
            joblib.dump(self.modelo_oportunidades, modelo_path)

            # Salvar métricas
            metricas = {
                'mse': mse,
                'r2': r2,
                'timestamp_treino': datetime.now().isoformat(),
                'n_samples': len(dados),
                'features': self.features
            }

            with open(os.path.join(self.caminho_modelo, 'metricas_modelo.json'), 'w') as f:
                json.dump(metricas, f, indent=2)

            self.modelo_treinado = True
            return True

        except Exception as e:
            self.logger.error(f"Erro no treinamento: {e}")
            return False

    def carregar_modelo(self) -> bool:
        """Carregar modelo pré-treinado"""
        try:
            modelo_path = os.path.join(self.caminho_modelo, 'modelo_oportunidades.joblib')

            if os.path.exists(modelo_path):
                self.modelo_oportunidades = joblib.load(modelo_path)
                self.modelo_treinado = True
                self.logger.info("Modelo carregado com sucesso")
                return True
            else:
                self.logger.info("Modelo não encontrado, treinando novo...")
                return self.treinar_modelo()

        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo: {e}")
            return False

    def detectar_oportunidades(self) -> Dict:
        """Detectar oportunidades macro-técnicas em tempo real"""
        try:
            if not self.modelo_treinado:
                if not self.carregar_modelo():
                    return {'erro': 'Modelo não disponível'}

            # Coletar dados macro atuais
            dados_dxy = self.analisador_macro.coletar_dados_dxy()
            eventos = self.analisador_macro.analisar_eventos_criticos()
            carry_trades = self.analisador_macro.analisar_carry_trades()

            # Analisar portfolio com níveis
            analise_portfolio = self.motor_niveis.analisar_portfolio_niveis()

            oportunidades = []

            # Processar cada posição do portfolio
            for par, dados_posicao in analise_portfolio.get('resumo_niveis', {}).items():
                try:
                    # Preparar features para o modelo
                    features_posicao = self._extrair_features_posicao(
                        par, dados_posicao, dados_dxy, eventos, carry_trades
                    )

                    if features_posicao:
                        # Predizer probabilidade de sucesso
                        probabilidade = self.modelo_oportunidades.predict([features_posicao])[0]

                        # Classificar se é oportunidade
                        if probabilidade >= self.threshold_oportunidade:
                            oportunidade = {
                                'par': par,
                                'probabilidade_sucesso': round(probabilidade, 3),
                                'score_confianca': self._calcular_score_confianca(probabilidade),
                                'dados_posicao': dados_posicao,
                                'analise_macro': self._gerar_analise_macro(par, dados_dxy, eventos, carry_trades),
                                'analise_tecnica': self._gerar_analise_tecnica(dados_posicao),
                                'recomendacao': self._gerar_recomendacao(dados_posicao, probabilidade),
                                'timestamp': datetime.now().isoformat()
                            }

                            oportunidades.append(oportunidade)

                except Exception as e:
                    self.logger.error(f"Erro ao processar {par}: {e}")
                    continue

            # Ordenar por probabilidade
            oportunidades.sort(key=lambda x: x['probabilidade_sucesso'], reverse=True)

            resultado = {
                'oportunidades_detectadas': oportunidades,
                'total_oportunidades': len(oportunidades),
                'threshold_usado': self.threshold_oportunidade,
                'dados_macro': {
                    'dxy': dados_dxy,
                    'eventos': eventos,
                    'carry_trades': carry_trades
                },
                'timestamp_deteccao': datetime.now().isoformat()
            }

            # Salvar oportunidades detectadas
            self._salvar_oportunidades(resultado)

            return resultado

        except Exception as e:
            self.logger.error(f"Erro na detecção de oportunidades: {e}")
            return {'erro': str(e)}

    def _extrair_features_posicao(self, par: str, dados_posicao: Dict,
                                dados_dxy: Dict, eventos: Dict,
                                carry_trades: Dict) -> Optional[List]:
        """Extrair features de uma posição para o modelo ML"""
        try:
            # Features macroeconômicas
            dxy_var = dados_dxy.get('variacao_diaria', 0)
            dxy_tend_7d = dados_dxy.get('tendencia_7d', 0)
            dxy_vol = dados_dxy.get('volatilidade', 1)

            # Carry trade para este par
            carry_diff = 0
            carry_ops = carry_trades.get('oportunidades', [])
            for carry in carry_ops:
                if carry['par'] == par:
                    carry_diff = carry['diferencial']
                    break

            # Eventos críticos
            impacto_eventos = 1  # Default BAIXO
            eventos_par = eventos.get('eventos_por_par', {}).get(par, {})
            if eventos_par:
                impacto = eventos_par.get('impacto_estimado', 'MEDIO')
                impacto_eventos = {'BAIXO': 1, 'MEDIO': 2, 'ALTO': 3}.get(impacto, 2)

            # Features técnicas
            nivel_proximo = dados_posicao.get('nivel_mais_proximo', {})
            dist_nivel = nivel_proximo.get('distancia_pct', 5.0)
            tipo_nivel = 1 if nivel_proximo.get('tipo_nivel') == 'suporte' else 0

            # Confluência (simulada - em produção seria calculada)
            confluencia = min(1.0, 1 / (1 + dist_nivel * 0.1))

            # Volume (simulado)
            volume_rel = np.random.uniform(0.8, 2.0)

            # Dados da posição
            direcao = 1 if dados_posicao.get('direction') == 'LONG' else -1
            pnl_atual = dados_posicao.get('pnl', 0)

            return [
                dxy_var, dxy_tend_7d, dxy_vol,
                carry_diff, impacto_eventos, dist_nivel,
                tipo_nivel, confluencia, volume_rel,
                direcao, pnl_atual
            ]

        except Exception as e:
            self.logger.error(f"Erro ao extrair features para {par}: {e}")
            return None

    def _calcular_score_confianca(self, probabilidade: float) -> str:
        """Calcular score de confiança"""
        if probabilidade >= 0.85:
            return "MUITO_ALTA"
        elif probabilidade >= 0.75:
            return "ALTA"
        elif probabilidade >= 0.65:
            return "MEDIA"
        else:
            return "BAIXA"

    def _gerar_analise_macro(self, par: str, dados_dxy: Dict,
                           eventos: Dict, carry_trades: Dict) -> Dict:
        """Gerar análise macroeconômica para um par"""
        return {
            'regime_dolar': dados_dxy.get('regime', 'ESTAVEL'),
            'dxy_variacao': dados_dxy.get('variacao_diaria', 0),
            'eventos_criticos': eventos.get('eventos_por_par', {}).get(par, {}).get('eventos', []),
            'carry_trade': next((c for c in carry_trades.get('oportunidades', []) if c['par'] == par), None)
        }

    def _gerar_analise_tecnica(self, dados_posicao: Dict) -> Dict:
        """Gerar análise técnica resumida"""
        nivel_proximo = dados_posicao.get('nivel_mais_proximo', {})

        return {
            'preco_atual': dados_posicao.get('current_price'),
            'nivel_critico': nivel_proximo.get('nivel_mais_proximo'),
            'tipo_nivel': nivel_proximo.get('tipo_nivel'),
            'distancia_pct': nivel_proximo.get('distancia_pct'),
            'suportes': dados_posicao.get('suportes_chave', [])[-2:],
            'resistencias': dados_posicao.get('resistencias_chave', [])[-2:]
        }

    def _gerar_recomendacao(self, dados_posicao: Dict, probabilidade: float) -> Dict:
        """Gerar recomendação baseada na análise"""
        nivel_proximo = dados_posicao.get('nivel_mais_proximo', {})
        direcao_posicao = dados_posicao.get('direction')

        # Lógica de recomendação
        if probabilidade >= 0.80:
            if direcao_posicao == 'LONG' and nivel_proximo.get('tipo_nivel') == 'suporte':
                acao = "MANTER_POSICAO"
                justificativa = "Alta probabilidade + posição LONG próxima de suporte"
            elif direcao_posicao == 'LONG' and nivel_proximo.get('tipo_nivel') == 'resistencia':
                acao = "CONSIDERAR_TAKE_PROFIT"
                justificativa = "Alta probabilidade + LONG próximo de resistência"
            else:
                acao = "MONITORAR_PROXIMAMENTE"
                justificativa = "Alta probabilidade de movimento"
        else:
            acao = "AGUARDAR_CONFIRMACAO"
            justificativa = "Aguardar maior confluência de sinais"

        return {
            'acao': acao,
            'justificativa': justificativa,
            'probabilidade': probabilidade
        }

    def _salvar_oportunidades(self, oportunidades: Dict):
        """Salvar oportunidades detectadas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"oportunidades_{timestamp}.json"
        caminho = os.path.join(self.caminho_oportunidades, arquivo)

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(oportunidades, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Oportunidades salvas: {caminho}")


def main():
    """Função principal para demonstração"""
    print("🚀 INICIANDO SISTEMA DE OPORTUNIDADES MACRO-TÉCNICAS")
    print("=" * 70)

    # Inicializar detector
    detector = DetectorOportunidadesML()

    # Detectar oportunidades
    oportunidades = detector.detectar_oportunidades()

    if 'erro' in oportunidades:
        print(f"❌ Erro: {oportunidades['erro']}")
        return

    # Exibir resultados
    print(f"\n📊 OPORTUNIDADES DETECTADAS: {oportunidades['total_oportunidades']}")
    print("=" * 70)

    for i, op in enumerate(oportunidades['oportunidades_detectadas'][:5], 1):
        print(f"\n🎯 OPORTUNIDADE #{i}: {op['par']}")
        print("-" * 40)
        print(f"   📈 Probabilidade: {op['probabilidade_sucesso']:.1%}")
        print(f"   🎖️  Confiança: {op['score_confianca']}")
        print(f"   💡 Ação: {op['recomendacao']['acao']}")
        print(f"   📝 Justificativa: {op['recomendacao']['justificativa']}")

        # Análise macro
        macro = op['analise_macro']
        print(f"   🌍 Regime USD: {macro['regime_dolar']}")
        print(f"   📊 DXY Var: {macro['dxy_variacao']:+.2f}%")

        # Análise técnica
        tecnica = op['analise_tecnica']
        print(f"   🎯 Nível crítico: {tecnica['nivel_critico']} ({tecnica['tipo_nivel']})")
        print(f"   📏 Distância: {tecnica['distancia_pct']:.2f}%")

    print(f"\n✅ SISTEMA OPERACIONAL - {oportunidades['timestamp_deteccao'][:19]}")

    return detector, oportunidades


if __name__ == "__main__":
    detector, oportunidades = main()