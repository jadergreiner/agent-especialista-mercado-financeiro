# -*- coding: utf-8 -*-
"""
EXEMPLO: Integração de Boletins B3 com Estratégias de Trading

Este arquivo demonstra como os dados dos boletins B3 serão integrados
às estratégias existentes para melhorar a qualidade dos sinais.

NOTA: Este é um exemplo de referência. A implementação real ocorrerá após
      obter dados reais dos boletins B3.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, Dict


class FiltrosBoletimB3:
    """Filtros baseados em dados de boletins B3 para melhorar estratégias."""

    def __init__(self, gerenciador_boletim):
        """
        Args:
            gerenciador_boletim: Instância de GerenciadorBoletimB3
        """
        self.gerenciador = gerenciador_boletim

        # Configurações padrão
        self.volume_relativo_minimo = 0.7  # 70% da média
        self.spread_maximo_pontos = 10.0
        self.dias_antes_vencimento_alerta = 10
        self.percentual_rollover = 0.5  # 50% do volume no próximo

    def verificar_liquidez(self, simbolo: str, data_pregao: date) -> Dict:
        """
        Verifica condições de liquidez para operar.

        Returns:
            dict: {
                'pode_operar': bool,
                'motivo': str,
                'volume_relativo': float,
                'spread': float
            }
        """
        metricas = self.gerenciador.calcular_metricas_microestrutura(simbolo, data_pregao)

        resultado = {
            'pode_operar': True,
            'motivo': 'Liquidez adequada',
            'volume_relativo': metricas.get('volume_relativo'),
            'spread': None
        }

        # Verificar volume relativo
        if metricas.get('volume_relativo'):
            if metricas['volume_relativo'] < self.volume_relativo_minimo:
                resultado['pode_operar'] = False
                resultado['motivo'] = f"Volume baixo ({metricas['volume_relativo']:.1%} da média)"
                return resultado

        # Verificar spread (se disponível)
        boletins = self.gerenciador.obter_boletins(simbolo, data_pregao, data_pregao)
        if boletins and boletins[0].get('spread_bid_ask'):
            spread = boletins[0]['spread_bid_ask']
            resultado['spread'] = spread

            if spread > self.spread_maximo_pontos:
                resultado['pode_operar'] = False
                resultado['motivo'] = f"Spread muito alto ({spread:.1f} pontos)"
                return resultado

        return resultado

    def analisar_open_interest(self, simbolo: str, data_pregao: date) -> Dict:
        """
        Analisa padrão de Open Interest para confirmar tendências.

        Returns:
            dict: {
                'forca_tendencia': str,  # 'ALTA_FORTE', 'BAIXA_FORTE', 'RALI_FRACO', 'QUEDA_FRACA', 'NEUTRO'
                'boost_compra': float,   # Multiplicador para sinais de compra (-0.3 a +0.3)
                'boost_venda': float,    # Multiplicador para sinais de venda (-0.3 a +0.3)
                'variacao_oi': float,
                'variacao_preco': float
            }
        """
        boletins = self.gerenciador.obter_boletins(
            simbolo,
            date(data_pregao.year, data_pregao.month, 1),  # Início do mês
            data_pregao
        )

        if len(boletins) < 2:
            return {
                'forca_tendencia': 'NEUTRO',
                'boost_compra': 0.0,
                'boost_venda': 0.0,
                'variacao_oi': None,
                'variacao_preco': None
            }

        # Comparar hoje vs ontem
        hoje = boletins[0]
        ontem = boletins[1]

        var_preco = (hoje['fechamento'] - ontem['fechamento']) / ontem['fechamento']
        var_oi = (hoje['contratos_abertos'] - ontem['contratos_abertos']) / ontem['contratos_abertos']

        # Definir força da tendência
        if var_preco > 0 and var_oi > 0:
            forca = 'ALTA_FORTE'
            boost_compra = +0.3
            boost_venda = -0.2
        elif var_preco < 0 and var_oi > 0:
            forca = 'BAIXA_FORTE'
            boost_compra = -0.2
            boost_venda = +0.3
        elif var_preco > 0 and var_oi < 0:
            forca = 'RALI_FRACO'
            boost_compra = -0.3
            boost_venda = +0.1
        elif var_preco < 0 and var_oi < 0:
            forca = 'QUEDA_FRACA'
            boost_compra = +0.1
            boost_venda = -0.3
        else:
            forca = 'NEUTRO'
            boost_compra = 0.0
            boost_venda = 0.0

        return {
            'forca_tendencia': forca,
            'boost_compra': boost_compra,
            'boost_venda': boost_venda,
            'variacao_oi': var_oi,
            'variacao_preco': var_preco
        }

    def verificar_risco_rollover(self, simbolo: str, data_pregao: date, data_vencimento: date) -> Dict:
        """
        Verifica se está próximo do vencimento e se deve usar próximo contrato.

        Returns:
            dict: {
                'alerta_rollover': bool,
                'dias_ate_vencimento': int,
                'usar_proximo_vencimento': bool,
                'percentual_volume_proximo': float
            }
        """
        dias_ate_venc = (data_vencimento - data_pregao).days

        resultado = {
            'alerta_rollover': dias_ate_venc <= self.dias_antes_vencimento_alerta,
            'dias_ate_vencimento': dias_ate_venc,
            'usar_proximo_vencimento': False,
            'percentual_volume_proximo': None
        }

        # Se está próximo do vencimento, verificar se volume já migrou
        if resultado['alerta_rollover']:
            # TODO: Consultar volumes de diferentes vencimentos
            # Por enquanto, regra simples: últimos 7 dias = usar próximo
            resultado['usar_proximo_vencimento'] = dias_ate_venc <= 7

        return resultado

    def calcular_sentiment_cot(self, simbolo: str, data_pregao: date) -> Dict:
        """
        Calcula sentiment baseado em posicionamento (similar ao COT Report).

        Returns:
            dict: {
                'sentiment_score': float,  # -1.0 (bearish) a +1.0 (bullish)
                'fluxo_pf': str,          # 'COMPRANDO', 'VENDENDO', 'NEUTRO'
                'fluxo_institucional': str,
                'fluxo_estrangeiro': str,
                'ajuste_estrategia': str  # Recomendação
            }
        """
        boletins = self.gerenciador.obter_boletins(
            simbolo,
            date(data_pregao.year, data_pregao.month, 1),
            data_pregao
        )

        if len(boletins) < 2:
            return {
                'sentiment_score': 0.0,
                'fluxo_pf': 'NEUTRO',
                'fluxo_institucional': 'NEUTRO',
                'fluxo_estrangeiro': 'NEUTRO',
                'ajuste_estrategia': 'Manter padrão'
            }

        hoje = boletins[0]
        ontem = boletins[1]

        # Verificar se dados de posicionamento estão disponíveis
        if not hoje.get('posicao_pessoa_fisica'):
            return {
                'sentiment_score': 0.0,
                'fluxo_pf': 'N/A',
                'fluxo_institucional': 'N/A',
                'fluxo_estrangeiro': 'N/A',
                'ajuste_estrategia': 'Dados não disponíveis'
            }

        # Calcular fluxos
        fluxo_pf = hoje['posicao_pessoa_fisica'] - ontem['posicao_pessoa_fisica']
        fluxo_inst = hoje['posicao_investidor_institucional'] - ontem['posicao_investidor_institucional']
        fluxo_est = hoje['posicao_investidor_estrangeiro'] - ontem['posicao_investidor_estrangeiro']

        # Sentiment score: -1 (bearish) a +1 (bullish)
        # Lógica: PF contrário (peso -0.3), Institucional seguir (peso +0.4), Estrangeiro seguir (peso +0.3)
        sentiment = 0.0

        # PF: sentimento contrário
        if abs(fluxo_pf) > 1000:  # Movimento significativo
            sentiment -= 0.3 if fluxo_pf > 0 else -0.3

        # Institucional: seguir smart money
        if abs(fluxo_inst) > 1000:
            sentiment += 0.4 if fluxo_inst > 0 else -0.4

        # Estrangeiro: seguir fluxo global
        if abs(fluxo_est) > 1000:
            sentiment += 0.3 if fluxo_est > 0 else -0.3

        # Limitar entre -1 e +1
        sentiment = max(-1.0, min(1.0, sentiment))

        # Classificar fluxos
        def classificar(valor):
            if valor > 1000: return 'COMPRANDO'
            elif valor < -1000: return 'VENDENDO'
            else: return 'NEUTRO'

        # Recomendação de ajuste
        if sentiment > 0.5:
            ajuste = 'Favorecer sinais de compra (+20% peso)'
        elif sentiment < -0.5:
            ajuste = 'Favorecer sinais de venda (+20% peso)'
        else:
            ajuste = 'Manter pesos padrão'

        return {
            'sentiment_score': sentiment,
            'fluxo_pf': classificar(fluxo_pf),
            'fluxo_institucional': classificar(fluxo_inst),
            'fluxo_estrangeiro': classificar(fluxo_est),
            'ajuste_estrategia': ajuste
        }


class EstrategiaComBoletins:
    """
    Exemplo de estratégia que integra filtros de boletim B3.

    Esta classe demonstra como a estratégia ensemble_optimized seria
    aprimorada com dados dos boletins.
    """

    def __init__(self, estrategia_base, gerenciador_boletim):
        """
        Args:
            estrategia_base: Estratégia original (ex: EstrategiaEnsemble)
            gerenciador_boletim: GerenciadorBoletimB3
        """
        self.estrategia_base = estrategia_base
        self.filtros = FiltrosBoletimB3(gerenciador_boletim)

    def gerar_sinal(self, dados_mercado: Dict, data_pregao: date) -> Optional[Dict]:
        """
        Gera sinal considerando análise técnica + dados de boletim.

        Args:
            dados_mercado: Dados históricos de preços
            data_pregao: Data do pregão

        Returns:
            dict com sinal ou None se filtrado
        """
        simbolo = dados_mercado.get('simbolo', 'WIN')
        data_vencimento = dados_mercado.get('vencimento')

        # FASE 1: Verificar filtros de liquidez
        liquidez = self.filtros.verificar_liquidez(simbolo, data_pregao)
        if not liquidez['pode_operar']:
            print(f"❌ Filtro de liquidez: {liquidez['motivo']}")
            return None

        # FASE 2: Verificar rollover
        if data_vencimento:
            rollover = self.filtros.verificar_risco_rollover(simbolo, data_pregao, data_vencimento)
            if rollover['usar_proximo_vencimento']:
                print(f"⚠️  Rollover: usar próximo vencimento ({rollover['dias_ate_vencimento']} dias)")
                # Aqui seria ajustado o contrato alvo

        # FASE 3: Gerar sinal técnico base
        sinal_base = self.estrategia_base.gerar_sinal(dados_mercado)

        if not sinal_base:
            return None

        # FASE 4: Analisar Open Interest para confirmação
        analise_oi = self.filtros.analisar_open_interest(simbolo, data_pregao)

        # Ajustar força do sinal baseado em OI
        if sinal_base['direcao'] == 'COMPRA':
            boost = analise_oi['boost_compra']
            sinal_base['forca'] = sinal_base.get('forca', 1.0) * (1 + boost)
            sinal_base['confirmacao_oi'] = analise_oi['forca_tendencia']

            # Se OI contradiz muito, cancelar sinal
            if analise_oi['forca_tendencia'] == 'RALI_FRACO':
                print(f"❌ OI indica rali fraco - sinal cancelado")
                return None

        elif sinal_base['direcao'] == 'VENDA':
            boost = analise_oi['boost_venda']
            sinal_base['forca'] = sinal_base.get('forca', 1.0) * (1 + boost)
            sinal_base['confirmacao_oi'] = analise_oi['forca_tendencia']

            if analise_oi['forca_tendencia'] == 'QUEDA_FRACA':
                print(f"❌ OI indica queda fraca - sinal cancelado")
                return None

        # FASE 5: Ajustar targets/stops baseado em sentiment
        sentiment = self.filtros.calcular_sentiment_cot(simbolo, data_pregao)

        if sentiment['sentiment_score'] > 0.5 and sinal_base['direcao'] == 'COMPRA':
            # Smart money concorda - aumentar target
            sinal_base['tp2_atr_mult'] = sinal_base.get('tp2_atr_mult', 3.0) + 0.5
            print(f"📈 Sentiment bullish ({sentiment['sentiment_score']:.2f}) - target aumentado")

        elif sentiment['sentiment_score'] < -0.5 and sinal_base['direcao'] == 'VENDA':
            # Smart money concorda - aumentar target
            sinal_base['tp2_atr_mult'] = sinal_base.get('tp2_atr_mult', 3.0) + 0.5
            print(f"📉 Sentiment bearish ({sentiment['sentiment_score']:.2f}) - target aumentado")

        else:
            # Sentimento neutro ou contrário - manter conservador
            print(f"⚖️  Sentiment neutro ({sentiment['sentiment_score']:.2f}) - targets padrão")

        # Adicionar metadados do boletim ao sinal
        sinal_base['metadados_boletim'] = {
            'volume_relativo': liquidez.get('volume_relativo'),
            'spread': liquidez.get('spread'),
            'forca_oi': analise_oi['forca_tendencia'],
            'sentiment_score': sentiment['sentiment_score'],
            'fluxo_institucional': sentiment['fluxo_institucional']
        }

        return sinal_base


def exemplo_uso_completo():
    """Demonstração de uso completo da integração."""

    from src.dados.boletim_b3 import GerenciadorBoletimB3
    from src.backtest.estrategias_avancadas import EstrategiaEnsemble

    # 1. Inicializar componentes
    gerenciador_boletim = GerenciadorBoletimB3()

    estrategia_base = EstrategiaEnsemble(
        peso_ma=1.1,
        peso_rsi=1.0,
        peso_bollinger=0.8,
        peso_macd=0.6,
        limiar_consenso=0.55
    )

    estrategia_aprimorada = EstrategiaComBoletins(
        estrategia_base=estrategia_base,
        gerenciador_boletim=gerenciador_boletim
    )

    # 2. Gerar sinal com todos os filtros
    dados_exemplo = {
        'simbolo': 'WIN',
        'vencimento': date(2024, 12, 27),
        # ... outros dados de preços
    }

    sinal = estrategia_aprimorada.gerar_sinal(dados_exemplo, date(2024, 11, 5))

    if sinal:
        print(f"\n✅ SINAL GERADO:")
        print(f"   Direção: {sinal['direcao']}")
        print(f"   Força: {sinal['forca']:.2f}")
        print(f"   Confirmação OI: {sinal['confirmacao_oi']}")
        print(f"   Sentiment: {sinal['metadados_boletim']['sentiment_score']:.2f}")
    else:
        print(f"\n❌ Nenhum sinal gerado (filtrado)")


if __name__ == "__main__":
    print("Este é um arquivo de exemplo/referência.")
    print("A implementação real será feita após obter dados reais dos boletins B3.")
    print("\nEstrutura demonstrada:")
    print("  - FiltrosBoletimB3: Classe com todos os filtros")
    print("  - EstrategiaComBoletins: Wrapper que adiciona filtros à estratégia base")
    print("  - Exemplo de fluxo completo: liquidez → rollover → técnica → OI → sentiment")
