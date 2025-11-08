#!/usr/bin/env python3
"""
SCRIPT DE EXECUÇÃO - AVALIAÇÃO QUANTITATIVA AUDNZD
"""

from analisador_quantitativo_audnzd import AnalisadorQuantitativoAUDNZD
from datetime import datetime

def main():
    print('🔬 AVALIAÇÃO QUANTITATIVA COMPLETA - AUDNZD')
    print('=' * 70)
    print('Data/Hora da Análise:', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print()

    # Executar análise completa
    analisador = AnalisadorQuantitativoAUDNZD()
    resultado = analisador.executar_analise_quantitativa_completa()

    if resultado['status'] == 'concluido_com_sucesso':
        # Dados básicos
        dados = resultado['dados_basicos']
        print('📊 DADOS BÁSICOS:')
        print(f'   Par: AUDNZD')
        print(f'   Preço Atual: {dados["preco_atual"]}')
        print('.2f')
        print(f'   Período: {dados["periodo_analisado"]}')
        print()

        # Análise Técnica
        tecnica = resultado['analise_tecnica']
        print('📈 ANÁLISE TÉCNICA QUANTITATIVA:')

        medias = tecnica['medias_moveis']
        print(f'   📊 MÉDIAS MÓVEIS:')
        print(f'      SMA 20: {medias["SMA_20"]} ({medias["posicao_vs_sma20"]})')
        print(f'      SMA 50: {medias["SMA_50"]} ({medias["posicao_vs_sma50"]})')
        print(f'      EMA 12/26: {medias["EMA_12"]} / {medias["EMA_26"]}')

        rsi = tecnica['rsi']
        print(f'   🎯 RSI: {rsi["valor_atual"]} - {rsi["interpretacao"]}')

        macd = tecnica['macd']
        print(f'   📊 MACD: {macd["macd"]} (Signal: {macd["signal"]}) - {macd["sinal"]}')

        bb = tecnica['bollinger_bands']
        print(f'   📊 BOLLINGER BANDS:')
        print(f'      Upper: {bb["upper"]} | Middle: {bb["middle"]} | Lower: {bb["lower"]}')
        print(f'      Posição: {bb["posicao"]}')

        vol = tecnica['volatilidade']
        print('.2f')
        print()

        # Análise Estatística
        estat = resultado['analise_estatistica']
        print('📊 ANÁLISE ESTATÍSTICA:')

        desc = estat['descritiva']
        print('.4f')
        print('.2f')
        print(f'   📊 AMPLITUDE TOTAL: {desc["amplitude_total"]}%')
        print(f'   📈 MÁX/MÍN PERÍODO: {desc["maximo_periodo"]} / {desc["minimo_periodo"]}')

        dist = estat['distribuicao']
        print(f'   📊 DISTRIBUIÇÃO: Skewness {dist["skewness"]} | Kurtosis {dist["kurtosis"]}')
        print()

        # Correlações
        corr = resultado['analise_correlacao']
        print('🔗 ANÁLISE DE CORRELAÇÃO:')

        if 'correlacoes' in corr:
            print('   📊 Correlações com AUDNZD:')
            for par, valor in corr['correlacoes'].items():
                interp = corr['interpretacao'][par]
                print(f'      {par}: {valor} - {interp}')

            mais_corr = corr['par_mais_correlacionado']
            print(f'   🎯 MAIS CORRELACIONADO: {mais_corr["par"]} ({mais_corr["correlacao"]})')
        print()

        # Análise de Risco
        risco = resultado['analise_risco']
        print('⚠️ ANÁLISE DE RISCO:')

        vol_risco = risco['volatilidade']
        print('.2f')

        risco_metrics = risco['risco']
        print('.2f')
        print('.2f')

        perf = risco['performance']
        print(f'   📈 SHARPE RATIO: {perf["sharpe_ratio"]}')
        print('.1f')

        classif = risco['classificacao']
        print(f'   🏷️ CLASSIFICAÇÃO: Volatilidade {classif["volatilidade"]} | Risco {classif["risco_global"]}')
        print()

        # Níveis Críticos
        niveis = resultado['niveis_criticos']
        print('🎯 NÍVEIS CRÍTICOS:')

        if niveis['suportes']:
            print(f'   📉 SUPORTES: {niveis["suportes"]}')
        if niveis['resistencias']:
            print(f'   📈 RESISTÊNCIAS: {niveis["resistencias"]}')

        prox = niveis['proximos']
        if prox['suporte_mais_proximo']:
            print(f'   🎯 SUPORTE PRÓXIMO: {prox["suporte_mais_proximo"]}')
        if prox['resistencia_mais_proxima']:
            print(f'   🎯 RESISTÊNCIA PRÓXIMA: {prox["resistencia_mais_proxima"]}')
        print()

        # Sinais de Trading
        sinais = resultado['sinais_trading']
        print('🚀 SINAIS DE TRADING:')

        print(f'   📊 SINAIS DE COMPRA ({len(sinais["compra"])}):')
        for sinal in sinais['compra']:
            print(f'      • {sinal["tipo"]} ({sinal["forca"]}) - {sinal["descricao"]}')

        print(f'   📊 SINAIS DE VENDA ({len(sinais["venda"])}):')
        for sinal in sinais['venda']:
            print(f'      • {sinal["tipo"]} ({sinal["forca"]}) - {sinal["descricao"]}')

        print(f'   📊 SINAIS NEUTROS ({len(sinais["neutro"])}):')
        for sinal in sinais['neutro']:
            print(f'      • {sinal["tipo"]} ({sinal["forca"]}) - {sinal["descricao"]}')

        resumo = sinais['resumo']
        print(f'   🎯 SINAL PRINCIPAL: {resumo["sinal_principal"]} (Confiança: {resumo["confianca"]})')
        print(f'   💡 RECOMENDAÇÃO: {resumo["recomendacao"]}')

    else:
        print('❌ ERRO na análise quantitativa:')
        print(f'   Status: {resultado["status"]}')
        if 'erro' in resultado:
            print(f'   Detalhes: {resultado["erro"]}')

    print()
    print('✅ ANÁLISE QUANTITATIVA AUDNZD CONCLUÍDA')

if __name__ == "__main__":
    main()