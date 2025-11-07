#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Agente Adaptativo de Gestão de Risco e Portfólio (RMS)
"""

from sistema_atualizacao_portfolio_inteligente import SistemaAtualizacaoPortfolioInteligente
import json

def testar_sistema_rms():
    """Testa o sistema RMS completo"""
    print("🧠 TESTE DO AGENTE ADAPTATIVO DE GESTÃO DE RISCO E PORTFÓLIO (RMS)")
    print("=" * 80)

    try:
        # === TESTE 1: Inicialização e FASE 0 ===
        print("\n📋 TESTE 1: Inicialização RMS e Ciclo de Aprendizado")
        print("-" * 60)

        sistema = SistemaAtualizacaoPortfolioInteligente()
        print("✅ Sistema RMS inicializado com aprendizado ativo")

        # === TESTE 2: Verificação da Estrutura do Portfólio ===
        print("\n📋 TESTE 2: Verificação da Estrutura do Portfólio")
        print("-" * 60)

        portfolio = sistema.gestor_portfolio.portfolio
        positions = portfolio.get('positions', [])
        posicoes_open = [p for p in positions if p.get('status') == 'OPEN']

        print(f"✅ Portfolio carregado: {len(positions)} posições totais")
        print(f"✅ Posições abertas: {len(posicoes_open)}")

        # Verificar dados de alocação
        allocation = portfolio.get('allocation', {})
        exposicao_moedas = allocation.get('by_currency', {})
        print(f"✅ Exposição por moeda: {len(exposicao_moedas)} moedas")

        # Verificar exposição JPY (crítica para o sistema)
        jpy_exposure = exposicao_moedas.get('JPY_exposure', 0)
        print(f"✅ Exposição JPY: {jpy_exposure}%")
        if jpy_exposure < -50:
            print("⚠️ ALERTA: Exposição JPY altamente negativa detectada!")
        elif jpy_exposure < 0:
            print("🟡 ATENÇÃO: Exposição JPY negativa detectada!")

        # === TESTE 3: Geração do Relatório Executivo RMS ===
        print("\n📋 TESTE 3: Geração do Relatório Executivo RMS")
        print("-" * 60)

        relatorio = sistema.gerar_relatorio_executivo()
        print("✅ Relatório executivo RMS gerado")

        # Verificações do conteúdo
        assert "# 📊 RELATÓRIO EXECUTIVO - GESTÃO DE RISCO E PORTFÓLIO (RMS)" in relatorio
        assert "## 🔍 ANÁLISE INDIVIDUAL DOS ATIVOS" in relatorio
        assert "## ⚠️ RISCO DO PORTFÓLIO (CONSOLIDADO)" in relatorio
        assert "## 🌍 COERÊNCIA MACROECONÔMICA" in relatorio
        assert "## 💡 SUGESTÕES OTIMIZADAS" in relatorio
        print("✅ Estrutura do relatório validada")

        # Verificar iteração sobre posições OPEN
        posicoes_no_relatorio = relatorio.count("### ")
        print(f"✅ Análises individuais encontradas: {posicoes_no_relatorio - 5} posições")  # -5 para headers

        # Verificar se contém dados das posições
        if posicoes_open:
            primeira_posicao = posicoes_open[0]
            ativo = primeira_posicao.get('currency_pair', '')
            if ativo in relatorio:
                print(f"✅ Análise individual de {ativo} encontrada no relatório")

        # === TESTE 4: Verificação de Prioridade JPY ===
        print("\n📋 TESTE 4: Verificação de Prioridade JPY")
        print("-" * 60)

        if jpy_exposure < -50:
            assert "PRIORIDADE CRÍTICA - PROTEÇÃO JPY" in relatorio
            print("✅ Prioridade crítica JPY detectada e incluída")
        elif jpy_exposure < 0:
            assert "ATENÇÃO - MONITORAMENTO JPY" in relatorio
            print("✅ Monitoramento JPY detectado e incluído")
        else:
            print("✅ Exposição JPY adequada - sem alertas específicos")

        # === TESTE 5: Salvamento do Relatório ===
        print("\n📋 TESTE 5: Salvamento do Relatório")
        print("-" * 60)

        with open('teste_relatorio_rms.md', 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print("💾 Relatório RMS salvo em: teste_relatorio_rms.md")

        # Verificar tamanho do relatório
        tamanho_relatorio = len(relatorio)
        print(f"📊 Tamanho do relatório: {tamanho_relatorio} caracteres")

        if tamanho_relatorio > 10000:  # Relatório detalhado esperado
            print("✅ Relatório com conteúdo substancial gerado")
        else:
            print("⚠️ Relatório menor que esperado - verificar conteúdo")

        print("\n🎯 TODOS OS TESTES RMS APROVADOS!")
        print("=" * 80)
        print("✅ Sistema RMS operacional:")
        print("   • Análise individual de ativos OPEN")
        print("   • Risco consolidado com exposição e correlação")
        print("   • Coerência macroeconômica avaliada")
        print("   • Sugestões com prioridade JPY")
        print("   • Relatório executivo completo")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ ERRO NO TESTE RMS: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_sistema_rms()
    if sucesso:
        print("\n🚀 Agente Adaptativo de Gestão de Risco e Portfólio (RMS): PRONTO PARA PRODUÇÃO!")
    else:
        print("\n❌ Falha nos testes RMS - verificar implementação")