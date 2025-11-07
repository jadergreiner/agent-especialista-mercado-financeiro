#!/usr/bin/env python3
"""
Relatório de Fechamento de Posições - Análise de Timing

Gera relatório detalhado dos fechamentos de posições conforme recomendações
da análise de timing baseada em eventos econômicos.
"""

import json
from datetime import datetime
from pathlib import Path

def gerar_relatorio_fechamento():
    """Gera relatório detalhado dos fechamentos de posições."""

    # Dados dos fechamentos conforme relatório do usuário
    fechamentos = [
        {
            "ticket": "5301566535",
            "par": "EUR/CHF",
            "direcao": "SHORT",
            "swap": 0.10,
            "profit": 1.49,
            "total_realizado": 1.59,
            "motivo": "Análise de timing - Risco crítico evento BCE",
            "data_fechamento": datetime.now().isoformat()
        },
        {
            "ticket": "5301566496",
            "par": "EUR/USD",
            "direcao": "LONG",
            "swap": 0.03,
            "profit": 0.20,
            "total_realizado": 0.23,
            "motivo": "Análise de timing - Risco crítico evento BCE",
            "data_fechamento": datetime.now().isoformat()
        }
    ]

    # Calcular métricas do fechamento
    total_profit = sum(f['profit'] for f in fechamentos)
    total_swap = sum(f['swap'] for f in fechamentos)
    total_realizado = sum(f['total_realizado'] for f in fechamentos)

    # Carregar análise de timing para contexto
    caminho_timing = Path("data/timing_eventos/analise_timing_20251107_002837.json")
    contexto_timing = {}

    if caminho_timing.exists():
        with open(caminho_timing, 'r', encoding='utf-8') as f:
            dados_timing = json.load(f)
            contexto_timing = {
                "total_riscos_criticos": dados_timing.get('resumo_analise', {}).get('total_riscos_criticos', 0),
                "total_riscos_elevados": dados_timing.get('resumo_analise', {}).get('total_riscos_elevados', 0),
                "eventos_analisados": len(dados_timing.get('eventos_economicos', []))
            }

    # Gerar relatório
    relatorio = {
        "titulo": "RELATÓRIO DE FECHAMENTO DE POSIÇÕES",
        "data_geracao": datetime.now().isoformat(),
        "periodo": "Análise de Timing - Eventos Econômicos",
        "contexto_timing": contexto_timing,
        "fechamentos": fechamentos,
        "metricas_fechamento": {
            "total_posicoes_fechadas": len(fechamentos),
            "total_profit": total_profit,
            "total_swap": total_swap,
            "total_realizado": total_realizado,
            "pares_afetados": list(set(f['par'] for f in fechamentos)),
            "direcoes_fechadas": list(set(f['direcao'] for f in fechamentos))
        },
        "analise_impacto": {
            "reducao_risco_euro": "Sim - Fechamento posições EUR/CHF SHORT e EUR/USD LONG conforme recomendação timing",
            "alinhamento_estrategia": "Sim - Seguindo recomendações análise de eventos econômicos",
            "preservacao_capital": "Sim - Realização de lucros em período de risco elevado",
            "otimizacao_timing": "Sim - Saída antes de eventos de alto impacto (BCE)"
        },
        "recomendacoes_seguintes": [
            "Monitorar impacto dos eventos econômicos no mercado",
            "Reavaliar exposição EUR após divulgação dos dados",
            "Considerar reentrada em posições EUR com timing otimizado",
            "Atualizar análise de correlação após eventos"
        ]
    }

    # Salvar relatório
    caminho_relatorio = Path("reports/relatorio_fechamento_posicoes.json")
    caminho_relatorio.parent.mkdir(exist_ok=True)

    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    # Imprimir relatório formatado
    print("📊 RELATÓRIO DE FECHAMENTO DE POSIÇÕES")
    print("=" * 50)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Período: Análise de Timing - Eventos Econômicos")
    print()

    print("🔄 POSIÇÕES FECHADAS:")
    for i, fechamento in enumerate(fechamentos, 1):
        print(f"{i}. {fechamento['par']} {fechamento['direcao']} (Ticket: {fechamento['ticket']})")
        print(".2f")
        print(f"   Motivo: {fechamento['motivo']}")
        print()

    print("📈 MÉTRICAS DO FECHAMENTO:")
    print(f"Total posições fechadas: {len(fechamentos)}")
    print(".2f")
    print(".2f")
    print(".2f")
    print(f"Pares afetados: {', '.join(set(f['par'] for f in fechamentos))}")
    print()

    print("🎯 ANÁLISE DE IMPACTO:")
    print("✅ Redução risco Euro: Sim - Fechamento posições EUR conforme recomendação")
    print("✅ Alinhamento estratégia: Sim - Seguindo análise de eventos econômicos")
    print("✅ Preservação capital: Sim - Realização lucros em período risco elevado")
    print("✅ Otimização timing: Sim - Saída antes eventos alto impacto (BCE)")
    print()

    print("📋 RECOMENDAÇÕES SEGUINTES:")
    for i, rec in enumerate(relatorio['recomendacoes_seguintes'], 1):
        print(f"{i}. {rec}")
    print()

    print("✅ Relatório salvo em: reports/relatorio_fechamento_posicoes.json")

    return relatorio

if __name__ == "__main__":
    gerar_relatorio_fechamento()