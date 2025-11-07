"""
Estratégia Ensemble que combina múltiplos indicadores e estratégias.
Usa votação ponderada para gerar sinais mais robustos.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from src.backtest.motor_backtest import (
    SinalTecnico,
    CalculadorIndicadores,
    EstrategiaCruzamentoMedias,
    EstrategiaRSI,
    EstrategiaBollinger,
    EstrategiaMACD,
)


@dataclass
class VotoEstrategia:
    """Voto de uma estratégia individual."""
    nome: str
    tipo: str  # 'COMPRA', 'VENDA' ou None
    confianca: float
    razao: str


class EstrategiaEnsemble:
    """
    Estratégia Ensemble que combina múltiplas estratégias.
    Usa votação ponderada para decisão final.
    """

    def __init__(
        self,
        usar_ma: bool = True,
        usar_rsi: bool = True,
        usar_bollinger: bool = True,
        usar_macd: bool = True,
        peso_ma: float = 1.0,
        peso_rsi: float = 1.0,
        peso_bollinger: float = 0.8,
        peso_macd: float = 0.7,
        limiar_consenso: float = 0.6,
    ):
        """
        Args:
            usar_*: Se deve incluir cada estratégia
            peso_*: Peso de cada estratégia na votação (0.0 a 1.0)
            limiar_consenso: Consenso mínimo necessário para gerar sinal (0.0 a 1.0)
        """
        self.estrategias = []
        self.pesos = []

        if usar_ma:
            self.estrategias.append(('MA', EstrategiaCruzamentoMedias(9, 21)))
            self.pesos.append(peso_ma)

        if usar_rsi:
            self.estrategias.append(('RSI', EstrategiaRSI(14, 70, 30)))
            self.pesos.append(peso_rsi)

        if usar_bollinger:
            self.estrategias.append(('BB', EstrategiaBollinger(20, 2.0)))
            self.pesos.append(peso_bollinger)

        if usar_macd:
            self.estrategias.append(('MACD', EstrategiaMACD(12, 26, 9)))
            self.pesos.append(peso_macd)

        self.limiar_consenso = limiar_consenso
        self.nome = (
            f"Ensemble wMA={peso_ma:.1f},wRSI={peso_rsi:.1f},wBB={peso_bollinger:.1f},"
            f"wMACD={peso_macd:.1f},consenso={limiar_consenso:.0%}"
        )

    def gerar_sinal(self, dados_historicos: List[dict]) -> Optional[SinalTecnico]:
        """
        Gera sinal baseado em votação ponderada das estratégias.

        Returns:
            SinalTecnico se houver consenso suficiente, None caso contrário
        """
        if len(dados_historicos) < 50:
            return None

        # Coletar votos de cada estratégia
        votos = []
        for nome, estrategia in self.estrategias:
            sinal = estrategia.gerar_sinal(dados_historicos)
            if sinal:
                votos.append(VotoEstrategia(
                    nome=nome,
                    tipo=sinal.tipo,
                    confianca=sinal.confianca,
                    razao=sinal.razao
                ))

        if not votos:
            return None

        # Calcular consenso ponderado
        votos_compra = []
        votos_venda = []

        for i, voto in enumerate(votos):
            peso = self.pesos[i]
            if voto.tipo == 'COMPRA':
                votos_compra.append((voto, peso))
            elif voto.tipo == 'VENDA':
                votos_venda.append((voto, peso))

        # Calcular força de cada direção
        peso_total = sum(self.pesos[:len(votos)])
        forca_compra = sum(peso * voto.confianca for voto, peso in votos_compra) / peso_total if peso_total > 0 else 0
        forca_venda = sum(peso * voto.confianca for voto, peso in votos_venda) / peso_total if peso_total > 0 else 0

        # Determinar direção e consenso
        if forca_compra > forca_venda and forca_compra >= self.limiar_consenso:
            tipo_sinal = 'COMPRA'
            consenso = forca_compra
            votos_favoraveis = votos_compra
        elif forca_venda > forca_compra and forca_venda >= self.limiar_consenso:
            tipo_sinal = 'VENDA'
            consenso = forca_venda
            votos_favoraveis = votos_venda
        else:
            # Sem consenso suficiente
            return None

        # Construir sinal ensemble
        dado_atual = dados_historicos[-1]
        preco_atual = dado_atual['ultimo']

        # Calcular ATR para stops
        atr = CalculadorIndicadores.atr(dados_historicos, 14)
        if atr is None:
            atr = preco_atual * 0.02

        # Configurar stop e target baseado no consenso
        multiplicador_stop = 2.0 if consenso >= 0.8 else 2.5
        multiplicador_target = 3.0 if consenso >= 0.8 else 4.0

        if tipo_sinal == 'COMPRA':
            stop_loss = preco_atual - (atr * multiplicador_stop)
            take_profit = preco_atual + (atr * multiplicador_target)
        else:
            stop_loss = preco_atual + (atr * multiplicador_stop)
            take_profit = preco_atual - (atr * multiplicador_target)

        # Construir razão detalhada
        razao_partes = [f"Consenso {tipo_sinal}: {consenso:.1%} ({len(votos_favoraveis)}/{len(votos)} estratégias)"]
        for voto, peso in votos_favoraveis:
            razao_partes.append(f"  • {voto.nome}: {voto.confianca:.0%} - {voto.razao[:50]}")

        razao = "\n".join(razao_partes)

        return SinalTecnico(
            data=dado_atual['data'],
            tipo=tipo_sinal,
            preco_entrada=preco_atual,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confianca=consenso,
            indicadores={
                'atr': atr,
                'num_votos': len(votos),
                'votos_favoraveis': len(votos_favoraveis),
                'forca_compra': forca_compra,
                'forca_venda': forca_venda
            },
            razao=razao
        )


class EstrategiaMultiIndicador:
    """
    Estratégia que usa múltiplos indicadores com confirmação cruzada.
    Mais rígida que o ensemble - todos os indicadores devem concordar.
    """

    def __init__(
        self,
        periodo_ma_curta: int = 9,
        periodo_ma_longa: int = 21,
        periodo_rsi: int = 14,
        rsi_sobrecompra: float = 70,
        rsi_sobrevenda: float = 30,
    ):
        self.periodo_ma_curta = periodo_ma_curta
        self.periodo_ma_longa = periodo_ma_longa
        self.periodo_rsi = periodo_rsi
        self.rsi_sobrecompra = rsi_sobrecompra
        self.rsi_sobrevenda = rsi_sobrevenda
        self.nome = f"Multi-Indicador (MA{periodo_ma_curta}/{periodo_ma_longa} + RSI{periodo_rsi})"

    def gerar_sinal(self, dados_historicos: List[dict]) -> Optional[SinalTecnico]:
        """Gera sinal apenas quando todos os indicadores concordam."""
        if len(dados_historicos) < max(self.periodo_ma_longa, self.periodo_rsi) + 2:
            return None

        precos = [d['ultimo'] for d in dados_historicos]

        # Calcular indicadores
        ma_curta = CalculadorIndicadores.media_movel_simples(precos, self.periodo_ma_curta)
        ma_longa = CalculadorIndicadores.media_movel_simples(precos, self.periodo_ma_longa)
        ma_curta_ant = CalculadorIndicadores.media_movel_simples(precos[:-1], self.periodo_ma_curta)
        ma_longa_ant = CalculadorIndicadores.media_movel_simples(precos[:-1], self.periodo_ma_longa)

        rsi = CalculadorIndicadores.rsi(precos, self.periodo_rsi)

        bandas = CalculadorIndicadores.bollinger_bands(precos, 20, 2.0)

        if None in [ma_curta, ma_longa, ma_curta_ant, ma_longa_ant, rsi, bandas]:
            return None

        banda_sup, banda_media, banda_inf = bandas

        dado_atual = dados_historicos[-1]
        preco_atual = dado_atual['ultimo']

        # Calcular ATR
        atr = CalculadorIndicadores.atr(dados_historicos, 14)
        if atr is None:
            atr = preco_atual * 0.02

        # Verificar cruzamento de médias
        cruzamento_alta = ma_curta_ant <= ma_longa_ant and ma_curta > ma_longa
        cruzamento_baixa = ma_curta_ant >= ma_longa_ant and ma_curta < ma_longa

        # Sinal de COMPRA: todas as condições devem ser verdadeiras
        if cruzamento_alta:
            # Confirmações necessárias:
            # 1. RSI não está em sobrecompra (< 70)
            # 2. Preço próximo ou abaixo da banda média (potencial de alta)
            # 3. Tendência de alta (MA curta > MA longa)

            condicoes_compra = [
                rsi < self.rsi_sobrecompra,  # RSI não sobrecomprado
                preco_atual <= banda_media * 1.01,  # Próximo da média
                ma_curta > ma_longa,  # Tendência de alta
            ]

            if all(condicoes_compra):
                distancia_pct = ((ma_curta - ma_longa) / ma_longa) * 100
                confianca = 0.7 + min(abs(distancia_pct) / 5, 0.25)

                return SinalTecnico(
                    data=dado_atual['data'],
                    tipo='COMPRA',
                    preco_entrada=preco_atual,
                    stop_loss=preco_atual - (atr * 2),
                    take_profit=preco_atual + (atr * 3),
                    confianca=min(confianca, 0.95),
                    indicadores={
                        'ma_curta': ma_curta,
                        'ma_longa': ma_longa,
                        'rsi': rsi,
                        'banda_media': banda_media,
                        'atr': atr
                    },
                    razao=f"COMPRA confirmada: MA{self.periodo_ma_curta} cruzou acima ({ma_curta:.0f} > {ma_longa:.0f}), RSI={rsi:.1f}, Preço={preco_atual:.0f} vs Média BB={banda_media:.0f}"
                )

        # Sinal de VENDA: todas as condições devem ser verdadeiras
        elif cruzamento_baixa:
            condicoes_venda = [
                rsi > self.rsi_sobrevenda,  # RSI não sobrevendido
                preco_atual >= banda_media * 0.99,  # Próximo da média
                ma_curta < ma_longa,  # Tendência de baixa
            ]

            if all(condicoes_venda):
                distancia_pct = ((ma_longa - ma_curta) / ma_longa) * 100
                confianca = 0.7 + min(abs(distancia_pct) / 5, 0.25)

                return SinalTecnico(
                    data=dado_atual['data'],
                    tipo='VENDA',
                    preco_entrada=preco_atual,
                    stop_loss=preco_atual + (atr * 2),
                    take_profit=preco_atual - (atr * 3),
                    confianca=min(confianca, 0.95),
                    indicadores={
                        'ma_curta': ma_curta,
                        'ma_longa': ma_longa,
                        'rsi': rsi,
                        'banda_media': banda_media,
                        'atr': atr
                    },
                    razao=f"VENDA confirmada: MA{self.periodo_ma_curta} cruzou abaixo ({ma_curta:.0f} < {ma_longa:.0f}), RSI={rsi:.1f}, Preço={preco_atual:.0f} vs Média BB={banda_media:.0f}"
                )

        return None


class EstrategiaRegimeMercado:
    """
    Estratégia que detecta regime de mercado (tendência vs lateral).
    Usa estratégias diferentes para cada regime.
    """

    def __init__(self, periodo_atr: int = 14, limiar_volatilidade: float = 1.5):
        self.periodo_atr = periodo_atr
        self.limiar_volatilidade = limiar_volatilidade

        # Estratégias para cada regime
        self.estrategia_tendencia = EstrategiaCruzamentoMedias(9, 21)
        self.estrategia_lateral = EstrategiaBollinger(20, 2.0)

        self.nome = f"Regime Adaptativo (ATR={periodo_atr}, limiar={limiar_volatilidade})"

    def detectar_regime(self, dados_historicos: List[dict]) -> str:
        """
        Detecta se o mercado está em tendência ou lateral.

        Returns:
            'tendencia', 'lateral' ou 'indefinido'
        """
        if len(dados_historicos) < 50:
            return 'indefinido'

        precos = [d['ultimo'] for d in dados_historicos]

        # Calcular ATR normalizado (ATR / preço)
        atr = CalculadorIndicadores.atr(dados_historicos, self.periodo_atr)
        if atr is None:
            return 'indefinido'

        preco_atual = precos[-1]
        atr_normalizado = (atr / preco_atual) * 100  # ATR em %

        # Calcular direcionalidade (ADX simplificado)
        ma_20 = CalculadorIndicadores.media_movel_simples(precos, 20)
        ma_50 = CalculadorIndicadores.media_movel_simples(precos, 50)

        if ma_20 is None or ma_50 is None:
            return 'indefinido'

        distancia_mas = abs((ma_20 - ma_50) / ma_50) * 100

        # Classificar regime
        if atr_normalizado > self.limiar_volatilidade and distancia_mas > 2.0:
            return 'tendencia'
        elif atr_normalizado < self.limiar_volatilidade * 0.7:
            return 'lateral'
        else:
            return 'indefinido'

    def gerar_sinal(self, dados_historicos: List[dict]) -> Optional[SinalTecnico]:
        """Gera sinal baseado no regime de mercado detectado."""
        regime = self.detectar_regime(dados_historicos)

        if regime == 'indefinido':
            return None

        # Selecionar estratégia apropriada
        if regime == 'tendencia':
            sinal = self.estrategia_tendencia.gerar_sinal(dados_historicos)
            if sinal:
                sinal.razao = f"[REGIME: TENDÊNCIA] {sinal.razao}"
        else:  # lateral
            sinal = self.estrategia_lateral.gerar_sinal(dados_historicos)
            if sinal:
                sinal.razao = f"[REGIME: LATERAL] {sinal.razao}"

        return sinal
