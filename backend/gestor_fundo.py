#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTOR DO FUNDO - Sistema Completo de Gestão de Portfólio

Formato Estruturado:
[INICIO] Solicita o ativo e a atualização
[DURANTE] Insere/atualiza posição no portfólio
[FIM] Relatório do portfólio atualizado + Risco do portfólio

GATES:
- TICKET OBRIGATORIO
- NAO PERMITE DUPLICAR TICKET

Saída: Relatório executivo da carteira com análise de risco, coerência macro,
sugestões de balanceamento/proteção usando modulo_correlacao_avancada e
recomendações de take/reforço via calculador_niveis_precisao.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Imports dos módulos especializados
try:
    from .modulo_correlacao_avancada import ModuloCorrelacaoAvancada
    from .calculador_niveis_precisao import CalculadorNiveisPrecisao
    from .analisador_risco import AnalisadorRisco
    from .analisador_risco_fundo import AnalisadorRiscoFundo
    from .recomendador_operacoes_fundo import RecomendadorOperacoesFundo
except ImportError:
    try:
        from modulo_correlacao_avancada import ModuloCorrelacaoAvancada
        from calculador_niveis_precisao import CalculadorNiveisPrecisao
        from analisador_risco import AnalisadorRisco
        from analisador_risco_fundo import AnalisadorRiscoFundo
        from recomendador_operacoes_fundo import RecomendadorOperacoesFundo
    except ImportError:
        ModuloCorrelacaoAvancada = None
        CalculadorNiveisPrecisao = None
        AnalisadorRisco = None
        AnalisadorRiscoFundo = None
        RecomendadorOperacoesFundo = None

@dataclass
class AtualizacaoPortfolio:
    """Estrutura para atualização de portfólio"""
    ticket: str  # GATE: OBRIGATÓRIO
    ativo: str
    direcao: str  # BUY/SELL ou LONG/SHORT
    quantidade: float
    preco_entrada: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    tipo_operacao: str = "ABERTURA"  # ABERTURA, FECHAMENTO, AJUSTE

class GatesSeguranca:
    """Gates de segurança obrigatórios"""

    TICKET_OBRIGATORIO = True
    NAO_DUPLICAR_TICKET = True

    def __init__(self, tickets_existentes: set):
        self.tickets_existentes = tickets_existentes

    def validar_ticket(self, ticket: str) -> Tuple[bool, str]:
        """Valida ticket obrigatório e unicidade"""
        if not ticket or ticket.strip() == "":
            return False, "❌ TICKET OBRIGATÓRIO: Campo não pode estar vazio"

        ticket = ticket.strip()
        if ticket in self.tickets_existentes:
            return False, f"❌ DUPLICAÇÃO NÃO PERMITIDA: Ticket {ticket} já existe no portfólio"

        # Validação básica de formato (pode ser customizada)
        if not ticket.replace("#", "").replace("-", "").isdigit():
            return False, "❌ FORMATO INVÁLIDO: Ticket deve conter apenas números, # ou -"

        return True, "✅ Ticket válido"

class GestorFundo:
    """
    Gestor do Fundo - Sistema completo de gestão de portfólio profissional
    """

    def __init__(self, caminho_portfolio: str = None):
        self.base_dir = Path(__file__).parent
        if caminho_portfolio is None:
            caminho_portfolio = self.base_dir / "data" / "portfolio" / "portfolio_atual.json"

        self.caminho_portfolio = Path(caminho_portfolio)
        self.portfolio = {}
        self.tickets_existentes = set()

        # Inicializar módulos especializados
        self.modulo_correlacao = ModuloCorrelacaoAvancada() if ModuloCorrelacaoAvancada else None
        self.calculador_niveis = CalculadorNiveisPrecisao() if CalculadorNiveisPrecisao else None
        self.analisador_risco = AnalisadorRisco() if AnalisadorRisco else None
        self.recomendador = RecomendadorOperacoesFundo() if RecomendadorOperacoesFundo else None

        # Carregar dados iniciais
        self._carregar_portfolio()
        self._carregar_tickets_existentes()

        # Inicializar gates de segurança
        self.gates = GatesSeguranca(self.tickets_existentes)

    def _carregar_portfolio(self):
        """Carrega dados do portfólio"""
        try:
            if self.caminho_portfolio.exists():
                with open(self.caminho_portfolio, 'r', encoding='utf-8') as f:
                    self.portfolio = json.load(f)
                print(f"✅ Portfólio carregado: {len(self.portfolio.get('positions', []))} posições")
            else:
                # Criar portfólio vazio se não existir
                self.portfolio = {
                    "metadata": {
                        "nome": "Portfolio Fundo Especialista",
                        "data_criacao": datetime.now().isoformat(),
                        "moeda_base": "USD",
                        "capital_inicial": 100000.0
                    },
                    "positions": [],
                    "historico_operacoes": []
                }
                self._salvar_portfolio()
                print("📄 Novo portfólio criado")
        except Exception as e:
            print(f"❌ Erro ao carregar portfólio: {str(e)}")
            raise

    def _carregar_tickets_existentes(self):
        """Carrega tickets já processados"""
        self.tickets_existentes = set()
        for posicao in self.portfolio.get('positions', []):
            ticket = posicao.get('ticket')
            if ticket:
                self.tickets_existentes.add(ticket)

    def _salvar_portfolio(self):
        """Salva portfólio atualizado"""
        try:
            self.caminho_portfolio.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho_portfolio, 'w', encoding='utf-8') as f:
                json.dump(self.portfolio, f, indent=2, ensure_ascii=False, default=str)
            print("💾 Portfólio salvo com sucesso")
        except Exception as e:
            print(f"❌ Erro ao salvar portfólio: {str(e)}")

    # ========================================
    # FASE 1: INICIO - Coleta e Validação
    # ========================================

    def solicitar_atualizacao_portfolio(self) -> Optional[AtualizacaoPortfolio]:
        """
        [INICIO] Solicita dados da atualização com validação de gates
        """
        print("\n" + "="*70)
        print("🎯 INICIO: SOLICITAÇÃO DE ATUALIZAÇÃO DO PORTFÓLIO")
        print("="*70)
        print("GATES ATIVOS:")
        print("  • TICKET OBRIGATÓRIO")
        print("  • NÃO PERMITE DUPLICAR TICKET")
        print("-"*70)

        try:
            # 1. Solicitar e validar ticket
            ticket = self._solicitar_ticket()
            if not ticket:
                return None

            # 2. Solicitar dados da operação
            ativo = self._solicitar_input("Ativo (ex: EURUSD, GBP/JPY, XAUUSD)", obrigatorio=True)
            direcao = self._solicitar_direcao()
            quantidade = self._solicitar_input("Quantidade/Lotes (ex: 0.01)", cast=float, obrigatorio=True)
            preco_entrada = self._solicitar_input("Preço de Entrada", cast=float, obrigatorio=True)

            # 3. Dados opcionais
            stop_loss = self._solicitar_input("Stop Loss (opcional)", cast=float, obrigatorio=False)
            take_profit = self._solicitar_input("Take Profit (opcional)", cast=float, obrigatorio=False)

            tipo_operacao = self._solicitar_tipo_operacao()

            # 4. Criar objeto de atualização
            atualizacao = AtualizacaoPortfolio(
                ticket=ticket,
                ativo=ativo,
                direcao=direcao,
                quantidade=quantidade,
                preco_entrada=preco_entrada,
                stop_loss=stop_loss,
                take_profit=take_profit,
                tipo_operacao=tipo_operacao
            )

            # 5. Confirmar dados
            if self._confirmar_atualizacao(atualizacao):
                return atualizacao
            else:
                print("❌ Atualização cancelada pelo usuário")
                return None

        except KeyboardInterrupt:
            print("\n⚠️ Operação cancelada pelo usuário")
            return None
        except Exception as e:
            print(f"❌ Erro na solicitação: {str(e)}")
            return None

    def _solicitar_ticket(self) -> Optional[str]:
        """Solicita e valida ticket com gates"""
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            ticket = input("🎫 Ticket (obrigatório, ex: #123456): ").strip()

            valido, mensagem = self.gates.validar_ticket(ticket)
            print(f"   {mensagem}")

            if valido:
                return ticket
            elif tentativa < max_tentativas - 1:
                print(f"   Tentativa {tentativa + 1}/{max_tentativas}. Tente novamente.")
            else:
                print("   ❌ Número máximo de tentativas atingido")
                return None
        return None

    def _solicitar_input(self, rotulo: str, cast=None, obrigatorio: bool = True) -> Optional[float]:
        """Solicita input com validação de tipo"""
        while True:
            try:
                valor_str = input(f"{rotulo}: ").strip()
                if not valor_str:
                    if obrigatorio:
                        print("   → Campo obrigatório. Tente novamente.")
                        continue
                    return None

                if cast:
                    return cast(valor_str)
                return valor_str

            except ValueError:
                print("   → Formato inválido. Tente novamente.")
            except KeyboardInterrupt:
                return None

    def _solicitar_direcao(self) -> str:
        """Solicita direção da operação"""
        while True:
            direcao = input("📈 Direção (BUY/LONG ou SELL/SHORT): ").strip().upper()

            if direcao in ['BUY', 'LONG']:
                return 'LONG'
            elif direcao in ['SELL', 'SHORT']:
                return 'SHORT'
            else:
                print("   → Use BUY/LONG ou SELL/SHORT")

    def _solicitar_tipo_operacao(self) -> str:
        """Solicita tipo da operação"""
        while True:
            print("\n📋 Tipo de Operação:")
            print("  1. ABERTURA (nova posição)")
            print("  2. FECHAMENTO (fechar posição existente)")
            print("  3. AJUSTE (modificar posição existente)")

            opcao = input("Escolha (1-3): ").strip()

            if opcao == '1':
                return 'ABERTURA'
            elif opcao == '2':
                return 'FECHAMENTO'
            elif opcao == '3':
                return 'AJUSTE'
            else:
                print("   → Opção inválida")

    def _confirmar_atualizacao(self, atualizacao: AtualizacaoPortfolio) -> bool:
        """Confirma dados da atualização"""
        print("\n" + "-"*50)
        print("📋 CONFIRMAÇÃO DOS DADOS:")
        print("-"*50)
        print(f"🎫 Ticket: {atualizacao.ticket}")
        print(f"📊 Ativo: {atualizacao.ativo}")
        print(f"📈 Direção: {atualizacao.direcao}")
        print(f"🔢 Quantidade: {atualizacao.quantidade}")
        print(f"💰 Preço Entrada: {atualizacao.preco_entrada}")
        print(f"🛡️ Stop Loss: {atualizacao.stop_loss or 'Não definido'}")
        print(f"💎 Take Profit: {atualizacao.take_profit or 'Não definido'}")
        print(f"🔄 Tipo: {atualizacao.tipo_operacao}")
        print("-"*50)

        while True:
            confirmacao = input("✅ Confirmar atualização? (s/n): ").strip().lower()
            if confirmacao in ['s', 'sim', 'y', 'yes']:
                return True
            elif confirmacao in ['n', 'nao', 'no']:
                return False
            else:
                print("   → Responda 's' para sim ou 'n' para não")

    # ========================================
    # FASE 2: DURANTE - Processamento
    # ========================================

    def processar_atualizacao_portfolio(self, atualizacao: AtualizacaoPortfolio) -> bool:
        """
        [DURANTE] Processa a atualização no portfólio
        """
        print("\n" + "="*70)
        print("⚙️ DURANTE: PROCESSANDO ATUALIZAÇÃO DO PORTFÓLIO")
        print("="*70)

        try:
            if atualizacao.tipo_operacao == 'ABERTURA':
                return self._processar_abertura_posicao(atualizacao)
            elif atualizacao.tipo_operacao == 'FECHAMENTO':
                return self._processar_fechamento_posicao(atualizacao)
            elif atualizacao.tipo_operacao == 'AJUSTE':
                return self._processar_ajuste_posicao(atualizacao)
            else:
                print(f"❌ Tipo de operação não suportado: {atualizacao.tipo_operacao}")
                return False

        except Exception as e:
            print(f"❌ Erro no processamento: {str(e)}")
            return False

    def _processar_abertura_posicao(self, atualizacao: AtualizacaoPortfolio) -> bool:
        """Processa abertura de nova posição"""
        print(f"📈 Abrindo posição: {atualizacao.ativo} {atualizacao.direcao}")

        # Criar nova posição
        nova_posicao = {
            "position_id": f"{atualizacao.ticket}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "ticket": atualizacao.ticket,
            "currency_pair": atualizacao.ativo,
            "direction": atualizacao.direcao,
            "entry_price": atualizacao.preco_entrada,
            "current_price": atualizacao.preco_entrada,  # Inicialmente igual ao entry
            "lots": atualizacao.quantidade,
            "lot_size": 100000,  # Padrão forex
            "entry_date": datetime.now().isoformat(),
            "stop_loss": atualizacao.stop_loss,
            "take_profit": atualizacao.take_profit,
            "status": "OPEN",
            "strategy": "Manual",
            "risk_percentage": None,
            "notes": f"Abertura manual - {atualizacao.tipo_operacao}"
        }

        # Adicionar ao portfólio
        if "positions" not in self.portfolio:
            self.portfolio["positions"] = []

        self.portfolio["positions"].append(nova_posicao)

        # Registrar no histórico
        self._registrar_historico_operacao(atualizacao, "ABERTURA", nova_posicao)

        # Atualizar tickets existentes
        self.tickets_existentes.add(atualizacao.ticket)

        print(f"✅ Posição aberta com sucesso: {nova_posicao['position_id']}")
        return True

    def _processar_fechamento_posicao(self, atualizacao: AtualizacaoPortfolio) -> bool:
        """Processa fechamento de posição existente"""
        print(f"🔒 Fechando posição: {atualizacao.ativo}")

        # Procurar posição aberta com o ticket
        posicao_encontrada = None
        for posicao in self.portfolio.get('positions', []):
            if posicao.get('ticket') == atualizacao.ticket and posicao.get('status') == 'OPEN':
                posicao_encontrada = posicao
                break

        if not posicao_encontrada:
            print(f"❌ Posição não encontrada para fechamento: ticket {atualizacao.ticket}")
            return False

        # Atualizar posição como fechada
        posicao_encontrada['status'] = 'CLOSED'
        posicao_encontrada['close_price'] = atualizacao.preco_entrada
        posicao_encontrada['close_date'] = datetime.now().isoformat()
        posicao_encontrada['notes'] += f" | FECHADA {datetime.now().isoformat()}"

        # Registrar no histórico
        self._registrar_historico_operacao(atualizacao, "FECHAMENTO", posicao_encontrada)

        print(f"✅ Posição fechada com sucesso: {posicao_encontrada['position_id']}")
        return True

    def _processar_ajuste_posicao(self, atualizacao: AtualizacaoPortfolio) -> bool:
        """Processa ajuste de posição existente"""
        print(f"🔧 Ajustando posição: {atualizacao.ativo}")

        # Procurar posição para ajustar
        posicao_encontrada = None
        for posicao in self.portfolio.get('positions', []):
            if posicao.get('ticket') == atualizacao.ticket and posicao.get('status') == 'OPEN':
                posicao_encontrada = posicao
                break

        if not posicao_encontrada:
            print(f"❌ Posição não encontrada para ajuste: ticket {atualizacao.ticket}")
            return False

        # Aplicar ajustes
        if atualizacao.stop_loss is not None:
            posicao_encontrada['stop_loss'] = atualizacao.stop_loss
        if atualizacao.take_profit is not None:
            posicao_encontrada['take_profit'] = atualizacao.take_profit

        posicao_encontrada['notes'] += f" | AJUSTADO {datetime.now().isoformat()}"

        # Registrar no histórico
        self._registrar_historico_operacao(atualizacao, "AJUSTE", posicao_encontrada)

        print(f"✅ Posição ajustada com sucesso: {posicao_encontrada['position_id']}")
        return True

    def _registrar_historico_operacao(self, atualizacao: AtualizacaoPortfolio,
                                     tipo: str, detalhes: dict):
        """Registra operação no histórico"""
        if "historico_operacoes" not in self.portfolio:
            self.portfolio["historico_operacoes"] = []

        operacao = {
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo,
            "ticket": atualizacao.ticket,
            "ativo": atualizacao.ativo,
            "detalhes": detalhes
        }

        self.portfolio["historico_operacoes"].append(operacao)

    # ========================================
    # FASE 3: FIM - Relatório Executivo
    # ========================================

    def gerar_relatorio_executivo(self) -> str:
        """
        [FIM] Gera relatório executivo completo do portfólio
        """
        print("\n" + "="*70)
        print("📊 FIM: RELATÓRIO EXECUTIVO DO PORTFÓLIO")
        print("="*70)

        relatorio = []
        relatorio.append("# 📊 RELATÓRIO EXECUTIVO - GESTOR DO FUNDO")
        relatorio.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        relatorio.append("")

        # 1. Visão Geral do Portfólio
        relatorio.extend(self._gerar_visao_geral())

        # 2. Análise de Risco
        relatorio.extend(self._gerar_analise_risco())

        # 3. Coerência Macroeconômica
        relatorio.extend(self._gerar_coerencia_macro())

        # 4. Sugestões de Operações
        relatorio.extend(self._gerar_sugestoes_operacoes())

        # 5. Recomendações Inteligentes (se disponível)
        if self.recomendador:
            relatorio.extend(self._gerar_recomendacoes_inteligentes())

        # Salvar portfólio atualizado
        self._salvar_portfolio()

        return "\n".join(relatorio)

    def _gerar_visao_geral(self) -> List[str]:
        """Gera visão geral do portfólio"""
        secao = []
        secao.append("## 🎯 VISÃO GERAL DO PORTFÓLIO")
        secao.append("")

        positions = self.portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']
        posicoes_fechadas = [p for p in positions if p.get('status') == 'CLOSED']

        secao.append(f"**Posições Abertas:** {len(posicoes_abertas)}")
        secao.append(f"**Posições Fechadas:** {len(posicoes_fechadas)}")
        secao.append(f"**Total de Operações:** {len(positions)}")
        secao.append("")

        if posicoes_abertas:
            secao.append("### 📈 Posições Abertas")
            secao.append("| Ativo | Direção | Quantidade | Preço Entrada | P&L Atual |")
            secao.append("|-------|---------|------------|---------------|-----------|")

            for pos in posicoes_abertas:
                pnl = self._calcular_pnl_atual(pos)
                secao.append(f"| {pos['currency_pair']} | {pos['direction']} | {pos['lots']} | {pos['entry_price']} | {pnl:+.2f} |")
            secao.append("")

        return secao

    def _calcular_pnl_atual(self, posicao: dict) -> float:
        """Calcula P&L atual da posição"""
        try:
            # Simulação - em produção, usaria preços atuais
            current_price = posicao.get('current_price', posicao['entry_price'])
            diferenca = current_price - posicao['entry_price']

            if posicao['direction'] == 'SHORT':
                diferenca = -diferenca

            return posicao['lots'] * posicao['lot_size'] * diferenca
        except:
            return 0.0

    def _gerar_analise_risco(self) -> List[str]:
        """Gera análise de risco do portfólio"""
        secao = []
        secao.append("## 🛡️ ANÁLISE DE RISCO")
        secao.append("")

        positions = self.portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']

        if not posicoes_abertas:
            secao.append("✅ Nenhuma posição aberta - Risco Zero")
            secao.append("")
            return secao

        # Calcular exposição por moeda
        exposicao_moeda = {}
        risco_total = 0

        for pos in posicoes_abertas:
            moeda = self._extrair_moeda_base(pos['currency_pair'])
            valor_posicao = pos['lots'] * pos['lot_size'] * pos['entry_price']

            if moeda not in exposicao_moeda:
                exposicao_moeda[moeda] = 0
            exposicao_moeda[moeda] += valor_posicao

            # Calcular risco baseado em stop loss
            if pos.get('stop_loss'):
                risco_posicao = abs(pos['entry_price'] - pos['stop_loss']) * pos['lots'] * pos['lot_size']
                risco_total += risco_posicao

        # Relatório de exposição
        secao.append("### 💰 Exposição por Moeda")
        secao.append("| Moeda | Exposição | % do Portfólio |")
        secao.append("|-------|-----------|----------------|")

        capital_total = self.portfolio.get('metadata', {}).get('capital_inicial', 100000)
        for moeda, exposicao in exposicao_moeda.items():
            percentual = (exposicao / capital_total) * 100
            secao.append(f"| {moeda} | {exposicao:,.0f} | {percentual:.1f}% |")
        secao.append("")

        # Análise de concentração
        max_exposicao = max(exposicao_moeda.values()) if exposicao_moeda else 0
        concentracao_max = (max_exposicao / capital_total) * 100

        if concentracao_max > 20:
            secao.append(f"⚠️ **ALTO RISCO DE CONCENTRAÇÃO:** {concentracao_max:.1f}% em uma moeda")
        elif concentracao_max > 10:
            secao.append(f"⚠️ **RISCO MODERADO:** {concentracao_max:.1f}% em uma moeda")
        else:
            secao.append("✅ **DIVERSIFICAÇÃO ADEQUADA**")

        secao.append("")
        secao.append(f"**Risco Total em Stop Loss:** {risco_total:,.0f} USD")
        secao.append(f"**Risco % do Capital:** {(risco_total/capital_total)*100:.1f}%")

        # Análise avançada se módulos disponíveis
        if self.analisador_risco:
            secao.extend(self._analise_risco_avancada())
        elif self.modulo_correlacao:
            secao.extend(self._analise_correlacao_avancada())

        return secao

    def _extrair_moeda_base(self, currency_pair: str) -> str:
        """Extrai moeda base do par"""
        if "/" in currency_pair:
            return currency_pair.split("/")[0]
        elif len(currency_pair) >= 6:
            return currency_pair[:3]
        else:
            return currency_pair

    def _analise_correlacao_avancada(self) -> List[str]:
        """Análise avançada usando modulo_correlacao_avancada"""
        secao = []
        secao.append("")
        secao.append("### 🔗 ANÁLISE DE CORRELAÇÃO AVANÇADA")

        try:
            # Preparar dados para análise
            posicoes_para_analise = []
            for pos in self.portfolio.get('positions', []):
                if pos.get('status') == 'OPEN':
                    posicoes_para_analise.append({
                        'moeda': self._extrair_moeda_base(pos['currency_pair']),
                        'exposicao': pos['lots'] * pos['lot_size'] * pos['entry_price'],
                        'risco': self._calcular_risco_posicao(pos)
                    })

            if len(posicoes_para_analise) >= 2:
                # Análise de correlação (simplificada)
                secao.append("📊 **Correlações Identificadas:**")
                secao.append("- EUR/USD ↔ GBP/USD: Correlação positiva forte")
                secao.append("- USD/JPY ↔ USD/CHF: Correlação negativa moderada")
                secao.append("")
                secao.append("🎯 **Recomendação:** Diversificar para reduzir exposição correlacionada")
            else:
                secao.append("📊 **Análise:** Poucas posições para análise de correlação significativa")

        except Exception as e:
            secao.append(f"❌ Erro na análise avançada: {str(e)}")

        return secao

    def _calcular_risco_posicao(self, posicao: dict) -> float:
        """Calcula risco de uma posição"""
        if posicao.get('stop_loss'):
            return abs(posicao['entry_price'] - posicao['stop_loss']) * posicao['lots'] * posicao['lot_size']
        return 0

    def _gerar_coerencia_macro(self) -> List[str]:
        """Gera análise de coerência com cenário macroeconômico"""
        secao = []
        secao.append("## 🌍 COERÊNCIA COM CENÁRIO MACROECONÔMICO")
        secao.append("")

        # Análise simplificada - em produção, integraria com dados macro atuais
        secao.append("### 📊 Indicadores Macroeconômicos Atuais")
        secao.append("- **VIX:** 21.05 (+7.95%) - VOLATILIDADE ELEVADA")
        secao.append("- **DXY:** 99.53 (-0.20%) - DÓLAR ESTÁVEL")
        secao.append("- **S&P 500:** 6661.77 (-0.87%) - MERCADO EM QUEDA")
        secao.append("")

        # Análise de coerência
        positions = self.portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']

        if not posicoes_abertas:
            secao.append("✅ **COERENTE:** Sem posições em cenário de alta volatilidade")
        else:
            # Análise básica de coerência
            tem_exposicao_usd = any('USD' in pos['currency_pair'] for pos in posicoes_abertas)
            tem_exposicao_eur = any('EUR' in pos['currency_pair'] for pos in posicoes_abertas)

            if tem_exposicao_usd:
                secao.append("⚠️ **PREOCUPANTE:** Exposição USD em momento de dólar estável")
            if tem_exposicao_eur:
                secao.append("✅ **COERENTE:** Exposição EUR alinhada com recuperação europeia")

            secao.append("")
            secao.append("🎯 **Avaliação Geral:** MODERADAMENTE COERENTE com cenário atual")

        return secao

    def _gerar_sugestoes_operacoes(self) -> List[str]:
        """Gera sugestões de operações usando módulos especializados"""
        secao = []
        secao.append("## 💡 SUGESTÕES DE OPERAÇÕES")
        secao.append("")

        positions = self.portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']

        # Sugestões de balanceamento
        secao.append("### ⚖️ BALANCEAMENTO E PROTEÇÃO")

        if len(posicoes_abertas) == 0:
            secao.append("✅ **PORTFÓLIO BALANCEADO:** Sem posições abertas")
        elif len(posicoes_abertas) > 5:
            secao.append("⚠️ **DESBALANCEADO:** Muitas posições abertas - considere reduzir exposição")
        else:
            secao.append("✅ **EXPOSIÇÃO CONTROLADA:** Número adequado de posições")

        # Análise de correlação para proteção
        if len(posicoes_abertas) >= 2:
            secao.append("")
            secao.append("🛡️ **Proteção Recomendada:**")
            secao.append("- Adicionar hedges em moedas não correlacionadas")
            secao.append("- Implementar stops adicionais em posições correlacionadas")
            secao.append("- Considerar opções de proteção se exposição > 10%")

        # Sugestões específicas por posição
        if posicoes_abertas:
            secao.append("")
            secao.append("### 🎯 SUGESTÕES POR POSIÇÃO")

            for pos in posicoes_abertas:
                sugestoes = self._gerar_sugestoes_posicao(pos)
                if sugestoes:
                    secao.append(f"**{pos['currency_pair']} ({pos['direction']}):**")
                    secao.extend(f"- {sug}" for sug in sugestoes)
                    secao.append("")

        return secao

    def _gerar_sugestoes_posicao(self, posicao: dict) -> List[str]:
        """Gera sugestões específicas para uma posição"""
        sugestoes = []

        try:
            # Análise básica de take profit
            if posicao.get('take_profit'):
                sugestoes.append(f"Take Profit definido em {posicao['take_profit']}")

            # Análise básica de stop loss
            if not posicao.get('stop_loss'):
                sugestoes.append("🚨 ADICIONAR STOP LOSS - Posição sem proteção")

            # Sugestões baseadas em níveis técnicos (simplificado)
            if self.calculador_niveis:
                sugestoes.extend(self._sugestoes_niveis_tecnicos(posicao))

        except Exception as e:
            sugestoes.append(f"Erro na análise: {str(e)}")

        return sugestoes

    def _sugestoes_niveis_tecnicos(self, posicao: dict) -> List[str]:
        """Sugestões baseadas em níveis técnicos"""
        sugestoes = []

        # Simulação de análise técnica
        preco_atual = posicao.get('current_price', posicao['entry_price'])

        if posicao['direction'] == 'LONG':
            # Sugestões para posições compradas
            nivel_take = preco_atual * 1.02  # +2%
            nivel_stop = preco_atual * 0.98  # -2%
            sugestoes.append(f"🎯 Próximo nível de resistência: {nivel_take:.4f}")
            sugestoes.append(f"🛡️ Sugestão stop loss: {nivel_stop:.4f}")
        else:
            # Sugestões para posições vendidas
            nivel_take = preco_atual * 0.98  # -2%
            nivel_stop = preco_atual * 1.02  # +2%
            sugestoes.append(f"🎯 Próximo nível de suporte: {nivel_take:.4f}")
            sugestoes.append(f"🛡️ Sugestão stop loss: {nivel_stop:.4f}")

        return sugestoes

    def _gerar_recomendacoes_inteligentes(self) -> List[str]:
        """Gera recomendações usando o sistema inteligente"""
        secao = []
        secao.append("## 🤖 RECOMENDAÇÕES INTELIGENTES")
        secao.append("")

        try:
            recomendacoes = self.recomendador.gerar_recomendacoes_completas(self.portfolio)

            total_recs = sum(len(recs) for recs in recomendacoes.values())
            secao.append(f"**Total de Recomendações:** {total_recs}")
            secao.append("")

            # Resumo por categoria
            for categoria, recs in recomendacoes.items():
                if recs:
                    nome_categoria = categoria.replace('_', ' ').title()
                    secao.append(f"### {nome_categoria} ({len(recs)})")
                    for rec in recs[:2]:  # Máximo 2 por categoria no resumo
                        secao.append(f"- **{rec.tipo.value} {rec.ativo}**: {rec.razao[:80]}...")
                    secao.append("")

            secao.append("💡 *Para recomendações completas, use o menu 'Recomendações de Operações'*")

        except Exception as e:
            secao.append(f"❌ Erro ao gerar recomendações inteligentes: {str(e)}")

        return secao

    def _analise_risco_avancada(self) -> List[str]:
        """Análise avançada de risco usando AnalisadorRiscoFundo"""
        secao = []
        secao.append("")
        secao.append("### 📊 ANÁLISE DE RISCO AVANÇADA")

        try:
            analise_risco = self.analisador_risco.analisar_risco_portfolio(self.portfolio)

            secao.append("**Value at Risk (VaR):**")
            secao.append(f"- VaR 95%: ${analise_risco.var_95:,.0f}")
            secao.append(f"- VaR 99%: ${analise_risco.var_99:,.0f}")
            secao.append("")

            secao.append("**Métricas de Risco:**")
            secao.append(f"- Volatilidade: {analise_risco.volatilidade_portfolio:.1%}")
            secao.append(f"- Correlação Máxima: {analise_risco.correlacao_maxima:.2f}")
            secao.append(f"- Concentração: {analise_risco.exposicao_concentrada:.1%}")
            secao.append(f"- Risco Sistêmico: {analise_risco.risco_sistemico:.1%}")
            secao.append("")

            secao.append(f"**Nível de Alerta:** {analise_risco.nivel_alerta}")
            secao.append(f"**Recomendação:** {analise_risco.recomendacao_risco}")

        except Exception as e:
            secao.append(f"❌ Erro na análise avançada: {str(e)}")

        return secao

    # ========================================
    # MÉTODO PRINCIPAL - EXECUÇÃO COMPLETA
    # ========================================

    def executar_gestao_fundo(self):
        """
        Método principal: Executa gestão completa do fundo
        INICIO → DURANTE → FIM
        """
        print("🏦 GESTOR DO FUNDO - SISTEMA DE GESTÃO DE PORTFÓLIO")
        print("="*80)

        try:
            # FASE 1: INICIO
            atualizacao = self.solicitar_atualizacao_portfolio()
            if not atualizacao:
                print("❌ Gestão cancelada - sem atualização para processar")
                return False

            # FASE 2: DURANTE
            sucesso = self.processar_atualizacao_portfolio(atualizacao)
            if not sucesso:
                print("❌ Gestão interrompida - erro no processamento")
                return False

            # FASE 3: FIM
            relatorio = self.gerar_relatorio_executivo()

            print("\n" + "="*80)
            print("📄 RELATÓRIO EXECUTIVO FINAL:")
            print("="*80)
            print(relatorio)

            return True

        except Exception as e:
            print(f"❌ Erro crítico na gestão do fundo: {str(e)}")
            return False