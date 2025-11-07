# -*- coding: utf-8 -*-
"""
Analisador de Sentimento de Notícias Financeiras.

Analisa o sentimento de notícias coletadas para identificar:
- Sentimento geral (positivo/negativo/neutro)
- Score numérico de -1.0 (muito negativo) a +1.0 (muito positivo)
- Relevância para trading (0.0 a 1.0)
- Impacto estimado no mercado (alto/médio/baixo)
- Palavras-chave e entidades mencionadas

Métodos implementados:
1. Léxico (dicionário de palavras financeiras)
2. Padrões de regex para detectar movimentos
3. Análise de magnitude (números e percentuais)
"""

import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


CAMINHO_DB = Path(__file__).parent.parent.parent / "data" / "recomendacoes.sqlite"


class AnalisadorSentimento:
    """Analisa sentimento de notícias financeiras."""

    # Dicionário de palavras com sentimento
    PALAVRAS_POSITIVAS = [
        'alta', 'subiu', 'subir', 'sobe', 'sobem', 'ganho', 'ganhos',
        'lucro', 'lucros', 'valorização', 'valoriza', 'valorizam',
        'crescimento', 'cresce', 'cresceu', 'expansão', 'expande',
        'otimista', 'otimismo', 'confiança', 'confiante',
        'recuperação', 'recupera', 'recuperou', 'melhora', 'melhorou',
        'recorde', 'histórico', 'máxima', 'máximo',
        'forte', 'robusto', 'sólido', 'positivo', 'positiva',
        'avanço', 'avança', 'avançou', 'elevação', 'eleva',
        'supera', 'superou', 'bate', 'bateu', 'ultrapassa', 'ultrapassou'
    ]

    PALAVRAS_NEGATIVAS = [
        'queda', 'caiu', 'cair', 'cai', 'caem', 'perda', 'perdas',
        'prejuízo', 'prejuízos', 'desvalorização', 'desvaloriza',
        'retração', 'retrai', 'retraiu', 'contração', 'contrai',
        'pessimista', 'pessimismo', 'desconfiança', 'preocupação',
        'crise', 'recessão', 'depressão', 'colapso',
        'mínima', 'mínimo', 'histórico' + ' baixo', 'pior',
        'fraco', 'fraca', 'negativo', 'negativa',
        'recuo', 'recua', 'recuou', 'queda', 'declínio',
        'frustra', 'frustrou', 'decepciona', 'decepcionou',
        'tombo', 'despenca', 'despencou', 'derrete', 'derreteu'
    ]

    PALAVRAS_INCERTEZA = [
        'incerteza', 'incerto', 'dúvida', 'dúvidas', 'hesitação',
        'volatilidade', 'volátil', 'instabilidade', 'instável',
        'risco', 'riscos', 'ameaça', 'ameaças', 'temor', 'medo'
    ]

    # Padrões de movimento de mercado
    PADROES_MOVIMENTO = {
        r'(?:sobe|subiu|alta de?)\s+(\d+(?:,\d+)?)\s*%': 'positivo',
        r'(?:cai|caiu|queda de?)\s+(\d+(?:,\d+)?)\s*%': 'negativo',
        r'(?:avança|avançou)\s+(\d+(?:,\d+)?)\s*%': 'positivo',
        r'(?:recua|recuou)\s+(\d+(?:,\d+)?)\s*%': 'negativo',
    }

    # Entidades relevantes (empresas, índices, indicadores)
    ENTIDADES_MERCADO = [
        'ibovespa', 'bovespa', 'b3', 'ibov',
        'dólar', 'real', 'câmbio',
        'petrobras', 'vale', 'itaú', 'bradesco', 'banco do brasil',
        'pib', 'inflação', 'ipca', 'igpm', 'selic', 'copom',
        'fed', 'federal reserve', 'banco central', 'bacen',
        's&p', 's&p 500', 'dow jones', 'nasdaq'
    ]

    def analisar_noticia(self, titulo: str, conteudo: str) -> Dict:
        """
        Analisa sentimento de uma notícia.

        Args:
            titulo: Título da notícia
            conteudo: Conteúdo/resumo da notícia

        Returns:
            Dicionário com análise completa
        """
        texto_completo = f"{titulo} {conteudo}".lower()

        # 1. Análise léxica (contagem de palavras)
        score_lexico = self._analisar_lexico(texto_completo)

        # 2. Análise de padrões (movimentos específicos)
        score_padroes, magnitude = self._analisar_padroes(texto_completo)

        # 3. Análise de incerteza
        score_incerteza = self._analisar_incerteza(texto_completo)

        # 4. Combinar scores
        score_final = (score_lexico * 0.5) + (score_padroes * 0.3) + (score_incerteza * 0.2)
        score_final = max(-1.0, min(1.0, score_final))  # Limitar entre -1 e +1

        # 5. Classificar sentimento
        if score_final > 0.2:
            sentimento = 'positivo'
        elif score_final < -0.2:
            sentimento = 'negativo'
        else:
            sentimento = 'neutro'

        # 6. Calcular relevância para trading
        relevancia = self._calcular_relevancia(texto_completo, magnitude)

        # 7. Estimar impacto
        if relevancia > 0.7 and abs(score_final) > 0.5:
            impacto = 'alto'
        elif relevancia > 0.4 and abs(score_final) > 0.3:
            impacto = 'medio'
        else:
            impacto = 'baixo'

        # 8. Extrair palavras-chave
        palavras_chave = self._extrair_palavras_chave(texto_completo)

        return {
            'sentimento': sentimento,
            'score_sentimento': round(score_final, 3),
            'relevancia_trading': round(relevancia, 3),
            'impacto_estimado': impacto,
            'palavras_chave': palavras_chave,
            'magnitude_movimento': magnitude,
            'detalhes': {
                'score_lexico': round(score_lexico, 3),
                'score_padroes': round(score_padroes, 3),
                'score_incerteza': round(score_incerteza, 3)
            }
        }

    def _analisar_lexico(self, texto: str) -> float:
        """Analisa texto usando léxico de palavras."""
        count_positivas = sum(1 for palavra in self.PALAVRAS_POSITIVAS if palavra in texto)
        count_negativas = sum(1 for palavra in self.PALAVRAS_NEGATIVAS if palavra in texto)

        total = count_positivas + count_negativas
        if total == 0:
            return 0.0

        # Score normalizado
        score = (count_positivas - count_negativas) / total
        return score

    def _analisar_padroes(self, texto: str) -> Tuple[float, float]:
        """
        Analisa padrões de movimento explícitos.

        Returns:
            (score, magnitude): Score de sentimento e magnitude do movimento
        """
        score = 0.0
        magnitude_maxima = 0.0

        for padrao, sentimento_tipo in self.PADROES_MOVIMENTO.items():
            matches = re.findall(padrao, texto)

            for match in matches:
                # Extrair percentual
                percentual = float(match.replace(',', '.'))
                magnitude_maxima = max(magnitude_maxima, percentual)

                # Ajustar score baseado em magnitude
                peso = min(percentual / 5.0, 1.0)  # Normalizar (5% = peso 1.0)

                if sentimento_tipo == 'positivo':
                    score += peso
                else:
                    score -= peso

        # Normalizar score
        if score != 0:
            score = score / max(abs(score), 1.0)

        return score, magnitude_maxima

    def _analisar_incerteza(self, texto: str) -> float:
        """Analisa nível de incerteza (reduz confiança do sentimento)."""
        count_incerteza = sum(1 for palavra in self.PALAVRAS_INCERTEZA if palavra in texto)

        # Incerteza reduz magnitude do sentimento
        fator_reducao = min(count_incerteza * 0.1, 0.5)  # Máximo 50% de redução

        return -fator_reducao

    def _calcular_relevancia(self, texto: str, magnitude: float) -> float:
        """Calcula relevância da notícia para trading."""
        relevancia = 0.0

        # 1. Menciona entidades importantes?
        count_entidades = sum(1 for entidade in self.ENTIDADES_MERCADO if entidade in texto)
        relevancia += min(count_entidades * 0.15, 0.5)

        # 2. Contém números/percentuais?
        if re.search(r'\d+(?:,\d+)?\s*%', texto):
            relevancia += 0.2

        # 3. Magnitude do movimento
        if magnitude > 0:
            relevancia += min(magnitude / 10.0, 0.3)  # Até 30% pela magnitude

        return min(relevancia, 1.0)

    def _extrair_palavras_chave(self, texto: str) -> List[str]:
        """Extrai palavras-chave relevantes."""
        palavras = []

        # Entidades mencionadas
        for entidade in self.ENTIDADES_MERCADO:
            if entidade in texto:
                palavras.append(entidade)

        # Palavras de sentimento encontradas
        for palavra in self.PALAVRAS_POSITIVAS[:10]:  # Top 10
            if palavra in texto:
                palavras.append(f"+{palavra}")

        for palavra in self.PALAVRAS_NEGATIVAS[:10]:  # Top 10
            if palavra in texto:
                palavras.append(f"-{palavra}")

        return palavras[:10]  # Máximo 10 palavras-chave

    def processar_noticias_pendentes(self, limite: int = 100) -> int:
        """
        Processa notícias que ainda não foram analisadas.

        Args:
            limite: Número máximo de notícias a processar

        Returns:
            Número de notícias processadas
        """
        conn = sqlite3.connect(CAMINHO_DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Buscar notícias não processadas
        cur.execute("""
            SELECT id, titulo, conteudo
            FROM noticias
            WHERE processada = 0
            ORDER BY data_publicacao DESC
            LIMIT ?
        """, (limite,))

        noticias = cur.fetchall()

        if not noticias:
            print("✅ Nenhuma notícia pendente para processar")
            return 0

        print(f"\n{'='*80}")
        print(f"PROCESSANDO {len(noticias)} NOTICIAS")
        print(f"{'='*80}\n")

        processadas = 0

        for noticia in noticias:
            try:
                # Analisar sentimento
                analise = self.analisar_noticia(
                    noticia['titulo'],
                    noticia['conteudo'] or ''
                )

                # Atualizar banco
                cur.execute("""
                    UPDATE noticias
                    SET sentimento = ?,
                        score_sentimento = ?,
                        relevancia_trading = ?,
                        impacto_estimado = ?,
                        processada = 1
                    WHERE id = ?
                """, (
                    analise['sentimento'],
                    analise['score_sentimento'],
                    analise['relevancia_trading'],
                    analise['impacto_estimado'],
                    noticia['id']
                ))

                # Salvar palavras-chave
                for palavra in analise['palavras_chave']:
                    cur.execute("""
                        INSERT INTO noticias_palavras_chave (id_noticia, palavra_chave)
                        VALUES (?, ?)
                    """, (noticia['id'], palavra))

                processadas += 1

                if processadas % 10 == 0:
                    print(f"  Processadas: {processadas}/{len(noticias)}")

            except Exception as e:
                print(f"⚠️  Erro ao processar notícia {noticia['id']}: {e}")

        conn.commit()
        conn.close()

        print(f"\n✅ Processadas: {processadas} notícias")
        return processadas

    def obter_sentimento_periodo(self, data_inicio: datetime, data_fim: datetime) -> Dict:
        """
        Calcula sentimento agregado de um período.

        Args:
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            Estatísticas de sentimento do período
        """
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT
                COUNT(*) as total,
                AVG(score_sentimento) as sentimento_medio,
                SUM(CASE WHEN sentimento = 'positivo' THEN 1 ELSE 0 END) as positivas,
                SUM(CASE WHEN sentimento = 'negativo' THEN 1 ELSE 0 END) as negativas,
                SUM(CASE WHEN sentimento = 'neutro' THEN 1 ELSE 0 END) as neutras,
                AVG(relevancia_trading) as relevancia_media
            FROM noticias
            WHERE data_publicacao BETWEEN ? AND ?
                AND processada = 1
        """, (data_inicio.isoformat(), data_fim.isoformat()))

        resultado = cur.fetchone()
        conn.close()

        if not resultado or resultado[0] == 0:
            return {
                'total': 0,
                'sentimento_medio': 0.0,
                'distribuicao': {'positivas': 0, 'negativas': 0, 'neutras': 0},
                'relevancia_media': 0.0
            }

        return {
            'total': resultado[0],
            'sentimento_medio': round(resultado[1] or 0.0, 3),
            'distribuicao': {
                'positivas': resultado[2],
                'negativas': resultado[3],
                'neutras': resultado[4]
            },
            'relevancia_media': round(resultado[5] or 0.0, 3)
        }


def exemplo_uso():
    """Exemplo de uso do analisador."""

    analisador = AnalisadorSentimento()

    # Exemplos de notícias para teste
    noticias_teste = [
        {
            'titulo': 'Ibovespa sobe 2,5% e fecha acima de 130 mil pontos',
            'conteudo': 'O índice Bovespa avançou forte nesta sessão, impulsionado pela alta de commodities e resultado positivo da Petrobras.'
        },
        {
            'titulo': 'Dólar dispara e fecha em alta de 3,2% após decisão do Fed',
            'conteudo': 'A moeda americana teve forte valorização com a decisão de manter juros altos, gerando preocupação no mercado brasileiro.'
        },
        {
            'titulo': 'B3 registra volume de negociação estável no mês',
            'conteudo': 'A bolsa brasileira manteve volume médio de R$ 25 bilhões em negociações diárias, sem grandes oscilações.'
        }
    ]

    print(f"\n{'='*80}")
    print("ANALISE DE SENTIMENTO - EXEMPLOS")
    print(f"{'='*80}\n")

    for i, noticia in enumerate(noticias_teste, 1):
        print(f"\n{i}. {noticia['titulo']}")
        print(f"   {noticia['conteudo']}\n")

        analise = analisador.analisar_noticia(noticia['titulo'], noticia['conteudo'])

        print(f"   Sentimento: {analise['sentimento'].upper()}")
        print(f"   Score: {analise['score_sentimento']}")
        print(f"   Relevância: {analise['relevancia_trading']}")
        print(f"   Impacto: {analise['impacto_estimado']}")
        print(f"   Palavras-chave: {', '.join(analise['palavras_chave'][:5])}")
        print(f"   {'-'*70}")

    # Processar notícias pendentes no banco
    print(f"\n{'='*80}")
    print("PROCESSANDO NOTICIAS DO BANCO")
    print(f"{'='*80}\n")

    processadas = analisador.processar_noticias_pendentes(limite=50)

    if processadas > 0:
        # Mostrar estatísticas recentes
        from datetime import timedelta
        agora = datetime.now()
        ontem = agora - timedelta(days=1)

        stats = analisador.obter_sentimento_periodo(ontem, agora)

        print(f"\n{'='*80}")
        print("SENTIMENTO DAS ULTIMAS 24 HORAS")
        print(f"{'='*80}")
        print(f"   Total de notícias: {stats['total']}")
        print(f"   Sentimento médio: {stats['sentimento_medio']}")
        print(f"   Distribuição:")
        print(f"      Positivas: {stats['distribuicao']['positivas']}")
        print(f"      Negativas: {stats['distribuicao']['negativas']}")
        print(f"      Neutras: {stats['distribuicao']['neutras']}")
        print(f"   Relevância média: {stats['relevancia_media']}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    exemplo_uso()
