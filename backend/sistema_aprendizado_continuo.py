"""
Sistema de Aprendizado Contínuo Baseado em Feedback de Recomendações
Implementa o prompt estruturado para análise de performance e ajustes dinâmicos

Funcionalidades:
1. Análise de performance de recomendações individuais
2. Comparação previsto vs real
3. Extração de aprendizados específicos
4. Ajuste automático de pesos baseado em feedback
5. Geração de relatórios de aprendizado
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
import pandas as pd

# Importar configuração de ambiente
try:
    from configuracao_ambiente import configurar_ambiente_producao
    CONFIG_AMBIENTE = configurar_ambiente_producao()
except ImportError:
    print("⚠️ Configuração de ambiente não encontrada - usando modo DEMO")
    CONFIG_AMBIENTE = None

@dataclass
class AnalisePerformance:
    """Resultado da análise de performance de uma recomendação"""
    recomendacao_id: int
    timestamp_analise: datetime

    # Dados de feedback
    resultado_real: str
    movimento_preco_observado: str
    eventos_ocorridos: str

    # Comparação previsto vs real
    probabilidade_prevista: float
    probabilidade_real: float
    timeframe_estimado: str
    timeframe_real: str
    catalisadores_previstos: List[str]
    catalisadores_reais: List[str]
    risco_previsto: float
    risco_real: float

    # Aprendizados
    pontos_positivos: List[str]
    pontos_melhoria: List[str]
    sinais_subestimados: List[str]
    sinais_superestimados: List[str]
    calibracao_probabilidades: str
    novos_inputs_sugeridos: List[str]

    # Ajustes recomendados
    ajustes_pesos: Dict[str, float]
    confianca_ajuste: str

class SistemaAprendizadoContinuo:
    """Sistema que implementa aprendizado contínuo baseado no prompt estruturado"""

    def __init__(self, db_path: str = "data/recomendacoes.sqlite"):
        self.logger = self._configurar_logger()
        self.db_path = db_path
        self.analises_dir = "data/aprendizado_continuo"

        os.makedirs(self.analises_dir, exist_ok=True)

        # Verificar configuração de ambiente
        if CONFIG_AMBIENTE:
            self.ambiente = CONFIG_AMBIENTE.ambiente.value
            self.usar_dados_reais = CONFIG_AMBIENTE.usar_dados_reais

            if self.ambiente == 'producao':
                self.logger.warning("🚨 SISTEMA EM MODO PRODUÇÃO - Usando dados reais!")
            elif self.ambiente == 'demo':
                self.logger.info("🔧 Sistema em modo DEMO - Usando dados simulados")
        else:
            self.ambiente = 'demo'
            self.usar_dados_reais = False
            self.logger.warning("⚠️ Configuração de ambiente não carregada - usando DEMO")

        # Pesos atuais do sistema (atualizados após análise de performance 2025-11-07)
        self.pesos_atuais = {
            'score_macro': 0.32,      # Reduzido de 0.35 (-0.03) - subestimado impacto negativo
            'score_tecnico': 0.28,    # Reduzido de 0.30 (-0.02) - superestimado em pânico
            'volatilidade': 0.18,     # Aumentado de 0.15 (+0.03) - velocidade subestimada
            'juros': 0.10,            # Mantido - não afetado
            'moeda': 0.05,            # Mantido - não afetado
            'commodities': 0.03,      # Mantido - movimento contrário observado
            'equity': 0.02,           # Mantido - não afetado
            # Novos fatores adicionados após análise
            'ewz_correlation': 0.012, # Novo - correlação EWZ ignorada
            'quant_flow': 0.015,      # Novo - vendas quant não previstas
            'central_bank_news': 0.012, # Novo - notícias BC subestimadas
            'dark_pool_activity': 0.008, # Novo - atividade dark pools
            'policy_sentiment': 0.007,   # Novo - sentimento política econômica
            'multi_timeframe_corr': 0.005 # Novo - correlação multi-timeframe
        }

        # Histórico de ajustes
        self.historico_ajustes = []

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('SistemaAprendizadoContinuo')
        logger.setLevel(logging.INFO)
        return logger

    def executar_prompt_aprendizado(self,
                                  recomendacao_id: int,
                                  resultado_real: str,
                                  movimento_preco_observado: str,
                                  eventos_ocorridos: str) -> str:
        """
        Executa o prompt de aprendizado contínuo com dados específicos

        Args:
            recomendacao_id: ID da recomendação analisada
            resultado_real: Resultado efetivo (ACERTOU/ERROU/CANCELADA/EXPIRADA)
            movimento_preco_observado: Descrição do movimento observado
            eventos_ocorridos: Eventos que impactaram o mercado

        Returns:
            Análise completa formatada
        """

        # Template do prompt
        prompt = f"""
ANÁLISE DE PERFORMANCE DA RECOMENDAÇÃO ANTERIOR:

DADOS DE FEEDBACK:
{resultado_real}
{movimento_preco_observado}
{eventos_ocorridos}

COMPARE:
- Probabilidade prevista vs resultado real
- Timeframe estimado vs tempo real de movimento
- Catalisadores previstos vs eventos reais que moveram mercado
- Nível de invalidação vs maior excursão adversa

APRENDIZADOS:
1. O que funcionou bem na análise?
2. Que sinais foram subestimados/superestimados?
3. Como melhorar a calibração de probabilidades?
4. Que novos inputs poderiam ter melhorado a previsão?

AJUSTE os pesos dos próximos fatores de decisão baseado nestes aprendizados.
"""

        # Aqui seria integrada uma chamada para LLM/IA
        # Por enquanto, simulamos uma análise baseada em regras
        analise = self._gerar_analise_simulada(recomendacao_id, resultado_real,
                                             movimento_preco_observado, eventos_ocorridos)

        return self._formatar_relatorio_analise(analise)

    def _gerar_analise_simulada(self,
                               recomendacao_id: int,
                               resultado_real: str,
                               movimento_preco_observado: str,
                               eventos_ocorridos: str) -> AnalisePerformance:
        """
        Gera análise simulada baseada em regras (substituir por LLM real)
        """

        # Lógica simplificada baseada no resultado
        if "ACERTOU" in resultado_real.upper():
            probabilidade_real = 1.0
            pontos_positivos = [
                "Análise técnica correta",
                "Timing de entrada preciso",
                "Catalisadores principais identificados"
            ]
            pontos_melhoria = [
                "Buffer de probabilidade poderia ser menor",
                "Considerar eventos secundários"
            ]
            ajustes_pesos = {
                'score_tecnico': 0.05,  # +5%
                'score_macro': 0.03    # +3%
            }
        else:
            probabilidade_real = 0.0
            pontos_positivos = [
                "Identificação de oportunidade válida"
            ]
            pontos_melhoria = [
                "Subestimação de riscos macro",
                "Catalisadores secundários ignorados",
                "Probabilidade superestimada"
            ]
            ajustes_pesos = {
                'score_macro': 0.05,   # +5%
                'volatilidade': 0.03,  # +3%
                'score_tecnico': -0.02  # -2%
            }

        # Análise de timeframe (simplificada)
        if "horas" in movimento_preco_observado.lower():
            timeframe_real = "2-4h"
        else:
            timeframe_real = "1-2 dias"

        return AnalisePerformance(
            recomendacao_id=recomendacao_id,
            timestamp_analise=datetime.now(),
            resultado_real=resultado_real,
            movimento_preco_observado=movimento_preco_observado,
            eventos_ocorridos=eventos_ocorridos,
            probabilidade_prevista=0.75,  # Assumindo padrão
            probabilidade_real=probabilidade_real,
            timeframe_estimado="2-4h",
            timeframe_real=timeframe_real,
            catalisadores_previstos=["Dados econômicos", "Análise técnica"],
            catalisadores_reais=eventos_ocorridos.split(", ") if eventos_ocorridos else [],
            risco_previsto=500.0,  # R$ 500 stop loss
            risco_real=380.0,     # R$ 380 perda máxima
            pontos_positivos=pontos_positivos,
            pontos_melhoria=pontos_melhoria,
            sinais_subestimados=["Impacto de notícias"],
            sinais_superestimados=[],
            calibracao_probabilidades="Reduzir probabilidade em 10-15% para setups similares",
            novos_inputs_sugeridos=[
                "Análise de sentimento de redes sociais",
                "Fluxo de opções",
                "Posicionamento institucional"
            ],
            ajustes_pesos=ajustes_pesos,
            confianca_ajuste="ALTA"
        )

    def _formatar_relatorio_analise(self, analise: AnalisePerformance) -> str:
        """Formata a análise em relatório estruturado"""

        relatorio = []
        relatorio.append("## 📊 ANÁLISE DE PERFORMANCE - RECOMENDAÇÃO")
        relatorio.append(f"**ID:** {analise.recomendacao_id}")
        relatorio.append(f"**Data:** {analise.timestamp_analise.strftime('%Y-%m-%d %H:%M')}")
        relatorio.append("")

        # Comparação previsto vs real
        relatorio.append("### 🔍 COMPARAÇÃO PREVISTO vs REAL")
        relatorio.append(f"- **Probabilidade**: Prevista {analise.probabilidade_prevista:.0%} → Real: {'ACERTOU' if analise.probabilidade_real > 0.5 else 'ERROU'} ({analise.probabilidade_real:.0%})")
        relatorio.append(f"- **Timeframe**: Estimado {analise.timeframe_estimado} → Real: {analise.timeframe_real}")
        relatorio.append(f"- **Catalisadores**: Previstos {analise.catalisadores_previstos} → Reais: {analise.catalisadores_reais}")
        relatorio.append(f"- **Risco**: Stop R$ {analise.risco_previsto:.0f} → Máxima perda R$ {analise.risco_real:.0f}")
        relatorio.append("")

        # O que funcionou bem
        relatorio.append("### ✅ O QUE FUNCIONOU BEM")
        for ponto in analise.pontos_positivos:
            relatorio.append(f"- {ponto}")
        relatorio.append("")

        # Pontos de melhoria
        relatorio.append("### ⚠️ PONTOS DE MELHORIA")
        for ponto in analise.pontos_melhoria:
            relatorio.append(f"- {ponto}")
        relatorio.append("")

        # Sinais sub/superestimados
        if analise.sinais_subestimados:
            relatorio.append("### 📉 SINAIS SUBESTIMADOS")
            for sinal in analise.sinais_subestimados:
                relatorio.append(f"- {sinal}")

        if analise.sinais_superestimados:
            relatorio.append("### 📈 SINAIS SUPERESTIMADOS")
            for sinal in analise.sinais_superestimados:
                relatorio.append(f"- {sinal}")
        relatorio.append("")

        # Calibração de probabilidades
        relatorio.append("### 🎯 CALIBRAÇÃO DE PROBABILIDADES")
        relatorio.append(f"{analise.calibracao_probabilidades}")
        relatorio.append("")

        # Novos inputs sugeridos
        relatorio.append("### 💡 NOVOS INPUTS SUGERIDOS")
        for input_sugerido in analise.novos_inputs_sugeridos:
            relatorio.append(f"- {input_sugerido}")
        relatorio.append("")

        # Ajustes recomendados
        relatorio.append("### 🔧 AJUSTES RECOMENDADOS")
        for fator, ajuste in analise.ajustes_pesos.items():
            simbolo = "+" if ajuste > 0 else ""
            relatorio.append(f"1. **Peso do {fator}**: {simbolo}{ajuste:.0%} (atual: {self.pesos_atuais.get(fator, 0):.0%} → novo: {self.pesos_atuais.get(fator, 0) + ajuste:.0%})")

        relatorio.append("")
        relatorio.append("### 📈 PRÓXIMAS RECOMENDAÇÕES")
        relatorio.append("- Aplicar ajustes acima nas próximas 3 recomendações")
        relatorio.append("- Monitorar impacto na acurácia por 1 semana")
        relatorio.append("- Revisar pesos novamente após 10 validações")
        relatorio.append("")
        relatorio.append(f"**Confiança do ajuste:** {analise.confianca_ajuste}")

        return "\n".join(relatorio)

    def ajustar_probabilidade_base(self, probabilidade_base: float, fatores_ajuste: Dict[str, bool]) -> float:
        """
        Ajusta probabilidade base baseada em fatores de risco identificados na análise

        Args:
            probabilidade_base: Probabilidade inicial calculada
            fatores_ajuste: Dicionário com fatores de risco presentes

        Returns:
            Probabilidade ajustada com limites de segurança
        """
        multiplicadores = {
            'payrolls_dia': 0.85,      # -15% em dias de payrolls EUA
            'dxy_alta_vol': 0.90,      # -10% em alta volatilidade DXY
            'stress_global': 0.80,     # -20% em períodos de stress global
            'quant_selling': 0.70,     # -30% quando vendas quant detectadas
            'intervencao_bc': 0.60,    # -40% em notícias de intervenção BC
            'ewz_high_vol': 0.80,      # -20% em alta volatilidade EWZ
            'dark_pool_selling': 0.75, # -25% em atividade dark pool negativa
            'policy_negative': 0.85,   # -15% em sentimento político negativo
        }

        prob_ajustada = probabilidade_base

        # Aplicar multiplicadores para fatores presentes
        for fator, presente in fatores_ajuste.items():
            if presente and fator in multiplicadores:
                prob_ajustada *= multiplicadores[fator]
                self.logger.info(f"🔧 Aplicado multiplicador {multiplicadores[fator]} para {fator}")

        # Aplicar limites de segurança (5%-95%)
        prob_ajustada = max(0.05, min(0.95, prob_ajustada))

        ajuste_pct = ((prob_ajustada - probabilidade_base) / probabilidade_base) * 100

        self.logger.info(f"🎯 Probabilidade ajustada: {probabilidade_base:.1%} → {prob_ajustada:.1%} ({ajuste_pct:+.1f}%)")

        return prob_ajustada

    def aplicar_ajustes_performance(self) -> Dict[str, float]:
        """
        Aplica ajustes específicos baseados na análise de performance de 2025-11-07

        Returns:
            Novos pesos aplicados
        """
        # Ajustes baseados na análise de performance
        ajustes_especificos = {
            'score_macro': -0.03,      # -3% - subestimado impacto negativo payrolls
            'score_tecnico': -0.02,    # -2% - superestimado em pânico de venda
            'volatilidade': 0.03,      # +3% - velocidade de movimento subestimada
            'ewz_correlation': 0.012,  # Novo fator - correlação EWZ ignorada
            'quant_flow': 0.015,       # Novo fator - vendas quant não previstas
            'central_bank_news': 0.012 # Novo fator - notícias BC subestimadas
        }

        self.logger.info("🔄 Aplicando ajustes baseados na análise de performance 2025-11-07")
        self.logger.info(f"Ajustes: {ajustes_especificos}")

        return self.aplicar_ajustes_pesos(ajustes_especificos)

    def aplicar_ajustes_pesos(self, ajustes: Dict[str, float]) -> Dict[str, float]:
        """
        Aplica ajustes aos pesos do sistema

        Args:
            ajustes: Dicionário com ajustes percentuais por fator

        Returns:
            Novos pesos aplicados
        """

        novos_pesos = self.pesos_atuais.copy()

        for fator, ajuste_pct in ajustes.items():
            if fator in novos_pesos:
                novos_pesos[fator] += ajuste_pct
                # Garantir que pesos não fiquem negativos
                novos_pesos[fator] = max(0.0, novos_pesos[fator])

        # Normalizar pesos para somar 100%
        total = sum(novos_pesos.values())
        if total > 0:
            novos_pesos = {k: v/total for k, v in novos_pesos.items()}

        # Registrar no histórico
        self.historico_ajustes.append({
            'timestamp': datetime.now(),
            'ajustes_aplicados': ajustes,
            'pesos_anteriores': self.pesos_atuais.copy(),
            'pesos_novos': novos_pesos.copy()
        })

        self.pesos_atuais = novos_pesos

        self.logger.info(f"🔄 Pesos ajustados: {novos_pesos}")

        return novos_pesos

    def salvar_analise(self, analise: AnalisePerformance):
        """Salva análise no banco de dados"""

        if not os.path.exists(self.db_path):
            self._criar_tabela_analises()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Inserir análise
        cursor.execute('''
            INSERT INTO analises_performance (
                recomendacao_id, timestamp_analise, resultado_real,
                movimento_preco_observado, eventos_ocorridos,
                probabilidade_prevista, probabilidade_real,
                timeframe_estimado, timeframe_real,
                catalisadores_previstos, catalisadores_reais,
                risco_previsto, risco_real,
                pontos_positivos, pontos_melhoria,
                sinais_subestimados, sinais_superestimados,
                calibracao_probabilidades, novos_inputs_sugeridos,
                ajustes_pesos, confianca_ajuste
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analise.recomendacao_id,
            analise.timestamp_analise.isoformat(),
            analise.resultado_real,
            analise.movimento_preco_observado,
            analise.eventos_ocorridos,
            analise.probabilidade_prevista,
            analise.probabilidade_real,
            analise.timeframe_estimado,
            analise.timeframe_real,
            json.dumps(analise.catalisadores_previstos),
            json.dumps(analise.catalisadores_reais),
            analise.risco_previsto,
            analise.risco_real,
            json.dumps(analise.pontos_positivos),
            json.dumps(analise.pontos_melhoria),
            json.dumps(analise.sinais_subestimados),
            json.dumps(analise.sinais_superestimados),
            analise.calibracao_probabilidades,
            json.dumps(analise.novos_inputs_sugeridos),
            json.dumps(analise.ajustes_pesos),
            analise.confianca_ajuste
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"💾 Análise salva para recomendação {analise.recomendacao_id}")

    def _criar_tabela_analises(self):
        """Cria tabela para armazenar análises de performance"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analises_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recomendacao_id INTEGER NOT NULL,
                timestamp_analise TEXT NOT NULL,
                resultado_real TEXT NOT NULL,
                movimento_preco_observado TEXT,
                eventos_ocorridos TEXT,
                probabilidade_prevista REAL,
                probabilidade_real REAL,
                timeframe_estimado TEXT,
                timeframe_real TEXT,
                catalisadores_previstos TEXT,
                catalisadores_reais TEXT,
                risco_previsto REAL,
                risco_real REAL,
                pontos_positivos TEXT,
                pontos_melhoria TEXT,
                sinais_subestimados TEXT,
                sinais_superestimados TEXT,
                calibracao_probabilidades TEXT,
                novos_inputs_sugeridos TEXT,
                ajustes_pesos TEXT,
                confianca_ajuste TEXT,
                FOREIGN KEY (recomendacao_id) REFERENCES recomendacoes (id)
            )
        ''')

        conn.commit()
        conn.close()

    def obter_metricas_aprendizado(self) -> Dict:
        """
        Obtém métricas consolidadas do sistema de aprendizado

        Returns:
            Dicionário com métricas de aprendizado
        """

        # Criar tabela se não existir
        self._criar_tabela_analises()

        if not os.path.exists(self.db_path):
            return {"erro": "Banco de dados não encontrado"}

        conn = sqlite3.connect(self.db_path)

        try:
            # Contar análises realizadas
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM analises_performance")
            total_analises = cursor.fetchone()[0]

            # Taxa de acerto das análises
            cursor.execute("""
                SELECT
                    AVG(probabilidade_real) as taxa_acerto_medio,
                    COUNT(CASE WHEN probabilidade_real > 0.5 THEN 1 END) as acertos,
                    COUNT(CASE WHEN probabilidade_real <= 0.5 THEN 1 END) as erros
                FROM analises_performance
            """)

            resultado = cursor.fetchone()
            taxa_acerto_medio = resultado[0] or 0
            acertos = resultado[1] or 0
            erros = resultado[2] or 0

            # Ajustes mais comuns
            cursor.execute("""
                SELECT ajustes_pesos
                FROM analises_performance
                WHERE ajustes_pesos IS NOT NULL
                ORDER BY timestamp_analise DESC
                LIMIT 10
            """)

            ajustes_recentes = []
            for row in cursor.fetchall():
                try:
                    ajustes = json.loads(row[0])
                    ajustes_recentes.append(ajustes)
                except:
                    continue

            return {
                "total_analises": total_analises,
                "taxa_acerto_medio": taxa_acerto_medio,
                "acertos": acertos,
                "erros": erros,
                "taxa_acerto_percentual": acertos / max(total_analises, 1),
                "ajustes_recentes": ajustes_recentes,
                "pesos_atuais": self.pesos_atuais.copy(),
                "historico_ajustes": len(self.historico_ajustes)
            }

        except Exception as e:
            return {"erro": f"Erro ao consultar métricas: {e}"}
        finally:
            conn.close()


def main():
    """Demonstração do sistema de aprendizado contínuo"""

    print("🧠 SISTEMA DE APRENDIZADO CONTÍNUO")
    print("=" * 50)

    # Inicializar sistema
    sistema = SistemaAprendizadoContinuo()

    # Exemplo de uso
    print("\n📝 Exemplo de Análise de Performance:")

    analise = sistema.executar_prompt_aprendizado(
        recomendacao_id=42,
        resultado_real="ACERTOU - TP1 atingido em +380 pontos",
        movimento_preco_observado="WIN subiu 420 pontos em 3.5h",
        eventos_ocorridos="Dados de emprego EUA melhores que esperado, Fed hints dovish"
    )

    print(analise)

    # Aplicar ajustes sugeridos (simulado)
    print("\n🔄 Aplicando ajustes de pesos...")
    ajustes_exemplo = {
        'score_macro': 0.05,  # +5%
        'score_tecnico': 0.03  # +3%
    }

    novos_pesos = sistema.aplicar_ajustes_pesos(ajustes_exemplo)
    print(f"✅ Novos pesos aplicados: {novos_pesos}")

    # Métricas do sistema
    print("\n📊 Métricas do Sistema de Aprendizado:")
    metricas = sistema.obter_metricas_aprendizado()
    print(f"Total de análises: {metricas['total_analises']}")
    print(f"Taxa de acerto atual: {metricas['taxa_acerto_medio']:.1%}")
    print(f"Pesos atuais: {metricas['pesos_atuais']}")

    return sistema


if __name__ == "__main__":
    sistema = main()