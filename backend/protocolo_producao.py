#!/usr/bin/env python3
"""
PROTOCOLO DE ACIONAMENTO DO MOTOR ML - MODO PRODUÇÃO
Captura oportunidades reais de mercado para execução imediata
"""

import json
import os
import sys
from datetime import datetime
from motor_oportunidades_integrado import MotorOportunidadesMacro
from analisador_oportunidades_forex import AnalisadorOportunidadesForex

def executar_protocolo_producao():
    """Executar protocolo completo de captura de oportunidades reais"""

    print("🚀 PROTOCOLO DE ACIONAMENTO - MODO PRODUÇÃO")
    print("=" * 60)

    # Carregar configuração de produção
    config_path = "config_producao.json"

    if not os.path.exists(config_path):
        print("❌ Arquivo de configuração não encontrado!")
        return False

    print(f"📋 Carregando configuração: {config_path}")

    # Carregar portfolio da configuração
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    portfolio_producao = config.get('portfolio_principal', [
        'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'AMZN',
        'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCAD=X', 'USDCHF=X'
    ])

    print(f"📊 Portfolio de produção: {len(portfolio_producao)} ativos")
    acoes = len([x for x in portfolio_producao if not x.endswith('=X')])
    forex = len([x for x in portfolio_producao if x.endswith('=X')])
    print(f"   🏢 Ações: {acoes}")
    print(f"   💱 FOREX: {forex}")

    # Inicializar motor em modo produção
    try:
        print("\n🔧 Inicializando motor de produção...")
        motor = MotorOportunidadesMacro(portfolio=portfolio_producao)

        # Executar análise completa
        print("\n🔄 EXECUTANDO ANÁLISE DE PRODUÇÃO...")
        resultado = motor.executar_ciclo_completo()

        print("\n📈 RESULTADO DA ANÁLISE DE PRODUÇÃO:")
        oportunidades = resultado.get('oportunidades_identificadas', [])
        print(f"🎯 Oportunidades encontradas: {len(oportunidades)}")

        if oportunidades:
            print("\n🎯 OPORTUNIDADES DETECTADAS (PRODUÇÃO):")
            for i, op in enumerate(oportunidades[:10], 1):
                ticker = op.get('ticker', 'N/A')
                tipo = op.get('tipo_oportunidade', 'N/A')
                score = op.get('score_final', 0)
                risco_recompensa = op.get('risco_recompensa', 0)

                # Classificar confiança baseada no score
                if score >= 0.8:
                    confianca = "MUITO_ALTA"
                    emoji = "🔥"
                elif score >= 0.7:
                    confianca = "ALTA"
                    emoji = "✅"
                elif score >= 0.6:
                    confianca = "MEDIA"
                    emoji = "⚠️"
                else:
                    confianca = "BAIXA"
                    emoji = "❌"

                print(f"   {i}. {emoji} {ticker}: {tipo}")
                print(f"      📊 Score: {score:.2f} ({confianca})")
                print(f"      🎯 Risco/Recompensa: {risco_recompensa:.2f}")

                if risco_recompensa > 2:
                    print("      💰 EXECUTAR - Alto potencial de ganho")
                elif risco_recompensa > 1.5:
                    print("      📈 CONSIDERAR - Potencial moderado")
                else:
                    print("      ⚠️ MONITORAR - Risco elevado")
        else:
            print("   ℹ️ Nenhuma oportunidade identificada no momento")
            print("   Sistema continuará monitorando...")

        # === ANÁLISE ESPECÍFICA DE FOREX ===
        print("\n💱 ANALISANDO OPORTUNIDADES ESPECÍFICAS FOREX...")
        try:
            analisador_forex = AnalisadorOportunidadesForex()
            resultado_forex = analisador_forex.analisar_oportunidades_forex()

            # TAKE PROFIT
            tp_oportunidades = resultado_forex.get('oportunidades_take_profit', [])
            if tp_oportunidades:
                print(f"\n💰 TAKE PROFIT DETECTADO ({len(tp_oportunidades)} oportunidades):")
                for i, op in enumerate(tp_oportunidades, 1):
                    print(f"   {i}. {op['par']} - {op['direcao']}")
                    print(f"      📊 Preço atual: {op['preco_atual']}")
                    print(f"      🎯 TP em: {op['nivel_tp']} (+{op['potencial_ganho_pct']}%)")
                    print(f"      💯 Confiança: {op['confianca']}")
                    print(f"      📝 {op['justificativa']}")

            # REFORÇO DE POSIÇÃO
            reforco_oportunidades = resultado_forex.get('oportunidades_reforco', [])
            if reforco_oportunidades:
                print(f"\n📈 REFORÇO DE POSIÇÃO ({len(reforco_oportunidades)} oportunidades):")
                for i, op in enumerate(reforco_oportunidades, 1):
                    print(f"   {i}. {op['par']} - {op['direcao']}")
                    print(f"      📊 Preço atual: {op['preco_atual']}")
                    print(f"      🎯 Entrada em: {op['nivel_entrada']}")
                    print(f"      📊 RSI: {op['rsi_atual']}")
                    print(f"      💯 Confiança: {op['confianca']}")
                    print(f"      📝 {op['justificativa']}")

            # HEDGE
            hedge_oportunidades = resultado_forex.get('oportunidades_hedge', [])
            if hedge_oportunidades:
                print(f"\n🛡️ OPORTUNIDADES DE HEDGE ({len(hedge_oportunidades)} pares):")
                for i, op in enumerate(hedge_oportunidades, 1):
                    print(f"   {i}. {op['par_principal']} ↔ {op['par_hedge']}")
                    print(f"      📊 Correlação: {op['correlacao']}")
                    print(f"      💯 Eficácia: {op['eficacia']}")
                    print(f"      📝 {op['justificativa']}")

            # CORRELAÇÃO
            correlacao = resultado_forex.get('analise_correlacao', {})
            if correlacao.get('pares_mais_correlacionados'):
                print(f"\n📊 ANÁLISE DE CORRELAÇÃO:")
                print("   Pares mais correlacionados:")
                for par_corr in correlacao['pares_mais_correlacionados']:
                    print(f"      {par_corr['par1']} ↔ {par_corr['par2']}: {par_corr['correlacao']}")

                print("   Pares menos correlacionados:")
                for par_corr in correlacao['pares_menos_correlacionados']:
                    print(f"      {par_corr['par1']} ↔ {par_corr['par2']}: {par_corr['correlacao']}")

                if correlacao.get('insights_correlacao'):
                    print("   💡 Insights:")
                    for insight in correlacao['insights_correlacao']:
                        print(f"      • {insight}")

            # Métricas Forex
            metricas_forex = resultado_forex.get('metricas_gerais', {})
            if metricas_forex:
                print(f"\n📈 MÉTRICAS FOREX:")
                print(f"   🎯 TP: {metricas_forex.get('total_oportunidades_tp', 0)}")
                print(f"   📈 Reforço: {metricas_forex.get('total_oportunidades_reforco', 0)}")
                print(f"   🛡️ Hedge: {metricas_forex.get('total_oportunidades_hedge', 0)}")
                print(f"   💱 Pares analisados: {metricas_forex.get('pares_analisados', 0)}")

        except Exception as e:
            print(f"⚠️ Erro na análise Forex (dados podem não estar disponíveis): {e}")

        status = resultado.get('status_geral', 'N/A')
        print(f"\n⚙️ Status geral: {status}")

        # Verificar etapas executadas
        etapas = resultado.get('etapas_executadas', {})
        print("\n📋 Etapas executadas:")
        for nome, info in etapas.items():
            status_etapa = info.get('status', 'desconhecido') if isinstance(info, dict) else 'concluida'
            emoji = '✅' if status_etapa in ['concluida', 'sucesso'] else '❌'
            nome_formatado = nome.replace('_', ' ').title()
            print(f'   {emoji} {nome_formatado}: {status_etapa}')

        print("\n✅ SISTEMA OPERACIONAL EM MODO PRODUÇÃO")
        print("🔄 Pronto para próximo ciclo em 15 minutos")
        print("📊 Dados salvos automaticamente")

        return True

    except Exception as e:
        print(f"❌ ERRO NO PROTOCOLO DE PRODUÇÃO: {e}")
        return False

if __name__ == "__main__":
    sucesso = executar_protocolo_producao()
    sys.exit(0 if sucesso else 1)