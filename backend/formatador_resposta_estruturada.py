#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FORMATADOR DE RESPOSTA ESTRUTURADA - US-PROMPT-004

Converte resposta bruta de LLM em RespostaAnaliseEstruturada validada.

Módulo responsável por:
1. Fazer LLM retornar JSON estruturado
2. Validar JSON contra schema Pydantic
3. Gerar Markdown paralelo
4. Retornar ambos (JSON + Markdown)

Classes:
- FormatadorRespostaEstruturada: Classe principal de formatação
"""

import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone
from pydantic import ValidationError

from modelos_resposta import RespostaAnaliseEstruturada, criar_resposta_exemplo

logger = logging.getLogger(__name__)


class FormatadorRespostaEstruturada:
    """
    Formatador de resposta estruturada para análises.

    Responsável por:
    - Construir prompts que forçam JSON do LLM
    - Parsear e validar JSON
    - Gerar Markdown
    - Retornar {json, markdown, modelo}
    """

    PROMPT_SYSTEM_JSON_FORCE = """
Você DEVE retornar APENAS JSON válido, sem markdown, sem explicações extras.

Formato esperado:
{{
  "metadata": {{
    "ativo": "EUR/USD",
    "modo": "trader",
    "ttl_segundos": 3600,
    "resumo_executivo": "..."
  }},
  "drivers": [
    {{
      "categoria": "macroeconomico",
      "titulo": "...",
      "descricao": "...",
      "impacto": "ALTO|MÉDIO|BAIXO",
      "confianca": 0.85,
      "fonte": "..."
    }}
  ],
  "riscos": [
    {{
      "categoria": "politico|economico|tecnico|liquidez",
      "titulo": "...",
      "descricao": "...",
      "probabilidade": "ALTA|MÉDIA|BAIXA",
      "impacto": "CRÍTICO|ALTO|MÉDIO|BAIXO",
      "mitigacao": "..."
    }}
  ],
  "proximos_passos": [...],
  "fontes": [...],
  "resumo_executivo": "..."
}}

IMPORTANTE:
- Retorne EXATAMENTE o JSON acima
- Use valores enum precisos: ALTO, MÉDIO, BAIXO, etc
- Sem explicações adicionais
- Sem blocos markdown (```)
- JSON deve ser parseable
"""

    @staticmethod
    def construir_prompt_json_estruturado(
        contexto_analise: str,
        modo: str,
        modo_system_personalizado: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Constrói prompt que força LLM a retornar JSON estruturado.

        Args:
            contexto_analise: Contexto da análise (com templates)
            modo: "trader" ou "analista"
            modo_system_personalizado: Override do prompt system

        Returns:
            (system_prompt, user_message)
        """
        system = modo_system_personalizado or FormatadorRespostaEstruturada.PROMPT_SYSTEM_JSON_FORCE

        user_message = f"""
Analise o seguinte ativo e retorne JSON estruturado:

{contexto_analise}

Modo: {modo}

Retorne APENAS o JSON, nada mais.
"""

        return system, user_message.strip()

    @staticmethod
    def parsear_json_da_resposta(resposta_bruta: str) -> Optional[Dict]:
        """
        Extrai JSON da resposta do LLM.

        Tenta múltiplas estratégias:
        1. Parse direto (LLM retornou JSON puro)
        2. Extrair de bloco markdown (```json...```)
        3. Procurar por { ... } válido

        Args:
            resposta_bruta: Resposta bruta do LLM

        Returns:
            Dict com JSON ou None se não conseguir parsear
        """
        resposta_bruta = resposta_bruta.strip()

        # Estratégia 1: Parse direto
        try:
            return json.loads(resposta_bruta)
        except json.JSONDecodeError:
            pass

        # Estratégia 2: Extrair de bloco markdown
        if "```json" in resposta_bruta:
            try:
                inicio = resposta_bruta.find("```json") + 7
                fim = resposta_bruta.find("```", inicio)
                json_str = resposta_bruta[inicio:fim].strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass

        # Estratégia 3: Procurar por { ... }
        try:
            inicio = resposta_bruta.find("{")
            fim = resposta_bruta.rfind("}") + 1
            if inicio >= 0 and fim > inicio:
                json_str = resposta_bruta[inicio:fim]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

        logger.warning("Não conseguiu parsear JSON da resposta")
        return None

    @staticmethod
    def validar_resposta_json(dados_json: Dict) -> Tuple[bool, Optional[RespostaAnaliseEstruturada], Optional[str]]:
        """
        Valida JSON contra schema Pydantic.

        Args:
            dados_json: Dicionário JSON

        Returns:
            (sucesso: bool, modelo: RespostaAnaliseEstruturada|None, erro: str|None)
        """
        try:
            # Validação automática do Pydantic
            modelo = RespostaAnaliseEstruturada.model_validate(dados_json)
            return True, modelo, None
        except ValidationError as e:
            erro_msg = f"Validação falhou: {e.error_count()} erros\n"
            for erro in e.errors():
                erro_msg += f"  - {erro['loc']}: {erro['msg']}\n"
            logger.error(erro_msg)
            return False, None, erro_msg
        except Exception as e:
            erro_msg = f"Erro ao validar: {str(e)}"
            logger.error(erro_msg)
            return False, None, erro_msg

    @staticmethod
    def formatar_resposta_completa(
        resposta_bruta_llm: str,
        contexto_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Pipeline completo: LLM → JSON → Validação → Markdown

        Args:
            resposta_bruta_llm: Resposta bruta do LLM
            contexto_metadata: Metadata opcional (ativo, modo)

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
        resultado = {
            "sucesso": False,
            "json": None,
            "markdown": None,
            "modelo": None,
            "erros": None,
            "ttl_segundos": 3600
        }

        # Passo 1: Parsear JSON
        json_dict = FormatadorRespostaEstruturada.parsear_json_da_resposta(resposta_bruta_llm)
        if not json_dict:
            resultado["erros"] = "Não conseguiu extrair JSON válido da resposta do LLM"
            return resultado

        # Passo 2: Validar
        sucesso, modelo, erro = FormatadorRespostaEstruturada.validar_resposta_json(json_dict)
        if not sucesso:
            resultado["erros"] = erro
            return resultado

        # Passo 3: Gerar Markdown
        try:
            markdown = modelo.para_markdown()
        except Exception as e:
            resultado["erros"] = f"Erro ao gerar Markdown: {str(e)}"
            return resultado

        # Passo 4: Montar resposta final
        resultado["sucesso"] = True
        resultado["json"] = modelo.model_dump()
        resultado["markdown"] = markdown
        resultado["modelo"] = modelo
        resultado["ttl_segundos"] = modelo.metadata.ttl_segundos

        return resultado

    @staticmethod
    def gerar_json_mock_estruturado(modo: str = "trader", ativo: str = "EUR/USD") -> str:
        """
        Gera resposta JSON mock para testes.

        Útil para testar formatação sem chamar LLM.

        Args:
            modo: "trader" ou "analista"
            ativo: Ativo a analisar

        Returns:
            JSON string pronta para testar
        """
        resposta = criar_resposta_exemplo(modo)
        resposta.metadata.ativo = ativo
        return resposta.model_dump_json()


# ============================================================================
# TESTE
# ============================================================================

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  TESTE: Formatador de Resposta Estruturada (US-PROMPT-004)   ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    # Teste 1: Construir prompt
    print("🧪 TESTE 1: Construir prompt com JSON force")
    print("-" * 70)
    system, user = FormatadorRespostaEstruturada.construir_prompt_json_estruturado(
        contexto_analise="EUR/USD em suporte técnico",
        modo="trader"
    )
    print(f"✓ System prompt length: {len(system)} chars")
    print(f"✓ User message length: {len(user)} chars")
    print(f"✓ Contém instrução JSON: {'JSON' in system}")
    print()

    # Teste 2: Gerar JSON mock
    print("🧪 TESTE 2: Gerar resposta mock")
    print("-" * 70)
    json_mock = FormatadorRespostaEstruturada.gerar_json_mock_estruturado("trader", "GBP/USD")
    print(f"✓ JSON mock gerado: {len(json_mock)} chars")
    print(f"✓ Preview: {json_mock[:100]}...")
    print()

    # Teste 3: Parsear JSON
    print("🧪 TESTE 3: Parsear JSON")
    print("-" * 70)
    json_dict = FormatadorRespostaEstruturada.parsear_json_da_resposta(json_mock)
    print(f"✓ JSON parseado: {json_dict is not None}")
    if json_dict:
        print(f"  - Ativo: {json_dict.get('metadata', {}).get('ativo')}")
        print(f"  - Modo: {json_dict.get('metadata', {}).get('modo')}")
    print()

    # Teste 4: Validar JSON
    print("🧪 TESTE 4: Validar JSON contra schema")
    print("-" * 70)
    sucesso, modelo, erro = FormatadorRespostaEstruturada.validar_resposta_json(json_dict)
    print(f"✓ Validação: {'✅ PASSA' if sucesso else '❌ FALHA'}")
    if erro:
        print(f"  Erros: {erro[:100]}...")
    else:
        print(f"  - Drivers: {len(modelo.drivers)}")
        print(f"  - Riscos: {len(modelo.riscos)}")
        print(f"  - Confiança: {modelo.metadata.confianca_geral:.0%}")
    print()

    # Teste 5: Gerar Markdown
    print("🧪 TESTE 5: Gerar Markdown")
    print("-" * 70)
    markdown = modelo.para_markdown()
    linhas = markdown.split('\n')
    print(f"✓ Markdown gerado: {len(markdown)} chars, {len(linhas)} linhas")
    print(f"  Preview:")
    for linha in linhas[:10]:
        print(f"    {linha}")
    print(f"    ...")
    print()

    # Teste 6: Pipeline completo
    print("🧪 TESTE 6: Pipeline completo (LLM → JSON → Validação → Markdown)")
    print("-" * 70)
    resultado = FormatadorRespostaEstruturada.formatar_resposta_completa(json_mock)
    print(f"✓ Sucesso: {resultado['sucesso']}")
    print(f"✓ JSON presente: {resultado['json'] is not None}")
    print(f"✓ Markdown presente: {resultado['markdown'] is not None and len(resultado['markdown']) > 100}")
    print(f"✓ TTL: {resultado['ttl_segundos']} segundos")
    print(f"✓ Erros: {resultado['erros'] if resultado['erros'] else 'Nenhum'}")
    print()

    # Teste 7: Teste com markdown wrapper (como LLM pode retornar)
    print("🧪 TESTE 7: Parsear JSON dentro de bloco markdown")
    print("-" * 70)
    resposta_markdown = f"""
Aqui está a análise estruturada:

```json
{json_mock}
```

Esperamos ser úteis!
"""
    json_dict_md = FormatadorRespostaEstruturada.parsear_json_da_resposta(resposta_markdown)
    print(f"✓ JSON extraído de markdown: {json_dict_md is not None}")
    if json_dict_md:
        print(f"  - Ativo: {json_dict_md.get('metadata', {}).get('ativo')}")
    print()

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  ✅ TODOS OS TESTES PASSARAM                                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")
