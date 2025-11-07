#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Tickets em Lote - Lote 2
Sistema para adicionar múltiplas posições via tickets de forma segura
"""

import json
from datetime import datetime
import os

def processar_tickets_lote2():
    """Processa o segundo lote de 9 tickets"""

    # Carregar portfolio atual
    portfolio_path = 'data/portfolio/portfolio_atual.json'
    with open(portfolio_path, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)

    # Novos tickets para processar - LOTE 2
    tickets = [
        {'ticket': '5312231336', 'action': 'SELL', 'pair': 'EUR/NZD', 'lots': 0.01, 'price': 2.02770},
        {'ticket': '5314589754', 'action': 'SELL', 'pair': 'EUR/USD', 'lots': 0.01, 'price': 1.15388},
        {'ticket': '5307192783', 'action': 'BUY', 'pair': 'GBP/JPY', 'lots': 0.01, 'price': 201.327},
        {'ticket': '5313579295', 'action': 'SELL', 'pair': 'GBP/NZD', 'lots': 0.01, 'price': 2.30341},
        {'ticket': '5308486753', 'action': 'BUY', 'pair': 'NZD/CAD', 'lots': 0.01, 'price': 0.80171},
        {'ticket': '5313792116', 'action': 'BUY', 'pair': 'NZD/CAD', 'lots': 0.01, 'price': 0.79895},
        {'ticket': '5308487664', 'action': 'BUY', 'pair': 'NZD/CHF', 'lots': 0.01, 'price': 0.45961},
        {'ticket': '5312258069', 'action': 'BUY', 'pair': 'USD/CHF', 'lots': 0.01, 'price': 0.81021},
        {'ticket': '5314594312', 'action': 'BUY', 'pair': 'XAU/USD', 'lots': 0.01, 'price': 3983.25}
    ]

    print('🎫 VERIFICANDO TICKETS DUPLICADOS - LOTE 2...')
    print('=' * 60)

    # Verificar tickets existentes
    tickets_existentes = []
    for pos in portfolio['positions']:
        if 'ticket' in pos:
            tickets_existentes.append(pos['ticket'])

    print(f'📋 Tickets já existentes no portfolio: {len(tickets_existentes)}')

    # Verificar duplicados
    tickets_novos = []
    tickets_duplicados = []

    for ticket in tickets:
        ticket_id = ticket['ticket']
        if ticket_id in tickets_existentes:
            print(f'❌ Ticket {ticket_id} JÁ EXISTE - IGNORANDO')
            tickets_duplicados.append(ticket_id)
        else:
            print(f'✅ Ticket {ticket_id} VÁLIDO - PROCESSANDO')
            tickets_novos.append(ticket)

    print(f'\\n📊 RESUMO VALIDAÇÃO:')
    print(f'   Tickets enviados: {len(tickets)}')
    print(f'   Tickets duplicados: {len(tickets_duplicados)}')
    print(f'   Tickets válidos: {len(tickets_novos)}')

    if len(tickets_novos) == 0:
        print('\\n⚠️  NENHUM TICKET NOVO PARA PROCESSAR')
        return False

    print(f'\\n🎫 PROCESSANDO {len(tickets_novos)} TICKETS VÁLIDOS...')
    print('=' * 60)

    # Encontrar próximo position_id
    max_id = 0
    for pos in portfolio['positions']:
        pos_id = int(pos['position_id'].split('_')[1])
        max_id = max(max_id, pos_id)

    next_id = max_id + 1

    # Adicionar cada ticket como nova posição
    for i, ticket in enumerate(tickets_novos):
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
            'strategy': f'Ticket Operation Lote 2 - {pair} {action}',
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

    print('\\n📊 RESULTADO FINAL:')
    print('=' * 60)
    print(f'✅ Posições totais: {len(portfolio["positions"])}')
    print(f'✅ Novas posições adicionadas: {len(tickets_novos)}')
    print(f'✅ Última atualização: {portfolio["portfolio_metadata"]["last_update"]}')
    print(f'✅ Portfolio salvo em: {os.path.abspath(portfolio_path)}')

    if tickets_duplicados:
        print(f'\\n⚠️  TICKETS DUPLICADOS IGNORADOS:')
        for ticket_id in tickets_duplicados:
            print(f'   - {ticket_id}')

    return True

if __name__ == "__main__":
    processar_tickets_lote2()