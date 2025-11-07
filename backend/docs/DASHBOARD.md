# Dashboard (Streamlit)

Visualização rápida de relatórios (SQLite) e sinais (bus).

## Pré-requisitos

- Python 3.10+
- Instalar dependências do backend (inclui Streamlit):

```powershell
cd c:\repo\projetos\agent-especialista-mercado-financeiro\backend
pip install -r .\requirements.txt
```

## Executar

```powershell
streamlit run .\app_dashboard.py
```

- Página "Relatórios":
  - Carrega os relatórios recentes da tabela `relatorios_intraday` (classeAtivo = forex/cripto)
  - Filtros por classe e par/ativo; inspeção do payload JSON por ID
  - Indicadores PASS/FAIL de validação do payload
  - Revalidação em lote ou individual (útil após mudanças nos schemas)
  - Filtro “Somente inválidos (FAIL)” para auditoria rápida

- Página "Sinais":
  - Lista arquivos JSON do diretório `backend/bus`
  - Filtros por contrato/classe/instrumento; visualização do envelope (valid, errors, event)
  - Revalidação individual; indicador PASS/FAIL por linha; botão “Atualizar lista”

## Geração de dados

Relatórios Forex + JSON + persistência

```powershell
python .\consultar_intraday_forex.py analisar EURUSD
```

Relatórios Cripto + JSON + persistência

```powershell
python .\consultar_trading_cripto.py analisar BTCUSDT
```

Publicação de sinais (gera eventos no `backend/bus`)

```powershell
# Forex
python .\publicar_sinais.py forex .\relatorios_intraday\EURUSD_YYYYMMDD_HHMMSS.json

# Cripto
python .\publicar_sinais.py cripto .\relatorios_trading\BTCUSDT_YYYYMMDD_HHMMSS.json
```

## Observações

- Se o banco não existir ainda, gere relatórios para popular.
- Os eventos escritos no bus já trazem o status de validação contra os schemas (PASS/erros listados).
- Os relatórios `report.intraday.v1` podem incluir campos opcionais:
  - `analises.tecnica.srisDetalhado` (H1/H4/D1) e `analises.tecnica.vwapSessoes` (tokyo/londres/ny)
  - `qualidade.dxy` (ok/fallback/indisponivel) e `qualidade.calendario` (ok/mock)
  - A dashboard exibe o JSON integral; campos opcionais não quebram a validação do contrato v1.
