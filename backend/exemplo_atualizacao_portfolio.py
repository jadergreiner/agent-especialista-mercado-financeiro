#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo: Atualização do Portfólio com Relatório Executivo Completo
Demonstra o fluxo INICIO → DURANTE → FIM
"""

import os
import sys

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from gestor_portfolio_atualizado import GestorPortfolioAtualizado


def main():
    print("=" * 70)
    print("🎯 EXEMPLO: ATUALIZAÇÃO DE PORTFÓLIO COM RELATÓRIO EXECUTIVO")
    print("=" * 70)
    print()

    # INICIO: Criar gestor
    print("📋 INICIO: Carregando portfólio...")
    gestor = GestorPortfolioAtualizado()
    print()

    # Dados da nova posição (exemplo)
    dados_posicao = {
        'ticket': '#1234567890',
        'currency_pair': 'USD/JPY',
        'direction': 'LONG',
        'lots': 0.02,
        'entry_price': 149.85,
        'stop_loss': 148.50,
        'take_profit': 151.20,
        'strategy': 'Breakout técnico + Fed dovish'
    }

    print("📊 DURANTE: Processando nova posição...")
    print(f"   Ticket: {dados_posicao['ticket']}")
    print(f"   Par: {dados_posicao['currency_pair']}")
    print(f"   Direção: {dados_posicao['direction']}")
    print(f"   Volume: {dados_posicao['lots']} lotes")
    print(f"   Preço: {dados_posicao['entry_price']}")
    print()

    # DURANTE: Processar nova posição
    sucesso = gestor.processar_nova_posicao(
        ticket=dados_posicao['ticket'],
        currency_pair=dados_posicao['currency_pair'],
        direction=dados_posicao['direction'],
        lots=dados_posicao['lots'],
        entry_price=dados_posicao['entry_price'],
        stop_loss=dados_posicao['stop_loss'],
        take_profit=dados_posicao['take_profit'],
        strategy=dados_posicao['strategy']
    )

    print()

    if sucesso:
        # FIM: Gerar relatório executivo completo
        print("🎯 FIM: Gerando relatório executivo completo...")
        print()
        gestor.gerar_relatorio_pos_atualizacao()
    else:
        print("❌ Não foi possível processar a posição.")
        print("   Verifique se o ticket já existe ou se os dados estão inválidos.")


if __name__ == "__main__":
    main()
