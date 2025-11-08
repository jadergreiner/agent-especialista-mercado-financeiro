#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator aprimorado de dados do WIN do boletim B3 com integração na análise
"""

import pdfplumber
import re
import sys
from datetime import datetime

def extrair_dados_win_boletim_melhorado(arquivo_pdf):
    """Extrai dados específicos do WIN do boletim B3 com melhor precisão"""
    dados_extraidos = {
        'data_pregao': None,
        'win_preco_liquidacao': None,
        'win_volume_contratos': None,
        'win_volume_financeiro': None,
        'ibov_preco_fechamento': None,
        'ibov_preco_liquidacao': None,
        'volume_total_mercado': None,
        'contratos_negociados_total': None,
        'taxa_cambio_ptax': None,
        'taxa_cambio_cupom': None
    }

    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            texto_completo = ""

            # Extrair texto de todas as páginas
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() + "\n"

            # Buscar data do pregão
            match_data = re.search(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if match_data:
                dados_extraidos['data_pregao'] = match_data.group(1)

            # Procurar especificamente por dados do WIN
            linhas = texto_completo.split('\n')

            for linha in linhas:
                linha_upper = linha.upper()

                # WIN - Preço de liquidação
                if 'WIN FUTURO DE MINI INDICE BOVESPA' in linha_upper and 'PREÇO DE LIQUIDAÇÃO' in linha_upper:
                    match_preco = re.search(r'(\d+[,.]\d+)', linha)
                    if match_preco:
                        preco_str = match_preco.group(1).replace(',', '.')
                        dados_extraidos['win_preco_liquidacao'] = float(preco_str)
                        print(f"WIN Preço Liquidação encontrado: {dados_extraidos['win_preco_liquidacao']}")

                # WIN - Volume e contratos (linha com MÍNI ÍNDICES WIN)
                elif 'MÍNI ÍNDICES WIN:' in linha_upper and 'IBOVESPA MÍNI FUTURO' in linha_upper:
                    # Extrair números da linha
                    numeros = re.findall(r'(\d+[,.]?\d*)', linha)
                    if len(numeros) >= 5:
                        # Formato típico: contratos, volume financeiro, volume contratos, etc.
                        try:
                            dados_extraidos['win_volume_contratos'] = float(numeros[0].replace('.', ''))
                            dados_extraidos['win_volume_financeiro'] = float(numeros[2].replace('.', '').replace(',', '.'))
                            print(f"WIN Volume Contratos: {dados_extraidos['win_volume_contratos']}")
                            print(f"WIN Volume Financeiro: {dados_extraidos['win_volume_financeiro']}")
                        except (ValueError, IndexError) as e:
                            print(f"Erro ao processar volumes WIN: {e}")

                # IBOVESPA - Preço de fechamento
                elif 'IND:' in linha_upper and 'IBOVESPA FUTURO' in linha_upper:
                    match_ibov = re.findall(r'(\d+[,.]\d+)', linha)
                    if match_ibov and len(match_ibov) >= 3:
                        try:
                            dados_extraidos['ibov_preco_fechamento'] = float(match_ibov[2].replace('.', '').replace(',', '.'))
                            print(f"IBOV Preço Fechamento: {dados_extraidos['ibov_preco_fechamento']}")
                        except (ValueError, IndexError):
                            pass

                # IBOVESPA - Preço de liquidação
                elif 'IND FUTURO DE INDICE BOVESPA' in linha_upper and 'LIQUIDAÇÃO' in linha_upper:
                    match_liq = re.search(r'(\d+[,.]\d+)', linha)
                    if match_liq:
                        liq_str = match_liq.group(1).replace(',', '.')
                        dados_extraidos['ibov_preco_liquidacao'] = float(liq_str)
                        print(f"IBOV Preço Liquidação: {dados_extraidos['ibov_preco_liquidacao']}")

                # Volume total do mercado
                elif 'VOLUME TOTAL' in linha_upper and any(x in linha_upper for x in ['DERIVATIVOS', 'MERCADO']):
                    match_vol = re.search(r'(\d+[,.]\d+)', linha)
                    if match_vol:
                        vol_str = match_vol.group(1).replace(',', '.')
                        dados_extraidos['volume_total_mercado'] = float(vol_str)
                        print(f"Volume Total Mercado: {dados_extraidos['volume_total_mercado']}")

                # Contratos negociados total
                elif 'CONTRATOS NEGOCIADOS' in linha_upper:
                    match_contr = re.search(r'(\d+)', linha)
                    if match_contr:
                        dados_extraidos['contratos_negociados_total'] = int(match_contr.group(1))
                        print(f"Contratos Negociados Total: {dados_extraidos['contratos_negociados_total']}")

                # Taxa de câmbio PTAX
                elif 'PTAX' in linha_upper and 'VENDA' in linha_upper:
                    match_ptax = re.search(r'(\d+[,.]\d+)', linha)
                    if match_ptax:
                        ptax_str = match_ptax.group(1).replace(',', '.')
                        dados_extraidos['taxa_cambio_ptax'] = float(ptax_str)
                        print(f"PTAX Venda: {dados_extraidos['taxa_cambio_ptax']}")

                # Taxa de câmbio Cupom Limpo
                elif 'CUPOM LIMPO' in linha_upper and 'DÓLAR' in linha_upper:
                    match_cupom = re.search(r'(\d+[,.]\d+)', linha)
                    if match_cupom:
                        cupom_str = match_cupom.group(1).replace(',', '.')
                        dados_extraidos['taxa_cambio_cupom'] = float(cupom_str)
                        print(f"Câmbio Cupom Limpo: {dados_extraidos['taxa_cambio_cupom']}")

    except Exception as e:
        print(f"Erro ao processar PDF: {e}")
        return None

    return dados_extraidos

def analisar_impacto_boletim_melhorado(dados):
    """Analisa o impacto dos dados do boletim no trading com foco no WIN"""
    if not dados:
        return {"score": 0, "analise": "Dados não disponíveis"}

    analise = {
        "score": 0,
        "fatores": [],
        "niveis_tecnicos": {},
        "volume_analise": "",
        "cambio_analise": "",
        "resumo": "",
        "recomendacao_win": ""
    }

    # Análise de preço do WIN
    if dados.get('win_preco_liquidacao'):
        preco_win = dados['win_preco_liquidacao']
        analise['niveis_tecnicos']['win_preco_liquidacao'] = preco_win

        # Comparar com IBOV se disponível
        if dados.get('ibov_preco_liquidacao'):
            ibov_liq = dados['ibov_preco_liquidacao']
            relacao_win_ibov = preco_win / ibov_liq
            analise['niveis_tecnicos']['relacao_win_ibov'] = relacao_win_ibov

            if relacao_win_ibov < 0.2:  # WIN deveria ser próximo ao IBOV
                analise['score'] -= 1
                analise['fatores'].append("WIN muito descontado vs IBOV [-1]")
            else:
                analise['fatores'].append("WIN com relação normal vs IBOV [0]")

        # Análise de nível técnico do WIN
        if preco_win > 155000:
            analise['score'] += 1
            analise['fatores'].append("WIN acima de resistência chave 155k [+1]")
        elif preco_win < 145000:
            analise['score'] -= 1
            analise['fatores'].append("WIN abaixo de suporte chave 145k [-1]")
        else:
            analise['fatores'].append("WIN em zona neutra [0]")

    # Análise de volume do WIN
    if dados.get('win_volume_financeiro'):
        vol_win = dados['win_volume_financeiro']
        analise['volume_analise'] = f"Volume WIN: R$ {vol_win:,.0f}"

        if vol_win > 2000000000:  # R$ 2 bi
            analise['score'] += 1
            analise['fatores'].append("Volume alto no WIN [+1]")
        elif vol_win < 500000000:  # R$ 500 mi
            analise['score'] -= 1
            analise['fatores'].append("Volume baixo no WIN [-1]")
        else:
            analise['fatores'].append("Volume normal no WIN [0]")

    # Análise de câmbio
    if dados.get('taxa_cambio_cupom'):
        cambio = dados['taxa_cambio_cupom']
        analise['cambio_analise'] = f"Câmbio: R$ {cambio:.4f}"

        if cambio > 5.50:
            analise['score'] -= 1
            analise['fatores'].append("Câmbio em nível alto [-1]")
        elif cambio < 5.00:
            analise['score'] += 1
            analise['fatores'].append("Câmbio em nível baixo [+1]")
        else:
            analise['fatores'].append("Câmbio em nível neutro [0]")

    # Resumo da análise
    analise['resumo'] = f"Score Boletim B3: {analise['score']:+d}"

    if analise['score'] >= 2:
        analise['resumo'] += " → POSITIVO para WIN"
        analise['recomendacao_win'] = "LONG no WINZ25"
    elif analise['score'] <= -2:
        analise['resumo'] += " → NEGATIVO para WIN"
        analise['recomendacao_win'] = "SHORT no WINZ25"
    else:
        analise['resumo'] += " → NEUTRO"
        analise['recomendacao_win'] = "AGUARDAR no WINZ25"

    return analise

def integrar_analise_boletim_win(analise_atual, dados_boletim):
    """Integra dados do boletim na análise atual do WIN"""
    if not dados_boletim:
        return analise_atual

    analise_boletim = analisar_impacto_boletim_melhorado(dados_boletim)

    # Adicionar seção do boletim na análise
    analise_integrada = analise_atual + "\n\n" + "="*60 + "\n"
    analise_integrada += "📊 DADOS DO BOLETIM B3 - WIN\n"
    analise_integrada += "="*60 + "\n\n"

    # Dados extraídos
    if dados_boletim.get('data_pregao'):
        analise_integrada += f"Data do Pregão: {dados_boletim['data_pregao']}\n"

    if dados_boletim.get('win_preco_liquidacao'):
        preco = dados_boletim['win_preco_liquidacao']
        analise_integrada += f"WIN Preço Liquidação: {preco:,.0f} pontos\n"

    if dados_boletim.get('win_volume_financeiro'):
        vol = dados_boletim['win_volume_financeiro']
        analise_integrada += f"WIN Volume Financeiro: R$ {vol:,.0f}\n"

    if dados_boletim.get('taxa_cambio_cupom'):
        cambio = dados_boletim['taxa_cambio_cupom']
        analise_integrada += f"Câmbio Cupom Limpo: R$ {cambio:.4f}\n"

    analise_integrada += "\n" + "🎯 ANÁLISE DE IMPACTO:\n"
    analise_integrada += f"Score: {analise_boletim['score']}\n\n"

    for fator in analise_boletim['fatores']:
        analise_integrada += f"• {fator}\n"

    analise_integrada += f"\n{analise_boletim['resumo']}\n"
    analise_integrada += f"Recomendação Boletim: {analise_boletim['recomendacao_win']}\n"

    return analise_integrada

if __name__ == '__main__':
    arquivo = r'c:\repo\projetos\agent-especialista-mercado-financeiro\backend\data\boletins_b3\raw\2024-11\BDI_00_20251106.pdf'

    print("🔍 ANÁLISE MELHORADA DO BOLETIM B3 - WIN")
    print("=" * 60)

    dados = extrair_dados_win_boletim_melhorado(arquivo)

    if dados:
        print("\n📊 DADOS EXTRAÍDOS:")
        for chave, valor in dados.items():
            if valor is not None:
                if isinstance(valor, float):
                    if 'preco' in chave:
                        print(f"  {chave}: {valor:,.0f}")
                    elif 'volume' in chave or 'financeiro' in chave:
                        print(f"  {chave}: R$ {valor:,.0f}")
                    else:
                        print(f"  {chave}: {valor:.4f}")
                else:
                    print(f"  {chave}: {valor}")

        print("\n" + "="*60)
        analise = analisar_impacto_boletim_melhorado(dados)

        print("🎯 ANÁLISE DE IMPACTO:")
        print(f"Score: {analise['score']}")
        print("\nFatores:")
        for fator in analise['fatores']:
            print(f"  • {fator}")

        print(f"\nResumo: {analise['resumo']}")
        print(f"Recomendação: {analise['recomendacao_win']}")

        if analise['niveis_tecnicos']:
            print("\n📈 NÍVEIS TÉCNICOS:")
            nt = analise['niveis_tecnicos']
            for chave, valor in nt.items():
                if isinstance(valor, float):
                    if 'preco' in chave or 'win_' in chave:
                        print(f"  {chave}: {valor:,.0f}")
                    else:
                        print(f"  {chave}: {valor:.4f}")
                else:
                    print(f"  {chave}: {valor}")
    else:
        print("❌ Erro na extração de dados")