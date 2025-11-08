#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI INTERATIVO - GESTOR DO FUNDO COMPLETO

Interface de linha de comando para o sistema completo de gestão de portfólio.
Permite entrada interativa de operações com validações em tempo real.

Uso:
    python cli_gestor_fundo_completo.py
"""

import sys
import os
from pathlib import Path

# Adicionar diretório backend ao path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from gestor_fundo_completo import GestorFundoCompleto, DadosOperacao


class CLIGestorFundoCompleto:
    """Interface CLI para o Gestor do Fundo Completo"""

    def __init__(self):
        self.gestor = GestorFundoCompleto()
        print("✅ Gestor do Fundo Completo inicializado")

    def solicitar_input(self, prompt: str, tipo=str, obrigatorio: bool = True, padrao=None):
        """Solicitar input do usuário com validação"""
        while True:
            try:
                valor_str = input(f"{prompt}: ").strip()

                # Se não é obrigatório e está vazio, retornar padrão
                if not obrigatorio and valor_str == "":
                    return padrao

                # Se é obrigatório e está vazio, pedir novamente
                if obrigatorio and valor_str == "":
                    print("❌ Este campo é obrigatório. Tente novamente.")
                    continue

                # Converter para o tipo desejado
                if tipo == float:
                    valor = float(valor_str)
                    if valor <= 0:
                        print("❌ Valor deve ser maior que zero. Tente novamente.")
                        continue
                    return valor
                elif tipo == int:
                    return int(valor_str)
                else:
                    return valor_str

            except ValueError:
                print(f"❌ Valor inválido. Esperado: {tipo.__name__}. Tente novamente.")
            except KeyboardInterrupt:
                print("\n\n❌ Operação cancelada pelo usuário")
                sys.exit(0)

    def coletar_dados_operacao(self) -> DadosOperacao:
        """Coletar dados da operação do usuário"""
        print("\n" + "=" * 80)
        print("📝 CADASTRO DE NOVA OPERAÇÃO")
        print("=" * 80)
        print("Por favor, forneça os dados da operação:\n")

        # Dados obrigatórios
        ticket = self.solicitar_input("🎫 Ticket (obrigatório)", obrigatorio=True)
        currency_pair = self.solicitar_input("💱 Par de Moedas (ex: EUR/USD, GBP/JPY)", obrigatorio=True)

        # Direção
        while True:
            direction = self.solicitar_input("📊 Direção (LONG/SHORT ou BUY/SELL)", obrigatorio=True).upper()
            if direction in ['LONG', 'SHORT', 'BUY', 'SELL']:
                break
            print("❌ Direção inválida. Use: LONG, SHORT, BUY ou SELL")

        entry_price = self.solicitar_input("💰 Preço de Entrada", tipo=float, obrigatorio=True)
        lots = self.solicitar_input("📦 Volume (lotes)", tipo=float, obrigatorio=True)

        # Dados opcionais
        print("\n--- Dados Opcionais (pressione Enter para pular) ---")
        stop_loss = self.solicitar_input("🛡️  Stop Loss", tipo=float, obrigatorio=False, padrao=None)
        take_profit = self.solicitar_input("🎯 Take Profit", tipo=float, obrigatorio=False, padrao=None)
        strategy = self.solicitar_input("📋 Estratégia", obrigatorio=False, padrao=None)
        notes = self.solicitar_input("📝 Notas/Observações", obrigatorio=False, padrao=None)

        # Criar objeto DadosOperacao
        dados = DadosOperacao(
            ticket=ticket,
            currency_pair=currency_pair,
            direction=direction,
            entry_price=entry_price,
            lots=lots,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=strategy,
            notes=notes
        )

        return dados

    def confirmar_operacao(self, dados: DadosOperacao) -> bool:
        """Solicitar confirmação do usuário"""
        print("\n" + "=" * 80)
        print("🔍 CONFIRMAÇÃO DA OPERAÇÃO")
        print("=" * 80)
        print(f"🎫 Ticket: {dados.ticket}")
        print(f"💱 Par: {dados.currency_pair}")
        print(f"📊 Direção: {dados.direction}")
        print(f"💰 Preço: ${dados.entry_price:.5f}")
        print(f"📦 Volume: {dados.lots} lotes")

        if dados.stop_loss:
            print(f"🛡️  Stop Loss: ${dados.stop_loss:.5f}")
        if dados.take_profit:
            print(f"🎯 Take Profit: ${dados.take_profit:.5f}")
        if dados.strategy:
            print(f"📋 Estratégia: {dados.strategy}")
        if dados.notes:
            print(f"📝 Notas: {dados.notes}")

        print("=" * 80)

        while True:
            confirmacao = input("\n✅ Confirma esta operação? (S/N): ").strip().upper()
            if confirmacao in ['S', 'SIM', 'Y', 'YES']:
                return True
            elif confirmacao in ['N', 'NAO', 'NÃO', 'NO']:
                return False
            print("❌ Resposta inválida. Digite S para Sim ou N para Não.")

    def executar(self):
        """Executar CLI interativo"""
        try:
            print("\n" + "=" * 80)
            print("💼 GESTOR DO FUNDO - SISTEMA COMPLETO")
            print("🎯 Atualização de Portfólio com Análise Integrada")
            print("=" * 80)

            # Coletar dados
            dados = self.coletar_dados_operacao()

            # Confirmar operação
            if not self.confirmar_operacao(dados):
                print("\n❌ Operação cancelada pelo usuário")
                return

            # Processar operação completa
            print("\n🚀 Processando operação...")
            relatorio = self.gestor.processar_operacao_completa(dados)

            # Exibir relatório
            print("\n" + relatorio)

            # Salvar relatório em arquivo
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_relatorio = f"reports/relatorio_fundo_{timestamp}.txt"

            os.makedirs("reports", exist_ok=True)
            with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
                f.write(relatorio)

            print(f"\n💾 Relatório salvo em: {arquivo_relatorio}")

            # Perguntar se deseja ver recomendações detalhadas
            print("\n" + "-" * 80)
            ver_detalhes = input("📊 Deseja ver recomendações detalhadas? (S/N): ").strip().upper()

            if ver_detalhes in ['S', 'SIM', 'Y', 'YES']:
                print("\n🔄 Gerando recomendações detalhadas...")
                if self.gestor.recomendador:
                    recomendacoes = self.gestor.recomendador.gerar_recomendacoes_completas(self.gestor.portfolio)
                    relatorio_recs = self.gestor.recomendador.gerar_relatorio_recomendacoes(recomendacoes)
                    print("\n" + relatorio_recs)

                    # Salvar recomendações
                    arquivo_recs = f"reports/recomendacoes_{timestamp}.md"
                    with open(arquivo_recs, 'w', encoding='utf-8') as f:
                        f.write(relatorio_recs)
                    print(f"\n💾 Recomendações salvas em: {arquivo_recs}")
                else:
                    print("⚠️ Módulo de recomendações não disponível")

            print("\n✅ Operação concluída com sucesso!")

        except KeyboardInterrupt:
            print("\n\n❌ Operação cancelada pelo usuário")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Função principal"""
    cli = CLIGestorFundoCompleto()
    cli.executar()


if __name__ == "__main__":
    main()
