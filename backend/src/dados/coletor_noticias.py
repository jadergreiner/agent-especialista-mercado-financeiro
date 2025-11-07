# -*- coding: utf-8 -*-
"""
Sistema de Coleta Automática de Notícias Financeiras.

Este módulo coleta notícias de múltiplas fontes para análise de impacto
no mercado financeiro, especialmente focado em índices brasileiros (IBOV, WIN).

Fontes implementadas:
1. RSS Feeds (InfoMoney, Valor Econômico, etc.)
2. APIs públicas (NewsAPI, AlphaVantage News)
3. Web Scraping (quando necessário e permitido)

Dados armazenados:
- Título e conteúdo da notícia
- Fonte e URL
- Data/hora de publicação
- Categorias/tags
- Sentimento (positivo/negativo/neutro)
- Score de relevância para trading
"""

import sqlite3
import feedparser
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
from urllib.parse import urlparse
import time
from bs4 import BeautifulSoup


# Configuração de caminhos
DIRETORIO_BASE = Path(__file__).parent.parent.parent / "data" / "noticias"
CAMINHO_DB = Path(__file__).parent.parent.parent / "data" / "recomendacoes.sqlite"


@dataclass
class Noticia:
    """Estrutura de dados para uma notícia."""

    titulo: str
    conteudo: str
    fonte: str
    url: str
    data_publicacao: datetime
    categoria: str

    # Campos de análise (preenchidos posteriormente)
    sentimento: Optional[str] = None  # 'positivo', 'negativo', 'neutro'
    score_sentimento: Optional[float] = None  # -1.0 a +1.0
    relevancia_trading: Optional[float] = None  # 0.0 a 1.0
    palavras_chave: Optional[List[str]] = None
    impacto_estimado: Optional[str] = None  # 'alto', 'medio', 'baixo'


class ColetorNoticias:
    """Coleta notícias de múltiplas fontes automaticamente."""

    # RSS Feeds de fontes brasileiras
    FEEDS_RSS = {
        'infomoney': {
            'mercados': 'https://www.infomoney.com.br/feed/',
            'economia': 'https://www.infomoney.com.br/economia/feed/',
        },
        'valor': {
            'financas': 'https://valor.globo.com/rss/financas',
            'empresas': 'https://valor.globo.com/rss/empresas',
        },
        'estadao': {
            'economia': 'https://economia.estadao.com.br/rss/ultimas.xml',
        },
        'g1': {
            'economia': 'https://g1.globo.com/economia/index.xml',
        }
    }

    # Palavras-chave relevantes para filtrar notícias
    PALAVRAS_CHAVE_RELEVANTES = [
        # Mercado
        'bovespa', 'ibovespa', 'b3', 'bolsa', 'índice', 'ibov',
        'dólar', 'câmbio', 'juros', 'selic', 'copom', 'bacen', 'bc',
        # Indicadores
        'pib', 'inflação', 'ipca', 'igpm', 'desemprego',
        # Internacional
        'fed', 'federal reserve', 's&p', 'dow jones', 'nasdaq',
        # Commodities
        'petróleo', 'petrobrás', 'vale', 'minério',
        # Eventos
        'crise', 'recessão', 'alta', 'queda', 'recorde',
        'balanço', 'resultado', 'lucro', 'prejuízo'
    ] + [
        # English market terms (para fontes como Finviz)
        'stocks', 'stock', 'equities', 'index', 'indices', 'futures', 'future',
        'sp500', 's&p', 'dow', 'nasdaq', 'fed', 'fomc', 'rate', 'rates',
        'hike', 'cut', 'gdp', 'inflation', 'cpi', 'ppi', 'jobs', 'payrolls',
        'treasury', 'yields', 'bond', 'bonds',
        # Crypto
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'binance'
    ]

    def __init__(self):
        """Inicializa o coletor."""
        self._criar_tabelas()
        DIRETORIO_BASE.mkdir(parents=True, exist_ok=True)

    def _criar_tabelas(self):
        """Cria tabelas necessárias no banco."""
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        # Tabela principal de notícias
        cur.execute("""
            CREATE TABLE IF NOT EXISTS noticias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                conteudo TEXT,
                fonte TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                data_publicacao TIMESTAMP NOT NULL,
                categoria TEXT,

                -- Análise de sentimento
                sentimento TEXT,
                score_sentimento REAL,
                relevancia_trading REAL,
                impacto_estimado TEXT,

                -- Metadados
                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processada BOOLEAN DEFAULT 0
            )
        """)

        # Criar índices separadamente
        cur.execute("CREATE INDEX IF NOT EXISTS idx_noticias_data_pub ON noticias(data_publicacao)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_noticias_fonte ON noticias(fonte)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_noticias_sentimento ON noticias(sentimento)")

        # Tabela de palavras-chave por notícia
        cur.execute("""
            CREATE TABLE IF NOT EXISTS noticias_palavras_chave (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_noticia INTEGER NOT NULL,
                palavra_chave TEXT NOT NULL,

                FOREIGN KEY (id_noticia) REFERENCES noticias(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_palavras_chave ON noticias_palavras_chave(palavra_chave)")

        # Tabela de correlação notícias x movimentos de mercado
        cur.execute("""
            CREATE TABLE IF NOT EXISTS noticias_impacto_mercado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_noticia INTEGER NOT NULL,
                data_pregao DATE NOT NULL,
                simbolo TEXT NOT NULL,

                -- Movimento do mercado após a notícia
                variacao_1h REAL,
                variacao_1d REAL,
                variacao_3d REAL,

                -- Validação do impacto
                impacto_real TEXT,

                FOREIGN KEY (id_noticia) REFERENCES noticias(id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_impacto_data ON noticias_impacto_mercado(data_pregao)")

        conn.commit()
        conn.close()
        print(f"✅ Tabelas de notícias criadas/verificadas em: {CAMINHO_DB}")

    def coletar_rss(self, limite_horas: int = 24) -> List[Noticia]:
        """
        Coleta notícias de feeds RSS.

        Args:
            limite_horas: Coletar notícias das últimas N horas

        Returns:
            Lista de notícias coletadas
        """
        noticias = []
        data_limite = datetime.now() - timedelta(hours=limite_horas)

        print(f"\n{'='*80}")
        print(f"COLETANDO NOTICIAS VIA RSS (ultimas {limite_horas}h)")
        print(f"{'='*80}\n")

        for fonte, feeds in self.FEEDS_RSS.items():
            print(f"\n📰 Fonte: {fonte.upper()}")

            for categoria, url in feeds.items():
                try:
                    print(f"  Categoria: {categoria}... ", end='')

                    feed = feedparser.parse(url)

                    if not feed.entries:
                        print("sem entradas")
                        continue

                    novas = 0
                    for entry in feed.entries:
                        # Parsear data de publicação
                        if hasattr(entry, 'published_parsed'):
                            data_pub = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed'):
                            data_pub = datetime(*entry.updated_parsed[:6])
                        else:
                            data_pub = datetime.now()

                        # Filtrar por data
                        if data_pub < data_limite:
                            continue

                        # Extrair conteúdo
                        conteudo = ''
                        if hasattr(entry, 'summary'):
                            conteudo = entry.summary
                        elif hasattr(entry, 'description'):
                            conteudo = entry.description

                        # Limpar HTML
                        conteudo = re.sub(r'<[^>]+>', '', conteudo)

                        # Verificar relevância
                        texto_completo = f"{entry.title} {conteudo}".lower()
                        if not self._e_relevante(texto_completo):
                            continue

                        noticia = Noticia(
                            titulo=entry.title,
                            conteudo=conteudo,
                            fonte=fonte,
                            url=entry.link,
                            data_publicacao=data_pub,
                            categoria=categoria
                        )

                        noticias.append(noticia)
                        novas += 1

                    print(f"{novas} relevantes")
                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    print(f"erro: {str(e)[:50]}")

        print(f"\n✅ Total coletado: {len(noticias)} notícias relevantes")
        return noticias

    def _e_relevante(self, texto: str) -> bool:
        """
        Verifica se o texto contém palavras-chave relevantes.

        Args:
            texto: Texto a verificar (título + conteúdo)

        Returns:
            True se relevante para trading
        """
        texto_lower = texto.lower()

        for palavra in self.PALAVRAS_CHAVE_RELEVANTES:
            if palavra in texto_lower:
                return True

        return False

    def salvar_noticias(self, noticias: List[Noticia]) -> int:
        """
        Salva notícias no banco de dados.

        Args:
            noticias: Lista de notícias a salvar

        Returns:
            Número de notícias novas salvas
        """
        if not noticias:
            return 0

        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        salvos = 0
        duplicados = 0

        for noticia in noticias:
            try:
                cur.execute("""
                    INSERT INTO noticias (
                        titulo, conteudo, fonte, url, data_publicacao, categoria,
                        sentimento, score_sentimento, relevancia_trading, impacto_estimado
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    noticia.titulo,
                    noticia.conteudo,
                    noticia.fonte,
                    noticia.url,
                    noticia.data_publicacao.isoformat(),
                    noticia.categoria,
                    noticia.sentimento,
                    noticia.score_sentimento,
                    noticia.relevancia_trading,
                    noticia.impacto_estimado
                ))

                salvos += 1

            except sqlite3.IntegrityError:
                # URL já existe (duplicado)
                duplicados += 1

        conn.commit()
        conn.close()

        print(f"\n💾 Salvamento:")
        print(f"   Novas: {salvos}")
        print(f"   Duplicadas: {duplicados}")

        return salvos

    # ------------------
    # Coleta via Scraping
    # ------------------
    def _criar_noticia(self, titulo: str, conteudo: str, url: str, fonte_padrao: str,
                        categoria: str, data_pub: Optional[datetime] = None) -> Optional[Noticia]:
        """Helper para criar notícia aplicando filtro de relevância."""
        texto = f"{titulo} {conteudo}"
        if not self._e_relevante(texto.lower()):
            return None
        if not data_pub:
            data_pub = datetime.now()
        fonte = fonte_padrao or urlparse(url).netloc
        return Noticia(
            titulo=titulo.strip(),
            conteudo=conteudo.strip(),
            fonte=fonte,
            url=url,
            data_publicacao=data_pub,
            categoria=categoria
        )

    def coletar_finviz(self, limite_horas: int = 24) -> List[Noticia]:
        """Coleta notícias do Finviz (https://finviz.com/news.ashx)."""
        url = "https://finviz.com/news.ashx"
        noticias: List[Noticia] = []
        data_limite = datetime.now() - timedelta(hours=limite_horas)
        try:
            print("\n🗞️ Finviz: coletando...")
            resp = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            })
            if resp.status_code != 200:
                print(f"  erro HTTP {resp.status_code}")
                return noticias
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Finviz costuma ter uma tabela com datas/horas e títulos
            # Estratégia: procurar linhas/links e tentar capturar data próxima
            for bloco in soup.select('table, div, li'):  # varrer estruturas comuns
                texto_bloco = bloco.get_text(" ", strip=True)
                # Encontrar timestamps tipo 'Nov-05-25 08:30AM' ou '08:30AM'
                m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-\s]?\d{2}[-\s]?\d{2}\s+\d{1,2}:\d{2}\s*(AM|PM)', texto_bloco)
                ts = None
                if m:
                    ts_str = m.group(0)
                    try:
                        ts = datetime.strptime(ts_str, '%b-%d-%y %I:%M %p')
                    except Exception:
                        ts = None
                for a in bloco.find_all('a', href=True):
                    titulo = a.get_text(strip=True)
                    href = a['href']
                    if not href.startswith('http'):
                        continue
                    if not titulo:
                        continue
                    data_pub = ts or datetime.now()
                    if data_pub < data_limite:
                        continue
                    noticia = self._criar_noticia(titulo, '', href, 'finviz', 'finviz', data_pub)
                    if noticia:
                        noticias.append(noticia)
            print(f"  coletadas {len(noticias)} (pré-filtro duplicatas)")
        except Exception as e:
            print(f"  erro: {e}")
        return noticias

    def coletar_moneytimes(self, limite_horas: int = 24) -> List[Noticia]:
        url = "https://www.moneytimes.com.br/ultimas-noticias/"
        noticias: List[Noticia] = []
        data_limite = datetime.now() - timedelta(hours=limite_horas)
        try:
            print("\n🗞️ MoneyTimes: coletando...")
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                print(f"  erro HTTP {resp.status_code}")
                return noticias
            soup = BeautifulSoup(resp.text, 'html.parser')
            artigos = soup.select('article, .article, .post, .mt-post')
            for art in artigos:
                a = art.find('a', href=True)
                if not a:
                    continue
                titulo = a.get_text(strip=True)
                href = a['href']
                # Tentar extrair data
                data_pub = datetime.now()
                time_tag = art.find('time')
                if time_tag and time_tag.has_attr('datetime'):
                    try:
                        data_pub = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
                    except Exception:
                        pass
                if data_pub < data_limite:
                    continue
                noticia = self._criar_noticia(titulo, '', href, 'moneytimes', 'moneytimes', data_pub)
                if noticia:
                    noticias.append(noticia)
            print(f"  coletadas {len(noticias)}")
        except Exception as e:
            print(f"  erro: {e}")
        return noticias

    def coletar_b3_noticias(self, limite_horas: int = 24) -> List[Noticia]:
        url = "https://www.b3.com.br/pt_br/noticias/"
        noticias: List[Noticia] = []
        data_limite = datetime.now() - timedelta(hours=limite_horas)
        try:
            print("\n🗞️ B3 Notícias: coletando...")
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                print(f"  erro HTTP {resp.status_code}")
                return noticias
            soup = BeautifulSoup(resp.text, 'html.parser')
            cards = soup.select('article, .card, .noticia, .news-item')
            for c in cards:
                a = c.find('a', href=True)
                if not a:
                    continue
                titulo = a.get_text(strip=True)
                href = a['href']
                if href.startswith('/'):
                    href = f"https://www.b3.com.br{href}"
                data_pub = datetime.now()
                if data_pub < data_limite:
                    continue
                noticia = self._criar_noticia(titulo, '', href, 'b3', 'b3_noticias', data_pub)
                if noticia:
                    noticias.append(noticia)
            print(f"  coletadas {len(noticias)}")
        except Exception as e:
            print(f"  erro: {e}")
        return noticias

    def coletar_plantao_b3(self, limite_horas: int = 24, agencia: int = 18) -> List[Noticia]:
        base = "https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/Index"
        params = {"agencia": str(agencia)}
        noticias: List[Noticia] = []
        data_limite = datetime.now() - timedelta(hours=limite_horas)
        try:
            print("\n🗞️ Plantão B3 (ag. 18): coletando...")
            resp = requests.get(base, params=params, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                print(f"  erro HTTP {resp.status_code}")
                return noticias
            soup = BeautifulSoup(resp.text, 'html.parser')
            itens = soup.select('li, .noticia, .news-item, .list-group-item')
            for it in itens:
                a = it.find('a', href=True)
                if not a:
                    continue
                titulo = a.get_text(strip=True)
                href = a['href']
                if href.startswith('/'):
                    href = f"https://sistemasweb.b3.com.br{href}"
                # Tentar achar data
                data_pub = datetime.now()
                texto = it.get_text(" ", strip=True)
                m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
                if m:
                    try:
                        data_pub = datetime.strptime(m.group(1), '%d/%m/%Y')
                    except Exception:
                        pass
                if data_pub < data_limite:
                    continue
                noticia = self._criar_noticia(titulo, '', href, 'plantao_b3', 'plantao_b3', data_pub)
                if noticia:
                    noticias.append(noticia)
            print(f"  coletadas {len(noticias)}")
        except Exception as e:
            print(f"  erro: {e}")
        return noticias

    def coletar_binance_square(self, limite_horas: int = 24) -> List[Noticia]:
        url = "https://www.binance.com/pt-BR/square/news/all"
        noticias: List[Noticia] = []
        data_limite = datetime.now() - timedelta(hours=limite_horas)
        try:
            print("\n🗞️ Binance Square: coletando...")
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                print(f"  erro HTTP {resp.status_code}")
                return noticias
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Conteúdo pode ser dinâmico; tentar capturar links iniciais
            for a in soup.find_all('a', href=True):
                href = a['href']
                titulo = a.get_text(strip=True)
                if not href or not titulo:
                    continue
                if href.startswith('/'):
                    href = f"https://www.binance.com{href}"
                data_pub = datetime.now()
                if data_pub < data_limite:
                    continue
                noticia = self._criar_noticia(titulo, '', href, 'binance', 'binance_square', data_pub)
                if noticia:
                    noticias.append(noticia)
            print(f"  coletadas {len(noticias)} (possível conteúdo dinâmico – resultados parciais)")
        except Exception as e:
            print(f"  erro: {e}")
        return noticias

    def coletar_novadax(self, limite_horas: int = 24) -> List[Noticia]:
        url = "https://www.novadax.com.br/suporte/An%C3%BAncios/detail/22-Noti%CC%81cias"
        noticias: List[Noticia] = []
        data_limite = datetime.now() - timedelta(hours=limite_horas)
        try:
            print("\n🗞️ NovaDAX: coletando...")
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                print(f"  erro HTTP {resp.status_code}")
                return noticias
            soup = BeautifulSoup(resp.text, 'html.parser')
            itens = soup.select('a[href], .article, .post, li')
            for it in itens:
                a = it if it.name == 'a' else it.find('a', href=True)
                if not a:
                    continue
                href = a.get('href')
                titulo = a.get_text(strip=True)
                if not href or not titulo:
                    continue
                if href.startswith('/'):
                    href = f"https://www.novadax.com.br{href}"
                data_pub = datetime.now()
                if data_pub < data_limite:
                    continue
                noticia = self._criar_noticia(titulo, '', href, 'novadax', 'novadax', data_pub)
                if noticia:
                    noticias.append(noticia)
            print(f"  coletadas {len(noticias)}")
        except Exception as e:
            print(f"  erro: {e}")
        return noticias

    def coletar_newsapi(self, api_key: Optional[str] = None, limite_resultados: int = 50) -> List[Noticia]:
        """
        Coleta notícias via NewsAPI (requer API key).

        Args:
            api_key: Chave de API do NewsAPI (https://newsapi.org)
            limite_resultados: Número máximo de resultados

        Returns:
            Lista de notícias coletadas
        """
        if not api_key:
            print("⚠️  NewsAPI requer API key. Obtenha em: https://newsapi.org")
            return []

        noticias = []

        # Buscar notícias sobre mercado brasileiro
        queries = [
            'Bovespa OR Ibovespa OR B3',
            'Dólar Brasil',
            'Economia Brasil',
            'Juros Selic'
        ]

        print(f"\n{'='*80}")
        print(f"COLETANDO NOTICIAS VIA NEWSAPI")
        print(f"{'='*80}\n")

        for query in queries:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'language': 'pt',
                    'sortBy': 'publishedAt',
                    'pageSize': limite_resultados // len(queries),
                    'apiKey': api_key
                }

                print(f"📡 Query: {query}... ", end='')

                response = requests.get(url, params=params, timeout=10)

                if response.status_code != 200:
                    print(f"erro {response.status_code}")
                    continue

                data = response.json()
                artigos = data.get('articles', [])

                print(f"{len(artigos)} artigos")

                for artigo in artigos:
                    data_pub = datetime.fromisoformat(artigo['publishedAt'].replace('Z', '+00:00'))

                    noticia = Noticia(
                        titulo=artigo['title'],
                        conteudo=artigo.get('description', ''),
                        fonte=artigo['source']['name'],
                        url=artigo['url'],
                        data_publicacao=data_pub,
                        categoria='newsapi'
                    )

                    noticias.append(noticia)

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"erro: {str(e)[:50]}")

        print(f"\n✅ Total coletado: {len(noticias)} notícias via NewsAPI")
        return noticias

    def obter_noticias_recentes(self, horas: int = 24, limite: int = 50) -> List[Dict]:
        """
        Obtém notícias recentes do banco.

        Args:
            horas: Notícias das últimas N horas
            limite: Número máximo de resultados

        Returns:
            Lista de dicionários com dados das notícias
        """
        conn = sqlite3.connect(CAMINHO_DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        data_limite = datetime.now() - timedelta(hours=horas)

        cur.execute("""
            SELECT * FROM noticias
            WHERE data_publicacao >= ?
            ORDER BY data_publicacao DESC
            LIMIT ?
        """, (data_limite.isoformat(), limite))

        noticias = [dict(row) for row in cur.fetchall()]
        conn.close()

        return noticias

    def executar_coleta_automatica(self, newsapi_key: Optional[str] = None):
        """
        Executa coleta automática de todas as fontes configuradas.

        Args:
            newsapi_key: Chave de API do NewsAPI (opcional)
        """
        print(f"\n{'='*100}")
        print(f"COLETA AUTOMATICA DE NOTICIAS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*100}")

        # Coletar de RSS (sempre disponível)
        noticias_rss = self.coletar_rss(limite_horas=24)
        salvos_rss = self.salvar_noticias(noticias_rss)

        # Coletar de NewsAPI (se tiver chave)
        salvos_api = 0
        if newsapi_key:
            noticias_api = self.coletar_newsapi(newsapi_key, limite_resultados=50)
            salvos_api = self.salvar_noticias(noticias_api)

        # Coletar via scraping (novas fontes)
        fontes_scraping = [
            ("finviz", self.coletar_finviz),
            ("moneytimes", self.coletar_moneytimes),
            ("b3_noticias", self.coletar_b3_noticias),
            ("plantao_b3", self.coletar_plantao_b3),
            ("binance_square", self.coletar_binance_square),
            ("novadax", self.coletar_novadax),
        ]
        salvos_scraping = 0
        for nome, func in fontes_scraping:
            try:
                noticias_src = func(limite_horas=24)
                salvos_src = self.salvar_noticias(noticias_src)
                salvos_scraping += salvos_src
            except Exception as e:
                print(f"⚠️  Erro na fonte {nome}: {e}")

        total_salvos = salvos_rss + salvos_api + salvos_scraping

        print(f"\n{'='*100}")
        print(f"RESUMO DA COLETA")
        print(f"{'='*100}")
        print(f"   Noticias novas salvas: {total_salvos}")
        print(f"   Total no banco (ultimas 24h): {len(self.obter_noticias_recentes(24))}")
        print(f"{'='*100}\n")


def exemplo_uso():
    """Exemplo de uso do coletor."""

    coletor = ColetorNoticias()

    # Executar coleta automática
    # NOTA: Para usar NewsAPI, obtenha chave grátis em: https://newsapi.org
    coletor.executar_coleta_automatica(newsapi_key=None)

    # Visualizar notícias coletadas
    noticias = coletor.obter_noticias_recentes(horas=24, limite=10)

    print(f"\n{'='*100}")
    print("NOTICIAS RECENTES (ultimas 10)")
    print(f"{'='*100}\n")

    for i, noticia in enumerate(noticias, 1):
        print(f"{i}. {noticia['titulo']}")
        print(f"   Fonte: {noticia['fonte']} | {noticia['data_publicacao']}")
        print(f"   URL: {noticia['url'][:80]}...")
        print()


if __name__ == "__main__":
    exemplo_uso()
