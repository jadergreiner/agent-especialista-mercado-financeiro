"""
Monitor WIN Completo - Preços + Macro + Notícias em Tempo Real (Refatorado)
"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from monitoramento.monitor_win_base import MonitorWinBase

class MonitorWinMacroNoticias(MonitorWinBase):
    def __init__(self):
        niveis = {
            'entrada_compra': 155700,
            'stop_compra': 155350,
            'alvo1_compra': 156250,
            'entrada_venda': 155200,
            'stop_venda': 155550,
            'alvo1_venda': 154500
        }
        ativos = ['WIN=F', 'USDBRL=X', 'VALE3.SA', 'PETR4.SA', '^GSPC', 'GC=F']
        super().__init__(niveis=niveis, ativos=ativos)
        self.scoring_macro = {k: 0 for k in ['dol','vale','petr','spx','eem','vix','ouro']}

    def buscar_cotacao_macro(self):
        tickers = {
            'dol': 'USDBRL=X',
            'vale': 'VALE3.SA',
            'petr': 'PETR4.SA',
            'spx': '^GSPC',
            'eem': 'EEM',
            'vix': '^VIX',
            'ouro': 'GC=F'
        }
        resultados = {}
        for nome, ticker in tickers.items():
            info = self.buscar_cotacao(ticker)
            resultados[nome] = info
            if info['ok']:
                self._calcular_scoring(nome, info['var'])
        return resultados

    def _calcular_scoring(self, nome, variacao):
        if nome == 'dol':
            if variacao < -0.5:
                self.scoring_macro['dol'] = +1
            elif variacao > 0.5:
                self.scoring_macro['dol'] = -1
            else:
                self.scoring_macro['dol'] = 0
        elif nome == 'vale':
            if variacao > 1.0:
                self.scoring_macro['vale'] = +1
            elif variacao < -1.0:
                self.scoring_macro['vale'] = -1
            else:
                self.scoring_macro['vale'] = 0
        elif nome == 'petr':
            if variacao > 1.0:
                self.scoring_macro['petr'] = +1
            elif variacao < -1.0:
                self.scoring_macro['petr'] = -1
            else:
                self.scoring_macro['petr'] = 0
        elif nome == 'spx':
            if variacao > 0.3:
                self.scoring_macro['spx'] = +1
            elif variacao < -0.3:
                self.scoring_macro['spx'] = -1
            else:
                self.scoring_macro['spx'] = 0
        # Adicione regras para eem, vix, ouro conforme necessário

    def exibir_macro(self, resultados):
        print("\nResumo Macro:")
        for nome, info in resultados.items():
            print(f"{nome.upper()}: Preço {info['preco']:.2f} | Variação {info['var']:.2f}%")
        print("Scoring Macro:", self.scoring_macro)

def main():
    monitor = MonitorWinMacroNoticias()
    cotacoes = {ativo: monitor.buscar_cotacao(ativo) for ativo in monitor.ativos}
    noticias = monitor.buscar_noticias()
    macro = monitor.buscar_cotacao_macro()
    monitor.exibir_resumo(cotacoes, noticias)
    monitor.exibir_macro(macro)

if __name__ == "__main__":
    main()
                self.scoring_macro['spx'] = +1
            elif variacao < -0.3:
                self.scoring_macro['spx'] = -1
            else:
                self.scoring_macro['spx'] = 0

        elif nome == 'vix':
            if valor and valor > 20:
                self.scoring_macro['vix'] = -1  # VIX alto = medo
            elif valor and valor < 15:
                self.scoring_macro['vix'] = +1  # VIX baixo = calma
            else:
                self.scoring_macro['vix'] = 0

        elif nome == 'eem':
            if variacao > 0.5:
                self.scoring_macro['eem'] = +1
            elif variacao < -0.5:
                self.scoring_macro['eem'] = -1
            else:
                self.scoring_macro['eem'] = 0

        elif nome == 'ouro':
            if variacao > 1.0:
                self.scoring_macro['ouro'] = -1  # Ouro subindo = busca segurança
            elif variacao < -1.0:
                self.scoring_macro['ouro'] = +1  # Ouro caindo = risk-on
            else:
                self.scoring_macro['ouro'] = 0

    def buscar_noticias_investing(self):
        """Busca notícias do Investing.com Brasil"""
        # Buscar apenas a cada 5 minutos
        agora = datetime.now()
        if self.ultima_busca_noticias and (agora - self.ultima_busca_noticias).seconds < 300:
            return self.cache_noticias

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = 'https://br.investing.com/news/stock-market-news'
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                noticias = []

                # Buscar artigos de notícias
                artigos = soup.find_all('article', class_='js-article-item', limit=5)

                for artigo in artigos:
                    try:
                        titulo_elem = artigo.find('a', class_='title')
                        if titulo_elem:
                            titulo = titulo_elem.get_text(strip=True)
                            # Filtrar notícias relevantes para WIN
                            palavras_chave = ['bovespa', 'ibovespa', 'bolsa', 'vale', 'petrobras',
                                            'dólar', 'banco central', 'selic', 'inflação', 'pib']
                            if any(palavra in titulo.lower() for palavra in palavras_chave):
                                noticias.append({
                                    'titulo': titulo,
                                    'hora': datetime.now().strftime('%H:%M')
                                })
                    except:
                        continue

                self.cache_noticias = noticias[:5]  # Top 5
                self.ultima_busca_noticias = agora
                return self.cache_noticias
        except:
            pass

        return self.cache_noticias

    def exibir_dashboard(self, dados_mercado):
        """Exibe dashboard completo"""
        self.limpar_tela()
        agora = datetime.now().strftime("%H:%M:%S")

        print("╔" + "═" * 78 + "╗")
        print(f"║  📊 MONITOR WIN COMPLETO - {agora}".ljust(79) + "║")
        print("╠" + "═" * 78 + "╣")

        # === SEÇÃO 1: WIN ===
        if dados_mercado.get('WIN', {}).get('valido'):
            w = dados_mercado['WIN']
            emoji = "🟢" if w['variacao'] >= 0 else "🔴"

            print(f"║  💰 WIN (Mini Índice): {w['ultimo']:>10.2f} {emoji} {w['variacao']:>+6.2f}%".ljust(79) + "║")

            # Barra visual
            if w['maxima'] != w['minima']:
                pos = (w['ultimo'] - w['minima']) / (w['maxima'] - w['minima'])
                preenchido = int(pos * 50)
                barra = "█" * preenchido + "░" * (50 - preenchido)
                print(f"║     |{barra}|".ljust(79) + "║")

            print(f"║     Abertura: {w['abertura']:>8.2f} | Mínima: {w['minima']:>8.2f} | Máxima: {w['maxima']:>8.2f}".ljust(79) + "║")

            # Status do setup
            if w['ultimo'] >= self.entrada_compra:
                print(f"║     🔔 GATILHO COMPRA ATIVADO! Entrada: {self.entrada_compra}".ljust(79) + "║")
            elif w['ultimo'] <= self.entrada_venda:
                print(f"║     🔔 GATILHO VENDA ATIVADO! Entrada: {self.entrada_venda}".ljust(79) + "║")
            else:
                dist_c = self.entrada_compra - w['ultimo']
                dist_v = w['ultimo'] - self.entrada_venda
                print(f"║     📍 {dist_c:+.0f} pts para COMPRA | {dist_v:+.0f} pts para VENDA".ljust(79) + "║")
        else:
            print(f"║  💰 WIN: ⚠️ Dados indisponíveis (mercado fechado ou sem dados)".ljust(79) + "║")

        print("╠" + "═" * 78 + "╣")

        # === SEÇÃO 2: CORRELAÇÕES E MACRO ===
        print("║  🌍 CORRELAÇÕES E INDICADORES MACRO:".ljust(79) + "║")
        print("║" + " " * 78 + "║")

        # Calcular saldo macro
        saldo_macro = sum(self.scoring_macro.values())

        # USD/BRL
        if dados_mercado.get('DOL', {}).get('valido'):
            dol = dados_mercado['DOL']
            emoji = "🟢" if dol['variacao'] < 0 else "🔴"
            ponto = "+" if self.scoring_macro['dol'] > 0 else "-" if self.scoring_macro['dol'] < 0 else "0"
            print(f"║     💵 USD/BRL: R$ {dol['ultimo']:.4f} {emoji} {dol['variacao']:>+6.2f}% [{ponto}]".ljust(79) + "║")

        # VALE3
        if dados_mercado.get('VALE', {}).get('valido'):
            vale = dados_mercado['VALE']
            emoji = "🟢" if vale['variacao'] >= 0 else "🔴"
            ponto = "+" if self.scoring_macro['vale'] > 0 else "-" if self.scoring_macro['vale'] < 0 else "0"
            print(f"║     ⛏️  VALE3:  R$ {vale['ultimo']:>7.2f} {emoji} {vale['variacao']:>+6.2f}% [{ponto}] ~15% IBOV".ljust(79) + "║")

        # PETR4
        if dados_mercado.get('PETR', {}).get('valido'):
            petr = dados_mercado['PETR']
            emoji = "🟢" if petr['variacao'] >= 0 else "🔴"
            ponto = "+" if self.scoring_macro['petr'] > 0 else "-" if self.scoring_macro['petr'] < 0 else "0"
            print(f"║     🛢️  PETR4:  R$ {petr['ultimo']:>7.2f} {emoji} {petr['variacao']:>+6.2f}% [{ponto}] ~10% IBOV".ljust(79) + "║")

        # S&P 500
        if dados_mercado.get('SPX', {}).get('valido'):
            spx = dados_mercado['SPX']
            emoji = "🟢" if spx['variacao'] >= 0 else "🔴"
            ponto = "+" if self.scoring_macro['spx'] > 0 else "-" if self.scoring_macro['spx'] < 0 else "0"
            print(f"║     📈 S&P 500: {spx['ultimo']:>10.2f} {emoji} {spx['variacao']:>+6.2f}% [{ponto}]".ljust(79) + "║")

        # VIX
        if dados_mercado.get('VIX', {}).get('valido'):
            vix = dados_mercado['VIX']
            ponto = "+" if self.scoring_macro['vix'] > 0 else "-" if self.scoring_macro['vix'] < 0 else "0"
            print(f"║     😱 VIX:     {vix['ultimo']:>10.2f} {vix['variacao']:>+6.2f}% [{ponto}] Volatilidade".ljust(79) + "║")

        # Scoring total
        print("║" + " " * 78 + "║")
        if saldo_macro >= 3:
            interpretacao = "FORTEMENTE ALTISTA ✅✅"
        elif saldo_macro >= 1:
            interpretacao = "ALTISTA ✅"
        elif saldo_macro <= -3:
            interpretacao = "FORTEMENTE BAIXISTA ❌❌"
        elif saldo_macro <= -1:
            interpretacao = "BAIXISTA ❌"
        else:
            interpretacao = "NEUTRO ⚪"

        print(f"║     🎯 SALDO MACRO: {saldo_macro:+d} → {interpretacao}".ljust(79) + "║")

        print("╠" + "═" * 78 + "╣")

        # === SEÇÃO 3: NOTÍCIAS ===
        print("║  📰 NOTÍCIAS RELEVANTES:".ljust(79) + "║")
        noticias = self.buscar_noticias_investing()

        if noticias:
            for i, noticia in enumerate(noticias[:3], 1):
                titulo = noticia['titulo'][:65]
                print(f"║     {i}. [{noticia['hora']}] {titulo}...".ljust(79) + "║")
        else:
            print(f"║     ⚠️ Sem notícias recentes (cache vazio ou erro na busca)".ljust(79) + "║")

        print("╠" + "═" * 78 + "╣")

        # === SEÇÃO 4: SETUPS ===
        print("║  🎯 NÍVEIS DE SETUP:".ljust(79) + "║")
        print(f"║     🟢 COMPRA: Entrada {self.entrada_compra} | Stop {self.stop_compra} | Alvo {self.alvo1_compra}".ljust(79) + "║")
        print(f"║     🔴 VENDA:  Entrada {self.entrada_venda} | Stop {self.stop_venda} | Alvo {self.alvo1_venda}".ljust(79) + "║")

        print("╚" + "═" * 78 + "╝")
        print(f"\n⏰ Próxima atualização em 20s | Notícias: a cada 5min | Ctrl+C para sair")

    def monitorar(self):
        """Loop principal"""
        print("🚀 Iniciando Monitor WIN Completo...")
        print("📊 Carregando dados de mercado e notícias...\n")

        tickers = {
            'WIN': 'WIN$N.SA',
            'DOL': 'USDBRL=X',
            'VALE': 'VALE3.SA',
            'PETR': 'PETR4.SA',
            'SPX': '^GSPC',
            'VIX': '^VIX'
        }

        try:
            while True:
                dados_mercado = {}

                # Buscar cotações
                for nome, ticker in tickers.items():
                    dados_mercado[nome] = self.buscar_cotacao(ticker, nome.lower())

                # Exibir dashboard
                self.exibir_dashboard(dados_mercado)

                # Aguardar
                time.sleep(20)

        except KeyboardInterrupt:
            print("\n\n👋 Monitor encerrado pelo usuário.")
            print("✅ Sessão finalizada.")

if __name__ == '__main__':
    monitor = MonitorWINCompleto()
    monitor.monitorar()
