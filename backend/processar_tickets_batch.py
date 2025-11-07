#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Tickets em Lote
Sistema para adicionar múltiplas posições via tickets de forma segura
"""

import json
from datetime import datetime
import os

def processar_tickets_batch():
    """Processa múltiplos tickets de uma vez"""

    # Carregar portfolio atual
    portfolio_path = 'data/portfolio/portfolio_atual.json'
    with open(portfolio_path, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)

    # Tickets validados para processar
    tickets = [
        {'ticket': '5313534825', 'action': 'BUY', 'pair': 'CHF/JPY', 'lots': 0.01, 'price': 190.178},
        {'ticket': '5307171093', 'action': 'SELL', 'pair': 'EUR/AUD', 'lots': 0.01, 'price': 1.76374},
        {'ticket': '5312229393', 'action': 'SELL', 'pair': 'EUR/CAD', 'lots': 0.01, 'price': 1.61727},
        {'ticket': '5312253606', 'action': 'BUY', 'pair': 'EUR/CHF', 'lots': 0.01, 'price': 0.93018},
        {'ticket': '5308478433', 'action': 'SELL', 'pair': 'EUR/GBP', 'lots': 0.01, 'price': 0.87972},
        {'ticket': '5313548511', 'action': 'BUY', 'pair': 'EUR/JPY', 'lots': 0.01, 'price': 177.024}
    ]

    print('🎫 PROCESSANDO 6 TICKETS EM LOTE...')
    print('=' * 50)

    # Encontrar próximo position_id
    max_id = 0
    for pos in portfolio['positions']:
        pos_id = int(pos['position_id'].split('_')[1])
        max_id = max(max_id, pos_id)

    next_id = max_id + 1

    # Adicionar cada ticket como nova posição
    for i, ticket in enumerate(tickets):
        position_id = f'pos_{next_id + i:03d}'

        direction = 'LONG' if ticket['action'] == 'BUY' else 'SHORT'

        pair = ticket['pair']
        action = ticket['action']
        price = ticket['price']
        ticket_num = ticket['ticket']

        nova_posicao = {
            'position_id': position_id,
            'currency_pair': pair,
            'direction': direction,
            'entry_price': price,
            'current_price': price,
            'lots': ticket['lots'],
            'lot_size': 100000,
            'entry_date': datetime.now().isoformat() + 'Z',
            'stop_loss': None,
            'take_profit': [],
            'pnl_unrealized': 0.0,
            'pnl_realized': 0,
            'strategy': f'Ticket Operation - {pair} {action}',
            'risk_percentage': 0.1,
            'notes': f'Ticket #{ticket_num} - {action} {pair} @ {price}',
            'status': 'OPEN',
            'ticket': ticket_num
        }

        portfolio['positions'].append(nova_posicao)
        print(f'✅ #{ticket_num}: {direction} {pair} @ {price}')

    # Atualizar metadata
    portfolio['portfolio_metadata']['last_update'] = datetime.now().isoformat() + '+00:00'

    # Salvar portfolio atualizado
    with open(portfolio_path, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, indent=2, ensure_ascii=False)

    print('\n📊 RESULTADO:')
    print('=' * 50)
    print(f'✅ Posições totais: {len(portfolio["positions"])}')
    print(f'✅ Última atualização: {portfolio["portfolio_metadata"]["last_update"]}')
    print(f'✅ Portfolio salvo em: {os.path.abspath(portfolio_path)}')

    return True

if __name__ == "__main__":
    processar_tickets_batch()