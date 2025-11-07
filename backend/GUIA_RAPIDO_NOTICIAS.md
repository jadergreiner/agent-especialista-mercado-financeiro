# Guia Rápido - Sistema de Notícias

## ⚡ Comandos Essenciais

### Coletar Notícias Agora
```bash
cd backend
python consultar_noticias.py coletar
```

### Analisar Sentimento
```bash
python consultar_noticias.py analisar
```

### Ver Notícias Recentes
```bash
# Últimas 24h
python consultar_noticias.py listar

# Últimos 7 dias
python consultar_noticias.py listar --dias 7
```

### Ver Sentimento do Mercado
```bash
# Últimos 7 dias
python consultar_noticias.py sentimento

# Últimas 24h
python consultar_noticias.py sentimento --dias 1
```

## 📊 Fontes Ativas

| Fonte | Tipo | Status |
|-------|------|--------|
| InfoMoney | RSS | ✅ Ativo |
| Valor Econômico | RSS | ✅ Ativo |
| Estadão | RSS | ✅ Ativo |
| G1 Economia | RSS | ✅ Ativo |
| Finviz | Scraping | ✅ Ativo |
| MoneyTimes | Scraping | ✅ Ativo |
| B3 Notícias | Scraping | ✅ Ativo |
| Plantão B3 | Scraping | ✅ Ativo |
| Binance Square | Scraping | ⚠️ Parcial (conteúdo dinâmico) |
| NovaDAX | Scraping | ✅ Ativo |
| NewsAPI | API | 🔑 Requer chave |

## 🎯 Workflow Recomendado

### Diariamente (3x ao dia)

**07:00 - Pré-abertura**
```bash
python consultar_noticias.py coletar
python consultar_noticias.py analisar
python consultar_noticias.py sentimento --dias 1
```

**12:00 - Intraday**
```bash
python consultar_noticias.py coletar
python consultar_noticias.py analisar
```

**18:00 - Pós-fechamento**
```bash
python consultar_noticias.py coletar
python consultar_noticias.py analisar
python consultar_noticias.py sentimento --dias 7
```

## 📈 Interpretação do Sentimento

| Score | Interpretação | Ação Recomendada |
|-------|---------------|------------------|
| +0.5 a +1.0 | Muito Otimista | ⚠️ Evitar SHORT, considerar LONG |
| +0.2 a +0.5 | Otimista | ✅ Favorável para LONG |
| -0.2 a +0.2 | Neutro | ✅ Operar normalmente |
| -0.5 a -0.2 | Pessimista | ✅ Favorável para SHORT |
| -1.0 a -0.5 | Muito Pessimista | ⚠️ Evitar LONG, considerar SHORT |

## 🔧 Integração com Estratégias

### Verificar antes de operar

```python
from src.dados.analisador_sentimento import AnalisadorSentimento
from datetime import datetime, timedelta

analisador = AnalisadorSentimento()

# Sentimento das últimas 24h
agora = datetime.now()
ontem = agora - timedelta(days=1)
stats = analisador.obter_sentimento_periodo(ontem, agora)

score = stats['sentimento_medio']

if abs(score) > 0.5:
    print(f"⚠️ ALERTA: Sentimento extremo ({score:+.2f})")
    print("   Considerar reduzir exposição ou evitar operação")
else:
    print(f"✅ Sentimento normal ({score:+.2f})")
    print("   OK para operar")
```

## 📁 Estrutura de Arquivos

```
backend/
├── src/
│   └── dados/
│       ├── coletor_noticias.py      # Coleta de múltiplas fontes
│       └── analisador_sentimento.py # Análise de sentimento
├── data/
│   ├── noticias/
│   │   └── README.md                # Documentação completa
│   └── recomendacoes.sqlite         # Banco com tabela 'noticias'
└── consultar_noticias.py            # CLI principal
```

## 🐛 Troubleshooting

### Erro: "No module named 'bs4'"
```bash
pip install beautifulsoup4
```

### Erro: "No module named 'feedparser'"
```bash
pip install feedparser
```

### Nenhuma notícia coletada
- Verificar conexão de internet
- Algumas fontes podem estar temporariamente indisponíveis
- RSS feeds podem estar vazios (normal em certos horários)

### Binance retorna HTTP 202
- Site usa carregamento dinâmico (JavaScript)
- Resultados parciais são esperados
- Considerar usar API oficial Binance (requer chave)

## 📞 Comandos de Debug

```bash
# Ver todas as notícias (últimos 30 dias)
python consultar_noticias.py listar --dias 30 --limite 200

# Reprocessar análise de sentimento
python consultar_noticias.py analisar --limite 500

# Testar módulo diretamente
python src/dados/coletor_noticias.py
python src/dados/analisador_sentimento.py
```

## 🔑 NewsAPI (Opcional)

Para mais notícias internacionais:

1. Criar conta: https://newsapi.org
2. Obter chave API (plano grátis: 100 req/dia)
3. Usar ao coletar:

```bash
python consultar_noticias.py coletar --newsapi-key SUA_CHAVE_AQUI
```

Ou definir variável de ambiente:

```bash
# Windows PowerShell
$env:NEWSAPI_KEY="SUA_CHAVE_AQUI"
python consultar_noticias.py coletar

# Linux/Mac
export NEWSAPI_KEY="SUA_CHAVE_AQUI"
python consultar_noticias.py coletar
```

---

**Criado**: 05/11/2025
**Versão**: 1.0
