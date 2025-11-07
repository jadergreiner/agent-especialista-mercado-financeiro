# Sistema de Importação Resiliente de Dados

## Visão Geral
O sistema de importação de dados manuais via CSV é completamente resiliente e garante **uma única linha por data** para cada instrumento, sem duplicação, independentemente de quantas vezes os arquivos sejam importados.

## Características de Resiliência

### 1. **Estratégia UPSERT (INSERT OR REPLACE)**
- **Novos registros**: São inseridos normalmente no banco
- **Registros existentes**: São atualizados com os dados mais recentes
- **Garantia de unicidade**: Índice único em `(data, instrumento, fonte)`

### 2. **Múltiplas Importações Seguras**
Você pode:
- ✅ Importar o mesmo arquivo múltiplas vezes
- ✅ Importar múltiplos arquivos com datas sobrepostas
- ✅ Adicionar novos arquivos sem risco de duplicação
- ✅ Atualizar dados existentes (última importação vence)

### 3. **Relatórios Detalhados**
Cada importação mostra:
- **📊 Processados**: Total de linhas lidas do CSV
- **✨ Novos**: Registros inseridos pela primeira vez
- **🔄 Atualizados**: Registros que já existiam e foram atualizados
- **❌ Erros**: Linhas que falharam no processamento

## Exemplos de Uso

### Importar Todos os CSVs de um Ativo
```bash
cd backend
python src/cli_importar_csv.py importar-diario --fonte investing.com
```
Importa automaticamente todos os CSVs de `data/manual/WIN/*.csv`

### Importar Arquivo Específico
```bash
python src/cli_importar_csv.py importar-diario \
  --arquivo "data/manual/WIN/meus_dados.csv" \
  --fonte investing.com
```

### Importar Múltiplos Ativos
```bash
# WIN
python src/cli_importar_csv.py importar-diario \
  --dir data/manual/WIN --fonte investing.com

# DOL (Dólar Futuro)
python src/cli_importar_csv.py importar-diario \
  --dir data/manual/DOL --fonte investing.com
```

## Estrutura de Diretórios
```
backend/data/manual/
├── WIN/                          # Ibovespa Futuros
│   ├── historico_2024.csv
│   ├── historico_2025.csv
│   └── dados_novos_win.csv
├── DOL/                          # Dólar Futuro
│   └── historico_dolar.csv
└── WDO/                          # Mini Dólar
    └── historico_mini_dolar.csv
```

## Formato CSV Aceito

### Formatos de Data Suportados
- `dd.mm.yyyy` (ex: 04.11.2025)
- `dd/mm/yyyy` (ex: 04/11/2025)
- `dd-mm-yyyy` (ex: 04-11-2025)

### Formatos de Números PT-BR
- **Decimais**: Vírgula `,` (ex: 152.944,50)
- **Milhares**: Ponto `.` (ex: 152.944)
- **Volume**: Suporta K/M (ex: 50.000K = 50.000.000)

### Colunas Obrigatórias
```csv
Data,Último,Abertura,Máxima,Mínima,Vol.,Var%
04/11/2025,152.944,152.050,153.800,150.900,50.000K,0,05%
05/11/2025,153.500,152.944,154.200,152.500,48.500K,0,36%
```

### Encodings Suportados
- UTF-8 (com ou sem BOM)
- UTF-8-sig
- CP1252 (Windows Latin-1)
- Latin-1 (ISO-8859-1)

## Teste de Resiliência Executado

### Cenário 1: Re-importação do Mesmo Arquivo
```bash
# Primeira importação
python src/cli_importar_csv.py importar-diario --fonte investing.com
# Resultado: 22 novos

# Segunda importação (mesmo arquivo)
python src/cli_importar_csv.py importar-diario --fonte investing.com
# Resultado: 22 atualizados, 0 novos ✅
```

### Cenário 2: Múltiplos Arquivos com Datas Sobrepostas
```bash
# Arquivo 1: 22 registros (06/10/2025 a 04/11/2025)
# Arquivo 2: 5 registros (04/11/2025 a 08/11/2025)

python src/cli_importar_csv.py importar-diario --fonte investing.com
# Resultado:
#   Arquivo 1: 22 atualizados
#   Arquivo 2: 1 atualizado (04/11 sobreposto) + 4 novos (05-08/11)
#   Total: 26 registros únicos ✅
```

### Cenário 3: Terceira Importação do Arquivo 2
```bash
python src/cli_importar_csv.py importar-diario \
  --arquivo "data/manual/WIN/dados_novos_win.csv" \
  --fonte investing.com
# Resultado: 5 atualizados, 0 novos
# Banco continua com 26 registros únicos ✅
```

## Estratégia de Unicidade

### Chave Única
```sql
CREATE UNIQUE INDEX idx_precos_diarios_uniq
ON precos_diarios(data, instrumento, ifnull(fonte, ''));
```

### Comportamento
- **Mesma fonte**: Última importação vence (REPLACE)
- **Fontes diferentes**: Mantém registros separados
- **Exemplo**:
  ```
  2025-11-04 | WIN | investing.com  → Um registro
  2025-11-04 | WIN | manual         → Outro registro
  ```

## Integridade de Dados

### Validações Automáticas
- ✅ Detecção automática de encoding e delimitador
- ✅ Remoção de BOM (Byte Order Mark)
- ✅ Normalização de headers (case-insensitive, sem aspas)
- ✅ Conversão PT-BR → formato padrão
- ✅ Tratamento de erros por linha (não interrompe importação inteira)

### Tratamento de Erros
- Linhas com erro são reportadas individualmente
- Contador de erros é exibido no relatório final
- Importação continua mesmo com erros em linhas específicas

## Melhores Práticas

### 1. Organização de Arquivos
```
✅ BOM: data/manual/WIN/historico_2024.csv
✅ BOM: data/manual/WIN/historico_2025.csv
❌ EVITAR: data/manual/historico_win_2024.csv
```

### 2. Nomenclatura de Fontes
- Use nomes descritivos: `investing.com`, `yahoo_finance`, `manual`
- Mantenha consistência entre importações
- Fonte ajuda a rastrear origem dos dados

### 3. Workflow Recomendado
1. **Adicionar novos arquivos** em `data/manual/<ATIVO>/`
2. **Executar importação** com `--fonte` apropriada
3. **Verificar relatório** para conferir novos/atualizados
4. **Manter arquivos** no diretório (re-importação é segura)

### 4. Atualização de Dados
Para atualizar dados históricos:
1. Edite o CSV com novos valores
2. Re-importe o arquivo
3. Registros serão atualizados automaticamente

## Próximos Passos
- [ ] Integração com APIs para coleta automática
- [ ] Scheduler para importação periódica
- [ ] Dashboard de monitoramento de importações
- [ ] Export de dados para análise externa
- [ ] Suporte a outros formatos (Excel, JSON)
