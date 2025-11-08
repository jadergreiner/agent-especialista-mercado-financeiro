#!/usr/bin/env python3
"""
CLI para Sistema de Aprendizado Contínuo
Interface de linha de comando para executar análises de performance

Uso:
    python cli_aprendizado_continuo.py analisar --id 42 --resultado "ACERTOU" --movimento "WIN +380pts" --eventos "Dados EUA"
    python cli_aprendizado_continuo.py metricas
    python cli_aprendizado_continuo.py ajustar-pesos --score-macro 0.05 --score-tecnico 0.03
"""

import argparse
import sys
import os
from datetime import datetime

# Adicionar backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sistema_aprendizado_continuo import SistemaAprendizadoContinuo


def comando_analisar(args):
    """Executa análise de performance de uma recomendação"""

    sistema = SistemaAprendizadoContinuo()

    print(f"🧠 Executando análise de aprendizado contínuo...")
    print(f"Recomendação ID: {args.id}")
    print(f"Resultado: {args.resultado}")
    print(f"Movimento: {args.movimento}")
    print(f"Eventos: {args.eventos}")
    print("-" * 60)

    # Executar análise
    relatorio = sistema.executar_prompt_aprendizado(
        recomendacao_id=args.id,
        resultado_real=args.resultado,
        movimento_preco_observado=args.movimento,
        eventos_ocorridos=args.eventos
    )

    print(relatorio)

    # Perguntar se quer aplicar ajustes
    resposta = input("\n🔄 Deseja aplicar os ajustes sugeridos? (s/n): ").lower().strip()

    if resposta == 's':
        # Extração simplificada dos ajustes (em produção, seria mais robusta)
        # Aqui assumimos que os ajustes estão no formato específico do relatório
        ajustes = {}
        linhas = relatorio.split('\n')
        for linha in linhas:
            if 'score_macro' in linha.lower() and '+' in linha:
                try:
                    valor = float(linha.split('+')[1].split('%')[0]) / 100
                    ajustes['score_macro'] = valor
                except:
                    pass
            elif 'score_tecnico' in linha.lower() and '+' in linha:
                try:
                    valor = float(linha.split('+')[1].split('%')[0]) / 100
                    ajustes['score_tecnico'] = valor
                except:
                    pass

        if ajustes:
            print(f"\n🔧 Aplicando ajustes: {ajustes}")
            novos_pesos = sistema.aplicar_ajustes_pesos(ajustes)
            print(f"✅ Novos pesos: {novos_pesos}")
        else:
            print("⚠️ Não foi possível extrair ajustes automaticamente")

    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analise_performance_rec_{args.id}_{timestamp}.md"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(relatorio)

    print(f"\n💾 Relatório salvo: {filename}")


def comando_metricas(args):
    """Exibe métricas do sistema de aprendizado"""

    sistema = SistemaAprendizadoContinuo()

    print("📊 MÉTRICAS DO SISTEMA DE APRENDIZADO CONTÍNUO")
    print("=" * 60)

    metricas = sistema.obter_metricas_aprendizado()

    if "erro" in metricas:
        print(f"❌ Erro: {metricas['erro']}")
        return

    print(f"📈 Total de análises realizadas: {metricas['total_analises']}")
    print(".1f"    print(".1f"    print(f"📊 Distribuição: {metricas['acertos']} acertos / {metricas['erros']} erros")
    print(f"🔄 Total de ajustes aplicados: {metricas['historico_ajustes']}")
    print("")

    print("⚖️ PESOS ATUAIS DO SISTEMA:")
    for fator, peso in metricas['pesos_atuais'].items():
        print("6.1%")

    if metricas['ajustes_recentes']:
        print("
🔧 ÚLTIMOS AJUSTES REALIZADOS:"        for i, ajuste in enumerate(metricas['ajustes_recentes'][:3], 1):
            print(f"   {i}. {ajuste}")


def comando_ajustar_pesos(args):
    """Aplica ajustes manuais aos pesos do sistema"""

    sistema = SistemaAprendizadoContinuo()

    # Coletar ajustes dos argumentos
    ajustes = {}

    if args.score_macro is not None:
        ajustes['score_macro'] = args.score_macro
    if args.score_tecnico is not None:
        ajustes['score_tecnico'] = args.score_tecnico
    if args.volatilidade is not None:
        ajustes['volatilidade'] = args.volatilidade
    if args.juros is not None:
        ajustes['juros'] = args.juros
    if args.moeda is not None:
        ajustes['moeda'] = args.moeda
    if args.commodities is not None:
        ajustes['commodities'] = args.commodities
    if args.equity is not None:
        ajustes['equity'] = args.equity

    if not ajustes:
        print("❌ Nenhum ajuste especificado")
        return

    print("🔧 Aplicando ajustes manuais aos pesos:")
    for fator, ajuste in ajustes.items():
        simbolo = "+" if ajuste >= 0 else ""
        print(f"   {fator}: {simbolo}{ajuste:.1%}")

    resposta = input("\n✅ Confirmar aplicação? (s/n): ").lower().strip()

    if resposta == 's':
        novos_pesos = sistema.aplicar_ajustes_pesos(ajustes)
        print("
✅ Pesos atualizados com sucesso!"        print(f"   Novos pesos: {novos_pesos}")
    else:
        print("❌ Operação cancelada")


def main():
    parser = argparse.ArgumentParser(
        description="CLI para Sistema de Aprendizado Contínuo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

# Analisar performance de uma recomendação
python cli_aprendizado_continuo.py analisar --id 42 --resultado "ACERTOU - TP1" --movimento "WIN +380pts em 3.5h" --eventos "Dados EUA, Fed dovish"

# Ver métricas do sistema
python cli_aprendizado_continuo.py metricas

# Ajustar pesos manualmente
python cli_aprendizado_continuo.py ajustar-pesos --score-macro 0.05 --score-tecnico -0.02
        """
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponíveis')

    # Comando: analisar
    parser_analisar = subparsers.add_parser('analisar', help='Executar análise de performance')
    parser_analisar.add_argument('--id', type=int, required=True, help='ID da recomendação')
    parser_analisar.add_argument('--resultado', required=True, help='Resultado real (ACERTOU/ERROU/etc)')
    parser_analisar.add_argument('--movimento', required=True, help='Movimento de preço observado')
    parser_analisar.add_argument('--eventos', required=True, help='Eventos que ocorreram')

    # Comando: metricas
    parser_metricas = subparsers.add_parser('metricas', help='Exibir métricas do sistema')

    # Comando: ajustar-pesos
    parser_ajustes = subparsers.add_parser('ajustar-pesos', help='Aplicar ajustes manuais aos pesos')
    parser_ajustes.add_argument('--score-macro', type=float, help='Ajuste no peso do score macro (+/-)')
    parser_ajustes.add_argument('--score-tecnico', type=float, help='Ajuste no peso do score técnico (+/-)')
    parser_ajustes.add_argument('--volatilidade', type=float, help='Ajuste no peso da volatilidade (+/-)')
    parser_ajustes.add_argument('--juros', type=float, help='Ajuste no peso dos juros (+/-)')
    parser_ajustes.add_argument('--moeda', type=float, help='Ajuste no peso da moeda (+/-)')
    parser_ajustes.add_argument('--commodities', type=float, help='Ajuste no peso das commodities (+/-)')
    parser_ajustes.add_argument('--equity', type=float, help='Ajuste no peso do equity (+/-)')

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        return

    # Executar comando apropriado
    if args.comando == 'analisar':
        comando_analisar(args)
    elif args.comando == 'metricas':
        comando_metricas(args)
    elif args.comando == 'ajustar-pesos':
        comando_ajustar_pesos(args)


if __name__ == "__main__":
    main()