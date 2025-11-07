# -*- coding: utf-8 -*-
"""
Script para consulta e visualização de dados dos boletins B3.
"""

import sqlite3
from pathlib import Path
from datetime import date, timedelta


def consultar_boletins(simbolo: str = "WIN", dias: int = 5):
    """Exibe boletins dos últimos N dias."""

    db_path = Path(__file__).parent / "data" / "recomendacoes.sqlite"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=dias)

    cur.execute("""
        SELECT
            data_pregao,
            simbolo,
            DATE(vencimento) as vencimento,
            abertura,
            maxima,
            minima,
            fechamento,
            ajuste_diario,
            variacao_pontos,
            variacao_percentual,
            volume_contratos,
            volume_financeiro,
            numero_negocios,
            contratos_abertos,
            spread_bid_ask
        FROM boletins_diarios
        WHERE simbolo = ?
          AND data_pregao >= ?
        ORDER BY data_pregao DESC
        LIMIT 20
    """, (simbolo, data_inicio.isoformat()))

    resultados = cur.fetchall()
    conn.close()

    if not resultados:
        print(f"\nℹ️  Nenhum boletim encontrado para {simbolo}")
        print(f"   Período: {data_inicio} até {data_fim}")
        print(f"\n💡 Adicione boletins manualmente em: backend/data/boletins_b3/raw/")
        return

    print(f"\n📊 BOLETINS B3 - {simbolo}")
    print("=" * 120)
    print(f"{'Data':<12} {'Venc':<12} {'Abertura':>10} {'Máxima':>10} {'Mínima':>10} "
          f"{'Fecham.':>10} {'Ajuste':>10} {'Var.':>8} {'Volume':>10} {'OI':>10} {'Spread':>8}")
    print("-" * 120)

    for row in resultados:
        data_pregao = row['data_pregao']
        vencimento = row['vencimento']
        abertura = row['abertura']
        maxima = row['maxima']
        minima = row['minima']
        fechamento = row['fechamento']
        ajuste = row['ajuste_diario']
        var_pts = row['variacao_pontos']
        volume = row['volume_contratos']
        oi = row['contratos_abertos']
        spread = row['spread_bid_ask'] if row['spread_bid_ask'] else 0

        # Formatação com cores (sinal de variação)
        var_sinal = "+" if var_pts >= 0 else ""

        print(f"{data_pregao:<12} {vencimento:<12} "
              f"{abertura:>10.0f} {maxima:>10.0f} {minima:>10.0f} "
              f"{fechamento:>10.0f} {ajuste:>10.0f} "
              f"{var_sinal}{var_pts:>7.0f} {volume:>10,} {oi:>10,} {spread:>8.1f}")

    # Estatísticas do período
    print("-" * 120)

    volumes = [r['volume_contratos'] for r in resultados]
    ois = [r['contratos_abertos'] for r in resultados]

    print(f"\n📈 Estatísticas do Período:")
    print(f"   Total de pregões: {len(resultados)}")
    print(f"   Volume médio: {sum(volumes) / len(volumes):,.0f} contratos/dia")
    print(f"   OI médio: {sum(ois) / len(ois):,.0f} contratos")
    print(f"   OI mínimo: {min(ois):,} | OI máximo: {max(ois):,}")

    # Variação de OI
    if len(ois) >= 2:
        variacao_oi = ((ois[0] - ois[-1]) / ois[-1]) * 100
        print(f"   Variação OI no período: {variacao_oi:+.2f}%")


def listar_simbolos_disponiveis():
    """Lista todos os símbolos com boletins no banco."""

    db_path = Path(__file__).parent / "data" / "recomendacoes.sqlite"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            simbolo,
            COUNT(*) as total_boletins,
            MIN(data_pregao) as primeiro_pregao,
            MAX(data_pregao) as ultimo_pregao
        FROM boletins_diarios
        GROUP BY simbolo
        ORDER BY ultimo_pregao DESC
    """)

    resultados = cur.fetchall()
    conn.close()

    if not resultados:
        print("\nℹ️  Nenhum boletim encontrado no banco de dados.")
        print("   Importe boletins usando: python src/dados/boletim_b3.py")
        return

    print("\n📋 SÍMBOLOS DISPONÍVEIS:")
    print("=" * 80)
    print(f"{'Símbolo':<10} {'Total':<10} {'Primeiro Pregão':<20} {'Último Pregão':<20}")
    print("-" * 80)

    for row in resultados:
        simbolo, total, primeiro, ultimo = row
        print(f"{simbolo:<10} {total:<10} {primeiro:<20} {ultimo:<20}")

    print("-" * 80)


def verificar_qualidade_dados(simbolo: str = "WIN", dias: int = 30):
    """Verifica integridade e qualidade dos dados importados."""

    db_path = Path(__file__).parent / "data" / "recomendacoes.sqlite"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=dias)

    # Verificar gaps na série temporal
    cur.execute("""
        SELECT data_pregao FROM boletins_diarios
        WHERE simbolo = ? AND data_pregao >= ?
        ORDER BY data_pregao
    """, (simbolo, data_inicio.isoformat()))

    datas = [date.fromisoformat(row['data_pregao']) for row in cur.fetchall()]

    if not datas:
        print(f"\n⚠️  Nenhum dado encontrado para {simbolo}")
        return

    print(f"\n🔍 VERIFICAÇÃO DE QUALIDADE - {simbolo}")
    print("=" * 80)

    # Detectar gaps (dias úteis faltantes)
    gaps = []
    for i in range(len(datas) - 1):
        delta = (datas[i+1] - datas[i]).days
        if delta > 3:  # Mais de 3 dias (pode indicar gap além de fim de semana)
            gaps.append((datas[i], datas[i+1], delta))

    if gaps:
        print(f"\n⚠️  Gaps detectados na série temporal:")
        for data1, data2, delta in gaps:
            print(f"   {data1} → {data2} ({delta} dias)")
    else:
        print("\n✅ Série temporal contínua (sem gaps)")

    # Verificar campos nulos
    cur.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN spread_bid_ask IS NULL THEN 1 ELSE 0 END) as sem_spread,
            SUM(CASE WHEN posicao_pessoa_fisica IS NULL THEN 1 ELSE 0 END) as sem_posicoes
        FROM boletins_diarios
        WHERE simbolo = ? AND data_pregao >= ?
    """, (simbolo, data_inicio.isoformat()))

    row = cur.fetchone()
    total = row['total']
    sem_spread = row['sem_spread']
    sem_posicoes = row['sem_posicoes']

    print(f"\n📊 Completude dos Dados ({total} pregões):")
    print(f"   Spread bid/ask: {((total - sem_spread) / total * 100):.1f}% completo")
    print(f"   Posicionamento: {((total - sem_posicoes) / total * 100):.1f}% completo")

    # Verificar outliers em volume
    cur.execute("""
        SELECT
            AVG(volume_contratos) as media_volume,
            MIN(volume_contratos) as min_volume,
            MAX(volume_contratos) as max_volume
        FROM boletins_diarios
        WHERE simbolo = ? AND data_pregao >= ?
    """, (simbolo, data_inicio.isoformat()))

    row = cur.fetchone()
    media = row['media_volume']
    minimo = row['min_volume']
    maximo = row['max_volume']

    print(f"\n📈 Análise de Volume:")
    print(f"   Média: {media:,.0f} contratos")
    print(f"   Mínimo: {minimo:,} ({(minimo/media*100):.1f}% da média)")
    print(f"   Máximo: {maximo:,} ({(maximo/media*100):.1f}% da média)")

    if minimo < media * 0.3:
        print(f"   ⚠️  Dia de volume muito baixo detectado (< 30% da média)")

    if maximo > media * 3:
        print(f"   ⚠️  Dia de volume muito alto detectado (> 300% da média)")

    conn.close()
    print("=" * 80)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        comando = sys.argv[1]

        if comando == "listar":
            listar_simbolos_disponiveis()

        elif comando == "verificar":
            simbolo = sys.argv[2] if len(sys.argv) > 2 else "WIN"
            dias = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            verificar_qualidade_dados(simbolo, dias)

        elif comando == "consultar":
            simbolo = sys.argv[2] if len(sys.argv) > 2 else "WIN"
            dias = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            consultar_boletins(simbolo, dias)

        else:
            print("Comandos disponíveis:")
            print("  python consultar_boletins.py listar")
            print("  python consultar_boletins.py consultar [SIMBOLO] [DIAS]")
            print("  python consultar_boletins.py verificar [SIMBOLO] [DIAS]")

    else:
        # Modo padrão: consulta WIN dos últimos 5 dias
        consultar_boletins("WIN", 5)
