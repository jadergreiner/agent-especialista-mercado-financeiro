#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor em Tempo Real - WIN Day Trading
Acompanha WIN, VALE, PETR, DOL e gatilhos de setup
"""
import yfinance as yf
from datetime import datetime
import time
import sys
import os
from utils.terminal import limpar_tela

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class MonitorWIN:
    def __init__(self):
        # Níveis de setup
        self.entrada_compra = 155700
        self.stop_compra = 155350
        self.alvo1_compra = 156250
        self.alvo2_compra = 156800

        self.entrada_venda = 155200
        self.stop_venda = 155550
        self.alvo1_venda = 154500

        # Flags de alerta
        self.alertas_enviados = set()

    def limpar_tela(self):
        """Limpa a tela do terminal"""
        limpar_tela()

    def buscar_cotacao(self, ticker):
        """Busca cotação atual de um ativo"""
        try:
            ativo = yf.Ticker(ticker)
            dados = ativo.history(period='1d', interval='1m')
            if len(dados) > 0:
                ultimo = dados['Close'].iloc[-1]
                abertura = dados['Open'].iloc[0]
                maxima = dados['High'].max()
                minima = dados['Low'].min()
                var_percent = ((ultimo / abertura) - 1) * 100
                return {
                    'ultimo': ultimo,
                    'abertura': abertura,
                    'maxima': maxima,
                    'minima': minima,
                    'variacao': var_percent
                }
        except Exception as e:
            return None

    def verificar_gatilhos(self, win_preco):
        """Verifica se algum gatilho foi ativado"""
        alertas = []

        # Gatilho COMPRA
        if win_preco >= self.entrada_compra:
            alerta_key = f"compra_{win_preco}"
            if alerta_key not in self.alertas_enviados:
                alertas.append(("🔔 GATILHO COMPRA ATIVADO!", f"WIN rompeu {self.entrada_compra}"))
                self.alertas_enviados.add(alerta_key)

        # Stop COMPRA
        if win_preco <= self.stop_compra:
            alerta_key = f"stop_compra_{win_preco}"
            if alerta_key not in self.alertas_enviados:
                alertas.append(("🚨 STOP COMPRA", f"WIN caiu para {self.stop_compra}"))
                self.alertas_enviados.add(alerta_key)

        # Alvo 1 COMPRA
        if win_preco >= self.alvo1_compra:
            alerta_key = f"alvo1_compra_{win_preco}"
            if alerta_key not in self.alertas_enviados:
                alertas.append(("✅ ALVO 1 COMPRA ATINGIDO!", f"WIN chegou em {self.alvo1_compra}"))
                self.alertas_enviados.add(alerta_key)

        # Gatilho VENDA
        if win_preco <= self.entrada_venda:
            alerta_key = f"venda_{win_preco}"
            if alerta_key not in self.alertas_enviados:
                alertas.append(("🔔 GATILHO VENDA ATIVADO!", f"WIN perdeu {self.entrada_venda}"))
                self.alertas_enviados.add(alerta_key)

        # Stop VENDA
        if win_preco >= self.stop_venda:
            alerta_key = f"stop_venda_{win_preco}"
            if alerta_key not in self.alertas_enviados:
                alertas.append(("🚨 STOP VENDA", f"WIN subiu para {self.stop_venda}"))
                self.alertas_enviados.add(alerta_key)

        # Alvo 1 VENDA
        if win_preco <= self.alvo1_venda:
            alerta_key = f"alvo1_venda_{win_preco}"
            if alerta_key not in self.alertas_enviados:
                alertas.append(("✅ ALVO 1 VENDA ATINGIDO!", f"WIN caiu para {self.alvo1_venda}"))
                self.alertas_enviados.add(alerta_key)

        return alertas

    def exibir_dashboard(self, dados):
        """Exibe dashboard com todas as cotações"""
        self.limpar_tela()

        agora = datetime.now().strftime("%H:%M:%S")

        print("=" * 70)
        print(f"📊 MONITOR WIN DAY TRADING - {agora}")
        print("=" * 70)

        # WIN (se conseguir dados reais)
        if 'WIN' in dados and dados['WIN']:
            win = dados['WIN']
            emoji = "🟢" if win['variacao'] >= 0 else "🔴"
            print(f"\n💰 WIN (Mini Índice):")
            print(f"   Último: {win['ultimo']:.2f} {emoji} {win['variacao']:+.2f}%")
            print(f"   Abertura: {win['abertura']:.2f}")
            print(f"   Máxima: {win['maxima']:.2f}")
            print(f"   Mínima: {win['minima']:.2f}")

            # Distâncias dos níveis
            dist_compra = win['ultimo'] - self.entrada_compra
            dist_venda = win['ultimo'] - self.entrada_venda
            print(f"\n   📍 Distância Entrada COMPRA ({self.entrada_compra}): {dist_compra:+.0f} pts")
            print(f"   📍 Distância Entrada VENDA ({self.entrada_venda}): {dist_venda:+.0f} pts")
        else:
            print(f"\n💰 WIN (Mini Índice): ⚠️ Dados não disponíveis (mercado fechado?)")

        # VALE3
        if 'VALE' in dados and dados['VALE']:
            vale = dados['VALE']
            emoji = "🟢" if vale['variacao'] >= 0 else "🔴"
            print(f"\n⛏️ VALE3 (~15% IBOV):")
            print(f"   R$ {vale['ultimo']:.2f} {emoji} {vale['variacao']:+.2f}%")
        else:
            print(f"\n⛏️ VALE3: ⚠️ Dados não disponíveis")

        # PETR4
        if 'PETR' in dados and dados['PETR']:
            petr = dados['PETR']
            emoji = "🟢" if petr['variacao'] >= 0 else "🔴"
            print(f"\n🛢️ PETR4 (~10% IBOV):")
            print(f"   R$ {petr['ultimo']:.2f} {emoji} {petr['variacao']:+.2f}%")
        else:
            print(f"\n🛢️ PETR4: ⚠️ Dados não disponíveis")

        # USD/BRL
        if 'DOL' in dados and dados['DOL']:
            dol = dados['DOL']
            emoji = "🟢" if dol['variacao'] < 0 else "🔴"  # Invertido (queda é bom)
            print(f"\n💵 USD/BRL (Dólar):")
            print(f"   R$ {dol['ultimo']:.4f} {emoji} {dol['variacao']:+.2f}%")
        else:
            print(f"\n💵 USD/BRL: ⚠️ Dados não disponíveis")

        # S&P 500
        if 'SPX' in dados and dados['SPX']:
            spx = dados['SPX']
            emoji = "🟢" if spx['variacao'] >= 0 else "🔴"
            print(f"\n📈 S&P 500 Futuro:")
            print(f"   {spx['ultimo']:.2f} {emoji} {spx['variacao']:+.2f}%")
        else:
            print(f"\n📈 S&P 500: ⚠️ Dados não disponíveis")

        print("\n" + "-" * 70)
        print("🎯 NÍVEIS DE SETUP:")
        print("-" * 70)
        print(f"   COMPRA: Entrada {self.entrada_compra} | Stop {self.stop_compra} | Alvo {self.alvo1_compra}")
        print(f"   VENDA:  Entrada {self.entrada_venda} | Stop {self.stop_venda} | Alvo {self.alvo1_venda}")
        print("\n⏰ Atualização a cada 30 segundos | Ctrl+C para sair")
        print("=" * 70)

    def monitorar(self, intervalo=30):
        """Loop principal de monitoramento"""
        print("🚀 Iniciando monitor em tempo real...")
        print("⏳ Aguarde alguns segundos para carregar dados...\n")

        tickers = {
            'WIN': 'WINFEB25.SA',  # Contrato futuro WIN
            'VALE': 'VALE3.SA',
            'PETR': 'PETR4.SA',
            'DOL': 'USDBRL=X',
            'SPX': 'ES=F'  # S&P 500 Futuro
        }

        try:
            while True:
                dados = {}

                # Buscar todas as cotações
                for nome, ticker in tickers.items():
                    dados[nome] = self.buscar_cotacao(ticker)

                # Exibir dashboard
                self.exibir_dashboard(dados)

                # Verificar gatilhos (se temos dados do WIN)
                if dados.get('WIN'):
                    alertas = self.verificar_gatilhos(dados['WIN']['ultimo'])
                    if alertas:
                        print("\n" + "🔔" * 35)
                        for titulo, mensagem in alertas:
                            print(f"\n{titulo}")
                            print(f"   {mensagem}")
                        print("\n" + "🔔" * 35)
                        # Beep sonoro (Windows)
                        if sys.platform == 'win32':
                            import winsound
                            winsound.Beep(1000, 500)

                # Aguardar próxima atualização
                time.sleep(intervalo)

        except KeyboardInterrupt:
            print("\n\n👋 Monitor encerrado pelo usuário.")
            print("✅ Sessão finalizada.")

if __name__ == '__main__':
    monitor = MonitorWIN()
    monitor.monitorar(intervalo=30)  # Atualiza a cada 30 segundos
