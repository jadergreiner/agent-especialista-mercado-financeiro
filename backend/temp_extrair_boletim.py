#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script temporário para extrair dados do boletim B3
"""

import sys
import os
sys.path.append('.')

from extrator_boletim_b3 import extrair_dados_win_boletim, analisar_impacto_boletim

def main():
    # Processar o boletim específico
    arquivo_pdf = r'data\boletins_b3\raw\2024-11\BDI_00_20251106.pdf'

    print('🔍 EXTRAÇÃO DE DADOS DO BOLETIM B3 - WIN')
    print('=' * 60)
    print(f'Arquivo: {arquivo_pdf}')
    print()

    # Verificar se arquivo existe
    if not os.path.exists(arquivo_pdf):
        print(f'❌ Arquivo não encontrado: {arquivo_pdf}')
        return

    # Extrair dados
    dados = extrair_dados_win_boletim(arquivo_pdf)

    if dados:
        print('📊 DADOS EXTRAÍDOS:')
        for chave, valor in dados.items():
            if valor is not None:
                print(f'  {chave}: {valor}')

        print()
        # Analisar impacto
        analise = analisar_impacto_boletim(dados)

        print('🎯 ANÁLISE DE IMPACTO:')
        print(f'Score: {analise["score"]}')
        print()
        print('Fatores:')
        for fator in analise['fatores']:
            print(f'  • {fator}')

        print()
        print(f'Resumo: {analise["resumo"]}')

        if analise['niveis_tecnicos']:
            print()
            print('📈 NÍVEIS TÉCNICOS:')
            nt = analise['niveis_tecnicos']
            for chave, valor in nt.items():
                if isinstance(valor, float):
                    print(f'  {chave}: {valor:,.0f}')
                else:
                    print(f'  {chave}: {valor}')
    else:
        print('❌ Erro na extração de dados')

if __name__ == '__main__':
    main()