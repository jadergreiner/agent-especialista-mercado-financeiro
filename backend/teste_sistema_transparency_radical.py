#!/usr/bin/env python3
"""
Script de Teste — US-RISCO-003: Radical Transparency

Testa a integração do sistema de transparência radical com o orquestrador.
Valida:
1. Gates de qualidade pré-análise
2. Downgrade forçado de confiança
3. Disclaimers obrigatórios
4. Fallback gracioso em caso de erro API
"""

import json
import sys
from datetime import datetime, timezone

# Adicionar backend ao path
sys.path.insert(0, '/repo/projetos/agent-especialista-mercado-financeiro/backend')

from sistema_transparency_radical import (
    SystemaTransparencyRadical,
    AlertaCritico,
    NivelSeveridade,
    obter_sistema_transparency_radical
)


def teste_1_sistema_initialization():
    """Teste 1: Inicialização do sistema"""
    print("\n" + "="*60)
    print("TESTE 1: Inicialização do Sistema de Transparência Radical")
    print("="*60)

    sistema = obter_sistema_transparency_radical()
    print(f"✅ Sistema inicializado com confiança: {sistema.percentual_confianca_forcado}%")
    print(f"✅ Nível de confiança: {sistema.nivel_confianca_forcado.value}")
    assert sistema.percentual_confianca_forcado == 25, "Confiança deve ser 25%"
    print("✅ TESTE 1 PASSOU")


def teste_2_downgrade_confianca():
    """Teste 2: Downgrade forçado de confiança"""
    print("\n" + "="*60)
    print("TESTE 2: Downgrade Forçado de Confiança")
    print("="*60)

    sistema = obter_sistema_transparency_radical()
    resultado = sistema.downgrade_confianca_forcado(confianca_original=60)

    print(f"Confiança original: {resultado['confianca_original']}%")
    print(f"Confiança forçada: {resultado['confianca_forcada']}%")
    print(f"Downgrade: {resultado['percentual_downgrade']} pp")
    print(f"Estrelas display: {resultado['estrelas_display']}")

    assert resultado['confianca_original'] == 60, "Original deve ser 60%"
    assert resultado['confianca_forcada'] == 25, "Forçada deve ser 25%"
    assert resultado['percentual_downgrade'] == 35, "Downgrade deve ser 35pp"
    print("✅ TESTE 2 PASSOU")


def teste_3_disclaimer_obrigatorio():
    """Teste 3: Disclaimer obrigatório"""
    print("\n" + "="*60)
    print("TESTE 3: Disclaimer Obrigatório")
    print("="*60)

    sistema = obter_sistema_transparency_radical()
    disclaimer = sistema.gerar_disclaimer_obrigatorio()

    # Validar conteúdo crítico
    assert "SISTEMA EM FASE BETA" in disclaimer, "Deve mencionar fase beta"
    assert "25%" in disclaimer, "Deve mencionar confiança 25%"
    assert "SEM VALIDAÇÃO HISTÓRICA" in disclaimer, "Deve mencionar sem validação"
    assert "NÃO é recomendação" in disclaimer, "Deve negar recomendação"

    print(f"Disclaimer gerado com {len(disclaimer)} caracteres")
    print("✅ TESTE 3 PASSOU")


def teste_4_alerta_critico():
    """Teste 4: Criação de alerta crítico"""
    print("\n" + "="*60)
    print("TESTE 4: Criação de Alerta Crítico")
    print("="*60)

    sistema = obter_sistema_transparency_radical()
    sistema.limpar_alertas()

    alerta = AlertaCritico(
        titulo="Risco Ilimitado Detectado",
        descricao="Posição aberta sem stop loss",
        severidade=NivelSeveridade.CRITICO,
        metrica="Posições sem stop loss",
        valor_atual=25,
        threshold_critico=0,
        acao_recomendada="Configurar stop loss IMEDIATAMENTE"
    )

    sistema.adicionar_alerta_critico(alerta)

    assert len(sistema.alertas_criticos) == 1, "Deve haver 1 alerta"
    assert sistema.alertas_criticos[0].titulo == "Risco Ilimitado Detectado"

    print(f"✅ Alerta adicionado: {alerta.titulo}")
    print(f"✅ Severidade: {alerta.severidade.value}")
    print("✅ TESTE 4 PASSOU")


def teste_5_validacao_qualidade():
    """Teste 5: Validação de qualidade pré-análise"""
    print("\n" + "="*60)
    print("TESTE 5: Validação de Qualidade Pré-Análise")
    print("="*60)

    sistema = obter_sistema_transparency_radical()

    # Dados válidos
    dados_validos = {
        "ativo": "EURUSD",
        "preco": 1.1565,
        "variacao_pct": 0.10,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    resultado = sistema.validar_qualidade_pre_analise(dados_validos, None, frescor_minutos=60)

    print(f"Validação com dados válidos: {resultado['valido']}")
    print(f"Score de qualidade: {resultado['qualidade_score']}/100")
    print(f"Erros: {len(resultado['erros'])}")
    print(f"Avisos: {len(resultado['avisos'])}")

    assert resultado['valido'] == True, "Dados válidos devem passar"
    assert resultado['qualidade_score'] >= 80, "Score deve ser alto"

    print("✅ TESTE 5 PASSOU (dados válidos)")

    # Teste com dados inválidos
    dados_invalidos = {
        "ativo": None,
        "preco": None,
        "variacao_pct": None,
    }

    resultado_invalido = sistema.validar_qualidade_pre_analise(dados_invalidos, None)

    print(f"\nValidação com dados inválidos: {resultado_invalido['valido']}")
    print(f"Score de qualidade: {resultado_invalido['qualidade_score']}/100")
    print(f"Erros encontrados: {len(resultado_invalido['erros'])}")

    assert resultado_invalido['valido'] == False, "Dados inválidos devem falhar"
    assert len(resultado_invalido['erros']) > 0, "Deve haver erros"

    print("✅ TESTE 5 PASSOU (dados inválidos)")


def teste_6_fallback_gracioso():
    """Teste 6: Fallback gracioso em caso de erro API"""
    print("\n" + "="*60)
    print("TESTE 6: Fallback Gracioso - Erro API")
    print("="*60)

    sistema = obter_sistema_transparency_radical()

    fallback = sistema.fallback_gracioso_api_falha(
        ativo="EURUSD",
        tipo_erro="Connection timeout"
    )

    assert "SERVIÇO DE ANÁLISE LIMITADO" in fallback
    assert "EURUSD" in fallback
    assert "Connection timeout" in fallback

    print(f"✅ Fallback gerado com {len(fallback)} caracteres")
    print("✅ TESTE 6 PASSOU")


def teste_7_rejeicao_qualidade():
    """Teste 7: Resposta de rejeição por qualidade"""
    print("\n" + "="*60)
    print("TESTE 7: Rejeição de Análise por Qualidade")
    print("="*60)

    sistema = obter_sistema_transparency_radical()

    resultado_validacao = {
        "valido": False,
        "erros": ["Dados > 60min: 120 minutos de atraso"],
        "avisos": [],
        "qualidade_score": 30,
    }

    resposta = sistema.gerar_resposta_rejeicao_qualidade(resultado_validacao)

    assert "ANÁLISE REJEITADA" in resposta
    assert "Dados > 60min" in resposta
    assert "30/100" in resposta

    print(f"✅ Resposta de rejeição gerada com {len(resposta)} caracteres")
    print("✅ TESTE 7 PASSOU")


def teste_8_serializacao():
    """Teste 8: Serialização para JSON e Markdown"""
    print("\n" + "="*60)
    print("TESTE 8: Serialização JSON e Markdown")
    print("="*60)

    sistema = obter_sistema_transparency_radical()

    # Adicionar um alerta para teste
    alerta = AlertaCritico(
        titulo="Teste",
        descricao="Alerta de teste",
        severidade=NivelSeveridade.CRITICO,
        metrica="teste",
        valor_atual=1,
        threshold_critico=0,
        acao_recomendada="Ação teste"
    )
    sistema.adicionar_alerta_critico(alerta)

    # Serializar para JSON
    json_data = sistema.para_json()
    json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

    print(f"✅ JSON gerado: {len(json_str)} caracteres")
    assert "transparencia_radical" in json_str
    assert "alertas_criticos" in json_str

    # Serializar para Markdown
    markdown = sistema.para_markdown()

    print(f"✅ Markdown gerado: {len(markdown)} caracteres")
    assert "TRANSPARÊNCIA RADICAL" in markdown
    assert "Confiança" in markdown

    print("✅ TESTE 8 PASSOU")


def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🧪 TESTES - US-RISCO-003: RADICAL TRANSPARENCY")
    print("="*60)

    try:
        teste_1_sistema_initialization()
        teste_2_downgrade_confianca()
        teste_3_disclaimer_obrigatorio()
        teste_4_alerta_critico()
        teste_5_validacao_qualidade()
        teste_6_fallback_gracioso()
        teste_7_rejeicao_qualidade()
        teste_8_serializacao()

        print("\n" + "="*60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
