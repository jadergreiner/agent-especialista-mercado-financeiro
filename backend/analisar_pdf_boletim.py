# -*- coding: utf-8 -*-
"""
Script para analisar estrutura do PDF do Boletim Diário B3.
"""

import pdfplumber
from pathlib import Path


def analisar_pdf(caminho_pdf: Path):
    """Analisa estrutura do PDF e exibe informações."""

    print(f"\n{'='*80}")
    print(f"ANALISANDO: {caminho_pdf.name}")
    print(f"{'='*80}\n")

    with pdfplumber.open(caminho_pdf) as pdf:
        print(f"📄 Total de páginas: {len(pdf.pages)}\n")

        for i, page in enumerate(pdf.pages, 1):
            print(f"\n{'─'*80}")
            print(f"PÁGINA {i}")
            print(f"{'─'*80}")

            # Extrair texto
            texto = page.extract_text()
            if texto:
                linhas = texto.split('\n')
                print(f"\n📝 Primeiras 30 linhas de texto:")
                for j, linha in enumerate(linhas[:30], 1):
                    print(f"  {j:2d}: {linha[:100]}")

                if len(linhas) > 30:
                    print(f"\n  ... (total de {len(linhas)} linhas)")

            # Extrair tabelas
            tabelas = page.extract_tables()
            if tabelas:
                print(f"\n📊 Tabelas encontradas: {len(tabelas)}")
                for t_idx, tabela in enumerate(tabelas, 1):
                    print(f"\n  Tabela {t_idx}: {len(tabela)} linhas × {len(tabela[0]) if tabela else 0} colunas")
                    if tabela:
                        print(f"    Cabeçalho: {tabela[0][:5]}")  # Primeiras 5 colunas
                        if len(tabela) > 1:
                            print(f"    Linha 1: {tabela[1][:5]}")

            # Buscar padrões específicos
            if texto:
                # Procurar por WIN, WDO, etc.
                for contrato in ['WIN', 'WDO', 'DOL', 'IND']:
                    if contrato in texto:
                        print(f"\n🔍 Encontrado '{contrato}' na página {i}")
                        # Mostrar contexto
                        for linha in linhas:
                            if contrato in linha:
                                print(f"    {linha[:120]}")

            # Limitar análise às primeiras 3 páginas para não poluir
            if i >= 3:
                print(f"\n... (análise limitada às primeiras 3 páginas)")
                break


if __name__ == "__main__":
    # Procurar arquivos PDF na pasta
    pasta_raw = Path(__file__).parent / "data" / "boletins_b3" / "raw"

    pdfs = list(pasta_raw.rglob("*.pdf"))

    if not pdfs:
        print("❌ Nenhum arquivo PDF encontrado em data/boletins_b3/raw/")
        print(f"   Procurado em: {pasta_raw}")
    else:
        print(f"✅ Encontrados {len(pdfs)} arquivos PDF:")
        for pdf in pdfs:
            print(f"   - {pdf.relative_to(pasta_raw.parent)}")

        print("\n" + "="*80)
        # Analisar o primeiro (ou você pode escolher qual)
        analisar_pdf(pdfs[0])
