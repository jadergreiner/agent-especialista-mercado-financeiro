"""
Sistema de Alertas Inteligentes
Geração Automatizada de Alertas com Learning Adaptativo

Funcionalidades:
1. Alertas automáticos baseados em oportunidades detectadas
2. Sistema de scoring dinâmico baseado em performance passada
3. Personalização de alertas por assertividade
4. Integração com sistema de tracking para feedback contínuo
5. Motor de recomendações adaptativo
6. Persistência e histórico de alertas
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import logging
from enum import Enum

class TipoAlerta(Enum):
    OPORTUNIDADE_ALTA = "OPORTUNIDADE_ALTA"
    OPORTUNIDADE_MEDIA = "OPORTUNIDADE_MEDIA"
    TAKE_PROFIT = "TAKE_PROFIT"
    MONITORAMENTO = "MONITORAMENTO"
    WARNING = "WARNING"

class StatusAlerta(Enum):
    ATIVO = "ATIVO"
    EXECUTADO = "EXECUTADO"
    EXPIRADO = "EXPIRADO"
    CANCELADO = "CANCELADO"

@dataclass
class AlertaInteligente:
    """Estrutura de um alerta inteligente"""
    id_alerta: str
    tipo: TipoAlerta
    par: str
    prioridade: int  # 1-5 (5 = mais importante)
    probabilidade_sucesso: float
    score_confianca: str
    recomendacao: Dict
    dados_posicao: Dict
    contexto_macro: Dict
    timestamp_criacao: str
    validade_horas: int
    status: StatusAlerta = StatusAlerta.ATIVO
    feedback_usuario: Optional[str] = None
    resultado_real: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return asdict(self)

class SistemaAlertasInteligentes:
    """Sistema principal de alertas com aprendizado adaptativo"""

    def __init__(self):
        self.logger = self._configurar_logger()
        self.caminho_alertas = "data/alertas"
        self.caminho_configuracao = "data/config_alertas"

        # Criar diretórios
        os.makedirs(self.caminho_alertas, exist_ok=True)
        os.makedirs(self.caminho_configuracao, exist_ok=True)

        # Configurações adaptativas (aprendidas automaticamente)
        self.config_dinamica = self._carregar_configuracao_dinamica()

        # Limites adaptativos
        self.threshold_probabilidade_minima = self.config_dinamica.get('threshold_prob', 0.6)
        self.max_alertas_por_hora = self.config_dinamica.get('max_alertas_hora', 5)
        self.score_historico_performance = self.config_dinamica.get('score_performance', 0.7)

        # Cache de alertas ativos
        self.alertas_ativos = []

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('AlertasInteligentes')
        logger.setLevel(logging.INFO)
        return logger

    def _carregar_configuracao_dinamica(self) -> Dict:
        """Carregar configuração dinâmica baseada em aprendizado"""
        arquivo_config = os.path.join(self.caminho_configuracao, "config_dinamica.json")

        # Configuração padrão
        config_padrao = {
            'threshold_prob': 0.6,
            'max_alertas_hora': 5,
            'score_performance': 0.7,
            'pesos_por_confianca': {
                'MUITO_ALTA': 1.0,
                'ALTA': 0.8,
                'MEDIA': 0.6,
                'BAIXA': 0.3
            },
            'validade_por_tipo': {
                'OPORTUNIDADE_ALTA': 6,  # horas
                'OPORTUNIDADE_MEDIA': 12,
                'TAKE_PROFIT': 2,
                'MONITORAMENTO': 24,
                'WARNING': 4
            }
        }

        if os.path.exists(arquivo_config):
            try:
                with open(arquivo_config, 'r', encoding='utf-8') as f:
                    config_salva = json.load(f)
                    config_padrao.update(config_salva)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar config dinâmica: {e}")

        return config_padrao

    def processar_oportunidades_para_alertas(self, oportunidades: List[Dict]) -> List[AlertaInteligente]:
        """Processar oportunidades detectadas e gerar alertas inteligentes"""
        try:
            alertas_gerados = []

            if not oportunidades:
                return alertas_gerados

            # Filtrar e ranquear oportunidades
            oportunidades_validas = self._filtrar_oportunidades_validas(oportunidades)
            oportunidades_ranqueadas = self._ranquear_oportunidades(oportunidades_validas)

            # Aplicar limite de alertas por hora
            limite_atual = self._calcular_limite_dinamico()
            oportunidades_selecionadas = oportunidades_ranqueadas[:limite_atual]

            # Gerar alertas para oportunidades selecionadas
            for i, op in enumerate(oportunidades_selecionadas):
                alerta = self._criar_alerta_da_oportunidade(op, i + 1)
                alertas_gerados.append(alerta)

            # Salvar alertas
            self._salvar_alertas(alertas_gerados)

            # Atualizar cache
            self.alertas_ativos.extend(alertas_gerados)

            self.logger.info(f"Gerados {len(alertas_gerados)} alertas de {len(oportunidades)} oportunidades")

            return alertas_gerados

        except Exception as e:
            self.logger.error(f"Erro ao processar oportunidades: {e}")
            return []

    def _filtrar_oportunidades_validas(self, oportunidades: List[Dict]) -> List[Dict]:
        """Filtrar oportunidades com base em critérios adaptativos"""
        oportunidades_validas = []

        for op in oportunidades:
            # Critério 1: Probabilidade mínima
            prob = op.get('probabilidade_sucesso', 0)
            if prob < self.threshold_probabilidade_minima:
                continue

            # Critério 2: Score de confiança
            confianca = op.get('score_confianca', 'BAIXA')
            peso_confianca = self.config_dinamica['pesos_por_confianca'].get(confianca, 0)

            if peso_confianca < 0.5:
                continue

            # Critério 3: Não duplicar alertas recentes para mesmo par
            par = op.get('par', '')
            if self._tem_alerta_recente_para_par(par):
                continue

            # Critério 4: Validação de dados mínimos
            if not self._validar_dados_minimos(op):
                continue

            oportunidades_validas.append(op)

        return oportunidades_validas

    def _ranquear_oportunidades(self, oportunidades: List[Dict]) -> List[Dict]:
        """Ranquear oportunidades por prioridade inteligente"""

        def calcular_score_prioridade(op: Dict) -> float:
            """Calcular score de prioridade para uma oportunidade"""
            score = 0.0

            # Peso 1: Probabilidade de sucesso (40%)
            prob = op.get('probabilidade_sucesso', 0)
            score += prob * 0.4

            # Peso 2: Confiança histórica do modelo (30%)
            confianca = op.get('score_confianca', 'BAIXA')
            peso_confianca = self.config_dinamica['pesos_por_confianca'].get(confianca, 0)
            score += peso_confianca * 0.3

            # Peso 3: Performance histórica da recomendação (20%)
            acao = op.get('recomendacao', {}).get('acao', '')
            score_historico = self._obter_score_historico_acao(acao)
            score += score_historico * 0.2

            # Peso 4: Urgência temporal (10%)
            urgencia = self._calcular_urgencia_temporal(op)
            score += urgencia * 0.1

            return min(score, 1.0)  # Normalizar para max 1.0

        # Calcular scores e ordenar
        for op in oportunidades:
            op['score_prioridade'] = calcular_score_prioridade(op)

        return sorted(oportunidades, key=lambda x: x['score_prioridade'], reverse=True)

    def _tem_alerta_recente_para_par(self, par: str, horas_limite: int = 6) -> bool:
        """Verificar se já existe alerta recente para o par"""
        agora = datetime.now()
        limite_tempo = agora - timedelta(hours=horas_limite)

        for alerta in self.alertas_ativos:
            if alerta.par == par and alerta.status == StatusAlerta.ATIVO:
                timestamp_alerta = datetime.fromisoformat(alerta.timestamp_criacao)
                if timestamp_alerta > limite_tempo:
                    return True

        return False

    def _validar_dados_minimos(self, oportunidade: Dict) -> bool:
        """Validar se oportunidade tem dados mínimos necessários"""
        campos_obrigatorios = [
            'par', 'probabilidade_sucesso', 'score_confianca',
            'recomendacao', 'dados_posicao'
        ]

        for campo in campos_obrigatorios:
            if campo not in oportunidade or oportunidade[campo] is None:
                return False

        # Validar estrutura da recomendação
        rec = oportunidade.get('recomendacao', {})
        if 'acao' not in rec or 'justificativa' not in rec:
            return False

        return True

    def _obter_score_historico_acao(self, acao: str) -> float:
        """Obter score histórico de performance para uma ação específica"""
        # Simulação - em implementação real, consultaria métricas históricas
        scores_default = {
            'MANTER_POSICAO': 0.75,
            'CONSIDERAR_TAKE_PROFIT': 0.65,
            'MONITORAR_PROXIMAMENTE': 0.55,
            'AGUARDAR_CONFIRMACAO': 0.45
        }

        return scores_default.get(acao, 0.5)

    def _calcular_urgencia_temporal(self, oportunidade: Dict) -> float:
        """Calcular urgência baseada em fatores temporais"""
        urgencia = 0.5  # Base

        # Fator 1: Proximidade de eventos macro
        contexto_macro = oportunidade.get('contexto_macro', {})
        if contexto_macro.get('evento_iminente'):
            urgencia += 0.3

        # Fator 2: Volatilidade atual
        dados_posicao = oportunidade.get('dados_posicao', {})
        volatilidade = dados_posicao.get('volatilidade_atual', 0)
        if volatilidade > 0.02:  # >2% diário
            urgencia += 0.2

        return min(urgencia, 1.0)

    def _calcular_limite_dinamico(self) -> int:
        """Calcular limite dinâmico de alertas baseado em performance"""
        limite_base = self.max_alertas_por_hora

        # Ajustar baseado na performance recente
        if self.score_historico_performance > 0.8:
            return limite_base + 2  # Aumentar se performance boa
        elif self.score_historico_performance < 0.6:
            return max(2, limite_base - 2)  # Diminuir se performance ruim

        return limite_base

    def _criar_alerta_da_oportunidade(self, oportunidade: Dict, prioridade: int) -> AlertaInteligente:
        """Criar alerta estruturado a partir de oportunidade"""

        # Determinar tipo de alerta
        prob = oportunidade.get('probabilidade_sucesso', 0)
        confianca = oportunidade.get('score_confianca', 'BAIXA')

        if prob >= 0.8 and confianca in ['MUITO_ALTA', 'ALTA']:
            tipo_alerta = TipoAlerta.OPORTUNIDADE_ALTA
        elif prob >= 0.65:
            tipo_alerta = TipoAlerta.OPORTUNIDADE_MEDIA
        elif oportunidade.get('recomendacao', {}).get('acao') == 'CONSIDERAR_TAKE_PROFIT':
            tipo_alerta = TipoAlerta.TAKE_PROFIT
        else:
            tipo_alerta = TipoAlerta.MONITORAMENTO

        # Gerar ID único
        timestamp = datetime.now()
        id_alerta = f"{oportunidade['par']}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{prioridade}"

        # Determinar validade
        validade = self.config_dinamica['validade_por_tipo'][tipo_alerta.value]

        return AlertaInteligente(
            id_alerta=id_alerta,
            tipo=tipo_alerta,
            par=oportunidade['par'],
            prioridade=prioridade,
            probabilidade_sucesso=prob,
            score_confianca=confianca,
            recomendacao=oportunidade['recomendacao'],
            dados_posicao=oportunidade['dados_posicao'],
            contexto_macro=oportunidade.get('contexto_macro', {}),
            timestamp_criacao=timestamp.isoformat(),
            validade_horas=validade
        )

    def _salvar_alertas(self, alertas: List[AlertaInteligente]):
        """Salvar alertas gerados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"alertas_{timestamp}.json"
        caminho = os.path.join(self.caminho_alertas, arquivo)

        dados_alertas = {
            'timestamp_geracao': datetime.now().isoformat(),
            'total_alertas': len(alertas),
            'alertas': [alerta.to_dict() for alerta in alertas]
        }

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados_alertas, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Alertas salvos: {caminho}")

    def atualizar_configuracao_com_feedback(self, metricas_performance: Dict):
        """Atualizar configuração dinâmica baseada em performance"""
        try:
            resumo = metricas_performance.get('resumo_geral', {})
            taxa_acerto = resumo.get('taxa_acerto_geral', 0) / 100

            # Ajustar threshold de probabilidade
            if taxa_acerto < 0.6:
                # Performance ruim - aumentar threshold
                self.config_dinamica['threshold_prob'] = min(0.8,
                    self.config_dinamica['threshold_prob'] + 0.05)
            elif taxa_acerto > 0.8:
                # Performance boa - relaxar threshold
                self.config_dinamica['threshold_prob'] = max(0.5,
                    self.config_dinamica['threshold_prob'] - 0.02)

            # Ajustar pesos por confiança baseado em performance real
            analise_confianca = metricas_performance.get('analise_por_confianca', {})

            for nivel, dados in analise_confianca.items():
                taxa_nivel = dados.get('taxa_acerto', 0) / 100
                peso_atual = self.config_dinamica['pesos_por_confianca'].get(nivel, 0.5)

                # Ajustar peso baseado na performance real
                novo_peso = (peso_atual * 0.7) + (taxa_nivel * 0.3)
                self.config_dinamica['pesos_por_confianca'][nivel] = min(1.0, max(0.1, novo_peso))

            # Atualizar score de performance
            self.config_dinamica['score_performance'] = taxa_acerto

            # Salvar configuração atualizada
            self._salvar_configuracao_dinamica()

            self.logger.info("Configuração dinâmica atualizada com feedback de performance")

        except Exception as e:
            self.logger.error(f"Erro ao atualizar configuração: {e}")

    def _salvar_configuracao_dinamica(self):
        """Salvar configuração dinâmica atualizada"""
        arquivo_config = os.path.join(self.caminho_configuracao, "config_dinamica.json")

        with open(arquivo_config, 'w', encoding='utf-8') as f:
            json.dump(self.config_dinamica, f, indent=2, ensure_ascii=False)

    def obter_alertas_ativos(self) -> List[AlertaInteligente]:
        """Obter lista de alertas ainda ativos"""
        agora = datetime.now()
        alertas_validos = []

        for alerta in self.alertas_ativos:
            if alerta.status != StatusAlerta.ATIVO:
                continue

            # Verificar se ainda está válido
            timestamp_criacao = datetime.fromisoformat(alerta.timestamp_criacao)
            tempo_decorrido = (agora - timestamp_criacao).total_seconds() / 3600

            if tempo_decorrido < alerta.validade_horas:
                alertas_validos.append(alerta)
            else:
                # Marcar como expirado
                alerta.status = StatusAlerta.EXPIRADO

        return alertas_validos

    def processar_feedback_alerta(self, id_alerta: str, feedback: str, resultado: Optional[Dict] = None):
        """Processar feedback do usuário sobre um alerta"""
        try:
            # Encontrar alerta
            alerta_encontrado = None
            for alerta in self.alertas_ativos:
                if alerta.id_alerta == id_alerta:
                    alerta_encontrado = alerta
                    break

            if not alerta_encontrado:
                return {'erro': 'Alerta não encontrado'}

            # Atualizar feedback
            alerta_encontrado.feedback_usuario = feedback
            alerta_encontrado.resultado_real = resultado
            alerta_encontrado.status = StatusAlerta.EXECUTADO

            # Salvar feedback
            self._salvar_feedback_alerta(alerta_encontrado)

            return {'sucesso': 'Feedback registrado'}

        except Exception as e:
            self.logger.error(f"Erro ao processar feedback: {e}")
            return {'erro': str(e)}

    def _salvar_feedback_alerta(self, alerta: AlertaInteligente):
        """Salvar feedback de alerta para aprendizado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"feedback_{alerta.id_alerta}_{timestamp}.json"
        caminho = os.path.join(self.caminho_alertas, "feedback", arquivo)

        os.makedirs(os.path.dirname(caminho), exist_ok=True)

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(alerta.to_dict(), f, indent=2, ensure_ascii=False)

    def gerar_relatorio_alertas(self) -> Dict:
        """Gerar relatório de performance dos alertas"""
        try:
            alertas_ativos = self.obter_alertas_ativos()

            # Análise por tipo
            analise_por_tipo = {}
            for tipo in TipoAlerta:
                alertas_tipo = [a for a in self.alertas_ativos if a.tipo == tipo]
                analise_por_tipo[tipo.value] = {
                    'total': len(alertas_tipo),
                    'ativos': len([a for a in alertas_tipo if a.status == StatusAlerta.ATIVO]),
                    'executados': len([a for a in alertas_tipo if a.status == StatusAlerta.EXECUTADO]),
                    'expirados': len([a for a in alertas_tipo if a.status == StatusAlerta.EXPIRADO])
                }

            relatorio = {
                'resumo_geral': {
                    'total_alertas_gerados': len(self.alertas_ativos),
                    'alertas_ativos': len(alertas_ativos),
                    'taxa_execucao': self._calcular_taxa_execucao()
                },
                'analise_por_tipo': analise_por_tipo,
                'configuracao_atual': self.config_dinamica,
                'timestamp_relatorio': datetime.now().isoformat()
            }

            return relatorio

        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório: {e}")
            return {'erro': str(e)}

    def _calcular_taxa_execucao(self) -> float:
        """Calcular taxa de execução dos alertas"""
        if not self.alertas_ativos:
            return 0.0

        executados = len([a for a in self.alertas_ativos if a.status == StatusAlerta.EXECUTADO])
        return (executados / len(self.alertas_ativos)) * 100


def main():
    """Demonstração do sistema de alertas inteligentes"""
    print("🚨 SISTEMA DE ALERTAS INTELIGENTES")
    print("=" * 60)

    # Inicializar sistema
    sistema_alertas = SistemaAlertasInteligentes()

    # Simular oportunidades detectadas
    oportunidades_exemplo = [
        {
            'par': 'EUR/USD',
            'probabilidade_sucesso': 0.85,
            'score_confianca': 'MUITO_ALTA',
            'recomendacao': {
                'acao': 'MANTER_POSICAO',
                'justificativa': 'Confluência técnica e macro favorável'
            },
            'dados_posicao': {
                'current_price': 1.0950,
                'direction': 'LONG',
                'volatilidade_atual': 0.015
            },
            'contexto_macro': {
                'evento_iminente': True,
                'dxy_trend': 'BEARISH'
            }
        },
        {
            'par': 'GBP/JPY',
            'probabilidade_sucesso': 0.72,
            'score_confianca': 'ALTA',
            'recomendacao': {
                'acao': 'CONSIDERAR_TAKE_PROFIT',
                'justificativa': 'Resistência técnica próxima'
            },
            'dados_posicao': {
                'current_price': 195.50,
                'direction': 'LONG',
                'volatilidade_atual': 0.025
            },
            'contexto_macro': {
                'evento_iminente': False,
                'carry_trade_favoravel': True
            }
        }
    ]

    print(f"\n📊 PROCESSANDO {len(oportunidades_exemplo)} OPORTUNIDADES...")

    # Processar oportunidades para alertas
    alertas_gerados = sistema_alertas.processar_oportunidades_para_alertas(oportunidades_exemplo)

    print(f"🚨 ALERTAS GERADOS: {len(alertas_gerados)}")

    # Mostrar alertas
    for i, alerta in enumerate(alertas_gerados, 1):
        print(f"\n   📌 ALERTA #{i}")
        print(f"      Tipo: {alerta.tipo.value}")
        print(f"      Par: {alerta.par}")
        print(f"      Prioridade: {alerta.prioridade}")
        print(f"      Probabilidade: {alerta.probabilidade_sucesso:.1%}")
        print(f"      Confiança: {alerta.score_confianca}")
        print(f"      Ação: {alerta.recomendacao['acao']}")
        print(f"      Validade: {alerta.validade_horas}h")

    # Gerar relatório
    print(f"\n📈 RELATÓRIO DE PERFORMANCE...")
    relatorio = sistema_alertas.gerar_relatorio_alertas()

    if 'erro' not in relatorio:
        resumo = relatorio['resumo_geral']
        print(f"   📊 Total de alertas: {resumo['total_alertas_gerados']}")
        print(f"   ✅ Alertas ativos: {resumo['alertas_ativos']}")
        print(f"   📈 Taxa de execução: {resumo['taxa_execucao']:.1f}%")

        print(f"\n🔧 CONFIGURAÇÃO ADAPTATIVA:")
        config = relatorio['configuracao_atual']
        print(f"   🎯 Threshold probabilidade: {config['threshold_prob']:.1%}")
        print(f"   📊 Score performance: {config['score_performance']:.1%}")
        print(f"   📨 Max alertas/hora: {config['max_alertas_hora']}")

    print(f"\n✅ SISTEMA DE ALERTAS OPERACIONAL")
    print("🔄 Aprendizado contínuo ativo - configuração auto-ajustável")

    return sistema_alertas, alertas_gerados, relatorio


if __name__ == "__main__":
    sistema, alertas, relatorio = main()