#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Integrado de Atualização de Portfólio com Correlação Avançada
Gestor do Fundo - Sistema completo para atualização inteligente de portfólio

Funcionalidades:
1. Gates de segurança obrigatórios (ticket + anti-duplicação)
2. Atualização estruturada de posições
3. Análise integrada de risco + correlação + níveis + macroeconomia
4. Relatório executivo inteligente com recomendações
5. Sugestões de balanceamento/proteção usando correlação avançada
6. Recomendações de take/reforço baseadas em níveis de preço
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Garantir import de todos os módulos necessários
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Imports dos módulos existentes
from gestor_portfolio_atualizado import GestorPortfolioAtualizado
from calculador_niveis_precisao import CalculadorNiveisPrecisao
from analisador_risco import AnalisadorRiscoPortfolio
# from detector_oportunidades_ml import AnalisadorMacroEconomico  # Removido temporariamente
from modulo_correlacao_avancada import ModuloCorrelacaoAvancada
from motor_niveis_portfolio import MotorNiveisPortfolio

# Analisador macro simplificado (inline)
class AnalisadorMacroEconomicoSimplificado:
    """Versão simplificada do analisador macroeconômico"""

    def coletar_dados_dxy(self, periodo: int = 30) -> Dict:
        """Retorna dados simulados do DXY"""
        return {
            'preco_atual': 104.5,
            'variacao_diaria': 0.2,
            'tendencia_7d': 1.1,
            'volatilidade': 0.8,
            'regime': 'DOLAR_MODERADO'
        }

    def identificar_eventos_criticos(self) -> List:
        """Retorna eventos simulados"""
        return [
            {
                'evento': 'Reunião FOMC',
                'data': '2025-11-08',
                'impacto': 2,
                'moedas_afetadas': ['USD']
            }
        ]

@dataclass
class RecomendacaoAprendizado:
    """Estrutura para recomendações com tracking de aprendizado"""
    ticket_id: str
    tipo_recomendacao: str  # 'TAKE', 'REFORCO', 'HEDGE'
    ativo: str
    recomendacao: Dict
    data_criacao: datetime
    score_assertividade: Optional[float] = None
    performance_real: Optional[float] = None
    data_avaliacao: Optional[datetime] = None
    parametros_modelo: Dict = None  # Parâmetros usados na geração

@dataclass
class BaseRecomendacoes24h:
    """Base de dados para recomendações com ciclo de aprendizado 24h"""
    recomendacoes: List[RecomendacaoAprendizado] = None
    caminho_arquivo: str = "BaseDeRecomendacoes_24h.json"

    def __post_init__(self):
        if self.recomendacoes is None:
            self.recomendacoes = []
        self.carregar_base()

    def carregar_base(self):
        """Carrega a base de recomendações do arquivo"""
        try:
            if os.path.exists(self.caminho_arquivo):
                with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.recomendacoes = [
                        RecomendacaoAprendizado(**rec) for rec in dados.get('recomendacoes', [])
                    ]
                    # Converter strings de data para datetime
                    for rec in self.recomendacoes:
                        if isinstance(rec.data_criacao, str):
                            rec.data_criacao = datetime.fromisoformat(rec.data_criacao.replace('Z', '+00:00'))
                        if rec.data_avaliacao and isinstance(rec.data_avaliacao, str):
                            rec.data_avaliacao = datetime.fromisoformat(rec.data_avaliacao.replace('Z', '+00:00'))
        except Exception as e:
            print(f"Erro ao carregar base de recomendações: {e}")
            self.recomendacoes = []

    def salvar_base(self):
        """Salva a base de recomendações no arquivo"""
        try:
            dados = {
                'recomendacoes': [
                    {
                        'ticket_id': r.ticket_id,
                        'tipo_recomendacao': r.tipo_recomendacao,
                        'ativo': r.ativo,
                        'recomendacao': r.recomendacao,
                        'data_criacao': r.data_criacao.isoformat(),
                        'score_assertividade': r.score_assertividade,
                        'performance_real': r.performance_real,
                        'data_avaliacao': r.data_avaliacao.isoformat() if r.data_avaliacao else None,
                        'parametros_modelo': r.parametros_modelo
                    } for r in self.recomendacoes
                ],
                'ultima_atualizacao': datetime.now(timezone.utc).isoformat()
            }
            with open(self.caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar base de recomendações: {e}")

    def adicionar_recomendacao(self, recomendacao: RecomendacaoAprendizado):
        """Adiciona uma nova recomendação à base"""
        self.recomendacoes.append(recomendacao)
        self.salvar_base()

    def obter_pendencias_24h(self) -> List[RecomendacaoAprendizado]:
        """Retorna recomendações pendentes (>24h sem avaliação)"""
        agora = datetime.now(timezone.utc)
        pendencias = []
        for rec in self.recomendacoes:
            if rec.score_assertividade is None:  # Não avaliada ainda
                diferenca = agora - rec.data_criacao
                if diferenca.total_seconds() > 24 * 3600:  # > 24 horas
                    pendencias.append(rec)
        return pendencias

    def avaliar_assertividade(self, ticket_id: str, performance_real: float):
        """Avalia a assertividade de uma recomendação"""
        for rec in self.recomendacoes:
            if rec.ticket_id == ticket_id and rec.score_assertividade is None:
                # Calcular score baseado na performance real vs esperada
                # Lógica simplificada: score = 100 - |erro_percentual|
                if 'performance_esperada' in rec.recomendacao:
                    perf_esperada = rec.recomendacao['performance_esperada']
                    erro = abs(performance_real - perf_esperada)
                    score = max(0, 100 - (erro * 100))  # Score de 0-100
                else:
                    score = 50.0  # Score neutro se não há expectativa

                rec.score_assertividade = score
                rec.performance_real = performance_real
                rec.data_avaliacao = datetime.now(timezone.utc)
                break
        self.salvar_base()

    def limpar_avaliadas(self):
        """Remove recomendações já avaliadas (>24h)"""
        agora = datetime.now(timezone.utc)
        self.recomendacoes = [
            rec for rec in self.recomendacoes
            if rec.data_avaliacao is None or (agora - rec.data_avaliacao).total_seconds() <= 24 * 3600
        ]
        self.salvar_base()

    def obter_estatisticas_aprendizado(self) -> Dict:
        """Retorna estatísticas do aprendizado"""
        avaliadas = [r for r in self.recomendacoes if r.score_assertividade is not None]
        if not avaliadas:
            return {'total_avaliadas': 0, 'score_medio': 0, 'taxa_acerto': 0}

        scores = [r.score_assertividade for r in avaliadas]
        score_medio = sum(scores) / len(scores)
        taxa_acerto = len([s for s in scores if s >= 70]) / len(scores)  # >70% considerado acerto

        return {
            'total_avaliadas': len(avaliadas),
            'score_medio': round(score_medio, 2),
            'taxa_acerto': round(taxa_acerto * 100, 2),
            'ultima_avaliacao': max((r.data_avaliacao for r in avaliadas), default=None)
        }

class SistemaAutoAvaliacao:
    """Sistema de autoavaliação e ajuste de parâmetros baseado em aprendizado"""

    def __init__(self, base_recomendacoes: BaseRecomendacoes24h):
        self.base_recomendacoes = base_recomendacoes
        self.parametros_correlacao = {
            'threshold_correlacao': 0.7,  # Threshold para considerar correlação forte
            'peso_volatilidade': 0.3,     # Peso da volatilidade na análise
            'janela_analise_dias': 30,   # Janela de análise em dias
            'fator_ajuste_score': 1.0    # Fator multiplicativo para scores
        }
        self.parametros_niveis = {
            'threshold_suporte_resistencia': 0.02,  # 2% threshold para níveis
            'peso_volume': 0.4,                     # Peso do volume na análise
            'min_pontos_nivel': 3,                  # Mínimo de pontos para confirmar nível
            'fator_risco_take': 0.8                 # Fator de risco para sugestões take
        }
        self.historico_ajustes = []

    def executar_ciclo_aprendizado(self) -> Dict:
        """
        Executa o ciclo completo de aprendizado (FASE 0)
        """
        print("🧠 EXECUTANDO CICLO DE APRENDIZADO (FASE 0)")
        print("-" * 50)

        # 1. Verificar pendências >24h
        pendencias = self.base_recomendacoes.obter_pendencias_24h()
        print(f"📋 Pendências encontradas: {len(pendencias)} recomendações >24h")

        # 2. Avaliar assertividade
        resultados_avaliacao = []
        for recomendacao in pendencias:
            resultado = self._avaliar_recomendacao_individual(recomendacao)
            resultados_avaliacao.append(resultado)

        # 3. Autoavaliação e ajuste
        ajustes_realizados = self._autoavaliar_e_ajustar(resultados_avaliacao)

        # 4. Limpeza
        self.base_recomendacoes.limpar_avaliadas()
        print(f"🧹 Limpeza realizada: {len(pendencias)} entradas avaliadas removidas")

        # Estatísticas finais
        estatisticas = self.base_recomendacoes.obter_estatisticas_aprendizado()

        resultado_ciclo = {
            'pendencias_processadas': len(pendencias),
            'resultados_avaliacao': resultados_avaliacao,
            'ajustes_realizados': ajustes_realizados,
            'estatisticas_aprendizado': estatisticas,
            'timestamp_ciclo': datetime.now(timezone.utc)
        }

        print(f"✅ Ciclo de aprendizado concluído: Score médio {estatisticas['score_medio']}%, Taxa acerto {estatisticas['taxa_acerto']}%")
        return resultado_ciclo

    def _avaliar_recomendacao_individual(self, recomendacao: RecomendacaoAprendizado) -> Dict:
        """Avalia uma recomendação individual"""
        # Simulação de coleta de dados de mercado pós-24h
        performance_real = self._simular_performance_mercado(recomendacao)

        # Avaliar assertividade
        self.base_recomendacoes.avaliar_assertividade(recomendacao.ticket_id, performance_real)

        return {
            'ticket_id': recomendacao.ticket_id,
            'tipo': recomendacao.tipo_recomendacao,
            'ativo': recomendacao.ativo,
            'performance_real': performance_real,
            'score_calculado': recomendacao.score_assertividade
        }

    def _simular_performance_mercado(self, recomendacao: RecomendacaoAprendizado) -> float:
        """Simula a performance real do mercado (dados pós-24h)"""
        # Lógica simplificada - em produção usaria dados reais de mercado
        import random
        base_performance = random.uniform(-0.05, 0.05)  # -5% a +5%

        # Ajustar baseado no tipo de recomendação
        if recomendacao.tipo_recomendacao == 'TAKE':
            # Take profit: assumir que o mercado seguiu a tendência esperada
            ajuste = random.uniform(0.8, 1.2)
        elif recomendacao.tipo_recomendacao == 'REFORCO':
            # Reforço: assumir movimento contrário ao esperado (risco maior)
            ajuste = random.uniform(0.6, 1.4)
        else:  # HEDGE
            # Hedge: assumir proteção funcionou
            ajuste = random.uniform(0.9, 1.1)

        return base_performance * ajuste

    def _autoavaliar_e_ajustar(self, resultados_avaliacao: List[Dict]) -> Dict:
        """Autoavaliação e ajuste dos parâmetros baseado nos resultados"""
        if not resultados_avaliacao:
            return {'ajustes_realizados': False, 'motivo': 'Nenhuma avaliação disponível'}

        # Calcular métricas de performance
        scores = [r['score_calculado'] for r in resultados_avaliacao if r['score_calculado'] is not None]
        if not scores:
            return {'ajustes_realizados': False, 'motivo': 'Nenhum score válido'}

        score_medio = sum(scores) / len(scores)
        taxa_acerto = len([s for s in scores if s >= 70]) / len(scores)

        ajustes = {}

        # Ajustar parâmetros de correlação se score baixo
        if score_medio < 60:
            # Diminuir threshold para detectar mais correlações
            self.parametros_correlacao['threshold_correlacao'] = max(0.5,
                self.parametros_correlacao['threshold_correlacao'] - 0.05)
            ajustes['correlacao_threshold'] = self.parametros_correlacao['threshold_correlacao']

            # Aumentar peso da volatilidade
            self.parametros_correlacao['peso_volatilidade'] = min(0.5,
                self.parametros_correlacao['peso_volatilidade'] + 0.05)
            ajustes['correlacao_peso_volatilidade'] = self.parametros_correlacao['peso_volatilidade']

        # Ajustar parâmetros de níveis se taxa de acerto baixa
        if taxa_acerto < 0.6:
            # Diminuir threshold para detectar mais níveis
            self.parametros_niveis['threshold_suporte_resistencia'] = max(0.01,
                self.parametros_niveis['threshold_suporte_resistencia'] - 0.005)
            ajustes['niveis_threshold'] = self.parametros_niveis['threshold_suporte_resistencia']

            # Aumentar peso do volume
            self.parametros_niveis['peso_volume'] = min(0.6,
                self.parametros_niveis['peso_volume'] + 0.05)
            ajustes['niveis_peso_volume'] = self.parametros_niveis['peso_volume']

        # Registrar ajuste no histórico
        if ajustes:
            self.historico_ajustes.append({
                'timestamp': datetime.now(timezone.utc),
                'score_medio': score_medio,
                'taxa_acerto': taxa_acerto,
                'ajustes_realizados': ajustes
            })

        return {
            'ajustes_realizados': bool(ajustes),
            'score_medio': round(score_medio, 2),
            'taxa_acerto': round(taxa_acerto * 100, 2),
            'parametros_ajustados': ajustes
        }

    def obter_parametros_otimizados(self) -> Dict:
        """Retorna os parâmetros atuais otimizados"""
        return {
            'correlacao': self.parametros_correlacao.copy(),
            'niveis': self.parametros_niveis.copy(),
            'historico_ajustes': self.historico_ajustes[-5:] if self.historico_ajustes else []  # Últimos 5 ajustes
        }

@dataclass
class SolicitacaoAtualizacao:
    """Estrutura para solicitação de atualização de portfólio"""
    ticket: str
    ativo: str  # Par de moedas (ex: "EUR/USD")
    tipo_operacao: str  # "ABRIR", "FECHAR", "AJUSTAR"
    direcao: str  # "LONG", "SHORT"
    lots: float
    preco_entrada: float
    stop_loss: Optional[float] = None
    take_profit: Optional[List[Dict]] = None
    justificativa: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class RelatorioExecutivoInteligente:
    """Relatório executivo completo com todas as análises"""
    timestamp: datetime
    portfolio_resumo: Dict
    analise_risco: Dict
    validacao_macroeconomica: Dict
    analise_correlacao_sistemica: Dict
    sugestoes_balanceamento_protecao: Dict
    sugestoes_niveis_take_reforco: Dict
    recomendacoes_finais_integradas: List[Dict]

class SistemaAtualizacaoPortfolioInteligente:
    """
    Sistema integrado para atualização inteligente de portfólio
    com análise avançada de correlação e níveis de preço
    """

    def __init__(self, caminho_portfolio: str = None):
        """Inicializa o sistema integrado"""

        # Caminhos padrão
        if caminho_portfolio is None:
            caminho_portfolio = os.path.join(BASE_DIR, "data", "portfolio", "portfolio_atual.json")

        # === SISTEMA DE APRENDIZADO ===
        # Inicializar base de recomendações 24h
        self.base_recomendacoes = BaseRecomendacoes24h()
        self.sistema_autoavaliacao = SistemaAutoAvaliacao(self.base_recomendacoes)

        # Executar FASE 0: Ciclo de Aprendizado (sempre antes de qualquer operação)
        self._executar_fase_aprendizado()

        # Inicializar módulos com parâmetros otimizados
        self.gestor_portfolio = GestorPortfolioAtualizado(caminho_portfolio)
        self.calculador_niveis = CalculadorNiveisPrecisao()
        self.analisador_risco = AnalisadorRiscoPortfolio(caminho_portfolio)
        self.analisador_macro = AnalisadorMacroEconomicoSimplificado()  # Versão simplificada
        self.modulo_correlacao = ModuloCorrelacaoAvancada()
        self.motor_niveis = MotorNiveisPortfolio()

        # Aplicar parâmetros otimizados pelos módulos
        self._aplicar_parametros_otimizados()

        # Cache e controle
        self.tickets_processados = set()
        self._carregar_tickets_existentes()

        # Configurações
        self.caminho_reports = os.path.join(BASE_DIR, "reports")
        os.makedirs(self.caminho_reports, exist_ok=True)

        print("🚀 Sistema Integrado de Atualização de Portfólio - INICIALIZADO")
        print("✅ Módulos carregados: Portfolio, Níveis, Risco, Macro, Correlação")
        print("🧠 Sistema de Aprendizado: Ativo")
        print("=" * 70)

    def _carregar_tickets_existentes(self):
        """Carrega tickets já processados para evitar duplicação"""
        try:
            portfolio = self.gestor_portfolio.portfolio
            self.tickets_processados = set()

            for posicao in portfolio.get('positions', []):
                ticket = posicao.get('ticket')
                if ticket:
                    self.tickets_processados.add(ticket)

            print(f"📋 Tickets existentes carregados: {len(self.tickets_processados)}")

        except Exception as e:
            print(f"⚠️ Erro ao carregar tickets existentes: {e}")
            self.tickets_processados = set()

    # ========================================
    # SISTEMA DE APRENDIZADO (FASE 0)
    # ========================================

    def _executar_fase_aprendizado(self):
        """Executa a FASE 0: Ciclo de Aprendizado (sempre antes de qualquer operação)"""
        try:
            resultado_aprendizado = self.sistema_autoavaliacao.executar_ciclo_aprendizado()

            # Log do resultado
            estatisticas = resultado_aprendizado['estatisticas_aprendizado']
            if estatisticas['total_avaliadas'] > 0:
                print("🧠 APRENDIZADO EXECUTADO:")
                print(f"   📊 Avaliações processadas: {resultado_aprendizado['pendencias_processadas']}")
                print(f"   🎯 Score médio: {estatisticas['score_medio']}%")
                print(f"   ✅ Taxa acerto: {estatisticas['taxa_acerto']}%")

                ajustes = resultado_aprendizado['ajustes_realizados']
                if ajustes.get('ajustes_realizados', False):
                    print(f"   🔧 Parâmetros ajustados: {len(ajustes.get('parametros_ajustados', {}))} parâmetros")
                else:
                    print("   📌 Modelo mantido (performance satisfatória)")
            else:
                print("🧠 APRENDIZADO: Nenhuma avaliação pendente (>24h)")

        except Exception as e:
            print(f"⚠️ Erro no ciclo de aprendizado: {e}")
            print("📌 Continuando com parâmetros padrão...")

    def _aplicar_parametros_otimizados(self):
        """Aplica os parâmetros otimizados pelos módulos após aprendizado"""
        try:
            parametros = self.sistema_autoavaliacao.obter_parametros_otimizados()

            # Aplicar parâmetros de correlação
            params_corr = parametros['correlacao']
            if hasattr(self.modulo_correlacao, 'atualizar_parametros'):
                self.modulo_correlacao.atualizar_parametros(params_corr)
                print(f"🔗 Correlação: Parâmetros aplicados (threshold: {params_corr['threshold_correlacao']})")

            # Aplicar parâmetros de níveis
            params_niv = parametros['niveis']
            if hasattr(self.calculador_niveis, 'atualizar_parametros'):
                self.calculador_niveis.atualizar_parametros(params_niv)
                print(f"🎯 Níveis: Parâmetros aplicados (threshold: {params_niv['threshold_suporte_resistencia']})")

        except Exception as e:
            print(f"⚠️ Erro ao aplicar parâmetros otimizados: {e}")

    # ========================================
    # GATES DE SEGURANÇA
    # ========================================

    def validar_ticket_obrigatorio(self, ticket: str) -> bool:
        """Valida obrigatoriedade e formato do ticket"""
        if not ticket or not ticket.strip():
            raise ValueError("❌ TICKET OBRIGATÓRIO - Campo não pode estar vazio")

        # Formato esperado: TICKET-XXXXXXX ou numérico
        ticket = ticket.strip()
        if not (ticket.startswith('TICKET-') or ticket.isdigit()):
            raise ValueError("❌ FORMATO INVÁLIDO - Use TICKET-XXXXXXX ou número")

        return True

    def verificar_duplicacao_ticket(self, ticket: str) -> bool:
        """Verifica se ticket já foi processado"""
        if ticket in self.tickets_processados:
            raise ValueError(f"❌ TICKET DUPLICADO - {ticket} já foi processado anteriormente")

        # Verificar também no portfolio atual
        portfolio = self.gestor_portfolio.portfolio
        for posicao in portfolio.get('positions', []):
            if posicao.get('ticket') == ticket:
                raise ValueError(f"❌ TICKET EXISTENTE - {ticket} já existe no portfolio")

        return False

    # ========================================
    # SOLICITAÇÃO DE ATUALIZAÇÃO
    # ========================================

    def solicitar_atualizacao(self) -> SolicitacaoAtualizacao:
        """Interface para solicitar atualização com validação completa"""

        print("\n🔐 SOLICITAÇÃO DE ATUALIZAÇÃO DE PORTFÓLIO")
        print("=" * 50)

        while True:
            try:
                # Solicitar dados básicos
                ticket = input("🎫 Ticket (obrigatório): ").strip()
                self.validar_ticket_obrigatorio(ticket)
                self.verificar_duplicacao_ticket(ticket)

                # Consultar histórico de aprendizado (GATE: consultar histórico)
                print("\n🧠 CONSULTANDO HISTÓRICO DE APRENDIZADO:")
                estatisticas = self.base_recomendacoes.obter_estatisticas_aprendizado()
                if estatisticas['total_avaliadas'] > 0:
                    print(f"   📊 Avaliações realizadas: {estatisticas['total_avaliadas']}")
                    print(f"   🎯 Score médio: {estatisticas['score_medio']}%")
                    print(f"   ✅ Taxa acerto: {estatisticas['taxa_acerto']}%")
                    print("   💡 Sistema otimizado baseado em aprendizado contínuo")
                else:
                    print("   📌 Sistema em modo inicial (sem histórico de aprendizado)")
                print("-" * 40)

                ativo = input("💱 Ativo (ex: EUR/USD): ").strip().upper()
                tipo_operacao = input("⚙️ Tipo (ABRIR/FECHAR/AJUSTAR): ").strip().upper()
                direcao = input("📈 Direção (LONG/SHORT): ").strip().upper()
                lots = float(input("📊 Lots: ").strip())
                preco_entrada = float(input("💰 Preço entrada: ").strip())

                # Dados opcionais
                stop_loss_input = input("🛑 Stop Loss (opcional): ").strip()
                stop_loss = float(stop_loss_input) if stop_loss_input else None

                take_profit_input = input("🎯 Take Profit (opcional, separado por vírgula): ").strip()
                take_profit = None
                if take_profit_input:
                    take_profit = []
                    for tp in take_profit_input.split(','):
                        nivel = float(tp.strip())
                        take_profit.append({"level": nivel, "percentage": 50})

                justificativa = input("📝 Justificativa: ").strip()

                # Criar solicitação
                solicitacao = SolicitacaoAtualizacao(
                    ticket=ticket,
                    ativo=ativo,
                    tipo_operacao=tipo_operacao,
                    direcao=direcao,
                    lots=lots,
                    preco_entrada=preco_entrada,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    justificativa=justificativa
                )

                print("\n✅ Solicitação criada com sucesso!")
                print(f"🎫 Ticket: {solicitacao.ticket}")
                print(f"💱 Ativo: {solicitacao.ativo}")
                print(f"⚙️ Operação: {solicitacao.tipo_operacao} {solicitacao.direcao}")

                return solicitacao

            except ValueError as e:
                print(f"❌ Erro: {e}")
                print("🔄 Tente novamente...\n")
            except KeyboardInterrupt:
                print("\n⏹️ Operação cancelada pelo usuário")
                raise SystemExit

    # ========================================
    # PROCESSAMENTO INTEGRADO
    # ========================================

    def processar_atualizacao_completa(self, solicitacao: SolicitacaoAtualizacao) -> Dict:
        """
        Processa atualização completa com todas as análises integradas
        """

        print(f"\n⚙️ PROCESSANDO ATUALIZAÇÃO: {solicitacao.ticket}")
        print("=" * 50)

        try:
            # 1. Atualizar portfolio
            print("📝 1. Atualizando portfolio...")
            self.gestor_portfolio.atualizar_posicao(solicitacao)
            self.tickets_processados.add(solicitacao.ticket)

            # 2. Recalcular níveis se necessário
            print("📊 2. Atualizando níveis de preço...")
            ticker = self._converter_ativo_para_ticker(solicitacao.ativo)
            if ticker:
                self.calculador_niveis.processar_ativo_especifico(ticker)

            # 3. Análise integrada completa
            print("🔍 3. Executando análises integradas...")
            analises_completas = self.realizar_analise_integrada()

            # 4. Gerar relatório executivo
            print("📋 4. Gerando relatório executivo...")
            relatorio = self.gerar_relatorio_executivo_inteligente()

            # 5. Persistir sugestões otimizadas na base de aprendizado (FASE 3)
            print("💾 5. Persistindo sugestões na base de aprendizado...")
            self._persistir_sugestoes_aprendizado(relatorio, solicitacao.ticket)

            resultado = {
                'status': 'SUCESSO',
                'ticket': solicitacao.ticket,
                'portfolio_atualizado': True,
                'analises_realizadas': True,
                'relatorio_gerado': True,
                'sugestoes_persistidas': True,
                'relatorio_executivo': relatorio,
                'timestamp_processamento': datetime.now(timezone.utc).isoformat()
            }

            print("✅ Atualização processada com sucesso!")
            print("🧠 Sugestões armazenadas para aprendizado contínuo")
            return resultado

        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            return {
                'status': 'ERRO',
                'erro': str(e),
                'ticket': solicitacao.ticket,
                'timestamp_erro': datetime.now(timezone.utc).isoformat()
            }

    def _persistir_sugestoes_aprendizado(self, relatorio: RelatorioExecutivoInteligente, ticket_id: str):
        """Persiste as sugestões otimizadas na base de aprendizado 24h"""
        try:
            # Extrair sugestões de balanceamento/proteção
            sugestoes_balanceamento = relatorio.sugestoes_balanceamento_protecao
            if sugestoes_balanceamento and 'impacto_cascata' in sugestoes_balanceamento:
                impacto_cascata = sugestoes_balanceamento['impacto_cascata']
                if impacto_cascata.get('recomendacoes_protecao'):
                    for moeda, recomendacao in impacto_cascata['recomendacoes_protecao'].items():
                        rec = RecomendacaoAprendizado(
                            ticket_id=f"{ticket_id}_HEDGE_{moeda}",
                            tipo_recomendacao='HEDGE',
                            ativo=moeda,
                            recomendacao=recomendacao,
                            data_criacao=datetime.now(timezone.utc),
                            parametros_modelo=self.sistema_autoavaliacao.parametros_correlacao.copy()
                        )
                        self.base_recomendacoes.adicionar_recomendacao(rec)

            # Extrair sugestões de take/reforço
            sugestoes_niveis = relatorio.sugestoes_niveis_take_reforco
            if isinstance(sugestoes_niveis, dict):
                for tipo_sugestao, dados in sugestoes_niveis.items():
                    if isinstance(dados, dict) and 'recomendacoes' in dados:
                        for recomendacao in dados['recomendacoes']:
                            tipo_rec = 'TAKE' if 'take' in tipo_sugestao.lower() else 'REFORCO'
                            rec = RecomendacaoAprendizado(
                                ticket_id=f"{ticket_id}_{tipo_rec}_{recomendacao.get('ativo', 'UNKNOWN')}",
                                tipo_recomendacao=tipo_rec,
                                ativo=recomendacao.get('ativo', 'UNKNOWN'),
                                recomendacao=recomendacao,
                                data_criacao=datetime.now(timezone.utc),
                                parametros_modelo=self.sistema_autoavaliacao.parametros_niveis.copy()
                            )
                            self.base_recomendacoes.adicionar_recomendacao(rec)

            print(f"💾 {len(self.base_recomendacoes.recomendacoes)} sugestões persistidas para avaliação 24h")

        except Exception as e:
            print(f"⚠️ Erro ao persistir sugestões: {e}")

    def _converter_ativo_para_ticker(self, ativo: str) -> Optional[str]:
        """Converte ativo para ticker Yahoo Finance"""
        conversoes = {
            'GBP/JPY': 'GBPJPY=X',
            'EUR/USD': 'EURUSD=X',
            'CHF/JPY': 'CHFJPY=X',
            'GBP/USD': 'GBPUSD=X',
            'USD/JPY': 'USDJPY=X',
            'USD/CAD': 'USDCAD=X',
            'USD/CHF': 'USDCHF=X',
            'AUD/USD': 'AUDUSD=X',
            'AUD/CHF': 'AUDCHF=X',
            'AUD/JPY': 'AUDJPY=X',
            'XAU/USD': 'GC=F'
        }
        return conversoes.get(ativo)

    # ========================================
    # ANÁLISE INTEGRADA AVANÇADA
    # ========================================

    def realizar_analise_integrada(self) -> Dict:
        """
        Realiza análise integrada completa com todos os módulos
        """

        analises = {}

        try:
            # 1. Análise de risco sistêmico com correlação
            analises['risco_sistemico'] = self.analisar_risco_sistemico_balanceamento()

            # 2. Simulação de impacto cascata
            analises['impacto_cascata'] = self.simular_protecao_impacto_cascata()

            # 3. Recomendações de diversificação por clusters
            analises['diversificacao_clusters'] = self.recomendar_diversificacao_clusters()

            # 4. Sugestões baseadas em níveis
            analises['sugestoes_niveis'] = self.gerar_sugestoes_niveis_inteligentes()

            # 5. Validação macroeconômica
            analises['validacao_macroeconomica'] = self.validar_cenario_macroeconomico()

            print("✅ Análises integradas concluídas")

        except Exception as e:
            print(f"⚠️ Erro em análise integrada: {e}")
            analises['erro'] = str(e)

        return analises

    # ========================================
    # ANÁLISES ESPECÍFICAS COM CORRELAÇÃO
    # ========================================

    def analisar_risco_sistemico_balanceamento(self) -> Dict:
        """
        Usa modulo_correlacao_avancada para identificar necessidades de balanceamento
        """

        try:
            # Carregar dados no módulo de correlação
            self.modulo_correlacao.carregar_portfolio()
            self.modulo_correlacao.carregar_precos_historicos()
            self.modulo_correlacao.calcular_matriz_correlacao_real()
            self.modulo_correlacao.construir_rede_correlacao()

            # Calcular risco sistêmico
            risco_sistemico = self.modulo_correlacao.calcular_risco_sistemico()

            # Identificar concentrações excessivas
            concentracao_excessiva = {}
            for moeda, risco in risco_sistemico.items():
                if risco > 0.15:  # Threshold alto
                    concentracao_excessiva[moeda] = {
                        'risco_sistemico': risco,
                        'recomendacao': 'REDUZIR_EXPOSICAO',
                        'justificativa': f'Alto risco sistêmico ({risco:.1%}) - diversificar'
                    }

            # Identificar clusters
            clusters = self.modulo_correlacao.identificar_clusters_correlacao()

            protecao_clusters = {}
            for cluster in clusters:
                if cluster.correlacao_media > 0.7:
                    protecao_clusters[cluster.id_cluster] = {
                        'moedas_afetadas': list(cluster.moedas),
                        'correlacao_media': cluster.correlacao_media,
                        'recomendacao': 'HEDGE_CORRELACIONADO',
                        'justificativa': f'Cluster altamente correlacionado ({cluster.correlacao_media:.1%})'
                    }

            return {
                'concentracao_excessiva': concentracao_excessiva,
                'protecao_clusters': protecao_clusters,
                'clusters_identificados': len(clusters),
                'timestamp_analise': datetime.now().isoformat()
            }

        except Exception as e:
            return {'erro': f'Erro na análise de risco sistêmico: {str(e)}'}

    def simular_protecao_impacto_cascata(self, moeda_alvo: str = "EUR") -> Dict:
        """
        Simula impacto cascata para recomendar proteções preventivas
        """

        try:
            # Simular choque de 5%
            impacto_cascata = self.modulo_correlacao.analisar_impacto_cascata(
                moeda_afetada=moeda_alvo,
                choque_inicial=0.05
            )

            # Identificar moedas mais afetadas
            moedas_afetadas = sorted(
                [(moeda, impacto) for moeda, impacto in impacto_cascata.items() if impacto > 0.01],
                key=lambda x: x[1],
                reverse=True
            )[:5]

            # Recomendações de proteção
            recomendacoes_protecao = {}
            for moeda, impacto in moedas_afetadas:
                if impacto > 0.03:
                    recomendacoes_protecao[moeda] = {
                        'impacto_cascata': impacto,
                        'protecao_recomendada': self._determinar_tipo_protecao(moeda, impacto),
                        'urgencia': 'ALTA' if impacto > 0.04 else 'MEDIA',
                        'justificativa': f'Impacto cascata de {impacto:.1%} de {moeda_alvo}'
                    }

            return {
                'moeda_alvo': moeda_alvo,
                'choque_simulado': 0.05,
                'moedas_afetadas': moedas_afetadas,
                'recomendacoes_protecao': recomendacoes_protecao,
                'timestamp_simulacao': datetime.now().isoformat()
            }

        except Exception as e:
            return {'erro': f'Erro na simulação de impacto cascata: {str(e)}'}

    def recomendar_diversificacao_clusters(self) -> List[Dict]:
        """
        Recomendações de diversificação baseadas em clusters de correlação
        """

        try:
            clusters = self.modulo_correlacao.identificar_clusters_correlacao()
            recomendacoes = []

            for cluster in clusters:
                exposicao_cluster = self._calcular_exposicao_cluster(cluster)

                if exposicao_cluster['percentual_total'] > 0.25:  # >25% do portfolio
                    recomendacao = {
                        'tipo': 'DIVERSIFICACAO_CLUSTER',
                        'cluster_id': cluster.id_cluster,
                        'moedas_afetadas': list(cluster.moedas),
                        'exposicao_atual': exposicao_cluster['percentual_total'],
                        'correlacao_media': cluster.correlacao_media,
                        'acao_recomendada': 'REDUZIR_EXPOSICAO_20_30_PCT',
                        'ativos_alternativos': self._sugerir_moedas_diversificacao(cluster),
                        'justificativa': f'Cluster representa {exposicao_cluster["percentual_total"]:.1%} do portfolio',
                        'prioridade': 'ALTA'
                    }
                    recomendacoes.append(recomendacao)

            return recomendacoes

        except Exception as e:
            return [{'erro': f'Erro nas recomendações de diversificação: {str(e)}'}]

    # ========================================
    # ANÁLISES COM NÍVEIS DE PREÇO
    # ========================================

    def gerar_sugestoes_niveis_inteligentes(self) -> Dict:
        """
        Gera sugestões inteligentes baseadas em níveis de preço
        """

        sugestoes = {}

        try:
            portfolio = self.gestor_portfolio.portfolio

            for posicao in portfolio.get('positions', []):
                if posicao['status'] == 'OPEN':
                    posicao_id = posicao['position_id']
                    sugestoes[posicao_id] = self.recomendar_take_reforco_niveis(posicao)

            return sugestoes

        except Exception as e:
            return {'erro': f'Erro nas sugestões de níveis: {str(e)}'}

    def recomendar_take_reforco_niveis(self, posicao: Dict) -> Dict:
        """
        Recomendações de take profit ou reforço baseadas em níveis críticos
        """

        try:
            par = posicao['currency_pair']
            preco_atual = posicao['current_price']
            direcao = posicao['direction']

            # Obter níveis do ativo
            ticker = self._converter_ativo_para_ticker(par)
            if not ticker:
                return {'erro': f'Ticker não encontrado para {par}'}

            niveis = self.motor_niveis.obter_niveis_ativo(ticker)

            recomendacoes = {
                'take_profit': [],
                'reforco': [],
                'risco': []
            }

            if direcao == 'LONG':
                # Take profit em resistências próximas
                resistencias = niveis.get('resistencias_chave', [])
                for resistencia in resistencias[:3]:
                    distancia = ((resistencia / preco_atual) - 1) * 100
                    if 0.5 <= distancia <= 5.0:
                        recomendacoes['take_profit'].append({
                            'nivel': resistencia,
                            'distancia_percentual': distancia,
                            'pontuacao': self._calcular_pontuacao_take(resistencia, distancia)
                        })

                # Reforço em suportes próximos
                suportes = niveis.get('suportes_chave', [])
                for suporte in suportes[:2]:
                    distancia = ((preco_atual / suporte) - 1) * 100
                    if distancia <= 0.3:
                        recomendacoes['reforco'].append({
                            'nivel': suporte,
                            'distancia_percentual': distancia,
                            'justificativa': 'Suporte crítico próximo - oportunidade de reforço'
                        })

            elif direcao == 'SHORT':
                # Take profit em suportes próximos
                suportes = niveis.get('suportes_chave', [])
                for suporte in suportes[:3]:
                    distancia = ((preco_atual / suporte) - 1) * 100
                    if 0.5 <= distancia <= 5.0:
                        recomendacoes['take_profit'].append({
                            'nivel': suporte,
                            'distancia_percentual': distancia,
                            'pontuacao': self._calcular_pontuacao_take(suporte, distancia)
                        })

                # Reforço em resistências próximas
                resistencias = niveis.get('resistencias_chave', [])
                for resistencia in resistencias[:2]:
                    distancia = ((resistencia / preco_atual) - 1) * 100
                    if distancia <= 0.3:
                        recomendacoes['reforco'].append({
                            'nivel': resistencia,
                            'distancia_percentual': distancia,
                            'justificativa': 'Resistência crítica próxima - oportunidade de reforço'
                        })

            return recomendacoes

        except Exception as e:
            return {'erro': f'Erro nas recomendações de níveis: {str(e)}'}

    # ========================================
    # VALIDAÇÃO MACROECONÔMICA
    # ========================================

    def validar_cenario_macroeconomico(self) -> Dict:
        """
        Valida se o portfolio está coerente com cenário macro atual
        """

        try:
            # Coletar dados macro
            dados_dxy = self.analisador_macro.coletar_dados_dxy()
            eventos_criticos = self.analisador_macro.identificar_eventos_criticos()

            # Análise de exposição
            exposicao_moeda = self.analisador_risco.calcular_exposicao_cambial()

            # Validar coerência
            validacao = {
                'regime_dolar': dados_dxy.get('regime', 'DESCONHECIDO'),
                'eventos_criticos': eventos_criticos,
                'exposicao_risco': {},
                'recomendacoes_macro': []
            }

            # Análise por moeda
            for moeda, exposicao in exposicao_moeda.items():
                risco_macro = self._avaliar_risco_macro_moeda(moeda, dados_dxy, eventos_criticos)
                validacao['exposicao_risco'][moeda] = {
                    'exposicao_total': exposicao,
                    'risco_macro': risco_macro,
                    'coerente': risco_macro['nivel'] <= 3
                }

            # Recomendações baseadas em cenário
            validacao['recomendacoes_macro'] = self._gerar_recomendacoes_macro(validacao)

            return validacao

        except Exception as e:
            return {'erro': f'Erro na validação macroeconômica: {str(e)}'}

    def _gerar_resumo_portfolio(self) -> Dict:
        """Gera resumo executivo do portfólio atual"""
        try:
            # Carregar dados do portfólio
            portfolio_data = self.gestor_portfolio.carreguar_portfolio()

            if not portfolio_data or 'positions' not in portfolio_data:
                return {
                    'erro': 'Dados do portfólio não disponíveis',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

            posicoes = portfolio_data['positions']
            posicoes_open = [p for p in posicoes if p.get('status') == 'OPEN']

            # Cálculos básicos
            total_posicoes = len(posicoes)
            posicoes_abertas = len(posicoes_open)
            pnl_total = sum(p.get('pnl_unrealized', 0) for p in posicoes_open)

            # Exposição por moeda
            exposicao_moeda = {}
            for posicao in posicoes_open:
                moeda = posicao.get('currency_pair', '').split('/')[0] if '/' in posicao.get('currency_pair', '') else 'N/A'
                valor_posicao = abs(posicao.get('position_value', 0))
                exposicao_moeda[moeda] = exposicao_moeda.get(moeda, 0) + valor_posicao

            # Calcular percentuais
            total_exposicao = sum(exposicao_moeda.values())
            exposicao_percentual = {}
            for moeda, valor in exposicao_moeda.items():
                if total_exposicao > 0:
                    exposicao_percentual[moeda] = (valor / total_exposicao) * 100

            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_posicoes': total_posicoes,
                'posicoes_abertas': posicoes_abertas,
                'pnl_total_nao_realizado': pnl_total,
                'exposicao_por_moeda': exposicao_moeda,
                'exposicao_percentual': exposicao_percentual,
                'numero_moedas': len(exposicao_moeda),
                'status_portfolio': 'ATIVO' if posicoes_abertas > 0 else 'INATINO'
            }

        except Exception as e:
            return {
                'erro': f'Erro ao gerar resumo do portfólio: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def gerar_relatorio_executivo_inteligente(self) -> RelatorioExecutivoInteligente:
        """
        Gera relatório executivo completo com todas as análises
        """

        try:
            # Resumo do portfolio
            portfolio_resumo = self._gerar_resumo_portfolio()

            # Análise de risco
            analise_risco = self.analisador_risco.calcular_metricas_risco()

            # Validação macro
            validacao_macro = self.validar_cenario_macroeconomico()

            # Análise de correlação sistêmica
            analise_correlacao = self.analisar_risco_sistemico_balanceamento()

            # Sugestões de balanceamento/proteção
            sugestoes_balanceamento = {
                'impacto_cascata': self.simular_protecao_impacto_cascata(),
                'diversificacao_clusters': self.recomendar_diversificacao_clusters()
            }

            # Sugestões de níveis
            sugestoes_niveis = self.gerar_sugestoes_niveis_inteligentes()

            # Recomendações finais integradas
            recomendacoes_finais = self._integrar_recomendacoes_finais(
                analise_risco, validacao_macro, analise_correlacao,
                sugestoes_balanceamento, sugestoes_niveis
            )

            relatorio = RelatorioExecutivoInteligente(
                timestamp=datetime.now(timezone.utc),
                portfolio_resumo=portfolio_resumo,
                analise_risco=analise_risco,
                validacao_macroeconomica=validacao_macro,
                analise_correlacao_sistemica=analise_correlacao,
                sugestoes_balanceamento_protecao=sugestoes_balanceamento,
                sugestoes_niveis_take_reforco=sugestoes_niveis,
                recomendacoes_finais_integradas=recomendacoes_finais
            )

            # Salvar relatório
            self._salvar_relatorio(relatorio)

            return relatorio

        except Exception as e:
            print(f"❌ Erro na geração do relatório: {e}")
            raise

    def _integrar_recomendacoes_finais(self, analise_risco: Dict, validacao_macro: Dict,
                                      analise_correlacao: Dict, sugestoes_balanceamento: Dict,
                                      sugestoes_niveis: Dict) -> List[Dict]:
        """Integra todas as recomendações em uma lista consolidada"""
        try:
            recomendacoes = []

            # Recomendações de risco
            if analise_risco and 'recomendacoes' in analise_risco:
                for rec in analise_risco['recomendacoes']:
                    recomendacoes.append({
                        'tipo': 'RISCO',
                        'prioridade': rec.get('prioridade', 'MEDIA'),
                        'recomendacao': rec.get('recomendacao', ''),
                        'justificativa': rec.get('justificativa', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            # Recomendações macroeconômicas
            if validacao_macro and 'recomendacoes' in validacao_macro:
                for rec in validacao_macro['recomendacoes']:
                    recomendacoes.append({
                        'tipo': 'MACROECONOMICO',
                        'prioridade': rec.get('prioridade', 'MEDIA'),
                        'recomendacao': rec.get('recomendacao', ''),
                        'justificativa': rec.get('justificativa', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            # Recomendações de correlação
            if analise_correlacao and 'recomendacoes' in analise_correlacao:
                for rec in analise_correlacao['recomendacoes']:
                    recomendacoes.append({
                        'tipo': 'CORRELACAO',
                        'prioridade': rec.get('prioridade', 'MEDIA'),
                        'recomendacao': rec.get('recomendacao', ''),
                        'justificativa': rec.get('justificativa', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            # Recomendações de balanceamento
            if sugestoes_balanceamento:
                for chave, valor in sugestoes_balanceamento.items():
                    if isinstance(valor, list):
                        for rec in valor:
                            recomendacoes.append({
                                'tipo': 'BALANCEAMENTO',
                                'prioridade': rec.get('prioridade', 'MEDIA'),
                                'recomendacao': rec.get('recomendacao', ''),
                                'justificativa': rec.get('justificativa', ''),
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            })

            # Recomendações de níveis
            if sugestoes_niveis and 'recomendacoes' in sugestoes_niveis:
                for rec in sugestoes_niveis['recomendacoes']:
                    recomendacoes.append({
                        'tipo': 'NIVEIS',
                        'prioridade': rec.get('prioridade', 'MEDIA'),
                        'recomendacao': rec.get('recomendacao', ''),
                        'justificativa': rec.get('justificativa', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            # Se não há recomendações específicas, adicionar recomendação padrão
            if not recomendacoes:
                recomendacoes.append({
                    'tipo': 'GERAL',
                    'prioridade': 'BAIXA',
                    'recomendacao': 'Manter monitoramento ativo do portfólio',
                    'justificativa': 'Nenhuma recomendação específica identificada no momento',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })

            return recomendacoes

        except Exception as e:
            return [{
                'tipo': 'ERRO',
                'prioridade': 'ALTA',
                'recomendacao': 'Revisar sistema de integração de recomendações',
                'justificativa': f'Erro na integração: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }]

    def gerar_relatorio_executivo(self) -> str:
        """
        Gera relatório executivo completo com iteração sobre posições OPEN
        """
        try:
            # Obter relatório inteligente
            relatorio_obj = self.gerar_relatorio_executivo_inteligente()

            # Converter para markdown
            markdown = "# 📊 RELATÓRIO EXECUTIVO - GESTÃO DE RISCO E PORTFÓLIO (RMS)\n\n"
            markdown += f"**Data/Hora:** {relatorio_obj.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"

            # 1. ITERAÇÃO E RELATÓRIO INDIVIDUAL DOS ATIVOS (Asset Deep Dive)
            markdown += "## � ANÁLISE INDIVIDUAL DOS ATIVOS (POSIÇÕES OPEN)\n\n"

            portfolio_data = self.gestor_portfolio.portfolio
            positions = portfolio_data.get('positions', [])
            posicoes_open = [p for p in positions if p.get('status') == 'OPEN']

            if posicoes_open:
                for posicao in posicoes_open:
                    markdown += self._gerar_analise_individual_ativo(posicao)
                    markdown += "\n---\n\n"

                # Consolidado das posições
                markdown += self._gerar_consolidado_posicoes(posicoes_open)
            else:
                markdown += "*Nenhuma posição aberta encontrada.*\n\n"

            # 2. RISCO DO PORTFÓLIO (CONSOLIDADO)
            markdown += "## ⚠️ RISCO DO PORTFÓLIO (CONSOLIDADO)\n\n"
            markdown += self._gerar_analise_risco_consolidado(portfolio_data)

            # 3. COERÊNCIA MACROECONÔMICA
            markdown += "## 🌍 COERÊNCIA MACROECONÔMICA\n\n"
            markdown += self._gerar_analise_coerencia_macroeconomica(portfolio_data)

            # 4. SUGESTÕES OTIMIZADAS (AÇÃO ACIONÁVEL)
            markdown += "## 💡 SUGESTÕES OTIMIZADAS (AÇÃO ACIONÁVEL)\n\n"

            # Balanceamento/Proteção com prioridade JPY
            markdown += "### 🛡️ BALANCEAMENTO E PROTEÇÃO\n\n"
            markdown += self._gerar_sugestoes_balanceamento_prioridade_jpy(relatorio_obj, portfolio_data)

            # Take/Reforço
            markdown += "### 🎯 TAKE E REFORÇO\n\n"
            niveis = relatorio_obj.sugestoes_niveis_take_reforco
            if isinstance(niveis, dict):
                for chave, valor in niveis.items():
                    markdown += f"#### {chave.replace('_', ' ').title()}\n"
                    if isinstance(valor, dict):
                        for sub_chave, sub_valor in valor.items():
                            markdown += f"- **{sub_chave.replace('_', ' ').title()}:** {sub_valor}\n"
                    else:
                        markdown += f"{valor}\n"
                    markdown += "\n"
            else:
                markdown += f"```\n{niveis}\n```\n\n"

            markdown += "---\n"
            markdown += "*Relatório gerado automaticamente pelo Agente Adaptativo de Gestão de Risco e Portfólio (RMS)*"

            return markdown

        except Exception as e:
            return f"# ❌ ERRO NA GERAÇÃO DO RELATÓRIO\n\nErro: {str(e)}"

    def _gerar_analise_individual_ativo(self, posicao: Dict) -> str:
        """Gera mini-análise individual para um ativo (Asset Deep Dive)"""
        ativo = posicao.get('currency_pair', 'N/A')
        direcao = posicao.get('direction', 'N/A')
        pnl_nao_realizado = posicao.get('pnl_unrealized', 0)
        estrategia = posicao.get('strategy', 'N/A')
        ticket = posicao.get('ticket', 'N/A')

        # Avaliação de risco individual
        risco_individual = self._calcular_risco_individual(posicao)

        analise = f"### {ativo} ({direcao}) - Ticket: {ticket}\n\n"
        analise += f"**📈 P&L Não Realizado:** R$ {pnl_nao_realizado:,.2f}\n\n"
        analise += f"**🎯 Estratégia:** {estrategia}\n\n"
        analise += f"**⚠️ Avaliação de Risco Individual:**\n{risco_individual}\n\n"

        return analise

    def _calcular_risco_individual(self, posicao: Dict) -> str:
        """Calcula avaliação de risco individual para uma posição"""
        try:
            preco_atual = posicao.get('current_price', 0)
            stop_loss = posicao.get('stop_loss')
            take_profit = posicao.get('take_profit', [])

            risco = ""

            if stop_loss:
                if posicao['direction'] == 'LONG':
                    distancia_sl = ((preco_atual - stop_loss) / preco_atual) * 100
                    risco += f"- **Distância para Stop-Loss:** {distancia_sl:.2f}%\n"
                else:  # SHORT
                    distancia_sl = ((stop_loss - preco_atual) / preco_atual) * 100
                    risco += f"- **Distância para Stop-Loss:** {distancia_sl:.2f}%\n"

            if take_profit:
                if isinstance(take_profit, list) and take_profit:
                    tp_nivel = take_profit[0].get('level', 0) if isinstance(take_profit[0], dict) else take_profit[0]
                    if posicao['direction'] == 'LONG':
                        distancia_tp = ((tp_nivel - preco_atual) / preco_atual) * 100
                        risco += f"- **Distância para Take-Profit:** {distancia_tp:.2f}%\n"
                    else:  # SHORT
                        distancia_tp = ((preco_atual - tp_nivel) / preco_atual) * 100
                        risco += f"- **Distância para Take-Profit:** {distancia_tp:.2f}%\n"

            # Avaliação qualitativa
            pnl = posicao.get('pnl_unrealized', 0)
            if pnl > 0:
                risco += "- **Status:** Positivo - Monitorar para take-profit\n"
            elif pnl < -1000:  # Perda significativa
                risco += "- **Status:** Atenção - Avaliar stop-loss ou ajuste\n"
            else:
                risco += "- **Status:** Neutro - Manter monitoramento\n"

            return risco

        except Exception as e:
            return f"- **Erro na avaliação:** {str(e)}\n"

    def _gerar_consolidado_posicoes(self, posicoes_open: List[Dict]) -> str:
        """Gera consolidado das posições para o relatório de performance e alocação"""
        if not posicoes_open:
            return ""

        # Cálculos consolidados
        total_pnl = sum(p.get('pnl_unrealized', 0) for p in posicoes_open)
        pnl_positivo = sum(p.get('pnl_unrealized', 0) for p in posicoes_open if p.get('pnl_unrealizado', 0) > 0)
        pnl_negativo = sum(p.get('pnl_unrealizado', 0) for p in posicoes_open if p.get('pnl_unrealizado', 0) < 0)

        # Contagem por direção
        long_positions = len([p for p in posicoes_open if p.get('direction') == 'LONG'])
        short_positions = len([p for p in posicoes_open if p.get('direction') == 'SHORT'])

        # Top performers
        top_performers = sorted(posicoes_open, key=lambda x: x.get('pnl_unrealizado', 0), reverse=True)[:3]

        consolidado = "### 📊 CONSOLIDADO DAS POSIÇÕES\n\n"
        consolidado += f"**Total de Posições Abertas:** {len(posicoes_open)}\n\n"
        consolidado += f"**P&L Total Não Realizado:** R$ {total_pnl:,.2f}\n"
        consolidado += f"- **Positivo:** R$ {pnl_positivo:,.2f}\n"
        consolidado += f"- **Negativo:** R$ {pnl_negativo:,.2f}\n\n"

        consolidado += f"**Distribuição por Direção:**\n"
        consolidado += f"- **LONG:** {long_positions} posições\n"
        consolidado += f"- **SHORT:** {short_positions} posições\n\n"

        consolidado += "**🏆 Top 3 Performers:**\n"
        for i, pos in enumerate(top_performers, 1):
            ativo = pos.get('currency_pair', 'N/A')
            pnl = pos.get('pnl_unrealized', 0)
            consolidado += f"{i}. {ativo}: R$ {pnl:,.2f}\n"
        consolidado += "\n"

        return consolidado

    def _gerar_analise_risco_consolidado(self, portfolio_data: Dict) -> str:
        """Gera análise de risco consolidado focada em exposição e correlação"""
        try:
            allocation = portfolio_data.get('allocation', {})
            correlation_matrix = allocation.get('correlation_matrix', {})

            # Exposição de moedas (Net Exposure)
            exposicao_moedas = allocation.get('by_currency', {})
            exposicao_texto = "### 💱 EXPOSIÇÃO DE MOEDAS (NET EXPOSURE)\n\n"
            for moeda, exposicao in exposicao_moedas.items():
                status = "🔴 ALTA" if abs(exposicao) > 50 else "🟡 MODERADA" if abs(exposicao) > 20 else "🟢 BAIXA"
                exposicao_texto += f"- **{moeda}:** {exposicao}% ({status})\n"
            exposicao_texto += "\n"

            # Drawdown implícito (baseado em posições atuais)
            positions = portfolio_data.get('positions', [])
            posicoes_open = [p for p in positions if p.get('status') == 'OPEN']

            if posicoes_open:
                # Calcular drawdown potencial baseado em stop-loss
                drawdown_potencial = 0
                for pos in posicoes_open:
                    stop_loss = pos.get('stop_loss')
                    if stop_loss:
                        preco_atual = pos.get('current_price', 0)
                        lots = pos.get('lots', 0)
                        lot_size = pos.get('lot_size', 100000)

                        if pos['direction'] == 'LONG':
                            perda_potencial = (preco_atual - stop_loss) * lots * lot_size
                        else:  # SHORT
                            perda_potencial = (stop_loss - preco_atual) * lots * lot_size

                        drawdown_potencial += max(0, -perda_potencial)  # Só perdas

                capital_total = portfolio_data.get('portfolio_metadata', {}).get('total_capital', 100000)
                drawdown_percentual = (drawdown_potencial / capital_total) * 100
            else:
                drawdown_percentual = 0

            drawdown_texto = f"### 📉 DRAWDOWN IMPLÍCITO\n\n"
            drawdown_texto += f"- **Drawdown Potencial:** R$ {drawdown_potencial:,.2f}\n"
            drawdown_texto += f"- **Percentual do Capital:** {drawdown_percentual:.2f}%\n"
            status_dd = "🔴 CRÍTICO" if drawdown_percentual > 5 else "🟡 ATENÇÃO" if drawdown_percentual > 2 else "🟢 CONTROLADO"
            drawdown_texto += f"- **Status:** {status_dd}\n\n"

            # Impacto da correlação na volatilidade
            correlacao_texto = "### 🔗 IMPACTO DA CORRELAÇÃO NA VOLATILIDADE\n\n"
            if correlation_matrix:
                correlacao_texto += "**Matriz de Correlação Crítica:**\n"
                for par, correlacao in correlation_matrix.items():
                    intensidade = "🔴 FORTE" if abs(correlacao) > 0.7 else "🟡 MODERADA" if abs(correlacao) > 0.4 else "🟢 FRACA"
                    correlacao_texto += f"- **{par}:** {correlacao:.2f} ({intensidade})\n"
                correlacao_texto += "\n"

                # Análise de risco sistêmico
                correlacoes_fortes = [c for c in correlation_matrix.values() if abs(c) > 0.7]
                if correlacoes_fortes:
                    correlacao_texto += "**⚠️ Risco Sistêmico:** Correlações fortes detectadas. "
                    correlacao_texto += "Movimentos em um ativo podem impactar outros significativamente.\n\n"
                else:
                    correlacao_texto += "**✅ Risco Sistêmico:** Diversificação adequada mantida.\n\n"
            else:
                correlacao_texto += "*Dados de correlação não disponíveis.*\n\n"

            return exposicao_texto + drawdown_texto + correlacao_texto

        except Exception as e:
            return f"Erro na análise de risco consolidado: {str(e)}\n\n"

    def _gerar_analise_coerencia_macroeconomica(self, portfolio_data: Dict) -> str:
        """Gera análise de coerência macroeconômica focada em estratégias ativas"""
        try:
            allocation = portfolio_data.get('allocation', {})
            estrategias = allocation.get('by_strategy', {})
            exposicao_moedas = allocation.get('by_currency', {})

            # Análise de estratégias ativas
            analise = "### 🎯 ANÁLISE DE ESTRATÉGIAS ATIVAS\n\n"

            if estrategias:
                for estrategia, percentual in estrategias.items():
                    analise += f"**{estrategia.replace('_', ' ').title()}:** {percentual}%\n"

                    # Avaliação específica por estratégia
                    if 'carry' in estrategia.lower():
                        analise += "- **Carry Trade:** Alinhado com cenário de dólar moderado. "
                        analise += "Diferenças de taxa favorecem posições LONG em moedas de alta taxa.\n\n"
                    elif 'rate_differential' in estrategia.lower():
                        analise += "- **Diferenical de Taxa:** Estratégia defensiva adequada para "
                        analise += "períodos de incerteza no mercado de juros.\n\n"
                    elif 'hedge' in estrategia.lower():
                        analise += "- **Hedge/Proteção:** Estratégia prudente para proteção contra "
                        analise += "volatilidade e riscos sistêmicos.\n\n"
                    else:
                        analise += "- **Análise:** Estratégia genérica - monitorar performance.\n\n"
            else:
                analise += "*Dados de estratégias não disponíveis.*\n\n"

            # Análise de exposição por moeda
            analise += "### 💱 AVALIAÇÃO DE EXPOSIÇÃO POR MOEDA\n\n"

            # Cenário macro atual (simulado)
            cenario_dolar = "DOLAR_MODERADO"  # Deveria vir do analisador macro

            for moeda, exposicao in exposicao_moedas.items():
                analise += f"**{moeda} (Exposição: {exposicao}%):**\n"

                if moeda == 'USD_exposure':
                    if cenario_dolar == 'DOLAR_MODERADO':
                        analise += "- **Avaliação:** Exposição adequada ao cenário de dólar moderado. "
                        analise += "Posições defensivas recomendadas.\n"
                    else:
                        analise += "- **Avaliação:** Monitorar intensamente mudanças no Fed.\n"

                elif moeda == 'JPY_exposure':
                    if exposicao < -50:  # Exposição negativa alta
                        analise += "- **⚠️ ALERTA:** Exposição negativa elevada ao JPY. "
                        analise += "Risco de carry trade unwind. Considerar hedge.\n"
                    elif exposicao < 0:
                        analise += "- **Atenção:** Exposição negativa ao JPY. "
                        analise += "Vigilância necessária com política do BoJ.\n"
                    else:
                        analise += "- **Positivo:** Exposição positiva ao JPY. "
                        analise += "Benefício potencial de safe-haven.\n"

                elif moeda == 'EUR_exposure':
                    analise += "- **Avaliação:** Monitorar dados econômicos da Zona Euro. "
                    analise += "Sensibilidade a decisões do BCE.\n"

                elif moeda == 'GBP_exposure':
                    analise += "- **Avaliação:** Atenção aos dados de emprego e inflação do Reino Unido. "
                    analise += "Volatilidade potencial com Brexit.\n"

                elif moeda == 'GOLD_exposure':
                    analise += "- **Avaliação:** Posição defensiva adequada. "
                    analise += "Proteção contra inflação e instabilidade.\n"

                analise += "\n"

            # Conclusão de coerência
            analise += "### ✅ CONCLUSÃO DE COERÊNCIA\n\n"

            # Verificar exposição negativa ao JPY
            jpy_exposure = exposicao_moedas.get('JPY_exposure', 0)
            if jpy_exposure < -50:
                analise += "**⚠️ INCOERENTE:** Exposição negativa muito alta ao JPY "
                analise += "não está alinhada com cenário macro atual. "
                analise += "Recomenda-se redução ou hedge imediato.\n\n"
            else:
                analise += "**✅ COERENTE:** Estratégias ativas estão alinhadas "
                analise += "com o cenário macroeconômico atual. "
                analise += "Manter monitoramento contínuo.\n\n"

            return analise

        except Exception as e:
            return f"Erro na análise de coerência macroeconômica: {str(e)}\n\n"

    def _gerar_sugestoes_balanceamento_prioridade_jpy(self, relatorio_obj: RelatorioExecutivoInteligente, portfolio_data: Dict) -> str:
        """Gera sugestões de balanceamento com prioridade para proteção JPY"""
        try:
            portfolio_data_local = self.gestor_portfolio.portfolio
            exposicao_moedas = portfolio_data_local.get('allocation', {}).get('by_currency', {})
            jpy_exposure = exposicao_moedas.get('JPY_exposure', 0)

            sugestoes = ""

            # Prioridade 1: Proteção JPY se exposição negativa alta
            if jpy_exposure < -50:
                sugestoes += "**🔴 PRIORIDADE CRÍTICA - PROTEÇÃO JPY**\n\n"
                sugestoes += f"- **Exposição Atual JPY:** {jpy_exposure}% (ALTAMENTE NEGATIVA)\n"
                sugestoes += "- **Risco:** Carry trade unwind pode causar perdas significativas\n"
                sugestoes += "- **Ação Recomendada:**\n"
                sugestoes += "  - Fechar posições SHORT JPY (GBP/JPY, CHF/JPY, etc.)\n"
                sugestoes += "  - Implementar hedge JPY via opções ou posições LONG\n"
                sugestoes += "  - Reduzir exposição total em pares com JPY\n"
                sugestoes += "  - Considerar posições safe-haven (GOLD, USD)\n\n"

            elif jpy_exposure < 0:
                sugestoes += "**🟡 ATENÇÃO - MONITORAMENTO JPY**\n\n"
                sugestoes += f"- **Exposição Atual JPY:** {jpy_exposure}% (NEGATIVA)\n"
                sugestoes += "- **Risco:** Moderado - monitorar política do BoJ\n"
                sugestoes += "- **Ação Recomendada:**\n"
                sugestoes += "  - Manter vigilância nas posições JPY\n"
                sugestoes += "  - Preparar plano de hedge se exposição aumentar\n\n"

            # Sugestões gerais de balanceamento
            balanceamento = relatorio_obj.sugestoes_balanceamento_protecao
            if isinstance(balanceamento, dict):
                sugestoes += "**⚖️ BALANCEAMENTO GERAL**\n\n"
                for chave, valor in balanceamento.items():
                    sugestoes += f"#### {chave.replace('_', ' ').title()}\n"
                    if isinstance(valor, dict):
                        for sub_chave, sub_valor in valor.items():
                            sugestoes += f"- **{sub_chave.replace('_', ' ').title()}:** {sub_valor}\n"
                    else:
                        sugestoes += f"{valor}\n"
                    sugestoes += "\n"

            return sugestoes

        except Exception as e:
            return f"Erro ao gerar sugestões de balanceamento: {str(e)}\n\n"

    def _converter_ativo_para_ticker(self, ativo: str) -> Optional[str]:
        """Converte ativo para ticker Yahoo Finance"""
        conversoes = {
            'GBP/JPY': 'GBPJPY=X',
            'EUR/USD': 'EURUSD=X',
            'CHF/JPY': 'CHFJPY=X',
            'GBP/USD': 'GBPUSD=X',
            'USD/JPY': 'USDJPY=X',
            'USD/CAD': 'USDCAD=X',
            'USD/CHF': 'USDCHF=X',
            'AUD/USD': 'AUDUSD=X',
            'AUD/CHF': 'AUDCHF=X',
            'AUD/JPY': 'AUDJPY=X',
            'XAU/USD': 'GC=F'
        }
        return conversoes.get(ativo)

    # ========================================
    # ANÁLISE INTEGRADA AVANÇADA
    # ========================================

    def realizar_analise_integrada(self) -> Dict:
        """
        Realiza análise integrada completa com todos os módulos
        """

        analises = {}

        try:
            # 1. Análise de risco sistêmico com correlação
            analises['risco_sistemico'] = self.analisar_risco_sistemico_balanceamento()

            # 2. Simulação de impacto cascata
            analises['impacto_cascata'] = self.simular_protecao_impacto_cascata()

            # 3. Recomendações de diversificação por clusters
            analises['diversificacao_clusters'] = self.recomendar_diversificacao_clusters()

            # 4. Sugestões baseadas em níveis
            analises['sugestoes_niveis'] = self.gerar_sugestoes_niveis_inteligentes()

            # 5. Validação macroeconômica
            analises['validacao_macroeconomica'] = self.validar_cenario_macroeconomico()

            print("✅ Análises integradas concluídas")

        except Exception as e:
            print(f"⚠️ Erro em análise integrada: {e}")
            analises['erro'] = str(e)

        return analises

    # ========================================
    # ANÁLISES ESPECÍFICAS COM CORRELAÇÃO
    # ========================================

    def analisar_risco_sistemico_balanceamento(self) -> Dict:
        """
        Usa modulo_correlacao_avancada para identificar necessidades de balanceamento
        """

        try:
            # Carregar dados no módulo de correlação
            self.modulo_correlacao.carregar_portfolio()
            self.modulo_correlacao.carregar_precos_historicos()
            self.modulo_correlacao.calcular_matriz_correlacao_real()
            self.modulo_correlacao.construir_rede_correlacao()

            # Calcular risco sistêmico
            risco_sistemico = self.modulo_correlacao.calcular_risco_sistemico()

            # Identificar concentrações excessivas
            concentracao_excessiva = {}
            for moeda, risco in risco_sistemico.items():
                if risco > 0.15:  # Threshold alto
                    concentracao_excessiva[moeda] = {
                        'risco_sistemico': risco,
                        'recomendacao': 'REDUZIR_EXPOSICAO',
                        'justificativa': f'Alto risco sistêmico ({risco:.1%}) - diversificar'
                    }

            # Identificar clusters
            clusters = self.modulo_correlacao.identificar_clusters_correlacao()

            protecao_clusters = {}
            for cluster in clusters:
                if cluster.correlacao_media > 0.7:
                    protecao_clusters[cluster.id_cluster] = {
                        'moedas_afetadas': list(cluster.moedas),
                        'correlacao_media': cluster.correlacao_media,
                        'recomendacao': 'HEDGE_CORRELACIONADO',
                        'justificativa': f'Cluster altamente correlacionado ({cluster.correlacao_media:.1%})'
                    }

            return {
                'concentracao_excessiva': concentracao_excessiva,
                'protecao_clusters': protecao_clusters,
                'clusters_identificados': len(clusters),
                'timestamp_analise': datetime.now().isoformat()
            }

        except Exception as e:
            return {'erro': f'Erro na análise de risco sistêmico: {str(e)}'}

    def simular_protecao_impacto_cascata(self, moeda_alvo: str = "EUR") -> Dict:
        """
        Simula impacto cascata para recomendar proteções preventivas
        """

        try:
            # Simular choque de 5%
            impacto_cascata = self.modulo_correlacao.analisar_impacto_cascata(
                moeda_afetada=moeda_alvo,
                choque_inicial=0.05
            )

            # Identificar moedas mais afetadas
            moedas_afetadas = sorted(
                [(moeda, impacto) for moeda, impacto in impacto_cascata.items() if impacto > 0.01],
                key=lambda x: x[1],
                reverse=True
            )[:5]

            # Recomendações de proteção
            recomendacoes_protecao = {}
            for moeda, impacto in moedas_afetadas:
                if impacto > 0.03:
                    recomendacoes_protecao[moeda] = {
                        'impacto_cascata': impacto,
                        'protecao_recomendada': self._determinar_tipo_protecao(moeda, impacto),
                        'urgencia': 'ALTA' if impacto > 0.04 else 'MEDIA',
                        'justificativa': f'Impacto cascata de {impacto:.1%} de {moeda_alvo}'
                    }

            return {
                'moeda_alvo': moeda_alvo,
                'choque_simulado': 0.05,
                'moedas_afetadas': moedas_afetadas,
                'recomendacoes_protecao': recomendacoes_protecao,
                'timestamp_simulacao': datetime.now().isoformat()
            }

        except Exception as e:
            return {'erro': f'Erro na simulação de impacto cascata: {str(e)}'}

    def recomendar_diversificacao_clusters(self) -> List[Dict]:
        """
        Recomendações de diversificação baseadas em clusters de correlação
        """

        try:
            clusters = self.modulo_correlacao.identificar_clusters_correlacao()
            recomendacoes = []

            for cluster in clusters:
                exposicao_cluster = self._calcular_exposicao_cluster(cluster)

                if exposicao_cluster['percentual_total'] > 0.25:  # >25% do portfolio
                    recomendacao = {
                        'tipo': 'DIVERSIFICACAO_CLUSTER',
                        'cluster_id': cluster.id_cluster,
                        'moedas_afetadas': list(cluster.moedas),
                        'exposicao_atual': exposicao_cluster['percentual_total'],
                        'correlacao_media': cluster.correlacao_media,
                        'acao_recomendada': 'REDUZIR_EXPOSICAO_20_30_PCT',
                        'ativos_alternativos': self._sugerir_moedas_diversificacao(cluster),
                        'justificativa': f'Cluster representa {exposicao_cluster["percentual_total"]:.1%} do portfolio',
                        'prioridade': 'ALTA'
                    }
                    recomendacoes.append(recomendacao)

            return recomendacoes

        except Exception as e:
            return [{'erro': f'Erro nas recomendações de diversificação: {str(e)}'}]

    # ========================================
    # ANÁLISES COM NÍVEIS DE PREÇO
    # ========================================

    def gerar_sugestoes_niveis_inteligentes(self) -> Dict:
        """
        Gera sugestões inteligentes baseadas em níveis de preço
        """

        sugestoes = {}

        try:
            portfolio = self.gestor_portfolio.portfolio

            for posicao in portfolio.get('positions', []):
                if posicao['status'] == 'OPEN':
                    posicao_id = posicao['position_id']
                    sugestoes[posicao_id] = self.recomendar_take_reforco_niveis(posicao)

            return sugestoes

        except Exception as e:
            return {'erro': f'Erro nas sugestões de níveis: {str(e)}'}

    def recomendar_take_reforco_niveis(self, posicao: Dict) -> Dict:
        """
        Recomendações de take profit ou reforço baseadas em níveis críticos
        """

        try:
            par = posicao['currency_pair']
            preco_atual = posicao['current_price']
            direcao = posicao['direction']

            # Obter níveis do ativo
            ticker = self._converter_ativo_para_ticker(par)
            if not ticker:
                return {'erro': f'Ticker não encontrado para {par}'}

            niveis = self.motor_niveis.obter_niveis_ativo(ticker)

            recomendacoes = {
                'take_profit': [],
                'reforco': [],
                'risco': []
            }

            if direcao == 'LONG':
                # Take profit em resistências próximas
                resistencias = niveis.get('resistencias_chave', [])
                for resistencia in resistencias[:3]:
                    distancia = ((resistencia / preco_atual) - 1) * 100
                    if 0.5 <= distancia <= 5.0:
                        recomendacoes['take_profit'].append({
                            'nivel': resistencia,
                            'distancia_percentual': distancia,
                            'pontuacao': self._calcular_pontuacao_take(resistencia, distancia)
                        })

                # Reforço em suportes próximos
                suportes = niveis.get('suportes_chave', [])
                for suporte in suportes[:2]:
                    distancia = ((preco_atual / suporte) - 1) * 100
                    if distancia <= 0.3:
                        recomendacoes['reforco'].append({
                            'nivel': suporte,
                            'distancia_percentual': distancia,
                            'justificativa': 'Suporte crítico próximo - oportunidade de reforço'
                        })

            elif direcao == 'SHORT':
                # Take profit em suportes próximos
                suportes = niveis.get('suportes_chave', [])
                for suporte in suportes[:3]:
                    distancia = ((preco_atual / suporte) - 1) * 100
                    if 0.5 <= distancia <= 5.0:
                        recomendacoes['take_profit'].append({
                            'nivel': suporte,
                            'distancia_percentual': distancia,
                            'pontuacao': self._calcular_pontuacao_take(suporte, distancia)
                        })

                # Reforço em resistências próximas
                resistencias = niveis.get('resistencias_chave', [])
                for resistencia in resistencias[:2]:
                    distancia = ((resistencia / preco_atual) - 1) * 100
                    if distancia <= 0.3:
                        recomendacoes['reforco'].append({
                            'nivel': resistencia,
                            'distancia_percentual': distancia,
                            'justificativa': 'Resistência crítica próxima - oportunidade de reforço'
                        })

            return recomendacoes

        except Exception as e:
            return {'erro': f'Erro nas recomendações de níveis: {str(e)}'}

    # ========================================
    # VALIDAÇÃO MACROECONÔMICA
    # ========================================

    def validar_cenario_macroeconomico(self) -> Dict:
        """
        Valida se o portfolio está coerente com cenário macro atual
        """

        try:
            # Coletar dados macro
            dados_dxy = self.analisador_macro.coletar_dados_dxy()
            eventos_criticos = self.analisador_macro.identificar_eventos_criticos()

            # Análise de exposição
            exposicao_moeda = self.analisador_risco.calcular_exposicao_cambial()

            # Validar coerência
            validacao = {
                'regime_dolar': dados_dxy.get('regime', 'DESCONHECIDO'),
                'eventos_criticos': eventos_criticos,
                'exposicao_risco': {},
                'recomendacoes_macro': []
            }

            # Análise por moeda
            for moeda, exposicao in exposicao_moeda.items():
                risco_macro = self._avaliar_risco_macro_moeda(moeda, dados_dxy, eventos_criticos)
                validacao['exposicao_risco'][moeda] = {
                    'exposicao_total': exposicao,
                    'risco_macro': risco_macro,
                    'coerente': risco_macro['nivel'] <= 3
                }

            # Recomendações baseadas em cenário
            validacao['recomendacoes_macro'] = self._gerar_recomendacoes_macro(validacao)

            return validacao

        except Exception as e:
            return {'erro': f'Erro na validação macroeconômica: {str(e)}'}

    # ========================================
    # RELATÓRIO EXECUTIVO
    # ========================================

    def gerar_relatorio_executivo_inteligente(self) -> RelatorioExecutivoInteligente:
        """
        Gera relatório executivo completo com todas as análises
        """

        try:
            # Resumo do portfolio
            portfolio_resumo = self._gerar_resumo_portfolio()

            # Análise de risco
            analise_risco = self.analisador_risco.calcular_metricas_risco()

            # Validação macro
            validacao_macro = self.validar_cenario_macroeconomico()

            # Análise de correlação sistêmica
            analise_correlacao = self.analisar_risco_sistemico_balanceamento()

            # Sugestões de balanceamento/proteção
            sugestoes_balanceamento = {
                'impacto_cascata': self.simular_protecao_impacto_cascata(),
                'diversificacao_clusters': self.recomendar_diversificacao_clusters()
            }

            # Sugestões de níveis
            sugestoes_niveis = self.gerar_sugestoes_niveis_inteligentes()

            # Recomendações finais integradas
            recomendacoes_finais = self._integrar_recomendacoes_finais(
                analise_risco, validacao_macro, analise_correlacao,
                sugestoes_balanceamento, sugestoes_niveis
            )

            relatorio = RelatorioExecutivoInteligente(
                timestamp=datetime.now(timezone.utc),
                portfolio_resumo=portfolio_resumo,
                analise_risco=analise_risco,
                validacao_macroeconomica=validacao_macro,
                analise_correlacao_sistemica=analise_correlacao,
                sugestoes_balanceamento_protecao=sugestoes_balanceamento,
                sugestoes_niveis_take_reforco=sugestoes_niveis,
                recomendacoes_finais_integradas=recomendacoes_finais
            )

            # Salvar relatório
            self._salvar_relatorio(relatorio)

            return relatorio

        except Exception as e:
            print(f"❌ Erro na geração do relatório: {e}")
            raise

    def _integrar_recomendacoes_finais(self, analise_risco: Dict, validacao_macro: Dict,
                                      analise_correlacao: Dict, sugestoes_balanceamento: Dict,
                                      sugestoes_niveis: Dict) -> List[Dict]:
        """Integra todas as recomendações em uma lista consolidada"""
        try:
            recomendacoes = []

            # Recomendações de risco
            if analise_risco and 'recomendacoes' in analise_risco:
                for rec in analise_risco['recomendacoes']:
                    recomendacoes.append({
                        'tipo': 'RISCO',
                        'prioridade': rec.get('prioridade', 'MEDIA'),
                        'recomendacao': rec.get('recomendacao', ''),
                        'justificativa': rec.get('justificativa', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            # Recomendações macroeconômicas
            if validacao_macro and 'recomendacoes' in validacao_macro:
                for rec in validacao_macro['recomendacoes']:
                    recomendacoes.append({
                        'tipo': 'MACROECONOMICO',
                        'prioridade': rec.get('prioridade', 'MEDIA'),
                        'recomendacao': rec.get('recomendacao', ''),
                        'justificativa': rec.get('justificativa', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            # Recomendações de correlação
            if analise_correlacao and 'recomendacoes' in analise_correlacao:
                for rec in analise_correlacao['recomendacoes']:
                    recomendacoes.append({
                        'tipo': 'CORRELACAO',
                        'prioridade': rec.get('prioridade', 'MEDIA'),
                        'recomendacao': rec.get('recomendacao', ''),
                        'justificativa': rec.get('justificativa', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            # Recomendações de balanceamento
            if sugestoes_balanceamento:
                for chave, valor in sugestoes_balanceamento.items():
                    if isinstance(valor, list):
                        for rec in valor:
                            recomendacoes.append({
                                'tipo': 'BALANCEAMENTO',
                                'prioridade': rec.get('prioridade', 'MEDIA'),
                                'recomendacao': rec.get('recomendacao', ''),
                                'justificativa': rec.get('justificativa', ''),
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            })

            # Recomendações de níveis
            if sugestoes_niveis and 'recomendacoes' in sugestoes_niveis:
                for rec in sugestoes_niveis['recomendacoes']:
                    recomendacoes.append({
                        'tipo': 'NIVEIS',
                        'prioridade': rec.get('prioridade', 'MEDIA'),
                        'recomendacao': rec.get('recomendacao', ''),
                        'justificativa': rec.get('justificativa', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            # Se não há recomendações específicas, adicionar recomendação padrão
            if not recomendacoes:
                recomendacoes.append({
                    'tipo': 'GERAL',
                    'prioridade': 'BAIXA',
                    'recomendacao': 'Manter monitoramento ativo do portfólio',
                    'justificativa': 'Nenhuma recomendação específica identificada no momento',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })

            return recomendacoes

        except Exception as e:
            return [{
                'tipo': 'ERRO',
                'prioridade': 'ALTA',
                'recomendacao': 'Revisar sistema de integração de recomendações',
                'justificativa': f'Erro na integração: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }]

    def gerar_relatorio_executivo(self) -> str:
        """
        Gera relatório executivo completo com iteração sobre posições OPEN
        """
        try:
            # Obter relatório inteligente
            relatorio_obj = self.gerar_relatorio_executivo_inteligente()

            # Converter para markdown
            markdown = "# 📊 RELATÓRIO EXECUTIVO - GESTÃO DE RISCO E PORTFÓLIO (RMS)\n\n"
            markdown += f"**Data/Hora:** {relatorio_obj.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"

            # 1. ITERAÇÃO E RELATÓRIO INDIVIDUAL DOS ATIVOS (Asset Deep Dive)
            markdown += "## � ANÁLISE INDIVIDUAL DOS ATIVOS (POSIÇÕES OPEN)\n\n"

            portfolio_data = self.gestor_portfolio.portfolio
            positions = portfolio_data.get('positions', [])
            posicoes_open = [p for p in positions if p.get('status') == 'OPEN']

            if posicoes_open:
                for posicao in posicoes_open:
                    markdown += self._gerar_analise_individual_ativo(posicao)
                    markdown += "\n---\n\n"

                # Consolidado das posições
                markdown += self._gerar_consolidado_posicoes(posicoes_open)
            else:
                markdown += "*Nenhuma posição aberta encontrada.*\n\n"

            # 2. RISCO DO PORTFÓLIO (CONSOLIDADO)
            markdown += "## ⚠️ RISCO DO PORTFÓLIO (CONSOLIDADO)\n\n"
            markdown += self._gerar_analise_risco_consolidado(portfolio_data)

            # 3. COERÊNCIA MACROECONÔMICA
            markdown += "## 🌍 COERÊNCIA MACROECONÔMICA\n\n"
            markdown += self._gerar_analise_coerencia_macroeconomica(portfolio_data)

            # 4. SUGESTÕES OTIMIZADAS (AÇÃO ACIONÁVEL)
            markdown += "## 💡 SUGESTÕES OTIMIZADAS (AÇÃO ACIONÁVEL)\n\n"

            # Balanceamento/Proteção com prioridade JPY
            markdown += "### 🛡️ BALANCEAMENTO E PROTEÇÃO\n\n"
            markdown += self._gerar_sugestoes_balanceamento_prioridade_jpy(relatorio_obj, portfolio_data)

            # Take/Reforço
            markdown += "### 🎯 TAKE E REFORÇO\n\n"
            niveis = relatorio_obj.sugestoes_niveis_take_reforco
            if isinstance(niveis, dict):
                for chave, valor in niveis.items():
                    markdown += f"#### {chave.replace('_', ' ').title()}\n"
                    if isinstance(valor, dict):
                        for sub_chave, sub_valor in valor.items():
                            markdown += f"- **{sub_chave.replace('_', ' ').title()}:** {sub_valor}\n"
                    else:
                        markdown += f"{valor}\n"
                    markdown += "\n"
            else:
                markdown += f"```\n{niveis}\n```\n\n"

            markdown += "---\n"
            markdown += "*Relatório gerado automaticamente pelo Agente Adaptativo de Gestão de Risco e Portfólio (RMS)*"

            return markdown

        except Exception as e:
            return f"# ❌ ERRO NA GERAÇÃO DO RELATÓRIO\n\nErro: {str(e)}"

    def _gerar_analise_individual_ativo(self, posicao: Dict) -> str:
        """Gera mini-análise individual para um ativo (Asset Deep Dive)"""
        ativo = posicao.get('currency_pair', 'N/A')
        direcao = posicao.get('direction', 'N/A')
        pnl_nao_realizado = posicao.get('pnl_unrealized', 0)
        estrategia = posicao.get('strategy', 'N/A')
        ticket = posicao.get('ticket', 'N/A')

        # Avaliação de risco individual
        risco_individual = self._calcular_risco_individual(posicao)

        analise = f"### {ativo} ({direcao}) - Ticket: {ticket}\n\n"
        analise += f"**📈 P&L Não Realizado:** R$ {pnl_nao_realizado:,.2f}\n\n"
        analise += f"**🎯 Estratégia:** {estrategia}\n\n"
        analise += f"**⚠️ Avaliação de Risco Individual:**\n{risco_individual}\n\n"

        return analise

    def _calcular_risco_individual(self, posicao: Dict) -> str:
        """Calcula avaliação de risco individual para uma posição"""
        try:
            preco_atual = posicao.get('current_price', 0)
            stop_loss = posicao.get('stop_loss')
            take_profit = posicao.get('take_profit', [])

            risco = ""

            if stop_loss:
                if posicao['direction'] == 'LONG':
                    distancia_sl = ((preco_atual - stop_loss) / preco_atual) * 100
                    risco += f"- **Distância para Stop-Loss:** {distancia_sl:.2f}%\n"
                else:  # SHORT
                    distancia_sl = ((stop_loss - preco_atual) / preco_atual) * 100
                    risco += f"- **Distância para Stop-Loss:** {distancia_sl:.2f}%\n"

            if take_profit:
                if isinstance(take_profit, list) and take_profit:
                    tp_nivel = take_profit[0].get('level', 0) if isinstance(take_profit[0], dict) else take_profit[0]
                    if posicao['direction'] == 'LONG':
                        distancia_tp = ((tp_nivel - preco_atual) / preco_atual) * 100
                        risco += f"- **Distância para Take-Profit:** {distancia_tp:.2f}%\n"
                    else:  # SHORT
                        distancia_tp = ((preco_atual - tp_nivel) / preco_atual) * 100
                        risco += f"- **Distância para Take-Profit:** {distancia_tp:.2f}%\n"

            # Avaliação qualitativa
            pnl = posicao.get('pnl_unrealized', 0)
            if pnl > 0:
                risco += "- **Status:** Positivo - Monitorar para take-profit\n"
            elif pnl < -1000:  # Perda significativa
                risco += "- **Status:** Atenção - Avaliar stop-loss ou ajuste\n"
            else:
                risco += "- **Status:** Neutro - Manter monitoramento\n"

            return risco

        except Exception as e:
            return f"- **Erro na avaliação:** {str(e)}\n"

    def _gerar_consolidado_posicoes(self, posicoes_open: List[Dict]) -> str:
        """Gera consolidado das posições para o relatório de performance e alocação"""
        if not posicoes_open:
            return ""

        # Cálculos consolidados
        total_pnl = sum(p.get('pnl_unrealized', 0) for p in posicoes_open)
        pnl_positivo = sum(p.get('pnl_unrealized', 0) for p in posicoes_open if p.get('pnl_unrealizado', 0) > 0)
        pnl_negativo = sum(p.get('pnl_unrealizado', 0) for p in posicoes_open if p.get('pnl_unrealizado', 0) < 0)

        # Contagem por direção
        long_positions = len([p for p in posicoes_open if p.get('direction') == 'LONG'])
        short_positions = len([p for p in posicoes_open if p.get('direction') == 'SHORT'])

        # Top performers
        top_performers = sorted(posicoes_open, key=lambda x: x.get('pnl_unrealizado', 0), reverse=True)[:3]

        consolidado = "### 📊 CONSOLIDADO DAS POSIÇÕES\n\n"
        consolidado += f"**Total de Posições Abertas:** {len(posicoes_open)}\n\n"
        consolidado += f"**P&L Total Não Realizado:** R$ {total_pnl:,.2f}\n"
        consolidado += f"- **Positivo:** R$ {pnl_positivo:,.2f}\n"
        consolidado += f"- **Negativo:** R$ {pnl_negativo:,.2f}\n\n"

        consolidado += f"**Distribuição por Direção:**\n"
        consolidado += f"- **LONG:** {long_positions} posições\n"
        consolidado += f"- **SHORT:** {short_positions} posições\n\n"

        consolidado += "**🏆 Top 3 Performers:**\n"
        for i, pos in enumerate(top_performers, 1):
            ativo = pos.get('currency_pair', 'N/A')
            pnl = pos.get('pnl_unrealized', 0)
            consolidado += f"{i}. {ativo}: R$ {pnl:,.2f}\n"
        consolidado += "\n"

        return consolidado

    def _gerar_analise_risco_consolidado(self, portfolio_data: Dict) -> str:
        """Gera análise de risco consolidado focada em exposição e correlação"""
        try:
            allocation = portfolio_data.get('allocation', {})
            correlation_matrix = allocation.get('correlation_matrix', {})

            # Exposição de moedas (Net Exposure)
            exposicao_moedas = allocation.get('by_currency', {})
            exposicao_texto = "### 💱 EXPOSIÇÃO DE MOEDAS (NET EXPOSURE)\n\n"
            for moeda, exposicao in exposicao_moedas.items():
                status = "🔴 ALTA" if abs(exposicao) > 50 else "🟡 MODERADA" if abs(exposicao) > 20 else "🟢 BAIXA"
                exposicao_texto += f"- **{moeda}:** {exposicao}% ({status})\n"
            exposicao_texto += "\n"

            # Drawdown implícito (baseado em posições atuais)
            positions = portfolio_data.get('positions', [])
            posicoes_open = [p for p in positions if p.get('status') == 'OPEN']

            if posicoes_open:
                # Calcular drawdown potencial baseado em stop-loss
                drawdown_potencial = 0
                for pos in posicoes_open:
                    stop_loss = pos.get('stop_loss')
                    if stop_loss:
                        preco_atual = pos.get('current_price', 0)
                        lots = pos.get('lots', 0)
                        lot_size = pos.get('lot_size', 100000)

                        if pos['direction'] == 'LONG':
                            perda_potencial = (preco_atual - stop_loss) * lots * lot_size
                        else:  # SHORT
                            perda_potencial = (stop_loss - preco_atual) * lots * lot_size

                        drawdown_potencial += max(0, -perda_potencial)  # Só perdas

                capital_total = portfolio_data.get('portfolio_metadata', {}).get('total_capital', 100000)
                drawdown_percentual = (drawdown_potencial / capital_total) * 100
            else:
                drawdown_percentual = 0

            drawdown_texto = f"### 📉 DRAWDOWN IMPLÍCITO\n\n"
            drawdown_texto += f"- **Drawdown Potencial:** R$ {drawdown_potencial:,.2f}\n"
            drawdown_texto += f"- **Percentual do Capital:** {drawdown_percentual:.2f}%\n"
            status_dd = "🔴 CRÍTICO" if drawdown_percentual > 5 else "🟡 ATENÇÃO" if drawdown_percentual > 2 else "🟢 CONTROLADO"
            drawdown_texto += f"- **Status:** {status_dd}\n\n"

            # Impacto da correlação na volatilidade
            correlacao_texto = "### 🔗 IMPACTO DA CORRELAÇÃO NA VOLATILIDADE\n\n"
            if correlation_matrix:
                correlacao_texto += "**Matriz de Correlação Crítica:**\n"
                for par, correlacao in correlation_matrix.items():
                    intensidade = "🔴 FORTE" if abs(correlacao) > 0.7 else "🟡 MODERADA" if abs(correlacao) > 0.4 else "🟢 FRACA"
                    correlacao_texto += f"- **{par}:** {correlacao:.2f} ({intensidade})\n"
                correlacao_texto += "\n"

                # Análise de risco sistêmico
                correlacoes_fortes = [c for c in correlation_matrix.values() if abs(c) > 0.7]
                if correlacoes_fortes:
                    correlacao_texto += "**⚠️ Risco Sistêmico:** Correlações fortes detectadas. "
                    correlacao_texto += "Movimentos em um ativo podem impactar outros significativamente.\n\n"
                else:
                    correlacao_texto += "**✅ Risco Sistêmico:** Diversificação adequada mantida.\n\n"
            else:
                correlacao_texto += "*Dados de correlação não disponíveis.*\n\n"

            return exposicao_texto + drawdown_texto + correlacao_texto

        except Exception as e:
            return f"Erro na análise de risco consolidado: {str(e)}\n\n"

    def _gerar_analise_coerencia_macroeconomica(self, portfolio_data: Dict) -> str:
        """Gera análise de coerência macroeconômica focada em estratégias ativas"""
        try:
            allocation = portfolio_data.get('allocation', {})
            estrategias = allocation.get('by_strategy', {})
            exposicao_moedas = allocation.get('by_currency', {})

            # Análise de estratégias ativas
            analise = "### 🎯 ANÁLISE DE ESTRATÉGIAS ATIVAS\n\n"

            if estrategias:
                for estrategia, percentual in estrategias.items():
                    analise += f"**{estrategia.replace('_', ' ').title()}:** {percentual}%\n"

                    # Avaliação específica por estratégia
                    if 'carry' in estrategia.lower():
                        analise += "- **Carry Trade:** Alinhado com cenário de dólar moderado. "
                        analise += "Diferenças de taxa favorecem posições LONG em moedas de alta taxa.\n\n"
                    elif 'rate_differential' in estrategia.lower():
                        analise += "- **Diferenical de Taxa:** Estratégia defensiva adequada para "
                        analise += "períodos de incerteza no mercado de juros.\n\n"
                    elif 'hedge' in estrategia.lower():
                        analise += "- **Hedge/Proteção:** Estratégia prudente para proteção contra "
                        analise += "volatilidade e riscos sistêmicos.\n\n"
                    else:
                        analise += "- **Análise:** Estratégia genérica - monitorar performance.\n\n"
            else:
                analise += "*Dados de estratégias não disponíveis.*\n\n"

            # Análise de exposição por moeda