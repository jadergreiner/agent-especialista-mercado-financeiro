# Sistema de Coleta de Notícias Financeiras

## 📰 Visão Geral

Sistema automatizado de coleta e análise de notícias financeiras de múltiplas fontes, com análise de sentimento e impacto estimado para auxiliar na tomada de decisão de trading.

## 🎯 Funcionalidades

### Coleta Automática
- **RSS Feeds**: InfoMoney, Valor Econômico, Estadão, G1
- **Web Scraping**: Finviz, MoneyTimes, B3 Notícias, Plantão B3, Binance Square, NovaDAX
- **APIs**: NewsAPI (opcional, requer chave)

### Análise de Sentimento
- Classificação: **positivo**, **negativo**, **neutro**
- Score numérico: **-1.0** (bearish) a **+1.0** (bullish)
- Relevância para trading: **0.0** a **1.0**
- Impacto estimado: **alto**, **médio**, **baixo**

### Armazenamento
- Banco SQLite com 3 tabelas:
  - `noticias`: Dados principais das notícias
  - `noticias_palavras_chave`: Palavras-chave extraídas
  - `noticias_impacto_mercado`: Correlação com movimentos de mercado (futuro)

## 📥 Instalação

### Dependências

```bash
pip install beautifulsoup4==4.12.3
pip install feedparser==6.0.10
pip install requests==2.31.0
pip install textblob==0.17.1
pip install nltk==3.8.1
```

Ou instalar todas via `requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
```

## 🚀 Uso Rápido

### 1. Coletar Notícias

```bash
# Coletar de todas as fontes (RSS + scraping)
python consultar_noticias.py coletar

# Coletar incluindo NewsAPI (requer chave)
python consultar_noticias.py coletar --newsapi-key SUA_CHAVE_AQUI
```

**Obter chave NewsAPI**: https://newsapi.org (plano grátis: 100 requisições/dia)

### 2. Analisar Sentimento

```bash
# Processar notícias pendentes (sem análise)
python consultar_noticias.py analisar

# Processar até 200 notícias
python consultar_noticias.py analisar --limite 200
```

### 3. Listar Notícias

```bash
# Últimas 24 horas
python consultar_noticias.py listar

# Últimos 7 dias
python consultar_noticias.py listar --dias 7

# Máximo 50 notícias
python consultar_noticias.py listar --dias 3 --limite 50
```

### 4. Visualizar Sentimento Agregado

```bash
# Sentimento dos últimos 7 dias
python consultar_noticias.py sentimento

# Sentimento das últimas 24 horas
python consultar_noticias.py sentimento --dias 1

# Sentimento do último mês
python consultar_noticias.py sentimento --dias 30
```

## 📊 Exemplos de Saída

### Coleta Automática

```
====================================================================================================
COLETA AUTOMATICA DE NOTICIAS - 05/11/2025 22:39:19
====================================================================================================

================================================================================
COLETANDO NOTICIAS VIA RSS (ultimas 24h)
================================================================================

📰 Fonte: INFOMONEY
  Categoria: mercados... 2 relevantes
  Categoria: economia... 5 relevantes

✅ Total coletado: 7 notícias relevantes

🗞️ Finviz: coletando...
  coletadas 306 (pré-filtro duplicatas)

💾 Salvamento:
   Novas: 51
   Duplicadas: 255

====================================================================================================
RESUMO DA COLETA
====================================================================================================
   Noticias novas salvas: 58
   Total no banco (ultimas 24h): 50
====================================================================================================
```

### Análise de Sentimento

```
================================================================================
PROCESSANDO 58 NOTICIAS
================================================================================

  Processadas: 10/58
  Processadas: 20/58
  ...
  Processadas: 50/58

✅ Processadas: 58 notícias

====================================================================================================
SENTIMENTO DOS ULTIMOS 7 DIAS
====================================================================================================
   Total de notícias: 56
   Sentimento médio: +0.018
   Distribuição:
      📈 Positivas: 2 (3.6%)
      📉 Negativas: 0 (0.0%)
      ➡️  Neutras: 54 (96.4%)
   Relevância média: 0.095
====================================================================================================
```

### Visualização de Sentimento

```
====================================================================================================
SENTIMENTO DO PERIODO (7 dias)
====================================================================================================
   Período: 29/10/2025 a 05/11/2025
   Total de notícias: 56

   Sentimento médio: +0.018
   📉 Bearish ────────────────────█─────────────────── Bullish 📈
        -1.0                  0.0                  +1.0

   Distribuição:
      📈 Positivas: 2 (3.6%)
      📉 Negativas: 0 (0.0%)
      ➡️  Neutras: 54 (96.4%)

   Relevância média: 0.095

   📊 Interpretação:
      Mercado NEUTRO - Sem viés claro nas notícias
====================================================================================================
```

## 🔧 Uso Programático

### Coletar Notícias

```python
from src.dados.coletor_noticias import ColetorNoticias

coletor = ColetorNoticias()

# Coletar via RSS
noticias_rss = coletor.coletar_rss(limite_horas=24)
salvos_rss = coletor.salvar_noticias(noticias_rss)

# Coletar de fonte específica
noticias_finviz = coletor.coletar_finviz(limite_horas=24)
salvos_finviz = coletor.salvar_noticias(noticias_finviz)

# Coletar de todas as fontes
coletor.executar_coleta_automatica(newsapi_key="SUA_CHAVE")

# Obter notícias recentes
noticias = coletor.obter_noticias_recentes(horas=24, limite=50)
```

### Analisar Sentimento

```python
from src.dados.analisador_sentimento import AnalisadorSentimento
from datetime import datetime, timedelta

analisador = AnalisadorSentimento()

# Analisar uma notícia individual
analise = analisador.analisar_noticia(
    titulo="Ibovespa sobe 2,5% e fecha acima de 130 mil pontos",
    conteudo="O índice avançou forte com alta de commodities..."
)

print(f"Sentimento: {analise['sentimento']}")
print(f"Score: {analise['score_sentimento']}")
print(f"Relevância: {analise['relevancia_trading']}")
print(f"Impacto: {analise['impacto_estimado']}")

# Processar notícias pendentes
processadas = analisador.processar_noticias_pendentes(limite=100)

# Obter sentimento agregado de período
agora = datetime.now()
ontem = agora - timedelta(days=1)
stats = analisador.obter_sentimento_periodo(ontem, agora)

print(f"Sentimento médio: {stats['sentimento_medio']}")
print(f"Positivas: {stats['distribuicao']['positivas']}")
print(f"Negativas: {stats['distribuicao']['negativas']}")
```

## 🔍 Filtros de Relevância

### Palavras-chave em Português
- **Mercado**: bovespa, ibovespa, b3, bolsa, índice, dólar, câmbio, juros, selic
- **Indicadores**: pib, inflação, ipca, igpm, desemprego
- **Internacional**: fed, s&p, dow jones, nasdaq
- **Commodities**: petróleo, vale, minério
- **Eventos**: crise, recessão, alta, queda, recorde, balanço

### Palavras-chave em Inglês (Finviz)
- **Market**: stocks, equities, futures, sp500, nasdaq, dow
- **Economic**: fed, fomc, gdp, inflation, cpi, jobs, yields
- **Crypto**: bitcoin, btc, ethereum, eth, binance

## 📈 Integração com Estratégias

### Filtro de Sentimento

```python
from src.dados.analisador_sentimento import AnalisadorSentimento
from datetime import datetime, timedelta

def verificar_sentimento_mercado(data_operacao: datetime) -> dict:
    """
    Verifica sentimento do mercado antes de operar.

    Returns:
        {
            'pode_operar': bool,
            'sentimento': str,
            'score': float,
            'motivo': str
        }
    """
    analisador = AnalisadorSentimento()

    # Sentimento das últimas 24h
    inicio = data_operacao - timedelta(hours=24)
    stats = analisador.obter_sentimento_periodo(inicio, data_operacao)

    if stats['total'] < 5:
        return {
            'pode_operar': True,
            'sentimento': 'neutro',
            'score': 0.0,
            'motivo': 'Poucas notícias no período'
        }

    score = stats['sentimento_medio']

    # Sentimento muito negativo = evitar long
    if score < -0.5:
        return {
            'pode_operar': False,
            'sentimento': 'muito_negativo',
            'score': score,
            'motivo': 'Sentimento muito negativo nas últimas 24h'
        }

    # Sentimento muito positivo = evitar short
    if score > 0.5:
        return {
            'pode_operar': False,
            'sentimento': 'muito_positivo',
            'score': score,
            'motivo': 'Sentimento muito positivo nas últimas 24h'
        }

    return {
        'pode_operar': True,
        'sentimento': 'neutro' if abs(score) < 0.2 else ('positivo' if score > 0 else 'negativo'),
        'score': score,
        'motivo': 'Sentimento dentro da faixa aceitável'
    }

# Exemplo de uso
resultado = verificar_sentimento_mercado(datetime.now())
if resultado['pode_operar']:
    print(f"✅ Pode operar | Sentimento: {resultado['sentimento']} ({resultado['score']:+.2f})")
else:
    print(f"⚠️  Evitar operação | {resultado['motivo']}")
```

## 🗓️ Agendamento Automático

### Windows (Task Scheduler)

Criar arquivo `coletar_noticias.bat`:

```batch
@echo off
cd C:\repo\projetos\agent-especialista-mercado-financeiro\backend
C:\Users\Usuario\AppData\Local\Programs\Python\Python313\python.exe consultar_noticias.py coletar
C:\Users\Usuario\AppData\Local\Programs\Python\Python313\python.exe consultar_noticias.py analisar
```

Agendar no Task Scheduler:
- **Horário**: 07:00, 12:00, 18:00 (3x ao dia)
- **Ação**: Executar `coletar_noticias.bat`

### Linux/Mac (cron)

```bash
# Editar crontab
crontab -e

# Adicionar linhas (3x ao dia: 07:00, 12:00, 18:00)
0 7,12,18 * * * cd /path/to/backend && python3 consultar_noticias.py coletar && python3 consultar_noticias.py analisar
```

## 🧪 Testes

### Teste Manual de Scraping

```python
from src.dados.coletor_noticias import ColetorNoticias

coletor = ColetorNoticias()

# Testar cada fonte individualmente
print("=== Finviz ===")
noticias_finviz = coletor.coletar_finviz(limite_horas=24)
print(f"Coletadas: {len(noticias_finviz)}")

print("\n=== MoneyTimes ===")
noticias_mt = coletor.coletar_moneytimes(limite_horas=24)
print(f"Coletadas: {len(noticias_mt)}")

print("\n=== B3 Notícias ===")
noticias_b3 = coletor.coletar_b3_noticias(limite_horas=24)
print(f"Coletadas: {len(noticias_b3)}")

# Verificar qualidade dos dados
if noticias_finviz:
    print(f"\nExemplo Finviz:")
    n = noticias_finviz[0]
    print(f"  Título: {n.titulo[:60]}...")
    print(f"  URL: {n.url[:60]}...")
    print(f"  Data: {n.data_publicacao}")
```

## 📝 Estrutura do Banco de Dados

### Tabela: `noticias`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | Chave primária |
| titulo | TEXT | Título da notícia |
| conteudo | TEXT | Resumo/conteúdo |
| fonte | TEXT | Fonte (infomoney, finviz, etc.) |
| url | TEXT | URL única (UNIQUE constraint) |
| data_publicacao | TIMESTAMP | Data/hora de publicação |
| categoria | TEXT | Categoria da notícia |
| sentimento | TEXT | positivo/negativo/neutro |
| score_sentimento | REAL | -1.0 a +1.0 |
| relevancia_trading | REAL | 0.0 a 1.0 |
| impacto_estimado | TEXT | alto/medio/baixo |
| data_coleta | TIMESTAMP | Quando foi coletada |
| processada | BOOLEAN | Sentimento analisado? |

### Índices
- `idx_noticias_data_pub`: Busca por data de publicação
- `idx_noticias_fonte`: Filtro por fonte
- `idx_noticias_sentimento`: Filtro por sentimento

## 🔮 Próximos Passos

- [ ] Integrar com estratégias de trading (filtro de sentimento)
- [ ] Tabela `noticias_impacto_mercado`: correlacionar notícias com movimentos reais
- [ ] Validar acurácia do sentimento vs movimentos do mercado
- [ ] Adicionar mais fontes (Twitter/X, Telegram, Discord)
- [ ] Melhorar análise de sentimento com modelo ML treinado
- [ ] Dashboard visual com gráficos de sentimento ao longo do tempo
- [ ] Alertas por email/Telegram quando sentimento extremo detectado

## ⚙️ Configurações Avançadas

### Ajustar Palavras-chave

Editar `src/dados/coletor_noticias.py`:

```python
class ColetorNoticias:
    PALAVRAS_CHAVE_RELEVANTES = [
        # Adicionar suas próprias palavras-chave
        'minha_empresa',
        'meu_setor',
        # ...
    ]
```

### Ajustar Léxico de Sentimento

Editar `src/dados/analisador_sentimento.py`:

```python
class AnalisadorSentimento:
    PALAVRAS_POSITIVAS = [
        # Adicionar mais palavras positivas
        'boom',
        'explosão',
        # ...
    ]

    PALAVRAS_NEGATIVAS = [
        # Adicionar mais palavras negativas
        'catástrofe',
        'desastre',
        # ...
    ]
```

## 📞 Suporte

Em caso de dúvidas ou problemas:
1. Verificar logs de erro no terminal
2. Confirmar dependências instaladas: `pip list | grep -E "beautifulsoup|feedparser|requests"`
3. Testar conexão de rede: algumas fontes podem estar bloqueadas por firewall/proxy
4. Verificar se o banco SQLite está acessível: `ls -lh data/recomendacoes.sqlite`

---

**Última atualização**: 05/11/2025
