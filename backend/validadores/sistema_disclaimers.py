"""
Sistema de Segurança e Disclaimers — Agent Especialista Mercado Financeiro

Implementa camadas de segurança e disclaimers obrigatórios para proteger
usuários contra interpretações incorretas das análises de mercado.
"""

import re
from typing import Dict, List, Any
from datetime import datetime, timezone

class SistemaDisclaimers:
    """
    Sistema abrangente de disclaimers e validações de segurança.
    """

    def __init__(self):
        """Inicializa o sistema de disclaimers."""
        self.disclaimers_obrigatorios = self._carregar_disclaimers_obrigatorios()
        self.palavras_proibidas = self._carregar_palavras_proibidas()
        self.padrao_seguranca = self._compilar_padrao_seguranca()

    def _carregar_disclaimers_obrigatorios(self) -> Dict[str, str]:
        """Carrega disclaimers obrigatórios por tipo de análise."""
        return {
            "geral": """
⚠️ **DISCLAIMER IMPORTANTE**

Esta análise é fornecida apenas para fins informativos e educacionais.
NÃO constitui recomendação de investimento, conselho financeiro ou solicitação para comprar/vender ativos.

As análises são baseadas em dados históricos e condições de mercado atuais, que podem mudar rapidamente.
Resultados passados não garantem resultados futuros.

Sempre consulte profissionais certificados antes de tomar decisões de investimento.
""",

            "risco": """
🚨 **AVISO DE RISCO**

Trading de forex e outros ativos financeiros envolve risco substancial de perda.
Você pode perder todo o capital investido.

Esta análise NÃO substitui análise fundamental própria e due diligence.
""",

            "limitação": """
📊 **LIMITAÇÕES DA ANÁLISE**

- Dados em tempo real podem ter atraso
- Análises técnicas não garantem resultados
- Condições de mercado podem mudar rapidamente
- Sistema em fase BETA - use com cautela
""",

            "transparencia": """
🔍 **TRANSPARÊNCIA TOTAL**

- Fontes de dados: Yahoo Finance, APIs públicas
- Modelo: GPT-4o-mini (dados mock para desenvolvimento)
- Timestamp: {timestamp}
- Confiança estimada: Baseada em indicadores objetivos
"""
        }

    def _carregar_palavras_proibidas(self) -> List[str]:
        """Carrega lista de palavras/frases que indicam linguagem proibida."""
        return [
            # Linguagem prescritiva
            "compre", "venda", "invista", "negocie",
            "recomendo", "aconselho", "sugiro",
            "obrigatório", "deve", "tem que",
            "garantido", "certo", "seguro",

            # Promessas de performance
            "lucro garantido", "sem risco", "risco zero",
            "retorno garantido", "performance garantida",

            # Linguagem especulativa perigosa
            "aposte", "risque", "arrisque",
            "oportunidade única", "não perca"
        ]

    def _compilar_padrao_seguranca(self) -> re.Pattern:
        """Compila padrão regex para detecção de linguagem proibida."""
        # Criar padrão que detecta frases proibidas (case insensitive)
        padrao = r'\b(?:' + '|'.join(re.escape(palavra) for palavra in self.palavras_proibidas) + r')\b'
        return re.compile(padrao, re.IGNORECASE | re.UNICODE)

    def validar_conteudo_seguro(self, texto: str) -> Dict[str, Any]:
        """
        Valida se o conteúdo está em conformidade com políticas de segurança.

        Args:
            texto: Conteúdo a ser validado

        Returns:
            dict: Resultado da validação com status e alertas
        """
        resultado = {
            "seguro": True,
            "alertas": [],
            "violacoes_detectadas": [],
            "recomendacoes": []
        }

        # Verificar linguagem proibida
        matches = self.padrao_seguranca.findall(texto)
        if matches:
            resultado["seguro"] = False
            resultado["violacoes_detectadas"].extend(matches)
            resultado["alertas"].append({
                "tipo": "linguagem_proibida",
                "severidade": "ALTA",
                "mensagem": f"Detectadas {len(matches)} palavras/frases proibidas: {', '.join(matches[:3])}{'...' if len(matches) > 3 else ''}",
                "recomendacao": "Substituir por linguagem neutra e descritiva"
            })

        # Verificar se contém disclaimers obrigatórios
        disclaimers_ausentes = []
        for tipo, disclaimer in self.disclaimers_obrigatorios.items():
            if tipo != "transparencia":  # Transparência é dinâmica
                # Verificar se pelo menos 80% do disclaimer está presente
                palavras_disclaimer = set(disclaimer.lower().split())
                palavras_texto = set(texto.lower().split())
                cobertura = len(palavras_disclaimer.intersection(palavras_texto)) / len(palavras_disclaimer)

                if cobertura < 0.8:
                    disclaimers_ausentes.append(tipo)

        if disclaimers_ausentes:
            resultado["alertas"].append({
                "tipo": "disclaimer_ausente",
                "severidade": "MÉDIA",
                "mensagem": f"Disclaimers ausentes: {', '.join(disclaimers_ausentes)}",
                "recomendacao": "Incluir disclaimers obrigatórios no início da análise"
            })

        # Verificar comprimento mínimo para análise séria
        if len(texto.split()) < 50:
            resultado["alertas"].append({
                "tipo": "conteudo_insuficiente",
                "severidade": "BAIXA",
                "mensagem": "Análise muito curta para ser considerada completa",
                "recomendacao": "Expandir análise com mais contexto e detalhes"
            })

        return resultado

    def aplicar_disclaimers(self, analise: str, modo: str = "trader") -> str:
        """
        Aplica disclaimers obrigatórios à análise.

        Args:
            analise: Texto da análise
            modo: Modo de análise (trader/analista)

        Returns:
            str: Análise com disclaimers aplicados
        """
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        # Header com timestamp e versão
        header = f"""# Análise de Mercado Financeiro
**Sistema**: Agent Especialista v1.0.0
**Timestamp**: {timestamp}
**Modo**: {modo.title()}
**Status**: ANÁLISE INFORMATIVA - NÃO CONSTITUI RECOMENDAÇÃO

"""

        # Disclaimers obrigatórios
        disclaimers = self.disclaimers_obrigatorios["geral"] + "\n\n" + \
                     self.disclaimers_obrigatorios["risco"] + "\n\n" + \
                     self.disclaimers_obrigatorios["limitação"] + "\n\n" + \
                     self.disclaimers_obrigatorios["transparencia"].format(timestamp=timestamp)

        # Combinar tudo
        analise_segura = header + disclaimers + "\n\n---\n\n" + analise

        return analise_segura

    def sanitizar_texto(self, texto: str) -> str:
        """
        Sanitiza texto removendo ou substituindo conteúdo potencialmente perigoso.

        Args:
            texto: Texto a ser sanitizado

        Returns:
            str: Texto sanitizado
        """
        # Substituir linguagem proibida por alternativas seguras
        substituicoes = {
            "compre": "considere compra se",
            "venda": "considere venda se",
            "invista": "avalia investimento em",
            "recomendo": "sugiro avaliar",
            "garantido": "potencial",
            "certo": "possível",
            "sem risco": "com risco controlado"
        }

        texto_sanitizado = texto
        for proibida, segura in substituicoes.items():
            texto_sanitizado = re.sub(
                r'\b' + re.escape(proibida) + r'\b',
                segura,
                texto_sanitizado,
                flags=re.IGNORECASE
            )

        return texto_sanitizado

    def gerar_relatorio_seguranca(self, analise: str, modo: str) -> Dict[str, Any]:
        """
        Gera relatório completo de segurança para uma análise.

        Args:
            analise: Texto da análise
            modo: Modo de análise

        Returns:
            dict: Relatório completo de segurança
        """
        validacao = self.validar_conteudo_seguro(analise)
        analise_com_disclaimers = self.aplicar_disclaimers(analise, modo)
        analise_sanitizada = self.sanitizar_texto(analise_com_disclaimers)

        return {
            "validacao_conteudo": validacao,
            "analise_original": analise,
            "analise_com_disclaimers": analise_com_disclaimers,
            "analise_final": analise_sanitizada,
            "metadados_seguranca": {
                "timestamp_validacao": datetime.now(timezone.utc).isoformat(),
                "modo_analise": modo,
                "disclaimers_aplicados": list(self.disclaimers_obrigatorios.keys()),
                "sanitizacao_aplicada": analise != analise_sanitizada,
                "status_seguranca": "APROVADO" if validacao["seguro"] else "REVISAR"
            }
        }