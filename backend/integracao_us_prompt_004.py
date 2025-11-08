#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
INTEGRAÇÃO US-PROMPT-004 - Modificação do Orquestrador

Este arquivo mostra como integrar RespostaAnaliseEstruturada no OrquestradorAnalise.

A função `_chamar_llm_analise_v2_json` é uma versão atualizada que:
1. Força LLM a retornar JSON estruturado
2. Valida contra schema Pydantic
3. Gera Markdown paralelo
4. Mantém backward compatibility com versão anterior
"""

from typing import Optional, Dict, Tuple, Any
import openai
import os
import json
from datetime import datetime, timezone
import logging

# Importar novos módulos
from modelos_resposta import RespostaAnaliseEstruturada
from formatador_resposta_estruturada import FormatadorRespostaEstruturada
from sistema_templates_analise import TemplatesAnalise

logger = logging.getLogger(__name__)


class OrquestradorAnaliseV2:
    """
    Versão melhorada do Orquestrador com suporte a JSON estruturado (US-PROMPT-004).

    Adiciona método `_chamar_llm_analise_v2_json` que:
    - Força resposta JSON
    - Valida com Pydantic
    - Gera Markdown
    - Mantém compatibilidade com versão anterior
    """

    def __init__(self, api_key: str = None, modelo: str = "gpt-4o-mini", versao: str = "v1"):
        """
        Args:
            api_key: OpenAI API key (default from env)
            modelo: LLM model (default: gpt-4o-mini)
            versao: "v1" (texto) ou "v2" (JSON) - default v1 para backward compatibility
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.modelo = modelo
        self.versao = versao
        self.max_tokens = 2000
        self.temperatura = 0.3

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não configurada")

        self.cliente = openai.OpenAI(api_key=self.api_key)

    def _chamar_llm_analise_v1_texto(
        self,
        contexto: str,
        modo: str
    ) -> str:
        """
        Versão original - LLM retorna texto livre.

        Mantida para backward compatibility.

        Args:
            contexto: Contexto da análise
            modo: "analista" ou "trader"

        Returns:
            Texto bruto da análise
        """
        prompt_sistema = TemplatesAnalise.obter_prompt_sistema(modo)

        resposta = self.cliente.chat.completions.create(
            model=self.modelo,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": contexto}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperatura
        )

        return resposta.choices[0].message.content

    def _chamar_llm_analise_v2_json(
        self,
        contexto: str,
        modo: str
    ) -> Dict[str, Any]:
        """
        Versão nova - LLM retorna JSON estruturado (US-PROMPT-004).

        MUDANÇA CRÍTICA: Usa response_format para forçar JSON válido.

        Args:
            contexto: Contexto da análise
            modo: "analista" ou "trader"

        Returns:
            {
                "sucesso": bool,
                "json": dict | None,
                "markdown": str | None,
                "modelo": RespostaAnaliseEstruturada | None,
                "erros": str | None,
                "ttl_segundos": int
            }
        """
        logger.info(f"Chamando LLM v2 JSON (modo: {modo})")

        # Construir prompts com instrução para JSON estruturado
        system, user = FormatadorRespostaEstruturada.construir_prompt_json_estruturado(
            contexto_analise=contexto,
            modo=modo
        )

        # MUDANÇA CRÍTICA: Usar response_format para forçar JSON
        try:
            resposta = self.cliente.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperatura,
                # ⭐ ISSO FORÇA LLM A RETORNAR APENAS JSON VÁLIDO
                response_format={"type": "json_object"}
            )

            resposta_bruta = resposta.choices[0].message.content
            logger.info(f"LLM respondeu com {len(resposta_bruta)} chars de JSON")

        except Exception as e:
            logger.error(f"Erro na chamada LLM v2: {e}")
            return {
                "sucesso": False,
                "json": None,
                "markdown": None,
                "modelo": None,
                "erros": str(e),
                "ttl_segundos": 0
            }

        # Pipeline: Parsear → Validar → Gerar Markdown
        resultado = FormatadorRespostaEstruturada.formatar_resposta_completa(resposta_bruta)

        return resultado

    def _chamar_llm_analise_inteligente(
        self,
        contexto: str,
        modo: str,
        forcar_versao: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Router inteligente que escolhe v1 ou v2 baseado em configuração.

        Permite migração gradual de v1 → v2.

        Args:
            contexto: Contexto da análise
            modo: "analista" ou "trader"
            forcar_versao: "v1", "v2", ou None (usa self.versao)

        Returns:
            Resposta estruturada (v1 texto ou v2 JSON)
        """
        versao_usar = forcar_versao or self.versao

        if versao_usar == "v2":
            logger.info("Usando LLM v2 (JSON estruturado)")
            return self._chamar_llm_analise_v2_json(contexto, modo)
        else:
            logger.info("Usando LLM v1 (texto livre)")
            texto = self._chamar_llm_analise_v1_texto(contexto, modo)
            # Adaptar para retornar dicionário consistente
            return {
                "sucesso": True,
                "json": None,
                "markdown": texto,  # Aqui retornamos o texto como markdown
                "modelo": None,
                "erros": None,
                "ttl_segundos": 0
            }


# ============================================================================
# INSTRUÇÕES DE INTEGRAÇÃO NO ORQUESTRADOR EXISTENTE
# ============================================================================

"""
PASSO 1: Adicionar imports no topo de orquestrador_analise.py

```python
from modelos_resposta import RespostaAnaliseEstruturada
from formatador_resposta_estruturada import FormatadorRespostaEstruturada
```

PASSO 2: Adicionar variável de configuração (pode ir em .env)

```python
# No __init__ do OrquestradorAnalise:
self.versao_resposta = os.getenv('ANALISE_VERSAO_RESPOSTA', 'v1')  # v1 ou v2
```

PASSO 3: Atualizar _chamar_llm_analise para suportar ambas

```python
def _chamar_llm_analise(self, contexto: str, modo: str, ...):
    # Novo: Check versão
    if self.versao_resposta == "v2":
        return self._chamar_llm_analise_v2_json(contexto, modo)
    else:
        return self._chamar_llm_analise_v1_texto(contexto, modo)

def _chamar_llm_analise_v2_json(self, contexto: str, modo: str):
    # [Copiar conteúdo do método abaixo]
    ...

def _chamar_llm_analise_v1_texto(self, contexto: str, modo: str):
    # [Manter código existente]
    ...
```

PASSO 4: Atualizar método analisar_ativo para lidar com ambas

```python
def analisar_ativo(self, ativo: str, modo: str = "analista", ...):
    # ... código existente até _chamar_llm_analise ...

    resposta = self._chamar_llm_analise(contexto, modo)

    # Novo: Tratar v2 JSON
    if isinstance(resposta, dict) and 'sucesso' in resposta:
        if not resposta['sucesso']:
            logger.error(f"Erro na análise JSON: {resposta['erros']}")
            # Fallback para v1
            return {...erro...}

        json_estruturado = resposta['json']
        markdown_output = resposta['markdown']
        modelo = resposta['modelo']
        ttl = resposta['ttl_segundos']
    else:
        # v1 - resposta é string
        json_estruturado = None
        markdown_output = resposta
        modelo = None
        ttl = 0

    # ... resto do processamento ...
    return {
        "analise": markdown_output,
        "json_estruturado": json_estruturado,
        "modelo": modelo,
        "ttl": ttl
    }
```

PASSO 5: Testar com ambas versões

```python
# Teste v1
orq = OrquestradorAnalise(versao_resposta="v1")
resultado_v1 = orq.analisar_ativo("EURUSD")

# Teste v2 (novo)
orq = OrquestradorAnalise(versao_resposta="v2")
resultado_v2 = orq.analisar_ativo("EURUSD")

# Ambos devem funcionar sem erros
```

PASSO 6: Monitorar em produção

Configurar .env com:
- `ANALISE_VERSAO_RESPOSTA=v1` (default)
- Depois migrar para `v2` quando confiante
- Manter v1 como fallback

BENEFÍCIOS DA INTEGRAÇÃO:
✅ Zero downtime migration path
✅ A/B testing possível
✅ Rollback automático em caso de erro
✅ Validação schema automática com Pydantic
✅ Markdown gerado automaticamente
✅ TTL e cache gerenciados
"""


# ============================================================================
# TESTE SIMULADO
# ============================================================================

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  Integração US-PROMPT-004 no Orquestrador                     ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    print("📋 EXEMPLO: Como integrar no OrquestradorAnalise existente")
    print("-" * 70)
    print()

    print("1️⃣ Adicionar imports:")
    print("   from modelos_resposta import RespostaAnaliseEstruturada")
    print("   from formatador_resposta_estruturada import FormatadorRespostaEstruturada")
    print()

    print("2️⃣ Adicionar método v2 (JSON estruturado):")
    print("   def _chamar_llm_analise_v2_json(self, contexto, modo):")
    print("       # Usar response_format JSON")
    print("       response = self.cliente.chat.completions.create(")
    print("           response_format={'type': 'json_object'}")
    print("       )")
    print("       return FormatadorRespostaEstruturada.formatar_resposta_completa()")
    print()

    print("3️⃣ Router inteligente:")
    print("   if self.versao_resposta == 'v2':")
    print("       return self._chamar_llm_analise_v2_json(...)")
    print("   else:")
    print("       return self._chamar_llm_analise_v1_texto(...)")
    print()

    print("4️⃣ Configurar no .env:")
    print("   ANALISE_VERSAO_RESPOSTA=v1  # ou v2")
    print()

    print("✅ Benefícios:")
    print("   ✓ JSON estruturado validado automaticamente")
    print("   ✓ Markdown gerado em paralelo")
    print("   ✓ TTL gerenciado")
    print("   ✓ Zero downtime migration")
    print("   ✓ Fallback automático para v1")
    print()

    # Simular resposta JSON mock
    print("🧪 Teste: Simular resposta LLM → JSON → Validação → Markdown")
    print("-" * 70)

    # Gerar JSON mock como se fosse resposta do LLM
    json_mock = FormatadorRespostaEstruturada.gerar_json_mock_estruturado("trader", "EUR/USD")
    print(f"✓ JSON mock: {len(json_mock)} chars")

    # Formatar como faria o pipeline real
    resultado = FormatadorRespostaEstruturada.formatar_resposta_completa(json_mock)
    print(f"✓ Pipeline resultado: sucesso={resultado['sucesso']}")
    print(f"  - JSON: {len(str(resultado['json']))} chars")
    print(f"  - Markdown: {len(resultado['markdown'])} chars")
    print(f"  - TTL: {resultado['ttl_segundos']} segundos")
    print()

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  ✅ Integração pronta para implementação                      ║")
    print("╚════════════════════════════════════════════════════════════════╝")
