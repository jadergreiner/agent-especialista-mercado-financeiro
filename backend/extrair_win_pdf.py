# -*- coding: utf-8 -*-
"""
Extrai dados específicos do WIN do PDF do boletim B3.
"""

import pdfplumber
from pathlib import Path
from datetime import date
from decimal import Decimal
import re


def extrair_dados_win(caminho_pdf: Path):
    """Extrai dados do WIN de forma estruturada."""

    print(f"\n{'='*100}")
    print(f"EXTRAINDO DADOS DO WIN: {caminho_pdf.name}")
    print(f"{'='*100}\n")

    # Extrair data do nome do arquivo: BDI_00_20251104.pdf
    match = re.search(r'(\d{8})', caminho_pdf.name)
    if match:
        data_str = match.group(1)
        data_pregao = date(int(data_str[:4]), int(data_str[4:6]), int(data_str[6:8]))
        print(f"Data do pregao: {data_pregao.strftime('%d/%m/%Y')}\n")

    with pdfplumber.open(caminho_pdf) as pdf:
        # Página 6 (índice 5) tem o resumo diário
        page_resumo = pdf.pages[5]

        print("="*100)
        print("PÁGINA 6 - RESUMO DIÁRIO")
        print("="*100)

        # Extrair tabelas
        tabelas = page_resumo.extract_tables()

        print(f"\nTotal de tabelas na pagina: {len(tabelas)}\n")

        for t_idx, tabela in enumerate(tabelas):
            print(f"\n{'-'*100}")
            print(f"TABELA {t_idx + 1}: {len(tabela)} linhas x {len(tabela[0]) if tabela else 0} colunas")
            print(f"{'-'*100}")

            if not tabela:
                continue

            # Mostrar cabeçalho
            print(f"\nCabecalho:")
            for i, col in enumerate(tabela[0]):
                print(f"  [{i}]: {col}")

            # Buscar linhas com WIN
            linhas_win = []
            for linha in tabela:
                linha_str = ' '.join([str(c) if c else '' for c in linha])
                if 'WIN' in linha_str.upper() and 'IBOVESPA' in linha_str.upper():
                    linhas_win.append(linha)

            if linhas_win:
                print(f"\nEncontradas {len(linhas_win)} linhas com WIN nesta tabela:")
                for i, linha in enumerate(linhas_win, 1):
                    print(f"\n  Linha {i}:")
                    for j, valor in enumerate(linha):
                        print(f"    [{j}]: {valor}")

        # Tentar extrair dados específicos do WIN
        texto_completo = page_resumo.extract_text()
        linhas_texto = texto_completo.split('\n')

        print(f"\n{'='*100}")
        print("DADOS DO WIN NO TEXTO")
        print(f"{'='*100}\n")

        for i, linha in enumerate(linhas_texto):
            if 'WIN' in linha.upper() and 'IBOVESPA' in linha.upper():
                print(f"Linha {i}:")
                print(f"  {linha}")
                print(f"  Campos (split por espaço): {linha.split()}")

                # Tentar parsear os números
                numeros = re.findall(r'[\d,.]+', linha)
                if numeros:
                    print(f"  Números encontrados: {numeros}")
                print()


if __name__ == "__main__":
    pasta_raw = Path(__file__).parent / "data" / "boletins_b3" / "raw"
    pdfs = list(pasta_raw.rglob("*.pdf"))

    if pdfs:
        extrair_dados_win(pdfs[0])
    else:
        print("❌ Nenhum PDF encontrado")
