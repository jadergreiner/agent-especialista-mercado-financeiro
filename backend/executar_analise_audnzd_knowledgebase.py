#!/usr/bin/env python3
"""
EXECUÇÃO DA ANÁLISE QUANTITATIVA AUDNZD COM KNOWLEDGEBASE
Script principal para executar análise completa incluindo notícias e indicadores econômicos

KNOWLEDGEBASE ECONÔMICO IMPLEMENTADO:
✅ Notícias recentes da Austrália e Nova Zelândia
✅ Indicadores econômicos atualizados
✅ Impactos no par AUDNZD
✅ Análise fundamental integrada
✅ Sinais de trading combinados
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analisador_quantitativo_audnzd_knowledgebase import AnalisadorQuantitativoAUDNZD

def executar_analise_audnzd_knowledgebase() -> None:
    """
    Executar análise quantitativa completa do AUDNZD com KNOWLEDGEBASE
    INCLUI: Notícias, indicadores econômicos, análise técnica e sinais de trading
    """
    print("� INICIANDO ANÁLISE QUANTITATIVA AUDNZD COM KNOWLEDGEBASE")
    print("=" * 80)

    try:
        # Inicializar analisador
        analisador = AnalisadorQuantitativoAUDNZD()

        # Executar análise completa
        resultado = analisador.executar_analise_quantitativa_completa()

        if resultado['status'] == 'concluido_com_sucesso':
            # Exibir resultados formatados
            exibir_resultados_formatados(resultado)
        else:
            print(f"❌ ERRO na análise: {resultado.get('erro', 'Erro desconhecido')}")

    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

def exibir_resultados_formatados(resultado: Dict[str, Any]) -> None:
    """Exibir resultados da análise de forma organizada"""

    print("📊 DADOS BÁSICOS AUDNZD")
    print("-" * 40)
    dados = resultado['dados_basicos']
    print(f"Preço Atual: {dados['preco_atual']}")
    print(f"Variação 24h: {dados['variacao_24h']:.2%}")
    print(f"Período: {dados['periodo_analisado']}")
    print()

    # KNOWLEDGEBASE - Análise Fundamental
    print("📰 KNOWLEDGEBASE - ANÁLISE FUNDAMENTAL")
    print("=" * 80)

    fundamental = resultado['knowledgebase_fundamental']

    # Austrália
    print("🇦🇺 AUSTRÁLIA")
    print("-" * 20)
    aus = fundamental['australia']
    print(f"Sentimento: {aus['sentimento']['classificacao']} (Score: {aus['sentimento']['score']})")
    print(f"Taxa de Juros: {aus['indicadores_chave']['taxa_juros']}%")
    print(f"Inflação: {aus['indicadores_chave']['inflacao']:.1f}%")
    print(f"PIB: +{aus['indicadores_chave']['pib_crescimento']:.1f}%")
    print(f"Desemprego: {aus['indicadores_chave']['desemprego']:.1f}%")
    print("Notícias Principais:")
    for noticia in aus['noticias_principais']:
        print(f"  • {noticia}")
    print()

    # Nova Zelândia
    print("🇳🇿 NOVA ZELÂNDIA")
    print("-" * 20)
    nzd = fundamental['new_zealand']
    print(f"Sentimento: {nzd['sentimento']['classificacao']} (Score: {nzd['sentimento']['score']})")
    print(f"Taxa de Juros: {nzd['indicadores_chave']['taxa_juros']}%")
    print(f"Inflação: {nzd['indicadores_chave']['inflacao']:.1f}%")
    print(f"PIB: +{nzd['indicadores_chave']['pib_crescimento']:.1f}%")
    print(f"Desemprego: {nzd['indicadores_chave']['desemprego']:.1f}%")
    print("Notícias Principais:")
    for noticia in nzd['noticias_principais']:
        print(f"  • {noticia}")
    print()

    # Dinâmica AUDNZD
    print("💱 DINÂMICA AUDNZD")
    print("-" * 20)
    dynamics = fundamental['audnzd_dynamics']
    print(f"Diferencial de Taxas: {dynamics['diferencial_taxas']:.2f}%")
    print("Forças AUD:")
    for forca in dynamics['forcas_aud']:
        print(f"  • {forca}")
    print("Forças NZD:")
    for forca in dynamics['forcas_nzd']:
        print(f"  • {forca}")
    print()

    # Impacto no Par
    print("📈 IMPACTO NO PAR AUDNZD")
    print("-" * 25)
    impacto = fundamental['impacto_no_par']
    print(f"Viés AUD: {impacto['vies_aud']}")
    print(f"Viés NZD: {impacto['vies_nzd']}")
    print(f"Impacto Líquido: {impacto['impacto_liquido']}")
    print(f"Força Diferencial: {impacto['forca_diferencial']:.1f} pontos")
    print(f"Interpretação: {impacto['interpretacao']}")
    print(f"Probabilidade Alta: {impacto['probabilidade_alta']}")
    print()

    # Sentimento Geral
    print("🎯 SENTIMENTO GERAL DO MERCADO")
    print("-" * 30)
    sentimento = fundamental['sentimento_mercado']
    print(f"Sentimento AUD: {sentimento['sentimento_aud']}")
    print(f"Sentimento NZD: {sentimento['sentimento_nzd']}")
    print(f"Diferencial Taxas: {sentimento['diferencial_taxas']:.2f}%")
    vies = sentimento['vies_geral']
    print(f"Viés Geral: {vies['vies_principal']}")
    print(f"Confiança: {vies['confianca']}")
    print(f"Recomendação: {vies['recomendacao']}")
    print()

    # Análise Técnica
    print("📈 ANÁLISE TÉCNICA QUANTITATIVA")
    print("=" * 80)
    tecnica = resultado['analise_tecnica']

    # Médias Móveis
    print("� MÉDIAS MÓVEIS")
    print("-" * 15)
    medias = tecnica['medias_moveis']
    print(f"SMA 20: {medias['SMA_20']} ({medias['posicao_vs_sma20']})")
    print(f"SMA 50: {medias['SMA_50']} ({medias['posicao_vs_sma50']})")
    print(f"EMA 12: {medias['EMA_12']}")
    print(f"EMA 26: {medias['EMA_26']}")
    print()

    # RSI
    print("📊 RSI (ÍNDICE DE FORÇA RELATIVA)")
    print("-" * 30)
    rsi = tecnica['rsi']
    print(f"Valor Atual: {rsi['valor_atual']}")
    print(f"Interpretação: {rsi['interpretacao']}")
    print()

    # MACD
    print("📊 MACD (CONVERGÊNCIA/DIVERGÊNCIA MÉDIAS MÓVEIS)")
    print("-" * 45)
    macd = tecnica['macd']
    print(f"MACD: {macd['macd']}")
    print(f"Linha de Sinal: {macd['signal']}")
    print(f"Sinal: {macd['sinal']}")
    print()

    # Bollinger Bands
    print("📊 BOLLINGER BANDS")
    print("-" * 15)
    bb = tecnica['bollinger_bands']
    print(f"Upper: {bb['upper']}")
    print(f"Middle: {bb['middle']}")
    print(f"Lower: {bb['lower']}")
    print(f"Posição: {bb['posicao']}")
    print()

    # Volatilidade
    print("📊 VOLATILIDADE")
    print("-" * 12)
    vol = tecnica['volatilidade']
    print(f"ATR: {vol['atr']}")
    print(f"ATR %: {vol['atr_percentual']}%")
    print()

    # Sinais de Trading
    print("🚀 SINAIS DE TRADING INTEGRADOS")
    print("=" * 80)
    sinais = resultado['sinais_trading']

    # Sinais de Compra
    if sinais['compra']:
        print("� SINAIS DE COMPRA")
        print("-" * 18)
        for sinal in sinais['compra']:
            print(f"• {sinal['tipo']} ({sinal['forca']}): {sinal['descricao']}")
        print()

    # Sinais de Venda
    if sinais['venda']:
        print("� SINAIS DE VENDA")
        print("-" * 18)
        for sinal in sinais['venda']:
            print(f"• {sinal['tipo']} ({sinal['forca']}): {sinal['descricao']}")
        print()

    # Sinais Neutros
    if sinais['neutro']:
        print("� SINAIS NEUTROS")
        print("-" * 16)
        for sinal in sinais['neutro']:
            print(f"• {sinal['tipo']} ({sinal['forca']}): {sinal['descricao']}")
        print()

    # Resumo dos Sinais
    print("📊 RESUMO DOS SINAIS")
    print("-" * 20)
    resumo = sinais['resumo']
    print(f"Sinal Principal: {resumo['sinal_principal']}")
    print(f"Confiança: {resumo['confianca']}")
    print(f"Total Sinais Compra: {resumo['total_sinais_compra']}")
    print(f"Total Sinais Venda: {resumo['total_sinais_venda']}")
    print(f"Total Sinais Neutro: {resumo['total_sinais_neutro']}")
    print(f"Viés Fundamental: {resumo['vies_fundamental']}")
    print()

    # Recomendação Final
    print("🎯 RECOMENDAÇÃO FINAL")
    print("=" * 80)
    print(resumo['recomendacao'])
    print()

    # Timestamp da análise
    print("⏰ TIMESTAMP DA ANÁLISE")
    print("-" * 22)
    print(f"Executado em: {resultado['timestamp_analise']}")
    print(f"Par Analisado: {resultado['par_analisado']}")
    print(f"KNOWLEDGEBASE Aplicado: {'✅ SIM' if resultado['knowledgebase_aplicado'] else '❌ NÃO'}")
    print()

    print("✅ ANÁLISE QUANTITATIVA AUDNZD COM KNOWLEDGEBASE CONCLUÍDA COM SUCESSO!")
    print("� Dados econômicos atualizados e análise integrada fundamental + técnica aplicada.")

if __name__ == "__main__":
    executar_analise_audnzd_knowledgebase()