"""
Módulo base para monitoramento WIN - parametrizável para diferentes estratégias, ativos e fontes de notícias.
"""
import yfinance as yf
from datetime import datetime, timedelta
import os
from utils.terminal import limpar_tela
import requests
from bs4 import BeautifulSoup

class MonitorWinBase:
    def __init__(self, niveis=None, ativos=None, fontes_noticias=None):
        self.niveis = niveis or {}
        self.ativos = ativos or ['WIN=F']
        self.fontes_noticias = fontes_noticias or ['google_news']
        self.cache_noticias = []
        self.ultima_busca_noticias = None

    def limpar_tela(self):
        limpar_tela()

    def buscar_cotacao(self, ticker):
        try:
            ativo = yf.Ticker(ticker)
            hist = ativo.history(period='5d')
            if len(hist) >= 2:
                ontem = hist['Close'].iloc[-2]
                hoje = hist['Close'].iloc[-1]
                var = ((hoje / ontem) - 1) * 100
                return {'preco': hoje, 'var': var, 'ok': True}
        except Exception:
            pass
        return {'preco': 0, 'var': 0, 'ok': False}

    def buscar_noticias(self, termos_busca=None, limite=3):
        """Busca notícias relevantes via Google News RSS"""
        noticias = []
        termos = termos_busca or ['Bovespa', 'Ibovespa', 'Bolsa Brasil', 'Dólar Brasil', 'Mercado Financeiro Brasil']
        headers = {'User-Agent': 'Mozilla/5.0'}
        for termo in termos[:limite]:
            try:
                url = f'https://news.google.com/rss/search?q={termo.replace(" ", "+")}&hl=pt-BR&gl=BR&ceid=BR:pt-419'
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'xml')
                    for item in soup.find_all('item')[:2]:
                        noticias.append({
                            'titulo': item.title.text,
                            'link': item.link.text,
                            'pubDate': item.pubDate.text
                        })
            except Exception:
                continue
        return noticias

    def exibir_resumo(self, cotacoes, noticias):
        print("\nResumo das Cotações:")
        for ativo, info in cotacoes.items():
            print(f"{ativo}: Preço {info['preco']:.2f} | Variação {info['var']:.2f}%")
        print("\nNotícias Recentes:")
        for n in noticias:
            print(f"- {n['titulo']} ({n['pubDate']})")
            print(f"  {n['link']}")

# Exemplo de uso
if __name__ == "__main__":
    monitor = MonitorWinBase()
    cotacoes = {ativo: monitor.buscar_cotacao(ativo) for ativo in monitor.ativos}
    noticias = monitor.buscar_noticias()
    monitor.exibir_resumo(cotacoes, noticias)
