#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor WIN Simples - Preços + Macro + Notícias
Versão robusta e confiável
"""
import yfinance as yf
from datetime import datetime, timedelta
import time
import sys
import os
import requests
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def buscar_cotacao_simples(ticker):
    """Busca cotação de forma simples e robusta"""
    try:
        ativo = yf.Ticker(ticker)
        hist = ativo.history(period='5d')
        if len(hist) >= 2:
            ontem = hist['Close'].iloc[-2]
            hoje = hist['Close'].iloc[-1]
            var = ((hoje / ontem) - 1) * 100
            return {
                'preco': hoje,
                'var': var,
                'ok': True
            }
    except:
        pass
    return {'preco': 0, 'var': 0, 'ok': False}

def buscar_noticias_24h():
    """Busca notícias relevantes das últimas 24 horas via Google News RSS"""
    noticias = []

    try:
        # Google News RSS - Mercado Financeiro Brasil
        termos_busca = [
            'Bovespa',
            'Ibovespa',
            'Bolsa Brasil',
            'Dólar Brasil',
            'Mercado Financeiro Brasil'
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for termo in termos_busca[:2]:  # Limitar a 2 termos para não demorar
            try:
                url = f'https://news.google.com/rss/search?q={termo.replace(" ", "+")}&hl=pt-BR&gl=BR&ceid=BR:pt-419'
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item', limit=3)

                    for item in items:
                        try:
                            titulo = item.find('title')
                            pubdate = item.find('pubDate')

                            if titulo:
                                titulo_texto = titulo.get_text(strip=True)

                                # Verificar se não é duplicada
                                if titulo_texto not in [n['titulo'] for n in noticias]:
                                    # Extrair horário
                                    horario = ''
                                    if pubdate:
                                        try:
                                            from datetime import datetime
                                            dt = datetime.strptime(pubdate.get_text(strip=True),
                                                                  '%a, %d %b %Y %H:%M:%S %Z')
                                            horario = dt.strftime('%H:%M')
                                        except:
                                            pass

                                    noticias.append({
                                        'titulo': titulo_texto[:100],
                                        'horario': horario,
                                        'fonte': 'Google News'
                                    })
                        except:
                            continue
            except:
                continue

    except Exception as e:
        pass

    return noticias[:5]  # Máximo 5 notícias

def calcular_scoring(dados):
    """Calcula scoring macro"""
    score = 0
    detalhes = []

    # DOL (inverso)
    if dados['DOL']['ok']:
        if dados['DOL']['var'] < -0.5:
            score += 1
            detalhes.append("DOL caindo [+1]")
        elif dados['DOL']['var'] > 0.5:
            score -= 1
            detalhes.append("DOL subindo [-1]")

    # VALE
    if dados['VALE']['ok']:
        if dados['VALE']['var'] > 1.0:
            score += 1
            detalhes.append("VALE forte [+1]")
        elif dados['VALE']['var'] < -1.0:
            score -= 1
            detalhes.append("VALE fraca [-1]")

    # PETR
    if dados['PETR']['ok']:
        if dados['PETR']['var'] > 1.0:
            score += 1
            detalhes.append("PETR forte [+1]")
        elif dados['PETR']['var'] < -1.0:
            score -= 1
            detalhes.append("PETR fraca [-1]")

    # S&P
    if dados['SPX']['ok']:
        if dados['SPX']['var'] > 0.3:
            score += 1
            detalhes.append("S&P subindo [+1]")
        elif dados['SPX']['var'] < -0.3:
            score -= 1
            detalhes.append("S&P caindo [-1]")

    # VIX (inverso - volatilidade alta é ruim para compra)
    if dados['VIX']['ok']:
        if dados['VIX']['var'] < -5.0:
            score += 1
            detalhes.append("VIX caindo (menos medo) [+1]")
        elif dados['VIX']['var'] > 5.0:
            score -= 1
            detalhes.append("VIX subindo (mais medo) [-1]")

    return score, detalhes

def main():
    print("🚀 Iniciando Monitor WIN...")
    print("📊 Carregando dados...\n")

    # Níveis
    COMPRA = 155700
    VENDA = 155200

    tentativa = 0

    while True:
        try:
            tentativa += 1
            limpar()

            agora = datetime.now().strftime("%H:%M:%S")

            # Buscar dados
            # Nota: WIN não disponível no yfinance, usando IBOV como proxy
            dados = {
                'WIN': {'preco': 0, 'var': 0, 'ok': False},  # Não disponível
                'IBOV': buscar_cotacao_simples('^BVSP'),
                'DOL': buscar_cotacao_simples('USDBRL=X'),
                'VALE': buscar_cotacao_simples('VALE3.SA'),
                'PETR': buscar_cotacao_simples('PETR4.SA'),
                'SPX': buscar_cotacao_simples('^GSPC'),
                'VIX': buscar_cotacao_simples('^VIX')
            }

            # Calcular scoring
            score, detalhes = calcular_scoring(dados)

            # Buscar notícias
            noticias = buscar_noticias_24h()

            # Exibir
            print("=" * 70)
            print(f"📊 MONITOR WIN - {agora} (tentativa #{tentativa})")
            print("=" * 70)

            # WIN
            print(f"\n💰 WIN: ⚠️ Dados não disponíveis no yfinance")
            print(f"   � Abertura referência: 155.455")
            print(f"   📍 Níveis: COMPRA {COMPRA} | VENDA {VENDA}")

            # IBOV
            if dados['IBOV']['ok']:
                ib = dados['IBOV']
                emoji = "🟢" if ib['var'] >= 0 else "🔴"
                print(f"📈 IBOVESPA: {ib['preco']:>10,.0f} {emoji} {ib['var']:>+6.2f}%")

            # Correlações
            print(f"\n🌍 CORRELAÇÕES:")

            if dados['DOL']['ok']:
                d = dados['DOL']
                emoji = "🟢" if d['var'] < 0 else "🔴"
                print(f"   💵 DOL:  R$ {d['preco']:.4f} {emoji} {d['var']:>+6.2f}%")

            if dados['VALE']['ok']:
                v = dados['VALE']
                emoji = "🟢" if v['var'] >= 0 else "🔴"
                print(f"   ⛏️  VALE: R$ {v['preco']:>6.2f} {emoji} {v['var']:>+6.2f}% (~15% IBOV)")

            if dados['PETR']['ok']:
                p = dados['PETR']
                emoji = "🟢" if p['var'] >= 0 else "🔴"
                print(f"   🛢️  PETR: R$ {p['preco']:>6.2f} {emoji} {p['var']:>+6.2f}% (~10% IBOV)")

            if dados['SPX']['ok']:
                s = dados['SPX']
                emoji = "🟢" if s['var'] >= 0 else "🔴"
                print(f"   📈 S&P:  {s['preco']:>10,.2f} {emoji} {s['var']:>+6.2f}%")

            if dados['VIX']['ok']:
                vix = dados['VIX']
                # VIX: verde se caindo (menos medo), vermelho se subindo (mais medo)
                emoji = "🟢" if vix['var'] < 0 else "🔴"
                nivel = "BAIXO" if vix['preco'] < 15 else "MÉDIO" if vix['preco'] < 20 else "ALTO"
                print(f"   😨 VIX:  {vix['preco']:>10,.2f} {emoji} {vix['var']:>+6.2f}% ({nivel})")

            # Scoring
            print(f"\n🎯 SALDO MACRO: {score:+d}")
            if score >= 3:
                print(f"   → FORTEMENTE ALTISTA ✅✅ (favorece COMPRA)")
            elif score >= 1:
                print(f"   → ALTISTA ✅ (favorece COMPRA)")
            elif score <= -3:
                print(f"   → FORTEMENTE BAIXISTA ❌❌ (favorece VENDA)")
            elif score <= -1:
                print(f"   → BAIXISTA ❌ (favorece VENDA)")
            else:
                print(f"   → NEUTRO ⚪ (aguardar)")

            if detalhes:
                print(f"\n   Fatores ativos:")
                for det in detalhes:
                    print(f"     • {det}")

            # Setups
            print(f"\n📋 SETUPS:")
            print(f"   🟢 COMPRA: {COMPRA} | Stop: 155350 | Alvo: 156250")
            print(f"   🔴 VENDA:  {VENDA} | Stop: 155550 | Alvo: 154500")

            # Notícias
            if noticias:
                print(f"\n📰 NOTÍCIAS RECENTES (via Google News):")
                for i, noticia in enumerate(noticias, 1):
                    horario_str = f" [{noticia.get('horario', '')}]" if noticia.get('horario') else ""
                    print(f"   {i}.{horario_str} {noticia['titulo']}")
            else:
                print(f"\n📰 NOTÍCIAS: Buscando notícias relevantes...")

            print("=" * 70)
            print(f"⏰ Próxima atualização em 30 minutos | Ctrl+C para sair")

            time.sleep(1800)  # 30 minutos = 1800 segundos

        except KeyboardInterrupt:
            print("\n\n👋 Monitor encerrado.")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("🔄 Tentando novamente em 10s...")
            time.sleep(10)

if __name__ == '__main__':
    main()
