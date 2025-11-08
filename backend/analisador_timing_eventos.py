#!/usr/bin/env python3
"""
Análise de Timing Baseado em Eventos - Sistema Especialista Mercado Financeiro

Analisa o calendário econômico das próximas 48h e avalia:
1. Riscos de evento para cada posição
2. Oportunidades de aceleração favorável
3. Janelas ótimas de saída
4. Ajustes de posicionamento pré-evento

Autor: Sistema Especialista Mercado Financeiro
Data: 2025-11-07
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class EventoEconomico:
    """Representa um evento econômico."""
    timestamp: datetime
    moeda: str
    titulo: str
    impacto: str
    expectativa: Optional[float] = None
    anterior: Optional[float] = None

@dataclass
class AnalisePosicao:
    """Análise de timing para uma posição."""
    position_id: str
    par: str
    direcao: str
    risco_eventos: List[Dict]
    oportunidade_eventos: List[Dict]
    timing_saida: Dict
    ajustes_pre_evento: Dict

class AnalisadorTimingEventos:
    """Analisa timing baseado em eventos econômicos."""

    def __init__(self, caminho_portfolio: str = "backend/data/portfolio/portfolio_atual.json"):
        self.caminho_portfolio = caminho_portfolio
        self.eventos_proximos = self._carregar_calendario_economico()

    def _carregar_calendario_economico(self) -> List[EventoEconomico]:
        """Carrega eventos econômicos das próximas 48h."""
        # Baseado nos dados coletados dos calendários
        eventos = [
            # Sexta-feira 7 Nov 2025
            EventoEconomico(
                timestamp=datetime(2025, 11, 7, 0, 1),  # 12:01am GMT
                moeda="CNY",
                titulo="China Trade Balance",
                impacto="MODERATE",
                expectativa=640.0,
                anterior=90.1
            ),
            EventoEconomico(
                timestamp=datetime(2025, 11, 7, 4, 0),  # 4:00am GMT
                moeda="EUR",
                titulo="German Trade Balance",
                impacto="MODERATE"
            ),
            EventoEconomico(
                timestamp=datetime(2025, 11, 7, 4, 45),  # 4:45am GMT
                moeda="EUR",
                titulo="French Trade Balance",
                impacto="LOW"
            ),
            EventoEconomico(
                timestamp=datetime(2025, 11, 7, 10, 30),  # 10:30am GMT
                moeda="CAD",
                titulo="Canada Employment Change & Unemployment",
                impacto="HIGH"
            ),
            EventoEconomico(
                timestamp=datetime(2025, 11, 7, 12, 0),  # 12:00pm GMT
                moeda="USD",
                titulo="US Prelim UoM Consumer Sentiment",
                impacto="MODERATE"
            ),
            EventoEconomico(
                timestamp=datetime(2025, 11, 7, 12, 15),  # 12:15pm GMT
                moeda="GBP",
                titulo="UK MPC Member Pill Speaks",
                impacto="MODERATE"
            ),
            EventoEconomico(
                timestamp=datetime(2025, 11, 7, 17, 0),  # 5:00pm GMT
                moeda="USD",
                titulo="US Consumer Credit",
                impacto="LOW"
            ),
        ]
        return eventos

    def analisar_portfolio_completo(self) -> Dict[str, Any]:
        """Analisa todas as posições abertas do portfólio."""
        print("🔍 Analisando timing baseado em eventos para o portfólio...")

        # Carregar posições abertas
        portfolio = self._carregar_portfolio()
        posicoes_abertas = [p for p in portfolio.get('positions', []) if p.get('status') == 'OPEN']

        analises = []
        for posicao in posicoes_abertas:
            analise = self._analisar_posicao(posicao)
            analises.append(analise)

        resultado = {
            "timestamp_analise": datetime.now().isoformat(),
            "periodo_cobertura": "48h",
            "total_posicoes_analisadas": len(analises),
            "eventos_monitorados": len(self.eventos_proximos),
            "analises_posicoes": [self._converter_para_dict(a) for a in analises],
            "resumo_riscos": self._gerar_resumo_riscos(analises),
            "recomendacoes_gerais": self._gerar_recomendacoes_gerais(analises)
        }

        self._persistir_analise(resultado)
        return resultado

    def _carregar_portfolio(self) -> Dict:
        """Carrega dados do portfólio."""
        try:
            with open(self.caminho_portfolio, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar portfólio: {e}")
            return {}

    def _analisar_posicao(self, posicao: Dict) -> AnalisePosicao:
        """Analisa uma posição específica."""
        par = posicao['currency_pair']
        direcao = posicao['direction']
        position_id = posicao['position_id']

        # Identificar moedas envolvidas
        moedas_posicao = self._extrair_moedas_par(par)

        # Filtrar eventos relevantes
        eventos_relevantes = [
            e for e in self.eventos_proximos
            if any(moeda in e.moeda for moeda in moedas_posicao)
        ]

        # Analisar riscos
        risco_eventos = self._analisar_riscos_eventos(eventos_relevantes, par, direcao)

        # Analisar oportunidades
        oportunidade_eventos = self._analisar_oportunidades_eventos(eventos_relevantes, par, direcao)

        # Timing de saída
        timing_saida = self._calcular_timing_saida(eventos_relevantes, posicao)

        # Ajustes pré-evento
        ajustes_pre_evento = self._calcular_ajustes_pre_evento(eventos_relevantes, posicao)

        return AnalisePosicao(
            position_id=position_id,
            par=par,
            direcao=direcao,
            risco_eventos=risco_eventos,
            oportunidade_eventos=oportunidade_eventos,
            timing_saida=timing_saida,
            ajustes_pre_evento=ajustes_pre_evento
        )

    def _extrair_moedas_par(self, par: str) -> List[str]:
        """Extrai as moedas de um par de moedas."""
        if par in ['GC=F', 'SI=F']:  # Commodities
            return ['USD', 'XAU', 'XAG']
        elif '/' in par:
            return par.split('/')
        else:
            return [par]

    def _analisar_riscos_eventos(self, eventos: List[EventoEconomico], par: str, direcao: str) -> List[Dict]:
        """Analisa riscos de eventos para a posição."""
        riscos = []

        for evento in eventos:
            risco = self._calcular_risco_evento(evento, par, direcao)
            if risco['nivel_risco'] > 0:
                riscos.append(risco)

        return sorted(riscos, key=lambda x: x['nivel_risco'], reverse=True)

    def _calcular_risco_evento(self, evento: EventoEconomico, par: str, direcao: str) -> Dict:
        """Calcula o nível de risco de um evento para a posição."""
        moedas_posicao = self._extrair_moedas_par(par)

        # Base de risco por moeda
        risco_base = {
            'USD': 8, 'EUR': 7, 'GBP': 6, 'JPY': 5, 'CHF': 4, 'CAD': 3, 'CNY': 2
        }

        # Multiplicador por impacto
        impacto_mult = {
            'HIGH': 3.0, 'MODERATE': 2.0, 'LOW': 1.0
        }

        # Calcular risco base
        risco_moeda = max([risco_base.get(m, 1) for m in moedas_posicao if m in evento.moeda], default=1)
        risco_impacto = impacto_mult.get(evento.impacto, 1.0)

        nivel_risco = min(risco_moeda * risco_impacto, 10)  # Máximo 10

        # Ajustes específicos por tipo de evento e direção
        if evento.titulo.lower().find('trade balance') >= 0:
            if 'JPY' in par and direcao == 'LONG':
                nivel_risco *= 1.3  # Carry trade sensível a dados China

        elif evento.titulo.lower().find('employment') >= 0:
            if 'USD' in par:
                nivel_risco *= 1.2  # Emprego EUA afeta USD

        elif evento.titulo.lower().find('consumer sentiment') >= 0:
            if 'USD' in par:
                nivel_risco *= 1.1

        return {
            'evento': evento.titulo,
            'timestamp': evento.timestamp.isoformat(),
            'moeda': evento.moeda,
            'impacto': evento.impacto,
            'nivel_risco': round(nivel_risco, 1),
            'justificativa': self._gerar_justificativa_risco(evento, par, direcao, nivel_risco),
            'recomendacao': self._gerar_recomendacao_risco(nivel_risco)
        }

    def _gerar_justificativa_risco(self, evento: EventoEconomico, par: str, direcao: str, nivel_risco: float) -> str:
        """Gera justificativa para o nível de risco."""
        justificativas = []

        if evento.impacto == 'HIGH':
            justificativas.append("Evento de alto impacto pode causar volatilidade extrema")

        if any(m in evento.moeda for m in self._extrair_moedas_par(par)):
            justificativas.append(f"Evento afeta diretamente {evento.moeda} no par {par}")

        if nivel_risco > 7:
            justificativas.append("Risco crítico - considerar saída parcial")
        elif nivel_risco > 5:
            justificativas.append("Risco elevado - monitorar closely")
        elif nivel_risco > 3:
            justificativas.append("Risco moderado - manter stop loss")

        return "; ".join(justificativas)

    def _gerar_recomendacao_risco(self, nivel_risco: float) -> str:
        """Gera recomendação baseada no nível de risco."""
        if nivel_risco >= 8:
            return "SAÍDA IMEDIATA - Risco crítico"
        elif nivel_risco >= 6:
            return "REDUZIR POSIÇÃO - Alto risco"
        elif nivel_risco >= 4:
            return "TIGHTEN STOP - Risco moderado"
        elif nivel_risco >= 2:
            return "MONITORAR - Baixo risco"
        else:
            return "MANTER - Risco mínimo"

    def _analisar_oportunidades_eventos(self, eventos: List[EventoEconomico], par: str, direcao: str) -> List[Dict]:
        """Analisa oportunidades de aceleração favorável."""
        oportunidades = []

        for evento in eventos:
            oportunidade = self._calcular_oportunidade_evento(evento, par, direcao)
            if oportunidade['potencial_aceleracao'] > 0:
                oportunidades.append(oportunidade)

        return sorted(oportunidades, key=lambda x: x['potencial_aceleracao'], reverse=True)

    def _calcular_oportunidade_evento(self, evento: EventoEconomico, par: str, direcao: str) -> Dict:
        """Calcula potencial de oportunidade de um evento."""
        moedas_posicao = self._extrair_moedas_par(par)

        # Eventos que podem acelerar movimento favorável
        eventos_favoraveis = {
            'trade balance': {'JPY': 2.0 if direcao == 'LONG' else 0.5},
            'employment': {'USD': 1.5 if direcao == 'LONG' else 0.8},
            'consumer sentiment': {'USD': 1.3 if direcao == 'LONG' else 0.7},
            'speaks': {'GBP': 1.2, 'EUR': 1.1}
        }

        potencial = 0
        for tipo_evento, multiplicadores in eventos_favoraveis.items():
            if tipo_evento in evento.titulo.lower():
                for moeda in moedas_posicao:
                    if moeda in multiplicadores:
                        potencial += multiplicadores[moeda]

        # Ajustar por impacto do evento
        if evento.impacto == 'HIGH':
            potencial *= 1.5
        elif evento.impacto == 'MODERATE':
            potencial *= 1.2

        return {
            'evento': evento.titulo,
            'timestamp': evento.timestamp.isoformat(),
            'moeda': evento.moeda,
            'potencial_aceleracao': round(potencial, 1),
            'cenarios_favoraveis': self._identificar_cenarios_favoraveis(evento, par, direcao),
            'timing_otimo': self._calcular_timing_otimo(evento)
        }

    def _identificar_cenarios_favoraveis(self, evento: EventoEconomico, par: str, direcao: str) -> List[str]:
        """Identifica cenários que podem acelerar movimento favorável."""
        cenarios = []

        if 'trade balance' in evento.titulo.lower():
            if 'JPY' in par and direcao == 'LONG':
                cenarios.append("Surpresa positiva no balanço comercial chinês pode acelerar apreciação JPY")

        if 'employment' in evento.titulo.lower():
            if 'USD' in par and direcao == 'LONG':
                cenarios.append("Dados de emprego canadense acima do esperado podem fortalecer CAD")

        if 'consumer sentiment' in evento.titulo.lower():
            if 'USD' in par:
                cenarios.append("Sentimento do consumidor EUA melhor que esperado pode beneficiar USD")

        if 'speaks' in evento.titulo.lower():
            cenarios.append("Comentários dovish do MPC podem beneficiar GBP no carry trade")

        return cenarios

    def _calcular_timing_otimo(self, evento: EventoEconomico) -> str:
        """Calcula timing ótimo para entrada/saída em torno do evento."""
        # Timing baseado no horário do evento
        hora = evento.timestamp.hour

        if 0 <= hora < 6:  # Madrugada (GMT)
            return "Pré-evento: 30min antes; Pós-evento: 2h após"
        elif 6 <= hora < 12:  # Manhã
            return "Pré-evento: 1h antes; Pós-evento: 3h após"
        elif 12 <= hora < 18:  # Tarde
            return "Pré-evento: 2h antes; Pós-evento: 4h após"
        else:  # Noite
            return "Pré-evento: 1h antes; Pós-evento: 2h após"

    def _calcular_timing_saida(self, eventos: List[EventoEconomico], posicao: Dict) -> Dict:
        """Calcula janelas ótimas de saída baseadas em eventos."""
        eventos_risco = [e for e in eventos if e.impacto in ['HIGH', 'MODERATE']]

        if not eventos_risco:
            return {
                'janela_otima': 'Sem eventos críticos próximos',
                'recomendacao': 'Manter posição até targets técnicos'
            }

        # Encontrar evento de maior risco
        evento_critico = min(eventos_risco, key=lambda x: x.timestamp)

        horas_ate_evento = (evento_critico.timestamp - datetime.now()).total_seconds() / 3600

        if horas_ate_evento < 2:
            return {
                'janela_otima': 'IMEDIATA - Antes do evento crítico',
                'recomendacao': 'Considerar saída parcial ou total',
                'evento_critico': evento_critico.titulo,
                'horas_restantes': round(horas_ate_evento, 1)
            }
        elif horas_ate_evento < 6:
            return {
                'janela_otima': 'Próximas 2h - Antes do evento',
                'recomendacao': 'Preparar saída parcial',
                'evento_critico': evento_critico.titulo,
                'horas_restantes': round(horas_ate_evento, 1)
            }
        else:
            return {
                'janela_otima': f'Dentro de {round(horas_ate_evento)}h - Antes do evento',
                'recomendacao': 'Manter posição, monitorar',
                'evento_critico': evento_critico.titulo,
                'horas_restantes': round(horas_ate_evento, 1)
            }

    def _calcular_ajustes_pre_evento(self, eventos: List[EventoEconomico], posicao: Dict) -> Dict:
        """Calcula ajustes recomendados no tamanho da posição pré-evento."""
        eventos_alto_risco = [e for e in eventos if e.impacto == 'HIGH']
        eventos_moderado_risco = [e for e in eventos if e.impacto == 'MODERATE']

        risco_total = len(eventos_alto_risco) * 3 + len(eventos_moderado_risco) * 2

        if risco_total >= 6:
            return {
                'ajuste_recomendado': 'REDUZIR 50%',
                'justificativa': f'Múltiplos eventos de risco ({risco_total} pontos)',
                'acao_imediata': 'Implementar stop loss mais apertado'
            }
        elif risco_total >= 4:
            return {
                'ajuste_recomendado': 'REDUZIR 25%',
                'justificativa': f'Eventos moderados de risco ({risco_total} pontos)',
                'acao_imediata': 'Aumentar monitoramento'
            }
        elif risco_total >= 2:
            return {
                'ajuste_recomendado': 'MANTER',
                'justificativa': f'Eventos isolados de risco ({risco_total} pontos)',
                'acao_imediata': 'Confirmar stops em posição'
            }
        else:
            return {
                'ajuste_recomendado': 'MANTER',
                'justificativa': 'Baixo risco de eventos próximos',
                'acao_imediata': 'Continuar estratégia normal'
            }

    def _converter_para_dict(self, analise: AnalisePosicao) -> Dict:
        """Converte AnalisePosicao para dicionário."""
        return {
            'position_id': analise.position_id,
            'par': analise.par,
            'direcao': analise.direcao,
            'risco_eventos': analise.risco_eventos,
            'oportunidade_eventos': analise.oportunidade_eventos,
            'timing_saida': analise.timing_saida,
            'ajustes_pre_evento': analise.ajustes_pre_evento
        }

    def _gerar_resumo_riscos(self, analises: List[AnalisePosicao]) -> Dict:
        """Gera resumo geral dos riscos."""
        total_riscos = sum(len(a.risco_eventos) for a in analises)
        riscos_criticos = sum(
            len([r for r in a.risco_eventos if r['nivel_risco'] >= 8])
            for a in analises
        )

        return {
            'total_riscos_identificados': total_riscos,
            'riscos_criticos': riscos_criticos,
            'posicoes_em_risco': len([a for a in analises if a.risco_eventos]),
            'recomendacao_geral': 'REDUZIR EXPOSIÇÃO' if riscos_criticos > 0 else 'MONITORAR'
        }

    def _gerar_recomendacoes_gerais(self, analises: List[AnalisePosicao]) -> List[str]:
        """Gera recomendações gerais baseadas em todas as análises."""
        recomendacoes = []

        # Verificar se há muitos riscos
        riscos_altos = sum(len([r for r in a.risco_eventos if r['nivel_risco'] >= 6]) for a in analises)
        if riscos_altos > 3:
            recomendacoes.append("🔴 REDUZIR POSIÇÕES - Múltiplos eventos de alto risco próximos")

        # Verificar oportunidades
        oportunidades = sum(len(a.oportunidade_eventos) for a in analises)
        if oportunidades > 0:
            recomendacoes.append("🟢 MONITORAR OPORTUNIDADES - Eventos podem acelerar movimentos favoráveis")

        # Timing geral
        eventos_proximos = [e for e in self.eventos_proximos if e.impacto in ['HIGH', 'MODERATE']]
        if eventos_proximos:
            proximo_evento = min(eventos_proximos, key=lambda x: x.timestamp)
            horas = (proximo_evento.timestamp - datetime.now()).total_seconds() / 3600
            recomendacoes.append(f"⏰ PRÓXIMO EVENTO CRÍTICO: {proximo_evento.titulo} em {horas:.1f}h")

        return recomendacoes

    def _persistir_analise(self, resultado: Dict) -> None:
        """Persiste o resultado da análise."""
        import os
        os.makedirs("backend/data/timing_eventos", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"backend/data/timing_eventos/analise_timing_{timestamp}.json"

        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)

        print(f"💾 Análise salva em: {nome_arquivo}")

def main():
    """Função principal."""
    print("🎯 ANALISADOR DE TIMING BASEADO EM EVENTOS")
    print("=" * 50)

    analisador = AnalisadorTimingEventos()

    try:
        resultado = analisador.analisar_portfolio_completo()

        print("\n📊 RESUMO DA ANÁLISE:")
        print(f"Posições analisadas: {resultado['total_posicoes_analisadas']}")
        print(f"Eventos monitorados: {resultado['eventos_monitorados']}")
        print(f"Riscos identificados: {resultado['resumo_riscos']['total_riscos_identificados']}")
        print(f"Riscos críticos: {resultado['resumo_riscos']['riscos_criticos']}")

        print("\n🔴 RECOMENDAÇÕES GERAIS:")
        for rec in resultado.get('recomendacoes_gerais', []):
            print(f"• {rec}")

        print("\n✅ Análise concluída com sucesso!")
        return 0

    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return 1

if __name__ == "__main__":
    exit(main())