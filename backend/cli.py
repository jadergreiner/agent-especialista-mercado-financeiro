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
    import json

    linhas = []
    linhas.append("\n" + "=" * 70)
    linhas.append(f"📊 ANÁLISE: {resultado.get('ativo', resultado.get('par', 'N/A'))}")
    linhas.append("=" * 70)

    # Identificar tipo de análise
    tipo = resultado.get('tipo_analise', resultado.get('tipo', 'N/A'))
    mercado = resultado.get('mercado', 'N/A')

    linhas.append(f"Mercado: {mercado.upper()}")
    linhas.append(f"Tipo: {tipo.upper()}")

    # Timestamp
    timestamp = resultado.get('timestamp_analise', resultado.get('timestamp', 'N/A'))
    linhas.append(f"Timestamp: {timestamp}")
    linhas.append(f"Status: {resultado.get('status', 'N/A').upper()}")

    # Preço/Cotação atual
    preco = resultado.get('preco_atual', resultado.get('cotacao_atual', resultado.get('preco_spot', None)))
    if preco is not None:
        linhas.append("\n" + "-" * 70)
        linhas.append("� COTAÇÃO:")
        linhas.append(f"  Atual: {preco}")

        # Variações
        var_dia = resultado.get('variacao_dia', resultado.get('variacao_24h', None))
        if var_dia:
            linhas.append(f"  Variação 24h: {var_dia}")

    # Análise Técnica
    if 'analise_tecnica' in resultado:
        at = resultado['analise_tecnica']
        linhas.append("\n" + "-" * 70)
        linhas.append("📈 ANÁLISE TÉCNICA:")

        if 'tendencia' in at:
            linhas.append(f"  Tendência: {at['tendencia'].upper()}")
        if 'forca' in at:
            linhas.append(f"  Força: {at['forca']}/10")
        if 'rsi' in at:
            linhas.append(f"  RSI: {at['rsi']}")
        if 'suporte_resistencia' in at:
            sr = at['suporte_resistencia']
            linhas.append(f"  Suporte: {sr.get('suporte', 'N/A')}")
            linhas.append(f"  Resistência: {sr.get('resistencia', 'N/A')}")

    # Recomendação
    recomendacao = resultado.get('recomendacao', resultado.get('recomendacao_trading', None))
    if recomendacao:
        linhas.append("\n" + "-" * 70)
        linhas.append("💡 RECOMENDAÇÃO:")

        if isinstance(recomendacao, dict):
            acao = recomendacao.get('acao', recomendacao.get('direcao', 'N/A'))
            linhas.append(f"  Ação: {acao.upper()}")

            confianca = recomendacao.get('confianca', recomendacao.get('confianca_sinal', 0))
            if isinstance(confianca, (int, float)):
                linhas.append(f"  Confiança: {confianca * 100:.1f}%")

            if 'entrada_sugerida' in recomendacao:
                linhas.append(f"  Entrada: {recomendacao['entrada_sugerida']}")
            if 'stop_loss' in recomendacao:
                linhas.append(f"  Stop Loss: {recomendacao['stop_loss']}")
            if 'take_profit' in recomendacao:
                linhas.append(f"  Take Profit: {recomendacao['take_profit']}")

            if 'justificativa' in recomendacao:
                linhas.append("\n  Justificativa:")
                for just in recomendacao['justificativa']:
                    linhas.append(f"    • {just}")
        else:
            linhas.append(f"  {recomendacao.upper()}")

    # Observações/Riscos
    observacoes = resultado.get('observacoes', resultado.get('riscos', None))
    if observacoes:
        linhas.append("\n" + "-" * 70)
        linhas.append("📝 OBSERVAÇÕES:")
        for obs in observacoes:
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
