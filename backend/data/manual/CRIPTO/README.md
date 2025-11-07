# Cotações Manuais (Cripto)

Coloque aqui um CSV por ativo para habilitar a análise quando o símbolo não estiver mapeado em provedores (ex.: Yahoo, Binance etc.).

Padrão do arquivo: `backend/data/manual/CRIPTO/<SIMBOLO>.csv`

Formato esperado (case-insensitive):

- Colunas: `datetime, open, high, low, close, volume`
- Delimitador: vírgula ou ponto-e-vírgula
- `datetime` em UTC (timezone será removido)
- `volume` é opcional

Exemplo (cabeçalho + 2 linhas):

```csv
datetime,open,high,low,close,volume
2025-01-03T00:00:00Z,1.23,1.30,1.20,1.28,123456
2025-01-04T00:00:00Z,1.28,1.35,1.25,1.33,234567
```

Observações:

- O analisador usará até 100 dias mais recentes.
- Caso haja erro de leitura, ele informará o motivo (coluna ausente, data inválida etc.).
- Se preferir, você também pode nos informar o símbolo correto no provedor (ex.: Yahoo `ABC-USD`) para integrar automaticamente.
