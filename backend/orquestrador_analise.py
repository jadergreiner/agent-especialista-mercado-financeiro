"""
Orquestrador de Análise — Sprint Prompt Interativo MVP

Coordena a análise de ativos financeiros usando LLM (OpenAI GPT-4o-mini)
para fornecer insights estruturados baseados em dados de mercado.

Funcionalidades:
- Análise interativa via prompt em linguagem natural
- Integração com ferramentas de dados (preço, indicadores, notícias)
- Templates de análise (Analista vs Trader Rápido)
- Saída estruturada (JSON + Markdown)
- Transparência Radical: gates de qualidade + downgrade de confiança
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional, Any

import openai
from dotenv import load_dotenv

from utils.logger_analise import obter_logger
from ferramentas.preco_atual import obter_preco_atual
from ferramentas.indicadores_tecnicos import calcular_sma_rsi
from ferramentas.noticias_resumidas import buscar_noticias_resumidas
from validadores.sistema_disclaimers import SistemaDisclaimers
from calibrador_confianca import CalibradorConfianca
from validador_consistencia import ValidadorConsistencia
from sistema_transparency_radical import obter_sistema_transparency_radical
from sistema_templates_analise import TemplatesAnalise

# Carregar variáveis de ambiente
load_dotenv()
logger = obter_logger(__name__)


class OrquestradorAnalise:
    """
    Orquestrador principal para análise de ativos via LLM.
    """

    def __init__(self):
        """Inicializa o orquestrador com configurações OpenAI."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.modelo = os.getenv('ANALISE_MODELO_LLM', 'gpt-4o-mini')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
        self.temperatura = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não configurada no arquivo .env")

        # Configurar cliente OpenAI
        self.cliente = openai.OpenAI(api_key=self.api_key)

        logger.info(f"Orquestrador inicializado: modelo={self.modelo}, max_tokens={self.max_tokens}")

    def analisar_ativo(
        self,
        ativo: str,
        modo: str = "analista",
        incluir_historico: bool = False
    ) -> Dict[str, Any]:
        """
        Analisa um ativo financeiro usando LLM.

        Args:
            ativo: Símbolo do ativo (ex: "EURUSD", "PETR4.SA")
            modo: "analista" (explicativo) ou "trader" (objetivo)
            incluir_historico: Incluir histórico de preços

        Returns:
            dict: Análise estruturada com dados e insights
        """
        logger.info(f"Iniciando análise de {ativo} no modo '{modo}'")

        try:
            # GATE 0: Obter sistema de transparência radical
            sistema_transparency = obter_sistema_transparency_radical()
            sistema_transparency.limpar_alertas()  # Reset alertas da requisição anterior

            # 1. Obter dados de preço atuais
            dados_preco = obter_preco_atual(ativo, incluir_historico)
            logger.info(f"Dados de preço obtidos para {ativo}")

            # 2. Obter indicadores técnicos
            try:
                dados_indicadores = calcular_sma_rsi(ativo)
                logger.info(f"Indicadores técnicos obtidos para {ativo}")
            except Exception as e:
                logger.warning(f"Erro ao obter indicadores para {ativo}: {e}. Continuando sem indicadores.")
                dados_indicadores = None

            # 3. Obter notícias resumidas
            try:
                dados_noticias = buscar_noticias_resumidas(ativo)
                logger.info(f"Notícias obtidas para {ativo}: {len(dados_noticias.get('noticias', []))} notícias")
            except Exception as e:
                logger.warning(f"Erro ao obter notícias para {ativo}: {e}. Continuando sem notícias.")
                dados_noticias = None

            # GATE 1: Validação de Qualidade (Radical Transparency)
            resultado_validacao = sistema_transparency.validar_qualidade_pre_analise(
                dados_preco, dados_indicadores, frescor_minutos=60
            )

            if not resultado_validacao["valido"]:
                logger.error(f"Validação de qualidade falhou para {ativo}")
                resposta_rejeicao = sistema_transparency.gerar_resposta_rejeicao_qualidade(resultado_validacao)
                return {
                    "ativo": ativo,
                    "sucesso": False,
                    "motivo_rejeicao": "qualidade_insuficiente",
                    "analise": resposta_rejeicao,
                    "metadata": {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "modo": modo,
                        "validacao": resultado_validacao,
                    },
                }

            # 4. Preparar contexto para LLM
            contexto = self._preparar_contexto_analise(dados_preco, dados_indicadores, dados_noticias, modo)

            # 5. Gerar análise via LLM (com fallback gracioso)
            try:
                analise_llm, dados_validacao = self._chamar_llm_analise(contexto, modo, dados_indicadores, dados_noticias)
            except Exception as e:
                logger.error(f"Erro ao chamar LLM para {ativo}: {e}")
                # Fallback gracioso
                analise_fallback = sistema_transparency.fallback_gracioso_api_falha(ativo, str(e))
                resposta_fallback = {
                    "ativo": ativo,
                    "preco_atual": dados_preco.get("preco"),
                    "variacao": dados_preco.get("variacao_pct"),
                    "dados_tecnicos_disponíveis": True,
                    "analise_llm_disponível": False,
                    "motivo_falha": str(e),
                    "analise": analise_fallback,
                }

                # Adicionar dados técnicos como fallback
                if dados_indicadores:
                    resposta_fallback["indicadores"] = dados_indicadores.get("indicadores", {})

                return resposta_fallback

            # 6. Estruturar resposta final
            resposta = self._estruturar_resposta_final(
                ativo, dados_preco, dados_indicadores, dados_noticias, analise_llm, modo, dados_validacao
            )

            logger.info(f"Análise concluída para {ativo}")
            return resposta

        except Exception as e:
            logger.error(f"Erro na análise de {ativo}: {e}")
            raise

    def _preparar_contexto_analise(self, dados_preco: Dict, dados_indicadores: Optional[Dict], dados_noticias: Optional[Dict], modo: str) -> str:
        """
        Prepara o contexto/prompt para o LLM baseado nos dados e modo.
        """
        ativo = dados_preco['ativo']
        preco = dados_preco['preco']
        variacao = dados_preco['variacao_pct']
        timestamp = dados_preco['timestamp']
        frescor = dados_preco.get('frescor', 'desconhecido')
        mercado_status = dados_preco.get('mercado_status', 'desconhecido')

        contexto_base = f"""
ATIVO: {ativo}
PREÇO ATUAL: {preco}
VARIAÇÃO: {variacao:+.2f}%
TIMESTAMP: {timestamp}
FRESCOR DADOS: {frescor}
STATUS MERCADO: {mercado_status}
"""

        # Adicionar indicadores técnicos se disponíveis
        if dados_indicadores:
            sma = dados_indicadores['indicadores']['sma']
            rsi = dados_indicadores['indicadores']['rsi']
            contexto_base += f"""
INDICADORES TÉCNICOS:
- SMA{20}: {sma['valor']:.4f} ({sma['sinal']}, diferença: {sma['diferenca_pct']:+.2f}%)
- RSI{14}: {rsi['valor']:.2f} ({rsi['sinal']} - {rsi['interpretacao']})
"""

        # Adicionar notícias se disponíveis
        if dados_noticias and dados_noticias.get('noticias'):
            contexto_base += f"""
NOTÍCIAS RECENTES ({len(dados_noticias['noticias'])} notícia(s)):
Sentimento geral: {dados_noticias['resumo_geral']['sentimento_geral']}
Impacto geral: {dados_noticias['resumo_geral']['impacto_geral']}
"""
            # Adicionar até 3 notícias mais relevantes
            for i, noticia in enumerate(dados_noticias['noticias'][:3]):
                contexto_base += f"""
{i+1}. {noticia['titulo']}
   Sentimento: {noticia['sentimento']} | Impacto: {noticia['impacto']}
   Resumo: {noticia['resumo']}
"""

        contexto_base += """

INSTRUÇÕES DE ANÁLISE:
- Forneça análise técnica e fundamental
- Considere correlações de mercado e indicadores técnicos quando disponíveis
- Avalie impacto de notícias quando disponíveis
- Seja objetivo e baseado em dados
"""

        # Templates diferenciados por modo com few-shots
        if modo == "analista":
            contexto_base += """
MODO ANALISTA (EXPLICATIVO - FOCO EM CONTEXTO E LONGO PRAZO):

OBJETIVO: Forneça análise profunda e contextualizada para tomada de decisão estratégica.

ESTRUTURA DA RESPOSTA:
1. CONTEXTO MACROECONÔMICO (2-3 parágrafos)
2. ANÁLISE FUNDAMENTAL (drivers econômicos, política monetária, dados)
3. ANÁLISE TÉCNICA (padrões, níveis chave, momentum)
4. AVALIAÇÃO DE RISCO (volatilidade, correlações, eventos externos)
5. PERSPECTIVAS E IMPLICAÇÕES (cenários possíveis, implicações de longo prazo)

EXEMPLO DE RESPOSTA:
"O par EUR/USD opera em um ambiente de crescente incerteza quanto à política monetária do BCE. Os dados de inflação da zona do euro, embora ainda elevados, mostram sinais de arrefecimento que podem permitir ao BCE uma pausa no ciclo de aperto monetário. Do lado americano, o payroll mostrou resiliência do mercado de trabalho, reforçando expectativas de manutenção de juros elevados por mais tempo.

Fundamentalmente, a divergência nas trajetórias de política monetária cria um ambiente desafiador para o euro. O BCE pode estar próximo do fim do ciclo de alta, enquanto o Fed sinaliza manutenção de postura restritiva. Esta assimetria favorece o dólar americano no médio prazo.

Tecnicamente, o preço abaixo da média móvel de 20 períodos confirma momentum baixista de curto prazo. Os níveis de suporte em 1.1500 e resistência em 1.1650 serão cruciais para definição da tendência intermediária.

Riscos incluem: aceleração inflacionária na zona do euro, dados de emprego americanos mais fortes que esperado, e eventos geopolíticos na Europa Oriental.

Perspectiva: O par deve permanecer volátil até próximos dados econômicos. Quebra consistente abaixo de 1.1500 abriria caminho para 1.1400, enquanto recuperação acima de 1.1650 sinalizaria reversão bullish."
"""
        elif modo == "trader":
            contexto_base += """
MODO TRADER (OBJETIVO - FOCO EM TIMING E EXECUÇÃO):

OBJETIVO: Forneça análise acionável focada em timing de entrada/saída e gestão de risco.

ESTRUTURA DA RESPOSTA:
1. SETUP ATUAL (preço, variação, mercado)
2. INDICADORES TÉCNICOS (sinais claros, níveis chave)
3. MOMENTUM E VOLATILIDADE (direção, força, risco)
4. CENÁRIOS (bull/bear com confiança e targets)
5. TIMING E GESTÃO (quando agir, stops, limites)

EXEMPLO DE RESPOSTA:
"SETUP ATUAL: EURUSD 1.1567 (+0.13%), mercado aberto.

INDICADORES TÉCNICOS: Preço abaixo SMA20 (bearish), RSI 45.1 neutro. Suporte 1.1500, resistência 1.1650, pivot 1.1575.

MOMENTUM: Baixista de curto prazo, volatilidade média (20 pips/dia). Sentimento notícias negativo impacta euro.

CENÁRIOS:
- BULL (45% confiança): Quebra acima 1.1650 → target 1.1750
- BEAR (55% confiança): Quebra abaixo 1.1500 → target 1.1400

TIMING: Aguardar confirmação de rompimento. Stop loss obrigatório em 1.1520 para longs, 1.1630 para shorts. Risco máximo 1% por trade."
"""
        else:
            raise ValueError(f"Modo '{modo}' não suportado. Use 'analista' ou 'trader'")

        return contexto_base

    def _chamar_llm_analise(self, contexto: str, modo: str, dados_indicadores: Optional[Dict] = None, dados_noticias: Optional[Dict] = None) -> tuple[str, Optional[Dict]]:
        """
        Chama o LLM para gerar a análise com templates por modo.

        US-PROMPT-003 INTEGRATION:
        - Usa sistema de templates com few-shots diferenciados por modo
        - Modo "analista": Análise profunda, explicativa, longo prazo
        - Modo "trader": Análise objetiva, acionável, timing de execução

        Retorna tupla: (analise_texto, dados_validacao)
        """
        # Validar modo
        if not TemplatesAnalise.validar_modo(modo):
            logger.warning(f"Modo '{modo}' inválido. Usando 'analista'.")
            modo = "analista"

        # Construir contexto com templates e few-shots
        contexto_com_template = TemplatesAnalise.construir_contexto_llm_com_template(
            contexto, modo, dados_validacao=None
        )

        # MOCK TEMPORÁRIO - Remover quando API key real for configurada
        if self.api_key == "sk-your-openai-api-key-here":
            logger.warning("Usando resposta mockada - configure OPENAI_API_KEY real no .env")
            return self._resposta_mockada(contexto_com_template, modo, dados_indicadores, dados_noticias)

        # Obter instrucções do sistema do template
        prompt_sistema = TemplatesAnalise.obter_prompt_sistema(modo)

        try:
            resposta = self.cliente.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": contexto_com_template}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperatura
            )

            analise = resposta.choices[0].message.content
            logger.info(f"LLM respondeu com {len(analise)} caracteres (modo: {modo})")
            return analise, None

        except Exception as e:
            logger.error(f"Erro na chamada LLM: {e}")
            raise

    def _resposta_mockada(self, contexto: str, modo: str, dados_indicadores: Optional[Dict] = None, dados_noticias: Optional[Dict] = None) -> tuple[str, Optional[Dict]]:
        """
        Resposta mockada para testes sem API key real.
        Usa dados reais quando disponíveis para maior realismo.
        Retorna tupla: (analise_texto, dados_validacao)
        """
        # Extrair dados do contexto
        linhas = contexto.split('\n')
        ativo = "EURUSD"  # Default
        preco = 1.1565   # Default
        variacao = 0.10  # Default

        for linha in linhas:
            if linha.startswith('ATIVO:'):
                ativo = linha.split(':')[1].strip()
            elif linha.startswith('PREÇO ATUAL:'):
                try:
                    preco = float(linha.split(':')[1].strip())
                except:
                    pass
            elif linha.startswith('VARIAÇÃO:'):
                try:
                    variacao_str = linha.split(':')[1].strip().rstrip('%')
                    variacao = float(variacao_str)
                except:
                    pass

        # Preparar dados de preço para calibração
        dados_preco_mock = {
            'ativo': ativo,
            'preco': preco,
            'variacao_pct': variacao,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'frescor': 'atual',
            'mercado_status': 'aberto'
        }

        # Usar calibrador de confiança automático
        calibrador = CalibradorConfianca()
        resultado_confianca = calibrador.calibrar_confianca(
            dados_preco_mock, dados_indicadores, dados_noticias
        )

        confianca_bull = resultado_confianca['confianca_bull']
        confianca_bear = resultado_confianca['confianca_bear']
        nivel_risco = resultado_confianca['nivel_risco']
        justificativas = resultado_confianca['justificativas']

        # Validar consistência entre fontes
        validador = ValidadorConsistencia()
        resultado_consistencia = validador.validar_consistencia(
            dados_preco_mock, dados_indicadores, dados_noticias,
            confianca_bull, confianca_bear
        )

        alertas_consistencia = resultado_consistencia['alertas']
        score_consistencia = resultado_consistencia['score_consistencia']
        nivel_consistencia = resultado_consistencia['nivel_consistencia']

        # Usar dados reais se disponíveis
        indicadores_info = ""
        rsi_valor = 50.0  # Default neutro
        vies_basico = "NEUTRO"  # Default neutro
        suporte = round(preco * 0.98, 4)  # Suporte aproximado 2% abaixo
        resistencia = round(preco * 1.02, 4)  # Resistência aproximada 2% acima
        pivot = round(preco, 4)  # Pivot aproximado no preço atual

        # Defaults para SMA se não fornecido
        sma_default = {
            'valor': preco * 0.99,
            'sinal': 'ACIMA',
            'diferenca_pct': 1.5
        }

        if dados_indicadores and 'indicadores' in dados_indicadores:
            sma = dados_indicadores['indicadores']['sma']
            rsi = dados_indicadores['indicadores']['rsi']
            rsi_valor = rsi['valor']

            # Determinar viés básico baseado no RSI e SMA
            if rsi['valor'] > 70:
                vies_basico = "SOBRECOMPRADO"
            elif rsi['valor'] < 30:
                vies_basico = "SOBREVENDIDO"
            elif sma['sinal'] == "ACIMA":
                vies_basico = "ALTISTA"
            elif sma['sinal'] == "ABAIXO":
                vies_basico = "BAIXISTA"
            else:
                vies_basico = "NEUTRO"

            indicadores_info = f"""
**Indicadores Técnicos**:
- SMA20: {sma['valor']:.4f} ({sma['sinal']}, diferença: {sma['diferenca_pct']:+.2f}%)
- RSI14: {rsi['valor']:.2f} ({rsi['sinal']} - {rsi['interpretacao']})
"""
        else:
            # Usar defaults quando dados não fornecidos
            sma = sma_default
            rsi_valor = 50.0
            vies_basico = "NEUTRO"
            indicadores_info = """
**Indicadores Técnicos**:
- Dados não disponíveis no contexto de teste
- Usando valores padrão para validação
"""

        # Usar dados de notícias se disponíveis
        noticias_info = ""
        sentimento_geral = "NEUTRO"
        impacto_geral = "MÉDIO"

        if dados_noticias and 'resumo_geral' in dados_noticias:
            sentimento_geral = dados_noticias['resumo_geral'].get('sentimento_geral', 'NEUTRO')
            impacto_geral = dados_noticias['resumo_geral'].get('impacto_geral', 'MÉDIO')
            noticias_info = f"""

**Contexto de Notícias**:
- Sentimento Geral: {sentimento_geral}
- Impacto Geral: {impacto_geral}
- {len(dados_noticias.get('noticias', []))} notícia(s) analisadas
"""

        if modo == "analista":
            # Estrutura padronizada para modo analista
            drivers = [
                {
                    "tipo": "macroeconomico",
                    "titulo": "Política Monetária Divergente",
                    "descricao": "BCE sinaliza pausa no aperto enquanto Fed mantém postura restritiva",
                    "impacto": "ALTO",
                    "fonte": "Comunicações oficiais BCE/Fed"
                },
                {
                    "tipo": "fundamental",
                    "titulo": "Dados de Inflação Europeia",
                    "descricao": "Inflação zona do euro em 2.1% vs 3.7% nos EUA",
                    "impacto": "MÉDIO",
                    "fonte": "Eurostat + Bureau of Labor Statistics"
                },
                {
                    "tipo": "tecnico",
                    "titulo": "Momentum Baixista",
                    "descricao": f"Preço abaixo SMA20 com diferença de {sma['diferenca_pct']:+.2f}%",
                    "impacto": "ALTO",
                    "fonte": "Yahoo Finance + pandas-ta"
                }
            ]

            riscos = [
                {
                    "categoria": "politico",
                    "titulo": "Eleições Europeias",
                    "descricao": "Pode aumentar volatilidade e incerteza política",
                    "probabilidade": "MÉDIA",
                    "impacto": "ALTO"
                },
                {
                    "categoria": "economico",
                    "titulo": "Payrolls EUA Surpreendentes",
                    "descricao": "Dados de emprego mais fortes que esperado podem fortalecer dólar",
                    "probabilidade": "ALTA",
                    "impacto": "ALTO"
                },
                {
                    "categoria": "sentimento",
                    "titulo": f"Notícias {sentimento_geral.lower()} com impacto {impacto_geral.lower()}",
                    "descricao": "Sentimento de mercado pode influenciar momentum",
                    "probabilidade": "MÉDIA",
                    "impacto": impacto_geral
                }
            ]

            proximos_passos = [
                {
                    "acao": "monitorar",
                    "titulo": "Dados de Emprego EUA",
                    "quando": "Próxima sexta-feira",
                    "importancia": "ALTA"
                },
                {
                    "acao": "observar",
                    "titulo": "Níveis Técnicos Chave",
                    "quando": "Próximas 24-48h",
                    "importancia": "MÉDIA"
                },
                {
                    "acao": "avaliar",
                    "titulo": "Comunicação BCE",
                    "quando": "Próxima reunião (dezembro)",
                    "importancia": "ALTA"
                }
            ]

            fontes = [
                {
                    "tipo": "dados_mercado",
                    "titulo": "Yahoo Finance",
                    "url": f"https://finance.yahoo.com/quote/{ativo}=X",
                    "frescor": "tempo_real",
                    "confiabilidade": "ALTA"
                },
                {
                    "tipo": "indicadores_tecnicos",
                    "titulo": "pandas-ta + Yahoo Finance",
                    "url": "https://github.com/twopirllc/pandas-ta",
                    "frescor": f"{dados_indicadores.get('dados_brutos', {}).get('periodo_analisado', {}).get('fim', 'N/A') if dados_indicadores else 'N/A'}",
                    "confiabilidade": "ALTA"
                },
                {
                    "tipo": "noticias",
                    "titulo": "Reuters + Bloomberg + CNBC",
                    "url": f"https://www.reuters.com/search/news?blob={ativo}",
                    "frescor": "últimas 7 dias",
                    "confiabilidade": "ALTA"
                }
            ]

            analise_texto = f"## Análise Fundamentalista Completa - {ativo}\n\n"
            analise_texto += f"**Timestamp da Análise**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            analise_texto += "### Contexto Macroeconômico\n"
            analise_texto += f"O par {ativo} opera em ambiente de crescente incerteza quanto à política monetária divergente entre BCE e Fed. "
            analise_texto += f"Dados de inflação mostram arrefecimento na zona do euro (2.1%) contrastando com resiliência americana (3.7%).\n\n"
            analise_texto += "### Drivers Principais\n"
            for driver in drivers:
                analise_texto += f"- **{driver['titulo']}**: {driver['descricao']} (Impacto: {driver['impacto']})\n"
            analise_texto += "\n"
            analise_texto += "### Análise Técnica\n"
            analise_texto += f"- **Preço Atual**: {preco:.4f} ({variacao:+.2f}%), mercado aberto\n"
            analise_texto += indicadores_info + "\n"
            analise_texto += "### Riscos Identificados\n"
            for risco in riscos:
                analise_texto += f"- **{risco['titulo']}**: {risco['descricao']} (Prob: {risco['probabilidade']}, Impacto: {risco['impacto']})\n"
            analise_texto += "\n"
            analise_texto += "### Próximos Passos\n"
            for passo in proximos_passos:
                analise_texto += f"- **{passo['titulo']}** ({passo['quando']}) - Importância: {passo['importancia']}\n"
            analise_texto += "\n"
            analise_texto += "### Fontes Consultadas\n"
            for fonte in fontes:
                analise_texto += f"- **{fonte['titulo']}**: [{fonte['url']}] ({fonte['frescor']}, Confiabilidade: {fonte['confiabilidade']})\n"
            analise_texto += "\n"
            analise_texto += "**Perspectiva Geral**: O par deve permanecer volátil até próximos catalisadores fundamentais. Recomenda-se cautela e acompanhamento próximo dos dados econômicos."

            return analise_texto, {
                'drivers': drivers,
                'riscos': riscos,
                'proximos_passos': proximos_passos,
                'fontes': fontes,
                'alertas': alertas_consistencia,
                'score_consistencia': score_consistencia,
                'nivel_consistencia': nivel_consistencia,
                'divergencias_detectadas': len(alertas_consistencia),
                'fonte_validacao': 'ValidadorConsistencia v1.0'
            }
        else:  # trader
            # Estrutura padronizada para modo trader
            drivers = [
                {
                    "tipo": "tecnico",
                    "titulo": "Momentum de Curto Prazo",
                    "descricao": f"{vies_basico} com RSI {rsi_valor:.1f}",
                    "impacto": "ALTO",
                    "fonte": "Yahoo Finance + pandas-ta"
                },
                {
                    "tipo": "sentimento",
                    "titulo": f"Notícias {sentimento_geral.lower()}",
                    "descricao": f"Impacto {impacto_geral.lower()} no mercado",
                    "impacto": impacto_geral,
                    "fonte": "Reuters + Bloomberg + CNBC"
                }
            ]

            riscos = [
                {
                    "categoria": "volatilidade",
                    "titulo": "Rompimento de Níveis Chave",
                    "descricao": f"Quebra de suporte {suporte} ou resistência {resistencia}",
                    "probabilidade": "ALTA",
                    "impacto": "ALTO"
                },
                {
                    "categoria": "noticias",
                    "titulo": "Eventos Econômicos Surpreendentes",
                    "descricao": "Payrolls EUA ou dados europeus fora do esperado",
                    "probabilidade": "MÉDIA",
                    "impacto": "ALTO"
                }
            ]

            proximos_passos = [
                {
                    "acao": "monitorar",
                    "titulo": "Confirmação de Rompimento",
                    "quando": "Próximas 24h",
                    "importancia": "ALTA"
                },
                {
                    "acao": "definir",
                    "titulo": "Stop Loss Obrigatório",
                    "quando": "Antes de qualquer entrada",
                    "importancia": "CRÍTICA"
                }
            ]

            fontes = [
                {
                    "tipo": "dados_mercado",
                    "titulo": "Yahoo Finance",
                    "url": f"https://finance.yahoo.com/quote/{ativo}=X",
                    "frescor": "tempo_real",
                    "confiabilidade": "ALTA"
                },
                {
                    "tipo": "indicadores_tecnicos",
                    "titulo": "pandas-ta",
                    "url": "https://github.com/twopirllc/pandas-ta",
                    "frescor": f"{dados_indicadores.get('dados_brutos', {}).get('periodo_analisado', {}).get('fim', 'N/A') if dados_indicadores else 'N/A'}",
                    "confiabilidade": "ALTA"
                }
            ]

            analise_texto = f"## Análise Técnica Rápida - {ativo}\n\n"
            analise_texto += f"**Timestamp da Análise**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            analise_texto += f"**Setup Atual**: Preço {preco:.4f} ({variacao:+.2f}%), mercado aberto\n"
            analise_texto += indicadores_info + "\n\n"
            analise_texto += "**Níveis Chave**:\n"
            analise_texto += f"- Suporte: {suporte} (forte)\n"
            analise_texto += f"- Resistência: {resistencia} (médio)\n"
            analise_texto += f"- Pivot: {pivot}\n\n"
            analise_texto += f"**Momentum**: {vies_basico}, RSI {rsi_valor:.1f}\n"
            analise_texto += "**Volatilidade**: Média (20 pips diários)\n"
            analise_texto += noticias_info + "\n\n"
            analise_texto += "**Cenários de Trading**:\n"
            analise_texto += f"- **Bull ({confianca_bull}% confiança)**: Quebra {resistencia} → alvo {resistencia + 0.01:.4f}\n"
            analise_texto += f"- **Bear ({confianca_bear}% confiança)**: Quebra {suporte} → alvo {suporte - 0.01:.4f}\n\n"
            analise_texto += f"**Calibração de Confiança**: {justificativas}\n"
            analise_texto += f"**Nível de Risco**: {nivel_risco}\n"
            analise_texto += f"**Consistência**: {score_consistencia:.1f}/100 ({nivel_consistencia})\n"

            # Adicionar alertas de divergência se houver
            if alertas_consistencia:
                analise_texto += "\n**🚨 ALERTAS DE DIVERGÊNCIA:**\n"
                for alerta in alertas_consistencia:
                    analise_texto += f"- **{alerta['severidade']}**: {alerta['titulo']} - {alerta['mensagem']}\n"
                    analise_texto += f"  → {alerta['recomendacao']}\n"
                analise_texto += "\n"

            analise_texto += "**Próximos Passos**:\n"
            for passo in proximos_passos:
                analise_texto += f"- **{passo['titulo']}** ({passo['quando']}) - Importância: {passo['importancia']}\n"
            analise_texto += "\n"
            analise_texto += "**Fontes**: [Yahoo Finance](https://finance.yahoo.com/quote/{ativo}=X) | [pandas-ta](https://github.com/twopirllc/pandas-ta)\n"
            analise_texto += "**Timing**: Aguardar confirmação de rompimento\n"

            return analise_texto, {
                'drivers': drivers,
                'riscos': riscos,
                'proximos_passos': proximos_passos,
                'fontes': fontes,
                'alertas': alertas_consistencia,
                'score_consistencia': score_consistencia,
                'nivel_consistencia': nivel_consistencia,
                'divergencias_detectadas': len(alertas_consistencia),
                'fonte_validacao': 'ValidadorConsistencia v1.0'
            }

    def _estruturar_resposta_final(
        self,
        ativo: str,
        dados_preco: Dict,
        dados_indicadores: Optional[Dict],
        dados_noticias: Optional[Dict],
        analise_llm: str,
        modo: str,
        dados_validacao: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Estrutura a resposta final com dados + análise + metadados.
        Integra Sistema de Transparência Radical para downgrade de confiança e alertas.
        """
        # SISTEMA DE TRANSPARÊNCIA RADICAL
        sistema_transparency = obter_sistema_transparency_radical()

        # Aplicar downgrade de confiança forçado
        confianca_original = 60  # Padrão simulado
        resultado_downgrade = sistema_transparency.downgrade_confianca_forcado(confianca_original)

        # Gerar seção de alertas críticos
        secao_alertas = sistema_transparency.gerar_secao_alertas_criticos()

        # Gerar disclaimer obrigatório
        disclaimer = sistema_transparency.gerar_disclaimer_obrigatorio()

        # Aplicar sistema completo de disclaimers e segurança
        sistema_seguranca = SistemaDisclaimers()
        relatorio_seguranca = sistema_seguranca.gerar_relatorio_seguranca(analise_llm, modo)

        # Prepend secção de alertas + disclaimer + análise original
        analise_com_alertas_e_disclaimers = ""

        if secao_alertas:
            analise_com_alertas_e_disclaimers += secao_alertas + "\n\n"

        analise_com_alertas_e_disclaimers += disclaimer + "\n\n"
        analise_com_alertas_e_disclaimers += relatorio_seguranca["analise_final"]

        resposta = {
            "ativo": ativo,
            "timestamp_analise": datetime.now(timezone.utc).isoformat(),
            "modo_analise": modo,
            "dados_mercado": dados_preco,
            "analise": {
                "conteudo_markdown": analise_com_alertas_e_disclaimers,
                "conteudo_original": analise_llm,
                "fonte_llm": self.modelo,
                "tokens_estimados": len(analise_com_alertas_e_disclaimers.split()) * 1.3
            },
            "transparencia_radical": {
                "confianca_original": resultado_downgrade["confianca_original"],
                "confianca_forcada": resultado_downgrade["confianca_forcada"],
                "percentual_downgrade": resultado_downgrade["percentual_downgrade"],
                "justificativa": resultado_downgrade["justificativa"],
                "estrelas_display": resultado_downgrade["estrelas_display"],
                "alertas_criticos_count": len(sistema_transparency.alertas_criticos),
            },
            "seguranca": {
                "disclaimers_aplicados": relatorio_seguranca["metadados_seguranca"]["disclaimers_aplicados"],
                "status_seguranca": relatorio_seguranca["metadados_seguranca"]["status_seguranca"],
                "sanitizacao_aplicada": relatorio_seguranca["metadados_seguranca"]["sanitizacao_aplicada"],
                "validacao_conteudo": relatorio_seguranca["validacao_conteudo"]
            },
            "metadados": {
                "versao_sistema": "1.0.0-transparency-radical",
                "fonte_dados": "Yahoo Finance + pandas-ta + OpenAI",
                "disclaimer_aplicado": True,
                "sistema_seguranca": "SistemaDisclaimers v1.0 + TransparencyRadical v1.0",
                "qualidade_dados_score": 85  # Placeholder para agora
            }
        }

        # Adicionar indicadores se disponíveis
        if dados_indicadores:
            resposta["indicadores_tecnicos"] = dados_indicadores

        # Adicionar notícias se disponíveis
        if dados_noticias:
            resposta["noticias"] = dados_noticias

        # Adicionar calibração de confiança se disponível
        if 'resultado_confianca' in locals():
            resposta["calibracao_confianca"] = resultado_confianca

        # Adicionar validação de consistência se disponível
        if dados_validacao:
            resposta["validacao_consistencia"] = dados_validacao

            # Adicionar campos estruturados se disponíveis na validação
            if 'drivers' in dados_validacao:
                resposta["estrutura_analise"] = {
                    "drivers": dados_validacao['drivers'],
                    "riscos": dados_validacao['riscos'],
                    "proximos_passos": dados_validacao['proximos_passos'],
                    "fontes": dados_validacao['fontes']
                }

        return resposta


def analisar_ativo_cli(
    ativo: str,
    modo: str = "analista",
    incluir_historico: bool = False,
    saida_json: bool = False
) -> None:
    """
    Função CLI para análise de ativos (ponto de entrada principal).
    """
    try:
        orquestrador = OrquestradorAnalise()
        resultado = orquestrador.analisar_ativo(ativo, modo, incluir_historico)

        if saida_json:
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        else:
            # Saída formatada para humanos
            print(f"\n{'='*60}")
            print(f"ANÁLISE DE {resultado['ativo'].upper()}")
            print(f"{'='*60}")
            print(f"Modo: {resultado['modo_analise']}")
            print(f"Timestamp: {resultado['timestamp_analise']}")
            print(f"Preço Atual: {resultado['dados_mercado']['preco']}")
            print(f"Variação: {resultado['dados_mercado']['variacao_pct']:+.2f}%")
            print(f"Status Mercado: {resultado['dados_mercado'].get('mercado_status', 'N/A')}")
            print(f"Frescor Dados: {resultado['dados_mercado'].get('frescor', 'N/A')}")
            print(f"\n{'='*60}")
            print("ANÁLISE:")
            print(f"{'='*60}")
            print(resultado['analise']['conteudo_markdown'])
            print(f"\n{'='*60}")
            print("FONTE: Yahoo Finance + OpenAI GPT-4o-mini")
            print(f"Timestamp Análise: {resultado['timestamp_analise']}")
            print(f"{'='*60}\n")

    except Exception as e:
        logger.error(f"Erro na análise CLI: {e}")
        print(f"ERRO: {str(e)}")
        exit(1)


if __name__ == "__main__":
    # Exemplo de uso direto
    import sys

    if len(sys.argv) < 2:
        print("Uso: python orquestrador_analise.py <ATIVO> [modo] [--json] [--historico]")
        print("Exemplo: python orquestrador_analise.py EURUSD trader --json")
        exit(1)

    ativo = sys.argv[1]
    modo = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "analista"
    saida_json = "--json" in sys.argv
    incluir_historico = "--historico" in sys.argv

    analisar_ativo_cli(ativo, modo, incluir_historico, saida_json)