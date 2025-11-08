"""
Script para Exibir Recomendações Detalhadas do Portfólio
"""

from gestor_fundo_completo import GestorFundoCompleto
import logging

# Configurar logging mínimo
logging.basicConfig(level=logging.WARNING)

def formatar_recomendacao(rec) -> str:
    """Formatar uma recomendação individual"""
    if isinstance(rec, str):
        return rec

    # Se for um objeto RecomendacaoOperacao, extrair informações
    texto = []

    if hasattr(rec, 'tipo'):
        texto.append(f"📌 Tipo: {rec.tipo.value if hasattr(rec.tipo, 'value') else rec.tipo}")

    if hasattr(rec, 'ativo'):
        texto.append(f"📊 Ativo: {rec.ativo}")

    if hasattr(rec, 'acao_recomendada'):
        texto.append(f"🎯 Ação: {rec.acao_recomendada}")

    if hasattr(rec, 'racional'):
        texto.append(f"💡 Razão: {rec.racional}")

    if hasattr(rec, 'nivel_confianca'):
        confianca = rec.nivel_confianca.value if hasattr(rec.nivel_confianca, 'value') else rec.nivel_confianca
        texto.append(f"✅ Confiança: {confianca}")

    if hasattr(rec, 'preco_atual'):
        texto.append(f"💵 Preço Atual: ${rec.preco_atual:.5f}")

    if hasattr(rec, 'preco_entrada_sugerido') and rec.preco_entrada_sugerido:
        texto.append(f"🎯 Entrada Sugerida: ${rec.preco_entrada_sugerido:.5f}")

    if hasattr(rec, 'stop_loss_sugerido') and rec.stop_loss_sugerido:
        texto.append(f"🛑 Stop Loss: ${rec.stop_loss_sugerido:.5f}")

    if hasattr(rec, 'take_profit_sugerido') and rec.take_profit_sugerido:
        texto.append(f"🎁 Take Profit: ${rec.take_profit_sugerido:.5f}")

    if hasattr(rec, 'risk_reward') and rec.risk_reward:
        texto.append(f"⚖️  Risk/Reward: {rec.risk_reward}")

    if hasattr(rec, 'prazo_estimado'):
        texto.append(f"⏱️  Prazo: {rec.prazo_estimado}")

    return '\n   '.join(texto) if texto else str(rec)

def main():
    print("\n" + "="*80)
    print("💡 RECOMENDAÇÕES DETALHADAS DO PORTFÓLIO")
    print("="*80 + "\n")

    try:
        # Inicializar gestor
        gestor = GestorFundoCompleto()
        gestor.carregar_portfolio()

        print("🧠 Gerando recomendações inteligentes...")
        print("(Isso pode levar alguns segundos...)\n")

        # Gerar recomendações
        resultado = gestor.gerar_recomendacoes()

        if resultado.get('status') in ['ERRO', 'DESCONHECIDO']:
            print(f"❌ {resultado.get('message', 'Erro desconhecido')}")
            return

        # Extrair detalhes
        detalhes = resultado.get('detalhes', {})

        # 1. RECOMENDAÇÕES PARA POSIÇÕES EXISTENTES
        posicoes_existentes = detalhes.get('posicoes_existentes', [])
        if posicoes_existentes:
            print("="*80)
            print(f"📋 GESTÃO DE POSIÇÕES EXISTENTES ({len(posicoes_existentes)} recomendações)")
            print("="*80 + "\n")

            # Mostrar primeiras 10
            for i, rec in enumerate(posicoes_existentes[:10], 1):
                print(f"\n{i}. " + "-"*75)
                print("   " + formatar_recomendacao(rec))
                print()

            if len(posicoes_existentes) > 10:
                print(f"\n   ... e mais {len(posicoes_existentes) - 10} recomendações.")
        else:
            print("ℹ️  Nenhuma recomendação para posições existentes.")

        # 2. NOVAS OPORTUNIDADES
        novas_oportunidades = detalhes.get('novas_oportunidades', [])
        if novas_oportunidades:
            print("\n" + "="*80)
            print(f"🆕 NOVAS OPORTUNIDADES DE ENTRADA ({len(novas_oportunidades)} identificadas)")
            print("="*80 + "\n")

            for i, rec in enumerate(novas_oportunidades, 1):
                print(f"\n{i}. " + "-"*75)
                print("   " + formatar_recomendacao(rec))
                print()
        else:
            print("\nℹ️  Nenhuma nova oportunidade identificada no momento.")

        # 3. GESTÃO DE RISCO
        gestao_risco = detalhes.get('gestao_risco', [])
        if gestao_risco:
            print("\n" + "="*80)
            print(f"🛡️  ALERTAS DE GESTÃO DE RISCO ({len(gestao_risco)} alertas)")
            print("="*80 + "\n")

            for i, rec in enumerate(gestao_risco, 1):
                print(f"\n⚠️  ALERTA {i}:")
                print("   " + formatar_recomendacao(rec))
                print()
        else:
            print("\n✅ Nenhum alerta crítico de risco no momento.")

        # 4. BALANCEAMENTO
        balanceamento = detalhes.get('balanceamento', [])
        if balanceamento:
            print("\n" + "="*80)
            print(f"⚖️  SUGESTÕES DE BALANCEAMENTO ({len(balanceamento)} sugestões)")
            print("="*80 + "\n")

            for i, rec in enumerate(balanceamento, 1):
                print(f"\n{i}. " + "-"*75)
                print("   " + formatar_recomendacao(rec))
                print()
        else:
            print("\n✅ Portfólio está bem balanceado.")

        # RESUMO FINAL
        print("\n" + "="*80)
        print("📊 RESUMO DAS RECOMENDAÇÕES")
        print("="*80)
        print(f"📋 Gestão de Posições: {len(posicoes_existentes)}")
        print(f"🆕 Novas Oportunidades: {len(novas_oportunidades)}")
        print(f"🛡️  Alertas de Risco: {len(gestao_risco)}")
        print(f"⚖️  Balanceamento: {len(balanceamento)}")
        print(f"📈 Total: {len(posicoes_existentes) + len(novas_oportunidades) + len(gestao_risco) + len(balanceamento)}")
        print("="*80 + "\n")

        print("✅ Análise de recomendações concluída!")
        print("\n💡 Dica: Use essas recomendações como guia, mas sempre valide")
        print("   com sua própria análise e gestão de risco.\n")

    except Exception as e:
        print(f"❌ ERRO ao gerar recomendações: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
