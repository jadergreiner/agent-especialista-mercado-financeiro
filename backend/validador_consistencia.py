"""
Validador de Consistência Entre Fontes

Detecta e alerta sobre divergências entre:
- Análise técnica (SMA, RSI, sinais de preço)
- Análise fundamental (sentimento de notícias)
- Cenários de análise (Bull vs Bear)

Gera alertas quando sinais contraditórios são detectados.
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidadorConsistencia:
    """
    Validador de consistência entre fontes de análise.
    """

    def __init__(self):
        """Inicializa o validador."""
        logger.info("Validador de consistência inicializado")

    def validar_consistencia(
        self,
        dados_preco: Dict,
        dados_indicadores: Optional[Dict],
        dados_noticias: Optional[Dict],
        confianca_bull: float,
        confianca_bear: float
    ) -> Dict[str, Any]:
        """
        Valida consistência entre todas as fontes de dados.

        Args:
            dados_preco: Dados de preço atuais
            dados_indicadores: Indicadores técnicos
            dados_noticias: Dados de notícias
            confianca_bull: Confiança no cenário Bull (%)
            confianca_bear: Confiança no cenário Bear (%)

        Returns:
            dict: Resultado da validação com alertas e score de consistência
        """
        logger.info("Iniciando validação de consistência")

        # Coletar sinais de cada fonte
        sinais = {
            'tecnico': self._analisar_sinais_tecnicos(dados_indicadores),
            'fundamental': self._analisar_sinais_fundamentais(dados_noticias),
            'cenario': self._analisar_sinais_cenario(confianca_bull, confianca_bear)
        }

        # Detectar divergências
        divergencias = self._detectar_divergencias(sinais)

        # Calcular score de consistência
        score_consistencia = self._calcular_score_consistencia(divergencias)

        # Gerar alertas
        alertas = self._gerar_alertas(divergencias, sinais)

        resultado = {
            'sinais_fontes': sinais,
            'divergencias_detectadas': divergencias,
            'score_consistencia': score_consistencia,
            'nivel_consistencia': self._determinar_nivel_consistencia(score_consistencia),
            'alertas': alertas,
            'recomendacoes': self._gerar_recomendacoes(alertas)
        }

        logger.info(f"Validação concluída: Score {score_consistencia:.1f}, {len(alertas)} alerta(s)")
        return resultado

    def _analisar_sinais_tecnicos(self, dados_indicadores: Optional[Dict]) -> Dict[str, Any]:
        """
        Analisa sinais técnicos (SMA, RSI, momentum).
        """
        if not dados_indicadores or 'indicadores' not in dados_indicadores:
            return {'sinal': 'NEUTRO', 'forca': 0, 'justificativa': 'Indicadores não disponíveis'}

        indicadores = dados_indicadores['indicadores']
        sinais = []

        # Análise SMA
        if 'sma' in indicadores:
            sma = indicadores['sma']
            if sma['sinal'] == 'ACIMA_SMA':
                sinais.append(('BULL', 0.6, f"SMA20 acima do preço ({sma['diferenca_pct']:+.2f}%)"))
            elif sma['sinal'] == 'ABAIXO_SMA':
                sinais.append(('BEAR', 0.6, f"SMA20 abaixo do preço ({sma['diferenca_pct']:+.2f}%)"))

        # Análise RSI
        if 'rsi' in indicadores:
            rsi = indicadores['rsi']
            if rsi['sinal'] == 'ALTISTA':
                sinais.append(('BULL', 0.4, f"RSI {rsi['valor']:.1f} altista"))
            elif rsi['sinal'] == 'BAIXISTA':
                sinais.append(('BEAR', 0.4, f"RSI {rsi['valor']:.1f} baixista"))
            else:
                sinais.append(('NEUTRO', 0.2, f"RSI {rsi['valor']:.1f} neutro"))

        # Consolidar sinais
        if not sinais:
            return {'sinal': 'NEUTRO', 'forca': 0, 'justificativa': 'Nenhum sinal técnico claro'}

        # Calcular sinal predominante
        bull_forca = sum(forca for sinal, forca, _ in sinais if sinal == 'BULL')
        bear_forca = sum(forca for sinal, forca, _ in sinais if sinal == 'BEAR')

        if bull_forca > bear_forca + 0.3:
            sinal_principal = 'BULL'
            forca_total = bull_forca
        elif bear_forca > bull_forca + 0.3:
            sinal_principal = 'BEAR'
            forca_total = bear_forca
        else:
            sinal_principal = 'NEUTRO'
            forca_total = max(bull_forca, bear_forca)

        justificativas = [just for _, _, just in sinais]

        return {
            'sinal': sinal_principal,
            'forca': min(forca_total, 1.0),
            'justificativa': '; '.join(justificativas)
        }

    def _analisar_sinais_fundamentais(self, dados_noticias: Optional[Dict]) -> Dict[str, Any]:
        """
        Analisa sinais fundamentais (sentimento de notícias).
        """
        if not dados_noticias or 'resumo_geral' not in dados_noticias:
            return {'sinal': 'NEUTRO', 'forca': 0, 'justificativa': 'Notícias não disponíveis'}

        resumo = dados_noticias['resumo_geral']
        sentimento = resumo.get('sentimento_geral', 'NEUTRO')
        impacto = resumo.get('impacto_geral', 'MÉDIO')

        # Mapear sentimento para sinal
        if sentimento == 'POSITIVO' and impacto == 'ALTO':
            sinal = 'BULL'
            forca = 0.8
        elif sentimento == 'NEGATIVO' and impacto == 'ALTO':
            sinal = 'BEAR'
            forca = 0.8
        elif sentimento == 'POSITIVO' and impacto == 'MÉDIO':
            sinal = 'BULL'
            forca = 0.5
        elif sentimento == 'NEGATIVO' and impacto == 'MÉDIO':
            sinal = 'BEAR'
            forca = 0.5
        else:
            sinal = 'NEUTRO'
            forca = 0.2

        justificativa = f"Notícias com sentimento {sentimento} e impacto {impacto}"

        return {
            'sinal': sinal,
            'forca': forca,
            'justificativa': justificativa
        }

    def _analisar_sinais_cenario(self, confianca_bull: float, confianca_bear: float) -> Dict[str, Any]:
        """
        Analisa sinais baseados nos cenários de confiança.
        """
        diff = confianca_bull - confianca_bear

        if diff > 20:
            sinal = 'BULL'
            forca = min(diff / 50, 1.0)  # Normalizar para 0-1
            justificativa = f"Cenário Bull dominante ({confianca_bull:.1f}% vs {confianca_bear:.1f}%)"
        elif diff < -20:
            sinal = 'BEAR'
            forca = min(abs(diff) / 50, 1.0)
            justificativa = f"Cenário Bear dominante ({confianca_bear:.1f}% vs {confianca_bull:.1f}%)"
        else:
            sinal = 'NEUTRO'
            forca = 0.1
            justificativa = f"Cenários equilibrados ({confianca_bull:.1f}% vs {confianca_bear:.1f}%)"

        return {
            'sinal': sinal,
            'forca': forca,
            'justificativa': justificativa
        }

    def _detectar_divergencias(self, sinais: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Detecta divergências entre as fontes.
        """
        divergencias = []

        tecnico = sinais['tecnico']
        fundamental = sinais['fundamental']
        cenario = sinais['cenario']

        # Divergência Técnico vs Fundamental
        if tecnico['sinal'] != 'NEUTRO' and fundamental['sinal'] != 'NEUTRO':
            if tecnico['sinal'] != fundamental['sinal']:
                # Verificar força das divergências
                forca_divergencia = (tecnico['forca'] + fundamental['forca']) / 2

                if forca_divergencia > 0.4:  # Divergência significativa
                    divergencias.append({
                        'tipo': 'tecnico_fundamental',
                        'fontes': ['tecnico', 'fundamental'],
                        'sinais': [tecnico['sinal'], fundamental['sinal']],
                        'forca': forca_divergencia,
                        'severidade': 'ALTA' if forca_divergencia > 0.7 else 'MÉDIA',
                        'descricao': f"Análise técnica ({tecnico['sinal']}) diverge do fundamental ({fundamental['sinal']})"
                    })

        # Divergência Técnico vs Cenário
        if tecnico['sinal'] != 'NEUTRO' and cenario['sinal'] != 'NEUTRO':
            if tecnico['sinal'] != cenario['sinal']:
                forca_divergencia = (tecnico['forca'] + cenario['forca']) / 2

                if forca_divergencia > 0.3:
                    divergencias.append({
                        'tipo': 'tecnico_cenario',
                        'fontes': ['tecnico', 'cenario'],
                        'sinais': [tecnico['sinal'], cenario['sinal']],
                        'forca': forca_divergencia,
                        'severidade': 'MÉDIA',
                        'descricao': f"Técnico ({tecnico['sinal']}) diverge do cenário ({cenario['sinal']})"
                    })

        # Divergência Fundamental vs Cenário
        if fundamental['sinal'] != 'NEUTRO' and cenario['sinal'] != 'NEUTRO':
            if fundamental['sinal'] != cenario['sinal']:
                forca_divergencia = (fundamental['forca'] + cenario['forca']) / 2

                if forca_divergencia > 0.3:
                    divergencias.append({
                        'tipo': 'fundamental_cenario',
                        'fontes': ['fundamental', 'cenario'],
                        'sinais': [fundamental['sinal'], cenario['sinal']],
                        'forca': forca_divergencia,
                        'severidade': 'MÉDIA',
                        'descricao': f"Fundamental ({fundamental['sinal']}) diverge do cenário ({cenario['sinal']})"
                    })

        return divergencias

    def _calcular_score_consistencia(self, divergencias: List[Dict]) -> float:
        """
        Calcula score de consistência (0-100, onde 100 = totalmente consistente).
        """
        if not divergencias:
            return 100.0

        # Penalizar por cada divergência baseada na força e severidade
        penalidade_total = 0

        for div in divergencias:
            if div['severidade'] == 'ALTA':
                penalidade = div['forca'] * 30  # Até 30 pontos por divergência alta
            else:  # MÉDIA
                penalidade = div['forca'] * 15  # Até 15 pontos por divergência média

            penalidade_total += penalidade

        # Limitar penalidade máxima em 80 pontos (mínimo score = 20)
        penalidade_total = min(penalidade_total, 80)

        return 100 - penalidade_total

    def _determinar_nivel_consistencia(self, score: float) -> str:
        """
        Determina nível de consistência baseado no score.
        """
        if score >= 90:
            return "EXCELENTE"
        elif score >= 75:
            return "BOM"
        elif score >= 60:
            return "REGULAR"
        elif score >= 40:
            return "RUIM"
        else:
            return "CRÍTICO"

    def _gerar_alertas(self, divergencias: List[Dict], sinais: Dict) -> List[Dict[str, Any]]:
        """
        Gera alertas baseados nas divergências detectadas.
        """
        alertas = []

        for div in divergencias:
            alerta = {
                'tipo': div['tipo'],
                'severidade': div['severidade'],
                'titulo': f"Divergência {div['tipo'].replace('_', ' vs ').title()}",
                'mensagem': div['descricao'],
                'recomendacao': self._gerar_recomendacao_divergencia(div),
                'fontes_afetadas': div['fontes'],
                'timestamp': datetime.now().isoformat()
            }
            alertas.append(alerta)

        # Alerta adicional para consistência geral baixa
        if len(divergencias) >= 2:
            alertas.append({
                'tipo': 'consistencia_geral',
                'severidade': 'ALTA',
                'titulo': 'Múltiplas Divergências Detectadas',
                'mensagem': f'{len(divergencias)} divergências identificadas entre fontes de análise',
                'recomendacao': 'Revisar todas as fontes de dados; considerar pausa na tomada de decisão',
                'fontes_afetadas': ['todas'],
                'timestamp': datetime.now().isoformat()
            })

        return alertas

    def _gerar_recomendacao_divergencia(self, divergencia: Dict) -> str:
        """
        Gera recomendação específica para uma divergência.
        """
        tipo = divergencia['tipo']

        if tipo == 'tecnico_fundamental':
            return "Monitorar resolução da divergência; aguardar confirmação de uma das fontes"
        elif tipo == 'tecnico_cenario':
            return "Recalibrar cenários baseado em dados técnicos atuais"
        elif tipo == 'fundamental_cenario':
            return "Reavaliar cenários considerando impacto das notícias recentes"
        else:
            return "Revisar fontes de dados conflitantes"

    def _gerar_recomendacoes(self, alertas: List[Dict]) -> List[str]:
        """
        Gera recomendações gerais baseadas nos alertas.
        """
        if not alertas:
            return ["Análise consistente - todas as fontes alinhadas"]

        recomendacoes = []

        severidades_altas = sum(1 for a in alertas if a['severidade'] == 'ALTA')

        if severidades_altas > 0:
            recomendacoes.append("🚨 ALERTA: Divergências críticas detectadas - exercer extrema cautela")
            recomendacoes.append("Recomendação: Aguardar resolução das divergências antes de agir")

        if len(alertas) > 1:
            recomendacoes.append("Múltiplas fontes conflitantes - considerar análise mais profunda")

        recomendacoes.append("Monitorar evolução dos indicadores para resolução das divergências")

        return recomendacoes