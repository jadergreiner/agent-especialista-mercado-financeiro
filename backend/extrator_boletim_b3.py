#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Dados do Boletim B3 - WIN
Análise específica para complementar trading
"""
import pdfplumber
import re
import sys
from datetime import datetime

def extrair_dados_win_boletim(arquivo_pdf):
    """Extrai dados relevantes do WIN do boletim B3"""
    dados_extraidos = {
        'data_pregao': None,
        'win_dados': {},
        'volume_total': None,
        'abertura_oficial': None,
        'fechamento_oficial': None,
        'maxima_dia': None,
        'minima_dia': None,
        'variacao_dia': None,
        'contratos_negociados': None,
        'ajuste_anterior': None,
        'volume_financeiro': None
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

            # Buscar dados do WIN (Mini Índice)
            # Padrões comuns em boletins B3
            padroes_win = [
                r'WIN.*?(\d+[,.]?\d*)',  # WIN seguido de números
                r'MINI.*IBOV.*?(\d+[,.]?\d*)',  # Mini Ibovespa
                r'IND.*(\d+[,.]?\d*)',  # Índice
            ]

            # Buscar valores específicos
            for linha in texto_completo.split('\n'):
                linha_upper = linha.upper()

                # Se contém WIN ou MINI IBOV
                if 'WIN' in linha_upper or ('MINI' in linha_upper and 'IBOV' in linha_upper):
                    # Extrair números da linha
                    numeros = re.findall(r'(\d+[,.]?\d*)', linha)
                    if numeros:
                        print(f"Linha WIN encontrada: {linha.strip()}")
                        print(f"Números extraídos: {numeros}")

                        # Tentar identificar preços (assumindo valores > 100.000)
                        for num in numeros:
                            valor_num = float(num.replace(',', '.'))
                            if valor_num > 100000:  # Valores típicos do WIN
                                if not dados_extraidos['fechamento_oficial']:
                                    dados_extraidos['fechamento_oficial'] = valor_num
                                elif not dados_extraidos['maxima_dia']:
                                    dados_extraidos['maxima_dia'] = valor_num
                                elif not dados_extraidos['minima_dia']:
                                    dados_extraidos['minima_dia'] = valor_num

            # Buscar volume total de derivativos
            match_volume = re.search(r'VOLUME.*?(\d+[,.]?\d*)', texto_completo, re.IGNORECASE)
            if match_volume:
                dados_extraidos['volume_total'] = match_volume.group(1)

            # Buscar contratos
            match_contratos = re.search(r'CONTRATOS.*?(\d+)', texto_completo, re.IGNORECASE)
            if match_contratos:
                dados_extraidos['contratos_negociados'] = match_contratos.group(1)

    except Exception as e:
        print(f"Erro ao processar PDF: {e}")
        return None

    return dados_extraidos

def analisar_impacto_boletim(dados):
    """Analisa o impacto dos dados do boletim no trading"""
    if not dados:
        return {"score": 0, "analise": "Dados não disponíveis"}

    analise = {
        "score": 0,
        "fatores": [],
        "niveis_tecnicos": {},
        "volume_analise": "",
        "resumo": ""
    }

    print("\n=== ANÁLISE DO BOLETIM B3 ===")
    print(f"Data do Pregão: {dados.get('data_pregao', 'N/A')}")

    # Análise de preços
    if dados.get('fechamento_oficial'):
        fechamento = dados['fechamento_oficial']
        print(f"Fechamento Oficial WIN: {fechamento:,.0f}")
        analise['niveis_tecnicos']['fechamento'] = fechamento

        if dados.get('maxima_dia') and dados.get('minima_dia'):
            maxima = dados['maxima_dia']
            minima = dados['minima_dia']
            range_dia = maxima - minima

            print(f"Máxima do Dia: {maxima:,.0f}")
            print(f"Mínima do Dia: {minima:,.0f}")
            print(f"Range do Dia: {range_dia:,.0f} pontos")

            # Posição do fechamento no range
            posicao_range = (fechamento - minima) / range_dia if range_dia > 0 else 0.5

            analise['niveis_tecnicos'].update({
                'maxima': maxima,
                'minima': minima,
                'range': range_dia,
                'posicao_range': posicao_range
            })

            # Scoring baseado na posição
            if posicao_range > 0.8:
                analise['score'] -= 2
                analise['fatores'].append("Fechamento próximo à máxima (resistência) [-2]")
            elif posicao_range < 0.2:
                analise['score'] += 2
                analise['fatores'].append("Fechamento próximo à mínima (suporte) [+2]")
            else:
                analise['fatores'].append("Fechamento no meio do range [0]")

    # Análise de volume
    if dados.get('volume_total'):
        volume = dados['volume_total']
        print(f"Volume Total: {volume}")
        analise['volume_analise'] = f"Volume: {volume}"

        # Assumindo volume alto como positivo para continuidade
        try:
            vol_num = float(volume.replace(',', '.'))
            if vol_num > 1000000:  # Volume alto
                analise['score'] += 1
                analise['fatores'].append("Volume alto (confirmação) [+1]")
            else:
                analise['fatores'].append("Volume baixo (incerteza) [0]")
        except:
            pass

    # Contratos negociados
    if dados.get('contratos_negociados'):
        contratos = dados['contratos_negociados']
        print(f"Contratos Negociados: {contratos}")

    # Resumo da análise
    analise['resumo'] = f"Score Boletim B3: {analise['score']:+d}"

    if analise['score'] >= 2:
        analise['resumo'] += " → POSITIVO para WIN"
    elif analise['score'] <= -2:
        analise['resumo'] += " → NEGATIVO para WIN"
    else:
        analise['resumo'] += " → NEUTRO"

    return analise

if __name__ == '__main__':
    arquivo = r'c:\repo\projetos\agent-especialista-mercado-financeiro\backend\data\boletins_b3\raw\2024-11\BDI_00_20251105.pdf'

    print("🔍 ANÁLISE DO BOLETIM B3 - WIN")
    print("=" * 50)

    dados = extrair_dados_win_boletim(arquivo)

    if dados:
        analise = analisar_impacto_boletim(dados)

        print("\n📊 IMPACTO NO TRADING:")
        for fator in analise['fatores']:
            print(f"  • {fator}")

        print(f"\n🎯 {analise['resumo']}")

        if analise['niveis_tecnicos']:
            print(f"\n📈 NÍVEIS TÉCNICOS B3:")
            nt = analise['niveis_tecnicos']
            if 'fechamento' in nt:
                print(f"  Fechamento: {nt['fechamento']:,.0f}")
            if 'maxima' in nt and 'minima' in nt:
                print(f"  Range: {nt['minima']:,.0f} - {nt['maxima']:,.0f}")
                print(f"  Posição: {nt['posicao_range']*100:.1f}% do range")
    else:
        print("❌ Não foi possível extrair dados do boletim")