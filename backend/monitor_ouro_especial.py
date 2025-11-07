#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Especializado de Ouro
============================

Sistema dedicado para monitoramento em tempo real da posição crítica XAUUSD.
Alertas avançados, tracking de P&L e dashboard específico.

Autor: Agent Especialista Mercado Financeiro
Data: 06/11/2025
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys

# Adicionar utils ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
try:
    from feed_resolver import resolver_cotacao_ouro, FeedResolver
except ImportError:
    print("⚠️ Feed resolver não disponível")
    def resolver_cotacao_ouro(ticker):
        return None


class MonitorOuroEspecial:
    """Monitor especializado para posições de ouro"""

    def __init__(self, portfolio_path: str = None):
        if portfolio_path is None:
            portfolio_path = 'data/portfolio/portfolio_atual.json'

        self.portfolio_path = portfolio_path
        self.feed_resolver = FeedResolver() if 'FeedResolver' in globals() else None
        self.historico_precos = []
        self.alertas_enviados = []

        # Configurações de alerta
        self.alerta_variacao_pct = 1.0  # Alertar mudanças > 1%
        self.alerta_critico_pct = 5.0   # Alerta crítico > 5%
        self.intervalo_update = 30      # Segundos entre updates

    def carregar_portfolio(self) -> Dict:
        """Carrega dados do portfolio"""
        try:
            with open(self.portfolio_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar portfolio: {e}")
            return {}

    def encontrar_posicoes_ouro(self) -> List[Dict]:
        """Encontra todas as posições de ouro no portfolio"""
        portfolio = self.carregar_portfolio()
        posicoes_ouro = []

        for pos in portfolio.get('positions', []):
            if pos['currency_pair'] in ['XAUUSD', 'XAU/USD'] and pos['status'] == 'OPEN':
                posicoes_ouro.append(pos)

        return posicoes_ouro

    def calcular_pnl_total_ouro(self, posicoes: List[Dict]) -> float:
        """Calcula P&L total das posições de ouro"""
        pnl_total = 0

        for pos in posicoes:
            entry_price = pos['entry_price']
            current_price = pos['current_price']
            lots = pos['lots']
            lot_size = pos['lot_size']
            direction = pos['direction']

            diferenca = current_price - entry_price
            if direction == 'SHORT':
                diferenca = -diferenca

            pnl_posicao = diferenca * lots * lot_size
            pnl_total += pnl_posicao

        return pnl_total

    def detectar_alertas(self, preco_atual: float, preco_anterior: float) -> List[str]:
        """Detecta situações que requerem alerta"""
        alertas = []

        if preco_anterior == 0:
            return alertas

        variacao_pct = abs((preco_atual - preco_anterior) / preco_anterior) * 100

        if variacao_pct >= self.alerta_critico_pct:
            alertas.append(f"🚨 CRÍTICO: Ouro variou {variacao_pct:.2f}% - ${preco_anterior:.2f} → ${preco_atual:.2f}")
        elif variacao_pct >= self.alerta_variacao_pct:
            alertas.append(f"⚠️ ALERTA: Ouro variou {variacao_pct:.2f}% - ${preco_anterior:.2f} → ${preco_atual:.2f}")

        # Alertas específicos por nível de preço
        if preco_atual > 4100:
            alertas.append(f"📈 Ouro acima de $4100: ${preco_atual:.2f}")
        elif preco_atual < 3800:
            alertas.append(f"📉 Ouro abaixo de $3800: ${preco_atual:.2f}")

        return alertas

    def atualizar_posicoes_ouro(self, novo_preco: float):
        """Atualiza preços das posições de ouro no portfolio"""
        try:
            portfolio = self.carregar_portfolio()

            for pos in portfolio.get('positions', []):
                if pos['currency_pair'] in ['XAUUSD', 'XAU/USD']:
                    pos['current_price'] = novo_preco

                    # Recalcular P&L
                    entry_price = pos['entry_price']
                    lots = pos['lots']
                    lot_size = pos['lot_size']
                    direction = pos['direction']

                    diferenca = novo_preco - entry_price
                    if direction == 'SHORT':
                        diferenca = -diferenca

                    pos['pnl_unrealized'] = diferenca * lots * lot_size

            # Atualizar timestamp
            portfolio['portfolio_metadata']['last_update'] = datetime.now().isoformat() + '+00:00'

            # Salvar portfolio atualizado
            with open(self.portfolio_path, 'w', encoding='utf-8') as f:
                json.dump(portfolio, f, indent=2, ensure_ascii=False)

            print(f"✅ Portfolio atualizado com preço do ouro: ${novo_preco:.2f}")

        except Exception as e:
            print(f"❌ Erro ao atualizar portfolio: {e}")

    def gerar_dashboard(self, posicoes: List[Dict], preco_atual: float) -> str:
        """Gera dashboard específico para ouro"""
        dashboard = []
        dashboard.append("🥇 DASHBOARD ESPECIALIZADO - OURO (XAUUSD)")
        dashboard.append("=" * 60)
        dashboard.append(f"🕐 Timestamp: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        dashboard.append(f"💰 Preço Atual: ${preco_atual:.2f}")

        if len(self.historico_precos) > 1:
            preco_anterior = self.historico_precos[-2]['price']
            variacao = preco_atual - preco_anterior
            variacao_pct = (variacao / preco_anterior) * 100

            emoji = "📈" if variacao > 0 else "📉" if variacao < 0 else "➡️"
            dashboard.append(f"{emoji} Variação: ${variacao:+.2f} ({variacao_pct:+.2f}%)")

        dashboard.append("")
        dashboard.append("📊 POSIÇÕES ATIVAS:")
        dashboard.append("-" * 40)

        pnl_total = 0
        for i, pos in enumerate(posicoes, 1):
            ticket = pos.get('ticket', 'N/A')
            direction = pos['direction']
            entry_price = pos['entry_price']
            lots = pos['lots']

            diferenca = preco_atual - entry_price
            if direction == 'SHORT':
                diferenca = -diferenca

            pnl = diferenca * lots * pos['lot_size']
            pnl_total += pnl

            status_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "🟡"
            dashboard.append(f"{i}. {status_emoji} Ticket #{ticket}")
            dashboard.append(f"   {direction} {lots} lotes @ ${entry_price:.2f}")
            dashboard.append(f"   P&L: ${pnl:,.2f}")
            dashboard.append("")

        dashboard.append("💼 RESUMO TOTAL:")
        dashboard.append(f"   P&L Total Ouro: ${pnl_total:,.2f}")
        dashboard.append(f"   Posições Ativas: {len(posicoes)}")

        # Status de risco
        if abs(pnl_total) > 50000:
            dashboard.append(f"🚨 RISCO ALTO: P&L > $50K")
        elif abs(pnl_total) > 10000:
            dashboard.append(f"⚠️ RISCO MÉDIO: P&L > $10K")
        else:
            dashboard.append(f"✅ RISCO CONTROLADO")

        return "\\n".join(dashboard)

    def executar_ciclo_monitoramento(self):
        """Executa um ciclo completo de monitoramento"""
        print(f"🔄 Iniciando monitoramento de ouro...")

        # Buscar preço atual
        preco_atual = resolver_cotacao_ouro("XAUUSD")
        if not preco_atual:
            print("❌ Falha ao obter cotação do ouro")
            return

        # Registrar no histórico
        timestamp = datetime.now()
        self.historico_precos.append({
            'timestamp': timestamp,
            'price': preco_atual
        })

        # Manter apenas últimas 100 entradas
        if len(self.historico_precos) > 100:
            self.historico_precos = self.historico_precos[-100:]

        # Detectar alertas
        preco_anterior = 0
        if len(self.historico_precos) > 1:
            preco_anterior = self.historico_precos[-2]['price']

        alertas = self.detectar_alertas(preco_atual, preco_anterior)

        # Processar alertas
        for alerta in alertas:
            if alerta not in self.alertas_enviados:
                print(alerta)
                self.alertas_enviados.append(alerta)

        # Encontrar posições e atualizar
        posicoes_ouro = self.encontrar_posicoes_ouro()
        if posicoes_ouro:
            self.atualizar_posicoes_ouro(preco_atual)

            # Gerar e exibir dashboard
            dashboard = self.gerar_dashboard(posicoes_ouro, preco_atual)
            print(dashboard)
        else:
            print("ℹ️ Nenhuma posição de ouro encontrada")

    def monitoramento_continuo(self, duracao_minutos: int = 60):
        """Executa monitoramento contínuo por tempo determinado"""
        print(f"🚀 Iniciando monitoramento contínuo por {duracao_minutos} minutos...")

        inicio = datetime.now()
        fim = inicio + timedelta(minutes=duracao_minutos)

        try:
            while datetime.now() < fim:
                self.executar_ciclo_monitoramento()
                print(f"\\n⏱️ Próxima atualização em {self.intervalo_update}s...")
                time.sleep(self.intervalo_update)

        except KeyboardInterrupt:
            print("\\n🛑 Monitoramento interrompido pelo usuário")

        print("\\n✅ Monitoramento finalizado")


if __name__ == "__main__":
    # Execução direta - teste básico
    monitor = MonitorOuroEspecial()

    if len(sys.argv) > 1 and sys.argv[1] == "--continuo":
        # Modo contínuo
        duracao = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        monitor.monitoramento_continuo(duracao)
    else:
        # Ciclo único
        monitor.executar_ciclo_monitoramento()