"""Script para comparar performance de diferentes estratégias de trading."""

import sqlite3
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

def analisar_estrategias():
    """Analisa e compara todas as estratégias testadas."""

    # Conectar ao banco
    db_path = Path(__file__).parent / 'data' / 'recomendacoes.sqlite'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Buscar todas as recomendações com resultados
    query = """
    SELECT
        r.id,
        r.estrategia_nome,
        r.direcao,
        r.preco_entrada,
        r.stop_loss,
        r.tp1,
        r.confianca,
        res.acertou,
        res.preco_saida,
        res.pnl_pontos,
        res.pnl_reais,
        res.status,
        res.motivo_saida
    FROM recomendacoes r
    INNER JOIN resultados res ON r.id = res.id_recomendacao
    WHERE r.estrategia_nome IS NOT NULL
        AND res.preco_saida IS NOT NULL
    ORDER BY r.estrategia_nome, r.timestamp
    """

    cursor.execute(query)
    operacoes = cursor.fetchall()
    conn.close()

    if not operacoes:
        print("❌ Nenhuma operação encontrada no banco de dados.")
        return

    # Agrupar por estratégia
    estrategias = defaultdict(list)
    for op in operacoes:
        estrategias[op['estrategia_nome']].append(op)

    print("\n" + "=" * 100)
    print("COMPARACAO DE ESTRATEGIAS DE TRADING")
    print("=" * 100)

    resultados = []

    for nome_estrategia, ops in sorted(estrategias.items()):
        print(f"\nESTRATEGIA: {nome_estrategia}")
        print("-" * 100)

        total_ops = len(ops)
        compras = [op for op in ops if op['direcao'] == 'COMPRA']
        vendas = [op for op in ops if op['direcao'] == 'VENDA']

        acertos = sum(1 for op in ops if op['acertou'])
        taxa_acerto = (acertos / total_ops * 100) if total_ops > 0 else 0

        compras_acerto = sum(1 for op in compras if op['acertou'])
        taxa_compra = (compras_acerto / len(compras) * 100) if compras else 0

        vendas_acerto = sum(1 for op in vendas if op['acertou'])
        taxa_venda = (vendas_acerto / len(vendas) * 100) if vendas else 0

        # PnL
        pnl_total = sum(op['pnl_pontos'] for op in ops if op['pnl_pontos'])
        pnl_medio = pnl_total / total_ops if total_ops > 0 else 0

        ganhos = [op['pnl_pontos'] for op in ops if op['pnl_pontos'] and op['pnl_pontos'] > 0]
        perdas = [op['pnl_pontos'] for op in ops if op['pnl_pontos'] and op['pnl_pontos'] < 0]

        ganho_medio = sum(ganhos) / len(ganhos) if ganhos else 0
        perda_media = sum(perdas) / len(perdas) if perdas else 0

        # Payoff ratio
        payoff = abs(ganho_medio / perda_media) if perda_media != 0 else 0

        # Expectativa matemática
        prob_ganho = len(ganhos) / total_ops if total_ops > 0 else 0
        prob_perda = len(perdas) / total_ops if total_ops > 0 else 0
        expectativa = (prob_ganho * ganho_medio) + (prob_perda * perda_media)

        # Confiança média
        confianca_media = sum(op['confianca'] for op in ops) / total_ops if total_ops > 0 else 0

        print(f"  Total de operacoes: {total_ops}")
        print(f"  Direcao: {len(compras)} COMPRA | {len(vendas)} VENDA")
        print(f"  Taxa de acerto geral: {taxa_acerto:.1f}% ({acertos}/{total_ops})")
        print(f"     - COMPRA: {taxa_compra:.1f}% ({compras_acerto}/{len(compras)})")
        print(f"     - VENDA: {taxa_venda:.1f}% ({vendas_acerto}/{len(vendas)})")
        print(f"  PnL total: {pnl_total:+.0f} pontos")
        print(f"  PnL medio: {pnl_medio:+.1f} pontos")
        print(f"  Ganho medio: +{ganho_medio:.1f} pontos ({len(ganhos)} ops)")
        print(f"  Perda media: {perda_media:.1f} pontos ({len(perdas)} ops)")
        print(f"  Payoff ratio: {payoff:.2f}")
        print(f"  Expectativa: {expectativa:+.1f} pontos por operacao")
        print(f"  Confianca media: {confianca_media*100:.1f}%")

        resultados.append({
            'nome': nome_estrategia,
            'total_ops': total_ops,
            'taxa_acerto': taxa_acerto,
            'pnl_total': pnl_total,
            'expectativa': expectativa,
            'payoff': payoff
        })

    # Ranking
    print("\n" + "=" * 100)
    print("RANKING DE ESTRATEGIAS")
    print("=" * 100)

    # Por expectativa matemática
    print("\nPor Expectativa Matematica (pontos/operacao):")
    for i, est in enumerate(sorted(resultados, key=lambda x: x['expectativa'], reverse=True), 1):
        print(f"  {i}. {est['nome']}: {est['expectativa']:+.1f} pontos/op")

    # Por taxa de acerto
    print("\nPor Taxa de Acerto:")
    for i, est in enumerate(sorted(resultados, key=lambda x: x['taxa_acerto'], reverse=True), 1):
        print(f"  {i}. {est['nome']}: {est['taxa_acerto']:.1f}%")

    # Por PnL total
    print("\nPor PnL Total:")
    for i, est in enumerate(sorted(resultados, key=lambda x: x['pnl_total'], reverse=True), 1):
        print(f"  {i}. {est['nome']}: {est['pnl_total']:+.0f} pontos")

    # Por Payoff
    print("\nPor Payoff Ratio:")
    for i, est in enumerate(sorted(resultados, key=lambda x: x['payoff'], reverse=True), 1):
        print(f"  {i}. {est['nome']}: {est['payoff']:.2f}")

    print("\n" + "=" * 100)


if __name__ == '__main__':
    analisar_estrategias()
