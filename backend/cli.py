"""
CLI - Interface de Linha de Comando para Análise de Mercado

Interface simples para interagir com o Agent Especialista de Mercado Financeiro.
Permite análises rápidas através de prompts simples.
"""

import sys
from typing import Optional
from src.agents.orquestrador_analise import OrquestradorAnalise, TipoAnalise


def exibir_banner():
    """Exibe banner de bienvenida"""
    print("=" * 70)
    print("🚀 AGENT ESPECIALISTA DE MERCADO FINANCEIRO")
    print("=" * 70)
    print("Versão: 0.1.0")
    print("Digite 'ajuda' para ver comandos disponíveis")
    print("Digite 'sair' para encerrar")
    print("=" * 70)
    print()


def exibir_ajuda():
    """Exibe comandos disponíveis"""
    print("\n📚 COMANDOS DISPONÍVEIS:")
    print("-" * 70)
    print("\nANÁLISE SIMPLES:")
    print("  <TICKER>                    - Análise completa (ex: BTCUSD, PETR4)")
    print("\nANÁLISE COM OPÇÕES:")
    print("  <TICKER> rapida             - Análise rápida")
    print("  <TICKER> tecnica            - Apenas análise técnica")
    print("  <TICKER> correlacao         - Apenas análise de correlações")
    print("  <TICKER> sentimento         - Apenas análise de sentimento")
    print("\nEXEMPLOS:")
    print("  BTCUSD                      - Análise completa de Bitcoin")
    print("  PETR4 rapida                - Análise rápida de Petrobras")
    print("  AAPL tecnica                - Análise técnica de Apple")
    print("\nOUTROS:")
    print("  ajuda                       - Exibe esta ajuda")
    print("  sair                        - Encerra o programa")
    print("-" * 70)


def formatar_analise(resultado: dict) -> str:
    """
    Formata resultado da análise para exibição

    Args:
        resultado: Dicionário com resultado da análise

    Returns:
        String formatada para exibição
    """
    linhas = []
    linhas.append("\n" + "=" * 70)
    linhas.append(f"📊 ANÁLISE: {resultado['ativo']}")
    linhas.append("=" * 70)
    linhas.append(f"Tipo: {resultado['tipo_analise'].upper()}")
    linhas.append(f"Período: {resultado['periodo_dias']} dias")
    linhas.append(f"Status: {resultado['status'].upper()}")
    linhas.append(f"Timestamp: {resultado['timestamp']}")

    # Se for análise rápida
    if 'recomendacao' in resultado:
        linhas.append("\n" + "-" * 70)
        linhas.append("📈 RESUMO RÁPIDO:")
        linhas.append(f"  Preço Atual: {resultado.get('preco_atual', 'N/A')}")
        linhas.append(f"  Variação (Dia): {resultado.get('variacao_dia', 'N/A')}")
        linhas.append(f"  Tendência: {resultado.get('tendencia', 'N/A').upper()}")
        linhas.append(f"  Recomendação: {resultado['recomendacao'].upper()}")
        linhas.append(f"  Confiança: {resultado.get('confianca', 0) * 100:.1f}%")

    # Se for análise completa
    if 'recomendacao_geral' in resultado:
        rec = resultado['recomendacao_geral']
        linhas.append("\n" + "-" * 70)
        linhas.append("💡 RECOMENDAÇÃO GERAL:")
        linhas.append(f"  Ação: {rec['acao'].upper()}")
        linhas.append(f"  Confiança: {rec['confianca'] * 100:.1f}%")
        linhas.append(f"  Timeframe: {rec['timeframe_sugerido'].replace('_', ' ').title()}")

        if rec.get('justificativa'):
            linhas.append("\n  Justificativa:")
            for just in rec['justificativa']:
                linhas.append(f"    • {just}")

        if rec.get('proximos_passos'):
            linhas.append("\n  Próximos Passos:")
            for passo in rec['proximos_passos']:
                linhas.append(f"    → {passo}")

    # Observações
    if 'observacoes' in resultado:
        linhas.append("\n" + "-" * 70)
        linhas.append("📝 OBSERVAÇÕES:")
        for obs in resultado['observacoes']:
            linhas.append(f"  • {obs}")

    # Se houver erro
    if resultado['status'] == 'erro':
        linhas.append("\n" + "-" * 70)
        linhas.append("❌ ERRO:")
        linhas.append(f"  {resultado.get('erro', 'Erro desconhecido')}")

    linhas.append("=" * 70 + "\n")

    return "\n".join(linhas)


def processar_comando(comando: str, orquestrador: OrquestradorAnalise) -> Optional[str]:
    """
    Processa comando do usuário

    Args:
        comando: Comando digitado pelo usuário
        orquestrador: Instância do orquestrador de análise

    Returns:
        Resposta formatada ou None se comando de controle
    """
    comando = comando.strip()

    if not comando:
        return None

    # Comandos de controle
    if comando.lower() in ['sair', 'exit', 'quit', 'q']:
        print("\n👋 Até logo!")
        sys.exit(0)

    if comando.lower() in ['ajuda', 'help', 'h', '?']:
        exibir_ajuda()
        return None

    # Processar análise
    partes = comando.split()
    ticker = partes[0].upper()

    # Determinar tipo de análise
    tipo_analise = TipoAnalise.COMPLETA
    if len(partes) > 1:
        tipo_str = partes[1].lower()
        if tipo_str in ['rapida', 'rápida', 'quick']:
            tipo_analise = TipoAnalise.RAPIDA
        elif tipo_str in ['tecnica', 'técnica', 'technical']:
            tipo_analise = TipoAnalise.TECNICA
        elif tipo_str in ['correlacao', 'correlação', 'correlation']:
            tipo_analise = TipoAnalise.CORRELACAO
        elif tipo_str in ['sentimento', 'sentiment']:
            tipo_analise = TipoAnalise.SENTIMENTO
        elif tipo_str in ['fundamental']:
            tipo_analise = TipoAnalise.FUNDAMENTAL

    # Executar análise
    print(f"\n⏳ Analisando {ticker}...")
    resultado = orquestrador.analisar(ticker, tipo_analise)

    return formatar_analise(resultado)


def modo_interativo():
    """Executa CLI em modo interativo"""
    exibir_banner()
    orquestrador = OrquestradorAnalise()

    while True:
        try:
            comando = input("\n💬 Digite o ativo para análise: ").strip()

            if not comando:
                continue

            resposta = processar_comando(comando, orquestrador)

            if resposta:
                print(resposta)

        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Erro ao processar comando: {e}")


def modo_comando_unico(ticker: str, tipo: Optional[str] = None):
    """
    Executa análise única e encerra

    Args:
        ticker: Ativo para análise
        tipo: Tipo de análise (opcional)
    """
    orquestrador = OrquestradorAnalise()

    comando = ticker
    if tipo:
        comando += f" {tipo}"

    print(f"🔍 Executando análise: {comando}\n")
    resposta = processar_comando(comando, orquestrador)

    if resposta:
        print(resposta)


def main():
    """Ponto de entrada principal"""
    if len(sys.argv) > 1:
        # Modo comando único
        ticker = sys.argv[1]
        tipo = sys.argv[2] if len(sys.argv) > 2 else None
        modo_comando_unico(ticker, tipo)
    else:
        # Modo interativo
        modo_interativo()


if __name__ == "__main__":
    main()
