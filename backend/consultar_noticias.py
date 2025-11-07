# -*- coding: utf-8 -*-
"""
CLI para consultar notícias coletadas automaticamente.

Uso:
    python consultar_noticias.py listar [--dias N]
    python consultar_noticias.py coletar [--newsapi-key KEY]
    python consultar_noticias.py analisar [--limite N]
    python consultar_noticias.py sentimento [--dias N]
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dados.coletor_noticias import ColetorNoticias
from dados.analisador_sentimento import AnalisadorSentimento


def listar_noticias(args):
    """Lista notícias recentes do banco."""
    coletor = ColetorNoticias()
    noticias = coletor.obter_noticias_recentes(horas=args.dias * 24, limite=args.limite)

    if not noticias:
        print("\n⚠️  Nenhuma notícia encontrada no período")
        return

    print(f"\n{'='*100}")
    print(f"NOTICIAS RECENTES (ultimos {args.dias} dias) - Total: {len(noticias)}")
    print(f"{'='*100}\n")

    # Agrupar por fonte
    por_fonte = {}
    for n in noticias:
        fonte = n['fonte']
        if fonte not in por_fonte:
            por_fonte[fonte] = []
        por_fonte[fonte].append(n)

    for fonte, lista in sorted(por_fonte.items()):
        print(f"\n📰 {fonte.upper()} ({len(lista)} notícias)")
        print(f"   {'-'*94}")

        for noticia in lista[:10]:  # Máximo 10 por fonte
            data = datetime.fromisoformat(noticia['data_publicacao'])
            titulo = noticia['titulo'][:70] + "..." if len(noticia['titulo']) > 70 else noticia['titulo']

            sentimento_icon = ""
            if noticia['sentimento']:
                if noticia['sentimento'] == 'positivo':
                    sentimento_icon = "📈"
                elif noticia['sentimento'] == 'negativo':
                    sentimento_icon = "📉"
                else:
                    sentimento_icon = "➡️"

            print(f"   {sentimento_icon} {titulo}")
            print(f"      {data.strftime('%d/%m/%Y %H:%M')} | {noticia['url'][:60]}...")

            if noticia['sentimento']:
                print(f"      Sentimento: {noticia['sentimento']} ({noticia['score_sentimento']:.2f}) | "
                      f"Relevância: {noticia['relevancia_trading']:.2f} | "
                      f"Impacto: {noticia['impacto_estimado']}")
            print()


def coletar_noticias(args):
    """Executa coleta automática de notícias."""
    coletor = ColetorNoticias()

    # Verificar se tem chave NewsAPI
    newsapi_key = args.newsapi_key
    if not newsapi_key:
        import os
        newsapi_key = os.environ.get('NEWSAPI_KEY')

    coletor.executar_coleta_automatica(newsapi_key=newsapi_key)


def analisar_sentimento(args):
    """Analisa sentimento de notícias pendentes."""
    analisador = AnalisadorSentimento()
    processadas = analisador.processar_noticias_pendentes(limite=args.limite)

    if processadas > 0:
        # Mostrar estatísticas
        agora = datetime.now()
        periodo_inicio = agora - timedelta(days=7)

        stats = analisador.obter_sentimento_periodo(periodo_inicio, agora)

        print(f"\n{'='*100}")
        print("SENTIMENTO DOS ULTIMOS 7 DIAS")
        print(f"{'='*100}")
        print(f"   Total de notícias: {stats['total']}")
        print(f"   Sentimento médio: {stats['sentimento_medio']:+.3f}")
        print(f"   Distribuição:")
        print(f"      📈 Positivas: {stats['distribuicao']['positivas']} "
              f"({stats['distribuicao']['positivas']/max(stats['total'],1)*100:.1f}%)")
        print(f"      📉 Negativas: {stats['distribuicao']['negativas']} "
              f"({stats['distribuicao']['negativas']/max(stats['total'],1)*100:.1f}%)")
        print(f"      ➡️  Neutras: {stats['distribuicao']['neutras']} "
              f"({stats['distribuicao']['neutras']/max(stats['total'],1)*100:.1f}%)")
        print(f"   Relevância média: {stats['relevancia_media']:.3f}")
        print(f"{'='*100}\n")


def mostrar_sentimento_periodo(args):
    """Mostra agregado de sentimento de um período."""
    analisador = AnalisadorSentimento()

    agora = datetime.now()
    inicio = agora - timedelta(days=args.dias)

    stats = analisador.obter_sentimento_periodo(inicio, agora)

    print(f"\n{'='*100}")
    print(f"SENTIMENTO DO PERIODO ({args.dias} dias)")
    print(f"{'='*100}")
    print(f"   Período: {inicio.strftime('%d/%m/%Y')} a {agora.strftime('%d/%m/%Y')}")
    print(f"   Total de notícias: {stats['total']}")

    if stats['total'] == 0:
        print("   ⚠️  Nenhuma notícia processada no período")
        print(f"{'='*100}\n")
        return

    # Score visual
    score = stats['sentimento_medio']
    barra_tam = 40
    pos = int((score + 1) / 2 * barra_tam)  # Converter -1..+1 para 0..40
    pos = max(0, min(barra_tam, pos))

    barra = ['─'] * barra_tam
    barra[pos] = '█'
    barra_str = ''.join(barra)

    print(f"\n   Sentimento médio: {score:+.3f}")
    print(f"   📉 Bearish {barra_str} Bullish 📈")
    print(f"        -1.0                  0.0                  +1.0")

    print(f"\n   Distribuição:")
    print(f"      📈 Positivas: {stats['distribuicao']['positivas']} "
          f"({stats['distribuicao']['positivas']/stats['total']*100:.1f}%)")
    print(f"      📉 Negativas: {stats['distribuicao']['negativas']} "
          f"({stats['distribuicao']['negativas']/stats['total']*100:.1f}%)")
    print(f"      ➡️  Neutras: {stats['distribuicao']['neutras']} "
          f"({stats['distribuicao']['neutras']/stats['total']*100:.1f}%)")

    print(f"\n   Relevância média: {stats['relevancia_media']:.3f}")

    # Interpretação
    print(f"\n   📊 Interpretação:")
    if abs(score) < 0.1:
        print("      Mercado NEUTRO - Sem viés claro nas notícias")
    elif score > 0.3:
        print("      Mercado OTIMISTA - Predomínio de notícias positivas")
    elif score < -0.3:
        print("      Mercado PESSIMISTA - Predomínio de notícias negativas")
    else:
        direção = "levemente otimista" if score > 0 else "levemente pessimista"
        print(f"      Mercado {direção.upper()} - Viés moderado")

    print(f"{'='*100}\n")


def main():
    parser = argparse.ArgumentParser(
        description="CLI para consultar e coletar notícias financeiras"
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponíveis')

    # Comando: listar
    parser_listar = subparsers.add_parser('listar', help='Listar notícias recentes')
    parser_listar.add_argument('--dias', type=int, default=1,
                               help='Número de dias (padrão: 1)')
    parser_listar.add_argument('--limite', type=int, default=100,
                               help='Número máximo de notícias (padrão: 100)')
    parser_listar.set_defaults(func=listar_noticias)

    # Comando: coletar
    parser_coletar = subparsers.add_parser('coletar', help='Coletar notícias automaticamente')
    parser_coletar.add_argument('--newsapi-key', type=str,
                                help='Chave de API do NewsAPI (opcional)')
    parser_coletar.set_defaults(func=coletar_noticias)

    # Comando: analisar
    parser_analisar = subparsers.add_parser('analisar', help='Analisar sentimento de notícias pendentes')
    parser_analisar.add_argument('--limite', type=int, default=100,
                                 help='Número máximo de notícias a processar (padrão: 100)')
    parser_analisar.set_defaults(func=analisar_sentimento)

    # Comando: sentimento
    parser_sentimento = subparsers.add_parser('sentimento', help='Mostrar sentimento agregado do período')
    parser_sentimento.add_argument('--dias', type=int, default=7,
                                   help='Número de dias (padrão: 7)')
    parser_sentimento.set_defaults(func=mostrar_sentimento_periodo)

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
