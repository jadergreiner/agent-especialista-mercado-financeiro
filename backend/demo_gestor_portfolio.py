#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração do Sistema de Gestão de Portfolio
Exemplo de operação com novos tickets
"""

from gestor_portfolio_atualizado import GestorPortfolioAtualizado
import sys

def demonstrar_operacao_exemplo():
    """Demonstra operação com dados de exemplo"""

    print("🎯 DEMONSTRAÇÃO - NOVA OPERAÇÃO")
    print("=" * 40)

    # Criar instância do gestor
    gestor = GestorPortfolioAtualizado()

    # Dados da operação exemplo
    operacao_exemplo = {
        'ticket': '5314594313',
        'currency_pair': 'EURUSD',
        'direction': 'BUY',
        'lots': 0.05,
        'entry_price': 1.0855,
        'stop_loss': 1.0800,
        'take_profit': 1.0950,
        'strategy': 'Hedge USD - Redução de exposição'
    }

    print("\n📋 DADOS DA OPERAÇÃO:")
    for key, value in operacao_exemplo.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")

    print("\n🔄 PROCESSANDO...")

    # Processar operação
    sucesso = gestor.processar_nova_posicao(**operacao_exemplo)

    if sucesso:
        print("\n✅ OPERAÇÃO PROCESSADA COM SUCESSO!")

        # Gerar relatório pós-atualização
        print("\n" + "="*60)
        gestor.gerar_relatorio_pos_atualizacao()

    else:
        print("\n❌ FALHA NO PROCESSAMENTO DA OPERAÇÃO")

    return sucesso

def demonstrar_operacao_hedge_jpy():
    """Demonstra operação de hedge JPY"""

    print("\n🔶 OPERAÇÃO DE HEDGE JPY")
    print("=" * 30)

    gestor = GestorPortfolioAtualizado()

    # Operação de hedge para JPY
    hedge_jpy = {
        'ticket': 'HD002JPY',
        'currency_pair': 'USDJPY',
        'direction': 'BUY',
        'lots': 0.40,
        'entry_price': 154.25,
        'stop_loss': 152.00,
        'take_profit': 157.00,
        'strategy': 'Hedge JPY - Redução exposição negativa'
    }

    print("\n📋 HEDGE JPY:")
    for key, value in hedge_jpy.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")

    print("\n🔄 EXECUTANDO HEDGE...")

    sucesso = gestor.processar_nova_posicao(**hedge_jpy)

    if sucesso:
        print("\n✅ HEDGE JPY EXECUTADO!")
        gestor.gerar_relatorio_pos_atualizacao()

    return sucesso

def menu_interativo():
    """Menu interativo para operações"""

    print("\n" + "="*50)
    print("💼 GESTOR DO FUNDO - MENU INTERATIVO")
    print("="*50)

    print("\n📋 OPERAÇÕES DISPONÍVEIS:")
    print("   1. Demonstrar operação EURUSD")
    print("   2. Executar hedge JPY")
    print("   3. Relatório atual do portfolio")
    print("   4. Sair")

    return input("\n➤ Escolha uma opção (1-4): ").strip()

def gerar_relatorio_atual():
    """Gera relatório do estado atual"""

    gestor = GestorPortfolioAtualizado()

    print("\n📊 RELATÓRIO ATUAL DO PORTFOLIO")
    print("=" * 40)

    gestor.gerar_relatorio_pos_atualizacao()

def main():
    """Função principal interativa"""

    while True:
        opcao = menu_interativo()

        if opcao == '1':
            demonstrar_operacao_exemplo()
        elif opcao == '2':
            demonstrar_operacao_hedge_jpy()
        elif opcao == '3':
            gerar_relatorio_atual()
        elif opcao == '4':
            print("\n👋 Saindo do sistema...")
            break
        else:
            print("\n❌ Opção inválida!")

        input("\n⏸ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()