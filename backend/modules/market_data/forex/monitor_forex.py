# -*- coding: utf-8 -*-
"""
Monitor Forex - Sistema de Monitoramento Multi-Par.

Monitora 42 pares Forex/Crypto em tempo real:
- 7 Majors
- 12 Crosses principais
- 9 Crosses secundários
- 10 Exóticos
- 1 Ouro (XAU/USD)
- 3 Crypto (BTC, ETH)

Gera ranking de oportunidades por confiança e carry trade.
"""

import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import time

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src" / "dados"))

from analisador_forex import AnalisadorForex, AnaliseForex


class MonitorForex:
    """Monitor de oportunidades em múltiplos pares Forex."""

    # Lista completa de 42 pares para monitorar
    PARES_MONITORADOS = [
        # MAJORS
        'USDBRL', 'EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD',

        # CROSSES PRINCIPAIS
        'EURJPY', 'EURGBP', 'EURCHF', 'AUDJPY', 'GBPJPY', 'CHFJPY',
        'EURCAD', 'AUDCAD', 'CADJPY', 'NZDJPY', 'AUDNZD',

        # CROSSES SECUNDÁRIOS
        'GBPAUD', 'EURAUD', 'GBPCHF', 'EURNZD', 'AUDCHF', 'GBPNZD',
        'GBPCAD', 'CADCHF', 'NZDCAD', 'NZDCHF',

        # EXÓTICOS
        'USDINR', 'USDCNY', 'USDSGD', 'USDHKD', 'USDDKK',
        'USDSEK', 'USDTRY', 'USDMXN', 'USDZAR',

        # OURO
        'XAUUSD',

        # CRYPTO
        'BTCUSD', 'BTCEUR', 'ETHUSD'
    ]

    def __init__(self):
        """Inicializa o monitor."""
        self.analisador = AnalisadorForex()
        self.analises: List[AnaliseForex] = []

    def monitorar_todos(self, operacao: str = 'COMPRA', verbose: bool = False) -> List[AnaliseForex]:
        """
        Monitora todos os 42 pares configurados.

        Args:
            operacao: COMPRA ou VENDA
            verbose: Se True, exibe progresso detalhado

        Returns:
            Lista de análises ordenadas por confiança
        """

        print(f"\n{'='*80}")
        print(f"🌐 MONITOR FOREX - {len(self.PARES_MONITORADOS)} PARES")
        print(f"{'='*80}")
        print(f"Operação: {operacao}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        analises_sucesso = []
        analises_erro = []

        for i, par in enumerate(self.PARES_MONITORADOS, 1):
            try:
                if verbose:
                    print(f"\n[{i}/{len(self.PARES_MONITORADOS)}] Analisando {par}...", end=' ')
                else:
                    print(f"{'.':<3}", end='', flush=True)
                    if i % 20 == 0:
                        print(f" {i}/{len(self.PARES_MONITORADOS)}")

                # Análise sem print (modo silencioso)
                import io
                import contextlib

                # Capturar output para modo não-verbose
                if not verbose:
                    f = io.StringIO()
                    with contextlib.redirect_stdout(f):
                        analise = self.analisador.analisar_par(par, operacao)
                else:
                    analise = self.analisador.analisar_par(par, operacao)

                analises_sucesso.append(analise)

                if verbose:
                    print(f"✅ {analise.recomendacao} ({analise.confianca}%)")

                # Delay para evitar rate limiting
                time.sleep(0.1)

            except Exception as e:
                erro_msg = str(e)
                analises_erro.append({'par': par, 'erro': erro_msg})

                if verbose:
                    print(f"❌ ERRO: {erro_msg}")
                else:
                    print("❌", end='', flush=True)

        if not verbose:
            print()  # Nova linha após os pontos

        print(f"\n{'='*80}")
        print(f"✅ Analisados com sucesso: {len(analises_sucesso)}")
        print(f"❌ Erros: {len(analises_erro)}")
        print(f"{'='*80}\n")

        if analises_erro and verbose:
            print("\n⚠️  PARES COM ERRO:")
            for erro in analises_erro:
                print(f"  • {erro['par']}: {erro['erro']}")
            print()

        self.analises = sorted(analises_sucesso, key=lambda x: x.confianca, reverse=True)
        return self.analises

    def gerar_ranking(self, limite: int = 10) -> None:
        """
        Gera ranking das melhores oportunidades.

        Args:
            limite: Número de oportunidades a exibir
        """

        if not self.analises:
            print("⚠️  Nenhuma análise disponível. Execute monitorar_todos() primeiro.")
            return

        print(f"\n{'='*80}")
        print(f"🏆 TOP {limite} OPORTUNIDADES FOREX")
        print(f"{'='*80}\n")

        # Filtrar apenas aprovadas (confiança >= 50%)
        aprovadas = [a for a in self.analises if a.confianca >= 50]

        if not aprovadas:
            print("⚠️  Nenhuma oportunidade com confiança >= 50% encontrada.\n")
            print("🔍 ANÁLISE GERAL:")
            self._exibir_tabela_resumo(self.analises[:limite])
            return

        print(f"📊 Oportunidades Aprovadas: {len(aprovadas)}")
        print(f"{'='*80}\n")

        self._exibir_tabela_resumo(aprovadas[:limite])

    def _exibir_tabela_resumo(self, analises: List[AnaliseForex]) -> None:
        """Exibe tabela resumida de análises."""

        print(f"{'#':<4} {'Par':<10} {'Carry':>8} {'Conf.':>7} {'R:R':>7} {'Recomendação':<20}")
        print("-" * 80)

        for i, analise in enumerate(analises, 1):
            # Emoji de classificação
            if i == 1:
                emoji = "🥇"
            elif i == 2:
                emoji = "🥈"
            elif i == 3:
                emoji = "🥉"
            else:
                emoji = "  "

            # Emoji de recomendação
            if analise.confianca >= 70:
                status_emoji = "✅"
            elif analise.confianca >= 50:
                status_emoji = "⚠️ "
            else:
                status_emoji = "❌"

            print(f"{emoji} {i:<2} {analise.par:<10} " +
                  f"{float(analise.diferencial_juros):>7.2f}%  " +
                  f"{analise.confianca:>6}%  " +
                  f"{analise.risco_recompensa:>6.2f}  " +
                  f"{status_emoji} {analise.recomendacao:<18}")

        print(f"\n{'='*80}\n")

    def gerar_relatorio_categoria(self) -> None:
        """Gera relatório agregado por categoria de par."""

        if not self.analises:
            print("⚠️  Nenhuma análise disponível.")
            return

        categorias = {
            'Majors': ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD', 'USDBRL'],
            'Crosses': ['EURJPY', 'GBPJPY', 'EURGBP', 'EURCHF', 'AUDJPY', 'CHFJPY', 'EURCAD',
                       'AUDCAD', 'CADJPY', 'NZDJPY', 'AUDNZD', 'GBPAUD', 'EURAUD', 'GBPCHF',
                       'EURNZD', 'AUDCHF', 'GBPNZD', 'GBPCAD', 'CADCHF', 'NZDCAD', 'NZDCHF'],
            'Exóticos': ['USDINR', 'USDCNY', 'USDSGD', 'USDHKD', 'USDDKK', 'USDSEK',
                        'USDTRY', 'USDMXN', 'USDZAR'],
            'Ouro': ['XAUUSD'],
            'Crypto': ['BTCUSD', 'BTCEUR', 'ETHUSD']
        }

        print(f"\n{'='*80}")
        print("📋 RELATÓRIO POR CATEGORIA")
        print(f"{'='*80}\n")

        for categoria, pares in categorias.items():
            # Remover '/' dos pares analisados para comparação
            analises_cat = [a for a in self.analises if a.par.replace('/', '') in pares]

            if not analises_cat:
                continue

            aprovadas = [a for a in analises_cat if a.confianca >= 50]
            conf_media = sum(a.confianca for a in analises_cat) / len(analises_cat)

            print(f"{'='*80}")
            print(f"📊 {categoria.upper()}")
            print(f"{'='*80}")
            print(f"Total analisados: {len(analises_cat)}")
            print(f"Aprovados (≥50%): {len(aprovadas)}")
            print(f"Confiança média: {conf_media:.1f}%")

            if aprovadas:
                melhor = max(aprovadas, key=lambda x: x.confianca)
                print(f"Melhor oportunidade: {melhor.par} ({melhor.confianca}%, Carry {float(melhor.diferencial_juros):.2f}%)")

            print()

    def exportar_csv(self, arquivo: str = 'monitor_forex_resultado.csv') -> None:
        """Exporta resultados para CSV."""

        if not self.analises:
            print("⚠️  Nenhuma análise disponível.")
            return

        import csv

        caminho = Path(__file__).parent / arquivo

        with open(caminho, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Cabeçalho
            writer.writerow([
                'Par', 'Moeda_Base', 'Moeda_Cotada', 'Carry_%', 'Carry_Rating',
                'Divergencia_Politica', 'Preco_Atual', 'Entrada', 'Stop', 'TP1', 'TP2',
                'Tendencia', 'R_R', 'Correlacao_WIN', 'Sentimento', 'Confianca_%',
                'Recomendacao', 'Par_Alternativo', 'Timestamp'
            ])

            # Dados
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for a in self.analises:
                writer.writerow([
                    a.par, a.moeda_base, a.moeda_cotada, float(a.diferencial_juros),
                    a.carry_rating, a.divergencia_politica, float(a.preco_atual),
                    float(a.entrada_sugerida), float(a.stop_loss), float(a.take_profit_1),
                    float(a.take_profit_2), a.tendencia, a.risco_recompensa,
                    a.impacto_win, float(a.score_sentimento), a.confianca,
                    a.recomendacao, a.par_alternativo or '', timestamp
                ])

        print(f"✅ Resultados exportados para: {caminho}\n")


def main():
    """Função principal - execução do monitor."""

    import argparse

    parser = argparse.ArgumentParser(
        description='Monitor Forex - Análise de 42 pares em tempo real'
    )

    parser.add_argument(
        '--operacao',
        choices=['COMPRA', 'VENDA'],
        default='COMPRA',
        help='Tipo de operação (default: COMPRA)'
    )

    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Número de oportunidades no ranking (default: 10)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Exibe progresso detalhado'
    )

    parser.add_argument(
        '--categorias',
        action='store_true',
        help='Gera relatório por categoria'
    )

    parser.add_argument(
        '--exportar',
        action='store_true',
        help='Exporta resultados para CSV'
    )

    args = parser.parse_args()

    # Criar monitor
    monitor = MonitorForex()

    # Monitorar todos os pares
    print("🚀 Iniciando monitoramento...\n")
    monitor.monitorar_todos(operacao=args.operacao, verbose=args.verbose)

    # Gerar ranking
    monitor.gerar_ranking(limite=args.top)

    # Relatório por categoria (opcional)
    if args.categorias:
        monitor.gerar_relatorio_categoria()

    # Exportar CSV (opcional)
    if args.exportar:
        monitor.exportar_csv()

    print("✅ Monitoramento concluído!\n")


if __name__ == "__main__":
    main()
