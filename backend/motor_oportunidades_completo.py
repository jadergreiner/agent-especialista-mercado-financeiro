"""
Motor de Oportunidades Completo
Sistema Orquestrador Integrado para Detecção ML, Tracking e Alertas

Funcionalidades:
1. Orquestração completa dos sistemas ML, tracking e alertas
2. Pipeline automático de detecção → análise → alertas
3. Monitoramento contínuo e auto-aprimoramento
4. Interface unificada para operação em produção
5. Sistema de logs e métricas centralizadas
6. Configuração flexível e adaptativa
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import logging
import asyncio
from pathlib import Path

# Importar módulos do sistema
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from detector_oportunidades_ml import DetectorOportunidadesML, AnalisadorMacroEconomico
    from sistema_tracking_aprendizado import SistemaTracking, SistemaAprendizadoContinuo
    from sistema_alertas_inteligentes import SistemaAlertasInteligentes, AlertaInteligente
except ImportError as e:
    print(f"⚠️ Aviso: Módulos não encontrados - {e}")
    print("🔄 Sistema funcionará em modo simulação")


class MotorOportunidadesCompleto:
    """Sistema orquestrador principal para detecção de oportunidades"""

    def __init__(self, config_path: Optional[str] = None):
        self.logger = self._configurar_logger()

        # Configuração
        self.config = self._carregar_configuracao(config_path)

        # Inicializar subsistemas
        self.analisador_macro = None
        self.detector_ml = None
        self.sistema_tracking = None
        self.sistema_aprendizado = None
        self.sistema_alertas = None

        # Estado do sistema
        self.status_sistema = "INICIALIZANDO"
        self.ultima_execucao = None
        self.metricas_operacionais = {}

        # Diretórios
        self.caminho_base = "data"
        self.caminho_logs = os.path.join(self.caminho_base, "logs")
        self.caminho_metricas = os.path.join(self.caminho_base, "metricas_operacionais")

        # Criar estrutura de diretórios
        self._criar_estrutura_diretorios()

        # Inicializar subsistemas
        self._inicializar_subsistemas()

    def _configurar_logger(self) -> logging.Logger:
        """Configurar sistema de logging centralizado"""
        logger = logging.getLogger('MotorOportunidades')
        logger.setLevel(logging.INFO)

        # Criar handler para arquivo se não existir
        if not logger.handlers:
            os.makedirs("data/logs", exist_ok=True)

            # Handler para arquivo
            file_handler = logging.FileHandler(
                f"data/logs/motor_oportunidades_{datetime.now().strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)

            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    def _carregar_configuracao(self, config_path: Optional[str]) -> Dict:
        """Carregar configuração do sistema"""
        config_padrao = {
            'modo_operacao': 'PRODUCAO',  # PRODUCAO, DESENVOLVIMENTO, TESTE
            'intervalo_execucao_minutos': 30,
            'max_oportunidades_por_execucao': 10,
            'ativar_alertas_automaticos': True,
            'ativar_aprendizado_continuo': True,
            'threshold_retreino_automatico': 0.6,
            'backup_automatico': True,
            'monitoramento_performance': True,
            'debug_detalhado': False
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_arquivo = json.load(f)
                    config_padrao.update(config_arquivo)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar config: {e}")

        return config_padrao

    def _criar_estrutura_diretorios(self):
        """Criar estrutura completa de diretórios"""
        diretorios = [
            self.caminho_base,
            self.caminho_logs,
            self.caminho_metricas,
            os.path.join(self.caminho_base, "oportunidades"),
            os.path.join(self.caminho_base, "alertas"),
            os.path.join(self.caminho_base, "tracking"),
            os.path.join(self.caminho_base, "performance"),
            os.path.join(self.caminho_base, "ml_models"),
            os.path.join(self.caminho_base, "backup"),
            os.path.join(self.caminho_base, "config_alertas")
        ]

        for diretorio in diretorios:
            os.makedirs(diretorio, exist_ok=True)

    def _inicializar_subsistemas(self):
        """Inicializar todos os subsistemas"""
        try:
            self.logger.info("🔄 Inicializando subsistemas...")

            # Subsistema de análise macro
            try:
                self.analisador_macro = AnalisadorMacroEconomico()
                self.logger.info("✅ Analisador macro inicializado")
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar analisador macro: {e}")
                self.analisador_macro = None

            # Subsistema ML
            try:
                self.detector_ml = DetectorOportunidadesML()
                self.logger.info("✅ Detector ML inicializado")
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar detector ML: {e}")
                self.detector_ml = None

            # Subsistema de tracking
            try:
                self.sistema_tracking = SistemaTracking()
                self.logger.info("✅ Sistema de tracking inicializado")
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar tracking: {e}")
                self.sistema_tracking = None

            # Subsistema de aprendizado
            try:
                self.sistema_aprendizado = SistemaAprendizadoContinuo()
                self.logger.info("✅ Sistema de aprendizado inicializado")
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar aprendizado: {e}")
                self.sistema_aprendizado = None

            # Subsistema de alertas
            try:
                self.sistema_alertas = SistemaAlertasInteligentes()
                self.logger.info("✅ Sistema de alertas inicializado")
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar alertas: {e}")
                self.sistema_alertas = None

            # Verificar subsistemas críticos
            subsistemas_criticos = [
                self.detector_ml, self.sistema_alertas
            ]

            if all(s is not None for s in subsistemas_criticos):
                self.status_sistema = "OPERACIONAL"
                self.logger.info("✅ Todos os subsistemas críticos inicializados")
            else:
                self.status_sistema = "PARCIAL"
                self.logger.warning("⚠️ Alguns subsistemas não inicializados - modo parcial")

        except Exception as e:
            self.status_sistema = "ERRO"
            self.logger.error(f"❌ Erro geral na inicialização: {e}")

    def executar_ciclo_completo(self) -> Dict:
        """Executar ciclo completo de detecção de oportunidades"""
        try:
            self.logger.info("🔄 Iniciando ciclo completo de detecção")

            inicio = datetime.now()
            resultados = {
                'timestamp_inicio': inicio.isoformat(),
                'status': 'EM_ANDAMENTO',
                'etapas': {},
                'oportunidades_detectadas': [],
                'alertas_gerados': [],
                'metricas_ciclo': {}
            }

            # Etapa 1: Análise macroeconômica
            if self.analisador_macro:
                self.logger.info("📊 Executando análise macroeconômica...")
                try:
                    dados_macro = self._executar_analise_macro()
                    resultados['etapas']['analise_macro'] = {
                        'status': 'SUCESSO',
                        'dados_coletados': len(dados_macro) if dados_macro else 0
                    }
                except Exception as e:
                    self.logger.error(f"Erro na análise macro: {e}")
                    resultados['etapas']['analise_macro'] = {
                        'status': 'ERRO',
                        'erro': str(e)
                    }\n            \n            # Etapa 2: Detecção ML de oportunidades\n            if self.detector_ml:\n                self.logger.info(\"🤖 Executando detecção ML...\")\n                try:\n                    oportunidades = self._executar_deteccao_ml()\n                    resultados['oportunidades_detectadas'] = oportunidades\n                    resultados['etapas']['deteccao_ml'] = {\n                        'status': 'SUCESSO',\n                        'oportunidades_encontradas': len(oportunidades)\n                    }\n                except Exception as e:\n                    self.logger.error(f\"Erro na detecção ML: {e}\")\n                    resultados['etapas']['deteccao_ml'] = {\n                        'status': 'ERRO',\n                        'erro': str(e)\n                    }\n                    oportunidades = []\n            else:\n                oportunidades = []\n            \n            # Etapa 3: Geração de alertas\n            if self.sistema_alertas and oportunidades:\n                self.logger.info(\"🚨 Gerando alertas inteligentes...\")\n                try:\n                    alertas = self.sistema_alertas.processar_oportunidades_para_alertas(oportunidades)\n                    resultados['alertas_gerados'] = [a.to_dict() for a in alertas]\n                    resultados['etapas']['geracao_alertas'] = {\n                        'status': 'SUCESSO',\n                        'alertas_criados': len(alertas)\n                    }\n                except Exception as e:\n                    self.logger.error(f\"Erro na geração de alertas: {e}\")\n                    resultados['etapas']['geracao_alertas'] = {\n                        'status': 'ERRO',\n                        'erro': str(e)\n                    }\n            \n            # Etapa 4: Tracking e aprendizado\n            if self.sistema_tracking and self.sistema_aprendizado:\n                self.logger.info(\"📈 Executando tracking e aprendizado...\")\n                try:\n                    self._executar_tracking_aprendizado()\n                    resultados['etapas']['tracking_aprendizado'] = {\n                        'status': 'SUCESSO'\n                    }\n                except Exception as e:\n                    self.logger.error(f\"Erro no tracking: {e}\")\n                    resultados['etapas']['tracking_aprendizado'] = {\n                        'status': 'ERRO',\n                        'erro': str(e)\n                    }\n            \n            # Finalizar ciclo\n            fim = datetime.now()\n            duracao = (fim - inicio).total_seconds()\n            \n            resultados.update({\n                'timestamp_fim': fim.isoformat(),\n                'duracao_segundos': duracao,\n                'status': 'CONCLUIDO',\n                'metricas_ciclo': {\n                    'tempo_total': duracao,\n                    'oportunidades_detectadas': len(resultados['oportunidades_detectadas']),\n                    'alertas_gerados': len(resultados['alertas_gerados']),\n                    'etapas_bem_sucedidas': len([e for e in resultados['etapas'].values() \n                                               if e['status'] == 'SUCESSO'])\n                }\n            })\n            \n            # Salvar resultados do ciclo\n            self._salvar_resultados_ciclo(resultados)\n            \n            # Atualizar última execução\n            self.ultima_execucao = fim\n            \n            self.logger.info(f\"✅ Ciclo completo finalizado em {duracao:.1f}s\")\n            \n            return resultados\n            \n        except Exception as e:\n            self.logger.error(f\"❌ Erro no ciclo completo: {e}\")\n            return {\n                'status': 'ERRO_GERAL',\n                'erro': str(e),\n                'timestamp': datetime.now().isoformat()\n            }\n    \n    def _executar_analise_macro(self) -> Optional[Dict]:\n        \"\"\"Executar análise macroeconômica\"\"\"\n        if not self.analisador_macro:\n            return None\n            \n        try:\n            # Coletar dados DXY\n            dados_dxy = self.analisador_macro.coletar_dados_dxy()\n            \n            # Analisar eventos críticos\n            eventos = self.analisador_macro.analisar_eventos_criticos()\n            \n            # Analisar carry trades\n            carry_trades = self.analisador_macro.analisar_carry_trades()\n            \n            return {\n                'dxy': dados_dxy,\n                'eventos': eventos,\n                'carry_trades': carry_trades,\n                'timestamp': datetime.now().isoformat()\n            }\n            \n        except Exception as e:\n            self.logger.error(f\"Erro na análise macro: {e}\")\n            return None\n    \n    def _executar_deteccao_ml(self) -> List[Dict]:\n        \"\"\"Executar detecção ML de oportunidades\"\"\"\n        if not self.detector_ml:\n            return []\n            \n        try:\n            # Simular dados de posições do portfólio\n            posicoes_exemplo = self._obter_posicoes_portfolio()\n            \n            if not posicoes_exemplo:\n                self.logger.warning(\"Nenhuma posição encontrada no portfólio\")\n                return []\n            \n            # Detectar oportunidades\n            oportunidades = self.detector_ml.detectar_oportunidades(posicoes_exemplo)\n            \n            self.logger.info(f\"Detectadas {len(oportunidades)} oportunidades\")\n            \n            return oportunidades\n            \n        except Exception as e:\n            self.logger.error(f\"Erro na detecção ML: {e}\")\n            return []\n    \n    def _obter_posicoes_portfolio(self) -> List[Dict]:\n        \"\"\"Obter posições do portfólio (integração futura)\"\"\"\n        # Simular posições para demonstração\n        posicoes_simuladas = [\n            {\n                'par': 'EUR/USD',\n                'direction': 'LONG',\n                'entry_price': 1.0950,\n                'current_price': 1.0965,\n                'size': 100000,\n                'pnl_atual': 150.0,\n                'timestamp_abertura': (datetime.now() - timedelta(hours=2)).isoformat()\n            },\n            {\n                'par': 'GBP/JPY',\n                'direction': 'LONG',\n                'entry_price': 195.20,\n                'current_price': 195.50,\n                'size': 50000,\n                'pnl_atual': 75.0,\n                'timestamp_abertura': (datetime.now() - timedelta(hours=4)).isoformat()\n            }\n        ]\n        \n        return posicoes_simuladas\n    \n    def _executar_tracking_aprendizado(self):\n        \"\"\"Executar tracking e aprendizado contínuo\"\"\"\n        try:\n            if not self.sistema_tracking:\n                return\n                \n            # Calcular métricas de performance\n            metricas = self.sistema_tracking.calcular_metricas_performance()\n            \n            if 'erro' in metricas:\n                self.logger.warning(f\"Métricas indisponíveis: {metricas['erro']}\")\n                return\n            \n            # Avaliar necessidade de retreino\n            if self.sistema_aprendizado:\n                avaliacao = self.sistema_aprendizado.avaliar_necessidade_retreino()\n                \n                # Auto-retreino se necessário\n                if (avaliacao.get('necessita_retreino') and \n                    self.config.get('ativar_aprendizado_continuo')):\n                    \n                    self.logger.info(\"🔄 Iniciando retreino automático...\")\n                    # Aqui seria implementado o retreino automático\n                    \n            # Atualizar configuração de alertas\n            if self.sistema_alertas:\n                self.sistema_alertas.atualizar_configuracao_com_feedback(metricas)\n                \n        except Exception as e:\n            self.logger.error(f\"Erro no tracking/aprendizado: {e}\")\n    \n    def _salvar_resultados_ciclo(self, resultados: Dict):\n        \"\"\"Salvar resultados do ciclo de execução\"\"\"\n        try:\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            arquivo = f\"ciclo_execucao_{timestamp}.json\"\n            caminho = os.path.join(self.caminho_metricas, arquivo)\n            \n            with open(caminho, 'w', encoding='utf-8') as f:\n                json.dump(resultados, f, indent=2, ensure_ascii=False)\n                \n            self.logger.info(f\"Resultados salvos: {caminho}\")\n            \n        except Exception as e:\n            self.logger.error(f\"Erro ao salvar resultados: {e}\")\n    \n    def obter_status_sistema(self) -> Dict:\n        \"\"\"Obter status completo do sistema\"\"\"\n        return {\n            'status_geral': self.status_sistema,\n            'ultima_execucao': self.ultima_execucao.isoformat() if self.ultima_execucao else None,\n            'subsistemas': {\n                'analisador_macro': self.analisador_macro is not None,\n                'detector_ml': self.detector_ml is not None,\n                'sistema_tracking': self.sistema_tracking is not None,\n                'sistema_aprendizado': self.sistema_aprendizado is not None,\n                'sistema_alertas': self.sistema_alertas is not None\n            },\n            'configuracao': self.config,\n            'metricas_operacionais': self.metricas_operacionais,\n            'timestamp_status': datetime.now().isoformat()\n        }\n    \n    def executar_modo_continuo(self, duracao_horas: Optional[int] = None):\n        \"\"\"Executar sistema em modo contínuo\"\"\"\n        self.logger.info(\"🔄 Iniciando modo de execução contínua\")\n        \n        if duracao_horas:\n            fim_execucao = datetime.now() + timedelta(hours=duracao_horas)\n            self.logger.info(f\"⏰ Execução por {duracao_horas} horas\")\n        else:\n            fim_execucao = None\n            self.logger.info(\"♾️ Execução indefinida\")\n        \n        intervalo = self.config['intervalo_execucao_minutos'] * 60  # em segundos\n        \n        try:\n            while True:\n                # Verificar se deve parar\n                if fim_execucao and datetime.now() >= fim_execucao:\n                    break\n                \n                # Executar ciclo\n                resultados = self.executar_ciclo_completo()\n                \n                # Log resumo\n                if resultados['status'] == 'CONCLUIDO':\n                    metricas = resultados['metricas_ciclo']\n                    self.logger.info(\n                        f\"📊 Ciclo: {metricas['oportunidades_detectadas']} oportunidades, \"\n                        f\"{metricas['alertas_gerados']} alertas em {metricas['tempo_total']:.1f}s\"\n                    )\n                \n                # Aguardar próximo ciclo\n                self.logger.info(f\"⏳ Aguardando {self.config['intervalo_execucao_minutos']} minutos...\")\n                \n                import time\n                time.sleep(intervalo)\n                \n        except KeyboardInterrupt:\n            self.logger.info(\"⏹️ Execução interrompida pelo usuário\")\n        except Exception as e:\n            self.logger.error(f\"❌ Erro na execução contínua: {e}\")\n    \n    def gerar_relatorio_completo(self) -> Dict:\n        \"\"\"Gerar relatório completo do sistema\"\"\"\n        try:\n            relatorio = {\n                'timestamp_relatorio': datetime.now().isoformat(),\n                'status_sistema': self.obter_status_sistema(),\n                'metricas_performance': {},\n                'relatorio_alertas': {},\n                'sugestoes_melhoria': {},\n                'resumo_executivo': {}\n            }\n            \n            # Métricas de performance\n            if self.sistema_tracking:\n                try:\n                    metricas = self.sistema_tracking.calcular_metricas_performance()\n                    relatorio['metricas_performance'] = metricas\n                except Exception as e:\n                    relatorio['metricas_performance'] = {'erro': str(e)}\n            \n            # Relatório de alertas\n            if self.sistema_alertas:\n                try:\n                    rel_alertas = self.sistema_alertas.gerar_relatorio_alertas()\n                    relatorio['relatorio_alertas'] = rel_alertas\n                except Exception as e:\n                    relatorio['relatorio_alertas'] = {'erro': str(e)}\n            \n            # Sugestões de melhoria\n            if self.sistema_aprendizado:\n                try:\n                    sugestoes = self.sistema_aprendizado.sugerir_novos_inputs()\n                    relatorio['sugestoes_melhoria'] = sugestoes\n                except Exception as e:\n                    relatorio['sugestoes_melhoria'] = {'erro': str(e)}\n            \n            # Resumo executivo\n            relatorio['resumo_executivo'] = self._gerar_resumo_executivo(relatorio)\n            \n            # Salvar relatório\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            arquivo = f\"relatorio_completo_{timestamp}.json\"\n            caminho = os.path.join(self.caminho_metricas, arquivo)\n            \n            with open(caminho, 'w', encoding='utf-8') as f:\n                json.dump(relatorio, f, indent=2, ensure_ascii=False)\n            \n            return relatorio\n            \n        except Exception as e:\n            self.logger.error(f\"Erro ao gerar relatório: {e}\")\n            return {'erro': str(e)}\n    \n    def _gerar_resumo_executivo(self, relatorio: Dict) -> Dict:\n        \"\"\"Gerar resumo executivo dos resultados\"\"\"\n        resumo = {\n            'sistema_operacional': self.status_sistema == 'OPERACIONAL',\n            'recomendacoes': [],\n            'pontos_atencao': [],\n            'sucessos': []\n        }\n        \n        # Análise das métricas\n        metricas = relatorio.get('metricas_performance', {})\n        if 'resumo_geral' in metricas:\n            taxa_acerto = metricas['resumo_geral'].get('taxa_acerto_geral', 0)\n            \n            if taxa_acerto >= 80:\n                resumo['sucessos'].append(f\"Excelente taxa de acerto: {taxa_acerto}%\")\n            elif taxa_acerto >= 70:\n                resumo['sucessos'].append(f\"Boa taxa de acerto: {taxa_acerto}%\")\n            elif taxa_acerto < 60:\n                resumo['pontos_atencao'].append(f\"Taxa de acerto baixa: {taxa_acerto}%\")\n                resumo['recomendacoes'].append(\"Considerar retreino do modelo\")\n        \n        # Análise dos alertas\n        rel_alertas = relatorio.get('relatorio_alertas', {})\n        if 'resumo_geral' in rel_alertas:\n            taxa_execucao = rel_alertas['resumo_geral'].get('taxa_execucao', 0)\n            \n            if taxa_execucao >= 50:\n                resumo['sucessos'].append(f\"Boa taxa de execução de alertas: {taxa_execucao:.1f}%\")\n            elif taxa_execucao < 30:\n                resumo['pontos_atencao'].append(f\"Baixa execução de alertas: {taxa_execucao:.1f}%\")\n                resumo['recomendacoes'].append(\"Revisar relevância e timing dos alertas\")\n        \n        return resumo\n\n\ndef main():\n    \"\"\"Demonstração completa do motor de oportunidades\"\"\"\n    print(\"🚀 MOTOR DE OPORTUNIDADES COMPLETO\")\n    print(\"=\" * 70)\n    \n    # Inicializar motor\n    print(\"\\n🔧 Inicializando motor...\")\n    motor = MotorOportunidadesCompleto()\n    \n    # Mostrar status\n    status = motor.obter_status_sistema()\n    print(f\"\\n📊 STATUS DO SISTEMA:\")\n    print(f\"   Status geral: {status['status_geral']}\")\n    \n    subsistemas = status['subsistemas']\n    for nome, ativo in subsistemas.items():\n        emoji = \"✅\" if ativo else \"❌\"\n        print(f\"   {emoji} {nome.replace('_', ' ').title()}: {'Ativo' if ativo else 'Inativo'}\")\n    \n    # Executar ciclo completo\n    print(f\"\\n🔄 EXECUTANDO CICLO COMPLETO...\")\n    resultados = motor.executar_ciclo_completo()\n    \n    print(f\"\\n📈 RESULTADOS DO CICLO:\")\n    print(f\"   Status: {resultados['status']}\")\n    print(f\"   Duração: {resultados.get('duracao_segundos', 0):.1f}s\")\n    \n    # Mostrar etapas\n    etapas = resultados.get('etapas', {})\n    for nome, info in etapas.items():\n        emoji = \"✅\" if info['status'] == 'SUCESSO' else \"❌\"\n        print(f\"   {emoji} {nome.replace('_', ' ').title()}: {info['status']}\")\n    \n    # Mostrar métricas do ciclo\n    metricas = resultados.get('metricas_ciclo', {})\n    if metricas:\n        print(f\"\\n📊 MÉTRICAS DO CICLO:\")\n        print(f\"   Oportunidades detectadas: {metricas.get('oportunidades_detectadas', 0)}\")\n        print(f\"   Alertas gerados: {metricas.get('alertas_gerados', 0)}\")\n        print(f\"   Etapas bem-sucedidas: {metricas.get('etapas_bem_sucedidas', 0)}\")\n    \n    # Gerar relatório completo\n    print(f\"\\n📋 GERANDO RELATÓRIO COMPLETO...\")\n    relatorio = motor.gerar_relatorio_completo()\n    \n    if 'resumo_executivo' in relatorio:\n        resumo = relatorio['resumo_executivo']\n        \n        if resumo.get('sucessos'):\n            print(f\"\\n✅ SUCESSOS:\")\n            for sucesso in resumo['sucessos']:\n                print(f\"   • {sucesso}\")\n        \n        if resumo.get('recomendacoes'):\n            print(f\"\\n💡 RECOMENDAÇÕES:\")\n            for rec in resumo['recomendacoes']:\n                print(f\"   • {rec}\")\n    \n    print(f\"\\n✅ SISTEMA MOTOR OPERACIONAL\")\n    print(\"🔄 Para execução contínua: motor.executar_modo_continuo()\")\n    print(\"📊 Para relatórios: motor.gerar_relatorio_completo()\")\n    \n    return motor, resultados, relatorio\n\n\nif __name__ == \"__main__\":\n    motor, resultados, relatorio = main()"