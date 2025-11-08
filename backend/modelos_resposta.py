#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MODELO DE RESPOSTA ESTRUTURADA - US-PROMPT-004

Define a estrutura JSON para análises estruturadas (trader + analista).
Usa Pydantic para validação automática e serialização JSON.

Classes:
- DriverAnalise: Item individual de driver
- RiscoAnalise: Item individual de risco
- ProximoPasso: Ação planejada
- FonteReferencia: Fonte de dados
- MetadadosAnalise: Metadata da análise
- RespostaAnaliseEstruturada: Resposta completa
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, field_validator
import json
from enum import Enum


# ============================================================================
# ENUMS PARA VALORES PERMITIDOS
# ============================================================================

class CategoriaDriver(str, Enum):
    """Categorias de driver de análise."""
    MACROECONOMICO = "macroeconomico"
    FUNDAMENTAL = "fundamental"
    TECNICO = "tecnico"


class NivelImpacto(str, Enum):
    """Níveis de impacto."""
    CRITICO = "CRÍTICO"
    ALTO = "ALTO"
    MÉDIO = "MÉDIO"
    BAIXO = "BAIXO"


class NivelConfianca(str, Enum):
    """Níveis de confiança."""
    ALTA = "ALTA"
    MÉDIA = "MÉDIA"
    BAIXA = "BAIXA"


class NivelProbabilidade(str, Enum):
    """Níveis de probabilidade."""
    ALTA = "ALTA"
    MÉDIA = "MÉDIA"
    BAIXA = "BAIXA"


class ModoAnalise(str, Enum):
    """Modos de análise suportados."""
    ANALISTA = "analista"
    TRADER = "trader"


# ============================================================================
# MODELOS COMPONENTES
# ============================================================================

class DriverAnalise(BaseModel):
    """
    Driver individual de análise.

    Um driver é um fator que influencia o movimento do ativo.
    Exemplo: "Divergência Política Monetária BCE vs Fed"
    """
    categoria: CategoriaDriver = Field(
        ...,
        description="Categoria do driver: macroeconômico, fundamental ou técnico"
    )
    titulo: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Título descritivo do driver"
    )
    descricao: Optional[str] = Field(
        None,
        max_length=500,
        description="Descrição detalhada do driver"
    )
    impacto: NivelImpacto = Field(
        ...,
        description="Nível de impacto deste driver"
    )
    confianca: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confiança na análise (0-1)"
    )
    fonte: str = Field(
        ...,
        description="Fonte de dados (URL ou description)"
    )

    class Config:
        use_enum_values = False
        json_schema_extra = {
            "example": {
                "categoria": "macroeconomico",
                "titulo": "Divergência Política Monetária",
                "descricao": "BCE sinaliza pausa no aperto enquanto Fed mantém postura restritiva",
                "impacto": "ALTO",
                "confianca": 0.85,
                "fonte": "https://ecb.europa.eu"
            }
        }


class RiscoAnalise(BaseModel):
    """
    Risco individual identificado.

    Um risco é um cenário negativo potencial.
    Exemplo: "Eleições Europeias podem aumentar volatilidade"
    """
    categoria: str = Field(
        ...,
        description="Categoria: politico, economico, tecnico, liquidez"
    )
    titulo: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Título do risco"
    )
    descricao: Optional[str] = Field(
        None,
        max_length=500,
        description="Descrição detalhada do risco"
    )
    probabilidade: NivelProbabilidade = Field(
        ...,
        description="Probabilidade de ocorrência"
    )
    impacto: NivelImpacto = Field(
        ...,
        description="Impacto se ocorrer"
    )
    mitigacao: Optional[str] = Field(
        None,
        max_length=300,
        description="Como mitigar ou evitar este risco"
    )

    class Config:
        use_enum_values = False
        json_schema_extra = {
            "example": {
                "categoria": "politico",
                "titulo": "Eleições Europeias",
                "descricao": "Eleições podem aumentar volatilidade e incerteza",
                "probabilidade": "MÉDIA",
                "impacto": "ALTO",
                "mitigacao": "Reduzir posição se volatilidade >25%"
            }
        }


class ProximoPasso(BaseModel):
    """
    Ação recomendada ou monitoramento.

    Um próximo passo é uma ação que deve ser tomada.
    Exemplo: "Monitorar dados de emprego nos EUA amanhã às 13:30"
    """
    prioridade: int = Field(
        ...,
        ge=1,
        le=10,
        description="Prioridade (1-10, onde 10 é urgente)"
    )
    acao: str = Field(
        ...,
        min_length=5,
        max_length=300,
        description="Descrição da ação"
    )
    timeline: str = Field(
        ...,
        max_length=100,
        description="Quando fazer (ex: 'Próximas 2 horas', 'Amanhã às 13:30')"
    )
    gatilho: Optional[str] = Field(
        None,
        max_length=300,
        description="Condição que ativa esta ação (ex: 'Se NFP > 200k')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prioridade": 1,
                "acao": "Monitorar dados de emprego",
                "timeline": "Próximas 2 horas",
                "gatilho": "Se NFP > 200k, revisar posição"
            }
        }


class FonteReferencia(BaseModel):
    """
    Fonte de dados/referência.

    Rastreia de onde vieram os dados.
    Exemplo: "Yahoo Finance", "ECB Press Release"
    """
    nome: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome da fonte"
    )
    url: Optional[str] = Field(
        None,
        description="URL da fonte (se aplicável)"
    )
    ultima_atualizacao: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Última vez que a fonte foi consultada"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "nome": "Yahoo Finance",
                "url": "https://finance.yahoo.com/quote/EURUSD=X",
                "ultima_atualizacao": "2025-11-07T22:30:00Z"
            }
        }


class MetadadosAnalise(BaseModel):
    """
    Metadata da análise.

    Informações sobre quando, como e qual a versão da análise.
    """
    ativo: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Ativo analisado (ex: EUR/USD, XAUUSD)"
    )
    modo: ModoAnalise = Field(
        ...,
        description="Modo de análise (analista ou trader)"
    )
    timestamp_analise: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Quando a análise foi realizada"
    )
    ttl_segundos: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Time-to-live em segundos (quanto tempo a análise é válida)"
    )
    versao_schema: str = Field(
        default="1.0",
        description="Versão do schema de resposta"
    )
    confianca_geral: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confiança geral da análise (média dos drivers)"
    )

    class Config:
        use_enum_values = False
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "ativo": "EUR/USD",
                "modo": "trader",
                "timestamp_analise": "2025-11-07T22:30:00Z",
                "ttl_segundos": 3600,
                "versao_schema": "1.0",
                "confianca_geral": 0.85
            }
        }


# ============================================================================
# MODELO PRINCIPAL
# ============================================================================

class RespostaAnaliseEstruturada(BaseModel):
    """
    Resposta completa e estruturada de uma análise.

    Este é o modelo principal que contém todos os componentes de uma análise.
    Pode ser serializado para JSON ou convertido em Markdown.

    Uso:
    ```python
    resposta = RespostaAnaliseEstruturada(
        metadata=MetadadosAnalise(ativo="EUR/USD", modo="trader"),
        drivers=[...],
        riscos=[...],
        proximos_passos=[...],
        fontes=[...],
        resumo_executivo="..."
    )

    json_str = resposta.model_dump_json()
    markdown = resposta.para_markdown()
    ```
    """
    metadata: MetadadosAnalise = Field(
        ...,
        description="Metadata da análise"
    )
    drivers: List[DriverAnalise] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Drivers principais (1-10 items)"
    )
    riscos: List[RiscoAnalise] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Riscos identificados (1-10 items)"
    )
    proximos_passos: List[ProximoPasso] = Field(
        default_factory=list,
        max_items=10,
        description="Próximos passos (0-10 items)"
    )
    fontes: List[FonteReferencia] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Fontes de referência (1-10 items)"
    )
    resumo_executivo: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Resumo em 1-2 linhas da análise"
    )

    @field_validator("drivers")
    @classmethod
    def validar_drivers_unicos(cls, v):
        """Valida que não há drivers duplicados."""
        if v:
            titulos = [d.titulo for d in v]
            if len(titulos) != len(set(titulos)):
                raise ValueError("Drivers duplicados detectados")
        return v

    def model_post_init(self, __context):
        """Calcula confiança geral como média dos drivers após criação do modelo."""
        if self.drivers:
            confianca_media = sum(d.confianca for d in self.drivers) / len(self.drivers)
            self.metadata.confianca_geral = round(confianca_media, 2)

    def para_markdown(self) -> str:
        """
        Converte a resposta para Markdown formatado.

        Returns:
            Markdown bem-formatado com seções, headers, tabelas
        """
        md = []

        # Header
        md.append(f"# Análise: {self.metadata.ativo} ({self.metadata.modo.upper()})")
        md.append("")
        md.append(f"**Timestamp:** {self.metadata.timestamp_analise.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        md.append(f"**TTL:** {self.metadata.ttl_segundos // 60} minutos")
        md.append(f"**Confiança Geral:** {self.metadata.confianca_geral:.0%}")
        md.append("")
        md.append("---")
        md.append("")

        # Resumo
        md.append("## 📊 Resumo")
        md.append(self.resumo_executivo)
        md.append("")
        md.append("---")
        md.append("")

        # Drivers
        md.append("## 🎯 Drivers Principais")
        md.append("")
        for driver in self.drivers:
            emoji_impacto = {"CRÍTICO": "🔴", "ALTO": "🟠", "MÉDIO": "🟡", "BAIXO": "🟢"}
            emoji = emoji_impacto.get(driver.impacto.value, "⚪")
            md.append(f"### {emoji} [{driver.impacto.value}] {driver.titulo}")
            md.append(f"- **Categoria:** {driver.categoria.value}")
            md.append(f"- **Confiança:** {driver.confianca:.0%}")
            if driver.descricao:
                md.append(f"- **Detalhe:** {driver.descricao}")
            md.append(f"- **Fonte:** [{driver.fonte}]({driver.fonte})" if driver.fonte.startswith("http") else f"- **Fonte:** {driver.fonte}")
            md.append("")

        md.append("---")
        md.append("")

        # Riscos
        md.append("## ⚠️ Riscos Identificados")
        md.append("")
        for risco in self.riscos:
            emoji_prob = {"ALTA": "🔴", "MÉDIA": "🟠", "BAIXA": "🟡"}
            emoji = emoji_prob.get(risco.probabilidade.value, "⚪")
            md.append(f"### {emoji} [{risco.probabilidade.value}] {risco.titulo}")
            md.append(f"- **Categoria:** {risco.categoria}")
            md.append(f"- **Impacto:** {risco.impacto.value}")
            if risco.descricao:
                md.append(f"- **Descrição:** {risco.descricao}")
            if risco.mitigacao:
                md.append(f"- **Mitigação:** {risco.mitigacao}")
            md.append("")

        md.append("---")
        md.append("")

        # Próximos Passos
        if self.proximos_passos:
            md.append("## 🚀 Próximos Passos")
            md.append("")
            for passo in sorted(self.proximos_passos, key=lambda x: x.prioridade):
                prioridade_emoji = "🔴" if passo.prioridade >= 8 else "🟠" if passo.prioridade >= 5 else "🟡"
                md.append(f"### {prioridade_emoji} [{passo.prioridade}] {passo.acao}")
                md.append(f"- **Timeline:** {passo.timeline}")
                if passo.gatilho:
                    md.append(f"- **Gatilho:** {passo.gatilho}")
                md.append("")
            md.append("---")
            md.append("")

        # Fontes
        md.append("## 📚 Fontes de Referência")
        md.append("")
        for fonte in self.fontes:
            if fonte.url and fonte.url.startswith("http"):
                md.append(f"- [{fonte.nome}]({fonte.url})")
            else:
                md.append(f"- {fonte.nome}" + (f" - {fonte.url}" if fonte.url else ""))
        md.append("")

        return "\n".join(md)

    def modelo_json(self) -> dict:
        """
        Retorna o modelo como dicionário Python (não JSON string).
        Usa serialização automática do Pydantic.
        """
        return self.model_dump()

    def modelo_json_string(self) -> str:
        """
        Retorna o modelo como JSON string formatado.
        """
        return self.model_dump_json(indent=2)

    class Config:
        use_enum_values = False
        json_schema_extra = {
            "title": "Resposta de Análise Estruturada",
            "description": "Formato padrão para análises de mercado com validação automática"
        }


# ============================================================================
# HELPERS E UTILITÁRIOS
# ============================================================================

def criar_resposta_exemplo(modo: str = "trader") -> RespostaAnaliseEstruturada:
    """
    Cria uma resposta de exemplo para testes e documentação.

    Args:
        modo: "trader" ou "analista"

    Returns:
        RespostaAnaliseEstruturada preenchida com dados de exemplo
    """
    modo_enum = ModoAnalise.TRADER if modo.lower() == "trader" else ModoAnalise.ANALISTA

    return RespostaAnaliseEstruturada(
        metadata=MetadadosAnalise(
            ativo="EUR/USD",
            modo=modo_enum,
            confianca_geral=0.85
        ),
        drivers=[
            DriverAnalise(
                categoria=CategoriaDriver.MACROECONOMICO,
                titulo="Divergência Política Monetária",
                descricao="BCE sinaliza pausa no aperto enquanto Fed mantém postura restritiva",
                impacto=NivelImpacto.ALTO,
                confianca=0.85,
                fonte="https://ecb.europa.eu"
            ),
            DriverAnalise(
                categoria=CategoriaDriver.TECNICO,
                titulo="Momentum Altista",
                descricao="Preço acima de SMA20 com RSI em zona neutra",
                impacto=NivelImpacto.MÉDIO,
                confianca=0.70,
                fonte="Yahoo Finance"
            )
        ],
        riscos=[
            RiscoAnalise(
                categoria="politico",
                titulo="Eleições Europeias",
                descricao="Podem aumentar volatilidade",
                probabilidade=NivelProbabilidade.MÉDIA,
                impacto=NivelImpacto.ALTO,
                mitigacao="Reduzir posição se volatilidade >25%"
            )
        ],
        proximos_passos=[
            ProximoPasso(
                prioridade=1,
                acao="Monitorar dados de emprego",
                timeline="Próximas 2 horas",
                gatilho="Se NFP > 200k, revisar posição"
            )
        ],
        fontes=[
            FonteReferencia(nome="Yahoo Finance", url="https://finance.yahoo.com"),
            FonteReferencia(nome="ECB Official", url="https://ecb.europa.eu")
        ],
        resumo_executivo="EUR/USD em suporte técnico com fundamental positivo para EUR. Monitorar dados de emprego para break-out."
    )


if __name__ == "__main__":
    # Teste rápido
    resposta = criar_resposta_exemplo("trader")

    print("=== JSON ===")
    print(resposta.modelo_json_string())

    print("\n=== MARKDOWN ===")
    print(resposta.para_markdown())

    print("\n=== VALIDAÇÃO ===")
    print(f"Modelo válido: {resposta.model_validate(resposta.modelo_json())}")
    print("✅ Tudo OK!")
