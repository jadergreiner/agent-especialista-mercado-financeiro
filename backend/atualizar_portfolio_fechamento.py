#!/usr/bin/env python3
"""
Atualização de Portfólio - Fechamento de Posições

Atualiza o portfólio com fechamento de posições conforme relatório do usuário.
"""

import json
from datetime import datetime
from pathlib import Path

def atualizar_portfolio_fechamento():
    """Atualiza o portfólio com fechamento de posições."""

    caminho_portfolio = Path("data/portfolio/portfolio_atual.json")

    # Carregar portfólio atual
    with open(caminho_portfolio, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)

    print("🔄 Atualizando portfólio com fechamento de posições...")

    # Dados das posições fechadas conforme relatório do usuário
    fechamentos = [
        {
            "ticket": "5301566535",
            "par": "EUR/CHF",
            "direcao": "SHORT",
            "swap": 0.10,
            "profit": 1.49,
            "total_realizado": 1.59  # swap + profit
        },
        {
            "ticket": "5301566496",
            "par": "EUR/USD",
            "direcao": "LONG",
            "swap": 0.03,
            "profit": 0.20,
            "total_realizado": 0.23  # swap + profit
        }
    ]

    # Procurar e atualizar posições correspondentes
    posicoes_atualizadas = 0

    for posicao in portfolio['positions']:
        if posicao.get('status') == 'OPEN':
            for fechamento in fechamentos:
                # Verificar se corresponde (mesmo par e direção)
                if (posicao.get('currency_pair') == fechamento['par'] and
                    posicao.get('direction') == fechamento['direcao']):

                    # Atualizar posição como fechada
                    posicao['status'] = 'CLOSED'
                    posicao['close_date'] = datetime.now().isoformat()
                    posicao['pnl_realized'] = fechamento['total_realizado']
                    posicao['swap'] = fechamento['swap']
                    posicao['profit'] = fechamento['profit']
                    posicao['ticket_close'] = fechamento['ticket']
                    posicao['notes'] += f" | FECHADA {fechamento['ticket']} - Profit: {fechamento['profit']}, Swap: {fechamento['swap']}"

                    # Zerar PnL não realizado
                    posicao['pnl_unrealized'] = 0

                    posicoes_atualizadas += 1
                    print(f"✅ Posição {posicao['position_id']} ({fechamento['par']} {fechamento['direcao']}) fechada")
                    break

    # Atualizar timestamp do portfólio
    portfolio['portfolio_metadata']['last_update'] = datetime.now().isoformat()

    # Recalcular métricas do portfólio
    posicoes_abertas = [p for p in portfolio['positions'] if p.get('status') == 'OPEN']
    portfolio['portfolio_metadata']['open_positions'] = len(posicoes_abertas)

    # Calcular PnL total realizado
    pnl_total_realizado = sum(p.get('pnl_realized', 0) for p in portfolio['positions'])
    portfolio['portfolio_metadata']['total_realized_pnl'] = pnl_total_realizado

    # Salvar portfólio atualizado
    with open(caminho_portfolio, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, indent=2, ensure_ascii=False)

    print("\n📊 RESUMO DA ATUALIZAÇÃO:")
    print(f"Posições fechadas: {posicoes_atualizadas}")
    print(f"Posições ainda abertas: {len(posicoes_abertas)}")
    print(".2f")
    print("\n✅ Portfólio atualizado com sucesso!")
    return posicoes_atualizadas

if __name__ == "__main__":
    atualizar_portfolio_fechamento()