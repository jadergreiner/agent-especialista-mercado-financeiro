"""
Análise Complementar do Sistema de Validação
Engenheiro ML: Sistema avançado de insights e análise de performance dos níveis

Funcionalidades:
1. Análise de patterns nos dados de validação
2. Machine Learning para identificar características de níveis efetivos
3. Scoring preditivo de qualidade de níveis
4. Análise temporal de performance
5. Identificação de melhores configurações de parâmetros
"""

import pandas as pd
import numpy as np
import json
import sqlite3
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class AnalisadorPerformanceNiveis:
    """Sistema ML para análise de performance e insights dos níveis validados"""

    def __init__(self, db_path: str = "data/validacao_historica/validacao_niveis.db"):
        self.logger = self._configurar_logger()
        self.db_path = db_path
        self.insights_dir = "data/validacao_historica/insights"

        os.makedirs(self.insights_dir, exist_ok=True)

        # Modelo simples para scoring preditivo (sem sklearn)
        self.coeficientes_modelo = None
        self.estatisticas_features = None
        self.modelo_treinado = False

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('AnalisadorPerformanceNiveis')
        logger.setLevel(logging.INFO)
        return logger

    def carregar_dados_validacao(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Carregar dados de validação do SQLite"""

        if not os.path.exists(self.db_path):
            self.logger.error(f"Database não encontrado: {self.db_path}")
            return pd.DataFrame(), pd.DataFrame()

        conn = sqlite3.connect(self.db_path)

        # Dados individuais de níveis
        query_niveis = """
            SELECT * FROM validacoes_niveis
            ORDER BY ticker, data_identificacao
        """
        df_niveis = pd.read_sql_query(query_niveis, conn)

        # Dados de performance por portfolio
        query_performance = """
            SELECT * FROM performance_portfolio
            ORDER BY ticker, timestamp_teste
        """
        df_performance = pd.read_sql_query(query_performance, conn)

        conn.close()

        self.logger.info(f"✅ Carregados {len(df_niveis)} registros de níveis, {len(df_performance)} de performance")

        return df_niveis, df_performance

    def analisar_patterns_efetividade(self, df_niveis: pd.DataFrame) -> Dict:
        """Identificar patterns que levam a níveis mais efetivos"""

        if df_niveis.empty:
            return {}

        self.logger.info("🔍 Analisando patterns de efetividade dos níveis")

        # Criar features para análise ML
        features = []
        targets = []

        for _, row in df_niveis.iterrows():
            # Features baseadas nas características do nível
            feature_set = {
                'score_precisao': row['score_precisao'],
                'score_recall': row['score_recall'],
                'score_f1': row['score_f1'],
                'toques_validados': row['toques_validados'],
                'breakouts_detectados': row['breakouts_detectados'],
                'tipo_nivel_suporte': 1 if row['tipo_nivel'] == 'suporte' else 0,
                'nivel_preco_log': np.log(row['nivel_preco']),
                'confluencia_timeframes': int(row['metadados']) if row['metadados'] and row['metadados'].isdigit() else 0
            }

            features.append(list(feature_set.values()))
            targets.append(row['forca_nivel'])

        if len(features) < 10:  # Mínimo para análise
            return {'erro': 'Dados insuficientes para análise ML'}

        X = np.array(features)
        y = np.array(targets)

        # Treinar modelo simples (regressão linear com regularização manual)
        self._treinar_modelo_simples(X, y)
        self.modelo_treinado = True

        # Análise de importância das features
        feature_names = [
            'score_precisao', 'score_recall', 'score_f1', 'toques_validados',
            'breakouts_detectados', 'tipo_nivel_suporte', 'nivel_preco_log',
            'confluencia_timeframes'
        ]

        # Calcular importância baseada em correlação com target
        importancias = self._calcular_importancia_features(X, y, feature_names)

        # Performance do modelo
        y_pred = self._prever_com_modelo_simples(X)
        mae = np.mean(np.abs(y - y_pred))
        r2 = self._calcular_r2(y, y_pred)

        # Top features por importância
        feature_importance = list(zip(feature_names, importancias))
        feature_importance.sort(key=lambda x: x[1], reverse=True)

        return {
            'modelo_performance': {
                'r2_score': round(r2, 4),
                'mae_medio': round(mae, 4),
                'total_samples': len(features)
            },
            'top_features': feature_importance[:5],
            'insights_patterns': self._gerar_insights_patterns(df_niveis, feature_importance),
            'configuracoes_otimas': self._identificar_configuracoes_otimas(df_niveis)
        }

    def _gerar_insights_patterns(self, df_niveis: pd.DataFrame, feature_importance: List) -> List[str]:
        """Gerar insights textuais baseados nos patterns identificados"""

        insights = []

        # Análise por tipo de nível
        suportes = df_niveis[df_niveis['tipo_nivel'] == 'suporte']
        resistencias = df_niveis[df_niveis['tipo_nivel'] == 'resistencia']

        if not suportes.empty and not resistencias.empty:
            forca_suportes = suportes['forca_nivel'].mean()
            forca_resistencias = resistencias['forca_nivel'].mean()

            if forca_suportes > forca_resistencias * 1.1:
                insights.append(f"Suportes são {((forca_suportes/forca_resistencias-1)*100):.1f}% mais efetivos que resistências")
            elif forca_resistencias > forca_suportes * 1.1:
                insights.append(f"Resistências são {((forca_resistencias/forca_suportes-1)*100):.1f}% mais efetivas que suportes")

        # Análise de toques
        if len(df_niveis) > 10:
            correlacao_toques = df_niveis['toques_validados'].corr(df_niveis['forca_nivel'])
            if correlacao_toques > 0.3:
                insights.append(f"Níveis com mais toques são significativamente mais fortes (correlação: {correlacao_toques:.2f})")

        # Feature mais importante
        if feature_importance:
            top_feature = feature_importance[0]
            insights.append(f"'{top_feature[0]}' é o fator mais determinante da efetividade ({top_feature[1]:.1%} importância)")

        # Análise de breakouts
        niveis_com_breakout = df_niveis[df_niveis['breakouts_detectados'] > 0]
        if len(niveis_com_breakout) > 0:
            taxa_breakout = len(niveis_com_breakout) / len(df_niveis)
            insights.append(f"{taxa_breakout:.1%} dos níveis sofreram breakout durante validação")

        return insights

    def _identificar_configuracoes_otimas(self, df_niveis: pd.DataFrame) -> Dict:
        """Identificar configurações ótimas baseadas na performance"""

        if df_niveis.empty:
            return {}

        # Análise de níveis válidos vs inválidos
        niveis_validos = df_niveis[df_niveis['valido'] == True]
        niveis_invalidos = df_niveis[df_niveis['valido'] == False]

        config_otimas = {}

        if not niveis_validos.empty:
            # Características médias dos níveis válidos
            config_otimas['niveis_validos'] = {
                'toques_medio': round(niveis_validos['toques_validados'].mean(), 2),
                'f1_score_medio': round(niveis_validos['score_f1'].mean(), 4),
                'forca_media': round(niveis_validos['forca_nivel'].mean(), 4),
                'breakouts_medio': round(niveis_validos['breakouts_detectados'].mean(), 2)
            }

            # Percentis para thresholds recomendados
            config_otimas['thresholds_recomendados'] = {
                'min_toques': int(niveis_validos['toques_validados'].quantile(0.25)),
                'min_f1_score': round(niveis_validos['score_f1'].quantile(0.25), 4),
                'min_forca': round(niveis_validos['forca_nivel'].quantile(0.25), 4)
            }

        # Taxa de sucesso por ticker
        if 'ticker' in df_niveis.columns:
            taxa_por_ticker = df_niveis.groupby('ticker')['valido'].agg(['count', 'sum']).reset_index()
            taxa_por_ticker['taxa_sucesso'] = taxa_por_ticker['sum'] / taxa_por_ticker['count']
            taxa_por_ticker = taxa_por_ticker.sort_values('taxa_sucesso', ascending=False)

            config_otimas['performance_por_ativo'] = {
                'melhor_ativo': taxa_por_ticker.iloc[0]['ticker'] if len(taxa_por_ticker) > 0 else None,
                'melhor_taxa': round(taxa_por_ticker.iloc[0]['taxa_sucesso'], 4) if len(taxa_por_ticker) > 0 else 0,
                'ranking_ativos': taxa_por_ticker.to_dict('records')
            }

        return config_otimas

    def _treinar_modelo_simples(self, X: np.ndarray, y: np.ndarray):
        """Treinar modelo de regressão linear simples"""

        # Normalizar features
        self.estatisticas_features = {
            'mean': np.mean(X, axis=0),
            'std': np.std(X, axis=0) + 1e-8  # Evitar divisão por zero
        }

        X_norm = (X - self.estatisticas_features['mean']) / self.estatisticas_features['std']

        # Regressão linear com regularização manual (Ridge simples)
        alpha = 0.1  # Fator de regularização

        # Adicionar bias (intercepto)
        X_bias = np.column_stack([np.ones(X_norm.shape[0]), X_norm])

        # Resolver equação normal com regularização
        try:
            XTX = X_bias.T @ X_bias
            XTX_reg = XTX + alpha * np.eye(XTX.shape[0])
            XTy = X_bias.T @ y
            self.coeficientes_modelo = np.linalg.solve(XTX_reg, XTy)
        except:
            # Fallback para caso de problemas numéricos
            self.coeficientes_modelo = np.zeros(X_bias.shape[1])
            self.coeficientes_modelo[0] = np.mean(y)  # Intercepto = média do target

    def _prever_com_modelo_simples(self, X: np.ndarray) -> np.ndarray:
        """Fazer predições com o modelo simples"""

        if self.coeficientes_modelo is None or self.estatisticas_features is None:
            return np.full(X.shape[0], 0.5)  # Default neutro

        # Normalizar
        X_norm = (X - self.estatisticas_features['mean']) / self.estatisticas_features['std']

        # Adicionar bias
        X_bias = np.column_stack([np.ones(X_norm.shape[0]), X_norm])

        # Predizer
        return X_bias @ self.coeficientes_modelo

    def _calcular_importancia_features(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> np.ndarray:
        """Calcular importância das features baseada em correlação absoluta"""

        importancias = []

        for i in range(X.shape[1]):
            # Correlação de Pearson absoluta
            correlation = np.abs(np.corrcoef(X[:, i], y)[0, 1])

            # Se houver NaN (dados constantes), usar 0
            if np.isnan(correlation):
                correlation = 0.0

            importancias.append(correlation)

        # Normalizar para soma = 1
        importancias = np.array(importancias)
        soma_importancias = np.sum(importancias)

        if soma_importancias > 0:
            importancias = importancias / soma_importancias

        return importancias

    def _calcular_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcular R² score"""

        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

        if ss_tot == 0:
            return 0.0

        return 1 - (ss_res / ss_tot)

    def prever_qualidade_nivel(self, caracteristicas_nivel: Dict) -> float:
        """Usar modelo ML para prever qualidade de um novo nível"""

        if not self.modelo_treinado:
            return 0.5  # Score neutro se modelo não foi treinado

        # Converter características para features
        features = [
            caracteristicas_nivel.get('score_precisao', 0.5),
            caracteristicas_nivel.get('score_recall', 0.5),
            caracteristicas_nivel.get('score_f1', 0.5),
            caracteristicas_nivel.get('toques_validados', 1),
            caracteristicas_nivel.get('breakouts_detectados', 0),
            1 if caracteristicas_nivel.get('tipo_nivel') == 'suporte' else 0,
            np.log(caracteristicas_nivel.get('nivel_preco', 100)),
            caracteristicas_nivel.get('confluencia_timeframes', 0)
        ]

        predicao = self._prever_com_modelo_simples(np.array([features]))[0]
        return max(0.0, min(1.0, predicao))  # Limitar entre 0 e 1

    def gerar_relatorio_insights(self, df_niveis: pd.DataFrame, df_performance: pd.DataFrame) -> str:
        """Gerar relatório completo de insights"""

        relatorio = []
        relatorio.append("🧠 RELATÓRIO DE INSIGHTS - ANÁLISE ML DE NÍVEIS")
        relatorio.append("=" * 65)

        if df_niveis.empty:
            relatorio.append("\n❌ Nenhum dado de validação disponível para análise")
            return "\n".join(relatorio)

        # Estatísticas gerais
        total_niveis = len(df_niveis)
        niveis_validos = df_niveis['valido'].sum()
        taxa_geral = niveis_validos / total_niveis if total_niveis > 0 else 0

        relatorio.append(f"\n📊 ESTATÍSTICAS GERAIS:")
        relatorio.append(f"   Total de níveis analisados: {total_niveis}")
        relatorio.append(f"   Níveis válidos: {niveis_validos} ({taxa_geral:.1%})")
        relatorio.append(f"   Força média dos níveis: {df_niveis['forca_nivel'].mean():.3f}")
        relatorio.append(f"   F1-Score médio: {df_niveis['score_f1'].mean():.3f}")

        # Análise ML
        patterns = self.analisar_patterns_efetividade(df_niveis)

        if 'modelo_performance' in patterns:
            modelo = patterns['modelo_performance']
            relatorio.append(f"\n🤖 MODELO ML DE PREDIÇÃO:")
            relatorio.append(f"   R² Score: {modelo['r2_score']:.3f}")
            relatorio.append(f"   Erro médio absoluto: {modelo['mae_medio']:.4f}")
            relatorio.append(f"   Amostras de treinamento: {modelo['total_samples']}")

        # Top features
        if 'top_features' in patterns:
            relatorio.append(f"\n🎯 FATORES MAIS IMPORTANTES:")
            for i, (feature, importance) in enumerate(patterns['top_features'][:3], 1):
                relatorio.append(f"   {i}. {feature}: {importance:.1%}")

        # Insights dos patterns
        if 'insights_patterns' in patterns:
            relatorio.append(f"\n💡 INSIGHTS DESCOBERTOS:")
            for insight in patterns['insights_patterns']:
                relatorio.append(f"   • {insight}")

        # Configurações ótimas
        if 'configuracoes_otimas' in patterns:
            config = patterns['configuracoes_otimas']

            if 'thresholds_recomendados' in config:
                thresh = config['thresholds_recomendados']
                relatorio.append(f"\n⚙️ CONFIGURAÇÕES RECOMENDADAS:")
                relatorio.append(f"   Mínimo de toques: {thresh['min_toques']}")
                relatorio.append(f"   Mínimo F1-Score: {thresh['min_f1_score']:.3f}")
                relatorio.append(f"   Mínima força: {thresh['min_forca']:.3f}")

            if 'performance_por_ativo' in config:
                perf = config['performance_por_ativo']
                relatorio.append(f"\n🏆 PERFORMANCE POR ATIVO:")
                relatorio.append(f"   Melhor ativo: {perf['melhor_ativo']} ({perf['melhor_taxa']:.1%} sucesso)")

        # Distribuição por tipo
        suportes_count = (df_niveis['tipo_nivel'] == 'suporte').sum()
        resistencias_count = (df_niveis['tipo_nivel'] == 'resistencia').sum()

        relatorio.append(f"\n📈 DISTRIBUIÇÃO POR TIPO:")
        relatorio.append(f"   Suportes: {suportes_count} ({suportes_count/total_niveis:.1%})")
        relatorio.append(f"   Resistências: {resistencias_count} ({resistencias_count/total_niveis:.1%})")

        # Análise temporal se tiver dados suficientes
        if len(df_niveis) > 20:
            df_niveis_temp = df_niveis.copy()
            df_niveis_temp['data_identificacao'] = pd.to_datetime(df_niveis_temp['data_identificacao'])
            df_niveis_temp['mes'] = df_niveis_temp['data_identificacao'].dt.to_period('M')

            performance_mensal = df_niveis_temp.groupby('mes')['forca_nivel'].mean()
            if len(performance_mensal) > 1:
                tendencia = "crescente" if performance_mensal.iloc[-1] > performance_mensal.iloc[0] else "decrescente"
                relatorio.append(f"\n📅 TENDÊNCIA TEMPORAL:")
                relatorio.append(f"   Tendência de performance: {tendencia}")
                relatorio.append(f"   Melhor mês: {performance_mensal.idxmax()} ({performance_mensal.max():.3f})")

        relatorio.append("\n✅ SISTEMA DE INSIGHTS OPERACIONAL")
        relatorio.append("🧠 Análise ML de patterns implementada")
        relatorio.append("🎯 Modelo preditivo de qualidade treinado")
        relatorio.append("⚙️ Configurações otimizadas identificadas")

        return "\n".join(relatorio)

    def executar_analise_completa(self) -> Dict:
        """Executar análise completa e gerar todos os insights"""

        self.logger.info("🧠 Iniciando análise completa de insights")

        # Carregar dados
        df_niveis, df_performance = self.carregar_dados_validacao()

        if df_niveis.empty:
            self.logger.warning("⚠️ Nenhum dado encontrado para análise")
            return {}

        # Gerar análises
        patterns = self.analisar_patterns_efetividade(df_niveis)
        relatorio = self.gerar_relatorio_insights(df_niveis, df_performance)

        # Preparar resultado completo
        resultado_completo = {
            'timestamp_analise': datetime.now().isoformat(),
            'estatisticas_gerais': {
                'total_niveis': len(df_niveis),
                'niveis_validos': int(df_niveis['valido'].sum()),
                'taxa_sucesso_geral': float(df_niveis['valido'].mean()),
                'forca_media': float(df_niveis['forca_nivel'].mean()),
                'f1_score_medio': float(df_niveis['score_f1'].mean())
            },
            'patterns_ml': patterns,
            'relatorio_insights': relatorio,
            'modelo_treinado': self.modelo_treinado
        }

        # Salvar resultados
        output_path = os.path.join(self.insights_dir, "analise_completa_insights.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultado_completo, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info(f"✅ Análise completa salva em: {output_path}")

        return resultado_completo


def main():
    """Demonstração do sistema de análise de insights"""

    print("🧠 SISTEMA DE ANÁLISE DE INSIGHTS - ML AVANÇADO")
    print("=" * 65)

    # Inicializar analisador
    analisador = AnalisadorPerformanceNiveis()

    print("🔄 Executando análise completa de insights...")

    # Executar análise
    resultado = analisador.executar_analise_completa()

    if resultado and 'relatorio_insights' in resultado:
        print(f"\n{resultado['relatorio_insights']}")

        # Exemplo de predição
        if analisador.modelo_treinado:
            print(f"\n🔮 EXEMPLO DE PREDIÇÃO:")
            exemplo_nivel = {
                'score_precisao': 0.8,
                'score_recall': 0.7,
                'score_f1': 0.75,
                'toques_validados': 3,
                'breakouts_detectados': 0,
                'tipo_nivel': 'suporte',
                'nivel_preco': 150.0,
                'confluencia_timeframes': 2
            }

            qualidade_prevista = analisador.prever_qualidade_nivel(exemplo_nivel)
            print(f"   Nível exemplo: qualidade prevista {qualidade_prevista:.1%}")
    else:
        print("⚠️ Nenhum dado disponível para análise de insights")

    return analisador, resultado


if __name__ == "__main__":
    analisador, resultado = main()