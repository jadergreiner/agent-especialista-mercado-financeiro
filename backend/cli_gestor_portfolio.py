#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI - Gestor do Fundo: Atualização de Portfólio com GATES

Formato:
- INICIO: Solicita o ativo e a atualização
- DURANTE: Insere/atualiza posição no portfólio
- FIM:
  - Relatório do portfólio atualizado
  - Risco do portfólio

GATES:
- TICKET OBRIGATORIO
- NAO PERMITE DUPLICAR TICKET
"""

from __future__ import annotations

import sys
import os

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from gestor_portfolio_atualizado import GestorPortfolioAtualizado


def solicitar_input_rotulado(rotulo: str, obrigatorio: bool = True, cast=None):
    while True:
        valor = input(f"{rotulo}: ").strip()
        if not valor:
            if obrigatorio:
                print("   -> Campo obrigatório. Tente novamente.")
                continue
            return None
        if cast:
            try:
                return cast(valor)
            except Exception:
                print("   -> Formato inválido. Tente novamente.")
                continue
        return valor


essa_sessao = "GESTOR DO FUNDO - ATUALIZAÇÃO DO PORTFÓLIO"

def main():
    print("=" * 70)
    print(essa_sessao)
    print("=" * 70)

    print("\nINICIO — Coleta de dados (GATES ativos)")
    print("- Ticket obrigatório")
    print("- Não permite duplicar ticket")
    print("- Validação de dados em tempo real\n")

    gestor = GestorPortfolioAtualizado()

    # Coletar dados
    ticket = solicitar_input_rotulado("Ticket (ex.: #123456)")
    par = solicitar_input_rotulado("Par (ex.: EURUSD, GBP/JPY, XAUUSD)")
    direcao = solicitar_input_rotulado("Direção (BUY/SELL ou LONG/SHORT)")
    lots = solicitar_input_rotulado("Volume em lotes (ex.: 0.01)", cast=float)
    preco_entrada = solicitar_input_rotulado("Preço de entrada", cast=float)

    print("\nDURANTE — Processando inclusão/atualização de posição\n")
    ok = gestor.processar_nova_posicao(
        ticket=ticket,
        currency_pair=par,
        direction=direcao,
        lots=lots,
        entry_price=preco_entrada,
    )

    print("\nFIM — Relatório pós-atualização\n")
    if ok:
        gestor.gerar_relatorio_pos_atualizacao()
    else:
        print("Não foi possível concluir a atualização do portfólio. Verifique as mensagens acima.")


if __name__ == "__main__":
    main()
