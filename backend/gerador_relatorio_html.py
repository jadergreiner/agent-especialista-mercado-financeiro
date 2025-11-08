"""
Gerador de Relatório HTML para Avaliação de Portfólio
Gera visualização HTML interativa e moderna das recomendações
"""

from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import webbrowser


class GeradorRelatorioHTML:
    """Gera relatórios HTML para avaliação de portfólio"""

    def __init__(self):
        self.output_dir = Path("relatorios/html")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def gerar_html_completo(
        self,
        resumo_portfolio: Dict,
        analise_risco: Any,
        macro_coerencia: Dict,
        correlacoes: Dict,
        recomendacoes: Dict
    ) -> str:
        """Gera HTML completo do relatório"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_relatorio_{timestamp}.html"
        filepath = self.output_dir / filename

        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💼 Relatório de Portfólio - {datetime.now().strftime("%d/%m/%Y %H:%M")}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .header .timestamp {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 40px;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .section-title {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}

        .stat-value.positive {{
            color: #10b981;
        }}

        .stat-value.negative {{
            color: #ef4444;
        }}

        .stat-value.neutral {{
            color: #f59e0b;
        }}

        .alert-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            margin-left: 10px;
        }}

        .alert-alto {{
            background: #fee2e2;
            color: #dc2626;
        }}

        .alert-medio {{
            background: #fef3c7;
            color: #d97706;
        }}

        .alert-baixo {{
            background: #d1fae5;
            color: #059669;
        }}

        .recomendacoes-list {{
            list-style: none;
            margin-top: 20px;
        }}

        .recomendacao-item {{
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}

        .recomendacao-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .recomendacao-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .recomendacao-titulo {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }}

        .recomendacao-badge {{
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
        }}

        .badge-gestao {{
            background: #dbeafe;
            color: #1e40af;
        }}

        .badge-oportunidade {{
            background: #d1fae5;
            color: #065f46;
        }}

        .badge-risco {{
            background: #fee2e2;
            color: #991b1b;
        }}

        .badge-balanceamento {{
            background: #fef3c7;
            color: #92400e;
        }}

        .recomendacao-descricao {{
            color: #666;
            line-height: 1.6;
            margin-top: 10px;
        }}

        .confianca-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9em;
            color: #666;
            margin-top: 10px;
        }}

        .exposicao-moeda {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 15px;
        }}

        .moeda-card {{
            flex: 1;
            min-width: 150px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .moeda-symbol {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}

        .moeda-value {{
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 5px;
        }}

        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e5e7eb;
        }}

        .disclaimer {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
        }}

        .tab-container {{
            margin-top: 20px;
        }}

        .tab-buttons {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .tab-button {{
            padding: 12px 24px;
            background: white;
            border: 2px solid #667eea;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            color: #667eea;
            transition: all 0.3s;
        }}

        .tab-button:hover {{
            background: #667eea;
            color: white;
        }}

        .tab-button.active {{
            background: #667eea;
            color: white;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
            .recomendacao-item {{
                page-break-inside: avoid;
            }}
        }}

        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            .header h1 {{
                font-size: 1.8em;
            }}
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💼 Relatório de Avaliação de Portfólio</h1>
            <div class="timestamp">📅 {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}</div>
        </div>

        <div class="content">
            {self._gerar_secao_resumo(resumo_portfolio)}
            {self._gerar_secao_risco(analise_risco)}
            {self._gerar_secao_macro(macro_coerencia)}
            {self._gerar_secao_correlacao(correlacoes)}
            {self._gerar_secao_recomendacoes(recomendacoes)}
        </div>

        <div class="footer">
            <div class="disclaimer">
                ⚠️ <strong>DISCLAIMER:</strong> Este relatório é gerado automaticamente para fins educacionais e informativos.
                Sempre considere seu perfil de risco e consulte um profissional antes de tomar decisões de investimento.
            </div>
            <p>Gerado por: <strong>Sistema de Gestão de Fundos</strong> | Versão 1.0</p>
            <p>© 2025 - Todos os direitos reservados</p>
        </div>
    </div>

    <script>
        // Animação de entrada
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.stat-card, .recomendacao-item');
            cards.forEach((card, index) => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {{
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }}, index * 50);
            }});

            // Sistema de tabs
            const tabButtons = document.querySelectorAll('.tab-button');
            const tabContents = document.querySelectorAll('.tab-content');

            tabButtons.forEach(button => {{
                button.addEventListener('click', () => {{
                    const targetTab = button.dataset.tab;

                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabContents.forEach(content => content.classList.remove('active'));

                    button.classList.add('active');
                    document.getElementById(targetTab).classList.add('active');
                }});
            }});

            // Ativar primeira tab
            if (tabButtons.length > 0) {{
                tabButtons[0].click();
            }}
        }});
    </script>
</body>
</html>"""

        # Salvar arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(filepath.absolute())

    def _gerar_secao_resumo(self, resumo: Dict) -> str:
        """Gera seção de resumo do portfólio"""

        pnl_total = resumo.get('pnl_total', 0)
        pnl_percent = resumo.get('pnl_percent', 0)
        pnl_class = 'positive' if pnl_total >= 0 else 'negative'
        pnl_icon = '📈' if pnl_total >= 0 else '📉'

        return f"""
        <div class="section">
            <div class="section-title">
                📊 Resumo do Portfólio
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">💰 Capital Total</div>
                    <div class="stat-value">${resumo.get('capital_total', 0):,.2f}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">📊 Posições Ativas</div>
                    <div class="stat-value">{resumo.get('posicoes_ativas', 0)}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">{pnl_icon} P&L Total</div>
                    <div class="stat-value {pnl_class}">
                        ${pnl_total:,.2f}
                        <div style="font-size: 0.6em; margin-top: 5px;">({pnl_percent:+.2f}%)</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">💎 Exposição Total</div>
                    <div class="stat-value">${resumo.get('exposicao_total', 0):,.2f}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">⚖️ Alavancagem</div>
                    <div class="stat-value neutral">{resumo.get('alavancagem', 0):.2f}x</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">💵 P&L Não Realizado</div>
                    <div class="stat-value {pnl_class}">${resumo.get('pnl_nao_realizado', 0):,.2f}</div>
                </div>
            </div>

            <div style="margin-top: 30px;">
                <h3 style="color: #667eea; margin-bottom: 15px;">💱 Exposição por Moeda</h3>
                <div class="exposicao-moeda">
                    {self._gerar_cards_moedas(resumo.get('exposicao_moedas', {}))}
                </div>
            </div>
        </div>
        """

    def _gerar_cards_moedas(self, exposicao: Dict) -> str:
        """Gera cards de exposição por moeda"""
        cards = []
        for moeda, valor in sorted(exposicao.items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
            valor_class = 'positive' if valor >= 0 else 'negative'
            simbolo = '+' if valor >= 0 else ''
            cards.append(f"""
                <div class="moeda-card">
                    <div class="moeda-symbol">{moeda}</div>
                    <div class="moeda-value {valor_class}">{simbolo}${valor:,.0f}</div>
                </div>
            """)
        return ''.join(cards)

    def _gerar_secao_risco(self, analise_risco: Any) -> str:
        """Gera seção de análise de risco"""

        if not analise_risco:
            return ""

        nivel_alerta = getattr(analise_risco, 'nivel_alerta', 'DESCONHECIDO')
        alert_class = {
            'ALTO': 'alert-alto',
            'MEDIO': 'alert-medio',
            'BAIXO': 'alert-baixo'
        }.get(nivel_alerta, 'alert-medio')

        concentracao = getattr(analise_risco, 'concentracao_maxima', 0)
        moeda_concentrada = getattr(analise_risco, 'moeda_concentrada', 'N/A')
        correlacao_max = getattr(analise_risco, 'correlacao_maxima', 0)
        var_95 = getattr(analise_risco, 'var_95', 0)

        return f"""
        <div class="section">
            <div class="section-title">
                🛡️ Análise de Risco
                <span class="alert-badge {alert_class}">{nivel_alerta}</span>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">📊 Concentração Máxima</div>
                    <div class="stat-value neutral">{concentracao:.1f}%</div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">em {moeda_concentrada}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(concentracao, 100)}%"></div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">🔗 Correlação Máxima</div>
                    <div class="stat-value">{correlacao_max:.2f}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">📉 VaR (95%)</div>
                    <div class="stat-value negative">${var_95:,.2f}</div>
                </div>
            </div>

            {self._gerar_recomendacoes_risco(analise_risco)}
        </div>
        """

    def _gerar_recomendacoes_risco(self, analise_risco: Any) -> str:
        """Gera lista de recomendações de risco"""
        recomendacoes = getattr(analise_risco, 'recomendacoes', [])

        if not recomendacoes:
            return ""

        items = []
        for rec in recomendacoes:
            items.append(f"""
                <div class="recomendacao-item" style="border-left-color: #ef4444;">
                    <div class="recomendacao-descricao">⚠️ {rec}</div>
                </div>
            """)

        return f"""
            <div style="margin-top: 25px;">
                <h3 style="color: #667eea; margin-bottom: 15px;">🎯 Recomendações de Risco</h3>
                {''.join(items)}
            </div>
        """

    def _gerar_secao_macro(self, macro: Dict) -> str:
        """Gera seção de coerência macroeconômica"""

        if not macro:
            return ""

        vix = macro.get('vix', 0)
        dxy = macro.get('dxy', 0)
        cenario = macro.get('cenario', 'DESCONHECIDO')
        alinhamento = macro.get('alinhamento', 'DESCONHECIDO')

        return f"""
        <div class="section">
            <div class="section-title">
                🌐 Coerência Macroeconômica
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">📊 VIX (Volatilidade)</div>
                    <div class="stat-value">{vix:.1f}</div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                        {self._classificar_volatilidade(vix)}
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">💵 DXY (Índice Dólar)</div>
                    <div class="stat-value">{dxy:.1f}</div>
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                        {self._classificar_dxy(dxy)}
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">🎯 Cenário de Mercado</div>
                    <div class="stat-value" style="font-size: 1.5em;">{cenario}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">✅ Alinhamento do Portfólio</div>
                    <div class="stat-value {'positive' if alinhamento == 'COERENTE' else 'negative'}" style="font-size: 1.5em;">
                        {alinhamento}
                    </div>
                </div>
            </div>
        </div>
        """

    def _classificar_volatilidade(self, vix: float) -> str:
        """Classifica nível de volatilidade"""
        if vix < 12:
            return "Volatilidade BAIXA"
        elif vix < 20:
            return "Volatilidade MODERADA"
        else:
            return "Volatilidade ELEVADA"

    def _classificar_dxy(self, dxy: float) -> str:
        """Classifica força do dólar"""
        if dxy < 95:
            return "USD FRACO"
        elif dxy < 105:
            return "USD NEUTRO"
        else:
            return "USD FORTE"

    def _gerar_secao_correlacao(self, correlacoes: Dict) -> str:
        """Gera seção de análise de correlação"""

        if not correlacoes:
            return ""

        redundantes = correlacoes.get('exposicoes_redundantes', [])
        pares_unicos = correlacoes.get('pares_unicos', 0)

        return f"""
        <div class="section">
            <div class="section-title">
                🔗 Análise de Correlação
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">📊 Pares Únicos</div>
                    <div class="stat-value">{pares_unicos}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">⚠️ Exposições Redundantes</div>
                    <div class="stat-value neutral">{len(redundantes)}</div>
                </div>
            </div>

            {self._gerar_lista_redundantes(redundantes)}
        </div>
        """

    def _gerar_lista_redundantes(self, redundantes: List) -> str:
        """Gera lista de exposições redundantes"""
        if not redundantes:
            return "<p style='color: #10b981; font-weight: bold; margin-top: 20px;'>✅ Nenhuma exposição redundante detectada</p>"

        items = ', '.join(redundantes)
        return f"""
            <div style="margin-top: 20px;">
                <p style="color: #666;"><strong>Moedas com exposição redundante:</strong></p>
                <p style="background: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 10px; color: #92400e;">
                    {items}
                </p>
            </div>
        """

    def _gerar_secao_recomendacoes(self, recomendacoes: Dict) -> str:
        """Gera seção de recomendações"""

        if not recomendacoes or not recomendacoes.get('detalhes'):
            return ""

        detalhes = recomendacoes['detalhes']

        return f"""
        <div class="section">
            <div class="section-title">
                💡 Recomendações Inteligentes
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">📋 Gestão de Posições</div>
                    <div class="stat-value">{len(detalhes.get('posicoes_existentes', []))}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">🆕 Novas Oportunidades</div>
                    <div class="stat-value positive">{len(detalhes.get('novas_oportunidades', []))}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">🛡️ Alertas de Risco</div>
                    <div class="stat-value negative">{len(detalhes.get('gestao_risco', []))}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">⚖️ Balanceamento</div>
                    <div class="stat-value neutral">{len(detalhes.get('balanceamento', []))}</div>
                </div>
            </div>

            {self._gerar_tabs_recomendacoes(detalhes)}
        </div>
        """

    def _gerar_tabs_recomendacoes(self, detalhes: Dict) -> str:
        """Gera sistema de tabs para recomendações"""

        posicoes = detalhes.get('posicoes_existentes', [])
        oportunidades = detalhes.get('novas_oportunidades', [])
        riscos = detalhes.get('gestao_risco', [])
        balanceamento = detalhes.get('balanceamento', [])

        return f"""
        <div class="tab-container">
            <div class="tab-buttons">
                <button class="tab-button" data-tab="tab-posicoes">
                    📋 Gestão de Posições ({len(posicoes)})
                </button>
                <button class="tab-button" data-tab="tab-oportunidades">
                    🆕 Novas Oportunidades ({len(oportunidades)})
                </button>
                <button class="tab-button" data-tab="tab-riscos">
                    🛡️ Alertas de Risco ({len(riscos)})
                </button>
                <button class="tab-button" data-tab="tab-balanceamento">
                    ⚖️ Balanceamento ({len(balanceamento)})
                </button>
            </div>

            <div id="tab-posicoes" class="tab-content">
                {self._gerar_lista_recomendacoes(posicoes, 'gestao')}
            </div>

            <div id="tab-oportunidades" class="tab-content">
                {self._gerar_lista_recomendacoes(oportunidades, 'oportunidade')}
            </div>

            <div id="tab-riscos" class="tab-content">
                {self._gerar_lista_recomendacoes(riscos, 'risco')}
            </div>

            <div id="tab-balanceamento" class="tab-content">
                {self._gerar_lista_recomendacoes(balanceamento, 'balanceamento')}
            </div>
        </div>
        """

    def _gerar_lista_recomendacoes(self, recomendacoes: List, tipo: str) -> str:
        """Gera lista de recomendações"""

        if not recomendacoes:
            return "<p style='color: #666; padding: 20px;'>Nenhuma recomendação disponível nesta categoria.</p>"

        items = []
        for i, rec in enumerate(recomendacoes, 1):
            if isinstance(rec, str):
                # Recomendação em formato string
                items.append(f"""
                    <div class="recomendacao-item">
                        <div class="recomendacao-header">
                            <div class="recomendacao-titulo">#{i}</div>
                            <span class="recomendacao-badge badge-{tipo}">{tipo.upper()}</span>
                        </div>
                        <div class="recomendacao-descricao">{rec}</div>
                    </div>
                """)
            else:
                # Recomendação em formato dataclass
                ativo = getattr(rec, 'ativo', 'N/A')
                razao = getattr(rec, 'razao', 'Sem descrição')
                nivel = getattr(rec, 'nivel_confianca', 'N/A')
                preco = getattr(rec, 'preco_sugerido', None)
                risco = getattr(rec, 'risco_estimado', None)

                # Novos campos para posições existentes
                ticket = getattr(rec, 'ticket', None)
                entry_date = getattr(rec, 'entry_date', None)
                entry_price = getattr(rec, 'entry_price', None)
                partial_results = getattr(rec, 'partial_results', None)
                direction = getattr(rec, 'direction', None)

                # Título com ticket se disponível
                titulo = f"#{i} - {ativo}"
                if ticket:
                    titulo = f"#{i} - {ativo} | 🎫 Ticket: {ticket}"

                # Informações da posição existente
                info_posicao = ""
                if entry_date or entry_price:
                    info_posicao = "<div style='margin-top: 15px; padding: 15px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #667eea;'>"

                    if direction:
                        direction_emoji = "📈" if direction == "LONG" else "📉"
                        direction_color = "#10b981" if direction == "LONG" else "#ef4444"
                        info_posicao += f"<div style='color: {direction_color}; font-weight: bold; margin-bottom: 8px;'>{direction_emoji} Direção: {direction}</div>"

                    if entry_date:
                        info_posicao += f"<div style='color: #666; margin-bottom: 5px;'>📅 Data de Abertura: <strong>{entry_date}</strong></div>"

                    if entry_price is not None:
                        info_posicao += f"<div style='color: #666; margin-bottom: 5px;'>🔵 Preço de Entrada: <strong>${entry_price:.5f}</strong></div>"

                    if preco is not None:
                        info_posicao += f"<div style='color: #666; margin-bottom: 5px;'>🔴 Preço Atual: <strong>${preco:.5f}</strong></div>"

                        # Calcular variação percentual
                        if entry_price and entry_price > 0:
                            variacao_pct = ((preco - entry_price) / entry_price) * 100
                            variacao_color = "#10b981" if variacao_pct >= 0 else "#ef4444"
                            variacao_emoji = "📈" if variacao_pct >= 0 else "📉"
                            info_posicao += f"<div style='color: {variacao_color}; font-weight: bold; margin-bottom: 5px;'>{variacao_emoji} Variação: {variacao_pct:+.2f}%</div>"

                    if partial_results is not None:
                        result_color = "#10b981" if partial_results >= 0 else "#ef4444"
                        result_emoji = "✅" if partial_results >= 0 else "❌"
                        info_posicao += f"<div style='color: {result_color}; font-weight: bold; font-size: 1.1em; margin-top: 8px;'>{result_emoji} P&L: ${partial_results:+,.2f}</div>"

                    info_posicao += "</div>"

                preco_html = f"<div style='margin-top: 10px; color: #10b981; font-weight: bold;'>💰 Preço Sugerido: ${preco:.2f}</div>" if preco and not entry_price else ""
                risco_html = f"<div style='margin-top: 10px; color: #ef4444; font-weight: bold;'>🚨 Risco: {risco:.1f}%</div>" if risco and risco > 0 else ""

                items.append(f"""
                    <div class="recomendacao-item">
                        <div class="recomendacao-header">
                            <div class="recomendacao-titulo">{titulo}</div>
                            <span class="recomendacao-badge badge-{tipo}">{tipo.upper()}</span>
                        </div>
                        <div class="recomendacao-descricao">{razao}</div>
                        {info_posicao}
                        <div class="confianca-indicator">
                            🎯 Confiança: <strong>{nivel}</strong>
                        </div>
                        {preco_html}
                        {risco_html}
                    </div>
                """)

        return f"""
            <ul class="recomendacoes-list">
                {''.join(items)}
            </ul>
        """

    def abrir_no_navegador(self, filepath: str):
        """Abre o relatório HTML no navegador padrão"""
        webbrowser.open(f'file://{filepath}')


if __name__ == "__main__":
    print("🚀 Gerador de Relatório HTML inicializado")
    print("Use este módulo através do script avaliar_portfolio_html.py")
