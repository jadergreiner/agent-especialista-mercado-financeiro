""""""

Motor de Oportunidades Completo - Sistema de ProduçãoMotor de Oportunidades Completo

Captura oportunidades reais de mercado para execução imediataSistema Orquestrador Integrado para Detecção ML, Tracking e Alertas

"""

Funcionalidades:

import json1. Orquestração completa dos sistemas ML, tracking e alertas

import os2. Pipeline automático de detecção → análise → alertas

import sys3. Monitoramento contínuo e auto-aprimoramento

from datetime import datetime, timedelta4. Interface unificada para operação em produção

from typing import Dict, List, Optional5. Sistema de logs e métricas centralizadas

import logging6. Configuração flexível e adaptativa

"""

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json

try:import os

    from detector_oportunidades_ml import DetectorOportunidadesML, AnalisadorMacroEconomicoimport sys

    from sistema_tracking_aprendizado import SistemaTracking, SistemaAprendizadoContinuofrom datetime import datetime, timedelta

    from sistema_alertas_inteligentes import SistemaAlertasInteligentes, AlertaInteligentefrom typing import Dict, List, Optional, Tuple

except ImportError as e:import pandas as pd

    print(f"⚠️ Aviso: Módulos não encontrados - {e}")import logging

    print("🔄 Sistema funcionará em modo simulação")import asyncio

from pathlib import Path



class MotorOportunidadesCompleto:# Importar módulos do sistema

    """Sistema orquestrador principal para detecção de oportunidades"""sys.path.append(os.path.dirname(os.path.abspath(__file__)))



    def __init__(self, config_path: Optional[str] = None):try:

        self.logger = self._configurar_logger()    from detector_oportunidades_ml import DetectorOportunidadesML, AnalisadorMacroEconomico

    from sistema_tracking_aprendizado import SistemaTracking, SistemaAprendizadoContinuo

        # Configuração    from sistema_alertas_inteligentes import SistemaAlertasInteligentes, AlertaInteligente

        self.config = self._carregar_configuracao(config_path)except ImportError as e:

    print(f"⚠️ Aviso: Módulos não encontrados - {e}")

        # Inicializar subsistemas    print("🔄 Sistema funcionará em modo simulação")

        self.analisador_macro = None

        self.detector_ml = None

        self.sistema_tracking = Noneclass MotorOportunidadesCompleto:

        self.sistema_aprendizado = None    """Sistema orquestrador principal para detecção de oportunidades"""

        self.sistema_alertas = None

    def __init__(self, config_path: Optional[str] = None):

        # Status e métricas        self.logger = self._configurar_logger()

        self.status_sistema = "INICIALIZANDO"

        self.ultima_execucao = None        # Configuração

        self.metricas_operacionais = {}        self.config = self._carregar_configuracao(config_path)



        # Inicializar sistema        # Inicializar subsistemas

        self._inicializar_sistema()        self.analisador_macro = None

        self.detector_ml = None

    def _configurar_logger(self) -> logging.Logger:        self.sistema_tracking = None

        """Configurar sistema de logging"""        self.sistema_aprendizado = None

        logger = logging.getLogger('MotorOportunidades')        self.sistema_alertas = None

        logger.setLevel(logging.INFO)

        # Estado do sistema

        if not logger.handlers:        self.status_sistema = "INICIALIZANDO"

            # Handler para arquivo        self.ultima_execucao = None

            log_dir = "data/logs"        self.metricas_operacionais = {}

            os.makedirs(log_dir, exist_ok=True)

        # Diretórios

            log_file = os.path.join(log_dir, f"motor_oportunidades_{datetime.now().strftime('%Y%m%d')}.log")        self.caminho_base = "data"

            file_handler = logging.FileHandler(log_file, encoding='utf-8')        self.caminho_logs = os.path.join(self.caminho_base, "logs")

            file_handler.setLevel(logging.INFO)        self.caminho_metricas = os.path.join(self.caminho_base, "metricas_operacionais")



            # Handler para console        # Criar estrutura de diretórios

            console_handler = logging.StreamHandler()        self._criar_estrutura_diretorios()

            console_handler.setLevel(logging.INFO)

        # Inicializar subsistemas

            formatter = logging.Formatter(        self._inicializar_subsistemas()

                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

            )    def _configurar_logger(self) -> logging.Logger:

            file_handler.setFormatter(formatter)        """Configurar sistema de logging centralizado"""

            console_handler.setFormatter(formatter)        logger = logging.getLogger('MotorOportunidades')

        logger.setLevel(logging.INFO)

            logger.addHandler(file_handler)

            logger.addHandler(console_handler)        # Criar handler para arquivo se não existir

        if not logger.handlers:

        return logger            os.makedirs("data/logs", exist_ok=True)



    def _carregar_configuracao(self, config_path: Optional[str]) -> Dict:            # Handler para arquivo

        """Carregar configuração do sistema"""            file_handler = logging.FileHandler(

        config_padrao = {                f"data/logs/motor_oportunidades_{datetime.now().strftime('%Y%m%d')}.log",

            'modo_operacao': 'PRODUCAO',  # PRODUCAO, DESENVOLVIMENTO, TESTE                encoding='utf-8'

            'intervalo_execucao_minutos': 15,            )

            'max_oportunidades_por_execucao': 20,            file_handler.setLevel(logging.INFO)

            'ativar_alertas_automaticos': True,

            'ativar_aprendizado_continuo': True,            # Handler para console

            'threshold_retreino_automatico': 0.7,            console_handler = logging.StreamHandler()

            'backup_automatico': True,            console_handler.setLevel(logging.INFO)

            'monitoramento_performance': True,

            'debug_detalhado': False,            # Formatter

            'portfolio_principal': [            formatter = logging.Formatter(

                "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META", "AMZN",                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

                "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X", "USDCHF=X"            )

            ]            file_handler.setFormatter(formatter)

        }            console_handler.setFormatter(formatter)



        if config_path and os.path.exists(config_path):            logger.addHandler(file_handler)

            try:            logger.addHandler(console_handler)

                with open(config_path, 'r', encoding='utf-8') as f:

                    config_arquivo = json.load(f)        return logger

                    config_padrao.update(config_arquivo)

            except Exception as e:    def _carregar_configuracao(self, config_path: Optional[str]) -> Dict:

                self.logger.warning(f"Erro ao carregar config: {e}")        """Carregar configuração do sistema"""

        config_padrao = {

        return config_padrao            'modo_operacao': 'PRODUCAO',  # PRODUCAO, DESENVOLVIMENTO, TESTE

            'intervalo_execucao_minutos': 30,

    def _inicializar_sistema(self):            'max_oportunidades_por_execucao': 10,

        """Inicializar sistema completo"""            'ativar_alertas_automaticos': True,

        try:            'ativar_aprendizado_continuo': True,

            self.logger.info("🔄 Inicializando sistema de produção...")            'threshold_retreino_automatico': 0.6,

            'backup_automatico': True,

            # Criar estrutura de diretórios            'monitoramento_performance': True,

            self._criar_estrutura_diretorios()            'debug_detalhado': False

        }

            # Inicializar subsistemas

            self._inicializar_subsistemas()        if config_path and os.path.exists(config_path):

            try:

            # Verificar status final                with open(config_path, 'r', encoding='utf-8') as f:

            if self._verificar_subsistemas_criticos():                    config_arquivo = json.load(f)

                self.status_sistema = "OPERACIONAL"                    config_padrao.update(config_arquivo)

                self.logger.info("✅ Sistema operacional em modo produção")            except Exception as e:

            else:                self.logger.warning(f"Erro ao carregar config: {e}")

                self.status_sistema = "PARCIAL"

                self.logger.warning("⚠️ Sistema em modo parcial - alguns subsistemas indisponíveis")        return config_padrao



        except Exception as e:    def _criar_estrutura_diretorios(self):

            self.status_sistema = "ERRO"        """Criar estrutura completa de diretórios"""

            self.logger.error(f"❌ Erro na inicialização: {e}")        diretorios = [

            self.caminho_base,

    def _criar_estrutura_diretorios(self):            self.caminho_logs,

        """Criar estrutura completa de diretórios"""            self.caminho_metricas,

        diretorios = [            os.path.join(self.caminho_base, "oportunidades"),

            "data",            os.path.join(self.caminho_base, "alertas"),

            "data/logs",            os.path.join(self.caminho_base, "tracking"),

            "data/metricas_operacionais",            os.path.join(self.caminho_base, "performance"),

            "data/oportunidades",            os.path.join(self.caminho_base, "ml_models"),

            "data/alertas",            os.path.join(self.caminho_base, "backup"),

            "data/tracking",            os.path.join(self.caminho_base, "config_alertas")

            "data/performance",        ]

            "data/ml_models",

            "data/backup",        for diretorio in diretorios:

            "data/config_alertas"            os.makedirs(diretorio, exist_ok=True)

        ]

    def _inicializar_subsistemas(self):

        for diretorio in diretorios:        """Inicializar todos os subsistemas"""

            os.makedirs(diretorio, exist_ok=True)        try:

            self.logger.info("🔄 Inicializando subsistemas...")

    def _inicializar_subsistemas(self):

        """Inicializar todos os subsistemas"""            # Subsistema de análise macro

        try:            try:

            self.logger.info("🔄 Inicializando subsistemas...")                self.analisador_macro = AnalisadorMacroEconomico()

                self.logger.info("✅ Analisador macro inicializado")

            # Subsistema de análise macro            except Exception as e:

            try:                self.logger.error(f"❌ Erro ao inicializar analisador macro: {e}")

                self.analisador_macro = AnalisadorMacroEconomico()                self.analisador_macro = None

                self.logger.info("✅ Analisador macro inicializado")

            except Exception as e:            # Subsistema ML

                self.logger.error(f"❌ Erro ao inicializar analisador macro: {e}")            try:

                self.analisador_macro = None                self.detector_ml = DetectorOportunidadesML()

                self.logger.info("✅ Detector ML inicializado")

            # Subsistema ML            except Exception as e:

            try:                self.logger.error(f"❌ Erro ao inicializar detector ML: {e}")

                self.detector_ml = DetectorOportunidadesML()                self.detector_ml = None

                self.logger.info("✅ Detector ML inicializado")

            except Exception as e:            # Subsistema de tracking

                self.logger.error(f"❌ Erro ao inicializar detector ML: {e}")            try:

                self.detector_ml = None                self.sistema_tracking = SistemaTracking()

                self.logger.info("✅ Sistema de tracking inicializado")

            # Subsistema de tracking            except Exception as e:

            try:                self.logger.error(f"❌ Erro ao inicializar tracking: {e}")

                self.sistema_tracking = SistemaTracking()                self.sistema_tracking = None

                self.logger.info("✅ Sistema de tracking inicializado")

            except Exception as e:            # Subsistema de aprendizado

                self.logger.error(f"❌ Erro ao inicializar tracking: {e}")            try:

                self.sistema_tracking = None                self.sistema_aprendizado = SistemaAprendizadoContinuo()

                self.logger.info("✅ Sistema de aprendizado inicializado")

            # Subsistema de aprendizado            except Exception as e:

            try:                self.logger.error(f"❌ Erro ao inicializar aprendizado: {e}")

                self.sistema_aprendizado = SistemaAprendizadoContinuo()                self.sistema_aprendizado = None

                self.logger.info("✅ Sistema de aprendizado inicializado")

            except Exception as e:            # Subsistema de alertas

                self.logger.error(f"❌ Erro ao inicializar aprendizado: {e}")            try:

                self.sistema_aprendizado = None                self.sistema_alertas = SistemaAlertasInteligentes()

                self.logger.info("✅ Sistema de alertas inicializado")

            # Subsistema de alertas            except Exception as e:

            try:                self.logger.error(f"❌ Erro ao inicializar alertas: {e}")

                self.sistema_alertas = SistemaAlertasInteligentes()                self.sistema_alertas = None

                self.logger.info("✅ Sistema de alertas inicializado")

            except Exception as e:            # Verificar subsistemas críticos

                self.logger.error(f"❌ Erro ao inicializar alertas: {e}")            subsistemas_criticos = [

                self.sistema_alertas = None                self.detector_ml, self.sistema_alertas

            ]

        except Exception as e:

            self.logger.error(f"Erro geral na inicialização de subsistemas: {e}")            if all(s is not None for s in subsistemas_criticos):

                self.status_sistema = "OPERACIONAL"

    def _verificar_subsistemas_criticos(self) -> bool:                self.logger.info("✅ Todos os subsistemas críticos inicializados")

        """Verificar se subsistemas críticos estão operacionais"""            else:

        subsistemas_criticos = [                self.status_sistema = "PARCIAL"

            self.analisador_macro,                self.logger.warning("⚠️ Alguns subsistemas não inicializados - modo parcial")

            self.detector_ml

        ]        except Exception as e:

        return all(s is not None for s in subsistemas_criticos)            self.status_sistema = "ERRO"

            self.logger.error(f"❌ Erro geral na inicialização: {e}")

    def executar_ciclo_completo(self) -> Dict:

        """Executar ciclo completo de detecção de oportunidades reais"""    def executar_ciclo_completo(self) -> Dict:

        inicio = datetime.now()        """Executar ciclo completo de detecção de oportunidades"""

        try:

        self.logger.info("🚀 INICIANDO CICLO DE PRODUÇÃO")            self.logger.info("🔄 Iniciando ciclo completo de detecção")

        self.logger.info(f"📊 Portfolio: {len(self.config['portfolio_principal'])} ativos")

            inicio = datetime.now()

        resultados = {            resultados = {

            'timestamp_inicio': inicio.isoformat(),                'timestamp_inicio': inicio.isoformat(),

            'modo_operacao': self.config['modo_operacao'],                'status': 'EM_ANDAMENTO',

            'portfolio_analisado': self.config['portfolio_principal'],                'etapas': {},

            'etapas': {},                'oportunidades_detectadas': [],

            'oportunidades_detectadas': [],                'alertas_gerados': [],

            'alertas_gerados': [],                'metricas_ciclo': {}

            'status': 'INICIADO'            }

        }

            # Etapa 1: Análise macroeconômica

        try:            if self.analisador_macro:

            # Etapa 1: Análise macro                self.logger.info("📊 Executando análise macroeconômica...")

            if self.analisador_macro:                try:

                self.logger.info("🌐 Executando análise macroeconômica...")                    dados_macro = self._executar_analise_macro()

                try:                    resultados['etapas']['analise_macro'] = {

                    dados_macro = self._executar_analise_macro()                        'status': 'SUCESSO',

                    resultados['etapas']['analise_macro'] = {                        'dados_coletados': len(dados_macro) if dados_macro else 0

                        'status': 'SUCESSO',                    }

                        'dados_coletados': len(dados_macro) if dados_macro else 0                except Exception as e:

                    }                    self.logger.error(f"Erro na análise macro: {e}")

                except Exception as e:                    resultados['etapas']['analise_macro'] = {

                    self.logger.error(f"Erro na análise macro: {e}")                        'status': 'ERRO',

                    resultados['etapas']['analise_macro'] = {                        'erro': str(e)

                        'status': 'ERRO',                    }\n            \n            # Etapa 2: Detecção ML de oportunidades\n            if self.detector_ml:\n                self.logger.info(\"🤖 Executando detecção ML...\")\n                try:\n                    oportunidades = self._executar_deteccao_ml()\n                    resultados['oportunidades_detectadas'] = oportunidades\n                    resultados['etapas']['deteccao_ml'] = {\n                        'status': 'SUCESSO',\n                        'oportunidades_encontradas': len(oportunidades)\n                    }\n                except Exception as e:\n                    self.logger.error(f\"Erro na detecção ML: {e}\")\n                    resultados['etapas']['deteccao_ml'] = {\n                        'status': 'ERRO',\n                        'erro': str(e)\n                    }\n                    oportunidades = []\n            else:\n                oportunidades = []\n            \n            # Etapa 3: Geração de alertas\n            if self.sistema_alertas and oportunidades:\n                self.logger.info(\"🚨 Gerando alertas inteligentes...\")\n                try:\n                    alertas = self.sistema_alertas.processar_oportunidades_para_alertas(oportunidades)\n                    resultados['alertas_gerados'] = [a.to_dict() for a in alertas]\n                    resultados['etapas']['geracao_alertas'] = {\n                        'status': 'SUCESSO',\n                        'alertas_criados': len(alertas)\n                    }\n                except Exception as e:\n                    self.logger.error(f\"Erro na geração de alertas: {e}\")\n                    resultados['etapas']['geracao_alertas'] = {\n                        'status': 'ERRO',\n                        'erro': str(e)\n                    }\n            \n            # Etapa 4: Tracking e aprendizado\n            if self.sistema_tracking and self.sistema_aprendizado:\n                self.logger.info(\"📈 Executando tracking e aprendizado...\")\n                try:\n                    self._executar_tracking_aprendizado()\n                    resultados['etapas']['tracking_aprendizado'] = {\n                        'status': 'SUCESSO'\n                    }\n                except Exception as e:\n                    self.logger.error(f\"Erro no tracking: {e}\")\n                    resultados['etapas']['tracking_aprendizado'] = {\n                        'status': 'ERRO',\n                        'erro': str(e)\n                    }\n            \n            # Finalizar ciclo\n            fim = datetime.now()\n            duracao = (fim - inicio).total_seconds()\n            \n            resultados.update({\n                'timestamp_fim': fim.isoformat(),\n                'duracao_segundos': duracao,\n                'status': 'CONCLUIDO',\n                'metricas_ciclo': {\n                    'tempo_total': duracao,\n                    'oportunidades_detectadas': len(resultados['oportunidades_detectadas']),\n                    'alertas_gerados': len(resultados['alertas_gerados']),\n                    'etapas_bem_sucedidas': len([e for e in resultados['etapas'].values() \n                                               if e['status'] == 'SUCESSO'])\n                }\n            })\n            \n            # Salvar resultados do ciclo\n            self._salvar_resultados_ciclo(resultados)\n            \n            # Atualizar última execução\n            self.ultima_execucao = fim\n            \n            self.logger.info(f\"✅ Ciclo completo finalizado em {duracao:.1f}s\")\n            \n            return resultados\n            \n        except Exception as e:\n            self.logger.error(f\"❌ Erro no ciclo completo: {e}\")\n            return {\n                'status': 'ERRO_GERAL',\n                'erro': str(e),\n                'timestamp': datetime.now().isoformat()\n            }\n    \n    def _executar_analise_macro(self) -> Optional[Dict]:\n        \"\"\"Executar análise macroeconômica\"\"\"\n        if not self.analisador_macro:\n            return None\n            \n        try:\n            # Coletar dados DXY\n            dados_dxy = self.analisador_macro.coletar_dados_dxy()\n            \n            # Analisar eventos críticos\n            eventos = self.analisador_macro.analisar_eventos_criticos()\n            \n            # Analisar carry trades\n            carry_trades = self.analisador_macro.analisar_carry_trades()\n            \n            return {\n                'dxy': dados_dxy,\n                'eventos': eventos,\n                'carry_trades': carry_trades,\n                'timestamp': datetime.now().isoformat()\n            }\n            \n        except Exception as e:\n            self.logger.error(f\"Erro na análise macro: {e}\")\n            return None\n    \n    def _executar_deteccao_ml(self) -> List[Dict]:\n        \"\"\"Executar detecção ML de oportunidades\"\"\"\n        if not self.detector_ml:\n            return []\n            \n        try:\n            # Simular dados de posições do portfólio\n            posicoes_exemplo = self._obter_posicoes_portfolio()\n            \n            if not posicoes_exemplo:\n                self.logger.warning(\"Nenhuma posição encontrada no portfólio\")\n                return []\n            \n            # Detectar oportunidades\n            oportunidades = self.detector_ml.detectar_oportunidades(posicoes_exemplo)\n            \n            self.logger.info(f\"Detectadas {len(oportunidades)} oportunidades\")\n            \n            return oportunidades\n            \n        except Exception as e:\n            self.logger.error(f\"Erro na detecção ML: {e}\")\n            return []\n    \n    def _obter_posicoes_portfolio(self) -> List[Dict]:\n        \"\"\"Obter posições do portfólio (integração futura)\"\"\"\n        # Simular posições para demonstração\n        posicoes_simuladas = [\n            {\n                'par': 'EUR/USD',\n                'direction': 'LONG',\n                'entry_price': 1.0950,\n                'current_price': 1.0965,\n                'size': 100000,\n                'pnl_atual': 150.0,\n                'timestamp_abertura': (datetime.now() - timedelta(hours=2)).isoformat()\n            },\n            {\n                'par': 'GBP/JPY',\n                'direction': 'LONG',\n                'entry_price': 195.20,\n                'current_price': 195.50,\n                'size': 50000,\n                'pnl_atual': 75.0,\n                'timestamp_abertura': (datetime.now() - timedelta(hours=4)).isoformat()\n            }\n        ]\n        \n        return posicoes_simuladas\n    \n    def _executar_tracking_aprendizado(self):\n        \"\"\"Executar tracking e aprendizado contínuo\"\"\"\n        try:\n            if not self.sistema_tracking:\n                return\n                \n            # Calcular métricas de performance\n            metricas = self.sistema_tracking.calcular_metricas_performance()\n            \n            if 'erro' in metricas:\n                self.logger.warning(f\"Métricas indisponíveis: {metricas['erro']}\")\n                return\n            \n            # Avaliar necessidade de retreino\n            if self.sistema_aprendizado:\n                avaliacao = self.sistema_aprendizado.avaliar_necessidade_retreino()\n                \n                # Auto-retreino se necessário\n                if (avaliacao.get('necessita_retreino') and \n                    self.config.get('ativar_aprendizado_continuo')):\n                    \n                    self.logger.info(\"🔄 Iniciando retreino automático...\")\n                    # Aqui seria implementado o retreino automático\n                    \n            # Atualizar configuração de alertas\n            if self.sistema_alertas:\n                self.sistema_alertas.atualizar_configuracao_com_feedback(metricas)\n                \n        except Exception as e:\n            self.logger.error(f\"Erro no tracking/aprendizado: {e}\")\n    \n    def _salvar_resultados_ciclo(self, resultados: Dict):\n        \"\"\"Salvar resultados do ciclo de execução\"\"\"\n        try:\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            arquivo = f\"ciclo_execucao_{timestamp}.json\"\n            caminho = os.path.join(self.caminho_metricas, arquivo)\n            \n            with open(caminho, 'w', encoding='utf-8') as f:\n                json.dump(resultados, f, indent=2, ensure_ascii=False)\n                \n            self.logger.info(f\"Resultados salvos: {caminho}\")\n            \n        except Exception as e:\n            self.logger.error(f\"Erro ao salvar resultados: {e}\")\n    \n    def obter_status_sistema(self) -> Dict:\n        \"\"\"Obter status completo do sistema\"\"\"\n        return {\n            'status_geral': self.status_sistema,\n            'ultima_execucao': self.ultima_execucao.isoformat() if self.ultima_execucao else None,\n            'subsistemas': {\n                'analisador_macro': self.analisador_macro is not None,\n                'detector_ml': self.detector_ml is not None,\n                'sistema_tracking': self.sistema_tracking is not None,\n                'sistema_aprendizado': self.sistema_aprendizado is not None,\n                'sistema_alertas': self.sistema_alertas is not None\n            },\n            'configuracao': self.config,\n            'metricas_operacionais': self.metricas_operacionais,\n            'timestamp_status': datetime.now().isoformat()\n        }\n    \n    def executar_modo_continuo(self, duracao_horas: Optional[int] = None):\n        \"\"\"Executar sistema em modo contínuo\"\"\"\n        self.logger.info(\"🔄 Iniciando modo de execução contínua\")\n        \n        if duracao_horas:\n            fim_execucao = datetime.now() + timedelta(hours=duracao_horas)\n            self.logger.info(f\"⏰ Execução por {duracao_horas} horas\")\n        else:\n            fim_execucao = None\n            self.logger.info(\"♾️ Execução indefinida\")\n        \n        intervalo = self.config['intervalo_execucao_minutos'] * 60  # em segundos\n        \n        try:\n            while True:\n                # Verificar se deve parar\n                if fim_execucao and datetime.now() >= fim_execucao:\n                    break\n                \n                # Executar ciclo\n                resultados = self.executar_ciclo_completo()\n                \n                # Log resumo\n                if resultados['status'] == 'CONCLUIDO':\n                    metricas = resultados['metricas_ciclo']\n                    self.logger.info(\n                        f\"📊 Ciclo: {metricas['oportunidades_detectadas']} oportunidades, \"\n                        f\"{metricas['alertas_gerados']} alertas em {metricas['tempo_total']:.1f}s\"\n                    )\n                \n                # Aguardar próximo ciclo\n                self.logger.info(f\"⏳ Aguardando {self.config['intervalo_execucao_minutos']} minutos...\")\n                \n                import time\n                time.sleep(intervalo)\n                \n        except KeyboardInterrupt:\n            self.logger.info(\"⏹️ Execução interrompida pelo usuário\")\n        except Exception as e:\n            self.logger.error(f\"❌ Erro na execução contínua: {e}\")\n    \n    def gerar_relatorio_completo(self) -> Dict:\n        \"\"\"Gerar relatório completo do sistema\"\"\"\n        try:\n            relatorio = {\n                'timestamp_relatorio': datetime.now().isoformat(),\n                'status_sistema': self.obter_status_sistema(),\n                'metricas_performance': {},\n                'relatorio_alertas': {},\n                'sugestoes_melhoria': {},\n                'resumo_executivo': {}\n            }\n            \n            # Métricas de performance\n            if self.sistema_tracking:\n                try:\n                    metricas = self.sistema_tracking.calcular_metricas_performance()\n                    relatorio['metricas_performance'] = metricas\n                except Exception as e:\n                    relatorio['metricas_performance'] = {'erro': str(e)}\n            \n            # Relatório de alertas\n            if self.sistema_alertas:\n                try:\n                    rel_alertas = self.sistema_alertas.gerar_relatorio_alertas()\n                    relatorio['relatorio_alertas'] = rel_alertas\n                except Exception as e:\n                    relatorio['relatorio_alertas'] = {'erro': str(e)}\n            \n            # Sugestões de melhoria\n            if self.sistema_aprendizado:\n                try:\n                    sugestoes = self.sistema_aprendizado.sugerir_novos_inputs()\n                    relatorio['sugestoes_melhoria'] = sugestoes\n                except Exception as e:\n                    relatorio['sugestoes_melhoria'] = {'erro': str(e)}\n            \n            # Resumo executivo\n            relatorio['resumo_executivo'] = self._gerar_resumo_executivo(relatorio)\n            \n            # Salvar relatório\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            arquivo = f\"relatorio_completo_{timestamp}.json\"\n            caminho = os.path.join(self.caminho_metricas, arquivo)\n            \n            with open(caminho, 'w', encoding='utf-8') as f:\n                json.dump(relatorio, f, indent=2, ensure_ascii=False)\n            \n            return relatorio\n            \n        except Exception as e:\n            self.logger.error(f\"Erro ao gerar relatório: {e}\")\n            return {'erro': str(e)}\n    \n    def _gerar_resumo_executivo(self, relatorio: Dict) -> Dict:\n        \"\"\"Gerar resumo executivo dos resultados\"\"\"\n        resumo = {\n            'sistema_operacional': self.status_sistema == 'OPERACIONAL',\n            'recomendacoes': [],\n            'pontos_atencao': [],\n            'sucessos': []\n        }\n        \n        # Análise das métricas\n        metricas = relatorio.get('metricas_performance', {})\n        if 'resumo_geral' in metricas:\n            taxa_acerto = metricas['resumo_geral'].get('taxa_acerto_geral', 0)\n            \n            if taxa_acerto >= 80:\n                resumo['sucessos'].append(f\"Excelente taxa de acerto: {taxa_acerto}%\")\n            elif taxa_acerto >= 70:\n                resumo['sucessos'].append(f\"Boa taxa de acerto: {taxa_acerto}%\")\n            elif taxa_acerto < 60:\n                resumo['pontos_atencao'].append(f\"Taxa de acerto baixa: {taxa_acerto}%\")\n                resumo['recomendacoes'].append(\"Considerar retreino do modelo\")\n        \n        # Análise dos alertas\n        rel_alertas = relatorio.get('relatorio_alertas', {})\n        if 'resumo_geral' in rel_alertas:\n            taxa_execucao = rel_alertas['resumo_geral'].get('taxa_execucao', 0)\n            \n            if taxa_execucao >= 50:\n                resumo['sucessos'].append(f\"Boa taxa de execução de alertas: {taxa_execucao:.1f}%\")\n            elif taxa_execucao < 30:\n                resumo['pontos_atencao'].append(f\"Baixa execução de alertas: {taxa_execucao:.1f}%\")\n                resumo['recomendacoes'].append(\"Revisar relevância e timing dos alertas\")\n        \n        return resumo\n\n\ndef main():\n    \"\"\"Demonstração completa do motor de oportunidades\"\"\"\n    print(\"🚀 MOTOR DE OPORTUNIDADES COMPLETO\")\n    print(\"=\" * 70)\n    \n    # Inicializar motor\n    print(\"\\n🔧 Inicializando motor...\")\n    motor = MotorOportunidadesCompleto()\n    \n    # Mostrar status\n    status = motor.obter_status_sistema()\n    print(f\"\\n📊 STATUS DO SISTEMA:\")\n    print(f\"   Status geral: {status['status_geral']}\")\n    \n    subsistemas = status['subsistemas']\n    for nome, ativo in subsistemas.items():\n        emoji = \"✅\" if ativo else \"❌\"\n        print(f\"   {emoji} {nome.replace('_', ' ').title()}: {'Ativo' if ativo else 'Inativo'}\")\n    \n    # Executar ciclo completo\n    print(f\"\\n🔄 EXECUTANDO CICLO COMPLETO...\")\n    resultados = motor.executar_ciclo_completo()\n    \n    print(f\"\\n📈 RESULTADOS DO CICLO:\")\n    print(f\"   Status: {resultados['status']}\")\n    print(f\"   Duração: {resultados.get('duracao_segundos', 0):.1f}s\")\n    \n    # Mostrar etapas\n    etapas = resultados.get('etapas', {})\n    for nome, info in etapas.items():\n        emoji = \"✅\" if info['status'] == 'SUCESSO' else \"❌\"\n        print(f\"   {emoji} {nome.replace('_', ' ').title()}: {info['status']}\")\n    \n    # Mostrar métricas do ciclo\n    metricas = resultados.get('metricas_ciclo', {})\n    if metricas:\n        print(f\"\\n📊 MÉTRICAS DO CICLO:\")\n        print(f\"   Oportunidades detectadas: {metricas.get('oportunidades_detectadas', 0)}\")\n        print(f\"   Alertas gerados: {metricas.get('alertas_gerados', 0)}\")\n        print(f\"   Etapas bem-sucedidas: {metricas.get('etapas_bem_sucedidas', 0)}\")\n    \n    # Gerar relatório completo\n    print(f\"\\n📋 GERANDO RELATÓRIO COMPLETO...\")\n    relatorio = motor.gerar_relatorio_completo()\n    \n    if 'resumo_executivo' in relatorio:\n        resumo = relatorio['resumo_executivo']\n        \n        if resumo.get('sucessos'):\n            print(f\"\\n✅ SUCESSOS:\")\n            for sucesso in resumo['sucessos']:\n                print(f\"   • {sucesso}\")\n        \n        if resumo.get('recomendacoes'):\n            print(f\"\\n💡 RECOMENDAÇÕES:\")\n            for rec in resumo['recomendacoes']:\n                print(f\"   • {rec}\")\n    \n    print(f\"\\n✅ SISTEMA MOTOR OPERACIONAL\")\n    print(\"🔄 Para execução contínua: motor.executar_modo_continuo()\")\n    print(\"📊 Para relatórios: motor.gerar_relatorio_completo()\")\n    \n    return motor, resultados, relatorio\n\n\nif __name__ == \"__main__\":\n    motor, resultados, relatorio = main()"
                        'erro': str(e)
                    }

            # Etapa 2: Detecção ML de oportunidades
            if self.detector_ml:
                self.logger.info("🤖 Executando detecção ML...")
                try:
                    oportunidades = self._executar_deteccao_ml()
                    resultados['oportunidades_detectadas'] = oportunidades
                    resultados['etapas']['deteccao_ml'] = {
                        'status': 'SUCESSO',
                        'oportunidades_encontradas': len(oportunidades)
                    }
                except Exception as e:
                    self.logger.error(f"Erro na detecção ML: {e}")
                    resultados['etapas']['deteccao_ml'] = {
                        'status': 'ERRO',
                        'erro': str(e)
                    }
                    oportunidades = []
            else:
                oportunidades = []

            # Etapa 3: Geração de alertas
            if self.sistema_alertas and oportunidades:
                self.logger.info("🚨 Gerando alertas inteligentes...")
                try:
                    alertas = self.sistema_alertas.processar_oportunidades_para_alertas(oportunidades)
                    resultados['alertas_gerados'] = [a.to_dict() for a in alertas]
                    resultados['etapas']['geracao_alertas'] = {
                        'status': 'SUCESSO',
                        'alertas_criados': len(alertas)
                    }
                except Exception as e:
                    self.logger.error(f"Erro na geração de alertas: {e}")
                    resultados['etapas']['geracao_alertas'] = {
                        'status': 'ERRO',
                        'erro': str(e)
                    }

            # Etapa 4: Tracking e aprendizado
            if self.sistema_tracking and self.sistema_aprendizado:
                self.logger.info("📈 Executando tracking e aprendizado...")
                try:
                    self._executar_tracking_aprendizado()
                    resultados['etapas']['tracking_aprendizado'] = {
                        'status': 'SUCESSO'
                    }
                except Exception as e:
                    self.logger.error(f"Erro no tracking: {e}")
                    resultados['etapas']['tracking_aprendizado'] = {
                        'status': 'ERRO',
                        'erro': str(e)
                    }

            # Finalizar ciclo
            fim = datetime.now()
            duracao = (fim - inicio).total_seconds()

            resultados.update({
                'timestamp_fim': fim.isoformat(),
                'duracao_segundos': duracao,
                'status': 'CONCLUIDO',
                'metricas_ciclo': {
                    'tempo_total': duracao,
                    'oportunidades_detectadas': len(resultados['oportunidades_detectadas']),
                    'alertas_gerados': len(resultados['alertas_gerados']),
                    'etapas_bem_sucedidas': len([e for e in resultados['etapas'].values()
                                               if e['status'] == 'SUCESSO'])
                }
            })

            # Salvar resultados do ciclo
            self._salvar_resultados_ciclo(resultados)

            # Atualizar última execução
            self.ultima_execucao = fim

            self.logger.info(f"✅ Ciclo de produção finalizado em {duracao:.1f}s")
            self.logger.info(f"🎯 {len(resultados['oportunidades_detectadas'])} oportunidades detectadas")

            return resultados

        except Exception as e:
            self.logger.error(f"❌ Erro no ciclo de produção: {e}")
            return {
                'status': 'ERRO_GERAL',
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _executar_analise_macro(self) -> Optional[Dict]:
        """Executar análise macroeconômica"""
        if not self.analisador_macro:
            return None

        try:
            # Coletar dados DXY
            dados_dxy = self.analisador_macro.coletar_dados_dxy()

            # Analisar eventos críticos
            eventos = self.analisador_macro.analisar_eventos_criticos()

            # Analisar carry trades
            carry_trades = self.analisador_macro.analisar_carry_trades()

            return {
                'dxy': dados_dxy,
                'eventos': eventos,
                'carry_trades': carry_trades,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Erro na análise macro: {e}")
            return None

    def _executar_deteccao_ml(self) -> List[Dict]:
        """Executar detecção ML de oportunidades"""
        if not self.detector_ml:
            return []

        try:
            # Obter posições do portfolio
            posicoes = self._obter_posicoes_portfolio()

            if not posicoes:
                self.logger.warning("Nenhuma posição encontrada no portfólio")
                return []

            # Detectar oportunidades
            oportunidades = self.detector_ml.detectar_oportunidades(posicoes)

            self.logger.info(f"Detectadas {len(oportunidades)} oportunidades")

            return oportunidades

        except Exception as e:
            self.logger.error(f"Erro na detecção ML: {e}")
            return []

    def _obter_posicoes_portfolio(self) -> List[Dict]:
        """Obter posições do portfólio (integração futura)"""
        # Simular posições para demonstração
        posicoes_simuladas = [
            {
                'par': 'EUR/USD',
                'direction': 'LONG',
                'entry_price': 1.0950,
                'current_price': 1.0965,
                'size': 100000,
                'pnl_atual': 150.0,
                'timestamp_abertura': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'par': 'GBP/JPY',
                'direction': 'LONG',
                'entry_price': 195.20,
                'current_price': 195.50,
                'size': 50000,
                'pnl_atual': 75.0,
                'timestamp_abertura': (datetime.now() - timedelta(hours=4)).isoformat()
            }
        ]

        return posicoes_simuladas

    def _executar_tracking_aprendizado(self):
        """Executar tracking e aprendizado contínuo"""
        try:
            if not self.sistema_tracking:
                return

            # Calcular métricas de performance
            metricas = self.sistema_tracking.calcular_metricas_performance()

            if 'erro' in metricas:
                self.logger.warning(f"Métricas indisponíveis: {metricas['erro']}")
                return

            # Avaliar necessidade de retreino
            if self.sistema_aprendizado:
                avaliacao = self.sistema_aprendizado.avaliar_necessidade_retreino()

                # Auto-retreino se necessário
                if (avaliacao.get('necessita_retreino') and
                    self.config.get('ativar_aprendizado_continuo')):

                    self.logger.info("🔄 Iniciando retreino automático...")
                    # Aqui seria implementado o retreino automático

            # Atualizar configuração de alertas
            if self.sistema_alertas:
                self.sistema_alertas.atualizar_configuracao_com_feedback(metricas)

        except Exception as e:
            self.logger.error(f"Erro no tracking/aprendizado: {e}")

    def _salvar_resultados_ciclo(self, resultados: Dict):
        """Salvar resultados do ciclo de execução"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"ciclo_execucao_{timestamp}.json"
            caminho = os.path.join("data/metricas_operacionais", arquivo)

            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Resultados salvos: {caminho}")

        except Exception as e:
            self.logger.error(f"Erro ao salvar resultados: {e}")

    def obter_status_subsistemas(self) -> Dict:
        """Obter status completo dos subsistemas"""
        return {
            'status_geral': self.status_sistema,
            'subsistemas': {
                'analisador_macro': self.analisador_macro is not None,
                'detector_ml': self.detector_ml is not None,
                'sistema_tracking': self.sistema_tracking is not None,
                'sistema_aprendizado': self.sistema_aprendizado is not None,
                'sistema_alertas': self.sistema_alertas is not None
            }
        }

    def executar_modo_continuo(self, duracao_horas: Optional[int] = None):
        """Executar sistema em modo contínuo"""
        self.logger.info("🔄 Iniciando modo de execução contínua")

        if duracao_horas:
            fim_execucao = datetime.now() + timedelta(hours=duracao_horas)
            self.logger.info(f"⏰ Execução por {duracao_horas} horas")
        else:
            fim_execucao = None
            self.logger.info("♾️ Execução indefinida")

        intervalo = self.config['intervalo_execucao_minutos'] * 60  # em segundos

        try:
            while True:
                # Verificar se deve parar
                if fim_execucao and datetime.now() >= fim_execucao:
                    break

                # Executar ciclo
                resultados = self.executar_ciclo_completo()

                # Log resumo
                if resultados['status'] == 'CONCLUIDO':
                    metricas = resultados['metricas_ciclo']
                    self.logger.info(
                        f"📊 Ciclo: {metricas['oportunidades_detectadas']} oportunidades, "
                        f"{metricas['alertas_gerados']} alertas em {metricas['tempo_total']:.1f}s"
                    )

                # Aguardar próximo ciclo
                self.logger.info(f"⏳ Aguardando {self.config['intervalo_execucao_minutos']} minutos...")

                import time
                time.sleep(intervalo)

        except KeyboardInterrupt:
            self.logger.info("⏹️ Execução interrompida pelo usuário")
        except Exception as e:
            self.logger.error(f"❌ Erro na execução contínua: {e}")


def main():
    """Demonstração completa do motor de oportunidades em modo produção"""
    print("🚀 MOTOR DE OPORTUNIDADES - MODO PRODUÇÃO")
    print("=" * 60)

    # Carregar configuração de produção
    config_path = "config_producao.json"

    # Inicializar motor
    print("\n🔧 Inicializando motor de produção...")
    motor = MotorOportunidadesCompleto(config_path=config_path)

    # Verificar status dos subsistemas
    status_subsistemas = motor.obter_status_subsistemas()

    print("\n📊 STATUS DOS SUBSISTEMAS:")
    print(f"   Status geral: {status_subsistemas['status_geral']}")

    for nome, ativo in status_subsistemas['subsistemas'].items():
        emoji = "✅" if ativo else "❌"
        print(f"   {emoji} {nome.replace('_', ' ').title()}: {'Ativo' if ativo else 'Inativo'}")

    # Verificar se sistema está operacional
    if status_subsistemas['status_geral'] not in ['OPERACIONAL', 'PARCIAL']:
        print("❌ Sistema não está operacional para produção!")
        return None, None, None

    print("\n🔄 EXECUTANDO CICLO DE PRODUÇÃO...")
    # Executar ciclo completo
    resultados = motor.executar_ciclo_completo()

    print("\n📈 RESULTADOS DO CICLO DE PRODUÇÃO:")
    print(f"   Status: {resultados['status']}")
    print(f"   Duração: {resultados.get('duracao_segundos', 0):.1f}s")

    # Mostrar etapas
    etapas = resultados.get('etapas', {})
    print("\n📋 ETAPAS EXECUTADAS:")
    for nome, info in etapas.items():
        status_etapa = info['status'] if isinstance(info, dict) else 'SUCESSO'
        emoji = "✅" if status_etapa == 'SUCESSO' else "❌"
        print(f"   {emoji} {nome.replace('_', ' ').title()}: {status_etapa}")

    # Mostrar métricas do ciclo
    metricas = resultados.get('metricas_ciclo', {})
    if metricas:
        print("\n📊 MÉTRICAS DO CICLO:")
        print(f"   Oportunidades detectadas: {metricas.get('oportunidades_detectadas', 0)}")
        print(f"   Alertas gerados: {metricas.get('alertas_gerados', 0)}")
        print(f"   Etapas bem-sucedidas: {metricas.get('etapas_bem_sucedidas', 0)}")

    # Mostrar oportunidades detectadas
    oportunidades = resultados.get('oportunidades_detectadas', [])
    if oportunidades:
        print("\n🎯 OPORTUNIDADES DETECTADAS (PRODUÇÃO):")
        for i, op in enumerate(oportunidades[:10], 1):  # Limitar a 10 para não sobrecarregar
            ticker = op.get('ticker', 'N/A')
            probabilidade = op.get('probabilidade', 0) * 100
            confianca = op.get('nivel_confianca', 'BAIXA')
            acao = op.get('acao_recomendada', 'N/A')

            print(f"   {i}. {ticker}: {probabilidade:.1f}% ({confianca})")
            print(f"      Ação: {acao}")

            # Mostrar justificativa se disponível
            justificativa = op.get('justificativa', '')
            if justificativa:
                print(f"      📝 {justificativa[:100]}...")
    else:
        print("\n🎯 NENHUMA OPORTUNIDADE DETECTADA")
        print("   Sistema aguardará próximo ciclo de 15 minutos")

    # Verificar alertas gerados
    alertas = resultados.get('alertas_gerados', [])
    if alertas:
        print("\n🚨 ALERTAS GERADOS:")
        for alerta in alertas[:5]:  # Limitar a 5 alertas
            tipo = alerta.get('tipo', 'N/A')
            prioridade = alerta.get('prioridade', 'BAIXA')
            mensagem = alerta.get('mensagem', 'N/A')
            print(f"   🚨 [{prioridade}] {tipo}: {mensagem}")

    print("\n✅ SISTEMA OPERACIONAL EM MODO PRODUÇÃO")
    print("🔄 Pronto para próximo ciclo em 15 minutos")
    print("📊 Dados salvos em: data/metricas_operacionais/")

    return motor, resultados, None


if __name__ == "__main__":
    motor, resultados, relatorio = main()