# Gerador de Playbook Quantitativo WIN
# Sistema de Análise Operacional Diária
# Framework: Detecção de Campo Neutro → Ressonância Inicial → Validação → Consolidação

"""
GERADOR DE PLAYBOOK QUÂNTICO - WIN

Este módulo implementa um sistema de geração automática de playbooks operacionais
para análise intraday do WIN (mini-índice futuro do Ibovespa).

Funcionalidades:
- Coleta automática de indicadores globais via Yahoo Finance
- Análise de campo neutro (pré-abertura)
- Detecção de ressonância inicial (primeira hora)
- Validação de direcional emergente (meio do dia)
- Consolidação de aprendizado (fechamento)

Integração com Framework Assimétrico:
- Complementa análise técnica com visão operacional
- Fornece contexto de mercado para detecção de setups
- Suporta tomada de decisão em tempo real
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Dict, Optional, Tuple
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeradorPlaybookWIN:
    """
    Gerador de playbook quantitativo para análise operacional do WIN.
    """

    def __init__(self, periodo_coleta: str = "5d"):
        """
        Inicializa o gerador de playbook.

        Args:
            periodo_coleta: Período para coleta histórica (padrão: 5d)
        """
        self.periodo_coleta = periodo_coleta
        self.tickers = self._configurar_tickers()
        logger.info("Gerador de Playbook WIN inicializado")

    def _configurar_tickers(self) -> Dict[str, str]:
        """Configura tickers dos indicadores globais"""
        return {
            "S&P500": "^GSPC",
            "NASDAQ": "^IXIC",
            "DXY": "DX-Y.NYB",
            "VIX": "^VIX",
            "Treasuries_10Y": "^TNX",
            "Brent": "BZ=F",
            "Iron_Ore": "TIOc1",
            "USD/BRL": "USDBRL=X"
        }

    def coletar_dados_mercado(self) -> Dict[str, str]:
        """
        Coleta dados de mercado dos indicadores globais.

        Returns:
            Dict com variações percentuais formatadas
        """
        logger.info("Iniciando coleta de dados de mercado")
        dados = {}

        for nome, ticker in self.tickers.items():
            try:
                logger.debug(f"Coletando dados para {nome} ({ticker})")
                info = yf.Ticker(ticker).history(period=self.periodo_coleta)

                if len(info) < 2:
                    dados[nome] = "N/D"
                    continue

                close_atual = info["Close"].iloc[-1]
                close_anterior = info["Close"].iloc[-2]

                if close_anterior != 0:
                    variacao_pct = ((close_atual - close_anterior) / close_anterior) * 100
                    dados[nome] = f"{variacao_pct:+.2f}%"
                else:
                    dados[nome] = "N/D"

            except Exception as e:
                logger.warning(f"Erro ao coletar {nome}: {e}")
                dados[nome] = "N/D"

        logger.info(f"Coleta concluída: {len(dados)} indicadores processados")
        return dados

    def _interpretar_campo_global(self, dados: Dict[str, str]) -> str:
        """Interpreta o campo global baseado nos indicadores"""
        try:
            # Contar sinais positivos/negativos
            positivos = 0
            negativos = 0

            indicadores_chave = ["S&P500", "NASDAQ", "DXY", "VIX", "Treasuries_10Y"]

            for indicador in indicadores_chave:
                if dados.get(indicador, "N/D") != "N/D":
                    valor_str = dados[indicador].rstrip('%')
                    try:
                        valor = float(valor_str)
                        if valor > 0.1:
                            positivos += 1
                        elif valor < -0.1:
                            negativos += 1
                    except ValueError:
                        continue

            if positivos > negativos + 1:
                return "Positivo"
            elif negativos > positivos + 1:
                return "Negativo"
            else:
                return "Neutro"

        except Exception as e:
            logger.error(f"Erro na interpretação do campo global: {e}")
            return "Neutro"

    def gerar_playbook(self,
                       dados_mercado: Optional[Dict[str, str]] = None,
                       salvar_arquivo: bool = True,
                       caminho_saida: Optional[str] = None) -> str:
        """
        Gera o playbook completo em formato Markdown.

        Args:
            dados_mercado: Dados de mercado (opcional, coletará se não fornecido)
            salvar_arquivo: Se deve salvar em arquivo
            caminho_saida: Caminho customizado para salvar

        Returns:
            String com conteúdo do playbook
        """
        # Coletar dados se não fornecidos
        if dados_mercado is None:
            dados_mercado = self.coletar_dados_mercado()

        # Timestamp de geração
        agora = datetime.now()
        data_hoje = agora.strftime("%Y-%m-%d")
        hora_geracao = agora.strftime("%H:%M")

        # Interpretar campo global
        campo_global = self._interpretar_campo_global(dados_mercado)

        # Gerar conteúdo Markdown
        playbook = f"""# 🧭 PLAYBOOK QUÂNTICO – DIA NEUTRO (WIN)

> **Gerado automaticamente em {data_hoje} às {hora_geracao}**
>
> **Objetivo:** detectar o nascimento do direcional em dias sem campo dominante.

---

## 🕕 1. PRÉ-ABERTURA (07h00–09h00)
**Missão:** avaliar se o campo está realmente neutro.

| Indicador | Variação | Interpretação |
|------------|-----------|----------------|
| S&P500 | {dados_mercado.get('S&P500', 'N/D')} | |
| NASDAQ | {dados_mercado.get('NASDAQ', 'N/D')} | |
| DXY | {dados_mercado.get('DXY', 'N/D')} | |
| VIX | {dados_mercado.get('VIX', 'N/D')} | |
| Treasuries (10y) | {dados_mercado.get('Treasuries_10Y', 'N/D')} | |
| Petróleo Brent | {dados_mercado.get('Brent', 'N/D')} | |
| Minério de Ferro | {dados_mercado.get('Iron_Ore', 'N/D')} | |
| USD/BRL | {dados_mercado.get('USD/BRL', 'N/D')} | |
| DI1F / Política Fiscal | | |
| Agenda Macro | | |

**Campo Global:** ☐ Neutro ☐ Positivo ☐ Negativo → **Interpretado: {campo_global}**
**Campo Local:** ☐ Neutro ☐ Positivo ☐ Negativo

**Comentário inicial:**

---

## 🕙 2. PRIMEIRA HORA (09h00–10h00)
**Missão:** capturar o ponto de ressonância inicial.

| Sinal | Observação | Interpretação |
|--------|-------------|---------------|
| Quem lidera: WIN ou Dólar? | | |
| EWZ (ADR Brasil) | | |
| Volume estrangeiro B3 | | |
| Spread WIN x Dólar | | |

**Bias inicial:** ☐ Alta ☐ Baixa ☐ Neutro
**Força percebida:** 🔵 fraca 🔷 média 🔶 forte

---

## ⏰ 3. MEIO DO DIA (11h30–14h00)
**Missão:** validar o direcional emergente.

| Indicador | Observação | Interpretação |
|------------|-------------|---------------|
| Abertura NY (S&P) | | |
| Correlação WIN x S&P | | |
| Divergência Global x Local | | |
| Variação de volume | | |

**Tendência:** ☐ Confirmada ☐ Falsa ☐ Indefinida
**Ação sugerida:** 🟢 seguir tendência / 🔴 operar fade / ⚪ aguardar

---

## 🌙 4. FECHAMENTO (16h00–17h00)
**Missão:** consolidar aprendizado do dia.

| Métrica | Observação |
|----------|-------------|
| Eixo dominante ao fim do dia | |
| Tempo até definição de campo | |
| Volatilidade média (pts) | |
| Correlação WIN–Dólar | |
| Correlação WIN–S&P | |

**Resumo do dia:**
- Direcional dominante:
- Melhor janela de operação:
- Erros de leitura:
- Ajustes para amanhã:

---

## 🔁 SÍNTESE DO CAMPO
> **Bias final:**
> 🟩 Bullish 🟥 Bearish ⬜ Neutro
> **Ressonância predominante:** 🌍 Global / 🇧🇷 Local / 💱 Câmbio / 🛢 Commodities

---

## 📓 NOTAS LIVRES
- Dados automáticos capturados via *Yahoo Finance (yfinance)*.
- Campo global interpretado automaticamente baseado em indicadores chave.
- Execute o script entre **08h45–08h55** para capturar o pré-mercado.
- Atualize manualmente os campos locais (DI1F, política fiscal, agenda macro).

---

**Framework de Detecção Assimétrica - Integração Operacional**
"""

        # Salvar arquivo se solicitado
        if salvar_arquivo:
            nome_arquivo = caminho_saida or f"playbook_WIN_{data_hoje}.md"
            try:
                with open(nome_arquivo, "w", encoding="utf-8") as f:
                    f.write(playbook)
                logger.info(f"Playbook salvo: {nome_arquivo}")
                print(f"✅ Playbook gerado com sucesso: {nome_arquivo}")
            except Exception as e:
                logger.error(f"Erro ao salvar playbook: {e}")

        return playbook

    def obter_metricas_coleta(self) -> Dict[str, any]:
        """
        Retorna métricas da última coleta de dados.

        Returns:
            Dict com métricas de coleta
        """
        return {
            'total_indicadores': len(self.tickers),
            'indicadores_configurados': list(self.tickers.keys()),
            'periodo_coleta': self.periodo_coleta,
            'timestamp': datetime.now().isoformat()
        }


# Função principal para uso standalone
def gerar_playbook_diario(caminho_saida: Optional[str] = None,
                         periodo_coleta: str = "5d") -> str:
    """
    Função principal para gerar playbook diário.

    Args:
        caminho_saida: Caminho para salvar o arquivo
        periodo_coleta: Período para coleta histórica

    Returns:
        Conteúdo do playbook gerado
    """
    gerador = GeradorPlaybookWIN(periodo_coleta)
    return gerador.gerar_playbook(caminho_saida=caminho_saida)


if __name__ == "__main__":
    # Exemplo de uso
    print("🧭 Gerador de Playbook Quantitativo - WIN")
    print("=" * 50)

    # Gerar playbook
    playbook = gerar_playbook_diario()

    print("\n📊 Métricas de Coleta:")
    gerador = GeradorPlaybookWIN()
    metricas = gerador.obter_metricas_coleta()
    for chave, valor in metricas.items():
        print(f"  {chave}: {valor}")

    print("\n✅ Playbook gerado com sucesso!")