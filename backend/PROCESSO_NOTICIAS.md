# 📋 Processo de Coleta e Análise de Notícias

## 🔄 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                        COLETA DE NOTÍCIAS                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌─────────────────────────────────────────────┐
        │  1. Executar: consultar_noticias.py coletar │
        └─────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌───────────────────┐       ┌───────────────────┐
        │   RSS FEEDS       │       │   WEB SCRAPING    │
        ├───────────────────┤       ├───────────────────┤
        │ • InfoMoney       │       │ • Finviz          │
        │ • Valor Econômico │       │ • MoneyTimes      │
        │ • Estadão         │       │ • B3 Notícias     │
        │ • G1 Economia     │       │ • Plantão B3      │
        │                   │       │ • Binance Square  │
        │                   │       │ • NovaDAX         │
        └───────────────────┘       └───────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  FILTRO DE RELEVÂNCIA   │
                    ├─────────────────────────┤
                    │ Palavras-chave:         │
                    │ • Mercado (BR + EN)     │
                    │ • Indicadores econômicos│
                    │ • Commodities           │
                    │ • Crypto                │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   DEDUPLICAÇÃO (URL)    │
                    │   Evita repetições      │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  SALVAR NO SQLITE       │
                    │  Tabela: noticias       │
                    │  Campo: processada = 0  │
                    └─────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     ANÁLISE DE SENTIMENTO                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
        ┌─────────────────────────────────────────────┐
        │  2. Executar: consultar_noticias.py analisar│
        └─────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  BUSCAR NOTÍCIAS        │
                    │  WHERE processada = 0   │
                    └─────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌───────────────────┐       ┌───────────────────┐
        │  ANÁLISE LÉXICA   │       │ ANÁLISE PADRÕES   │
        ├───────────────────┤       ├───────────────────┤
        │ Dicionário de     │       │ Regex para:       │
        │ palavras:         │       │ • "sobe X%"       │
        │ • Positivas (alta,│       │ • "cai Y%"        │
        │   lucro, ganho)   │       │ • "avança Z%"     │
        │ • Negativas (queda│       │ • "recua W%"      │
        │   prejuízo, crise)│       │                   │
        │ • Incerteza       │       │ Extrai magnitude  │
        └───────────────────┘       └───────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │  CALCULAR SCORES                │
                    ├─────────────────────────────────┤
                    │ • Sentimento: -1.0 a +1.0       │
                    │   (léxico 50% + padrões 30% +   │
                    │    incerteza 20%)               │
                    │                                 │
                    │ • Relevância: 0.0 a 1.0         │
                    │   (entidades + números + magn.) │
                    │                                 │
                    │ • Impacto: alto/médio/baixo     │
                    │   (baseado em relevância + score│
                    └─────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │  CLASSIFICAR SENTIMENTO         │
                    ├─────────────────────────────────┤
                    │ score > +0.2  → Positivo  📈    │
                    │ score < -0.2  → Negativo  📉    │
                    │ -0.2 ≤ score ≤ +0.2 → Neutro ➡️ │
                    └─────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │  EXTRAIR PALAVRAS-CHAVE         │
                    │  • Entidades (Ibovespa, Dólar)  │
                    │  • Palavras de sentimento       │
                    └─────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │  ATUALIZAR SQLITE               │
                    │  • sentimento                   │
                    │  • score_sentimento             │
                    │  • relevancia_trading           │
                    │  • impacto_estimado             │
                    │  • processada = 1               │
                    │                                 │
                    │  + Tabela palavras_chave        │
                    └─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      CONSULTA E USO                                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌───────────────────────┐   ┌───────────────────────┐
        │ 3a. LISTAR NOTÍCIAS   │   │ 3b. VER SENTIMENTO    │
        │                       │   │     AGREGADO          │
        │ consultar_noticias.py │   │                       │
        │ listar --dias 7       │   │ consultar_noticias.py │
        │                       │   │ sentimento --dias 7   │
        └───────────────────────┘   └───────────────────────┘
                    │                           │
                    ▼                           ▼
        ┌───────────────────────┐   ┌───────────────────────┐
        │ Mostra por fonte:     │   │ Estatísticas:         │
        │ • Título (resumido)   │   │ • Total notícias      │
        │ • Data/hora           │   │ • Sentimento médio    │
        │ • URL                 │   │ • Distribuição        │
        │ • Sentimento 📈📉➡️   │   │   (pos/neg/neutro)    │
        │ • Score (-1 a +1)     │   │ • Relevância média    │
        │ • Relevância (0 a 1)  │   │ • Barra visual        │
        │ • Impacto             │   │ • Interpretação       │
        └───────────────────────┘   └───────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│              INTEGRAÇÃO COM ESTRATÉGIAS DE TRADING                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌───────────────────────┐   ┌───────────────────────┐
        │ FILTRO PRÉ-OPERAÇÃO   │   │ CONFIRMAÇÃO SINAL     │
        ├───────────────────────┤   ├───────────────────────┤
        │ Evitar operar quando: │   │ Validar sinal técnico │
        │                       │   │ com sentimento:       │
        │ • Sentimento > +0.5   │   │                       │
        │   (muito otimista)    │   │ Sinal COMPRA + sent>0 │
        │   → Evitar SHORT      │   │ → Executar ✅         │
        │                       │   │                       │
        │ • Sentimento < -0.5   │   │ Sinal COMPRA + sent<0 │
        │   (muito pessimista)  │   │ → Aguardar ⚠️         │
        │   → Evitar LONG       │   │                       │
        │                       │   │ Sinal VENDA + sent<0  │
        │ • Relevância > 0.7    │   │ → Executar ✅         │
        │   + Impacto alto      │   │                       │
        │   → Dia de risco      │   │ Sinal VENDA + sent>0  │
        │      elevado          │   │ → Aguardar ⚠️         │
        └───────────────────────┘   └───────────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │  AJUSTE DE TARGETS/STOPS        │
                    ├─────────────────────────────────┤
                    │ Sentimento > +0.4:              │
                    │   Target = target_base × 1.2    │
                    │   (mercado favorável)           │
                    │                                 │
                    │ Sentimento < -0.4:              │
                    │   Target = target_base × 0.8    │
                    │   Stop = stop_base × 0.8        │
                    │   (mercado desfavorável)        │
                    └─────────────────────────────────┘
```

## 📂 Estrutura de Dados

### Tabela: `noticias`

```sql
CREATE TABLE noticias (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    conteudo TEXT,
    fonte TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    data_publicacao TIMESTAMP NOT NULL,
    categoria TEXT,

    -- Análise de sentimento
    sentimento TEXT,              -- 'positivo', 'negativo', 'neutro'
    score_sentimento REAL,        -- -1.0 a +1.0
    relevancia_trading REAL,      -- 0.0 a 1.0
    impacto_estimado TEXT,        -- 'alto', 'medio', 'baixo'

    -- Controle
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processada BOOLEAN DEFAULT 0  -- 0 = pendente, 1 = analisada
);
```

### Tabela: `noticias_palavras_chave`

```sql
CREATE TABLE noticias_palavras_chave (
    id INTEGER PRIMARY KEY,
    id_noticia INTEGER NOT NULL,
    palavra_chave TEXT NOT NULL,
    FOREIGN KEY (id_noticia) REFERENCES noticias(id)
);
```

### Tabela: `noticias_impacto_mercado` (futuro)

```sql
CREATE TABLE noticias_impacto_mercado (
    id INTEGER PRIMARY KEY,
    id_noticia INTEGER NOT NULL,
    data_pregao DATE NOT NULL,
    simbolo TEXT NOT NULL,
    variacao_1h REAL,   -- Validar se notícia previu movimento
    variacao_1d REAL,
    variacao_3d REAL,
    impacto_real TEXT,  -- 'confirmado', 'neutro', 'contrario'
    FOREIGN KEY (id_noticia) REFERENCES noticias(id)
);
```

## 🎯 Workflow Diário Recomendado

### Manhã (07:00 - Pré-abertura)
```bash
# 1. Coletar notícias noturnas + manhã
python consultar_noticias.py coletar

# 2. Analisar sentimento
python consultar_noticias.py analisar

# 3. Verificar sentimento das últimas 24h
python consultar_noticias.py sentimento --dias 1

# 4. Decidir estratégia do dia baseado no sentimento
```

**Interpretação**:
- Sentimento > +0.3: Dia favorável para LONG
- Sentimento < -0.3: Dia favorável para SHORT
- |Sentimento| < 0.2: Operar normalmente

### Meio-dia (12:00 - Intraday)
```bash
# 1. Atualizar notícias
python consultar_noticias.py coletar

# 2. Analisar novas notícias
python consultar_noticias.py analisar

# 3. Verificar se houve mudança de sentimento
python consultar_noticias.py sentimento --dias 1
```

**Uso**: Detectar mudanças de sentimento durante o pregão

### Tarde (18:00 - Pós-fechamento)
```bash
# 1. Coletar notícias do fechamento
python consultar_noticias.py coletar

# 2. Analisar todas pendentes
python consultar_noticias.py analisar

# 3. Revisar sentimento da semana
python consultar_noticias.py sentimento --dias 7

# 4. Listar principais notícias
python consultar_noticias.py listar --dias 1 --limite 20
```

**Uso**: Preparação para o dia seguinte

## 📊 Exemplo de Integração em Código

### 1. Verificar sentimento antes de operar

```python
from src.dados.analisador_sentimento import AnalisadorSentimento
from datetime import datetime, timedelta

def pode_operar_hoje() -> dict:
    """Verifica se condições de sentimento permitem operar."""

    analisador = AnalisadorSentimento()

    # Sentimento das últimas 24h
    agora = datetime.now()
    ontem = agora - timedelta(days=1)
    stats = analisador.obter_sentimento_periodo(ontem, agora)

    if stats['total'] < 5:
        return {
            'pode_operar': True,
            'motivo': 'Poucas notícias - operar normalmente',
            'score': 0.0
        }

    score = stats['sentimento_medio']

    # Sentimento extremo = risco elevado
    if abs(score) > 0.5:
        return {
            'pode_operar': False,
            'motivo': f'Sentimento extremo ({score:+.2f})',
            'score': score,
            'acao': 'Reduzir exposição ou aguardar'
        }

    # Sentimento moderado = ajustar estratégia
    if score > 0.3:
        return {
            'pode_operar': True,
            'motivo': f'Sentimento otimista ({score:+.2f})',
            'score': score,
            'sugestao': 'Favorável para LONG, evitar SHORT'
        }

    if score < -0.3:
        return {
            'pode_operar': True,
            'motivo': f'Sentimento pessimista ({score:+.2f})',
            'score': score,
            'sugestao': 'Favorável para SHORT, evitar LONG'
        }

    return {
        'pode_operar': True,
        'motivo': f'Sentimento neutro ({score:+.2f})',
        'score': score,
        'sugestao': 'Operar normalmente'
    }

# Uso no início do dia
resultado = pode_operar_hoje()
print(f"{'✅' if resultado['pode_operar'] else '⚠️'} {resultado['motivo']}")
if 'sugestao' in resultado:
    print(f"   💡 {resultado['sugestao']}")
```

### 2. Confirmar sinal técnico com sentimento

```python
def validar_sinal_com_sentimento(sinal_tecnico: str, preco_atual: float) -> bool:
    """
    Valida sinal técnico com análise de sentimento.

    Args:
        sinal_tecnico: 'COMPRA', 'VENDA', ou None
        preco_atual: Preço atual do ativo

    Returns:
        True se sentimento confirma sinal, False caso contrário
    """
    if not sinal_tecnico:
        return False

    analisador = AnalisadorSentimento()
    agora = datetime.now()
    ontem = agora - timedelta(hours=24)

    stats = analisador.obter_sentimento_periodo(ontem, agora)
    score = stats['sentimento_medio']

    # COMPRA: sentimento deve ser neutro ou positivo
    if sinal_tecnico == 'COMPRA':
        if score < -0.3:
            print(f"⚠️ COMPRA rejeitada: sentimento muito negativo ({score:+.2f})")
            return False
        return True

    # VENDA: sentimento deve ser neutro ou negativo
    if sinal_tecnico == 'VENDA':
        if score > 0.3:
            print(f"⚠️ VENDA rejeitada: sentimento muito positivo ({score:+.2f})")
            return False
        return True

    return True

# Uso em estratégia
sinal = gerar_sinal_tecnico()  # De sua estratégia
if sinal and validar_sinal_com_sentimento(sinal, preco_atual):
    executar_ordem(sinal)
else:
    print("Sinal rejeitado por sentimento")
```

### 3. Ajustar targets baseado em sentimento

```python
def calcular_target_com_sentimento(target_base: float, stop_base: float) -> dict:
    """
    Ajusta target e stop baseado no sentimento de mercado.

    Args:
        target_base: Target calculado pela estratégia técnica
        stop_base: Stop calculado pela estratégia técnica

    Returns:
        dict com target e stop ajustados
    """
    analisador = AnalisadorSentimento()
    agora = datetime.now()
    ontem = agora - timedelta(hours=24)

    stats = analisador.obter_sentimento_periodo(ontem, agora)
    score = stats['sentimento_medio']

    # Sentimento forte positivo: expandir target
    if score > 0.4:
        return {
            'target': target_base * 1.2,  # +20%
            'stop': stop_base,
            'motivo': f'Sentimento muito positivo ({score:+.2f}) - target expandido'
        }

    # Sentimento moderado positivo: leve expansão
    if score > 0.2:
        return {
            'target': target_base * 1.1,  # +10%
            'stop': stop_base,
            'motivo': f'Sentimento positivo ({score:+.2f}) - target aumentado'
        }

    # Sentimento forte negativo: reduzir target
    if score < -0.4:
        return {
            'target': target_base * 0.8,  # -20%
            'stop': stop_base * 0.9,      # Stop mais apertado
            'motivo': f'Sentimento muito negativo ({score:+.2f}) - alvos reduzidos'
        }

    # Sentimento moderado negativo: leve redução
    if score < -0.2:
        return {
            'target': target_base * 0.9,  # -10%
            'stop': stop_base,
            'motivo': f'Sentimento negativo ({score:+.2f}) - target reduzido'
        }

    # Sentimento neutro: manter valores originais
    return {
        'target': target_base,
        'stop': stop_base,
        'motivo': f'Sentimento neutro ({score:+.2f}) - valores padrão'
    }

# Uso
ajuste = calcular_target_com_sentimento(target_base=300, stop_base=150)
print(f"Target: {ajuste['target']:.0f} pts | Stop: {ajuste['stop']:.0f} pts")
print(f"💡 {ajuste['motivo']}")
```

## 🔗 Links da Documentação

- **README completo**: `backend/data/noticias/README.md`
- **Guia rápido**: `backend/GUIA_RAPIDO_NOTICIAS.md`
- **Resumo do sistema**: `backend/RESUMO_SISTEMA_NOTICIAS.md`
- **Este documento**: `backend/PROCESSO_NOTICIAS.md`

## 📞 Comandos Úteis

```bash
# Ver ajuda dos comandos
python consultar_noticias.py --help
python consultar_noticias.py listar --help
python consultar_noticias.py sentimento --help

# Testar módulos diretamente
python src/dados/coletor_noticias.py      # Teste de coleta
python src/dados/analisador_sentimento.py # Teste de análise

# Ver estatísticas do banco
sqlite3 data/recomendacoes.sqlite "SELECT COUNT(*) FROM noticias"
sqlite3 data/recomendacoes.sqlite "SELECT fonte, COUNT(*) FROM noticias GROUP BY fonte"
sqlite3 data/recomendacoes.sqlite "SELECT sentimento, COUNT(*) FROM noticias WHERE processada=1 GROUP BY sentimento"
```

---

**Atualizado**: 05/11/2025
**Versão**: 1.0
