#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Web Interativo - Interface para Monitoramento de Mercado
Flask web application para visualização em tempo real de oportunidades e contexto macro
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import Flask, render_template, jsonify, request
import yfinance as yf

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports dos sistemas existentes
from backend.sistema_alertas_simplificado import SistemaAlertasSimplificado

class DashboardMercadoFinanceiro:
    """
    Dashboard Web para monitoramento completo do mercado

    Funcionalidades:
    - Visualização de oportunidades em tempo real
    - Contexto macroeconômico atualizado
    - Performance histórica do portfólio
    - Controle dos sistemas de monitoramento
    - Alertas e notificações
    """

    def __init__(self):
        self.app = Flask(__name__,
                        template_folder='../web/templates',
                        static_folder='../web/static')

        self.sistema_alertas = SistemaAlertasSimplificado()

        # Configurar rotas
        self.configurar_rotas()

        # Criar diretórios web
        os.makedirs('web/templates', exist_ok=True)
        os.makedirs('web/static/css', exist_ok=True)
        os.makedirs('web/static/js', exist_ok=True)

    def configurar_rotas(self):
        """Configurar todas as rotas da aplicação"""

        @self.app.route('/')
        def dashboard_principal():
            """Página principal do dashboard"""
            return render_template('dashboard.html')

        @self.app.route('/api/contexto-macro')
        def api_contexto_macro():
            """API para contexto macroeconômico atual"""
            try:
                contexto = self.obter_contexto_macro()
                return jsonify(contexto)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/oportunidades')
        def api_oportunidades():
            """API para oportunidades atuais"""
            try:
                oportunidades = self.obter_oportunidades_recentes()
                return jsonify(oportunidades)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/portfolio')
        def api_portfolio():
            """API para dados do portfólio"""
            try:
                portfolio = self.obter_dados_portfolio()
                return jsonify(portfolio)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/alertas')
        def api_alertas():
            """API para histórico de alertas"""
            try:
                dias = request.args.get('dias', 7, type=int)
                alertas = self.obter_alertas_recentes(dias)
                return jsonify(alertas)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/performance')
        def api_performance():
            """API para métricas de performance"""
            try:
                performance = self.calcular_metricas_performance()
                return jsonify(performance)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/sistema/status')
        def api_sistema_status():
            """API para status dos sistemas"""
            try:
                status = self.verificar_status_sistemas()
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def obter_contexto_macro(self) -> Dict:
        """Obter contexto macroeconômico atual"""
        try:
            # Indicadores principais
            vix = yf.Ticker('^VIX')
            vix_data = vix.history(period='2d')
            vix_atual = float(vix_data['Close'].iloc[-1]) if not vix_data.empty else 20.0

            treasury = yf.Ticker('^TNX')
            treasury_data = treasury.history(period='2d')
            treasury_atual = float(treasury_data['Close'].iloc[-1]) if not treasury_data.empty else 4.0

            sp500 = yf.Ticker('^GSPC')
            sp500_data = sp500.history(period='2d')
            sp500_atual = float(sp500_data['Close'].iloc[-1]) if not sp500_data.empty else 6700

            # Moeda e commodities
            dxy = yf.Ticker('DX-Y.NYB')
            dxy_data = dxy.history(period='2d')
            dxy_atual = float(dxy_data['Close'].iloc[-1]) if not dxy_data.empty else 100.0

            ouro = yf.Ticker('GC=F')
            ouro_data = ouro.history(period='2d')
            ouro_atual = float(ouro_data['Close'].iloc[-1]) if not ouro_data.empty else 2000.0

            petroleo = yf.Ticker('CL=F')
            petroleo_data = petroleo.history(period='2d')
            petroleo_atual = float(petroleo_data['Close'].iloc[-1]) if not petroleo_data.empty else 70.0

            return {
                'timestamp': datetime.now().isoformat(),
                'indicadores': {
                    'vix': {
                        'valor': vix_atual,
                        'nivel': 'Baixo' if vix_atual < 20 else 'Moderado' if vix_atual < 30 else 'Alto',
                        'cor': '#28a745' if vix_atual < 20 else '#ffc107' if vix_atual < 30 else '#dc3545'
                    },
                    'treasury_10y': {
                        'valor': treasury_atual,
                        'nivel': 'Baixas' if treasury_atual < 2 else 'Moderadas' if treasury_atual < 4 else 'Elevadas',
                        'cor': '#28a745' if treasury_atual < 2 else '#ffc107' if treasury_atual < 4 else '#dc3545'
                    },
                    'sp500': {
                        'valor': sp500_atual,
                        'nivel': 'Otimista' if sp500_atual > 6500 else 'Neutro',
                        'cor': '#28a745' if sp500_atual > 6500 else '#6c757d'
                    },
                    'dxy': {
                        'valor': dxy_atual,
                        'nivel': 'Forte' if dxy_atual > 105 else 'Fraco' if dxy_atual < 95 else 'Neutro',
                        'cor': '#dc3545' if dxy_atual > 105 else '#28a745' if dxy_atual < 95 else '#6c757d'
                    },
                    'ouro': {
                        'valor': ouro_atual,
                        'nivel': 'Alta' if ouro_atual > 2500 else 'Moderada' if ouro_atual > 2000 else 'Baixa',
                        'cor': '#ffc107' if ouro_atual > 2500 else '#6c757d'
                    },
                    'petroleo': {
                        'valor': petroleo_atual,
                        'nivel': 'Alto' if petroleo_atual > 80 else 'Moderado' if petroleo_atual > 60 else 'Baixo',
                        'cor': '#dc3545' if petroleo_atual > 80 else '#ffc107' if petroleo_atual > 60 else '#28a745'
                    }
                }
            }

        except Exception as e:
            return {'error': f'Erro obtendo contexto macro: {e}'}

    def obter_oportunidades_recentes(self, limit: int = 10) -> List[Dict]:
        """Obter oportunidades mais recentes"""
        try:
            # Carregar alertas do arquivo
            if os.path.exists(self.sistema_alertas.alertas_file):
                with open(self.sistema_alertas.alertas_file, 'r', encoding='utf-8') as f:
                    alertas = json.load(f)

                # Filtrar e formatar
                oportunidades = []
                for alerta in alertas[:limit]:
                    oportunidades.append({
                        'id': alerta['id_alerta'],
                        'timestamp': alerta['timestamp'],
                        'ativo': alerta['ativo'],
                        'acao': alerta['acao_recomendada'],
                        'probabilidade': alerta['probabilidade_sucesso'],
                        'confianca': alerta['confianca'],
                        'risk_reward': alerta['risk_reward'],
                        'preco_entrada': alerta['preco_entrada'],
                        'preco_alvo': alerta['preco_alvo'],
                        'stop_loss': alerta['stop_loss'],
                        'timeframe': alerta['timeframe'],
                        'prioridade': alerta['prioridade'],
                        'catalysts': alerta['catalysts'][:2]  # Primeiros 2 catalysts
                    })

                return oportunidades

            return []

        except Exception as e:
            return {'error': f'Erro obtendo oportunidades: {e}'}

    def obter_dados_portfolio(self) -> Dict:
        """Obter dados resumidos do portfólio"""
        try:
            # Carregar portfólio
            portfolio_path = "backend/data/portfolio/portfolio_atual.json"

            if not os.path.exists(portfolio_path):
                return {'error': 'Portfólio não encontrado'}

            with open(portfolio_path, 'r', encoding='utf-8') as f:
                portfolio = json.load(f)

            # Calcular métricas
            posicoes_abertas = [p for p in portfolio['positions'] if p['status'] == 'OPEN']
            posicoes_fechadas = [p for p in portfolio['positions'] if p['status'] == 'CLOSED']

            capital_total = portfolio['portfolio_metadata']['total_capital']
            pnl_unrealized = sum(p.get('pnl_unrealized', 0) for p in posicoes_abertas)
            pnl_realized = sum(p.get('pnl_realized', 0) for p in posicoes_fechadas)
            pnl_total = pnl_unrealized + pnl_realized
            retorno_pct = (pnl_total / capital_total) * 100

            # Top posições
            todas_posicoes = posicoes_abertas + posicoes_fechadas
            todas_posicoes.sort(key=lambda x: x.get('pnl_unrealized', 0) + x.get('pnl_realized', 0), reverse=True)

            top_posicoes = []
            for pos in todas_posicoes[:5]:
                pnl_pos = pos.get('pnl_unrealized', 0) + pos.get('pnl_realized', 0)
                top_posicoes.append({
                    'ativo': pos['currency_pair'],
                    'direcao': pos['direction'],
                    'pnl': pnl_pos,
                    'status': pos['status'],
                    'entrada': pos['entry_price']
                })

            return {
                'resumo': {
                    'capital_total': capital_total,
                    'pnl_total': pnl_total,
                    'retorno_percentual': retorno_pct,
                    'posicoes_ativas': len(posicoes_abertas),
                    'posicoes_fechadas': len(posicoes_fechadas),
                    'pnl_unrealized': pnl_unrealized,
                    'pnl_realized': pnl_realized
                },
                'top_posicoes': top_posicoes,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'error': f'Erro obtendo portfolio: {e}'}

    def obter_alertas_recentes(self, dias: int = 7) -> List[Dict]:
        """Obter alertas dos últimos N dias"""
        try:
            conn = sqlite3.connect(self.sistema_alertas.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id_alerta, timestamp_envio, ativo, acao_recomendada,
                       probabilidade_sucesso, confianca, risk_reward, prioridade,
                       canais_enviados
                FROM alertas_enviados
                WHERE timestamp_envio >= datetime('now', '-{} days')
                ORDER BY timestamp_envio DESC
                LIMIT 20
            '''.format(dias))

            alertas = []
            for row in cursor.fetchall():
                alertas.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'ativo': row[2],
                    'acao': row[3],
                    'probabilidade': row[4],
                    'confianca': row[5],
                    'risk_reward': row[6],
                    'prioridade': row[7],
                    'canais': json.loads(row[8]) if row[8] else []
                })

            conn.close()

            return alertas

        except Exception as e:
            return {'error': f'Erro obtendo alertas: {e}'}

    def calcular_metricas_performance(self) -> Dict:
        """Calcular métricas de performance dos sistemas"""
        try:
            # Performance dos alertas (últimos 30 dias)
            conn = sqlite3.connect(self.sistema_alertas.db_path)
            cursor = conn.cursor()

            # Total de alertas por período
            cursor.execute('''
                SELECT
                    COUNT(*) as total_alertas,
                    COUNT(CASE WHEN canais_enviados != '[]' THEN 1 END) as alertas_enviados,
                    AVG(probabilidade_sucesso) as prob_media,
                    AVG(confianca) as conf_media
                FROM alertas_enviados
                WHERE timestamp_envio >= datetime('now', '-30 days')
            ''')

            stats = cursor.fetchone()

            # Distribuição por ação
            cursor.execute('''
                SELECT acao_recomendada, COUNT(*) as count
                FROM alertas_enviados
                WHERE timestamp_envio >= datetime('now', '-30 days')
                GROUP BY acao_recomendada
                ORDER BY count DESC
            ''')

            distribuicao_acoes = [{'acao': row[0], 'count': row[1]} for row in cursor.fetchall()]

            # Distribuição por ativo
            cursor.execute('''
                SELECT ativo, COUNT(*) as count
                FROM alertas_enviados
                WHERE timestamp_envio >= datetime('now', '-30 days')
                GROUP BY ativo
                ORDER BY count DESC
                LIMIT 10
            ''')

            distribuicao_ativos = [{'ativo': row[0], 'count': row[1]} for row in cursor.fetchall()]

            conn.close()

            return {
                'alertas_30d': {
                    'total': stats[0] or 0,
                    'enviados': stats[1] or 0,
                    'taxa_envio': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
                    'probabilidade_media': stats[2] or 0,
                    'confianca_media': stats[3] or 0
                },
                'distribuicao_acoes': distribuicao_acoes,
                'distribuicao_ativos': distribuicao_ativos,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'error': f'Erro calculando performance: {e}'}

    def verificar_status_sistemas(self) -> Dict:
        """Verificar status operacional dos sistemas"""
        try:
            status = {
                'alertas': True,
                'portfolio': False,
                'macro_monitor': True,
                'backtesting': False,
                'integracao_corretoras': False
            }

            # Verificar sistema de alertas
            try:
                self.sistema_alertas.carregar_configuracao()
                status['alertas'] = True
            except:
                status['alertas'] = False

            # Verificar portfolio
            portfolio_path = "backend/data/portfolio/portfolio_atual.json"
            status['portfolio'] = os.path.exists(portfolio_path)

            # Verificar macro monitor (verificar se há dados recentes)
            try:
                vix = yf.Ticker('^VIX').history(period='1d')
                status['macro_monitor'] = not vix.empty
            except:
                status['macro_monitor'] = False

            return {
                'sistemas': status,
                'timestamp': datetime.now().isoformat(),
                'uptime': self.calcular_uptime()
            }

        except Exception as e:
            return {'error': f'Erro verificando status: {e}'}

    def calcular_uptime(self) -> str:
        """Calcular uptime aproximado"""
        # Simplificado - baseado na existência dos arquivos de sistema
        if os.path.exists(self.sistema_alertas.db_path):
            return "99.5%"  # Mock uptime
        return "0%"

    def executar(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = True):
        """Executar o servidor web"""
        print(f"🚀 Iniciando Dashboard Mercado Financeiro...")
        print(f"   URL: http://{host}:{port}")
        print(f"   Modo: {'Debug' if debug else 'Produção'}")

        self.app.run(host=host, port=port, debug=debug)

# Criar templates HTML
def criar_templates():
    """Criar templates HTML básicos"""

    # Template principal - dashboard.html
    dashboard_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Especialista Mercado Financeiro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .metric-card {
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
        }
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
        .status-warning { color: #ffc107; }

        .oportunidade-card {
            border-left: 4px solid #007bff;
            margin-bottom: 1rem;
        }
        .oportunidade-card.compra { border-left-color: #28a745; }
        .oportunidade-card.venda { border-left-color: #dc3545; }
        .oportunidade-card.observar { border-left-color: #ffc107; }

        .loading {
            text-align: center;
            padding: 2rem;
            color: #6c757d;
        }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-line"></i> Especialista Mercado Financeiro
            </span>
            <div class="d-flex">
                <span class="badge bg-success me-2" id="status-geral">Online</span>
                <span class="text-light" id="last-update">Atualizando...</span>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-3">
        <!-- Contexto Macro -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-globe"></i> Contexto Macroeconômico</h5>
                    </div>
                    <div class="card-body">
                        <div class="row" id="indicadores-macro">
                            <div class="loading">
                                <i class="fas fa-spinner fa-spin"></i> Carregando indicadores...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Portfolio e Oportunidades -->
        <div class="row mb-4">
            <!-- Portfolio -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-wallet"></i> Resumo do Portfólio</h5>
                    </div>
                    <div class="card-body" id="portfolio-resumo">
                        <div class="loading">
                            <i class="fas fa-spinner fa-spin"></i> Carregando portfólio...
                        </div>
                    </div>
                </div>
            </div>

            <!-- Oportunidades Recentes -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-bullseye"></i> Oportunidades Recentes</h5>
                    </div>
                    <div class="card-body" id="oportunidades-lista" style="max-height: 400px; overflow-y: auto;">
                        <div class="loading">
                            <i class="fas fa-spinner fa-spin"></i> Carregando oportunidades...
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alertas e Performance -->
        <div class="row mb-4">
            <!-- Alertas Recentes -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-bell"></i> Alertas Recentes (7 dias)</h5>
                    </div>
                    <div class="card-body" id="alertas-lista" style="max-height: 300px; overflow-y: auto;">
                        <div class="loading">
                            <i class="fas fa-spinner fa-spin"></i> Carregando alertas...
                        </div>
                    </div>
                </div>
            </div>

            <!-- Performance dos Sistemas -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-tachometer-alt"></i> Performance dos Sistemas</h5>
                    </div>
                    <div class="card-body" id="performance-metricas">
                        <div class="loading">
                            <i class="fas fa-spinner fa-spin"></i> Carregando métricas...
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Status dos Sistemas -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-server"></i> Status dos Sistemas</h5>
                    </div>
                    <div class="card-body" id="sistemas-status">
                        <div class="loading">
                            <i class="fas fa-spinner fa-spin"></i> Verificando sistemas...
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Atualização automática dos dados
        let updateInterval;

        async function atualizarDados() {
            try {
                // Atualizar indicadores macro
                const macroResponse = await fetch('/api/contexto-macro');
                const macroData = await macroResponse.json();
                atualizarIndicadoresMacro(macroData);

                // Atualizar portfolio
                const portfolioResponse = await fetch('/api/portfolio');
                const portfolioData = await portfolioResponse.json();
                atualizarPortfolio(portfolioData);

                // Atualizar oportunidades
                const oportunidadesResponse = await fetch('/api/oportunidades');
                const oportunidadesData = await oportunidadesResponse.json();
                atualizarOportunidades(oportunidadesData);

                // Atualizar alertas
                const alertasResponse = await fetch('/api/alertas');
                const alertasData = await alertasResponse.json();
                atualizarAlertas(alertasData);

                // Atualizar performance
                const performanceResponse = await fetch('/api/performance');
                const performanceData = await performanceResponse.json();
                atualizarPerformance(performanceData);

                // Atualizar status dos sistemas
                const statusResponse = await fetch('/api/sistema/status');
                const statusData = await statusResponse.json();
                atualizarStatusSistemas(statusData);

                // Atualizar timestamp
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();

            } catch (error) {
                console.error('Erro atualizando dados:', error);
                document.getElementById('status-geral').className = 'badge bg-danger me-2';
                document.getElementById('status-geral').textContent = 'Erro';
            }
        }

        function atualizarIndicadoresMacro(data) {
            const container = document.getElementById('indicadores-macro');

            if (data.error) {
                container.innerHTML = `<div class="col-12 text-danger">Erro: ${data.error}</div>`;
                return;
            }

            let html = '';
            for (const [key, indicator] of Object.entries(data.indicadores)) {
                html += `
                    <div class="col-md-2 col-sm-4 mb-3">
                        <div class="card metric-card text-center">
                            <div class="card-body">
                                <h6 class="card-title">${key.toUpperCase().replace('_', ' ')}</h6>
                                <h4 class="mb-1" style="color: ${indicator.cor}">${indicator.valor.toFixed(2)}</h4>
                                <small class="text-muted">${indicator.nivel}</small>
                            </div>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }

        function atualizarPortfolio(data) {
            const container = document.getElementById('portfolio-resumo');

            if (data.error) {
                container.innerHTML = `<div class="text-danger">Erro: ${data.error}</div>`;
                return;
            }

            const resumo = data.resumo;
            const retornoCor = resumo.retorno_percentual > 0 ? 'text-success' : 'text-danger';

            container.innerHTML = `
                <div class="row">
                    <div class="col-6">
                        <h6>Capital Total</h6>
                        <h4>$${resumo.capital_total.toLocaleString()}</h4>
                    </div>
                    <div class="col-6">
                        <h6>P&L Total</h6>
                        <h4 class="${retornoCor}">$${resumo.pnl_total.toLocaleString()}</h4>
                    </div>
                    <div class="col-6">
                        <h6>Retorno</h6>
                        <h4 class="${retornoCor}">${resumo.retorno_percentual.toFixed(1)}%</h4>
                    </div>
                    <div class="col-6">
                        <h6>Posições</h6>
                        <h4>${resumo.posicoes_ativas} ativas</h4>
                    </div>
                </div>
            `;
        }

        function atualizarOportunidades(data) {
            const container = document.getElementById('oportunidades-lista');

            if (data.error) {
                container.innerHTML = `<div class="text-danger">Erro: ${data.error}</div>`;
                return;
            }

            if (!data.length) {
                container.innerHTML = '<div class="text-muted">Nenhuma oportunidade recente</div>';
                return;
            }

            let html = '';
            data.forEach(opp => {
                const acaoClass = opp.acao.toLowerCase();
                const acaoIcon = opp.acao === 'COMPRA' ? 'fa-arrow-up text-success' :
                                opp.acao === 'VENDA' ? 'fa-arrow-down text-danger' : 'fa-eye text-warning';

                html += `
                    <div class="oportunidade-card ${acaoClass} card">
                        <div class="card-body py-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="mb-0">
                                        <i class="fas ${acaoIcon}"></i> ${opp.ativo} - ${opp.acao}
                                    </h6>
                                    <small class="text-muted">Prob: ${opp.probabilidade}% | R/R: ${opp.risk_reward}</small>
                                </div>
                                <div class="text-end">
                                    <small class="badge bg-${opp.prioridade === 'ALTA' ? 'danger' : opp.prioridade === 'MEDIA' ? 'warning' : 'info'}">
                                        ${opp.prioridade}
                                    </small>
                                    <br>
                                    <small class="text-muted">${new Date(opp.timestamp).toLocaleTimeString()}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        function atualizarAlertas(data) {
            const container = document.getElementById('alertas-lista');

            if (data.error) {
                container.innerHTML = `<div class="text-danger">Erro: ${data.error}</div>`;
                return;
            }

            if (!data.length) {
                container.innerHTML = '<div class="text-muted">Nenhum alerta recente</div>';
                return;
            }

            let html = '';
            data.forEach(alerta => {
                html += `
                    <div class="border-bottom pb-2 mb-2">
                        <div class="d-flex justify-content-between">
                            <span><strong>${alerta.ativo}</strong> - ${alerta.acao}</span>
                            <small class="text-muted">${new Date(alerta.timestamp).toLocaleString()}</small>
                        </div>
                        <div class="d-flex justify-content-between">
                            <small>Prob: ${alerta.probabilidade}% | Conf: ${alerta.confianca}%</small>
                            <small>Canais: ${alerta.canais.length}</small>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        function atualizarPerformance(data) {
            const container = document.getElementById('performance-metricas');

            if (data.error) {
                container.innerHTML = `<div class="text-danger">Erro: ${data.error}</div>`;
                return;
            }

            container.innerHTML = `
                <div class="row">
                    <div class="col-6">
                        <h6>Alertas (30d)</h6>
                        <p class="mb-1">${data.alertas_30d.total} total</p>
                        <p class="mb-1">${data.alertas_30d.enviados} enviados</p>
                        <p class="mb-0">Taxa: ${data.alertas_30d.taxa_envio.toFixed(1)}%</p>
                    </div>
                    <div class="col-6">
                        <h6>Qualidade Média</h6>
                        <p class="mb-1">Prob: ${data.alertas_30d.probabilidade_media.toFixed(0)}%</p>
                        <p class="mb-0">Conf: ${data.alertas_30d.confianca_media.toFixed(0)}%</p>
                    </div>
                </div>
            `;
        }

        function atualizarStatusSistemas(data) {
            const container = document.getElementById('sistemas-status');

            if (data.error) {
                container.innerHTML = `<div class="text-danger">Erro: ${data.error}</div>`;
                return;
            }

            let html = '<div class="row">';
            for (const [sistema, status] of Object.entries(data.sistemas)) {
                const statusClass = status ? 'status-online' : 'status-offline';
                const statusIcon = status ? 'fa-check-circle' : 'fa-times-circle';
                const statusText = status ? 'Online' : 'Offline';

                html += `
                    <div class="col-md-2 col-4 mb-2">
                        <div class="text-center">
                            <i class="fas ${statusIcon} ${statusClass} fa-2x"></i>
                            <h6 class="mt-2">${sistema.replace('_', ' ').toUpperCase()}</h6>
                            <small>${statusText}</small>
                        </div>
                    </div>
                `;
            }
            html += `
                <div class="col-12 mt-3">
                    <small class="text-muted">Uptime: ${data.uptime} | Última verificação: ${new Date(data.timestamp).toLocaleTimeString()}</small>
                </div>
            </div>`;

            container.innerHTML = html;
        }

        // Inicializar dashboard
        document.addEventListener('DOMContentLoaded', function() {
            atualizarDados();

            // Atualizar a cada 30 segundos
            updateInterval = setInterval(atualizarDados, 30000);
        });
    </script>
</body>
</html>'''

    # Salvar template
    os.makedirs('web/templates', exist_ok=True)
    with open('web/templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

def main():
    """Função principal para executar o dashboard"""

    # Criar templates se não existirem
    criar_templates()

    # Inicializar dashboard
    dashboard = DashboardMercadoFinanceiro()

    # Executar servidor
    dashboard.executar(host='127.0.0.1', port=5000, debug=True)

if __name__ == "__main__":
    main()