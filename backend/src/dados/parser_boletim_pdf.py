# -*- coding: utf-8 -*-
"""
Parser do PDF do Boletim Diário B3 - Versão Inicial.

Este parser extrai dados básicos do WIN do BDI em formato PDF.
VERSÃO ATUAL: Extrai volume e negócios (página 6).
TODO: Adicionar extração de preços OHLC e Open Interest (páginas 280+).
"""

import pdfplumber
from pathlib import Path
from datetime import date
from decimal import Decimal
import re
from typing import Optional

# Importar classe de dados do boletim
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.dados.boletim_b3 import DadosBoletimDiario, GerenciadorBoletimB3


class ParserBoletimPDF:
    """Parser para arquivos PDF do Boletim Diário B3."""

    def __init__(self):
        """Inicializa o parser."""
        self.gerenciador = GerenciadorBoletimB3()

    def extrair_data_do_nome_arquivo(self, caminho: Path) -> Optional[date]:
        """
        Extrai data do nome do arquivo BDI.

        Formato esperado: BDI_00_YYYYMMDD.pdf
        Exemplo: BDI_00_20251104.pdf -> 2025-11-04
        """
        match = re.search(r'(\d{8})', caminho.name)
        if match:
            data_str = match.group(1)
            return date(int(data_str[:4]), int(data_str[4:6]), int(data_str[6:8]))
        return None

    def extrair_dados_win_pagina6(self, pdf: pdfplumber.PDF) -> dict:
        """
        Extrai dados de volume e negócios do WIN da página 6.

        Formato da linha:
        MINI INDICES WIN: IBOVESPA MINI FUTURO 4.489.364 14.884.849 454.320.077.891 84.373.969.819

        Campos:
        [6]: Número de negócios
        [7]: Contratos negociados
        [8]: Volume total em R$
        [9]: Volume total em US$
        """
        try:
            page = pdf.pages[5]  # Página 6 (índice 5)
            texto = page.extract_text()

            if not texto:
                return None

            linhas = texto.split('\n')

            for linha in linhas:
                if 'WIN' in linha.upper() and 'IBOVESPA' in linha.upper():
                    # Extrair números (formato: 1.234.567)
                    numeros = re.findall(r'\d[\d.]*\d|\d+', linha)

                    if len(numeros) >= 4:
                        # Converter strings com pontos para números
                        def parse_numero(s):
                            return int(s.replace('.', ''))

                        return {
                            'numero_negocios': parse_numero(numeros[0]),
                            'contratos_negociados': parse_numero(numeros[1]),
                            'volume_reais': Decimal(str(parse_numero(numeros[2]))),
                            'volume_dolares': Decimal(str(parse_numero(numeros[3])))
                        }

        except Exception as e:
            print(f"Erro ao extrair dados da página 6: {e}")

        return None

    def importar_pdf(self, caminho_pdf: Path, vencimento: Optional[date] = None) -> bool:
        """
        Importa dados do PDF para o banco.

        Args:
            caminho_pdf: Caminho para o arquivo PDF
            vencimento: Data de vencimento do contrato (se None, usa estimativa)

        Returns:
            True se importou com sucesso
        """
        print(f"\n{'='*80}")
        print(f"IMPORTANDO: {caminho_pdf.name}")
        print(f"{'='*80}\n")

        # Extrair data do pregão
        data_pregao = self.extrair_data_do_nome_arquivo(caminho_pdf)
        if not data_pregao:
            print(f"❌ Não foi possível extrair data do arquivo: {caminho_pdf.name}")
            return False

        print(f"Data do pregao: {data_pregao.strftime('%d/%m/%Y')}")

        # Estimar vencimento se não fornecido (último dia útil do mês seguinte + 2 meses)
        if not vencimento:
            # Simplificação: próxima última quarta-feira do mês +2
            mes_venc = data_pregao.month + 2
            ano_venc = data_pregao.year
            if mes_venc > 12:
                mes_venc -= 12
                ano_venc += 1

            # Última quarta-feira aproximada (dia 27)
            vencimento = date(ano_venc, mes_venc, 27)
            print(f"Vencimento estimado: {vencimento.strftime('%d/%m/%Y')}")

        # Abrir PDF
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                # Extrair dados de volume
                dados_volume = self.extrair_dados_win_pagina6(pdf)

                if not dados_volume:
                    print("❌ Não foi possível extrair dados de volume do WIN")
                    return False

                print(f"\n✅ Dados de volume extraídos:")
                print(f"   Numero de negocios: {dados_volume['numero_negocios']:,}")
                print(f"   Contratos negociados: {dados_volume['contratos_negociados']:,}")
                print(f"   Volume R$: {dados_volume['volume_reais']:,.2f}")
                print(f"   Volume US$: {dados_volume['volume_dolares']:,.2f}")

                # TODO: Extrair preços OHLC e Open Interest (páginas 280+)
                # Por enquanto, usar valores placeholder
                print(f"\n⚠️  AVISO: Precos OHLC e Open Interest nao extraidos ainda (TODO)")
                print(f"   Usando valores placeholder para teste")

                # Criar estrutura de dados
                dados_boletim = DadosBoletimDiario(
                    data_pregao=data_pregao,
                    simbolo="WIN",
                    vencimento=vencimento,

                    # TODO: Extrair valores reais
                    abertura=Decimal("128500"),  # Placeholder
                    maxima=Decimal("129200"),
                    minima=Decimal("128100"),
                    fechamento=Decimal("128950"),
                    ajuste_diario=Decimal("128950"),
                    variacao_pontos=Decimal("450"),
                    variacao_percentual=Decimal("0.35"),

                    # Valores reais extraídos
                    volume_contratos=dados_volume['contratos_negociados'],
                    volume_financeiro=dados_volume['volume_reais'],
                    numero_negocios=dados_volume['numero_negocios'],

                    # TODO: Extrair valor real
                    contratos_abertos=520000  # Placeholder
                )

                # Salvar no banco
                sucesso = self.gerenciador.salvar_boletim(
                    dados_boletim,
                    arquivo_origem=caminho_pdf.name
                )

                if sucesso:
                    print(f"\n✅ Dados salvos no banco com sucesso!")
                else:
                    print(f"\nℹ️  Dados ja existiam no banco (nao sobrescrito)")

                return True

        except Exception as e:
            print(f"❌ Erro ao processar PDF: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Função principal para teste."""
    parser = ParserBoletimPDF()

    # Procurar PDFs na pasta raw
    pasta_raw = Path(__file__).parent.parent.parent / "data" / "boletins_b3" / "raw"
    pdfs = list(pasta_raw.rglob("*.pdf"))

    if not pdfs:
        print("❌ Nenhum PDF encontrado em data/boletins_b3/raw/")
        return

    print(f"✅ Encontrados {len(pdfs)} arquivo(s) PDF:")
    for pdf in pdfs:
        print(f"   - {pdf.relative_to(pasta_raw.parent)}")

    # Importar cada PDF
    for pdf in pdfs:
        parser.importar_pdf(pdf)
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
