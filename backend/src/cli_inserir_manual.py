"""
CLI para inserção manual de recomendações e resultados.
Útil para popular banco com dados históricos ou testar sem API.
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.persistencia.recomendacoes import (
    inicializar_banco,
    salvar_recomendacao,
    registrar_resultado,
    listar_pendentes,
)


def input_float(prompt: str, default: Optional[float] = None) -> float:
    """Helper para input de float com valor padrão"""
    while True:
        valor = input(prompt)
        if not valor and default is not None:
            return default
        try:
            return float(valor)
        except ValueError:
            print("❌ Valor inválido. Digite um número decimal.")


def input_int(prompt: str, default: Optional[int] = None) -> int:
    """Helper para input de int com valor padrão"""
    while True:
        valor = input(prompt)
        if not valor and default is not None:
            return default
        try:
            return int(valor)
        except ValueError:
            print("❌ Valor inválido. Digite um número inteiro.")


def input_choice(prompt: str, opcoes: list, default: Optional[str] = None) -> str:
    """Helper para input com escolha múltipla"""
    opcoes_str = "/".join(opcoes)
    while True:
        valor = input(f"{prompt} ({opcoes_str}): ").upper()
        if not valor and default is not None:
            return default.upper()
        if valor in [o.upper() for o in opcoes]:
            return valor
        print(f"❌ Opção inválida. Escolha entre: {opcoes_str}")


def cmd_nova_recomendacao(args: argparse.Namespace) -> None:
    """Wizard interativo para criar nova recomendação"""
    print("\n" + "="*70)
    print("📝 NOVA RECOMENDAÇÃO MANUAL")
    print("="*70)

    # Data/hora
    print("\n🕐 Data e Hora")
    usar_agora = input("Usar data/hora atual? (S/n): ").strip().lower()
    if usar_agora in ['', 's', 'sim']:
        timestamp = datetime.utcnow().isoformat()
        print(f"   ✓ Usando: {timestamp}")
    else:
        data = input("Data (AAAA-MM-DD): ").strip()
        hora = input("Hora (HH:MM): ").strip()
        timestamp = f"{data}T{hora}:00.000000"

    # Direção
    print("\n📊 Direção do Trade")
    direcao = input_choice("Direção", ["COMPRA", "VENDA", "AGUARDAR"])

    if direcao == "AGUARDAR":
        print("\n⚠️  Recomendação AGUARDAR - pulando preços de entrada/saída")
        preco_entrada = 0.0
        contratos = 0
        stop_loss = 0.0
        tp1 = tp2 = tp3 = 0.0
    else:
        # Preços
        print("\n💰 Preços")
        preco_entrada = input_float("Preço de entrada: ")
        contratos = input_int("Quantidade de contratos: ", default=1)
        stop_loss = input_float("Stop Loss: ")

        print("\n🎯 Take Profits")
        tp1 = input_float("TP1: ")
        tem_tp2 = input("Tem TP2? (s/N): ").strip().lower()
        tp2 = input_float("TP2: ") if tem_tp2 in ['s', 'sim'] else 0.0
        tem_tp3 = input("Tem TP3? (s/N): ").strip().lower() if tp2 > 0 else 'n'
        tp3 = input_float("TP3: ") if tem_tp3 in ['s', 'sim'] else 0.0

    # Contexto de mercado
    print("\n🌍 Contexto de Mercado")
    tendencia = input_choice("Tendência", ["ALTA", "BAIXA", "LATERAL"])
    melhor_spread = input_choice("Melhor Spread", ["COMPRA", "VENDA"])

    print("\n📈 Saldo Macro")
    print("   -3 = Fortemente Desfavorável")
    print("    0 = Neutro")
    print("   +3 = Favorável")
    print("   +6 = Fortemente Favorável")
    saldo_macro = input_int("Saldo Macro (-6 a +6): ")

    # Volatilidade
    print("\n📊 Volatilidade (ATR)")
    atr_valor = input_float("ATR em pontos: ", default=1000.0)

    # Confiança
    print("\n✨ Confiança")
    confianca = input_int("Confiança (0-10): ", default=5)

    # Validade
    print("\n⏰ Validade")
    valido_ate = input("Válido até (HH:MM ou deixe vazio): ").strip()

    # Variação do dia
    print("\n📉 Variação do Dia")
    variacao_dia = input("Variação % (ex: +1.5% ou -0.8%): ").strip()

    # Montar dados no formato esperado
    dados = {
        'timestamp': timestamp,
        'relatorio_executivo': {
            'variacao_dia': variacao_dia,
            'sintese': {
                'tendencia': tendencia,
                'melhor_spread': melhor_spread,
                'saldo_macro': f"{saldo_macro:+d} - {'FAVORÁVEL' if saldo_macro > 0 else 'DESFAVORÁVEL' if saldo_macro < 0 else 'NEUTRO'}",
            }
        },
        'plano_trading': {
            'direcao': direcao,
            'entrada_inicial': {
                'preco': preco_entrada,
                'contratos': contratos
            },
            'gestao_saida': {
                'stop_loss': {'preco': stop_loss},
                'take_profit': [
                    {'preco': tp1, 'contratos': contratos},
                    {'preco': tp2, 'contratos': contratos} if tp2 > 0 else {},
                    {'preco': tp3, 'contratos': contratos} if tp3 > 0 else {},
                ]
            },
            'reforcos': [],
            'confianca': confianca,
            'valido_ate': valido_ate,
        },
        'analise_tecnica': {
            'indicadores': {
                'atr': {
                    'valor': atr_valor,
                    'classificacao': 'média'
                }
            }
        }
    }

    # Confirmar antes de salvar
    print("\n" + "="*70)
    print("📋 RESUMO")
    print("="*70)
    print(f"Direção: {direcao}")
    if direcao != "AGUARDAR":
        print(f"Entrada: {preco_entrada:,.2f} ({contratos} contratos)")
        print(f"Stop: {stop_loss:,.2f}")
        print(f"TPs: {tp1:,.2f}" + (f" / {tp2:,.2f}" if tp2 > 0 else "") + (f" / {tp3:,.2f}" if tp3 > 0 else ""))
    print(f"Tendência: {tendencia} | Spread: {melhor_spread}")
    print(f"Saldo Macro: {saldo_macro:+d} | ATR: {atr_valor:.2f}")
    print(f"Confiança: {confianca}/10")
    print("="*70)

    confirma = input("\n💾 Salvar recomendação? (S/n): ").strip().lower()
    if confirma not in ['', 's', 'sim']:
        print("❌ Cancelado.")
        return

    # Salvar
    inicializar_banco()
    id_rec = salvar_recomendacao(dados)
    print(f"\n✅ Recomendação salva com sucesso! ID: {id_rec}")


def cmd_registrar_resultado(args: argparse.Namespace) -> None:
    """Wizard interativo para registrar resultado de recomendação existente"""
    print("\n" + "="*70)
    print("📊 REGISTRAR RESULTADO")
    print("="*70)

    # Listar pendentes
    inicializar_banco()
    pendentes = listar_pendentes()

    if not pendentes:
        print("\n⚠️  Não há recomendações pendentes.")
        return

    print("\n📋 Recomendações Pendentes:")
    for rec in pendentes[:10]:  # Mostrar apenas 10
        print(f"   ID {rec.id}: {rec.direcao} | Entrada: {rec.preco_entrada:,.2f} | {rec.timestamp}")

    # Escolher ID
    id_rec = input_int("\n🔢 ID da recomendação: ")

    # Status
    print("\n📊 Status da Execução")
    status = input_choice("Status", ["executada", "cancelada", "expirada"])

    if status != "executada":
        # Apenas registrar sem resultado financeiro
        registrar_resultado(
            id_recomendacao=id_rec,
            status=status,
            acertou=None,
            preco_saida=None,
            pnl_pontos=None,
            pnl_reais=None,
            motivo_saida=status,
            observacoes=input("Observações (opcional): ").strip() or None
        )
        print(f"\n✅ Resultado registrado: {status.upper()}")
        return

    # Se foi executada, coletar detalhes
    print("\n💰 Resultado Financeiro")
    acertou_str = input_choice("Acertou?", ["sim", "não", "S", "N"])
    acertou = acertou_str.upper() in ['SIM', 'S']

    preco_saida = input_float("Preço de saída: ")
    pnl_pontos = input_float("PnL em pontos: ")
    pnl_reais = input_float("PnL em R$: ")

    print("\n🎯 Motivo da Saída")
    motivo = input_choice("Motivo", ["tp1", "tp2", "tp3", "stop", "tempo", "manual"])

    observacoes = input("Observações (opcional): ").strip() or None

    # Confirmar
    print("\n" + "="*70)
    print("📋 RESUMO DO RESULTADO")
    print("="*70)
    print(f"ID: {id_rec}")
    print(f"Status: EXECUTADA")
    print(f"Resultado: {'✅ ACERTO' if acertou else '❌ ERRO'}")
    print(f"Saída: {preco_saida:,.2f}")
    print(f"PnL: {pnl_pontos:+,.2f} pontos = R$ {pnl_reais:+,.2f}")
    print(f"Motivo: {motivo.upper()}")
    print("="*70)

    confirma = input("\n💾 Confirmar registro? (S/n): ").strip().lower()
    if confirma not in ['', 's', 'sim']:
        print("❌ Cancelado.")
        return

    registrar_resultado(
        id_recomendacao=id_rec,
        status='executada',
        acertou=acertou,
        preco_saida=preco_saida,
        pnl_pontos=pnl_pontos,
        pnl_reais=pnl_reais,
        motivo_saida=motivo,
        observacoes=observacoes
    )

    print(f"\n✅ Resultado registrado com sucesso!")


def build_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos"""
    parser = argparse.ArgumentParser(
        description='Inserção manual de recomendações e resultados',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comando a executar')

    # Comando: nova
    p_nova = subparsers.add_parser('nova', help='Criar nova recomendação')
    p_nova.set_defaults(func=cmd_nova_recomendacao)

    # Comando: resultado
    p_res = subparsers.add_parser('resultado', help='Registrar resultado de recomendação existente')
    p_res.set_defaults(func=cmd_registrar_resultado)

    return parser


def main(argv=None):
    """Ponto de entrada principal"""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        raise


if __name__ == '__main__':
    main()
