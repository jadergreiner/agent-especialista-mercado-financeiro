"""
Validador Automático de Recomendações

Executa validação automática das recomendações pendentes usando um provider
intraday (mock nesta versão). Registra resultados diretamente no SQLite.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple

from persistencia.recomendacoes import (
    inicializar_banco,
    listar_pendentes,
    registrar_resultado,
)


@dataclass
class Barra:
    t: datetime
    o: float
    h: float
    l: float
    c: float


class ProviderIntraday:
    """Interface simples para providers intraday"""

    def obter_barras(self, instrumento: str, inicio: datetime, fim: datetime, tf_min: int = 1) -> List[Barra]:
        raise NotImplementedError


class ProviderMock(ProviderIntraday):
    """Gera séries sintéticas realistas para validação offline"""

    def obter_barras(self, instrumento: str, inicio: datetime, fim: datetime, tf_min: int = 1) -> List[Barra]:
        n = max(1, int((fim - inicio).total_seconds() // (tf_min * 60)))
        # Preço base heurístico por instrumento
        base = 130_000.0 if instrumento.upper().startswith('WIN') else 100.0
        random.seed(int(inicio.timestamp()) % 10_000)
        barras: List[Barra] = []
        preco = base
        t = inicio
        for i in range(n):
            # Variação aleatória com algum drift e picos
            drift = random.uniform(-40, 40)
            vol = random.uniform(20, 80)
            delta = drift + random.choice([-1, 1]) * vol
            o = preco
            h = o + abs(delta) * random.uniform(0.3, 1.0)
            l = o - abs(delta) * random.uniform(0.3, 1.0)
            c = o + delta * random.uniform(0.4, 0.9)
            barras.append(Barra(t=t, o=o, h=max(h, l), l=min(h, l), c=c))
            preco = c
            t = t + timedelta(minutes=tf_min)
        return barras


def _parse_valido_ate(ts_iso: str, valido_ate_hhmm: str) -> datetime:
    base = datetime.fromisoformat(ts_iso)
    hh, mm = valido_ate_hhmm.split(':')
    return datetime.combine(base.date(), time(int(hh), int(mm)))


def _cruzou_nivel(bar: Barra, nivel: float, compra: bool) -> bool:
    # Para compra: cruzou se low <= nivel <= high
    # Para venda: idem (checagem simétrica)
    return (bar.l <= nivel <= bar.h)


def _ordem_eventos(direcao: str, stop: float, tps: List[float]) -> List[Tuple[str, float]]:
    # Define prioridade de checagem dos níveis após execução
    # Sempre vence o primeiro nível tocado no tempo
    eventos = [('stop', stop)]
    if direcao == 'COMPRA':
        if tps:
            eventos.extend([(f'tp{i+1}', p) for i, p in enumerate(sorted(tps))])
    elif direcao == 'VENDA':
        if tps:
            eventos.extend([(f'tp{i+1}', p) for i, p in enumerate(sorted(tps, reverse=True))])
    return eventos


def validar_recomendacao(rec: Dict[str, any], provider: Optional[ProviderIntraday] = None) -> Dict[str, any]:
    """Valida uma recomendação individual e retorna dict com resultado"""
    provider = provider or ProviderMock()

    if rec['direcao'] == 'AGUARDAR' or rec['preco_entrada'] == 0:
        return {
            'status': 'expirada',
            'acertou': None,
            'motivo': 'tempo',
            'pnl_pontos': 0.0,
            'pnl_reais': 0.0,
        }

    inicio = datetime.fromisoformat(rec['timestamp'])
    fim = _parse_valido_ate(rec['timestamp'], rec['valido_ate'])
    barras = provider.obter_barras(rec['instrumento'], inicio, fim, tf_min=1)

    entrada = float(rec['preco_entrada'])
    stop = float(rec['stop_loss'])
    tps = [float(rec['tp1']), float(rec['tp2']), float(rec['tp3'])]
    tps = [x for x in tps if x > 0]

    # 1) Execução: precisa tocar o preço de entrada
    t_exec = None
    for b in barras:
        if _cruzou_nivel(b, entrada, compra=(rec['direcao'] == 'COMPRA')):
            t_exec = b.t
            break
    if t_exec is None:
        return {
            'status': 'expirada',
            'acertou': None,
            'motivo': 'tempo',
            'pnl_pontos': 0.0,
            'pnl_reais': 0.0,
        }

    # 2) Após execução: primeiro nível tocado vence
    pos = 0.0
    eventos = _ordem_eventos(rec['direcao'], stop, tps)
    for b in (x for x in barras if x.t >= t_exec):
        for nome, nivel in eventos:
            if _cruzou_nivel(b, nivel, compra=(rec['direcao'] == 'COMPRA')):
                acertou = (nome != 'stop')
                preco_saida = nivel
                pontos = (preco_saida - entrada) if rec['direcao'] == 'COMPRA' else (entrada - preco_saida)
                pnl_reais = pontos * 0.20 * (rec.get('contratos_inicio') or 1)
                return {
                    'status': 'executada',
                    'acertou': acertou,
                    'motivo': nome,
                    'preco_saida': round(preco_saida, 2),
                    'pnl_pontos': round(pontos, 2),
                    'pnl_reais': round(pnl_reais, 2),
                }

    # 3) Se não tocou nada depois da execução, considerar expirada por tempo
    return {
        'status': 'expirada',
        'acertou': None,
        'motivo': 'tempo',
        'pnl_pontos': 0.0,
        'pnl_reais': 0.0,
    }


def validar_pendentes(provider: Optional[ProviderIntraday] = None) -> List[int]:
    """Valida todas as recomendações pendentes e registra resultados"""
    inicializar_banco()
    pendentes = listar_pendentes()
    if not pendentes:
        print("\n✅ Nenhuma pendência para validar.")
        return []

    ids: List[int] = []
    for rec in pendentes:
        res = validar_recomendacao(rec, provider)
        registrar_resultado(
            id_recomendacao=rec['id'],
            status=res['status'],
            acertou=res.get('acertou'),
            preco_saida=res.get('preco_saida'),
            pnl_pontos=res.get('pnl_pontos'),
            pnl_reais=res.get('pnl_reais'),
            motivo_saida=res.get('motivo'),
            observacoes='automático(mock)'
        )
        print(f"- id={rec['id']} → {res['status']} | motivo={res['motivo']} | pnl=R$ {res.get('pnl_reais',0):.2f}")
        ids.append(rec['id'])
    return ids
