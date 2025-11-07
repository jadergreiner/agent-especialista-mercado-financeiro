import yfinance as yf
from datetime import datetime
import pandas as pd

# ========== CONFIGURAÇÃO ==========
TICKERS = {
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DXY": "DX-Y.NYB",
    "VIX": "^VIX",
    "Treasuries_10Y": "^TNX",
    "Brent": "BZ=F",
    "Iron_Ore": "TIOc1",
    "USD/BRL": "USDBRL=X"
}

# ========== COLETA DE DADOS ==========
data = {}
for nome, t in TICKERS.items():
    try:
        info = yf.Ticker(t).history(period="5d")
        close = info["Close"].iloc[-1]
        prev = info["Close"].iloc[-2]
        var_pct = ((close - prev) / prev) * 100
        data[nome] = f"{var_pct:+.2f}%"
    except Exception as e:
        data[nome] = "N/D"

# ========== GERAÇÃO DO PLAYBOOK ==========
now = datetime.now()
data_hoje = now.strftime("%Y-%m-%d")
hora_geracao = now.strftime("%H:%M")

md = f"""# 🧭 PLAYBOOK QUÂNTICO – DIA NEUTRO (WIN)

> **Gerado automaticamente em {data_hoje} às {hora_geracao}**
>
> **Objetivo:** detectar o nascimento do direcional em dias sem campo dominante.

---

## 🕕 1. PRÉ-ABERTURA (07h00–09h00)
**Missão:** avaliar se o campo está realmente neutro.

| Indicador | Variação | Interpretação |
|------------|-----------|----------------|
| S&P500 | {data['S&P500']} | |
| NASDAQ | {data['NASDAQ']} | |
| DXY | {data['DXY']} | |
| VIX | {data['VIX']} | |
| Treasuries (10y) | {data['Treasuries_10Y']} | |
| Petróleo Brent | {data['Brent']} | |
| Minério de Ferro | {data['Iron_Ore']} | |
| USD/BRL | {data['USD/BRL']} | |
| DI1F / Política Fiscal | | |
| Agenda Macro | | |

**Campo Global:** ☐ Neutro ☐ Positivo ☐ Negativo
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
- Execute o script entre **08h45–08h55** para capturar o pré-mercado.
- Atualize manualmente os campos locais (DI1F, política fiscal, agenda macro).

---

"""

# Salva o arquivo .md
nome_arquivo = f"playbook_WIN_{data_hoje}.md"
with open(nome_arquivo, "w", encoding="utf-8") as f:
    f.write(md)

print(f"✅ Playbook gerado com sucesso: {nome_arquivo}")