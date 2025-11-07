# -*- coding: utf-8 -*-
"""
Emissor de sinais a partir de relatórios (Forex/Cripto)

Converte payloads de relatório em eventos:
- signal.tech.v1
- signal.macroflow.v1

Opcionalmente escreve os eventos em um diretório 'bus' para consumo por outros componentes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from schemas.validador import validar_contra_schema


def _iso(dt: str | datetime) -> str:
    if isinstance(dt, datetime):
        return dt.isoformat(timespec='seconds')
    return dt


def _instrumento_from_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    if payload.get('classeAtivo') == 'forex':
        return {
            'id': payload.get('par', ''),
            'par': payload.get('par', ''),
            'tickerYahoo': payload.get('tickerYahoo') or payload.get('ticker_yahoo')
        }
    else:
        return {
            'id': payload.get('ativo', ''),
            'tickerYahoo': payload.get('tickerYahoo')
        }


def signals_from_forex_report(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    eventos: List[Dict[str, Any]] = []
    ts = payload.get('timestamp')
    instr = _instrumento_from_report(payload)

    # Macro/Flow
    macro = {
        'contractVersion': 'signal.macroflow.v1',
        'classeAtivo': 'forex',
        'instrumento': instr,
        'timestamp': _iso(ts),
        'sinal': {
            'viesSessao': payload.get('resumo', {}).get('viesSessao') or payload.get('resumo', {}).get('vies') or '-',
            'dxyVariacao': payload.get('analises', {}).get('dxyVariacao'),
            'eventosCriticos': payload.get('analises', {}).get('eventos', [])
        }
    }
    eventos.append(macro)

    # Técnicos: tendência 15m
    tendencia = payload.get('analises', {}).get('tecnica', {}).get('tendencia15m')
    if tendencia:
        eventos.append({
            'contractVersion': 'signal.tech.v1',
            'classeAtivo': 'forex',
            'instrumento': instr,
            'timestamp': _iso(ts),
            'timeframe': '15m',
            'sinal': {
                'tipo': 'tendencia',
                'valor': tendencia,
                'confianca': None,
                'detalhes': None
            }
        })

    # Técnicos: flow e vol
    fluxo = payload.get('analises', {}).get('fluxoVol', {}).get('fluxoInstitucional')
    if fluxo:
        eventos.append({
            'contractVersion': 'signal.tech.v1',
            'classeAtivo': 'forex',
            'instrumento': instr,
            'timestamp': _iso(ts),
            'timeframe': '5m',
            'sinal': {
                'tipo': 'flow_heuristico',
                'valor': fluxo,
                'confianca': None,
                'detalhes': None
            }
        })

    vol = payload.get('analises', {}).get('fluxoVol', {}).get('volRealizada')
    if vol:
        eventos.append({
            'contractVersion': 'signal.tech.v1',
            'classeAtivo': 'forex',
            'instrumento': instr,
            'timestamp': _iso(ts),
            'timeframe': '15m',
            'sinal': {
                'tipo': 'vol_realizada',
                'valor': vol,
                'confianca': None,
                'detalhes': None
            }
        })

    # Setup: VWAP pullback + rejeição em SRI (heurístico intraday)
    try:
        setup_ev = _detectar_setup_vwap_pullback_reject(payload)
        if setup_ev is not None:
            eventos.append({
                'contractVersion': 'setup.v1',
                'classeAtivo': 'forex',
                'instrumento': instr,
                'timestamp': _iso(ts),
                'timeframe': '15m',
                'setup': setup_ev
            })
    except Exception:
        # heurística opcional: falhas não devem quebrar emissão dos demais eventos
        pass

    return eventos


def signals_from_cripto_report(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    eventos: List[Dict[str, Any]] = []
    ts = payload.get('timestamp')
    instr = _instrumento_from_report(payload)

    # Técnicos: momentum técnico como tendência diária
    tendencia = payload.get('analises', {}).get('tecnica', {}).get('momentum')
    if tendencia:
        eventos.append({
            'contractVersion': 'signal.tech.v1',
            'classeAtivo': 'cripto',
            'instrumento': instr,
            'timestamp': _iso(ts),
            'timeframe': '1d',
            'sinal': {
                'tipo': 'tendencia',
                'valor': tendencia,
                'confianca': None,
                'detalhes': None
            }
        })

    # Técnicos: proximidade de SRs (derivado de suportes/resistências)
    try:
        preco = float(payload.get('precoAtual', 0))
        srs = payload.get('analises', {}).get('tecnica', {})
        sup = srs.get('suportes') or []
        res = srs.get('resistencias') or []
        def _prox(lista: List[float]) -> Optional[float]:
            if not lista:
                return None
            return float(sorted(lista, key=lambda x: abs(float(x) - preco))[0])
        alvo = _prox(sup + res)
        if alvo is not None:
            eventos.append({
                'contractVersion': 'signal.tech.v1',
                'classeAtivo': 'cripto',
                'instrumento': instr,
                'timestamp': _iso(ts),
                'timeframe': '1d',
                'sinal': {
                    'tipo': 'sri_proximidade',
                    'valor': abs(preco - alvo),
                    'confianca': None,
                    'detalhes': { 'alvo': alvo }
                }
            })
    except Exception:
        pass

    return eventos


def escrever_eventos(eventos: List[Dict[str, Any]], pasta_bus: Path) -> List[Path]:
    """Escreve eventos em arquivos JSON na pasta do bus e valida cada um."""
    pasta_bus.mkdir(parents=True, exist_ok=True)
    caminhos: List[Path] = []
    for idx, ev in enumerate(eventos):
        contrato = ev.get('contractVersion', 'event')
        ts = ev.get('timestamp')
        # sufixo para diferenciar múltiplos eventos no mesmo timestamp
        tipo = None
        try:
            tipo = ev.get('sinal', {}).get('tipo')
        except Exception:
            tipo = None
        if not tipo:
            # tenta usar tipo de setup se for um evento de setup
            try:
                tipo = ev.get('setup', {}).get('tipo')
            except Exception:
                tipo = None
        suf = (tipo or 'macroflow' or f"{idx}")
        suf = str(suf).replace(' ', '-').lower()
        nome = f"{contrato}_{ts.replace(':','').replace('-','').replace('T','_')}_{suf}.json"
        caminho = pasta_bus / nome
        ok, erros = validar_contra_schema(ev, contrato)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump({ 'valid': ok, 'errors': erros, 'event': ev }, f, ensure_ascii=False, indent=2)
        caminhos.append(caminho)
    return caminhos


# ========================= HEURÍSTICAS DE SETUP =========================
def _detectar_setup_vwap_pullback_reject(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Detecta um setup simples de pullback na VWAP com rejeição em SRI.

    Critérios (heurístico):
    - Direção: COMPRA quando tendência 15m = ALTISTA; VENDA quando = BAIXISTA
    - Preço atual próximo da VWAP da sessão (Londres/NY) ou VWAP geral
    - Presença de SRI no lado correto a uma curta distância relativa do preço
    - Fluxo institucional alinhado ou neutro

    Retorna dicionário conforme contrato setup.v1 ou None se não configurado.
    """
    from math import isfinite

    analises = payload.get('analises', {})
    tecnica = analises.get('tecnica', {})
    fluxo_vol = analises.get('fluxoVol', {})
    resumo = payload.get('resumo', {})

    preco = payload.get('precoAtual')
    if preco is None:
        return None
    try:
        preco = float(preco)
    except Exception:
        return None

    tendencia = tecnica.get('tendencia15m')
    vwap_geral = tecnica.get('vwap')
    vwap_sessoes = tecnica.get('vwapSessoes', {}) or {}
    # prefere Londres, depois NY; se indisponíveis, usa VWAP geral
    vwap_sess = vwap_sessoes.get('londres') or vwap_sessoes.get('ny') or vwap_geral
    if vwap_sess is None:
        return None
    try:
        vwap_sess = float(vwap_sess)
    except Exception:
        return None

    sris = tecnica.get('sris', {})
    suportes = [float(x) for x in (sris.get('suportes') or []) if _is_num(x)]
    resistencias = [float(x) for x in (sris.get('resistencias') or []) if _is_num(x)]

    fluxo = fluxo_vol.get('fluxoInstitucional')

    # tolerâncias relativas (aprox. 2–5 pips para majors)
    tol_vwap = 0.00025  # ~0.025%
    tol_sri = 0.00050   # ~0.050%

    def rel(a: float, b: float) -> float:
        base = abs(preco) if abs(preco) > 0 else 1.0
        return abs(a - b) / base

    dist_vwap = rel(preco, vwap_sess)

    # Parse R/R esperado (ex.: "1:1.8")
    rr_txt = (resumo.get('rr') or '').strip()
    rr_esperado = None
    try:
        if ':' in rr_txt:
            rr_esperado = float(rr_txt.split(':', 1)[1])
    except Exception:
        rr_esperado = None

    # Direção sugerida pelo contexto (opcional)
    direcao_sugerida = resumo.get('operacao') if resumo.get('operacao') in ('COMPRA', 'VENDA') else None

    # COMPRA: tendência ALTISTA, preço próximo/acima da VWAP, suporte próximo abaixo
    if tendencia == 'ALTISTA':
        prox_sup = _mais_proximo_abaixo(preco, suportes)
        dist_sup = rel(preco, prox_sup) if prox_sup is not None else None
        cond_vwap = (preco >= vwap_sess) and (dist_vwap <= tol_vwap)
        cond_sri = (dist_sup is not None) and (dist_sup <= tol_sri)
        cond_fluxo = fluxo in ('COMPRA', 'NEUTRO', None)
        if cond_vwap and cond_sri and cond_fluxo:
            return {
                'tipo': 'vwap_pullback_reject',
                'direcao': 'COMPRA',
                'score': _score_setup(dist_vwap, dist_sup, rr_esperado, bonus_fluxo=(fluxo == 'COMPRA')),
                'criterios': {
                    'distanciaVWAP': dist_vwap,
                    'distanciaSRI': dist_sup,
                    'sri': prox_sup,
                    'tendencia15m': tendencia,
                    'fluxo': fluxo,
                    'rrEsperado': rr_esperado
                }
            }

    # VENDA: tendência BAIXISTA, preço próximo/abaixo da VWAP, resistência próxima acima
    if tendencia == 'BAIXISTA':
        prox_res = _mais_proximo_acima(preco, resistencias)
        dist_res = rel(preco, prox_res) if prox_res is not None else None
        cond_vwap = (preco <= vwap_sess) and (dist_vwap <= tol_vwap)
        cond_sri = (dist_res is not None) and (dist_res <= tol_sri)
        cond_fluxo = fluxo in ('VENDA', 'NEUTRO', None)
        if cond_vwap and cond_sri and cond_fluxo:
            return {
                'tipo': 'vwap_pullback_reject',
                'direcao': 'VENDA',
                'score': _score_setup(dist_vwap, dist_res, rr_esperado, bonus_fluxo=(fluxo == 'VENDA')),
                'criterios': {
                    'distanciaVWAP': dist_vwap,
                    'distanciaSRI': dist_res,
                    'sri': prox_res,
                    'tendencia15m': tendencia,
                    'fluxo': fluxo,
                    'rrEsperado': rr_esperado
                }
            }

    # Sem setup
    return None


def _is_num(x: Any) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def _mais_proximo_abaixo(preco: float, niveis: List[float]) -> Optional[float]:
    candidatos = [n for n in niveis if n <= preco]
    if not candidatos:
        return None
    return max(candidatos)


def _mais_proximo_acima(preco: float, niveis: List[float]) -> Optional[float]:
    candidatos = [n for n in niveis if n >= preco]
    if not candidatos:
        return None
    return min(candidatos)


def _score_setup(dist_vwap: Optional[float], dist_sri: Optional[float], rr: Optional[float], bonus_fluxo: bool = False) -> float:
    """Pontuação simples: menor distância → melhor, maior R/R → melhor.
    Score em faixa ~0..1.5 (heurístico), com bônus se fluxo alinhado.
    """
    s = 0.0
    if dist_vwap is not None:
        s += max(0.0, 0.5 - 2.0 * float(dist_vwap))  # até 0.5
    if dist_sri is not None:
        s += max(0.0, 0.5 - 1.5 * float(dist_sri))   # até 0.5
    if rr is not None:
        s += min(0.4, 0.1 * float(rr))               # até 0.4
    if bonus_fluxo:
        s += 0.1
    return round(s, 3)
