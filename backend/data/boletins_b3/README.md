# Boletins Diários B3 - WIN

## Estrutura de Diretórios

```
boletins_b3/
├── raw/          # Arquivos originais baixados da B3 (não processar manualmente)
│   ├── 2024-01/
│   ├── 2024-02/
│   └── ...
└── processed/    # Arquivos processados (CSV/JSON) para análise manual
    ├── 2024-01/
    └── ...
```

## Como Adicionar Boletins Manualmente

1. **Baixar boletim da B3**:
   - Acesse: https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-de-derivativos/
   - Selecione a data desejada
   - Baixe o arquivo (formato TXT ou CSV)

2. **Salvar na pasta correta**:
   - Copie o arquivo para `raw/YYYY-MM/boletim_b3_YYYY-MM-DD.txt`
   - Exemplo: `raw/2024-11/boletim_b3_2024-11-05.txt`

3. **Processar o arquivo**:
   ```bash
   cd backend
   python src/dados/boletim_b3.py
   ```

## Formatos Suportados

- **TXT Posicional**: Formato padrão da B3 (layout documentado no site)
- **CSV**: Exportação via site da B3
- **PDF**: Boletim diário (requer pdfplumber/tabula) - EM DESENVOLVIMENTO

## Exemplo de Dados Necessários

Para cada pregão, o sistema precisa de:

- Data do pregão
- Símbolo (WIN, WDO, DOL, IND)
- Vencimento do contrato
- Preços: abertura, máxima, mínima, fechamento, ajuste
- Volume: contratos, financeiro, número de negócios
- Open Interest (contratos em aberto)
- Spread bid/ask (quando disponível)
- Posicionamento por tipo de investidor (quando disponível)

## Consulta aos Dados

Após importação, os dados estarão disponíveis em:
- **Banco SQLite**: `backend/data/recomendacoes.sqlite` - tabela `boletins_diarios`
- **Consulta via código**:
  ```python
  from src.dados.boletim_b3 import GerenciadorBoletimB3
  from datetime import date

  gerenciador = GerenciadorBoletimB3()
  boletins = gerenciador.obter_boletins("WIN", date(2024, 11, 1), date(2024, 11, 5))
  ```

## Status

- ✅ Estrutura de diretórios criada
- ✅ Tabelas no banco de dados criadas
- ✅ Módulo Python base implementado
- ⏳ Parser de arquivos B3 (aguardando exemplo de arquivo)
- ⏳ Cálculo de métricas avançadas
- ⏳ Integração com estratégias de trading
