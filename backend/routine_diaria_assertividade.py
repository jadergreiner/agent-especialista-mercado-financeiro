#!/usr/bin/env python3
"""
Rotina Diária de Assertividade - Sistema Especialista Mercado Financeiro

Esta rotina executa diariamente para:
1. Persistir oportunidades calculadas
2. Comparar com dias anteriores
3. Calcular métricas de assertividade
4. Sugerir melhorias no modelo

Autor: Sistema Especialista Mercado Financeiro
Data: 2025-11-07
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

class AvaliadorAssertividade:
    """Avalia a assertividade das oportunidades de trading ao longo do tempo."""

    def __init__(self, caminho_base: str = "backend/data"):
        self.caminho_base = Path(caminho_base)
        self.caminho_oportunidades = self.caminho_base / "oportunidades"
        self.caminho_assertividade = self.caminho_base / "assertividade"
        self.caminho_assertividade.mkdir(exist_ok=True)

    def executar_rotina_diaria(self) -> Dict[str, Any]:
        """
        Executa a rotina completa diária de avaliação de assertividade.

        Returns:
            Dict com métricas e sugestões de melhoria
        """
        print("🔄 Iniciando rotina diária de assertividade...")

        # 1. Coletar oportunidades dos últimos 30 dias
        oportunidades_historicas = self._coletar_oportunidades_historicas()

        # 2. Calcular métricas de assertividade
        metricas = self._calcular_metricas_assertividade(oportunidades_historicas)

        # 3. Identificar padrões de sucesso/fracasso
        padroes = self._identificar_padroes(metricas)

        # 4. Gerar sugestões de melhoria
        sugestoes = self._gerar_sugestoes_melhoria(metricas, padroes)

        # 5. Persistir resultados
        resultado = {
            "timestamp": datetime.now().isoformat(),
            "periodo_analisado": "30_dias",
            "metricas": metricas,
            "padroes": padroes,
            "sugestoes": sugestoes
        }

        self._persistir_resultado_assertividade(resultado)

        print("✅ Rotina diária concluída!")
        return resultado

    def _coletar_oportunidades_historicas(self, dias: int = 30) -> List[Dict]:
        """Coleta oportunidades dos últimos N dias."""
        oportunidades = []
        data_atual = datetime.now()

        for i in range(dias):
            data = data_atual - timedelta(days=i)
            padrao_arquivo = f"oportunidades_{data.strftime('%Y%m%d')}_*.json"

            arquivos = list(self.caminho_oportunidades.glob(padrao_arquivo))
            for arquivo in arquivos:
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                        # Adicionar data do arquivo aos dados
                        dados['data_arquivo'] = data.strftime('%Y-%m-%d')
                        oportunidades.extend(dados.get('oportunidades', []))
                except Exception as e:
                    print(f"⚠️ Erro ao ler {arquivo}: {e}")

        return oportunidades

    def _calcular_metricas_assertividade(self, oportunidades: List[Dict]) -> Dict[str, Any]:
        """Calcula métricas de assertividade das oportunidades."""
        if not oportunidades:
            return {"erro": "Nenhuma oportunidade encontrada"}

        df = pd.DataFrame(oportunidades)

        metricas = {
            "total_oportunidades": len(df),
            "pares_unicos": df['par'].nunique() if 'par' in df.columns else 0,
            "probabilidade_media": df['probabilidade'].mean() if 'probabilidade' in df.columns else 0,
            "distribuicao_direcao": df['direcao'].value_counts().to_dict() if 'direcao' in df.columns else {},
            "pares_mais_oportunidades": df['par'].value_counts().head(5).to_dict() if 'par' in df.columns else {},
            "probabilidade_por_par": df.groupby('par')['probabilidade'].mean().to_dict() if 'par' in df.columns else {},
            "tendencia_probabilidade": self._calcular_tendencia_probabilidade(df)
        }

        return metricas

    def _calcular_tendencia_probabilidade(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula tendência das probabilidades ao longo do tempo."""
        if 'data_arquivo' not in df.columns or 'probabilidade' not in df.columns:
            return {"erro": "Dados insuficientes para tendência"}

        df['data'] = pd.to_datetime(df['data_arquivo'])
        tendencia = df.groupby('data')['probabilidade'].mean().reset_index()

        return {
            "probabilidade_media_diaria": tendencia.set_index('data')['probabilidade'].to_dict(),
            "tendencia_geral": "crescente" if tendencia['probabilidade'].is_monotonic_increasing else
                             "decrescente" if tendencia['probabilidade'].is_monotonic_decreasing else "neutra"
        }

    def _identificar_padroes(self, metricas: Dict) -> Dict[str, Any]:
        """Identifica padrões de sucesso e fracasso."""
        padroes = {
            "pares_de_alto_desempenho": [],
            "pares_de_baixo_desempenho": [],
            "probabilidades_otimas": {},
            "recomendacoes_direcao": {}
        }

        if "probabilidade_por_par" in metricas:
            probs_por_par = metricas["probabilidade_por_par"]

            # Pares com alta probabilidade (>70%)
            padroes["pares_de_alto_desempenho"] = [
                par for par, prob in probs_por_par.items() if prob > 0.7
            ]

            # Pares com baixa probabilidade (<60%)
            padroes["pares_de_baixo_desempenho"] = [
                par for par, prob in probs_por_par.items() if prob < 0.6
            ]

        # Análise de direções
        if "distribuicao_direcao" in metricas:
            dist_direcao = metricas["distribuicao_direcao"]
            total = sum(dist_direcao.values())
            padroes["recomendacoes_direcao"] = {
                direcao: (contagem / total) * 100
                for direcao, contagem in dist_direcao.items()
            }

        return padroes

    def _gerar_sugestoes_melhoria(self, metricas: Dict, padroes: Dict) -> List[str]:
        """Gera sugestões de melhoria baseadas nas métricas e padrões."""
        sugestoes = []

        # Sugestões baseadas em probabilidade média
        prob_media = metricas.get("probabilidade_media", 0)
        if prob_media < 0.65:
            sugestoes.append("🔧 Ajustar algoritmo de cálculo de probabilidade - média atual baixa")
        elif prob_media > 0.75:
            sugestoes.append("✅ Probabilidades bem calibradas - manter estratégia atual")

        # Sugestões baseadas em pares de alto desempenho
        pares_alto = padroes.get("pares_de_alto_desempenho", [])
        if pares_alto:
            sugestoes.append(f"🎯 Focar mais em pares de alto desempenho: {', '.join(pares_alto[:3])}")

        # Sugestões baseadas em pares de baixo desempenho
        pares_baixo = padroes.get("pares_de_baixo_desempenho", [])
        if pares_baixo:
            sugestoes.append(f"⚠️ Reavaliar estratégia para pares de baixo desempenho: {', '.join(pares_baixo[:3])}")

        # Sugestões baseadas em distribuição de direção
        recomendacoes_direcao = padroes.get("recomendacoes_direcao", {})
        if recomendacoes_direcao:
            direcao_predominante = max(recomendacoes_direcao, key=recomendacoes_direcao.get)
            percentual = recomendacoes_direcao[direcao_predominante]
            if percentual > 70:
                sugestoes.append(f"📈 Estratégia predominantemente {direcao_predominante} ({percentual:.1f}%) - considerar diversificação")

        # Sugestões gerais
        total_oportunidades = metricas.get("total_oportunidades", 0)
        if total_oportunidades < 10:
            sugestoes.append("📊 Coletar mais dados históricos para melhorar análise estatística")

        return sugestoes

    def _persistir_resultado_assertividade(self, resultado: Dict) -> None:
        """Persiste o resultado da avaliação de assertividade."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"assertividade_diaria_{timestamp}.json"

        caminho_arquivo = self.caminho_assertividade / nome_arquivo

        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)

        print(f"💾 Resultado salvo em: {caminho_arquivo}")

def main():
    """Função principal para execução da rotina diária."""
    print("🚀 Iniciando Rotina Diária de Assertividade")
    print("=" * 50)

    avaliador = AvaliadorAssertividade()

    try:
        resultado = avaliador.executar_rotina_diaria()

        print("\n📊 RESULTADO DA AVALIAÇÃO:")
        print(f"Total de oportunidades analisadas: {resultado['metricas'].get('total_oportunidades', 0)}")
        print(".2f")
        print(f"Pares únicos: {resultado['metricas'].get('pares_unicos', 0)}")

        print("\n💡 SUGESTÕES DE MELHORIA:")
        for sugestao in resultado.get('sugestoes', []):
            print(f"• {sugestao}")

        print("\n✅ Rotina concluída com sucesso!")

    except Exception as e:
        print(f"❌ Erro na execução da rotina: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())