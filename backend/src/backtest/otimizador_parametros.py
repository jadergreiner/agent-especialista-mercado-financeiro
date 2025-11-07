"""
Sistema de otimização de parâmetros para estratégias de trading.
Implementa Walk-Forward Analysis para evitar overfitting.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from itertools import product

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backtest.motor_backtest import (
    BacktestEngine,
    EstrategiaCruzamentoMedias,
    EstrategiaRSI,
    EstrategiaBollinger,
    EstrategiaMACD,
)


@dataclass
class ResultadoOtimizacao:
    """Resultado de uma otimização de parâmetros."""
    parametros: Dict[str, Any]
    taxa_acerto: float
    pnl_total: float
    expectativa: float
    payoff_ratio: float
    num_operacoes: int
    sharpe_ratio: float


class OtimizadorParametros:
    """Otimizador de parâmetros com Walk-Forward Analysis."""

    def __init__(self, db_path: Path = None):
        self.engine = BacktestEngine(db_path)

    def grid_search_ma_crossover(
        self,
        instrumento: str,
        data_inicio: str,
        data_fim: str,
        periodos_curtos: List[int] = None,
        periodos_longos: List[int] = None,
    ) -> List[ResultadoOtimizacao]:
        """
        Busca em grade para estratégia de cruzamento de médias.

        Args:
            instrumento: Instrumento a testar
            data_inicio: Data inicial YYYY-MM-DD
            data_fim: Data final YYYY-MM-DD
            periodos_curtos: Lista de períodos curtos a testar (default: [5, 9, 13, 21])
            periodos_longos: Lista de períodos longos a testar (default: [21, 34, 50, 89])
        """
        if periodos_curtos is None:
            periodos_curtos = [5, 9, 13, 21]
        if periodos_longos is None:
            periodos_longos = [21, 34, 50, 89]

        resultados = []
        total_combinacoes = len(periodos_curtos) * len(periodos_longos)
        contador = 0

        print(f"\n🔬 OTIMIZAÇÃO: Cruzamento de Médias")
        print(f"📊 Testando {total_combinacoes} combinações de parâmetros...")
        print(f"📅 Período: {data_inicio} até {data_fim}\n")

        for curto, longo in product(periodos_curtos, periodos_longos):
            if curto >= longo:
                continue

            contador += 1
            print(f"[{contador}/{total_combinacoes}] Testando MA{curto}/MA{longo}...", end=' ')

            estrategia = EstrategiaCruzamentoMedias(
                periodo_curto=curto,
                periodo_longo=longo
            )

            metricas = self._executar_e_calcular_metricas(
                estrategia, instrumento, data_inicio, data_fim
            )

            if metricas:
                resultado = ResultadoOtimizacao(
                    parametros={'periodo_curto': curto, 'periodo_longo': longo},
                    **metricas
                )
                resultados.append(resultado)
                print(f"✅ Taxa: {metricas['taxa_acerto']:.1f}% | PnL: {metricas['pnl_total']:+.0f}")
            else:
                print("❌ Sem operações")

        return sorted(resultados, key=lambda x: x.expectativa, reverse=True)

    def grid_search_rsi(
        self,
        instrumento: str,
        data_inicio: str,
        data_fim: str,
        periodos: List[int] = None,
        niveis_sobrecompra: List[float] = None,
        niveis_sobrevenda: List[float] = None,
    ) -> List[ResultadoOtimizacao]:
        """Busca em grade para estratégia RSI."""
        if periodos is None:
            periodos = [9, 14, 21, 25]
        if niveis_sobrecompra is None:
            niveis_sobrecompra = [65, 70, 75, 80]
        if niveis_sobrevenda is None:
            niveis_sobrevenda = [20, 25, 30, 35]

        resultados = []
        total_combinacoes = len(periodos) * len(niveis_sobrecompra) * len(niveis_sobrevenda)
        contador = 0

        print(f"\n🔬 OTIMIZAÇÃO: RSI")
        print(f"📊 Testando {total_combinacoes} combinações de parâmetros...")
        print(f"📅 Período: {data_inicio} até {data_fim}\n")

        for periodo, sobrecompra, sobrevenda in product(periodos, niveis_sobrecompra, niveis_sobrevenda):
            if sobrevenda >= sobrecompra:
                continue

            contador += 1
            print(f"[{contador}] RSI({periodo}, {sobrevenda}/{sobrecompra})...", end=' ')

            estrategia = EstrategiaRSI(
                periodo_rsi=periodo,
                nivel_sobrecompra=sobrecompra,
                nivel_sobrevenda=sobrevenda
            )

            metricas = self._executar_e_calcular_metricas(
                estrategia, instrumento, data_inicio, data_fim
            )

            if metricas:
                resultado = ResultadoOtimizacao(
                    parametros={
                        'periodo_rsi': periodo,
                        'nivel_sobrecompra': sobrecompra,
                        'nivel_sobrevenda': sobrevenda
                    },
                    **metricas
                )
                resultados.append(resultado)
                print(f"✅ Taxa: {metricas['taxa_acerto']:.1f}% | PnL: {metricas['pnl_total']:+.0f}")
            else:
                print("❌ Sem operações")

        return sorted(resultados, key=lambda x: x.expectativa, reverse=True)

    def grid_search_bollinger(
        self,
        instrumento: str,
        data_inicio: str,
        data_fim: str,
        periodos: List[int] = None,
        desvios: List[float] = None,
    ) -> List[ResultadoOtimizacao]:
        """Busca em grade para estratégia Bollinger."""
        if periodos is None:
            periodos = [15, 20, 25, 30]
        if desvios is None:
            desvios = [1.5, 2.0, 2.5, 3.0]

        resultados = []
        total_combinacoes = len(periodos) * len(desvios)
        contador = 0

        print(f"\n🔬 OTIMIZAÇÃO: Bandas de Bollinger")
        print(f"📊 Testando {total_combinacoes} combinações de parâmetros...")
        print(f"📅 Período: {data_inicio} até {data_fim}\n")

        for periodo, desvio in product(periodos, desvios):
            contador += 1
            print(f"[{contador}/{total_combinacoes}] BB({periodo}, {desvio}σ)...", end=' ')

            estrategia = EstrategiaBollinger(
                periodo=periodo,
                num_desvios=desvio
            )

            metricas = self._executar_e_calcular_metricas(
                estrategia, instrumento, data_inicio, data_fim
            )

            if metricas:
                resultado = ResultadoOtimizacao(
                    parametros={'periodo': periodo, 'num_desvios': desvio},
                    **metricas
                )
                resultados.append(resultado)
                print(f"✅ Taxa: {metricas['taxa_acerto']:.1f}% | PnL: {metricas['pnl_total']:+.0f}")
            else:
                print("❌ Sem operações")

        return sorted(resultados, key=lambda x: x.expectativa, reverse=True)

    def grid_search_macd(
        self,
        instrumento: str,
        data_inicio: str,
        data_fim: str,
        periodos_rapidos: List[int] = None,
        periodos_lentos: List[int] = None,
        periodos_sinal: List[int] = None,
    ) -> List[ResultadoOtimizacao]:
        """Busca em grade para estratégia MACD."""
        if periodos_rapidos is None:
            periodos_rapidos = [8, 12, 16]
        if periodos_lentos is None:
            periodos_lentos = [21, 26, 30]
        if periodos_sinal is None:
            periodos_sinal = [7, 9, 11]

        resultados = []
        total_combinacoes = len(periodos_rapidos) * len(periodos_lentos) * len(periodos_sinal)
        contador = 0

        print(f"\n🔬 OTIMIZAÇÃO: MACD")
        print(f"📊 Testando {total_combinacoes} combinações de parâmetros...")
        print(f"📅 Período: {data_inicio} até {data_fim}\n")

        for rapida, lenta, sinal in product(periodos_rapidos, periodos_lentos, periodos_sinal):
            if rapida >= lenta:
                continue

            contador += 1
            print(f"[{contador}] MACD({rapida},{lenta},{sinal})...", end=' ')

            estrategia = EstrategiaMACD(
                rapida=rapida,
                lenta=lenta,
                sinal=sinal
            )

            metricas = self._executar_e_calcular_metricas(
                estrategia, instrumento, data_inicio, data_fim
            )

            if metricas:
                resultado = ResultadoOtimizacao(
                    parametros={
                        'rapida': rapida,
                        'lenta': lenta,
                        'sinal': sinal
                    },
                    **metricas
                )
                resultados.append(resultado)
                print(f"✅ Taxa: {metricas['taxa_acerto']:.1f}% | PnL: {metricas['pnl_total']:+.0f}")
            else:
                print("❌ Sem operações")

        return sorted(resultados, key=lambda x: x.expectativa, reverse=True)

    def _executar_e_calcular_metricas(
        self,
        estrategia,
        instrumento: str,
        data_inicio: str,
        data_fim: str
    ) -> Dict[str, Any] | None:
        """Executa backtest e calcula métricas."""
        # Carregar dados
        dados = self.engine.carregar_dados_historicos(instrumento, data_inicio, data_fim)

        if not dados:
            return None

        # Detectar janela mínima
        if hasattr(estrategia, 'periodo_curto') and hasattr(estrategia, 'periodo_longo'):
            janela_minima = max(estrategia.periodo_curto, estrategia.periodo_longo) + 14
        elif hasattr(estrategia, 'periodo_rsi'):
            janela_minima = estrategia.periodo_rsi + 14
        elif hasattr(estrategia, 'periodo'):
            janela_minima = estrategia.periodo + 14
        elif hasattr(estrategia, 'lenta'):
            janela_minima = estrategia.lenta + estrategia.sinal + 14
        else:
            janela_minima = 50

        operacoes = []

        for i in range(janela_minima, len(dados)):
            historico_ate_hoje = dados[:i+1]
            sinal = estrategia.gerar_sinal(historico_ate_hoje)

            if sinal:
                # Simular resultado D+1
                if i + 1 < len(dados):
                    dado_d1 = dados[i + 1]
                    preco_d1 = dado_d1['ultimo']

                    # Verificar se atingiu stop ou target
                    if sinal.tipo == 'COMPRA':
                        if preco_d1 <= sinal.stop_loss:
                            acertou = False
                            pnl = sinal.stop_loss - sinal.preco_entrada
                        elif preco_d1 >= sinal.take_profit:
                            acertou = True
                            pnl = sinal.take_profit - sinal.preco_entrada
                        else:
                            # Saída no fechamento
                            pnl = preco_d1 - sinal.preco_entrada
                            acertou = pnl > 0
                    else:  # VENDA
                        if preco_d1 >= sinal.stop_loss:
                            acertou = False
                            pnl = sinal.preco_entrada - sinal.stop_loss
                        elif preco_d1 <= sinal.take_profit:
                            acertou = True
                            pnl = sinal.preco_entrada - sinal.take_profit
                        else:
                            # Saída no fechamento
                            pnl = sinal.preco_entrada - preco_d1
                            acertou = pnl > 0

                    operacoes.append({
                        'acertou': acertou,
                        'pnl': pnl
                    })

        if not operacoes:
            return None

        # Calcular métricas
        num_ops = len(operacoes)
        acertos = sum(1 for op in operacoes if op['acertou'])
        taxa_acerto = (acertos / num_ops * 100) if num_ops > 0 else 0

        pnl_total = sum(op['pnl'] for op in operacoes)
        expectativa = pnl_total / num_ops if num_ops > 0 else 0

        ganhos = [op['pnl'] for op in operacoes if op['pnl'] > 0]
        perdas = [op['pnl'] for op in operacoes if op['pnl'] < 0]

        ganho_medio = sum(ganhos) / len(ganhos) if ganhos else 0
        perda_media = sum(perdas) / len(perdas) if perdas else 0
        payoff_ratio = abs(ganho_medio / perda_media) if perda_media != 0 else 0

        # Sharpe Ratio simplificado (assumindo risk-free rate = 0)
        if num_ops > 1:
            retornos = [op['pnl'] for op in operacoes]
            media_retorno = sum(retornos) / len(retornos)
            variancia = sum((r - media_retorno) ** 2 for r in retornos) / (len(retornos) - 1)
            desvio_padrao = variancia ** 0.5
            sharpe_ratio = (media_retorno / desvio_padrao) if desvio_padrao > 0 else 0
        else:
            sharpe_ratio = 0

        return {
            'taxa_acerto': taxa_acerto,
            'pnl_total': pnl_total,
            'expectativa': expectativa,
            'payoff_ratio': payoff_ratio,
            'num_operacoes': num_ops,
            'sharpe_ratio': sharpe_ratio
        }

    def walk_forward_analysis(
        self,
        estrategia_tipo: str,
        instrumento: str,
        periodos_treino: List[Tuple[str, str]],
        periodos_validacao: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        """
        Walk-Forward Analysis: treina em períodos passados e valida em períodos futuros.

        Args:
            estrategia_tipo: 'ma', 'rsi', 'bollinger' ou 'macd'
            instrumento: Instrumento a testar
            periodos_treino: Lista de tuplas (data_inicio, data_fim) para treino
            periodos_validacao: Lista de tuplas (data_inicio, data_fim) para validação
        """
        print(f"\n🚀 WALK-FORWARD ANALYSIS: {estrategia_tipo.upper()}")
        print(f"📊 {len(periodos_treino)} períodos de treino")
        print(f"📊 {len(periodos_validacao)} períodos de validação\n")

        resultados_wfa = {
            'treino': [],
            'validacao': [],
            'parametros_otimos': []
        }

        for i, (treino, validacao) in enumerate(zip(periodos_treino, periodos_validacao), 1):
            print(f"\n{'='*80}")
            print(f"JANELA {i}: Treino {treino[0]} a {treino[1]} | Validação {validacao[0]} a {validacao[1]}")
            print(f"{'='*80}")

            # Otimizar no período de treino
            if estrategia_tipo == 'ma':
                resultados_treino = self.grid_search_ma_crossover(
                    instrumento, treino[0], treino[1]
                )
            elif estrategia_tipo == 'rsi':
                resultados_treino = self.grid_search_rsi(
                    instrumento, treino[0], treino[1]
                )
            elif estrategia_tipo == 'bollinger':
                resultados_treino = self.grid_search_bollinger(
                    instrumento, treino[0], treino[1]
                )
            elif estrategia_tipo == 'macd':
                resultados_treino = self.grid_search_macd(
                    instrumento, treino[0], treino[1]
                )
            else:
                raise ValueError(f"Estratégia desconhecida: {estrategia_tipo}")

            if not resultados_treino:
                print("❌ Nenhum resultado válido no período de treino")
                continue

            # Melhor resultado no treino
            melhor_treino = resultados_treino[0]
            print(f"\n🏆 MELHOR NO TREINO: {melhor_treino.parametros}")
            print(f"   Taxa: {melhor_treino.taxa_acerto:.1f}% | Expectativa: {melhor_treino.expectativa:+.1f}")

            # Testar na validação
            if estrategia_tipo == 'ma':
                estrategia = EstrategiaCruzamentoMedias(**melhor_treino.parametros)
            elif estrategia_tipo == 'rsi':
                estrategia = EstrategiaRSI(**melhor_treino.parametros)
            elif estrategia_tipo == 'bollinger':
                estrategia = EstrategiaBollinger(**melhor_treino.parametros)
            elif estrategia_tipo == 'macd':
                estrategia = EstrategiaMACD(**melhor_treino.parametros)

            metricas_validacao = self._executar_e_calcular_metricas(
                estrategia, instrumento, validacao[0], validacao[1]
            )

            if metricas_validacao:
                print(f"\n📈 RESULTADO NA VALIDAÇÃO:")
                print(f"   Taxa: {metricas_validacao['taxa_acerto']:.1f}% | Expectativa: {metricas_validacao['expectativa']:+.1f}")

                resultados_wfa['treino'].append(melhor_treino)
                resultados_wfa['validacao'].append(metricas_validacao)
                resultados_wfa['parametros_otimos'].append(melhor_treino.parametros)
            else:
                print("❌ Nenhuma operação no período de validação")

        # Resumo geral
        if resultados_wfa['validacao']:
            print(f"\n{'='*80}")
            print("📊 RESUMO WALK-FORWARD ANALYSIS")
            print(f"{'='*80}")

            taxa_media_val = sum(r['taxa_acerto'] for r in resultados_wfa['validacao']) / len(resultados_wfa['validacao'])
            exp_media_val = sum(r['expectativa'] for r in resultados_wfa['validacao']) / len(resultados_wfa['validacao'])

            print(f"Taxa de acerto média (validação): {taxa_media_val:.1f}%")
            print(f"Expectativa média (validação): {exp_media_val:+.1f} pontos/op")
            print(f"\nParâmetros ótimos por janela:")
            for i, params in enumerate(resultados_wfa['parametros_otimos'], 1):
                print(f"  Janela {i}: {params}")

        return resultados_wfa


if __name__ == '__main__':
    # Exemplo de uso
    otimizador = OtimizadorParametros()

    # Grid search simples
    # resultados = otimizador.grid_search_ma_crossover('WIN', '2024-01-01', '2024-12-31')

    # Walk-forward analysis
    periodos_treino = [
        ('2021-01-01', '2022-12-31'),  # Treino: 2021-2022
        ('2022-01-01', '2023-12-31'),  # Treino: 2022-2023
    ]
    periodos_validacao = [
        ('2023-01-01', '2023-12-31'),  # Validação: 2023
        ('2024-01-01', '2024-12-31'),  # Validação: 2024
    ]

    otimizador.walk_forward_analysis('ma', 'WIN', periodos_treino, periodos_validacao)
