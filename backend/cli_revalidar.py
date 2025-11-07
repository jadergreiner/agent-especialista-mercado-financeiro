#!/usr/bin/env python3
"""
CLI para revalidação de relatórios intraday após 24h.

Uso:
    python cli_revalidar.py --dry-run         # Lista relatórios pendentes sem revalidar
    python cli_revalidar.py                   # Executa revalidação completa
    python cli_revalidar.py --limite 50       # Revalida até 50 relatórios
    python cli_revalidar.py --horas 48        # Revalida relatórios com 48h ou mais
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from persistencia.sqlite_repo import (
    inicializar,
    listar_relatorios_pendentes_revalidacao,
    salvar_revalidacao
)
from utils.dados_manuais import carregar_ohlcv_csv


def buscar_preco_24h_cripto(simbolo: str, timestamp_24h: datetime) -> Optional[float]:
    """Busca preço de cripto 24h após análise original.

    Args:
        simbolo: Par cripto (ex: BTCUSDT, VIRTUALUSDT)
        timestamp_24h: Data/hora da revalidação (24h após original)

    Returns:
        Preço de fechamento mais próximo do timestamp ou None se não encontrado
    """
    # Tenta carregar CSV manual
    csv_path = Path(__file__).parent / 'data' / 'manual' / 'CRIPTO' / f'{simbolo}.csv'
    if not csv_path.exists():
        print(f"  ⚠️  CSV manual não encontrado: {csv_path}")
        return None

    try:
        df = carregar_ohlcv_csv(csv_path)

        # Encontra candle mais próximo do timestamp_24h
        # Converte timestamp_24h para o timezone do DataFrame (se houver)
        if df.index.tz is not None:
            if timestamp_24h.tzinfo is None:
                timestamp_24h = timestamp_24h.replace(tzinfo=timezone.utc)
            timestamp_24h = timestamp_24h.astimezone(df.index.tz)
        else:
            # Remove timezone se DataFrame não tem
            if timestamp_24h.tzinfo is not None:
                timestamp_24h = timestamp_24h.replace(tzinfo=None)

        # Filtra dados até a data da revalidação
        df_ate_24h = df[df.index <= timestamp_24h]

        if df_ate_24h.empty:
            print(f"  ⚠️  Sem dados até {timestamp_24h.date()}")
            return None

        # Retorna preço de fechamento do candle mais recente
        preco = float(df_ate_24h.iloc[-1]['Close'])
        print(f"  ✓ Preço 24h encontrado: ${preco:.4f} (candle: {df_ate_24h.index[-1]})")
        return preco

    except Exception as e:
        print(f"  ❌ Erro ao buscar preço 24h: {e}")
        return None


def buscar_preco_24h_forex(par: str, timestamp_24h: datetime) -> Optional[float]:
    """Busca preço de forex 24h após análise original.

    Args:
        par: Par forex (ex: EURUSD, GBPUSD)
        timestamp_24h: Data/hora da revalidação (24h após original)

    Returns:
        Preço de fechamento mais próximo do timestamp ou None se não encontrado
    """
    # TODO: Implementar busca via yfinance ou CSV manual
    # Por enquanto retorna None
    print(f"  ⚠️  Busca de preço Forex não implementada ainda para {par}")
    return None


def calcular_assertividade(
    operacao: str,
    preco_entrada: float,
    preco_alvo1: float,
    preco_stop: float,
    preco_24h: float
) -> tuple[bool, Optional[float], Optional[float], Optional[str]]:
    """Calcula se a operação acertou a direção e métricas de movimento.

    Args:
        operacao: COMPRA|VENDA|ESPERAR
        preco_entrada: Preço de entrada sugerido
        preco_alvo1: Take profit 1
        preco_stop: Stop loss
        preco_24h: Preço real após 24h

    Returns:
        (acertou, pontos_movimento, pct_movimento, objetivo_atingido)
    """
    if operacao == 'ESPERAR':
        # Para ESPERAR, considera acerto se não houve movimento significativo
        pct_movimento = ((preco_24h - preco_entrada) / preco_entrada) * 100
        acertou = abs(pct_movimento) < 2.0  # Menos de 2% de movimento = acerto
        return (acertou, 0.0, pct_movimento, 'NENHUM')

    # Calcula movimento
    pontos_movimento = preco_24h - preco_entrada
    pct_movimento = (pontos_movimento / preco_entrada) * 100

    # Verifica acerto de direção
    if operacao == 'COMPRA':
        acertou = preco_24h > preco_entrada
        # Verifica objetivos
        if preco_24h >= preco_alvo1:
            objetivo = 'TP1'
        elif preco_24h <= preco_stop:
            objetivo = 'STOP'
        elif preco_24h > preco_entrada:
            objetivo = 'PARCIAL'
        else:
            objetivo = 'NENHUM'
    else:  # VENDA
        acertou = preco_24h < preco_entrada
        # Verifica objetivos
        if preco_24h <= preco_alvo1:
            objetivo = 'TP1'
        elif preco_24h >= preco_stop:
            objetivo = 'STOP'
        elif preco_24h < preco_entrada:
            objetivo = 'PARCIAL'
        else:
            objetivo = 'NENHUM'

    return (acertou, pontos_movimento, pct_movimento, objetivo)


def revalidar_relatorio(relatorio: dict, dry_run: bool = False) -> bool:
    """Revalida um relatório individual.

    Args:
        relatorio: Dict com dados do relatório pendente
        dry_run: Se True, apenas simula sem salvar

    Returns:
        True se revalidação foi bem-sucedida
    """
    rid = relatorio['id']
    classe = relatorio['classe_ativo']
    par = relatorio['par']
    ts_orig = relatorio['timestamp']
    operacao = relatorio['operacao']
    payload = relatorio['payload']

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Revalidando relatório #{rid}: {par} ({classe})")
    print(f"  Timestamp original: {ts_orig}")
    print(f"  Operação original: {operacao}")

    # Extrai preços do payload
    resumo = payload.get('resumo', {})
    preco_atual = resumo.get('precoAtual')
    entrada = resumo.get('entrada')
    alvo1 = resumo.get('alvo1')
    stop = resumo.get('stop')

    if not all([preco_atual, entrada, alvo1, stop]):
        print(f"  ❌ Preços incompletos no payload: preco_atual={preco_atual}, entrada={entrada}, alvo1={alvo1}, stop={stop}")
        return False

    # Calcula timestamp de revalidação (24h após original)
    ts_orig_dt = datetime.fromisoformat(ts_orig.replace('Z', '+00:00'))
    from datetime import timedelta
    ts_revalida_dt = ts_orig_dt + timedelta(hours=24)
    ts_revalida = ts_revalida_dt.isoformat()

    print(f"  Timestamp revalidação: {ts_revalida}")

    # Busca preço 24h conforme classe de ativo
    preco_24h = None
    if classe == 'cripto':
        preco_24h = buscar_preco_24h_cripto(par, ts_revalida_dt)
    elif classe == 'forex':
        preco_24h = buscar_preco_24h_forex(par, ts_revalida_dt)
    else:
        print(f"  ⚠️  Classe de ativo '{classe}' não suportada para revalidação")
        return False

    if preco_24h is None:
        print(f"  ❌ Não foi possível obter preço 24h para {par}")
        return False

    # Calcula assertividade
    acertou, pontos, pct, objetivo = calcular_assertividade(
        operacao, entrada, alvo1, stop, preco_24h
    )

    # Monta observações
    obs = f"Preço entrada: ${entrada:.4f} → Preço 24h: ${preco_24h:.4f} | Movimento: {pct:+.2f}% | Objetivo: {objetivo}"

    print(f"  📊 Assertividade:")
    print(f"     Acertou: {'✅ SIM' if acertou else '❌ NÃO'}")
    print(f"     Movimento: {pontos:+.6f} pontos ({pct:+.2f}%)")
    print(f"     Objetivo: {objetivo}")

    if dry_run:
        print(f"  [DRY-RUN] Não salvando no banco")
        return True

    # Salva revalidação no banco
    rev_id = salvar_revalidacao(
        relatorio_id=rid,
        classe_ativo=classe,
        par=par,
        timestamp_original=ts_orig,
        timestamp_revalidacao=ts_revalida,
        operacao_original=operacao,
        preco_entrada_original=entrada,
        preco_alvo1=alvo1,
        preco_stop=stop,
        preco_24h=preco_24h,
        acertou=acertou,
        pontos_movimento=pontos,
        pct_movimento=pct,
        objetivo_atingido=objetivo,
        observacoes=obs
    )

    if rev_id:
        print(f"  ✅ Revalidação salva no banco (id={rev_id})")
        return True
    else:
        print(f"  ❌ Erro ao salvar revalidação no banco")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Revalida relatórios intraday após 24h para calcular assertividade',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python cli_revalidar.py --dry-run           # Lista pendentes sem revalidar
  python cli_revalidar.py                     # Revalida todos pendentes
  python cli_revalidar.py --limite 10         # Revalida até 10 relatórios
  python cli_revalidar.py --horas 48          # Revalida com 48h ou mais
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Lista relatórios pendentes sem executar revalidação'
    )
    parser.add_argument(
        '--limite',
        type=int,
        default=None,
        help='Número máximo de relatórios a revalidar (padrão: sem limite)'
    )
    parser.add_argument(
        '--horas',
        type=int,
        default=24,
        help='Número de horas após análise original para revalidar (padrão: 24)'
    )

    args = parser.parse_args()

    # Inicializa banco
    print("🔧 Inicializando banco de dados...")
    inicializar()

    # Lista relatórios pendentes
    print(f"\n🔍 Buscando relatórios pendentes (>= {args.horas}h)...")
    pendentes = listar_relatorios_pendentes_revalidacao(limite_horas=args.horas)

    if not pendentes:
        print("\n✅ Nenhum relatório pendente de revalidação")
        return

    print(f"\n📋 Encontrados {len(pendentes)} relatório(s) pendente(s)")

    # Aplica limite se especificado
    if args.limite:
        pendentes = pendentes[:args.limite]
        print(f"   (limitando a {args.limite} primeiro(s))")

    if args.dry_run:
        print("\n[DRY-RUN] Listando relatórios que seriam revalidados:")
        for rel in pendentes:
            print(f"  - #{rel['id']}: {rel['par']} ({rel['classe_ativo']}) | {rel['timestamp']} | {rel['operacao']}")
        print(f"\n[DRY-RUN] Total: {len(pendentes)} relatório(s)")
        print("Execute sem --dry-run para revalidar")
        return

    # Executa revalidação
    print("\n🚀 Iniciando revalidação...")
    sucesso = 0
    falha = 0

    for rel in pendentes:
        if revalidar_relatorio(rel, dry_run=False):
            sucesso += 1
        else:
            falha += 1

    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DA REVALIDAÇÃO")
    print("="*60)
    print(f"✅ Sucesso: {sucesso}")
    print(f"❌ Falha:   {falha}")
    print(f"📋 Total:   {len(pendentes)}")
    print("="*60)


if __name__ == '__main__':
    main()
