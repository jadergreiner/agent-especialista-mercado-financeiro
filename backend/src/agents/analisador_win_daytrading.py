"""
Analisador WIN Day Trading
Sistema completo de análise para day trading do Mini Índice Brasileiro (WIN)
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.gerenciador_modelos import gerenciador_modelos
# Persistência
try:
    from persistencia.recomendacoes import (
        inicializar_banco,
        salvar_recomendacao,
    )
except Exception:
    inicializar_banco = None
    salvar_recomendacao = None


class PontuacaoMacro:
    """Sistema de pontuação macro para avaliar cenário de mercado"""

    def __init__(self):
        self.pontos_tecnico = {}
        self.pontos_macro_global = {}
        self.pontos_macro_brasil = {}
        self.pontos_noticias_brasil = []
        self.pontos_noticias_globais = []

    def adicionar_ponto_tecnico(self, categoria: str, pontos: int, justificativa: str):
        """Adiciona ponto técnico (-1, 0, +1)"""
        self.pontos_tecnico[categoria] = {
            'pontos': pontos,
            'justificativa': justificativa
        }

    def adicionar_ponto_macro_global(self, indicador: str, pontos: int, justificativa: str):
        """Adiciona ponto macro global (-1, 0, +1)"""
        self.pontos_macro_global[indicador] = {
            'pontos': pontos,
            'justificativa': justificativa
        }

    def adicionar_ponto_macro_brasil(self, indicador: str, pontos: int, justificativa: str):
        """Adiciona ponto macro Brasil (-1, 0, +1)"""
        self.pontos_macro_brasil[indicador] = {
            'pontos': pontos,
            'justificativa': justificativa
        }

    def adicionar_noticia_brasil(self, titulo: str, pontos: int, impacto: str):
        """Adiciona notícia Brasil"""
        self.pontos_noticias_brasil.append({
            'titulo': titulo,
            'pontos': pontos,
            'impacto': impacto
        })

    def adicionar_noticia_global(self, titulo: str, pontos: int, impacto: str):
        """Adiciona notícia global"""
        self.pontos_noticias_globais.append({
            'titulo': titulo,
            'pontos': pontos,
            'impacto': impacto
        })

    def calcular_saldo_total(self) -> Dict[str, Any]:
        """Calcula saldo total e retorna análise completa"""
        soma_tecnico = sum(item['pontos'] for item in self.pontos_tecnico.values())
        soma_macro_global = sum(item['pontos'] for item in self.pontos_macro_global.values())
        soma_macro_brasil = sum(item['pontos'] for item in self.pontos_macro_brasil.values())
        soma_noticias_br = sum(item['pontos'] for item in self.pontos_noticias_brasil)
        soma_noticias_global = sum(item['pontos'] for item in self.pontos_noticias_globais)

        saldo_total = (soma_tecnico + soma_macro_global + soma_macro_brasil +
                      soma_noticias_br + soma_noticias_global)

        # Interpretação do saldo
        if saldo_total >= 5:
            interpretacao = "FORTEMENTE FAVORÁVEL"
            emoji = "🟢"
        elif 2 <= saldo_total < 5:
            interpretacao = "FAVORÁVEL"
            emoji = "🟢"
        elif -2 < saldo_total < 2:
            interpretacao = "NEUTRO"
            emoji = "🟡"
        elif -5 < saldo_total <= -2:
            interpretacao = "DESFAVORÁVEL"
            emoji = "🔴"
        else:
            interpretacao = "FORTEMENTE DESFAVORÁVEL"
            emoji = "🔴"

        return {
            'detalhamento': {
                'tecnico': soma_tecnico,
                'macro_global': soma_macro_global,
                'macro_brasil': soma_macro_brasil,
                'noticias_brasil': soma_noticias_br,
                'noticias_globais': soma_noticias_global
            },
            'saldo_total': saldo_total,
            'interpretacao': interpretacao,
            'emoji': emoji,
            'pontos_positivos': sum(1 for cat in [self.pontos_tecnico, self.pontos_macro_global,
                                                   self.pontos_macro_brasil]
                                   for item in cat.values() if item['pontos'] > 0) +
                              sum(1 for item in self.pontos_noticias_brasil + self.pontos_noticias_globais
                                  if item['pontos'] > 0),
            'pontos_negativos': sum(1 for cat in [self.pontos_tecnico, self.pontos_macro_global,
                                                   self.pontos_macro_brasil]
                                   for item in cat.values() if item['pontos'] < 0) +
                              sum(1 for item in self.pontos_noticias_brasil + self.pontos_noticias_globais
                                  if item['pontos'] < 0)
        }


class AnalisadorWinDayTrading:
    """
    Analisador completo para Day Trading do Mini Índice (WIN)

    Executa análise em 7 fases:
    1. Coleta de Dados
    2. Análise Técnica
    3. Análise Macroeconômica
    4. Análise de Notícias
    5. Sistema de Pontuação
    6. Relatório Executivo
    7. Plano de Trading
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa analisador

        Args:
            config: Configuração opcional com parâmetros da operação
        """
        self.config = config or self._config_padrao()
        self.gerenciador_modelos = gerenciador_modelos
        self.pontuacao = PontuacaoMacro()

    def _config_padrao(self) -> Dict:
        """Retorna configuração padrão"""
        return {
            'instrumento': 'WIN',
            'contratos_inicio': 1,
            'contratos_max': 10,
            'meta_lucro': 1000.00,
            'perfil_risco': 'conservador',
            'janela_analise_minutos': 120
        }

    def analisar(
        self,
        dados_adicionais: Optional[Dict] = None,
        persistir: bool = True,
        caminho_bd: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Executa análise completa do WIN

        Args:
            dados_adicionais: Dados/contexto adicional fornecido pelo usuário

        Returns:
            Dicionário com relatório executivo e plano de trading
        """
        print("🚀 Iniciando análise WIN Day Trading...")

        # FASE 1: Coleta de Dados
        print("\n📊 FASE 1: Coletando dados de mercado...")
        dados = self._coletar_dados()

        # FASE 2: Análise Técnica
        print("📈 FASE 2: Executando análise técnica...")
        analise_tecnica = self._analisar_tecnica(dados)

        # FASE 3: Análise Macroeconômica
        print("🌍 FASE 3: Analisando cenário macroeconômico...")
        analise_macro = self._analisar_macro()

        # FASE 4: Análise de Notícias
        print("📰 FASE 4: Coletando e analisando notícias...")
        noticias = self._analisar_noticias()

        # FASE 5: Sistema de Pontuação
        print("🎯 FASE 5: Calculando pontuação macro...")
        saldo = self.pontuacao.calcular_saldo_total()

        # FASE 6: Relatório Executivo
        print("📋 FASE 6: Gerando relatório executivo...")
        relatorio = self._gerar_relatorio_executivo(
            dados, analise_tecnica, analise_macro, noticias, saldo
        )

        # Checkpoint 1: Input adicional
        print("\n" + "="*70)
        print("🔍 CHECKPOINT 1")
        print("="*70)
        if dados_adicionais:
            print("✅ Processando informação adicional fornecida...")
            relatorio = self._processar_input_adicional(relatorio, dados_adicionais)
            saldo = self.pontuacao.calcular_saldo_total()

        # FASE 7: Plano de Trading
        print("\n💼 FASE 7: Gerando plano de trading...")
        plano = self._gerar_plano_trading(
            dados, analise_tecnica, saldo, relatorio
        )

        print("\n✅ Análise concluída!")

        resultado = {
            'timestamp': datetime.now().isoformat(),
            'dados_mercado': dados,
            'analise_tecnica': analise_tecnica,
            'analise_macro': analise_macro,
            'noticias': noticias,
            'pontuacao': saldo,
            'relatorio_executivo': relatorio,
            'plano_trading': plano,
            'status': 'concluido'
        }

        # Persistência da recomendação (se habilitado)
        if persistir and salvar_recomendacao is not None:
            try:
                if inicializar_banco is not None:
                    inicializar_banco(caminho_bd)
                id_rec = salvar_recomendacao(resultado, caminho_bd)
                resultado['id_recomendacao'] = id_rec
                print(f"\n🗄️  Recomendação salva no histórico (id={id_rec})")
            except Exception as e:
                print(f"\n⚠️  Falha ao salvar recomendação: {e}")

        return resultado

    def _coletar_dados(self) -> Dict:
        """
        FASE 1: Coleta dados de múltiplas fontes

        TODO: Integrar com APIs reais
        - TradingView
        - Investing.com
        - BrAPI
        - IbovFinancials
        - HG Brasil
        """
        import random

        # Gerar dados mock realistas
        preco_base = random.uniform(128000, 132000)

        dados_mock = {
            'cotacao': {
                'preco_atual': round(preco_base, 2),
                'variacao_dia_percent': round(random.uniform(-1.5, 1.5), 2),
                'variacao_dia_pontos': round(random.uniform(-1500, 1500)),
                'maxima_dia': round(preco_base * 1.008, 2),
                'minima_dia': round(preco_base * 0.992, 2),
                'volume_negociado': random.randint(80000, 150000),
                'horario': datetime.now().strftime("%H:%M:%S")
            },
            'niveis_historicos': {
                'semana': {
                    'maxima': round(preco_base * 1.015, 2),
                    'minima': round(preco_base * 0.985, 2)
                },
                'mes': {
                    'maxima': round(preco_base * 1.025, 2),
                    'minima': round(preco_base * 0.975, 2)
                },
                'periodo_52_semanas': {
                    'maxima': round(preco_base * 1.10, 2),
                    'minima': round(preco_base * 0.90, 2)
                }
            }
        }

        print(f"   Cotação atual: {dados_mock['cotacao']['preco_atual']} " +
              f"({dados_mock['cotacao']['variacao_dia_percent']:+.2f}%)")

        return dados_mock

    def _analisar_tecnica(self, dados: Dict) -> Dict:
        """
        FASE 2: Análise técnica completa

        Inclui:
        - Suportes e resistências
        - Análise de spread
        - Volume profile
        - Indicadores técnicos
        - Identificação de armadilhas
        """
        preco_atual = dados['cotacao']['preco_atual']

        # Calcular níveis técnicos
        suporte_1 = round(preco_atual * 0.995, 2)
        suporte_2 = round(preco_atual * 0.988, 2)
        suporte_3 = round(preco_atual * 0.980, 2)

        resistencia_1 = round(preco_atual * 1.005, 2)
        resistencia_2 = round(preco_atual * 1.012, 2)
        resistencia_3 = round(preco_atual * 1.020, 2)

        # Análise de spread (melhor risco/ganho)
        spread_compra = preco_atual - suporte_1
        spread_venda = resistencia_1 - preco_atual

        melhor_spread_direcao = "COMPRA" if spread_compra > spread_venda else "VENDA"
        melhor_spread_pontos = max(spread_compra, spread_venda)

        # Indicadores técnicos (mock)
        import random
        rsi = round(random.uniform(35, 65), 1)

        analise = {
            'tendencia': {
                'curto_prazo': random.choice(['alta', 'baixa', 'lateral']),
                'forca': random.randint(5, 9)
            },
            'suportes': {
                's1': suporte_1,
                's1_justificativa': 'Mínima do pregão anterior',
                's2': suporte_2,
                's2_justificativa': 'Zona de acumulação de volume',
                's3': suporte_3,
                's3_justificativa': 'Suporte semanal'
            },
            'resistencias': {
                'r1': resistencia_1,
                'r1_justificativa': 'Máxima do pregão anterior',
                'r2': resistencia_2,
                'r2_justificativa': 'Topo da semana',
                'r3': resistencia_3,
                'r3_justificativa': 'Resistência mensal'
            },
            'spread_analysis': {
                'spread_compra_pontos': round(spread_compra, 2),
                'spread_venda_pontos': round(spread_venda, 2),
                'melhor_spread_direcao': melhor_spread_direcao,
                'melhor_spread_pontos': round(melhor_spread_pontos, 2),
                'relacao_risco_ganho': round(melhor_spread_pontos / min(spread_compra, spread_venda), 2)
            },
            'indicadores': {
                'rsi': {
                    'valor': rsi,
                    'interpretacao': 'sobrevendido' if rsi < 40 else ('sobrecomprado' if rsi > 60 else 'neutro')
                },
                'macd': {
                    'interpretacao': random.choice(['alta', 'baixa', 'neutro'])
                },
                'atr': {
                    'valor': round(random.uniform(800, 1500), 2),
                    'classificacao': 'média'
                }
            }
        }

        # Adicionar pontos técnicos
        tendencia_ponto = 1 if analise['tendencia']['curto_prazo'] == 'alta' else (-1 if analise['tendencia']['curto_prazo'] == 'baixa' else 0)
        self.pontuacao.adicionar_ponto_tecnico(
            'tendencia',
            tendencia_ponto,
            f"Tendência de {analise['tendencia']['curto_prazo']} (força {analise['tendencia']['forca']}/10)"
        )

        # Spread favorece compra ou venda?
        spread_ponto = 1 if melhor_spread_direcao == 'COMPRA' else -1
        self.pontuacao.adicionar_ponto_tecnico(
            'spread',
            spread_ponto,
            f"Melhor spread em {melhor_spread_direcao} ({melhor_spread_pontos:.0f} pontos)"
        )

        # RSI
        rsi_ponto = -1 if rsi < 35 else (1 if rsi > 65 else 0)
        self.pontuacao.adicionar_ponto_tecnico(
            'rsi',
            rsi_ponto,
            f"RSI em {rsi} ({analise['indicadores']['rsi']['interpretacao']})"
        )

        print(f"   Tendência: {analise['tendencia']['curto_prazo'].upper()} " +
              f"(força {analise['tendencia']['forca']}/10)")
        print(f"   Melhor Spread: {melhor_spread_direcao} ({melhor_spread_pontos:.0f} pontos)")
        print(f"   RSI: {rsi}")

        return analise

    def _analisar_macro(self) -> Dict:
        """
        FASE 3: Análise macroeconômica

        Indicadores:
        - Globais: DXY, VIX, Ouro, Juros US, Emergentes
        - Brasil: Selic, IPCA, USD/BRL
        """
        import random

        # Mock de indicadores
        dxy_var = random.uniform(-0.5, 0.5)
        vix_val = random.uniform(12, 20)
        usdbrl_var = random.uniform(-1.0, 1.0)

        analise = {
            'indicadores_globais': {
                'dxy': {
                    'valor': round(103.5 + dxy_var, 2),
                    'variacao': round(dxy_var, 2),
                    'impacto': 'Dólar forte pressiona emergentes' if dxy_var > 0 else 'Dólar fraco favorece emergentes'
                },
                'vix': {
                    'valor': round(vix_val, 2),
                    'nivel': 'baixo' if vix_val < 15 else ('médio' if vix_val < 20 else 'alto'),
                    'impacto': 'Baixa volatilidade favorece risco' if vix_val < 15 else 'Alta volatilidade aumenta cautela'
                }
            },
            'indicadores_brasil': {
                'cambio': {
                    'usdbrl': round(5.0 + (usdbrl_var * 0.05), 3),
                    'variacao': round(usdbrl_var, 2),
                    'impacto': 'Dólar em alta pressiona Ibovespa' if usdbrl_var > 0 else 'Dólar em queda favorece Ibovespa'
                }
            }
        }

        # Adicionar pontos macro
        # DXY: subida é negativo para BR
        dxy_ponto = -1 if dxy_var > 0.3 else (1 if dxy_var < -0.3 else 0)
        self.pontuacao.adicionar_ponto_macro_global(
            'dxy',
            dxy_ponto,
            analise['indicadores_globais']['dxy']['impacto']
        )

        # VIX: alta é negativo
        vix_ponto = -1 if vix_val > 18 else (1 if vix_val < 13 else 0)
        self.pontuacao.adicionar_ponto_macro_global(
            'vix',
            vix_ponto,
            analise['indicadores_globais']['vix']['impacto']
        )

        # USD/BRL: alta é negativo para WIN
        usdbrl_ponto = -1 if usdbrl_var > 0.5 else (1 if usdbrl_var < -0.5 else 0)
        self.pontuacao.adicionar_ponto_macro_brasil(
            'usdbrl',
            usdbrl_ponto,
            analise['indicadores_brasil']['cambio']['impacto']
        )

        print(f"   DXY: {analise['indicadores_globais']['dxy']['valor']} " +
              f"({analise['indicadores_globais']['dxy']['variacao']:+.2f}%)")
        print(f"   VIX: {analise['indicadores_globais']['vix']['valor']} " +
              f"({analise['indicadores_globais']['vix']['nivel']})")
        print(f"   USD/BRL: {analise['indicadores_brasil']['cambio']['usdbrl']} " +
              f"({analise['indicadores_brasil']['cambio']['variacao']:+.2f}%)")

        return analise

    def _analisar_noticias(self) -> Dict:
        """
        FASE 4: Análise de notícias

        Coleta e classifica notícias:
        - Brasil
        - Globais relevantes
        """
        # Mock de notícias
        noticias_br = [
            {
                'titulo': 'Banco Central mantém Selic em 10.75%',
                'impacto': 'médio',
                'pontos': 0,
                'justificativa': 'Dentro do esperado pelo mercado'
            },
            {
                'titulo': 'PIB cresce 0.3% no trimestre',
                'impacto': 'alto',
                'pontos': 1,
                'justificativa': 'Crescimento acima do esperado favorece bolsa'
            }
        ]

        noticias_global = [
            {
                'titulo': 'Fed mantém juros estáveis',
                'impacto': 'médio',
                'pontos': 1,
                'justificativa': 'Reduz pressão sobre emergentes'
            }
        ]

        # Adicionar pontos de notícias
        for noticia in noticias_br:
            self.pontuacao.adicionar_noticia_brasil(
                noticia['titulo'],
                noticia['pontos'],
                noticia['impacto']
            )

        for noticia in noticias_global:
            self.pontuacao.adicionar_noticia_global(
                noticia['titulo'],
                noticia['pontos'],
                noticia['impacto']
            )

        print(f"   Notícias Brasil: {len(noticias_br)}")
        print(f"   Notícias Globais: {len(noticias_global)}")

        return {
            'brasil': noticias_br,
            'globais': noticias_global
        }

    def _gerar_relatorio_executivo(
        self,
        dados: Dict,
        analise_tecnica: Dict,
        analise_macro: Dict,
        noticias: Dict,
        saldo: Dict
    ) -> Dict:
        """FASE 6: Gera relatório executivo sumarizado"""

        preco = dados['cotacao']['preco_atual']
        variacao = dados['cotacao']['variacao_dia_percent']

        relatorio = {
              'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'cotacao_atual': f"{preco:,.2f}",
            'variacao_dia': f"{variacao:+.2f}%",
            'sintese': {
                'tendencia': analise_tecnica['tendencia']['curto_prazo'].upper(),
                'melhor_spread': analise_tecnica['spread_analysis']['melhor_spread_direcao'],
                'pontos_spread': analise_tecnica['spread_analysis']['melhor_spread_pontos'],
                'saldo_macro': f"{saldo['saldo_total']:+d} - {saldo['interpretacao']} {saldo['emoji']}"
            },
            'detalhamento': saldo['detalhamento'],
            'recomendacao_preliminar': self._determinar_direcao(analise_tecnica, saldo)
        }

        return relatorio

    def _determinar_direcao(self, analise_tecnica: Dict, saldo: Dict) -> str:
        """Determina direção recomendada baseada em análise e saldo"""

        # Spread indica melhor lado
        direcao_spread = analise_tecnica['spread_analysis']['melhor_spread_direcao']

        # Saldo macro
        saldo_total = saldo['saldo_total']

        # Lógica de decisão
        if saldo_total >= 3:
            return direcao_spread  # Saldo favorável, segue spread
        elif saldo_total <= -3:
            return "AGUARDAR"  # Saldo desfavorável
        else:
            # Neutro, depende da força do spread
            relacao = analise_tecnica['spread_analysis']['relacao_risco_ganho']
            return direcao_spread if relacao > 2 else "AGUARDAR"

    def _gerar_plano_trading(
        self,
        dados: Dict,
        analise_tecnica: Dict,
        saldo: Dict,
        relatorio: Dict
    ) -> Dict:
        """FASE 7: Gera plano de trading estruturado"""

        direcao = relatorio['recomendacao_preliminar']
        preco_atual = dados['cotacao']['preco_atual']

        if direcao == "AGUARDAR":
            return {
                'direcao': 'AGUARDAR',
                'confianca': 0,
                'justificativa': 'Cenário não oferece relação risco/ganho favorável no momento',
                'sugestao': 'Aguardar melhores condições ou definição de tendência'
            }

        # Gerar plano de compra ou venda
        if direcao == "COMPRA":
            entrada = round(preco_atual * 0.999, 2)
            reforco_1 = analise_tecnica['suportes']['s1']
            reforco_2 = analise_tecnica['suportes']['s2']
            stop = round(analise_tecnica['suportes']['s2'] * 0.997, 2)
            tp1 = analise_tecnica['resistencias']['r1']
            tp2 = analise_tecnica['resistencias']['r2']
            tp3 = analise_tecnica['resistencias']['r3']
        else:  # VENDA
            entrada = round(preco_atual * 1.001, 2)
            reforco_1 = analise_tecnica['resistencias']['r1']
            reforco_2 = analise_tecnica['resistencias']['r2']
            stop = round(analise_tecnica['resistencias']['r2'] * 1.003, 2)
            tp1 = analise_tecnica['suportes']['s1']
            tp2 = analise_tecnica['suportes']['s2']
            tp3 = analise_tecnica['suportes']['s3']

        # Calcular risco e retorno (pontos no WIN = R$ por contrato)
        risco_pontos = abs(entrada - stop)
        retorno_tp1 = abs(tp1 - entrada)
        retorno_tp2 = abs(tp2 - entrada)
        retorno_tp3 = abs(tp3 - entrada)

        # WIN: 1 ponto = R$ 0.20
        risco_reais = risco_pontos * 0.20 * self.config['contratos_inicio']
        lucro_potencial = (retorno_tp1 * 3 + retorno_tp2 * 2 + retorno_tp3) * 0.20

        plano = {
            'valido_ate': (datetime.now() + timedelta(minutes=self.config['janela_analise_minutos'])).strftime("%H:%M"),
            'direcao': direcao,
            'confianca': min(10, max(1, 5 + saldo['saldo_total'])),
            'entrada_inicial': {
                'preco': entrada,
                'contratos': self.config['contratos_inicio'],
                'justificativa': f"Entrada próxima ao preço atual, {direcao.lower()} no melhor spread"
            },
            'reforcos': [
                {
                    'preco': reforco_1,
                    'contratos': 2,
                    'justificativa': f"Primeiro suporte/resistência - zona de liquidez"
                },
                {
                    'preco': reforco_2,
                    'contratos': 3,
                    'justificativa': f"Segundo nível - ponto de acumulação histórica"
                }
            ],
            'gestao_saida': {
                'stop_loss': {
                    'preco': stop,
                    'justificativa': 'Abaixo/acima do segundo nível técnico'
                },
                'take_profit': [
                    {
                        'objetivo': 1,
                        'preco': tp1,
                        'contratos': 3,
                        'lucro_estimado': round(retorno_tp1 * 3 * 0.20, 2)
                    },
                    {
                        'objetivo': 2,
                        'preco': tp2,
                        'contratos': 2,
                        'lucro_estimado': round(retorno_tp2 * 2 * 0.20, 2)
                    },
                    {
                        'objetivo': 3,
                        'preco': tp3,
                        'contratos': 1,
                        'lucro_estimado': round(retorno_tp3 * 0.20, 2)
                    }
                ]
            },
            'resumo_risco': {
                'risco_maximo': round(risco_reais, 2),
                'potencial_lucro': round(lucro_potencial, 2),
                'relacao_risco_retorno': round(lucro_potencial / risco_reais, 2) if risco_reais > 0 else 0,
                'percentual_meta': round((lucro_potencial / self.config['meta_lucro']) * 100, 1)
            }
        }

        return plano

    def _processar_input_adicional(self, relatorio: Dict, input_adicional: Dict) -> Dict:
        """Processa informação adicional do usuário e atualiza análise"""

        print(f"\n   📝 Processando: {input_adicional.get('descricao', 'Nova informação')}")

        # Avaliar impacto
        impacto_pontos = input_adicional.get('pontos', 0)
        categoria = input_adicional.get('categoria', 'outros')

        if categoria == 'noticia_brasil':
            self.pontuacao.adicionar_noticia_brasil(
                input_adicional.get('descricao', ''),
                impacto_pontos,
                input_adicional.get('impacto', 'médio')
            )
        elif categoria == 'noticia_global':
            self.pontuacao.adicionar_noticia_global(
                input_adicional.get('descricao', ''),
                impacto_pontos,
                input_adicional.get('impacto', 'médio')
            )

        print(f"   Impacto: {impacto_pontos:+d} pontos")

        # Recalcular saldo
        novo_saldo = self.pontuacao.calcular_saldo_total()
        relatorio['sintese']['saldo_macro'] = f"{novo_saldo['saldo_total']:+d} - {novo_saldo['interpretacao']} {novo_saldo['emoji']}"

        return relatorio

    def formatar_relatorio(self, resultado: Dict) -> str:
        """Formata resultado em texto legível"""

        rel = resultado['relatorio_executivo']
        plano = resultado['plano_trading']
        pontuacao = resultado['pontuacao']

        linhas = []
        linhas.append("\n" + "="*70)
        linhas.append("📊 RELATÓRIO EXECUTIVO - WIN DAY TRADE")
        linhas.append("="*70)
        linhas.append(f"⏰ {rel['timestamp']}")
        linhas.append(f"💰 WIN: {rel['cotacao_atual']} ({rel['variacao_dia']})")
        linhas.append("")

        linhas.append("🎯 VISÃO TÉCNICA")
        linhas.append(f"  Tendência: {rel['sintese']['tendencia']}")
        linhas.append(f"  Melhor Spread: {rel['sintese']['melhor_spread']} ({rel['sintese']['pontos_spread']:.0f} pontos)")
        linhas.append("")

        linhas.append("📈 SALDO MACRO")
        linhas.append(f"  Técnico: {pontuacao['detalhamento']['tecnico']:+d}")
        linhas.append(f"  Macro Global: {pontuacao['detalhamento']['macro_global']:+d}")
        linhas.append(f"  Macro Brasil: {pontuacao['detalhamento']['macro_brasil']:+d}")
        linhas.append(f"  Notícias: {pontuacao['detalhamento']['noticias_brasil'] + pontuacao['detalhamento']['noticias_globais']:+d}")
        linhas.append(f"  ▶ TOTAL: {rel['sintese']['saldo_macro']}")
        linhas.append("")

        linhas.append("💼 PLANO DE TRADING")
        linhas.append(f"  Direção: {plano['direcao']}")

        if plano['direcao'] != 'AGUARDAR':
            linhas.append(f"  Confiança: {plano['confianca']}/10")
            linhas.append(f"  Válido até: {plano['valido_ate']}")
            linhas.append("")
            linhas.append("  📍 ENTRADA")
            linhas.append(f"    Preço: {plano['entrada_inicial']['preco']:,.2f}")
            linhas.append(f"    Contratos: {plano['entrada_inicial']['contratos']}")
            linhas.append("")
            linhas.append("  ➕ REFORÇOS")
            for i, reforco in enumerate(plano['reforcos'], 1):
                linhas.append(f"    {i}. {reforco['preco']:,.2f} ({reforco['contratos']} contratos)")
            linhas.append("")
            linhas.append("  🛑 STOP LOSS")
            linhas.append(f"    {plano['gestao_saida']['stop_loss']['preco']:,.2f}")
            linhas.append("")
            linhas.append("  🎯 TAKE PROFIT")
            for tp in plano['gestao_saida']['take_profit']:
                linhas.append(f"    {tp['objetivo']}. {tp['preco']:,.2f} ({tp['contratos']} ct) = R$ {tp['lucro_estimado']:,.2f}")
            linhas.append("")
            linhas.append("  💵 RESUMO DE RISCO")
            linhas.append(f"    Risco: R$ {plano['resumo_risco']['risco_maximo']:,.2f}")
            linhas.append(f"    Lucro Potencial: R$ {plano['resumo_risco']['potencial_lucro']:,.2f}")
            linhas.append(f"    Relação R/R: 1:{plano['resumo_risco']['relacao_risco_retorno']:.2f}")
            linhas.append(f"    % da Meta: {plano['resumo_risco']['percentual_meta']:.1f}%")
        else:
            linhas.append(f"  ⏸️  {plano['justificativa']}")
            linhas.append(f"  💡 {plano['sugestao']}")

        linhas.append("="*70)

        return "\n".join(linhas)


def main():
    """Função principal para teste"""
    print("="*70)
    print("🚀 ANALISADOR WIN DAY TRADING")
    print("="*70)

    # Criar analisador
    analisador = AnalisadorWinDayTrading()

    # Executar análise
    resultado = analisador.analisar()

    # Exibir relatório formatado
    print(analisador.formatar_relatorio(resultado))

    print("\n✅ Análise completa!")
    print("\n💡 Próximos passos:")
    print("   1. Integrar com fontes de dados reais")
    print("   2. Implementar checkpoints interativos")
    print("   3. Adicionar backtesting")
    print("   4. Criar interface web")


if __name__ == "__main__":
    main()
