"""
Script para Avaliar o Portfólio Atual
Gera relatório executivo completo sem necessidade de nova operação
"""

from gestor_fundo_completo import GestorFundoCompleto
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("\n" + "="*80)
    print("💼 AVALIAÇÃO COMPLETA DO PORTFÓLIO ATUAL")
    print("="*80 + "\n")

    try:
        # Inicializar gestor
        gestor = GestorFundoCompleto()

        # Carregar portfólio
        print("📂 Carregando portfólio...")
        gestor.carregar_portfolio()

        print("📊 Atualizando preços do mercado...")
        gestor.atualizar_precos_mercado()

        print("\n🔍 Gerando análise completa...\n")

        # Gerar relatório executivo
        relatorio = gestor.formatar_relatorio_executivo()

        # Exibir relatório
        print(relatorio)

        # Salvar relatório em arquivo
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_relatorio = f"relatorios/avaliacao_portfolio_{timestamp}.txt"

        import os
        os.makedirs("relatorios", exist_ok=True)

        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write(relatorio)

        print(f"\n💾 Relatório salvo em: {arquivo_relatorio}")

        # Perguntar se deseja ver recomendações detalhadas
        print("\n" + "="*80)
        resposta = input("📄 Deseja ver as recomendações detalhadas? (s/n): ").strip().lower()

        if resposta in ['s', 'sim', 'y', 'yes']:
            print("\n" + "="*80)
            print("💡 RECOMENDAÇÕES DETALHADAS")
            print("="*80 + "\n")

            resultado_recomendacoes = gestor.gerar_recomendacoes()

            if resultado_recomendacoes.get('detalhes'):
                detalhes = resultado_recomendacoes['detalhes']

                # Agrupar por tipo
                por_posicao = detalhes.get('posicoes_existentes', [])
                novas_oportunidades = detalhes.get('novas_oportunidades', [])
                alertas_risco = detalhes.get('gestao_risco', [])
                balanceamento = detalhes.get('balanceamento', [])

                # Mostrar recomendações por posição (primeiras 5)
                if por_posicao:
                    print("📋 GESTÃO DE POSIÇÕES (Primeiras 5):")
                    print("-" * 80)
                    for i, rec in enumerate(por_posicao[:5], 1):
                        # Se rec é string, exibir direto; se é dataclass/objeto, acessar atributos
                        if isinstance(rec, str):
                            print(f"\n{i}. {rec}")
                        else:
                            # rec é uma instância de RecomendacaoOperacao (dataclass)
                            ativo = getattr(rec, 'ativo', 'N/A')
                            razao = getattr(rec, 'razao', 'Sem descrição')
                            nivel = getattr(rec, 'nivel_confianca', 'N/A')
                            print(f"\n{i}. {ativo} - {razao}")
                            print(f"   🎯 Confiança: {nivel}")

                # Mostrar novas oportunidades
                if novas_oportunidades:
                    print(f"\n\n🆕 NOVAS OPORTUNIDADES ({len(novas_oportunidades)}):")
                    print("-" * 80)
                    for i, rec in enumerate(novas_oportunidades, 1):
                        if isinstance(rec, str):
                            print(f"\n{i}. {rec}")
                        else:
                            ativo = getattr(rec, 'ativo', 'N/A')
                            razao = getattr(rec, 'razao', 'Sem descrição')
                            preco = getattr(rec, 'preco_sugerido', None)
                            print(f"\n{i}. {ativo}")
                            print(f"   {razao}")
                            if preco:
                                print(f"   💰 Preço Sugerido: ${preco:.2f}")

                # Mostrar alertas de risco
                if alertas_risco:
                    print(f"\n\n🛡️ ALERTAS DE RISCO ({len(alertas_risco)}):")
                    print("-" * 80)
                    for i, rec in enumerate(alertas_risco, 1):
                        if isinstance(rec, str):
                            print(f"\n{i}. {rec}")
                        else:
                            ativo = getattr(rec, 'ativo', 'N/A')
                            razao = getattr(rec, 'razao', 'Alerta')
                            risco = getattr(rec, 'risco_estimado', 0)
                            print(f"\n{i}. {ativo}")
                            print(f"   {razao}")
                            if risco > 0:
                                print(f"   🚨 Risco: {risco:.1f}%")

                # Mostrar sugestões de balanceamento
                if balanceamento:
                    print(f"\n\n⚖️ SUGESTÕES DE BALANCEAMENTO ({len(balanceamento)}):")
                    print("-" * 80)
                    for i, rec in enumerate(balanceamento, 1):
                        if isinstance(rec, str):
                            print(f"\n{i}. {rec}")
                        else:
                            ativo = getattr(rec, 'ativo', 'N/A')
                            razao = getattr(rec, 'razao', 'Sugestão')
                            print(f"\n{i}. {ativo}")
                            print(f"   {razao}")

                print("\n" + "="*80)
                total_recs = len(por_posicao) + len(novas_oportunidades) + len(alertas_risco) + len(balanceamento)
                print(f"📊 Total de recomendações: {total_recs}")
            else:
                print("ℹ️ Nenhuma recomendação disponível no momento.")

        print("\n" + "="*80)
        print("✅ AVALIAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*80 + "\n")

    except FileNotFoundError:
        print("❌ ERRO: Arquivo de portfólio não encontrado!")
        print("   Verifique se 'data/portfolio/portfolio_atual.json' existe.")
    except Exception as e:
        print(f"❌ ERRO ao avaliar portfólio: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
