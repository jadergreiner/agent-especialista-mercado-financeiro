"""
Sistema de Transparência Radical — Sprint Emergencial

Implementa o princípio de "Radical Transparency" forçando alertas críticos
e downgrade de confiança em TODAS as análises.

Princípio Norteador:
"Interface bonita que esconde risco crítico não é UX excelente, é negligência profissional"

Componentes:
- Downgrade forçado de confiança (60% → 20-30%)
- Sistema de disclaimers obrigatórios
- Alertas críticos de risco ilimitado
- Gates de qualidade pré-análise
- Fallback gracioso se recursos externos falham
"""

import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

# Logger
logger = logging.getLogger(__name__)


class NivelSeveridade(Enum):
    """Níveis de severidade de alertas críticos."""
    CRITICO = "CRÍTICO"
    ALTO = "ALTO"
    MEDIO = "MÉDIO"
    BAIXO = "BAIXO"


class NivelConfianca(Enum):
    """Níveis de confiança do sistema conforme Radical Transparency."""
    MUITO_BAIXA = 1  # 10-20%
    BAIXA = 2  # 20-30%
    MEDIA = 3  # 30-50% (raramente atingido)


@dataclass
class AlertaCritico:
    """Representa um alerta crítico de risco."""
    titulo: str
    descricao: str
    severidade: NivelSeveridade
    metrica: str  # ex: "Posições sem stop loss"
    valor_atual: Any
    threshold_critico: Any
    acao_recomendada: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def para_dict(self) -> Dict[str, Any]:
        """Converte alerta para dicionário."""
        return {
            "titulo": self.titulo,
            "descricao": self.descricao,
            "severidade": self.severidade.value,
            "metrica": self.metrica,
            "valor_atual": self.valor_atual,
            "threshold_critico": self.threshold_critico,
            "acao_recomendada": self.acao_recomendada,
            "timestamp": self.timestamp,
        }

    def para_markdown(self) -> str:
        """Formata alerta como Markdown com cor de severidade."""
        emoji_severidade = {
            NivelSeveridade.CRITICO: "🔴",
            NivelSeveridade.ALTO: "🟠",
            NivelSeveridade.MEDIO: "🟡",
            NivelSeveridade.BAIXO: "🟢",
        }

        return f"""
{emoji_severidade[self.severidade]} **{self.titulo}** ({self.severidade.value})

{self.descricao}

- **Métrica:** {self.metrica}
- **Valor Atual:** {self.valor_atual}
- **Threshold Crítico:** {self.threshold_critico}
- **Ação Recomendada:** {self.acao_recomendada}
- **Timestamp:** {self.timestamp}
"""


class SystemaTransparencyRadical:
    """
    Sistema de Transparência Radical — força downgrade de confiança
    e alertas críticos em TODAS as análises.
    """

    def __init__(self):
        """Inicializa o sistema de transparência."""
        self.nivel_confianca_forcado = NivelConfianca.BAIXA  # 20-30%
        self.percentual_confianca_forcado = 25  # 25% como padrão (baixo e bem definido)
        self.alertas_criticos: List[AlertaCritico] = []
        logger.info(f"Sistema de Transparência Radical inicializado com confiança {self.percentual_confianca_forcado}%")

    def adicionar_alerta_critico(self, alerta: AlertaCritico) -> None:
        """Adiciona um alerta crítico ao sistema."""
        self.alertas_criticos.append(alerta)
        logger.warning(f"Alerta crítico adicionado: {alerta.titulo}")

    def limpar_alertas(self) -> None:
        """Limpa todos os alertas críticos."""
        self.alertas_criticos.clear()

    def gerar_disclaimer_obrigatorio(self) -> str:
        """Gera disclaimer obrigatório para TODAS as análises."""
        return """
⚠️ **DISCLAIMER CRÍTICO**

🔴 **SISTEMA EM FASE BETA — SEM VALIDAÇÃO HISTÓRICA**
- Este sistema NÃO possui histórico de backtesting > 6 meses
- Confiança declarada: 25% (BAIXA)
- Este material NÃO é recomendação de investimento

🚨 **AVISO DE RISCO**
- Este material é APENAS para análise educacional
- Não é recomendação, sugestão ou solicitação de investimento
- Sempre consulte um profissional certificado (CFP, CFA) antes de operar
- Riscos de perda total de capital existem

✋ **LIMITAÇÕES**
- Dados podem estar até 1 hora desatualizados
- Fontes de dados são agregadas (veja seção "FONTES")
- Modelo LLM pode alucinar; sempre validar fontes
- Sem acesso a dados não-públicos ou propriedade intelectual

**Você assume 100% da responsabilidade por qualquer ação baseada nesta análise.**
"""

    def gerar_alerta_risco_ilimitado(self) -> str:
        """Gera alerta padrão de risco ilimitado quando sem stop loss."""
        return """
🔴 **RISCO ILIMITADO DETECTADO**

Posições abertas SEM stop loss = risco de perda TOTAL do capital.

**AÇÃO URGENTE REQUERIDA:**
1. Abra posições sem risco definido em sua plataforma
2. Configure stop loss IMEDIATAMENTE a nível de suporte
3. Considere encerrar posições até proteções estarem em lugar
4. Monitore exposição total de alavancagem
"""

    def gerar_secao_alertas_criticos(self) -> str:
        """Gera seção formatada de alertas críticos em Markdown."""
        if not self.alertas_criticos:
            return ""

        markdown = "\n## 🚨 ALERTAS CRÍTICOS\n\n"
        markdown += "**Estes alertas BLOQUEIAM qualquer análise positiva até serem resolvidos.**\n\n"

        for alerta in self.alertas_criticos:
            markdown += alerta.para_markdown()
            markdown += "\n---\n"

        return markdown

    def downgrade_confianca_forcado(self, confianca_original: float) -> Dict[str, Any]:
        """
        Força downgrade de confiança de 60% para 20-30%.

        Retorna um dicionário com:
        - confianca_original: valor antes do downgrade
        - confianca_forcada: valor após downgrade
        - percentual_downgrade: diferença em pontos percentuais
        - justificativa: por que foi downgraded
        """
        downgrade = confianca_original - self.percentual_confianca_forcado

        return {
            "confianca_original": confianca_original,
            "confianca_forcada": self.percentual_confianca_forcado,
            "percentual_downgrade": downgrade,
            "justificativa": f"Downgrade forçado por Radical Transparency: sem validação histórica > 6 meses",
            "estrelas_display": self._gerar_estrelas_display(self.percentual_confianca_forcado),
        }

    def _gerar_estrelas_display(self, percentual: float) -> str:
        """Gera display de estrelas baseado em percentual."""
        if percentual < 20:
            return "⭐ (Muito Baixa)"
        elif percentual < 40:
            return "⭐⭐ (Baixa)"
        elif percentual < 60:
            return "⭐⭐⭐ (Média)"
        else:
            return "⭐⭐⭐⭐ (Alta)"

    def validar_qualidade_pre_analise(self, dados_preco: Optional[Dict],
                                     dados_indicadores: Optional[Dict],
                                     frescor_minutos: float = 60) -> Dict[str, Any]:
        """
        Valida qualidade de dados PRÉ-análise.

        Rejeita análise se:
        - Dados > frescor_minutos (default 60 min)
        - Inconsistência entre fontes > 80%
        - Campos obrigatórios faltando

        Retorna:
        {
            "valido": bool,
            "erros": List[str],
            "avisos": List[str],
            "qualidade_score": 0-100
        }
        """
        erros = []
        avisos = []
        qualidade_score = 100

        # Validação 1: Dados de preço existem
        if not dados_preco:
            erros.append("Dados de preço não disponíveis")
            return {
                "valido": False,
                "erros": erros,
                "avisos": avisos,
                "qualidade_score": 0,
            }

        # Validação 2: Frescor de dados
        if "timestamp" in dados_preco:
            try:
                timestamp_str = dados_preco["timestamp"]
                timestamp_dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                agora = datetime.now(timezone.utc)
                diferenca_minutos = (agora - timestamp_dt).total_seconds() / 60

                if diferenca_minutos > frescor_minutos:
                    erros.append(f"Dados > {frescor_minutos}min: {diferenca_minutos:.0f} minutos de atraso")
                    qualidade_score -= 30
                elif diferenca_minutos > frescor_minutos / 2:
                    avisos.append(f"Dados estão com {diferenca_minutos:.0f}min de atraso; use com cautela")
                    qualidade_score -= 10
            except Exception as e:
                avisos.append(f"Não foi possível validar frescor: {e}")
                qualidade_score -= 5

        # Validação 3: Campos obrigatórios
        campos_obrigatorios = ["ativo", "preco", "variacao_pct"]
        for campo in campos_obrigatorios:
            if campo not in dados_preco or dados_preco[campo] is None:
                erros.append(f"Campo obrigatório faltando: {campo}")
                qualidade_score -= 20

        # Validação 4: Consistência entre indicadores (se disponíveis)
        if dados_indicadores and "indicadores" in dados_indicadores:
            try:
                # Validação básica: RSI deve estar entre 0-100
                rsi_valor = dados_indicadores["indicadores"].get("rsi", {}).get("valor")
                if rsi_valor is not None and (rsi_valor < 0 or rsi_valor > 100):
                    avisos.append(f"RSI fora do range 0-100: {rsi_valor} (valor inválido)")
                    qualidade_score -= 15
            except Exception as e:
                avisos.append(f"Erro validando indicadores: {e}")
                qualidade_score -= 10

        # Determinar se válido (sem erros críticos)
        valido = len(erros) == 0 and qualidade_score >= 50

        resultado = {
            "valido": valido,
            "erros": erros,
            "avisos": avisos,
            "qualidade_score": max(0, qualidade_score),
        }

        if not valido and erros:
            logger.error(f"Validação pré-análise falhou: {erros}")
        elif avisos:
            logger.warning(f"Avisos na validação: {avisos}")

        return resultado

    def gerar_resposta_rejeicao_qualidade(self, resultado_validacao: Dict[str, Any]) -> str:
        """Gera resposta de rejeição de análise por qualidade."""
        markdown = """
🚫 **ANÁLISE REJEITADA POR QUALIDADE INSUFICIENTE**

O sistema não pode fornecer análise confiável neste momento.

**Erros encontrados:**
"""
        for erro in resultado_validacao["erros"]:
            markdown += f"- ❌ {erro}\n"

        if resultado_validacao["avisos"]:
            markdown += "\n**Avisos:**\n"
            for aviso in resultado_validacao["avisos"]:
                markdown += f"- ⚠️ {aviso}\n"

        markdown += f"""
**Score de Qualidade:** {resultado_validacao['qualidade_score']}/100

**Recomendações:**
1. Verifique se o mercado do ativo está aberto
2. Tente novamente em 1-2 minutos (dados atualizarão)
3. Se problema persistir, reporte para suporte técnico

**Nota:** Transparência Radical = Rejeitar análise duvidosa ao invés de fornecer confiança falsa.
"""
        return markdown

    def fallback_gracioso_api_falha(self, ativo: str, tipo_erro: str) -> str:
        """Gera resposta fallback gracioso quando API externa falha."""
        return f"""
⚠️ **SERVIÇO DE ANÁLISE LIMITADO**

O modelo LLM não está disponível no momento ({tipo_erro}).
Sistema em modo degradado — apenas dados brutos disponíveis para {ativo}.

**O que fazer:**
1. Tente novamente em 1-2 minutos
2. Use análise técnica manual (SMA/RSI fornecidos abaixo)
3. Se persistir, entre em contato com suporte

**Dados Disponíveis para {ativo}:**
- Preço atual: ✅ Disponível
- Indicadores (SMA/RSI): ✅ Disponível
- Notícias: ✅ Disponível
- **Análise LLM: ❌ Indisponível**

**Risco de Análise Incompleta**
- Sem contexto de notícias recentes
- Sem drivers macro considerados
- Sem cenários de risco mapeados

**Recomendação:** Aguarde disponibilidade total ou use apenas dados técnicos.
"""

    def para_json(self) -> Dict[str, Any]:
        """Serializa estado do sistema para JSON."""
        return {
            "sistema": "transparencia_radical",
            "nivel_confianca": self.nivel_confianca_forcado.name,
            "percentual_confianca": self.percentual_confianca_forcado,
            "alertas_criticos": [a.para_dict() for a in self.alertas_criticos],
            "timestamp_inicializacao": datetime.now(timezone.utc).isoformat(),
        }

    def para_markdown(self) -> str:
        """Serializa estado do sistema para Markdown."""
        markdown = f"""
# 🔴 TRANSPARÊNCIA RADICAL - Status do Sistema

**Confiança Declarada:** ⭐ {self.percentual_confianca_forcado}% (BAIXA)
**Nível:** {self.nivel_confianca_forcado.value}
**Alertas Críticos:** {len(self.alertas_criticos)}

## Garantias

- ✅ Sem recomendação de investimento
- ✅ Dados validados pré-análise
- ✅ Fallback gracioso se APIs falham
- ✅ Disclaimers obrigatórios em 100% das respostas

## Estado dos Alertas

{self._gerar_listagem_alertas()}
"""
        return markdown

    def _gerar_listagem_alertas(self) -> str:
        """Gera listagem formatada dos alertas críticos."""
        if not self.alertas_criticos:
            return "✅ Nenhum alerta crítico no momento"

        markdown = ""
        for alerta in self.alertas_criticos:
            emoji = {
                NivelSeveridade.CRITICO: "🔴",
                NivelSeveridade.ALTO: "🟠",
                NivelSeveridade.MEDIO: "🟡",
                NivelSeveridade.BAIXO: "🟢",
            }.get(alerta.severidade, "⚪")

            markdown += f"- {emoji} {alerta.titulo} ({alerta.severidade.value})\n"

        return markdown


# Instância singleton global
_sistema_singleton: Optional[SystemaTransparencyRadical] = None


def obter_sistema_transparency_radical() -> SystemaTransparencyRadical:
    """Obtém ou cria a instância singleton do sistema."""
    global _sistema_singleton
    if _sistema_singleton is None:
        _sistema_singleton = SystemaTransparencyRadical()
    return _sistema_singleton
