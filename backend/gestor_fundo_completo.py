#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTOR DO FUNDO - SISTEMA COMPLETO DE GESTÃO DE PORTFÓLIO

Sistema integrado que combina:
- Gestão de portfólio com gates de validação
- Análise de risco multi-dimensional
- Avaliação de coerência macroeconômica
- Análise de correlação avançada
- Recomendações inteligentes baseadas em níveis técnicos

Fluxo: [INÍCIO] → [DURANTE] → [FIM]
- INÍCIO: Coleta e validação de dados (gates obrigatórios)
- DURANTE: Atualização de portfólio e preços de mercado
- FIM: Relatório executivo completo com análises e recomendações
"""

import json
import yfinance as yf
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os
import sys
import logging

# Garantir imports dos módulos especializados
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from analisador_risco_fundo import AnalisadorRiscoFundo
    from recomendador_operacoes_fundo import RecomendadorOperacoesFundo
    from modulo_correlacao_avancada import ModuloCorrelacaoAvancada
    from calculador_niveis_precisao import CalculadorNiveisPrecisao
except ImportError as e:
    print(f"⚠️ Aviso: Alguns módulos especializados não disponíveis: {e}")
    AnalisadorRiscoFundo = None
    RecomendadorOperacoesFundo = None
    ModuloCorrelacaoAvancada = None
    CalculadorNiveisPrecisao = None


@dataclass
class DadosOperacao:
    """Dados completos de uma operação"""
    ticket: str
    currency_pair: str
    direction: str  # LONG/SHORT
    entry_price: float
    lots: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class RelatorioExecutivo:
    """Estrutura do relatório executivo completo"""
    timestamp: str
    portfolio_summary: Dict
    risk_analysis: Dict
    macro_coherence: Dict
    correlation_analysis: Dict
    recommendations: Dict


class GestorFundoCompleto:
    """
    Gestor Completo do Fundo com Análise Integrada
    """

    def __init__(self, caminho_portfolio: str = None):
        """Inicializa o gestor com todos os módulos de análise"""
        if caminho_portfolio is None:
            caminho_portfolio = os.path.join(BASE_DIR, "data", "portfolio", "portfolio_atual.json")

        self.caminho_portfolio = caminho_portfolio
        self.portfolio = None

        # Logger configurado
        self.logger = self._configurar_logger()

        # Módulos especializados
        self.analisador_risco = AnalisadorRiscoFundo() if AnalisadorRiscoFundo else None
        self.recomendador = RecomendadorOperacoesFundo() if RecomendadorOperacoesFundo else None
        self.modulo_correlacao = ModuloCorrelacaoAvancada() if ModuloCorrelacaoAvancada else None
        self.calculador_niveis = CalculadorNiveisPrecisao() if CalculadorNiveisPrecisao else None

        self.logger.info("✅ Gestor do Fundo Completo inicializado")

    def _configurar_logger(self) -> logging.Logger:
        """Configurar sistema de logging"""
        logger = logging.getLogger('GestorFundoCompleto')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    # ============================================================================
    # [INÍCIO] COLETA E VALIDAÇÃO DE DADOS
    # ============================================================================

    def validar_gates(self, dados: DadosOperacao) -> Tuple[bool, Optional[str]]:
        """
        Validação de gates obrigatórios

        GATES:
        1. Ticket obrigatório (não vazio)
        2. Ticket único (não pode existir no portfólio)
        3. Formato de dados correto

        Returns:
            (válido, mensagem_erro)
        """
        # GATE 1: Ticket obrigatório
        if not dados.ticket or dados.ticket.strip() == "":
            return False, "❌ GATE VIOLADO: Ticket é obrigatório"

        # GATE 2: Ticket único
        if self.portfolio:
            tickets_existentes = {
                pos.get('ticket', '') for pos in self.portfolio.get('positions', [])
                if pos.get('status') == 'OPEN'
            }

            if dados.ticket in tickets_existentes:
                return False, f"❌ GATE VIOLADO: Ticket '{dados.ticket}' já existe no portfólio"

        # GATE 3: Validações de formato
        if dados.entry_price <= 0:
            return False, "❌ GATE VIOLADO: Preço de entrada deve ser maior que zero"

        if dados.lots <= 0:
            return False, "❌ GATE VIOLADO: Volume (lotes) deve ser maior que zero"

        if dados.direction not in ['LONG', 'SHORT', 'BUY', 'SELL']:
            return False, f"❌ GATE VIOLADO: Direção '{dados.direction}' inválida (use LONG/SHORT ou BUY/SELL)"

        return True, None

    def carregar_portfolio(self):
        """Carregar portfólio do arquivo JSON"""
        try:
            with open(self.caminho_portfolio, 'r', encoding='utf-8') as f:
                self.portfolio = json.load(f)
            self.logger.info(f"✅ Portfólio carregado: {len(self.portfolio.get('positions', []))} posições")
        except FileNotFoundError:
            self.logger.error(f"❌ Arquivo de portfólio não encontrado: {self.caminho_portfolio}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Erro ao decodificar JSON: {e}")
            raise

    # ============================================================================
    # [DURANTE] ATUALIZAÇÃO DE PORTFÓLIO
    # ============================================================================

    def adicionar_posicao(self, dados: DadosOperacao):
        """
        Adicionar nova posição ao portfólio

        Args:
            dados: Dados completos da operação
        """
        # Normalizar direção
        direction = 'LONG' if dados.direction.upper() in ['BUY', 'LONG'] else 'SHORT'

        # Criar estrutura da posição
        nova_posicao = {
            "position_id": f"pos_{len(self.portfolio['positions']) + 1:03d}",
            "ticket": dados.ticket,
            "currency_pair": dados.currency_pair,
            "direction": direction,
            "entry_price": dados.entry_price,
            "current_price": dados.entry_price,  # Inicialmente igual ao entry
            "lots": dados.lots,
            "lot_size": 100000,  # Padrão forex
            "entry_date": datetime.now(timezone.utc).isoformat(),
            "stop_loss": dados.stop_loss,
            "take_profit": dados.take_profit if dados.take_profit else [],
            "pnl_unrealized": 0.0,
            "pnl_realized": 0,
            "strategy": dados.strategy or "Operação via Gestor do Fundo",
            "risk_percentage": 0.1,
            "notes": dados.notes or f"Adicionado via Gestor Completo - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "status": "OPEN"
        }

        # Adicionar ao portfólio
        self.portfolio['positions'].append(nova_posicao)

        # Atualizar metadata
        self.portfolio['portfolio_metadata']['last_update'] = datetime.now(timezone.utc).isoformat()
        posicoes_abertas = len([p for p in self.portfolio['positions'] if p.get('status') == 'OPEN'])
        self.portfolio['portfolio_metadata']['open_positions'] = posicoes_abertas

        self.logger.info(f"✅ Posição adicionada: {dados.ticket} - {dados.currency_pair} {direction}")

    def atualizar_precos_mercado(self):
        """Atualizar preços de mercado de todas as posições abertas"""
        self.logger.info("🔄 Atualizando preços do mercado...")

        posicoes_abertas = [p for p in self.portfolio['positions'] if p.get('status') == 'OPEN']

        for posicao in posicoes_abertas:
            currency_pair = posicao['currency_pair']
            preco_atual = self._obter_cotacao_atual(currency_pair)

            if preco_atual and preco_atual > 0:
                posicao['current_price'] = preco_atual

                # Recalcular P&L
                pnl = self._calcular_pnl_posicao(posicao)
                posicao['pnl_unrealized'] = pnl

                self.logger.info(f"   ✅ {currency_pair}: ${preco_atual:.5f} | P&L: ${pnl:+.2f}")

    def _obter_cotacao_atual(self, currency_pair: str) -> Optional[float]:
        """Obter cotação atual do Yahoo Finance"""
        try:
            # Mapeamento de símbolos
            symbol_map = {
                'GBP/JPY': 'GBPJPY=X',
                'EUR/USD': 'EURUSD=X',
                'CHF/JPY': 'CHFJPY=X',
                'EUR/CHF': 'EURCHF=X',
                'AUD/CAD': 'AUDCAD=X',
                'USD/CHF': 'USDCHF=X',
                'USD/JPY': 'USDJPY=X',
                'AUD/USD': 'AUDUSD=X',
                'XAU/USD': 'GC=F',
                'EURUSD': 'EURUSD=X',
                'USDJPY': 'USDJPY=X'
            }

            symbol = symbol_map.get(currency_pair, currency_pair)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')

            if not hist.empty:
                return float(hist['Close'].iloc[-1])

        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao obter cotação {currency_pair}: {e}")

        return None

    def _calcular_pnl_posicao(self, posicao: dict) -> float:
        """Calcular P&L de uma posição"""
        try:
            current_price = posicao.get('current_price', posicao['entry_price'])
            diferenca = current_price - posicao['entry_price']

            if posicao['direction'] == 'SHORT':
                diferenca = -diferenca

            return posicao['lots'] * posicao.get('lot_size', 100000) * diferenca
        except:
            return 0.0

    def salvar_portfolio(self):
        """Salvar portfólio atualizado"""
        try:
            with open(self.caminho_portfolio, 'w', encoding='utf-8') as f:
                json.dump(self.portfolio, f, indent=2, ensure_ascii=False)
            self.logger.info("💾 Portfólio salvo com sucesso")
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar portfólio: {e}")
            raise

    # ============================================================================
    # [FIM] GERAÇÃO DE RELATÓRIO EXECUTIVO
    # ============================================================================

    def gerar_relatorio_portfolio(self) -> Dict:
        """Gerar resumo do portfólio"""
        posicoes_abertas = [p for p in self.portfolio['positions'] if p.get('status') == 'OPEN']

        # Calcular totais
        total_pnl_unrealized = sum(p.get('pnl_unrealized', 0) for p in posicoes_abertas)
        total_pnl_realized = self.portfolio['portfolio_metadata'].get('total_realized_pnl', 0)
        total_pnl = total_pnl_unrealized + total_pnl_realized

        capital_total = self.portfolio['portfolio_metadata']['total_capital']
        retorno_percentual = (total_pnl / capital_total) * 100

        # Calcular exposição
        exposicao_total = sum(
            p['lots'] * p.get('lot_size', 100000) * p['entry_price']
            for p in posicoes_abertas
        )

        alavancagem = exposicao_total / capital_total if capital_total > 0 else 0

        # Exposição por moeda
        exposicao_moeda = {}
        for pos in posicoes_abertas:
            pair = pos['currency_pair']
            moeda_base = pair[:3]
            moeda_quote = pair[-3:] if '/' in pair else pair[3:6]

            valor = pos['lots'] * pos.get('lot_size', 100000) * pos['entry_price']

            if pos['direction'] == 'LONG':
                exposicao_moeda[moeda_base] = exposicao_moeda.get(moeda_base, 0) + valor
                exposicao_moeda[moeda_quote] = exposicao_moeda.get(moeda_quote, 0) - valor
            else:
                exposicao_moeda[moeda_base] = exposicao_moeda.get(moeda_base, 0) - valor
                exposicao_moeda[moeda_quote] = exposicao_moeda.get(moeda_quote, 0) + valor

        return {
            'capital_total': capital_total,
            'posicoes_ativas': len(posicoes_abertas),
            'pnl_total': total_pnl,
            'pnl_unrealized': total_pnl_unrealized,
            'pnl_realized': total_pnl_realized,
            'retorno_percentual': retorno_percentual,
            'exposicao_total': exposicao_total,
            'alavancagem': alavancagem,
            'exposicao_moeda': exposicao_moeda
        }

    def analisar_risco_completo(self) -> Dict:
        """Análise de risco utilizando AnalisadorRiscoFundo"""
        if not self.analisador_risco:
            return {'nivel_alerta': 'DESCONHECIDO', 'message': 'Módulo de risco não disponível'}

        try:
            analise = self.analisador_risco.analisar_risco_portfolio(self.portfolio)
            return {
                'nivel_alerta': analise.nivel_alerta,
                'concentracao_maxima': analise.concentracao_maxima,
                'moeda_concentrada': analise.moeda_concentrada,
                'correlacao_maxima': analise.correlacao_maxima,
                'var_95': analise.var_95,
                'recomendacoes': analise.recomendacoes
            }
        except Exception as e:
            self.logger.error(f"❌ Erro na análise de risco: {e}")
            return {'nivel_alerta': 'ERRO', 'message': str(e)}

    def avaliar_coerencia_macro(self) -> Dict:
        """Avaliar coerência com cenário macroeconômico"""
        try:
            # Coletar indicadores macro
            vix = self._obter_indicador('^VIX')
            dxy = self._obter_indicador('DX-Y.NYB')

            # Classificar cenário
            if vix and vix > 25:
                volatilidade = "ALTA"
                cenario = "RISK-OFF"
            elif vix and vix > 15:
                volatilidade = "MODERADA"
                cenario = "NEUTRO"
            else:
                volatilidade = "BAIXA"
                cenario = "RISK-ON"

            # Avaliar USD
            if dxy and dxy > 105:
                usd_strength = "FORTE"
            elif dxy and dxy > 95:
                usd_strength = "NEUTRO"
            else:
                usd_strength = "FRACO"

            # Análise de alinhamento
            posicoes_abertas = [p for p in self.portfolio['positions'] if p.get('status') == 'OPEN']

            # Contar carry trades (pares com JPY)
            carry_trades = len([p for p in posicoes_abertas if 'JPY' in p['currency_pair']])

            # Avaliar coerência
            alertas = []
            if cenario == "RISK-OFF" and carry_trades > 3:
                alertas.append("⚠️ Ambiente risk-off pode prejudicar carry trades")
                alinhamento = "ATENÇÃO"
            elif cenario == "RISK-ON" and carry_trades == 0:
                alertas.append("💡 Cenário favorável para carry trades, considere adicionar")
                alinhamento = "COERENTE"
            else:
                alinhamento = "COERENTE"

            return {
                'vix': vix or 0,
                'dxy': dxy or 0,
                'volatilidade': volatilidade,
                'cenario': cenario,
                'usd_strength': usd_strength,
                'alinhamento': alinhamento,
                'alertas': alertas
            }

        except Exception as e:
            self.logger.error(f"❌ Erro na análise macro: {e}")
            return {'cenario': 'ERRO', 'message': str(e)}

    def _obter_indicador(self, symbol: str) -> Optional[float]:
        """Obter valor atual de um indicador"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
        except:
            pass
        return None

    def analisar_correlacoes(self) -> Dict:
        """Análise de correlação usando ModuloCorrelacaoAvancada"""
        if not self.modulo_correlacao:
            return {'status': 'DESCONHECIDO', 'message': 'Módulo de correlação não disponível'}

        try:
            posicoes_abertas = [p for p in self.portfolio['positions'] if p.get('status') == 'OPEN']
            pares = [p['currency_pair'] for p in posicoes_abertas]

            # Análise simplificada de redundância
            moedas = {}
            for par in pares:
                base = par[:3]
                quote = par[-3:] if '/' in par else par[3:6]
                moedas[base] = moedas.get(base, 0) + 1
                moedas[quote] = moedas.get(quote, 0) + 1

            exposicoes_redundantes = [m for m, count in moedas.items() if count > 3]

            return {
                'exposicoes_redundantes': exposicoes_redundantes,
                'diversificacao': len(set(pares)),
                'recomendacao': 'Diversificar' if exposicoes_redundantes else 'Adequado'
            }

        except Exception as e:
            self.logger.error(f"❌ Erro na análise de correlação: {e}")
            return {'status': 'ERRO', 'message': str(e)}

    def gerar_recomendacoes(self) -> Dict:
        """Gerar recomendações usando RecomendadorOperacoesFundo"""
        if not self.recomendador:
            return {'status': 'DESCONHECIDO', 'message': 'Módulo de recomendações não disponível'}

        try:
            recomendacoes = self.recomendador.gerar_recomendacoes_completas(self.portfolio)

            # Organizar por prioridade
            resultado = {
                'posicoes_existentes': len(recomendacoes.get('posicoes_existentes', [])),
                'novas_oportunidades': len(recomendacoes.get('novas_oportunidades', [])),
                'gestao_risco': len(recomendacoes.get('gestao_risco', [])),
                'balanceamento': len(recomendacoes.get('balanceamento', [])),
                'detalhes': recomendacoes
            }

            return resultado

        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar recomendações: {e}")
            return {'status': 'ERRO', 'message': str(e)}

    def formatar_relatorio_executivo(self) -> str:
        """Formatar relatório executivo completo"""
        # Coletar todas as análises
        portfolio_summary = self.gerar_relatorio_portfolio()
        risk_analysis = self.analisar_risco_completo()
        macro_coherence = self.avaliar_coerencia_macro()
        correlation_analysis = self.analisar_correlacoes()
        recommendations = self.gerar_recomendacoes()

        # Formatar relatório
        linhas = []
        linhas.append("=" * 80)
        linhas.append("💼 RELATÓRIO EXECUTIVO DO FUNDO")
        linhas.append("=" * 80)
        linhas.append(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        linhas.append("")

        # RESUMO DO PORTFÓLIO
        linhas.append("📈 RESUMO DO PORTFÓLIO")
        linhas.append("-" * 50)
        linhas.append(f"💰 Capital Total: ${portfolio_summary['capital_total']:,.2f}")
        linhas.append(f"📊 Posições Ativas: {portfolio_summary['posicoes_ativas']}")
        linhas.append(f"💵 P&L Total: ${portfolio_summary['pnl_total']:+,.2f} ({portfolio_summary['retorno_percentual']:+.2f}%)")
        linhas.append(f"   └─ Não Realizado: ${portfolio_summary['pnl_unrealized']:+,.2f}")
        linhas.append(f"   └─ Realizado: ${portfolio_summary['pnl_realized']:+,.2f}")
        linhas.append(f"💎 Exposição Total: ${portfolio_summary['exposicao_total']:,.2f}")
        linhas.append(f"⚖️  Alavancagem: {portfolio_summary['alavancagem']:.2f}x")
        linhas.append("")

        # Exposição por moeda
        linhas.append("💱 EXPOSIÇÃO POR MOEDA")
        linhas.append("-" * 30)
        for moeda, exposicao in sorted(portfolio_summary['exposicao_moeda'].items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
            sinal = "+" if exposicao >= 0 else ""
            linhas.append(f"   {moeda}: {sinal}${exposicao:,.0f}")
        linhas.append("")

        # ANÁLISE DE RISCO
        linhas.append("⚠️  ANÁLISE DE RISCO")
        linhas.append("-" * 50)
        nivel = risk_analysis.get('nivel_alerta', 'DESCONHECIDO')
        emoji = {'BAIXO': '✅', 'MODERADO': '⚠️', 'ALTO': '🔴', 'CRÍTICO': '🚨'}.get(nivel, '❓')
        linhas.append(f"{emoji} Nível de Alerta: {nivel}")

        if 'concentracao_maxima' in risk_analysis:
            linhas.append(f"📊 Concentração Máxima: {risk_analysis['concentracao_maxima']:.1%} em {risk_analysis.get('moeda_concentrada', 'N/A')}")

        if 'correlacao_maxima' in risk_analysis:
            linhas.append(f"🔗 Correlação Máxima: {risk_analysis['correlacao_maxima']:.2f}")

        if 'var_95' in risk_analysis:
            linhas.append(f"📉 VaR (95%): ${risk_analysis['var_95']:,.2f}")
        linhas.append("")

        # COERÊNCIA MACROECONÔMICA
        linhas.append("🌐 COERÊNCIA MACROECONÔMICA")
        linhas.append("-" * 50)
        linhas.append(f"📊 VIX: {macro_coherence.get('vix', 0):.1f} (Volatilidade {macro_coherence.get('volatilidade', 'N/A')})")
        linhas.append(f"💵 DXY: {macro_coherence.get('dxy', 0):.1f} (USD {macro_coherence.get('usd_strength', 'N/A')})")
        linhas.append(f"🎯 Cenário: {macro_coherence.get('cenario', 'N/A')}")

        alinhamento = macro_coherence.get('alinhamento', 'N/A')
        emoji_align = {'COERENTE': '✅', 'ATENÇÃO': '⚠️', 'DESALINHADO': '❌'}.get(alinhamento, '❓')
        linhas.append(f"{emoji_align} Alinhamento: {alinhamento}")

        for alerta in macro_coherence.get('alertas', []):
            linhas.append(f"   {alerta}")
        linhas.append("")

        # ANÁLISE DE CORRELAÇÃO
        linhas.append("🔗 ANÁLISE DE CORRELAÇÃO")
        linhas.append("-" * 50)
        redundantes = correlation_analysis.get('exposicoes_redundantes', [])
        if redundantes:
            linhas.append(f"⚠️  Exposições Redundantes: {', '.join(redundantes)}")
        else:
            linhas.append("✅ Diversificação adequada")
        linhas.append(f"📊 Pares Únicos: {correlation_analysis.get('diversificacao', 0)}")
        linhas.append("")

        # RECOMENDAÇÕES
        linhas.append("💡 RECOMENDAÇÕES INTELIGENTES")
        linhas.append("-" * 50)
        linhas.append(f"📋 Gestão de Posições: {recommendations.get('posicoes_existentes', 0)} recomendações")
        linhas.append(f"🆕 Novas Oportunidades: {recommendations.get('novas_oportunidades', 0)} identificadas")
        linhas.append(f"🛡️  Gestão de Risco: {recommendations.get('gestao_risco', 0)} alertas")
        linhas.append(f"⚖️  Balanceamento: {recommendations.get('balanceamento', 0)} sugestões")
        linhas.append("")
        linhas.append("📄 Para detalhes completos, execute: gestor.recomendador.gerar_relatorio_recomendacoes(...)")
        linhas.append("")

        linhas.append("=" * 80)
        linhas.append("⚠️  DISCLAIMER: Análise para fins educacionais.")
        linhas.append("    Sempre considere seu perfil de risco antes de tomar decisões.")
        linhas.append("=" * 80)

        return "\n".join(linhas)

    # ============================================================================
    # FLUXO COMPLETO: INÍCIO → DURANTE → FIM
    # ============================================================================

    def processar_operacao_completa(self, dados: DadosOperacao) -> str:
        """
        Fluxo completo de processamento de operação

        [INÍCIO] → [DURANTE] → [FIM]

        Args:
            dados: Dados da operação a processar

        Returns:
            Relatório executivo completo formatado
        """
        try:
            print("\n" + "=" * 80)
            print("🚀 INICIANDO PROCESSAMENTO DE OPERAÇÃO")
            print("=" * 80)

            # [INÍCIO] Validação de Gates
            print("\n[INÍCIO] Validando gates de segurança...")
            self.carregar_portfolio()

            valido, erro = self.validar_gates(dados)
            if not valido:
                print(erro)
                raise ValueError(erro)

            print("✅ Gates validados com sucesso")
            print(f"   ✓ Ticket: {dados.ticket}")
            print(f"   ✓ Ativo: {dados.currency_pair}")
            print(f"   ✓ Direção: {dados.direction}")
            print(f"   ✓ Preço: ${dados.entry_price:.5f}")
            print(f"   ✓ Volume: {dados.lots} lotes")

            # [DURANTE] Atualização de Portfólio
            print("\n[DURANTE] Atualizando portfólio...")
            self.adicionar_posicao(dados)
            self.atualizar_precos_mercado()
            self.salvar_portfolio()
            print("✅ Portfólio atualizado com sucesso")

            # [FIM] Geração de Relatório Executivo
            print("\n[FIM] Gerando relatório executivo completo...")
            relatorio = self.formatar_relatorio_executivo()

            print("\n✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
            print("=" * 80)

            return relatorio

        except Exception as e:
            self.logger.error(f"❌ Erro no processamento: {e}")
            raise


def main():
    """Função principal para teste"""
    print("🎯 Gestor do Fundo Completo - Sistema de Gestão Integrada")
    print("=" * 80)

    # Exemplo de uso
    gestor = GestorFundoCompleto()

    # Dados de exemplo
    dados_operacao = DadosOperacao(
        ticket="#TEST123456",
        currency_pair="EUR/USD",
        direction="LONG",
        entry_price=1.0850,
        lots=0.01,
        stop_loss=1.08,
        take_profit=1.095,
        strategy="Teste de integração do sistema",
        notes="Operação de exemplo para validação"
    )

    try:
        relatorio = gestor.processar_operacao_completa(dados_operacao)
        print("\n" + relatorio)
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
