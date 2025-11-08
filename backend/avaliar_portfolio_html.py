"""
Script de Avaliação de Portfólio com Saída HTML
Gera relatório visual e interativo em HTML
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from gestor_fundo_completo import GestorFundoCompleto
from gerador_relatorio_html import GeradorRelatorioHTML
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    try:
        print("\n" + "="*80)
        print("💼 AVALIAÇÃO DE PORTFÓLIO - RELATÓRIO HTML")
        print("="*80 + "\n")

        # Inicializar gestor
        print("🔧 Inicializando Gestor de Fundo...")
        gestor = GestorFundoCompleto()

        # Carregar portfólio
        print("📂 Carregando portfólio...")
        gestor.carregar_portfolio()

        # Atualizar preços
        print("📊 Atualizando preços do mercado...")
        gestor.atualizar_precos_mercado()

        print("\n🔍 Gerando análises completas...\n")

        # Coletar dados
        resumo_portfolio = gestor.gerar_relatorio_portfolio()
        analise_risco = gestor.analisar_risco_completo()
        macro_coerencia = gestor.avaliar_coerencia_macro()
        correlacoes = gestor.analisar_correlacoes()
        recomendacoes = gestor.gerar_recomendacoes()

        # Preparar dados para HTML
        resumo_dict = {
            'capital_total': resumo_portfolio.get('capital_total', 0),
            'posicoes_ativas': len(gestor.portfolio.get('posicoes', [])),
            'pnl_total': resumo_portfolio.get('pnl_total', 0),
            'pnl_percent': (resumo_portfolio.get('pnl_total', 0) / resumo_portfolio.get('capital_total', 1)) * 100,
            'pnl_nao_realizado': resumo_portfolio.get('pnl_nao_realizado', 0),
            'exposicao_total': resumo_portfolio.get('exposicao_total', 0),
            'alavancagem': resumo_portfolio.get('alavancagem', 0),
            'exposicao_moedas': resumo_portfolio.get('exposicao_moedas', {})
        }

        macro_dict = {
            'vix': macro_coerencia.get('indicadores_macro', {}).get('vix', 0),
            'dxy': macro_coerencia.get('indicadores_macro', {}).get('dxy', 0),
            'cenario': macro_coerencia.get('cenario', 'DESCONHECIDO'),
            'alinhamento': macro_coerencia.get('alinhamento', 'DESCONHECIDO')
        }

        correlacoes_dict = {
            'exposicoes_redundantes': correlacoes.get('exposicoes_redundantes', []),
            'pares_unicos': correlacoes.get('pares_unicos', 0)
        }

        # Gerar HTML
        print("🎨 Gerando relatório HTML...")
        gerador = GeradorRelatorioHTML()

        filepath = gerador.gerar_html_completo(
            resumo_portfolio=resumo_dict,
            analise_risco=analise_risco,
            macro_coerencia=macro_dict,
            correlacoes=correlacoes_dict,
            recomendacoes=recomendacoes
        )

        print(f"\n✅ Relatório HTML gerado com sucesso!")
        print(f"📄 Arquivo: {filepath}")

        # Abrir no navegador
        print("\n🌐 Abrindo relatório no navegador...")
        gerador.abrir_no_navegador(filepath)

        print("\n" + "="*80)
        print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("="*80 + "\n")

        input("Pressione ENTER para sair...")

    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório HTML: {e}", exc_info=True)
        print(f"\n❌ ERRO: {e}")
        input("Pressione ENTER para sair...")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
