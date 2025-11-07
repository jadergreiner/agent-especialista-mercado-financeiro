# Como Obter Boletins Diários da B3

## 📥 Opções de Download

### Opção 1: Site B3 - Séries Históricas (RECOMENDADO)

**URL**: https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-de-derivativos/

**Passos**:
1. Acessar link acima
2. Selecionar "Mercado de Derivativos"
3. Escolher período desejado (ex: 01/11/2024 a 05/11/2024)
4. Baixar arquivo (formato TXT ou CSV)
5. Salvar em: `backend/data/boletins_b3/raw/2024-11/boletim_b3_2024-11-05.txt`

**Dados Disponíveis**:
- Preços OHLC (abertura, máxima, mínima, fechamento)
- Ajuste diário
- Volume negociado (contratos e financeiro)
- Número de negócios
- Contratos em aberto (Open Interest)
- Por vencimento

### Opção 2: Portal do Investidor B3

**URL**: https://www.investidor.b3.com.br/

**Passos**:
1. Menu "Market Data" → "Cotações"
2. Selecionar "Derivativos"
3. Filtrar por "WIN" (Mini Índice)
4. Exportar dados em CSV/Excel

### Opção 3: API de Dados (Pago/Limitado)

**URL**: https://developers.b3.com.br/

A B3 oferece APIs para desenvolvedores, mas requer cadastro e pode ter custos.

## 📊 Formato Esperado

### Campos Mínimos Necessários

Para cada pregão, precisamos de:

```
Data, Símbolo, Vencimento, Abertura, Máxima, Mínima, Fechamento, Ajuste, Volume, Negócios, OI
2024-11-05, WIN, 2024-12-27, 128500, 129200, 128100, 128950, 128950, 285000, 125000, 520000
```

### Campos Opcionais (Se Disponíveis)

```
Spread, MelhorBid, MelhorAsk, PosPF, PosInst, PosEst
5.0, 128945, 128950, 15000, -8000, -7000
```

## 🔄 Exemplo de Arquivo Posicional B3

O formato padrão da B3 usa layout posicional fixo. Exemplo:

```
00COTAHIST20241105      # Header com data
01WIN 20241227128500129200128100128950...  # Linha de dados
99TOTAL000001           # Footer com total de registros
```

**Documentação do Layout**:
- Disponível em: https://www.b3.com.br/ (seção "Dados Históricos")
- Arquivo: "SeriesHistoricas_Layout.pdf"

## 🛠️ Processamento Após Download

Após baixar o arquivo:

```bash
cd backend

# Opção 1: Processar via módulo Python (quando parser estiver pronto)
python src/dados/boletim_b3.py importar data/boletins_b3/raw/2024-11/boletim_b3_2024-11-05.txt

# Opção 2: Consultar dados importados
python consultar_boletins.py consultar WIN 5
```

## 📝 Checklist de Dados

Após importar, verificar:

- [ ] Preços fazem sentido (ex: WIN entre 120.000 e 135.000)
- [ ] Volume > 0 (dias úteis)
- [ ] Open Interest cresce ao longo do mês
- [ ] Spread < 20 pontos (condição normal)
- [ ] Sem gaps grandes na série temporal

```bash
python consultar_boletins.py verificar WIN 30
```

## 🚨 Dicas Importantes

### 1. Contratos WIN

O WIN tem vencimentos mensais. Em novembro/2024:
- **Contrato atual**: WINZ24 (dezembro/2024)
- **Próximo vencimento**: WINF25 (janeiro/2025)

Sempre baixar dados do **contrato mais líquido** (geralmente o mais próximo, exceto na semana de vencimento).

### 2. Horário de Divulgação

Boletins são publicados após o fechamento do pregão:
- **Pregão normal**: 18:00 (divulgação ~18:30)
- **After-hours**: 19:30 (divulgação ~20:00)

### 3. Feriados e Finais de Semana

Não há boletins em:
- Sábados e domingos
- Feriados nacionais (B3 fechada)
- Datas especiais (ex: Sexta-feira Santa, véspera de Ano Novo)

## 📞 Suporte

**Dúvidas sobre acesso aos dados**:
- Telefone B3: 0800 123 4567
- Email: marketdata@b3.com.br
- FAQ: https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/mercado-de-derivativos/contratos-disponiveis/

## ✅ Próximos Passos

1. **Download manual de 1 arquivo de teste**:
   - Baixar boletim de qualquer dia útil recente
   - Salvar em `backend/data/boletins_b3/raw/`
   - Enviar para análise do formato

2. **Desenvolvimento do parser**:
   - Analisar estrutura do arquivo
   - Implementar extração de campos
   - Validar dados importados

3. **Importação em lote**:
   - Script para baixar histórico completo 2024
   - Processar todos os arquivos
   - Validar qualidade da série

4. **Automação**:
   - Scheduler para download diário
   - Processamento automático
   - Alertas de falha
