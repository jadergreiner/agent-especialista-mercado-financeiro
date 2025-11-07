# -*- coding: utf-8 -*-
"""
Relatório de Trading Intraday - Forex (4–8 horas)
Análise Integrada: Eventos Macro (AF Imediata) + Técnica (5m/15m/60m) + Fluxo/Volatilidade

Observações Importantes:
- Calendário Econômico e COT: placeholders/mock. Integrações futuras via APIs (Investing.com, ForexFactory, CME/CFTC)
- VWAP: Yahoo Finance não entrega volume confiável para forex; usamos VWAP proxy (média acumulada do preço típico)
- SRIs (Suportes/Resistências Institucionais): pivôs recentes em 60m

Autor: Agent Especialista Mercado Financeiro
Data: 2025-11-06
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import pandas as pd
import numpy as np
import yfinance as yf
from .indicadores_macro import obter_dxy_resiliente
from .calendario_macro import eventos_do_dia


@dataclass
class RelatorioIntradayForex:
    # Identificação
    par: str
    ticker_yahoo: str
    preco_atual: Decimal
    timestamp: datetime

    # Parte 1 (Resumo)
    operacao: str  # COMPRA | VENDA | ESPERAR
    vies_sessao: str  # Dólar forte/fraco, Risco-On/Off
    rr_texto: str  # 1:1.8 etc

    # Parte 2A (Eventos Macro e Sentimento)
    eventos_criticos: List[str]
    dxy_variacao: Decimal
    forca_moeda_base: str
    forca_moeda_contra: str

    # Parte 2B (AT 5m/15m/60m)
    vwap: Optional[Decimal]
    range_dia: Dict[str, Decimal]  # max, min, amplitude_pct
    sris_suportes: List[Decimal]
    sris_resistencias: List[Decimal]
    invalicacao_intraday: Decimal
    tendencia_15m: str  # ALTISTA/NEUTRO/BAIXISTA

    # Parte 2C (Fluxo e Vol)
    fluxo_institucional: str  # COMPRA/VENDA/NEUTRO (heurístico)
    vol_realizada: str  # ALTA/MEDIA/BAIXA
    cot_curto_prazo: str  # LONG/SHORT/NEUTRO (mock)

    # Plano 4–8h
    preco_entrada: Decimal
    alvo_1: Decimal
    alvo_2: Decimal
    stop_loss: Decimal
    just_entrada: str
    just_alvos: str
    just_stop: str
    # Qualidade das fontes (devem vir no final para respeitar ordem do dataclass)
    dxy_qualidade: Optional[str] = None  # 'ok' | 'fallback' | 'indisponivel'
    calendario_qualidade: Optional[str] = None  # 'ok' | 'mock'


class AnalisadorIntradayForex:
    def __init__(self) -> None:
        self.mapa_ticker = self._criar_mapa_tickers()

    @staticmethod
    def _to_decimal_safe(value, default: str = '0') -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            try:
                v = float(value)
                if np.isfinite(v):
                    return Decimal(str(v))
            except Exception:
                pass
            return Decimal(default)

    def _criar_mapa_tickers(self) -> Dict[str, str]:
        pares = [
            'EURUSD','GBPUSD','USDJPY','USDCHF','USDCAD','AUDUSD','NZDUSD',
            'EURJPY','EURGBP','GBPJPY'
        ]
        return {p: f"{p}=X" for p in pares}

    # ========================= COLETA DADOS =========================
    def _obter_series(self, ticker: str):
        # 5m de hoje
        df_5m = yf.download(tickers=ticker, period='1d', interval='5m', auto_adjust=False, progress=False)
        # 15m últimos 5 dias
        df_15m = yf.download(tickers=ticker, period='5d', interval='15m', auto_adjust=False, progress=False)
        # 60m últimos 10 dias
        df_60m = yf.download(tickers=ticker, period='10d', interval='60m', auto_adjust=False, progress=False)
        return df_5m, df_15m, df_60m

    def _obter_dxy(self):
        # Migrado para função resiliente com fallback
        variacao, qualidade = obter_dxy_resiliente()
        return variacao, qualidade

    # ========================= AF IMEDIATA =========================
    def _eventos_macro_do_dia(self, par: str) -> Tuple[List[str], str]:
        # Chama calendário com cache/local e retorna qualidade
        return eventos_do_dia(par)

    def _avaliar_vies_sessao(self, par: str, dxy_var: Decimal) -> Dict[str, str]:
        base, contra = par[:3], par[3:]
        # DXY em alta => USD forte; em baixa => USD fraco
        if abs(dxy_var) < Decimal('0.0015'):
            dolar = 'Dólar estável'
        elif dxy_var > 0:
            dolar = 'Dólar forte'
        else:
            dolar = 'Dólar fraco'

        # Viés risk-on/off (proxy pelo DXY): DXY alto → risk-off; baixo → risk-on
        vies = 'Risco-Off' if dxy_var > Decimal('0') else 'Risco-On'
        return {'dolar': dolar, 'vies': vies}

    # ========================= AT INTRADAY =========================
    @staticmethod
    def _preco_tipico(df: pd.DataFrame) -> pd.Series:
        # Lida com colunas MultiIndex do yfinance
        def _col(d: pd.DataFrame, name: str) -> pd.Series:
            if isinstance(d.columns, pd.MultiIndex):
                col = d[name]
                if isinstance(col, pd.DataFrame):
                    return col.iloc[:, 0]
                return col
            return d[name]
        h = _col(df, 'High')
        l = _col(df, 'Low')
        c = _col(df, 'Close')
        return (h + l + c) / 3.0

    def _vwap_proxy(self, df_5m: pd.DataFrame) -> Optional[Decimal]:
        if df_5m is None or df_5m.empty:
            return None
        df_5m = df_5m.copy()
        tp = self._preco_tipico(df_5m).dropna()
        if tp.empty:
            return None
        cum_tp = tp.cumsum()
        vwap = Decimal(str(cum_tp.iloc[-1] / len(tp)))
        return vwap

    def _range_do_dia(self, df_5m: pd.DataFrame) -> Dict[str, Decimal]:
        if df_5m is None or df_5m.empty:
            return {'max': Decimal('0'), 'min': Decimal('0'), 'amplitude_pct': Decimal('0')}
        highs = pd.to_numeric((df_5m['High'].iloc[:,0] if isinstance(df_5m.columns, pd.MultiIndex) else df_5m['High']), errors='coerce').dropna()
        lows = pd.to_numeric((df_5m['Low'].iloc[:,0] if isinstance(df_5m.columns, pd.MultiIndex) else df_5m['Low']), errors='coerce').dropna()
        if highs.empty or lows.empty:
            return {'max': Decimal('0'), 'min': Decimal('0'), 'amplitude_pct': Decimal('0')}
        maximo = Decimal(str(highs.max()))
        minimo = Decimal(str(lows.min()))
        amplitude_pct = (maximo - minimo) / minimo * Decimal('100') if minimo > 0 else Decimal('0')
        return {'max': maximo, 'min': minimo, 'amplitude_pct': amplitude_pct}

    def _pivos_60m(self, df_60m: pd.DataFrame, janela: int = 2, n: int = 3) -> Dict[str, List[Decimal]]:
        suportes, resistencias = [], []
        if df_60m is None or df_60m.empty:
            return {'suportes': suportes, 'resistencias': resistencias}
        if isinstance(df_60m.columns, pd.MultiIndex):
            highs = pd.to_numeric(df_60m['High'].iloc[:,0], errors='coerce')
            lows = pd.to_numeric(df_60m['Low'].iloc[:,0], errors='coerce')
        else:
            highs = pd.to_numeric(df_60m['High'], errors='coerce')
            lows = pd.to_numeric(df_60m['Low'], errors='coerce')
        df = pd.DataFrame({'High': highs, 'Low': lows})
        df = df.dropna()
        if df.empty or len(df) < (2*janela+1):
            return {'suportes': suportes, 'resistencias': resistencias}
        highs = df['High'].values
        lows = df['Low'].values
        for i in range(janela, len(df) - janela):
            if highs[i] == max(highs[i - janela:i + janela + 1]):
                resistencias.append(Decimal(str(highs[i])))
            if lows[i] == min(lows[i - janela:i + janela + 1]):
                suportes.append(Decimal(str(lows[i])))
        resistencias = sorted(list(set(resistencias)))[-n:]
        suportes = sorted(list(set(suportes)))[:n]
        return {'suportes': suportes, 'resistencias': resistencias}

    def _pivos_por_df(self, df: pd.DataFrame, janela: int = 2, n: int = 4) -> Dict[str, List[Decimal]]:
        """Calcula pivôs (SRIs) em um DataFrame OHLC qualquer (já na periodicidade)."""
        suportes, resistencias = [], []
        if df is None or df.empty:
            return {'suportes': suportes, 'resistencias': resistencias}
        # MultiIndex safe
        if isinstance(df.columns, pd.MultiIndex):
            highs = pd.to_numeric(df['High'].iloc[:,0], errors='coerce')
            lows = pd.to_numeric(df['Low'].iloc[:,0], errors='coerce')
        else:
            highs = pd.to_numeric(df['High'], errors='coerce')
            lows = pd.to_numeric(df['Low'], errors='coerce')
        df2 = pd.DataFrame({'High': highs, 'Low': lows}).dropna()
        if df2.empty or len(df2) < (2*janela+1):
            return {'suportes': suportes, 'resistencias': resistencias}
        hv = df2['High'].values
        lv = df2['Low'].values
        for i in range(janela, len(df2) - janela):
            if hv[i] == max(hv[i - janela:i + janela + 1]):
                resistencias.append(Decimal(str(hv[i])))
            if lv[i] == min(lv[i - janela:i + janela + 1]):
                suportes.append(Decimal(str(lv[i])))
        resistencias = sorted(list(set(resistencias)))[-n:]
        suportes = sorted(list(set(suportes)))[:n]
        return {'suportes': suportes, 'resistencias': resistencias}

    def _resample_df(self, df_60m: pd.DataFrame, regra: str) -> pd.DataFrame:
        """Reamostra um DataFrame 60m para outra periodicidade (ex.: '4H', '1D')"""
        if df_60m is None or df_60m.empty:
            return df_60m
        # Normaliza para Series simples
        if isinstance(df_60m.columns, pd.MultiIndex):
            o = pd.to_numeric(df_60m['Open'].iloc[:,0], errors='coerce')
            h = pd.to_numeric(df_60m['High'].iloc[:,0], errors='coerce')
            l = pd.to_numeric(df_60m['Low'].iloc[:,0], errors='coerce')
            c = pd.to_numeric(df_60m['Close'].iloc[:,0], errors='coerce')
        else:
            o = pd.to_numeric(df_60m['Open'], errors='coerce')
            h = pd.to_numeric(df_60m['High'], errors='coerce')
            l = pd.to_numeric(df_60m['Low'], errors='coerce')
            c = pd.to_numeric(df_60m['Close'], errors='coerce')
        df = pd.DataFrame({'Open': o, 'High': h, 'Low': l, 'Close': c}).dropna()
        if df.empty:
            return df
        agg = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last'
        }
        return df.resample(regra).agg(agg).dropna()

    def _consolidar_sris(self, listas: List[Dict[str, List[Decimal]]], preco_ref: Decimal, tolerancia_pct: float = 0.0005, max_por_lado: int = 6) -> Dict[str, List[Decimal]]:
        """Consolida SRIs de múltiplos timeframes deduplicando por proximidade relativa.

        tolerancia_pct padrão ~0.05%.
        """
        suportes_all: List[Decimal] = []
        resistencias_all: List[Decimal] = []
        for item in listas:
            suportes_all.extend(item.get('suportes', []))
            resistencias_all.extend(item.get('resistencias', []))

        def _dedup(valores: List[Decimal]) -> List[Decimal]:
            xs = sorted(set(valores))
            out: List[Decimal] = []
            for v in xs:
                if not out:
                    out.append(v)
                else:
                    ultimo = out[-1]
                    # proximidade relativa
                    if preco_ref > 0:
                        rel = abs((v - ultimo) / preco_ref)
                    else:
                        rel = abs(v - ultimo) / (abs(float(ultimo)) + 1e-9)
                    if float(rel) <= tolerancia_pct:
                        # mescla escolhendo o mais próximo do preço de referência
                        if abs(v - preco_ref) < abs(ultimo - preco_ref):
                            out[-1] = v
                    else:
                        out.append(v)
            return out

        sup_c = _dedup(suportes_all)
        res_c = _dedup(resistencias_all)
        # Limita quantidade
        sup_c = sup_c[:max_por_lado]
        res_c = res_c[-max_por_lado:]
        return {'suportes': sup_c, 'resistencias': res_c}

    def _vwap_sessoes(self, df_5m: pd.DataFrame) -> Dict[str, Optional[Decimal]]:
        """Calcula VWAP proxy por sessões (Tokio, Londres, NY) usando preço típico médio.

        Janelas em UTC (estáticas):
        - tokyo:   00:00–09:00
        - londres: 07:00–16:00
        - ny:      12:00–21:00
        *Sobreposição é possível; cálculo independente por janela.
        """
        out = {'tokyo': None, 'londres': None, 'ny': None}
        if df_5m is None or df_5m.empty:
            return out
        idx = df_5m.index
        if hasattr(idx, 'tz') and idx.tz is not None:
            # converte para UTC e remove tz para facilitar slicing por hora
            df = df_5m.tz_convert('UTC').copy()
            df.index = df.index.tz_localize(None)
        else:
            df = df_5m.copy()

        # apenas barras do dia atual (UTC)
        hoje = datetime.utcnow().strftime('%Y-%m-%d')
        try:
            df_dia = df.loc[hoje]
        except Exception:
            mask = (df.index.strftime('%Y-%m-%d') == hoje)
            df_dia = df.loc[mask]
        if df_dia.empty:
            return out

        def _media_tp(dfw: pd.DataFrame) -> Optional[Decimal]:
            if dfw is None or dfw.empty:
                return None
            tp = self._preco_tipico(dfw).dropna()
            if tp.empty:
                return None
            return Decimal(str(tp.mean()))

        tokyo = df_dia.between_time('00:00', '09:00')
        londres = df_dia.between_time('07:00', '16:00')
        ny = df_dia.between_time('12:00', '21:00')
        out['tokyo'] = _media_tp(tokyo)
        out['londres'] = _media_tp(londres)
        out['ny'] = _media_tp(ny)
        return out

    def _tendencia_15m(self, df_15m: pd.DataFrame) -> str:
        if df_15m is None or df_15m.empty or len(df_15m) < 30:
            return 'NEUTRO'
        close = (df_15m['Close'].iloc[:,0] if isinstance(df_15m.columns, pd.MultiIndex) else df_15m['Close'])
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()
        if ema20.iloc[-1] > ema50.iloc[-1]:
            return 'ALTISTA'
        elif ema20.iloc[-1] < ema50.iloc[-1]:
            return 'BAIXISTA'
        return 'NEUTRO'

    # ========================= FLUXO/IV/COT =========================
    def _fluxo_institucional_heuristico(self, df_5m: pd.DataFrame) -> str:
        if df_5m is None or df_5m.empty or len(df_5m) < 20:
            return 'NEUTRO'
        close = (df_5m['Close'].iloc[:,0] if isinstance(df_5m.columns, pd.MultiIndex) else df_5m['Close'])
        open_ = (df_5m['Open'].iloc[:,0] if isinstance(df_5m.columns, pd.MultiIndex) else df_5m['Open'])
        corpo = (close - open_).tail(20)
        soma = corpo.sum()
        if soma > 0 and (corpo > 0).sum() >= 12:
            return 'COMPRA'
        if soma < 0 and (corpo < 0).sum() >= 12:
            return 'VENDA'
        return 'NEUTRO'

    def _vol_realizada_proxy(self, df_15m: pd.DataFrame) -> str:
        if df_15m is None or df_15m.empty or len(df_15m) < 64:
            return 'MEDIA'
        close = (df_15m['Close'].iloc[:,0] if isinstance(df_15m.columns, pd.MultiIndex) else df_15m['Close'])
        ret = close.pct_change().dropna()
        vol_ult = ret.tail(32).std()
        vol_hist = ret.tail(320).std() if len(ret) >= 320 else ret.std()
        if vol_hist == 0 or np.isnan(vol_hist):
            return 'MEDIA'
        ratio = vol_ult / vol_hist
        if ratio > 1.4:
            return 'ALTA'
        if ratio < 0.7:
            return 'BAIXA'
        return 'MEDIA'

    def _cot_mock(self, par: str) -> str:
        # Placeholder: usar CFTC COT para futuros relacionados
        base = par[:3]
        bullish_bases = {'USD': 'LONG', 'EUR': 'NEUTRO', 'GBP': 'NEUTRO', 'JPY': 'NEUTRO', 'CHF': 'NEUTRO','CAD':'NEUTRO','AUD':'NEUTRO','NZD':'NEUTRO'}
        return bullish_bases.get(base, 'NEUTRO')

    # ========================= OPERAÇÃO =========================
    def _decidir_operacao(self, par: str, preco_atual: Decimal, vwap: Optional[Decimal], tendencia_15m: str, dxy_var: Decimal) -> Dict[str, str]:
        base, contra = par[:3], par[3:]
        # Direção do USD vs posição do USD no par
        usd_forte = dxy_var > Decimal('0.0015')
        usd_fraco = dxy_var < Decimal('-0.0015')

        acima_vwap = (vwap is not None) and (preco_atual > vwap)
        abaixo_vwap = (vwap is not None) and (preco_atual < vwap)

        operacao = 'ESPERAR'
        vies = 'Neutro'
        if base == 'USD':
            # USD base: USD forte favorece COMPRA (ex: USDJPY)
            if usd_forte and tendencia_15m == 'ALTISTA' and acima_vwap:
                operacao = 'COMPRA'
            elif usd_fraco and tendencia_15m == 'BAIXISTA' and abaixo_vwap:
                operacao = 'VENDA'
        else:
            # USD contra: USD fraco favorece COMPRA (ex: EURUSD)
            if usd_fraco and tendencia_15m == 'ALTISTA' and acima_vwap:
                operacao = 'COMPRA'
            elif usd_forte and tendencia_15m == 'BAIXISTA' and abaixo_vwap:
                operacao = 'VENDA'

        # Viés sessão texto
        vies = 'Dólar forte / Risco-Off' if usd_forte else ('Dólar fraco / Risco-On' if usd_fraco else 'Dólar estável')
        return {'operacao': operacao, 'vies': vies}

    def _montar_plano(self, par: str, preco_atual: Decimal, vwap: Optional[Decimal], sris: Dict[str, List[Decimal]], range_dia: Dict[str, Decimal], operacao: str) -> Dict[str, Decimal | str]:
        # Escolher níveis próximos como entrada/TP/Stop
        suportes = sris['suportes']
        resistencias = sris['resistencias']
        entrada = preco_atual
        alvo1 = preco_atual
        alvo2 = preco_atual
        stop = preco_atual

        if operacao == 'COMPRA':
            # Entrada: reteste de suporte acima do VWAP, senão VWAP
            candidatos = [s for s in suportes if s < preco_atual]
            entrada = max(candidatos) if candidatos else (vwap if vwap else preco_atual)
            # Alvos: resistências
            candidatos_r = [r for r in resistencias if r > preco_atual]
            alvo1 = min(candidatos_r) if candidatos_r else range_dia['max']
            alvo2 = (min([r for r in resistencias if r > alvo1]) if any(r > alvo1 for r in resistencias) else range_dia['max'])
            # Stop: pouco abaixo do próximo suporte
            sup_stop = max([s for s in suportes if s < entrada], default=entrada * Decimal('0.999'))
            stop = sup_stop * Decimal('0.999')
        elif operacao == 'VENDA':
            # Entrada: rejeição em resistência ou VWAP
            candidatos_r = [r for r in resistencias if r > preco_atual]
            entrada = min(candidatos_r) if candidatos_r else (vwap if vwap else preco_atual)
            # Alvos: suportes
            candidatos_s = [s for s in suportes if s < preco_atual]
            alvo1 = max(candidatos_s) if candidatos_s else range_dia['min']
            alvo2 = (max([s for s in suportes if s < alvo1]) if any(s < alvo1 for s in suportes) else range_dia['min'])
            # Stop: pouco acima da próxima resistência
            res_stop = min([r for r in resistencias if r > entrada], default=entrada * Decimal('1.001'))
            stop = res_stop * Decimal('1.001')
        else:
            # Esperar: usar VWAP e extremo do dia como referência
            entrada = vwap if vwap else preco_atual
            alvo1 = range_dia['max']
            alvo2 = range_dia['min']
            stop = vwap if vwap else preco_atual

        # R/R baseado em Alvo 1 ou 2 conforme direção
        risco = float(abs(entrada - stop))
        if operacao == 'COMPRA':
            recompensa = float(alvo1 - entrada)
        elif operacao == 'VENDA':
            recompensa = float(entrada - alvo1)
        else:
            recompensa = 0.0
        rr = f"1:{(recompensa/risco):.1f}" if risco > 0 else 'N/A'

        just_entrada = "Zona institucional (SRL) alinhada à VWAP da sessão" if vwap else "SRL relevante (sem VWAP)"
        just_alvos = "Alvos em resistências/suportes imediatos (15m) e topo/fundo do range da sessão"
        just_stop = "Stop curto logo após a SRL/VWAP para preservar risco"

        return {
            'entrada': entrada,
            'alvo1': alvo1,
            'alvo2': alvo2,
            'stop': stop,
            'rr': rr,
            'just_entrada': just_entrada,
            'just_alvos': just_alvos,
            'just_stop': just_stop,
        }

    # ========================= PIPELINE PRINCIPAL =========================
    def analisar_par(self, par: str) -> Optional[RelatorioIntradayForex]:
        try:
            par = par.upper()
            if par not in self.mapa_ticker:
                print(f"❌ Par {par} não suportado. Disponíveis: {', '.join(self.mapa_ticker.keys())}")
                return None
            ticker = self.mapa_ticker[par]

            df_5m, df_15m, df_60m = self._obter_series(ticker)
            if df_15m is None or df_15m.empty:
                print(f"❌ Sem dados para {par}")
                return None

            # último preço válido (compatível com MultiIndex do yfinance)
            if isinstance(df_15m.columns, pd.MultiIndex):
                close_15 = pd.to_numeric(df_15m['Close'].iloc[:, 0], errors='coerce').dropna()
            else:
                close_15 = pd.to_numeric(df_15m['Close'], errors='coerce').dropna()
            if close_15.empty:
                if df_5m is not None and not df_5m.empty:
                    if isinstance(df_5m.columns, pd.MultiIndex):
                        close_5 = pd.to_numeric(df_5m['Close'].iloc[:, 0], errors='coerce').dropna()
                    else:
                        close_5 = pd.to_numeric(df_5m['Close'], errors='coerce').dropna()
                else:
                    close_5 = pd.Series(dtype=float)
                if close_5.empty:
                    print(f"❌ Sem preço válido para {par}")
                    return None
                preco_atual = self._to_decimal_safe(close_5.iloc[-1])
            else:
                preco_atual = self._to_decimal_safe(close_15.iloc[-1])

            dxy_var, dxy_q = self._obter_dxy()
            eventos, cal_q = self._eventos_macro_do_dia(par)
            sessao = self._avaliar_vies_sessao(par, dxy_var)
            vwap = self._vwap_proxy(df_5m)
            range_dia = self._range_do_dia(df_5m)
            # SRIs multi-timeframe: H1 (60m), H4 (resample), D1 (resample)
            sris_h1 = self._pivos_60m(df_60m)
            df_h4 = self._resample_df(df_60m, '4h')
            sris_h4 = self._pivos_por_df(df_h4)
            df_d1 = self._resample_df(df_60m, '1D')
            sris_d1 = self._pivos_por_df(df_d1)
            sris = self._consolidar_sris([sris_h1, sris_h4, sris_d1], preco_atual)
            tendencia = self._tendencia_15m(df_15m)
            fluxo = self._fluxo_institucional_heuristico(df_5m)
            vol = self._vol_realizada_proxy(df_15m)
            cot = self._cot_mock(par)
            vwap_sessoes = self._vwap_sessoes(df_5m)

            decisao = self._decidir_operacao(par, preco_atual, vwap, tendencia, dxy_var)
            plano = self._montar_plano(par, preco_atual, vwap, sris, range_dia, decisao['operacao'])

            rel = RelatorioIntradayForex(
                par=par,
                ticker_yahoo=ticker,
                preco_atual=preco_atual,
                timestamp=datetime.now(),
                operacao=decisao['operacao'],
                vies_sessao=decisao['vies'],
                rr_texto=plano['rr'],
                eventos_criticos=eventos,
                dxy_variacao=dxy_var,
                forca_moeda_base='-',
                forca_moeda_contra='-',
                dxy_qualidade=dxy_q,
                calendario_qualidade=cal_q,
                vwap=vwap,
                range_dia={k: v for k, v in range_dia.items()},
                sris_suportes=sris['suportes'],
                sris_resistencias=sris['resistencias'],
                invalicacao_intraday=plano['stop'],
                tendencia_15m=tendencia,
                fluxo_institucional=fluxo,
                vol_realizada=vol,
                cot_curto_prazo=cot,
                preco_entrada=plano['entrada'],
                alvo_1=plano['alvo1'],
                alvo_2=plano['alvo2'],
                stop_loss=plano['stop'],
                just_entrada=plano['just_entrada'],
                just_alvos=plano['just_alvos'],
                just_stop=plano['just_stop'],
            )
            # anexa atributos não mandatórios via monkey patch
            setattr(rel, 'sris_detalhado', {'H1': sris_h1, 'H4': sris_h4, 'D1': sris_d1})
            setattr(rel, 'vwap_sessoes', vwap_sessoes)
            return rel
        except Exception as e:
            print(f"❌ Erro ao analisar {par}: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ========================= RENDERIZADOR =========================
    def gerar_markdown(self, r: RelatorioIntradayForex) -> str:
        md = []
        md.append(f"\n# ⚡️ RELATÓRIO DE TRADING INTRA-DAY FOREX: {r.par}\n")
        md.append(f"**Preço Atual:** {float(r.preco_atual):.5f}\n")
        md.append(f"**Data/Hora:** {r.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        md.append("## 📊 PARTE 1 — RESUMO E OPERAÇÃO\n\n")
        md.append("| Categoria | Descrição do Foco de Análise |\n| :--- | :--- |\n")
        md.append(f"| **OPERAÇÃO RECOMENDADA (4–8h)** | **[{r.operacao}]** |\n")
        md.append(f"| **Viés da Sessão** | {r.vies_sessao} |\n")
        md.append(f"| **Risco/Recompensa (R/R)** | {r.rr_texto} |\n\n")

        md.append("## 📰 PARTE 2 — ANÁLISES DETALHADAS\n\n")
        md.append("### A. Eventos Macro e Sentimento do Dia\n")
        md.append("- **Eventos Críticos (mock):**\n")
        for ev in r.eventos_criticos:
            md.append(f"  - {ev}\n")
        md.append(f"- **DXY (var. diária):** {float(r.dxy_variacao)*100:.2f}%\n")
        md.append(f"- **Direção de Força Base/Contra:** {r.forca_moeda_base} / {r.forca_moeda_contra}\n\n")

        md.append("### B. Análise Técnica Imediata (5m/15m/60m)\n")
        if r.vwap:
            md.append(f"- **VWAP da Sessão (proxy):** {float(r.vwap):.5f}\n")
        else:
            md.append(f"- **VWAP da Sessão (proxy):** Indisponível (dados de volume não confiáveis)\n")
        md.append(f"- **Range do Dia:** Máx {float(r.range_dia['max']):.5f} | Mín {float(r.range_dia['min']):.5f} | Amp {float(r.range_dia['amplitude_pct']):.2f}%\n")
        sup = ", ".join([f"{float(s):.5f}" for s in r.sris_suportes]) if r.sris_suportes else "-"
        res = ", ".join([f"{float(s):.5f}" for s in r.sris_resistencias]) if r.sris_resistencias else "-"
        md.append(f"- **SRIs (Suportes):** {sup}\n")
        md.append(f"- **SRIs (Resistências):** {res}\n")
        md.append(f"- **Tendência 15m:** {r.tendencia_15m}\n")
        md.append(f"- **Invalidação Intraday:** {float(r.invalicacao_intraday):.5f}\n\n")

        md.append("### C. Fluxo de Fundos e Volatilidade\n")
        md.append(f"- **Order Flow (heurístico):** {r.fluxo_institucional}\n")
        md.append(f"- **Volatilidade Realizada (proxy de IV):** {r.vol_realizada}\n")
        md.append(f"- **Posicionamento Especulativo (COT mock):** {r.cot_curto_prazo}\n\n")

        md.append("## 🚀 PARTE 3 — PLANO DE EXECUÇÃO RÁPIDA\n\n")
        md.append("| Detalhe da Operação | Valor | Justificativa Refinada (4–8h) |\n| :--- | :---: | :--- |\n")
        md.append(f"| **PREÇO DE ENTRADA** | **{float(r.preco_entrada):.5f}** | {r.just_entrada} |\n")
        md.append(f"| **ALVO 1 (Take Profit)** | {float(r.alvo_1):.5f} | Resistência/Suporte imediato (15m), realização parcial |\n")
        md.append(f"| **ALVO 2 (Take Profit)** | {float(r.alvo_2):.5f} | Topo/Fundo do range da sessão ou próxima barreira institucional |\n")
        md.append(f"| **INVALIDAÇÃO (Stop Loss)** | **{float(r.stop_loss):.5f}** | {r.just_stop} |\n\n")

        md.append("---\n\n")
        md.append("⚠️  DISCLAIMER: Conteúdo educacional. Não é recomendação. Forex envolve risco elevado.\n")
        return "".join(md)

    # ========================= SERIALIZAÇÃO JSON =========================
    def gerar_json(self, r: RelatorioIntradayForex) -> dict:
        """Gera payload JSON compatível com o contrato report.intraday.v1.

        Observações:
        - Converte Decimals para float
        - Datas em ISO 8601 UTC local (sem tz para simplificação)
        - Campos de qualidade sinalizam disponibilidade dos dados
        """
        try:
            dxy_flag = r.dxy_qualidade if r.dxy_qualidade else ('ok' if r.dxy_variacao != Decimal('0') else 'indisponivel')
        except Exception:
            dxy_flag = 'indisponivel'

        payload = {
            'contractVersion': 'report.intraday.v1',
            'classeAtivo': 'forex',
            'par': r.par,
            'tickerYahoo': r.ticker_yahoo,
            'timestamp': r.timestamp.isoformat(timespec='seconds'),
            'precoAtual': float(r.preco_atual),
            'resumo': {
                'operacao': r.operacao,
                'viesSessao': r.vies_sessao,
                'rr': r.rr_texto,
            },
            'analises': {
                'eventos': list(r.eventos_criticos or []),
                'dxyVariacao': float(r.dxy_variacao),
                'tecnica': {
                    'vwap': (float(r.vwap) if r.vwap is not None else None),
                    'rangeDia': {
                        'max': float(r.range_dia.get('max', Decimal('0'))),
                        'min': float(r.range_dia.get('min', Decimal('0'))),
                        'amplitudePct': float(r.range_dia.get('amplitude_pct', Decimal('0'))),
                    },
                    'sris': {
                        'suportes': [float(x) for x in (r.sris_suportes or [])],
                        'resistencias': [float(x) for x in (r.sris_resistencias or [])],
                    },
                    'tendencia15m': r.tendencia_15m,
                    'invalicacaoIntraday': float(r.invalicacao_intraday),
                },
                'fluxoVol': {
                    'fluxoInstitucional': r.fluxo_institucional,
                    'volRealizada': r.vol_realizada,
                    'cotCurtoPrazo': r.cot_curto_prazo,
                },
            },
            'plano': {
                'entrada': float(r.preco_entrada),
                'alvo1': float(r.alvo_1),
                'alvo2': float(r.alvo_2),
                'stop': float(r.stop_loss),
                'justificativas': {
                    'entrada': r.just_entrada,
                    'alvos': r.just_alvos,
                    'stop': r.just_stop,
                }
            },
            'qualidade': {
                'dadosMercado': 'ok' if float(r.preco_atual) > 0 else 'indisponivel',
                'dxy': dxy_flag,
                'calendario': (r.calendario_qualidade or 'mock'),
            }
        }
        # Campos opcionais (compatíveis com schema atual – additionalProperties)
        try:
            sris_det = getattr(r, 'sris_detalhado', None)
            if isinstance(sris_det, dict):
                payload['analises']['tecnica']['srisDetalhado'] = {
                    k: {
                        'suportes': [float(x) for x in v.get('suportes', [])],
                        'resistencias': [float(x) for x in v.get('resistencias', [])]
                    }
                    for k, v in sris_det.items()
                }
        except Exception:
            pass
        try:
            vwap_sess = getattr(r, 'vwap_sessoes', None)
            if isinstance(vwap_sess, dict):
                payload['analises']['tecnica']['vwapSessoes'] = {
                    k: (float(v) if v is not None else None)
                    for k, v in vwap_sess.items()
                }
        except Exception:
            pass
        return payload


if __name__ == '__main__':
    analisador = AnalisadorIntradayForex()
    par = 'EURUSD'
    print(f"Testando relatório intraday para {par}...\n")
    r = analisador.analisar_par(par)
    if r:
        print(analisador.gerar_markdown(r))
