#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTOR DO FUNDO - CLI INTERATIVO

Interface de linha de comando para o sistema completo de gestão de portfólio
do especialista de mercado financeiro.

Formato Estruturado:
[INICIO] Menu principal e seleção de operação
[DURANTE] Processamento da operação selecionada
[FIM] Relatório executivo e recomendações
"""

import sys
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from .gestor_fundo import GestorFundo
    from .analisador_risco_fundo import AnalisadorRiscoFundo
    from .recomendador_operacoes_fundo import RecomendadorOperacoesFundo
except ImportError:
    try:
        from gestor_fundo import GestorFundo
        from analisador_risco_fundo import AnalisadorRiscoFundo
        from recomendador_operacoes_fundo import RecomendadorOperacoesFundo
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("Certifique-se de que os arquivos estão no diretório correto.")
        sys.exit(1)

class CLIGestorFundo:
    """
    CLI Interativo para o Gestor do Fundo
    """

    def __init__(self):
        self.gestor = None
        self.analisador_risco = AnalisadorRiscoFundo()
        self.recomendador = RecomendadorOperacoesFundo()

    def executar(self):
        """Executa o CLI principal"""
        self._exibir_banner()

        try:
            # Inicializar gestor
            self._inicializar_gestor()

            # Loop principal do menu
            while True:
                opcao = self._exibir_menu_principal()

                if opcao == '1':
                    self._executar_gestao_completa()
                elif opcao == '2':
                    self._exibir_relatorio_portfolio()
                elif opcao == '3':
                    self._exibir_analise_risco()
                elif opcao == '4':
                    self._exibir_recomendacoes()
                elif opcao == '5':
                    self._executar_stress_test()
                elif opcao == '6':
                    self._exibir_historico_operacoes()
                elif opcao == '0':
                    self._sair()
                    break
                else:
                    print("❌ Opção inválida. Tente novamente.")

        except KeyboardInterrupt:
            print("\n⚠️ Operação interrompida pelo usuário.")
            self._sair()
        except Exception as e:
            print(f"❌ Erro crítico: {str(e)}")
            self._sair()

    def _exibir_banner(self):
        """Exibe banner do sistema"""
        print("\n" + "="*80)
        print("🏦 GESTOR DO FUNDO - ESPECIALISTA MERCADO FINANCEIRO")
        print("💼 Sistema Completo de Gestão de Portfólio Profissional")
        print("="*80)
        print("📊 Análise Técnica + Fundamental + Correlação Avançada")
        print("🛡️ Gestão de Risco com VaR + Stress Test + Diversificação")
        print("🎯 Recomendações Inteligentes + Timing Ótimo")
        print("="*80)

    def _inicializar_gestor(self):
        """Inicializa o gestor do fundo"""
        print("\n🔧 Inicializando sistema...")

        try:
            self.gestor = GestorFundo()
            print("✅ Sistema inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro na inicialização: {str(e)}")
            print("Verifique se os arquivos de configuração estão corretos.")
            sys.exit(1)

    def _exibir_menu_principal(self) -> str:
        """Exibe menu principal e retorna opção selecionada"""
        print("\n" + "-"*60)
        print("📋 MENU PRINCIPAL - GESTOR DO FUNDO")
        print("-"*60)
        print("1. 🎯 Gestão Completa do Fundo (INICIO→DURANTE→FIM)")
        print("2. 📊 Relatório do Portfólio Atual")
        print("3. 🛡️ Análise de Risco Detalhada")
        print("4. 💡 Recomendações de Operações")
        print("5. ⚡ Stress Test do Portfólio")
        print("6. 📈 Histórico de Operações")
        print("0. 🚪 Sair")
        print("-"*60)

        return input("Escolha uma opção: ").strip()

    def _executar_gestao_completa(self):
        """Executa gestão completa do fundo"""
        print("\n🎯 INICIANDO GESTÃO COMPLETA DO FUNDO")
        print("Processo: INICIO → DURANTE → FIM")
        print("-"*50)

        try:
            sucesso = self.gestor.executar_gestao_fundo()

            if sucesso:
                print("\n✅ Gestão completa executada com sucesso!")
                input("\nPressione ENTER para continuar...")
            else:
                print("\n❌ Gestão interrompida com erros.")
                input("\nPressione ENTER para continuar...")

        except Exception as e:
            print(f"\n❌ Erro na gestão completa: {str(e)}")
            input("\nPressione ENTER para continuar...")

    def _exibir_relatorio_portfolio(self):
        """Exibe relatório atual do portfólio"""
        print("\n📊 RELATÓRIO ATUAL DO PORTFÓLIO")
        print("-"*50)

        try:
            relatorio = self.gestor.gerar_relatorio_executivo()
            print(relatorio)

            # Opção de salvar relatório
            if self._confirmar_acao("Salvar relatório em arquivo?"):
                self._salvar_relatorio(relatorio, "relatorio_portfolio")

        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {str(e)}")

        input("\nPressione ENTER para continuar...")

    def _exibir_analise_risco(self):
        """Exibe análise de risco detalhada"""
        print("\n🛡️ ANÁLISE DE RISCO DETALHADA")
        print("-"*50)

        try:
            # Análise geral do portfólio
            analise_risco = self.analisador_risco.analisar_risco_portfolio(self.gestor.portfolio)

            print("### 📊 MÉTRICAS PRINCIPAIS DE RISCO")
            print(f"VaR 95%: ${analise_risco.var_95:,.0f}")
            print(f"VaR 99%: ${analise_risco.var_99:,.0f}")
            print(f"Volatilidade: {analise_risco.volatilidade_portfolio:.1%}")
            print(f"Correlação Máxima: {analise_risco.correlacao_maxima:.2f}")
            print(f"Exposição Concentrada: {analise_risco.exposicao_concentrada:.1%}")
            print(f"Risco Sistêmico: {analise_risco.risco_sistemico:.1%}")
            print(f"Nível de Alerta: {analise_risco.nivel_alerta}")
            print()
            print("### 💡 RECOMENDAÇÃO")
            print(analise_risco.recomendacao_risco)

            # Análise por posição
            analises_posicoes = self.analisador_risco.analisar_posicoes_risco(self.gestor.portfolio)

            if analises_posicoes:
                print("\n### 🎯 ANÁLISE POR POSIÇÃO")
                print("| Ativo | Exposição | Risco Individual | Correlação | Nível |")
                print("|-------|-----------|------------------|------------|--------|")

                for analise in analises_posicoes:
                    print(f"| {analise.ativo} | ${analise.exposicao:,.0f} | ${analise.risco_individual:,.0f} | {analise.correlacao_media:.2f} | {analise.nivel_risco} |")

        except Exception as e:
            print(f"❌ Erro na análise de risco: {str(e)}")

        input("\nPressione ENTER para continuar...")

    def _exibir_recomendacoes(self):
        """Exibe recomendações de operações"""
        print("\n💡 RECOMENDAÇÕES DE OPERAÇÕES")
        print("-"*50)

        try:
            recomendacoes = self.recomendador.gerar_recomendacoes_completas(self.gestor.portfolio)
            relatorio = self.recomendador.gerar_relatorio_recomendacoes(recomendacoes)

            print(relatorio)

            # Opção de salvar recomendações
            if self._confirmar_acao("Salvar recomendações em arquivo?"):
                self._salvar_relatorio(relatorio, "recomendacoes_operacoes")

        except Exception as e:
            print(f"❌ Erro ao gerar recomendações: {str(e)}")

        input("\nPressione ENTER para continuar...")

    def _executar_stress_test(self):
        """Executa stress test do portfólio"""
        print("\n⚡ STRESS TEST DO PORTFÓLIO")
        print("-"*50)

        try:
            cenarios = [
                "crash_2008",
                "flash_crash",
                "high_volatility",
                "currency_crisis",
                "interest_rate_hike"
            ]

            resultados = self.analisador_risco.calcular_stress_test(self.gestor.portfolio, cenarios)

            print("### 📊 RESULTADOS DO STRESS TEST")
            print("| Cenário | Perda Estimada | % do Capital |")
            print("|---------|----------------|--------------|")

            capital_base = 100000  # USD
            for cenario, perda in resultados.items():
                percentual = (perda / capital_base) * 100
                nome_cenario = cenario.replace('_', ' ').title()
                print(f"| {nome_cenario} | ${perda:,.0f} | {percentual:.1f}% |")

            # Análise dos resultados
            perda_maxima = max(resultados.values())
            percentual_max = (perda_maxima / capital_base) * 100

            print(f"\n### 🎯 ANÁLISE")
            if percentual_max > 20:
                print(f"🚨 PERDA CRÍTICA: Cenário mais severo resulta em {percentual_max:.1f}% de perda")
                print("Recomendação: Reduzir exposição e implementar proteções adicionais")
            elif percentual_max > 10:
                print(f"⚠️ PERDA MODERADA: Cenário mais severo resulta em {percentual_max:.1f}% de perda")
                print("Recomendação: Monitorar de perto e ajustar stops")
            else:
                print(f"✅ RESISTÊNCIA BOA: Máxima perda estimada de {percentual_max:.1f}%")
                print("Portfólio bem protegido contra cenários extremos")

        except Exception as e:
            print(f"❌ Erro no stress test: {str(e)}")

        input("\nPressione ENTER para continuar...")

    def _exibir_historico_operacoes(self):
        """Exibe histórico de operações"""
        print("\n📈 HISTÓRICO DE OPERAÇÕES")
        print("-"*50)

        try:
            historico = self.gestor.portfolio.get('historico_operacoes', [])

            if not historico:
                print("📝 Nenhuma operação registrada ainda.")
            else:
                print(f"Total de operações: {len(historico)}")
                print()

                # Últimas 10 operações
                operacoes_recentes = sorted(historico, key=lambda x: x['timestamp'], reverse=True)[:10]

                for op in operacoes_recentes:
                    timestamp = datetime.fromisoformat(op['timestamp']).strftime('%Y-%m-%d %H:%M')
                    print(f"📅 {timestamp} - {op['tipo']} - {op['ativo']}")
                    print(f"   Ticket: {op['ticket']}")
                    print()

        except Exception as e:
            print(f"❌ Erro ao exibir histórico: {str(e)}")

        input("\nPressione ENTER para continuar...")

    def _confirmar_acao(self, mensagem: str) -> bool:
        """Confirma uma ação com o usuário"""
        while True:
            resposta = input(f"{mensagem} (s/n): ").strip().lower()
            if resposta in ['s', 'sim', 'y', 'yes']:
                return True
            elif resposta in ['n', 'nao', 'no']:
                return False
            else:
                print("Responda 's' para sim ou 'n' para não.")

    def _salvar_relatorio(self, conteudo: str, nome_base: str):
        """Salva relatório em arquivo"""
        try:
            # Criar diretório reports se não existir
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)

            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"{nome_base}_{timestamp}.md"
            caminho_arquivo = reports_dir / nome_arquivo

            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)

            print(f"✅ Relatório salvo em: {caminho_arquivo}")

        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {str(e)}")

    def _sair(self):
        """Procedimento de saída"""
        print("\n" + "="*50)
        print("👋 Obrigado por usar o Gestor do Fundo!")
        print("💼 Sistema desenvolvido pelo Especialista de Mercado Financeiro")
        print("="*50)
        print("📊 Lembre-se: O sucesso no mercado vem da disciplina,")
        print("🛡️ gestão de risco adequada e análise consistente.")
        print("="*50)

def main():
    """Função principal"""
    cli = CLIGestorFundo()
    cli.executar()

if __name__ == "__main__":
    main()