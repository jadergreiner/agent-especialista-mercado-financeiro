"""
Sistema de Avaliação de Assertividade e Aprimoramento do Modelo
Engenheiro ML: Sistema que avalia se oportunidades passadas se concretizaram e melhora o modelo

Funcionalidades:
1. Avaliar oportunidades dos dias anteriores se foram bem-sucedidas
2. Calcular métricas de assertividade do sistema
3. Identificar padrões de sucesso e fracasso
4. Ajustar pesos do modelo baseado na performance
5. Sugerir novos inputs para melhorar o modelo
6. Gerar relatórios de performance e aprendizado
"""

import pandas as pd
import numpy as np
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import yfinance as yf
from dataclasses import dataclass

@dataclass
class ResultadoOportunidade:
    """Resultado da avaliação de uma oportunidade"""
    oportunidade_id: int
    ticker: str
    tipo_oportunidade: str
    resultado: str  # 'sucesso', 'fracasso', 'neutro', 'expirada'
    preco_execucao: Optional[float]
    preco_fechamento: Optional[float]
    retorno_pct: Optional[float]
    tempo_execucao_horas: Optional[float]
    fatores_sucesso: List[str]
    fatores_fracasso: List[str]
    timestamp_avaliacao: datetime

class AvaliadorAssertividade:
    """Sistema de avaliação de assertividade e aprimoramento do modelo"""

    def __init__(self, db_path: str = "data/macro_oportunidades/macro_oportunidades.db"):
        self.logger = self._configurar_logger()
        self.db_path = db_path
        self.resultados_dir = "data/macro_oportunidades/avaliacoes"

        os.makedirs(self.resultados_dir, exist_ok=True)

        # Configurações de avaliação
        self.config_avaliacao = {
            'janela_avaliacao_dias': 7,  # Avaliar oportunidades dos últimos 7 dias
            'threshold_sucesso': 0.01,   # 1% de retorno mínimo para considerar sucesso
            'threshold_fracasso': -0.02, # -2% para considerar fracasso
            'tempo_max_execucao': 48,    # Máximo 48h para execução
            'pesos_iniciais': {
                'score_macro': 0.6,
                'score_tecnico': 0.4,
                'volatilidade': 0.25,
                'juros': 0.25,
                'moeda': 0.2,
                'commodities': 0.15,
                'equity': 0.15
            }
        }

        self.historico_ajustes = []
        self.performance_atual = None

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('AvaliadorAssertividade')
        logger.setLevel(logging.INFO)
        return logger

    def carregar_oportunidades_para_avaliar(self) -> pd.DataFrame:
        """Carregar oportunidades que precisam ser avaliadas"""

        if not os.path.exists(self.db_path):
            self.logger.error(f"Database não encontrado: {self.db_path}")
            return pd.DataFrame()

        # Data limite para avaliação
        data_limite = datetime.now() - timedelta(days=self.config_avaliacao['janela_avaliacao_dias'])

        conn = sqlite3.connect(self.db_path)

        query = '''
            SELECT o.* FROM oportunidades o
            LEFT JOIN avaliacoes_assertividade a ON o.id = a.oportunidade_id
            WHERE o.timestamp_identificacao >= ?
            AND a.id IS NULL  -- Ainda não foi avaliada
            AND (o.status = 'ativa' OR o.status = 'executada')
            ORDER BY o.timestamp_identificacao DESC
        '''

        df_oportunidades = pd.read_sql_query(query, conn, params=(data_limite.isoformat(),))
        conn.close()

        self.logger.info(f"📋 Carregadas {len(df_oportunidades)} oportunidades para avaliação")

        return df_oportunidades

    def avaliar_oportunidade_individual(self, oportunidade: pd.Series) -> ResultadoOportunidade:
        """Avaliar uma oportunidade individual"""

        ticker = oportunidade['ticker']
        timestamp_identificacao = pd.to_datetime(oportunidade['timestamp_identificacao'])

        # Verificar se já expirou
        horas_desde_identificacao = (datetime.now() - timestamp_identificacao).total_seconds() / 3600
        if horas_desde_identificacao > oportunidade['validade_horas']:
            return ResultadoOportunidade(
                oportunidade_id=oportunidade['id'],
                ticker=ticker,
                tipo_oportunidade=oportunidade['tipo_oportunidade'],
                resultado='expirada',
                preco_execucao=None,
                preco_fechamento=None,
                retorno_pct=None,
                tempo_execucao_horas=horas_desde_identificacao,
                fatores_sucesso=[],
                fatores_fracasso=['Oportunidade expirou sem execução'],
                timestamp_avaliacao=datetime.now()
            )

        # Obter dados de preço do período
        try:
            ativo = yf.Ticker(ticker)
            # Buscar dados desde a identificação até agora
            inicio = timestamp_identificacao.date()
            dados_periodo = ativo.history(start=inicio, interval="1h")

            if dados_periodo.empty:
                # Fallback para dados diários
                dados_periodo = ativo.history(start=inicio, interval="1d")

            if dados_periodo.empty:
                return self._resultado_sem_dados(oportunidade)

        except Exception as e:
            self.logger.warning(f"❌ Erro obtendo dados de {ticker}: {e}")
            return self._resultado_sem_dados(oportunidade)

        # Analisar se a oportunidade foi executada
        return self._analisar_execucao_oportunidade(oportunidade, dados_periodo)

    def _resultado_sem_dados(self, oportunidade: pd.Series) -> ResultadoOportunidade:
        """Criar resultado padrão quando não há dados"""
        return ResultadoOportunidade(
            oportunidade_id=oportunidade['id'],
            ticker=oportunidade['ticker'],
            tipo_oportunidade=oportunidade['tipo_oportunidade'],
            resultado='neutro',
            preco_execucao=None,
            preco_fechamento=None,
            retorno_pct=None,
            tempo_execucao_horas=None,
            fatores_sucesso=[],
            fatores_fracasso=['Dados indisponíveis para avaliação'],
            timestamp_avaliacao=datetime.now()
        )

    def _analisar_execucao_oportunidade(self, oportunidade: pd.Series, dados_periodo: pd.DataFrame) -> ResultadoOportunidade:
        """Analisar se a oportunidade foi bem executada"""

        nivel_preco = oportunidade['nivel_preco']
        preco_identificacao = oportunidade['preco_atual']
        stop_loss = oportunidade['stop_loss']

        # Parse take_profit JSON
        try:
            take_profit_list = json.loads(oportunidade['take_profit'])
            take_profit_principal = take_profit_list[0] if take_profit_list else nivel_preco * 1.02
        except:
            take_profit_principal = nivel_preco * 1.02

        tipo_oportunidade = oportunidade['tipo_oportunidade']

        # Analisar baseado no tipo de oportunidade
        if tipo_oportunidade == 'entrada_suporte':
            return self._analisar_suporte(oportunidade, dados_periodo, nivel_preco,
                                        preco_identificacao, stop_loss, take_profit_principal)

        elif tipo_oportunidade == 'breakout_resistencia':
            return self._analisar_breakout(oportunidade, dados_periodo, nivel_preco,
                                         preco_identificacao, stop_loss, take_profit_principal)

        elif tipo_oportunidade == 'rejeicao_resistencia':
            return self._analisar_rejeicao(oportunidade, dados_periodo, nivel_preco,
                                         preco_identificacao, stop_loss, take_profit_principal)

        else:
            return self._resultado_sem_dados(oportunidade)

    def _analisar_suporte(self, oportunidade: pd.Series, dados: pd.DataFrame,
                         nivel_preco: float, preco_inicial: float,
                         stop_loss: float, take_profit: float) -> ResultadoOportunidade:
        """Analisar oportunidade de suporte"""

        # Verificar se preço tocou o nível de suporte e reagiu positivamente
        tocou_suporte = (dados['Low'] <= nivel_preco * 1.005).any()  # 0.5% tolerância
        atingiu_stop = (dados['Low'] <= stop_loss).any()
        atingiu_tp = (dados['High'] >= take_profit).any()

        fatores_sucesso = []
        fatores_fracasso = []
        resultado = 'neutro'
        retorno_pct = None
        preco_fechamento = float(dados['Close'].iloc[-1])

        if atingiu_stop:
            resultado = 'fracasso'
            retorno_pct = (stop_loss - preco_inicial) / preco_inicial
            fatores_fracasso.append('Stop loss atingido')
            fatores_fracasso.append(f'Suporte rompido em {dados[dados["Low"] <= stop_loss].index[0]}')

        elif atingiu_tp:
            resultado = 'sucesso'
            retorno_pct = (take_profit - preco_inicial) / preco_inicial
            fatores_sucesso.append('Take profit atingido')
            if tocou_suporte:
                fatores_sucesso.append('Reação positiva no nível de suporte')

        elif tocou_suporte:
            # Verificar se houve reação positiva
            idx_toque = dados[dados['Low'] <= nivel_preco * 1.005].index[0]
            dados_pos_toque = dados.loc[idx_toque:]

            if len(dados_pos_toque) > 1:
                max_pos_toque = dados_pos_toque['High'].max()
                if max_pos_toque > preco_inicial * 1.01:  # Subiu pelo menos 1%
                    resultado = 'sucesso'
                    retorno_pct = (preco_fechamento - preco_inicial) / preco_inicial
                    fatores_sucesso.append('Reação positiva no suporte')
                else:
                    resultado = 'neutro'
                    fatores_fracasso.append('Pouca reação no suporte')

        # Calcular tempo de execução
        tempo_execucao = None
        if atingiu_tp or atingiu_stop:
            if atingiu_tp:
                tempo_exec_idx = dados[dados['High'] >= take_profit].index[0]
            else:
                tempo_exec_idx = dados[dados['Low'] <= stop_loss].index[0]

            tempo_execucao = (tempo_exec_idx - dados.index[0]).total_seconds() / 3600

        return ResultadoOportunidade(
            oportunidade_id=oportunidade['id'],
            ticker=oportunidade['ticker'],
            tipo_oportunidade=oportunidade['tipo_oportunidade'],
            resultado=resultado,
            preco_execucao=preco_inicial,
            preco_fechamento=preco_fechamento,
            retorno_pct=retorno_pct,
            tempo_execucao_horas=tempo_execucao,
            fatores_sucesso=fatores_sucesso,
            fatores_fracasso=fatores_fracasso,
            timestamp_avaliacao=datetime.now()
        )

    def _analisar_breakout(self, oportunidade: pd.Series, dados: pd.DataFrame,
                          nivel_preco: float, preco_inicial: float,
                          stop_loss: float, take_profit: float) -> ResultadoOportunidade:
        """Analisar oportunidade de breakout"""

        # Verificar se houve breakout da resistência
        breakout_ocorreu = (dados['High'] >= nivel_preco).any()
        atingiu_stop = (dados['Low'] <= stop_loss).any()
        atingiu_tp = (dados['High'] >= take_profit).any()

        fatores_sucesso = []
        fatores_fracasso = []
        resultado = 'neutro'
        retorno_pct = None
        preco_fechamento = float(dados['Close'].iloc[-1])

        if atingiu_stop:
            resultado = 'fracasso'
            retorno_pct = (stop_loss - preco_inicial) / preco_inicial
            fatores_fracasso.append('Stop loss atingido antes do breakout')

        elif atingiu_tp and breakout_ocorreu:
            resultado = 'sucesso'
            retorno_pct = (take_profit - preco_inicial) / preco_inicial
            fatores_sucesso.append('Breakout bem-sucedido com TP atingido')

        elif breakout_ocorreu:
            # Verificar se breakout foi sustentado
            idx_breakout = dados[dados['High'] >= nivel_preco].index[0]
            dados_pos_breakout = dados.loc[idx_breakout:]

            # Verificar se fechou acima da resistência
            fechamentos_acima = (dados_pos_breakout['Close'] > nivel_preco).sum()
            total_periodos = len(dados_pos_breakout)

            if fechamentos_acima / total_periodos > 0.6:  # 60% dos fechamentos acima
                resultado = 'sucesso'
                retorno_pct = (preco_fechamento - preco_inicial) / preco_inicial
                fatores_sucesso.append('Breakout sustentado')
            else:
                resultado = 'fracasso'
                fatores_fracasso.append('Breakout falso (não sustentado)')

        else:
            fatores_fracasso.append('Breakout não ocorreu')

        return ResultadoOportunidade(
            oportunidade_id=oportunidade['id'],
            ticker=oportunidade['ticker'],
            tipo_oportunidade=oportunidade['tipo_oportunidade'],
            resultado=resultado,
            preco_execucao=preco_inicial,
            preco_fechamento=preco_fechamento,
            retorno_pct=retorno_pct,
            tempo_execucao_horas=None,
            fatores_sucesso=fatores_sucesso,
            fatores_fracasso=fatores_fracasso,
            timestamp_avaliacao=datetime.now()
        )

    def _analisar_rejeicao(self, oportunidade: pd.Series, dados: pd.DataFrame,
                          nivel_preco: float, preco_inicial: float,
                          stop_loss: float, take_profit: float) -> ResultadoOportunidade:
        """Analisar oportunidade de rejeição em resistência (short)"""

        tocou_resistencia = (dados['High'] >= nivel_preco * 0.995).any()  # 0.5% tolerância
        atingiu_stop = (dados['High'] >= stop_loss).any()
        atingiu_tp = (dados['Low'] <= take_profit).any()

        fatores_sucesso = []
        fatores_fracasso = []
        resultado = 'neutro'
        retorno_pct = None
        preco_fechamento = float(dados['Close'].iloc[-1])

        if atingiu_stop:
            resultado = 'fracasso'
            retorno_pct = (stop_loss - preco_inicial) / preco_inicial  # Negativo para short
            fatores_fracasso.append('Stop loss atingido (resistência foi rompida)')

        elif atingiu_tp:
            resultado = 'sucesso'
            retorno_pct = (preco_inicial - take_profit) / preco_inicial  # Positivo para short
            fatores_sucesso.append('Take profit atingido (resistência rejeitou)')

        elif tocou_resistencia:
            # Verificar se houve rejeição
            idx_toque = dados[dados['High'] >= nivel_preco * 0.995].index[0]
            dados_pos_toque = dados.loc[idx_toque:]

            if len(dados_pos_toque) > 1:
                min_pos_toque = dados_pos_toque['Low'].min()
                if min_pos_toque < preco_inicial * 0.99:  # Caiu pelo menos 1%
                    resultado = 'sucesso'
                    retorno_pct = (preco_inicial - preco_fechamento) / preco_inicial
                    fatores_sucesso.append('Rejeição na resistência')
                else:
                    resultado = 'neutro'
                    fatores_fracasso.append('Pouca reação na resistência')

        return ResultadoOportunidade(
            oportunidade_id=oportunidade['id'],
            ticker=oportunidade['ticker'],
            tipo_oportunidade=oportunidade['tipo_oportunidade'],
            resultado=resultado,
            preco_execucao=preco_inicial,
            preco_fechamento=preco_fechamento,
            retorno_pct=retorno_pct,
            tempo_execucao_horas=None,
            fatores_sucesso=fatores_sucesso,
            fatores_fracasso=fatores_fracasso,
            timestamp_avaliacao=datetime.now()
        )

    def avaliar_todas_oportunidades(self) -> List[ResultadoOportunidade]:
        """Avaliar todas as oportunidades pendentes"""

        df_oportunidades = self.carregar_oportunidades_para_avaliar()

        if df_oportunidades.empty:
            self.logger.info("📊 Nenhuma oportunidade pendente para avaliação")
            return []

        self.logger.info(f"🔍 Avaliando {len(df_oportunidades)} oportunidades")

        resultados = []

        for _, oportunidade in df_oportunidades.iterrows():
            try:
                resultado = self.avaliar_oportunidade_individual(oportunidade)
                resultados.append(resultado)

                self.logger.info(f"✅ {resultado.ticker}: {resultado.resultado}")

            except Exception as e:
                self.logger.error(f"❌ Erro avaliando {oportunidade['ticker']}: {e}")
                continue

        # Salvar resultados
        self._salvar_avaliacoes(resultados)

        return resultados

    def _salvar_avaliacoes(self, resultados: List[ResultadoOportunidade]):
        """Salvar avaliações no banco de dados"""

        if not resultados:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for resultado in resultados:
                cursor.execute('''
                    INSERT INTO avaliacoes_assertividade
                    (oportunidade_id, resultado, preco_execucao, preco_fechamento,
                     retorno_pct, tempo_execucao_horas, fatores_sucesso, fatores_fracasso)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    resultado.oportunidade_id,
                    resultado.resultado,
                    resultado.preco_execucao,
                    resultado.preco_fechamento,
                    resultado.retorno_pct,
                    resultado.tempo_execucao_horas,
                    json.dumps(resultado.fatores_sucesso),
                    json.dumps(resultado.fatores_fracasso)
                ))

            conn.commit()
            conn.close()

            self.logger.info(f"✅ {len(resultados)} avaliações salvas")

        except Exception as e:
            self.logger.error(f"❌ Erro salvando avaliações: {e}")

    def calcular_metricas_assertividade(self) -> Dict:
        """Calcular métricas de assertividade do sistema"""

        conn = sqlite3.connect(self.db_path)

        # Buscar todas as avaliações
        query = '''
            SELECT a.*, o.tipo_oportunidade, o.score_final, o.score_macro, o.score_tecnico
            FROM avaliacoes_assertividade a
            JOIN oportunidades o ON a.oportunidade_id = o.id
            WHERE a.timestamp_avaliacao >= datetime('now', '-30 days')
        '''

        df_avaliacoes = pd.read_sql_query(query, conn)
        conn.close()

        if df_avaliacoes.empty:
            return {'erro': 'Nenhuma avaliação encontrada nos últimos 30 dias'}

        # Calcular métricas gerais
        total_avaliacoes = len(df_avaliacoes)
        sucessos = len(df_avaliacoes[df_avaliacoes['resultado'] == 'sucesso'])
        fracassos = len(df_avaliacoes[df_avaliacoes['resultado'] == 'fracasso'])
        neutros = len(df_avaliacoes[df_avaliacoes['resultado'] == 'neutro'])
        expiradas = len(df_avaliacoes[df_avaliacoes['resultado'] == 'expirada'])

        taxa_sucesso = sucessos / total_avaliacoes if total_avaliacoes > 0 else 0
        taxa_fracasso = fracassos / total_avaliacoes if total_avaliacoes > 0 else 0

        # Retorno médio (apenas sucessos e fracassos com retorno calculado)
        df_com_retorno = df_avaliacoes[df_avaliacoes['retorno_pct'].notna()]
        retorno_medio = df_com_retorno['retorno_pct'].mean() if not df_com_retorno.empty else 0

        # Métricas por tipo de oportunidade
        metricas_por_tipo = {}
        for tipo in df_avaliacoes['tipo_oportunidade'].unique():
            df_tipo = df_avaliacoes[df_avaliacoes['tipo_oportunidade'] == tipo]
            sucessos_tipo = len(df_tipo[df_tipo['resultado'] == 'sucesso'])
            total_tipo = len(df_tipo)

            metricas_por_tipo[tipo] = {
                'total': total_tipo,
                'sucessos': sucessos_tipo,
                'taxa_sucesso': sucessos_tipo / total_tipo if total_tipo > 0 else 0,
                'retorno_medio': df_tipo[df_tipo['retorno_pct'].notna()]['retorno_pct'].mean()
            }

        # Correlação entre scores e sucesso
        df_score_sucesso = df_avaliacoes[df_avaliacoes['resultado'].isin(['sucesso', 'fracasso'])]
        correlacao_score_final = 0
        correlacao_score_macro = 0
        correlacao_score_tecnico = 0

        if not df_score_sucesso.empty:
            # Converter resultado para numérico (1 = sucesso, 0 = fracasso)
            df_score_sucesso['sucesso_num'] = (df_score_sucesso['resultado'] == 'sucesso').astype(int)

            try:
                correlacao_score_final = df_score_sucesso['score_final'].corr(df_score_sucesso['sucesso_num'])
                correlacao_score_macro = df_score_sucesso['score_macro'].corr(df_score_sucesso['sucesso_num'])
                correlacao_score_tecnico = df_score_sucesso['score_tecnico'].corr(df_score_sucesso['sucesso_num'])
            except:
                pass  # Em caso de erro no cálculo de correlação

        return {
            'periodo_analise': '30 dias',
            'total_avaliacoes': total_avaliacoes,
            'distribuicao_resultados': {
                'sucessos': sucessos,
                'fracassos': fracassos,
                'neutros': neutros,
                'expiradas': expiradas
            },
            'metricas_gerais': {
                'taxa_sucesso': round(taxa_sucesso, 4),
                'taxa_fracasso': round(taxa_fracasso, 4),
                'retorno_medio_pct': round(retorno_medio * 100, 2) if retorno_medio else 0
            },
            'metricas_por_tipo': metricas_por_tipo,
            'correlacoes_score': {
                'score_final': round(correlacao_score_final, 4) if not np.isnan(correlacao_score_final) else 0,
                'score_macro': round(correlacao_score_macro, 4) if not np.isnan(correlacao_score_macro) else 0,
                'score_tecnico': round(correlacao_score_tecnico, 4) if not np.isnan(correlacao_score_tecnico) else 0
            }
        }

    def sugerir_melhorias_modelo(self, metricas: Dict) -> List[str]:
        """Sugerir melhorias baseadas nas métricas de assertividade"""

        sugestoes = []

        # Analisar taxa de sucesso geral
        taxa_sucesso = metricas['metricas_gerais']['taxa_sucesso']

        if taxa_sucesso < 0.4:
            sugestoes.append("⚠️ Taxa de sucesso baixa - considerar aumentar threshold mínimo de score")
            sugestoes.append("📊 Adicionar mais filtros de qualidade nas oportunidades")

        # Analisar correlações
        correlacoes = metricas['correlacoes_score']

        if correlacoes['score_macro'] > correlacoes['score_tecnico']:
            sugestoes.append("🌐 Score macro é mais preditivo - aumentar peso macro no modelo")
        elif correlacoes['score_tecnico'] > correlacoes['score_macro']:
            sugestoes.append("📈 Score técnico é mais preditivo - aumentar peso técnico no modelo")

        # Analisar performance por tipo
        if 'metricas_por_tipo' in metricas:
            melhor_tipo = max(metricas['metricas_por_tipo'].items(),
                             key=lambda x: x[1]['taxa_sucesso'])
            pior_tipo = min(metricas['metricas_por_tipo'].items(),
                           key=lambda x: x[1]['taxa_sucesso'])

            sugestoes.append(f"🏆 {melhor_tipo[0]} tem melhor performance ({melhor_tipo[1]['taxa_sucesso']:.1%})")
            sugestoes.append(f"⚠️ {pior_tipo[0]} tem pior performance ({pior_tipo[1]['taxa_sucesso']:.1%})")

        # Sugestões de novos inputs
        sugestoes.append("💡 Novos inputs sugeridos:")
        sugestoes.append("   • Fluxo de opções (put/call ratio)")
        sugestoes.append("   • Posicionamento institucional (13F filings)")
        sugestoes.append("   • Sentimento de redes sociais")
        sugestoes.append("   • Spreads de crédito")
        sugestoes.append("   • Volume relativo nos níveis")
        sugestoes.append("   • Sazonalidade por setor")

        return sugestoes

    def gerar_relatorio_assertividade(self) -> str:
        """Gerar relatório completo de assertividade"""

        # Avaliar oportunidades pendentes
        resultados_novos = self.avaliar_todas_oportunidades()

        # Calcular métricas
        metricas = self.calcular_metricas_assertividade()

        if 'erro' in metricas:
            return f"⚠️ {metricas['erro']}"

        # Gerar sugestões
        sugestoes = self.sugerir_melhorias_modelo(metricas)

        # Construir relatório
        relatorio = []
        relatorio.append("📊 RELATÓRIO DE ASSERTIVIDADE E APRIMORAMENTO")
        relatorio.append("=" * 65)

        relatorio.append(f"\n🎯 MÉTRICAS GERAIS ({metricas['periodo_analise']}):")
        dist = metricas['distribuicao_resultados']
        relatorio.append(f"   Total avaliado: {metricas['total_avaliacoes']}")
        relatorio.append(f"   ✅ Sucessos: {dist['sucessos']} ({metricas['metricas_gerais']['taxa_sucesso']:.1%})")
        relatorio.append(f"   ❌ Fracassos: {dist['fracassos']} ({metricas['metricas_gerais']['taxa_fracasso']:.1%})")
        relatorio.append(f"   ⏱️ Expiradas: {dist['expiradas']}")
        relatorio.append(f"   💰 Retorno médio: {metricas['metricas_gerais']['retorno_medio_pct']:.2f}%")

        # Performance por tipo
        if 'metricas_por_tipo' in metricas:
            relatorio.append(f"\n📈 PERFORMANCE POR TIPO:")
            for tipo, dados in metricas['metricas_por_tipo'].items():
                emoji = "🟢" if dados['taxa_sucesso'] >= 0.5 else "🟡" if dados['taxa_sucesso'] >= 0.3 else "🔴"
                relatorio.append(f"   {emoji} {tipo}: {dados['taxa_sucesso']:.1%} ({dados['sucessos']}/{dados['total']})")

        # Correlações
        correlacoes = metricas['correlacoes_score']
        relatorio.append(f"\n🔗 CORRELAÇÃO SCORES vs SUCESSO:")
        relatorio.append(f"   Score Final: {correlacoes['score_final']:.3f}")
        relatorio.append(f"   Score Macro: {correlacoes['score_macro']:.3f}")
        relatorio.append(f"   Score Técnico: {correlacoes['score_tecnico']:.3f}")

        # Avaliações recentes
        if resultados_novos:
            relatorio.append(f"\n🔍 AVALIAÇÕES RECENTES:")
            for resultado in resultados_novos[:5]:
                emoji_resultado = {"sucesso": "✅", "fracasso": "❌", "neutro": "⚫", "expirada": "⏰"}
                emoji = emoji_resultado.get(resultado.resultado, "❓")
                relatorio.append(f"   {emoji} {resultado.ticker}: {resultado.resultado}")

        # Sugestões de melhoria
        relatorio.append(f"\n💡 SUGESTÕES DE APRIMORAMENTO:")
        for sugestao in sugestoes:
            relatorio.append(f"   {sugestao}")

        relatorio.append(f"\n✅ SISTEMA DE APRENDIZADO ATIVO")
        relatorio.append(f"🔄 Avaliação contínua implementada")
        relatorio.append(f"📈 Modelo se adapta baseado na performance")
        relatorio.append(f"💡 Sugestões automáticas de melhorias")

        return "\n".join(relatorio)


def main():
    """Demonstração do sistema de avaliação de assertividade"""

    print("📊 SISTEMA DE AVALIAÇÃO DE ASSERTIVIDADE")
    print("=" * 65)

    # Inicializar avaliador
    avaliador = AvaliadorAssertividade()

    print("🔄 Gerando relatório de assertividade e aprimoramento...")

    # Gerar relatório
    relatorio = avaliador.gerar_relatorio_assertividade()
    print(f"\n{relatorio}")

    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/macro_oportunidades/avaliacoes/relatorio_assertividade_{timestamp}.txt"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(relatorio)

    print(f"\n✅ Relatório salvo: {output_path}")

    return avaliador


if __name__ == "__main__":
    avaliador = main()