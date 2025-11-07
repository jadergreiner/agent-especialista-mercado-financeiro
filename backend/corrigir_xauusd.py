#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corretor de Duplicação XAUUSD
Sistema para corrigir erro de cadastro duplo da posição de ouro
"""

import json
from datetime import datetime
import os

def corrigir_duplicacao_xauusd():
    """Corrige a duplicação incorreta de XAUUSD no portfolio"""

    # Carregar portfolio atual
    portfolio_path = 'data/portfolio/portfolio_atual.json'
    with open(portfolio_path, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)

    print('🔧 CORREÇÃO DE ERRO DE CADASTRO XAUUSD...')
    print('=' * 60)

    # Localizar posições XAUUSD/XAU/USD
    posicoes_ouro = []
    outras_posicoes = []

    for pos in portfolio['positions']:
        currency_pair = pos.get('currency_pair', '')
        if currency_pair in ['XAUUSD', 'XAU/USD']:
            posicoes_ouro.append(pos)
            print(f'🔍 Encontrada posição ouro: {pos["position_id"]} - {currency_pair} - {pos.get("ticket", "sem ticket")}')
        else:
            outras_posicoes.append(pos)

    print(f'\\n📊 ANÁLISE:')
    print(f'   Posições de ouro encontradas: {len(posicoes_ouro)}')
    print(f'   Outras posições: {len(outras_posicoes)}')

    if len(posicoes_ouro) == 0:
        print('\\n❌ ERRO: Nenhuma posição de ouro encontrada!')
        return False

    if len(posicoes_ouro) == 1:
        print('\\n✅ Apenas 1 posição de ouro encontrada - SEM DUPLICAÇÃO')
        # Verificar se é a posição correta
        pos_ouro = posicoes_ouro[0]
        ticket_correto = pos_ouro.get('ticket') == '5314594312'
        preco_correto = pos_ouro.get('entry_price') == 3983.25

        if ticket_correto and preco_correto:
            print(f'✅ Posição correta já cadastrada: Ticket #{pos_ouro["ticket"]} @ {pos_ouro["entry_price"]}')
            return True
        else:
            print(f'⚠️  Posição com dados incorretos:')
            print(f'   Ticket: {pos_ouro.get("ticket")} (esperado: 5314594312)')
            print(f'   Preço: {pos_ouro.get("entry_price")} (esperado: 3983.25)')

    print(f'\\n🔧 INICIANDO CORREÇÃO...')

    # Remover todas as posições de ouro incorretas
    posicoes_removidas = []
    for pos in posicoes_ouro:
        ticket = pos.get('ticket', 'sem ticket')
        if ticket != '5314594312':
            posicoes_removidas.append(pos)
            print(f'❌ Removendo posição incorreta: {pos["position_id"]} - Ticket: {ticket}')

    # Verificar se a posição correta já existe
    posicao_correta_existe = False
    for pos in posicoes_ouro:
        if pos.get('ticket') == '5314594312' and pos.get('entry_price') == 3983.25:
            posicao_correta_existe = True
            print(f'✅ Posição correta mantida: {pos["position_id"]} - Ticket: #5314594312')
            break

    # Adicionar a posição correta se não existir
    if not posicao_correta_existe:
        print(f'➕ Adicionando posição correta...')

        # Encontrar próximo position_id
        max_id = 0
        for pos in outras_posicoes:
            pos_id = int(pos['position_id'].split('_')[1])
            max_id = max(max_id, pos_id)

        nova_posicao_ouro = {
            'position_id': f'pos_{max_id + 1:03d}',
            'currency_pair': 'XAU/USD',
            'direction': 'LONG',
            'entry_price': 3983.25,
            'current_price': 3983.25,
            'lots': 0.01,
            'lot_size': 100000,
            'entry_date': datetime.now().isoformat() + 'Z',
            'stop_loss': None,
            'take_profit': [],
            'pnl_unrealized': 0.0,
            'pnl_realized': 0,
            'strategy': 'Ticket Operation Lote 2 - XAU/USD BUY',
            'risk_percentage': 0.1,
            'notes': 'Ticket #5314594312 - BUY XAU/USD @ 3983.25',
            'status': 'OPEN',
            'ticket': '5314594312'
        }

        outras_posicoes.append(nova_posicao_ouro)
        print(f'✅ Posição correta adicionada: {nova_posicao_ouro["position_id"]}')
    else:
        # Manter apenas a posição correta
        for pos in posicoes_ouro:
            if pos.get('ticket') == '5314594312':
                outras_posicoes.append(pos)

    # Reconstruir portfolio com posições corretas
    portfolio['positions'] = outras_posicoes
    portfolio['portfolio_metadata']['last_update'] = datetime.now().isoformat() + '+00:00'

    # Salvar portfolio corrigido
    with open(portfolio_path, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, indent=2, ensure_ascii=False)

    print(f'\\n📊 RESULTADO FINAL:')
    print('=' * 60)
    print(f'✅ Posições totais: {len(portfolio["positions"])}')
    print(f'✅ Posições de ouro removidas: {len(posicoes_removidas)}')
    print(f'✅ Posição correta mantida: XAU/USD Ticket #5314594312 @ 3983.25')
    print(f'✅ Portfolio corrigido em: {os.path.abspath(portfolio_path)}')

    return True

if __name__ == "__main__":
    corrigir_duplicacao_xauusd()