# -*- coding: utf-8 -*-
"""
Script para buscar dados específicos do WIN no PDF do Boletim B3.
"""

import pdfplumber
from pathlib import Path
import re


def buscar_win_no_pdf(caminho_pdf: Path):
    """Busca e extrai dados do WIN no PDF."""

    print(f"\n{'='*80}")
    print(f"BUSCANDO DADOS DO WIN EM: {caminho_pdf.name}")
    print(f"{'='*80}\n")

    dados_win = []

    with pdfplumber.open(caminho_pdf) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            texto = page.extract_text()

            if not texto:
                continue

            linhas = texto.split('\n')

            # Buscar linhas com WIN
            for j, linha in enumerate(linhas):
                if 'WIN' in linha.upper():
                    # Capturar contexto (linha anterior e próximas 2)
                    contexto_antes = linhas[j-1] if j > 0 else ""
                    contexto_depois1 = linhas[j+1] if j+1 < len(linhas) else ""
                    contexto_depois2 = linhas[j+2] if j+2 < len(linhas) else ""

                    dados_win.append({
                        'pagina': i,
                        'linha_numero': j,
                        'linha': linha,
                        'contexto_antes': contexto_antes,
                        'contexto_depois1': contexto_depois1,
                        'contexto_depois2': contexto_depois2
                    })

            # Também buscar em tabelas
            tabelas = page.extract_tables()
            if tabelas:
                for t_idx, tabela in enumerate(tabelas):
                    for r_idx, linha in enumerate(tabela):
                        linha_str = ' '.join([str(c) if c else '' for c in linha])
                        if 'WIN' in linha_str.upper():
                            dados_win.append({
                                'pagina': i,
                                'tabela': t_idx,
                                'linha_tabela': r_idx,
                                'conteudo': linha
                            })

    # Exibir resultados
    print(f"✅ Encontradas {len(dados_win)} ocorrências de WIN\n")

    # Agrupar por página
    por_pagina = {}
    for item in dados_win:
        pag = item['pagina']
        if pag not in por_pagina:
            por_pagina[pag] = []
        por_pagina[pag].append(item)

    print(f"📄 Distribuição por página:")
    for pag in sorted(por_pagina.keys())[:10]:  # Primeiras 10 páginas
        print(f"   Página {pag}: {len(por_pagina[pag])} ocorrências")

    if len(por_pagina) > 10:
        print(f"   ... (total de {len(por_pagina)} páginas com WIN)")

    # Mostrar exemplos detalhados das primeiras ocorrências
    print(f"\n{'─'*80}")
    print("EXEMPLOS DETALHADOS (primeiras 5 ocorrências):")
    print(f"{'─'*80}\n")

    for idx, item in enumerate(dados_win[:5], 1):
        print(f"\n🔍 Ocorrência #{idx} (Página {item['pagina']}):")

        if 'linha' in item:
            # Ocorrência em texto
            if item['contexto_antes']:
                print(f"   [-1]: {item['contexto_antes'][:100]}")
            print(f"   [ 0]: {item['linha'][:100]} ⬅️")
            if item['contexto_depois1']:
                print(f"   [+1]: {item['contexto_depois1'][:100]}")
            if item['contexto_depois2']:
                print(f"   [+2]: {item['contexto_depois2'][:100]}")

        elif 'conteudo' in item:
            # Ocorrência em tabela
            print(f"   Tabela #{item['tabela']}, Linha #{item['linha_tabela']}")
            print(f"   Conteúdo: {item['conteudo'][:5]}")  # Primeiras 5 colunas

    # Buscar página com resumo de derivativos
    print(f"\n{'─'*80}")
    print("BUSCANDO SEÇÃO 'DERIVATIVOS - RESUMO':")
    print(f"{'─'*80}\n")

    with pdfplumber.open(caminho_pdf) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            texto = page.extract_text()
            if texto and ('DERIVATIVOS' in texto.upper() and 'RESUMO' in texto.upper()):
                linhas = texto.split('\n')
                print(f"\n📊 Página {i} - Primeiras 40 linhas:")
                for j, linha in enumerate(linhas[:40], 1):
                    print(f"  {j:2d}: {linha[:120]}")

                # Extrair tabelas desta página
                tabelas = page.extract_tables()
                if tabelas:
                    print(f"\n📋 Tabelas na página {i}:")
                    for t_idx, tabela in enumerate(tabelas[:2]):  # Primeiras 2 tabelas
                        print(f"\n  Tabela {t_idx + 1}: {len(tabela)} linhas")
                        for r_idx, linha in enumerate(tabela[:10]):  # Primeiras 10 linhas
                            print(f"    {r_idx}: {linha}")

                break  # Parar após primeira página com resumo

    return dados_win


if __name__ == "__main__":
    pasta_raw = Path(__file__).parent / "data" / "boletins_b3" / "raw"
    pdfs = list(pasta_raw.rglob("*.pdf"))

    if pdfs:
        buscar_win_no_pdf(pdfs[0])
    else:
        print("❌ Nenhum PDF encontrado")
