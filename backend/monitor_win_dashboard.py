#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor WIN - Dashboard Visual Simplificado
"""
import yfinance as yf
from datetime import datetime
import time
import sys
import os
from utils.terminal import limpar_tela

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def limpar():
    """Adapter local para limpar tela usando utilitário seguro."""
    limpar_tela()

def barra_visual(valor, min_val, max_val, largura=40):
    """Cria barra visual do preço em relação ao range"""
    if max_val == min_val:
        pos = 0.5
    else:
        pos = (valor - min_val) / (max_val - min_val)
    pos = max(0, min(1, pos))

    preenchido = int(pos * largura)
    vazio = largura - preenchido

    barra = "█" * preenchido + "░" * vazio
    return f"|{barra}|"

def buscar_dados():
    """Busca dados de todos os ativos"""
    tickers = {
        'WIN': 'WIN$N.SA',  # Índice WIN spot
        'IBOV': '^BVSP',    # IBOVESPA
        'VALE': 'VALE3.SA',
        'PETR': 'PETR4.SA',
        'DOL': 'USDBRL=X',
        'SPX': '^GSPC'
    }

    dados = {}
    for nome, ticker in tickers.items():
        try:
            ativo = yf.Ticker(ticker)
            hist = ativo.history(period='1d', interval='1m')
            if len(hist) > 0:
                dados[nome] = {
                    'ultimo': hist['Close'].iloc[-1],
                    'abertura': hist['Open'].iloc[0],
                    'maxima': hist['High'].max(),
                    'minima': hist['Low'].min(),
                    'var': ((hist['Close'].iloc[-1] / hist['Open'].iloc[0]) - 1) * 100
                }
        except:
            dados[nome] = None

    return dados

def main():
    # Níveis de setup
    COMPRA_ENTRADA = 155700
    COMPRA_STOP = 155350
    VENDA_ENTRADA = 155200
    VENDA_STOP = 155550

    print("🚀 Carregando monitor...")

    while True:
        try:
            limpar()
            dados = buscar_dados()
            agora = datetime.now().strftime("%H:%M:%S")

            print("╔" + "═" * 68 + "╗")
            print(f"║ 📊 MONITOR WIN - {agora}".ljust(69) + "║")
            print("╠" + "═" * 68 + "╣")

            # WIN
            if dados.get('WIN'):
                w = dados['WIN']
                emoji = "🟢" if w['var'] >= 0 else "🔴"
                barra = barra_visual(w['ultimo'], w['minima'], w['maxima'], 40)

                print(f"║ 💰 WIN: {w['ultimo']:>10.2f} {emoji} {w['var']:>+6.2f}%".ljust(69) + "║")
                print(f"║    {barra}".ljust(69) + "║")
                print(f"║    Min: {w['minima']:>8.2f} | Abert: {w['abertura']:>8.2f} | Max: {w['maxima']:>8.2f}".ljust(69) + "║")

                # Status do setup
                if w['ultimo'] >= COMPRA_ENTRADA:
                    print(f"║    🔔 GATILHO COMPRA ATIVADO! ({COMPRA_ENTRADA})".ljust(69) + "║")
                elif w['ultimo'] <= VENDA_ENTRADA:
                    print(f"║    🔔 GATILHO VENDA ATIVADO! ({VENDA_ENTRADA})".ljust(69) + "║")
                else:
                    dist_c = COMPRA_ENTRADA - w['ultimo']
                    dist_v = w['ultimo'] - VENDA_ENTRADA
                    print(f"║    📍 {dist_c:+.0f} pts p/ COMPRA | {dist_v:+.0f} pts p/ VENDA".ljust(69) + "║")
            else:
                print(f"║ 💰 WIN: ⚠️ Dados indisponíveis (mercado fechado?)".ljust(69) + "║")

            print("╠" + "═" * 68 + "╣")

            # IBOVESPA
            if dados.get('IBOV'):
                ibov = dados['IBOV']
                emoji = "🟢" if ibov['var'] >= 0 else "🔴"
                print(f"║ 📈 IBOVESPA: {ibov['ultimo']:>10.0f} {emoji} {ibov['var']:>+6.2f}%".ljust(69) + "║")

            # VALE
            if dados.get('VALE'):
                vale = dados['VALE']
                emoji = "🟢" if vale['var'] >= 0 else "🔴"
                print(f"║ ⛏️  VALE3:   R$ {vale['ultimo']:>7.2f} {emoji} {vale['var']:>+6.2f}%".ljust(69) + "║")

            # PETR
            if dados.get('PETR'):
                petr = dados['PETR']
                emoji = "🟢" if petr['var'] >= 0 else "🔴"
                print(f"║ 🛢️  PETR4:   R$ {petr['ultimo']:>7.2f} {emoji} {petr['var']:>+6.2f}%".ljust(69) + "║")

            # DOL
            if dados.get('DOL'):
                dol = dados['DOL']
                emoji = "🟢" if dol['var'] < 0 else "🔴"  # Invertido
                print(f"║ 💵 USD/BRL: R$ {dol['ultimo']:>7.4f} {emoji} {dol['var']:>+6.2f}%".ljust(69) + "║")

            # S&P
            if dados.get('SPX'):
                spx = dados['SPX']
                emoji = "🟢" if spx['var'] >= 0 else "🔴"
                print(f"║ 🇺🇸 S&P 500: {spx['ultimo']:>10.2f} {emoji} {spx['var']:>+6.2f}%".ljust(69) + "║")

            print("╠" + "═" * 68 + "╣")
            print(f"║ 🎯 COMPRA: {COMPRA_ENTRADA} | Stop: {COMPRA_STOP} | Alvo: 156.250".ljust(69) + "║")
            print(f"║ 🎯 VENDA:  {VENDA_ENTRADA} | Stop: {VENDA_STOP} | Alvo: 154.500".ljust(69) + "║")
            print("╚" + "═" * 68 + "╝")
            print("\n⏰ Atualização a cada 15s | Ctrl+C para sair")

            time.sleep(15)

        except KeyboardInterrupt:
            print("\n\n👋 Monitor encerrado.")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
