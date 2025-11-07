#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Alertas Simplificado - Notificações Multi-Canal
Implementa notificações via console, webhook, arquivo e Telegram (sem email)
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3

@dataclass
class AlertaOportunidade:
    """Estrutura de alerta de oportunidade"""
    id_alerta: str
    timestamp: datetime
    ativo: str
    acao_recomendada: str
    probabilidade_sucesso: int
    confianca: int
    preco_entrada: float
    preco_alvo: float
    stop_loss: float
    risk_reward: float
    justificativa_tecnica: str
    justificativa_macro: str
    catalysts: List[str]
    timeframe: str
    canal_origem: str
    prioridade: str  # BAIXA, MEDIA, ALTA, CRITICA

class SistemaAlertasSimplificado:
    """
    Sistema de alertas multi-canal simplificado

    Canais suportados:
    - Console/Log com cores
    - Webhook HTTP (Discord, Zapier, etc.)
    - Telegram Bot (opcional)
    - Arquivo de alertas estruturado
    - Histórico em SQLite
    """

    def __init__(self, config_path: str = "config/alertas_config.json"):
        self.config_path = config_path
        self.db_path = "data/alertas/historico_alertas.db"
        self.alertas_file = "data/alertas/alertas_ativos.json"

        # Criar diretórios necessários primeiro
        os.makedirs("data/alertas", exist_ok=True)
        os.makedirs("config", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

        # Inicializar componentes após criar diretórios
        self.logger = self._setup_logger()
        self.carregar_configuracao()
        self.inicializar_banco_dados()

        # Rate limiting (max alertas por minuto)
        self.rate_limits = {
            'console': 100,
            'webhook': 20,
            'telegram': 10,
            'arquivo': 1000
        }

        # Contadores
        self.contadores_minuto = {}
        self.ultimo_reset = datetime.now()

    def _setup_logger(self) -> logging.Logger:
        """Configurar logger com cores para console"""
        logger = logging.getLogger('SistemaAlertas')
        logger.setLevel(logging.INFO)

        # Limpar handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Handler para arquivo detalhado
        file_handler = logging.FileHandler('logs/alertas.log', encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Handler para console com cores
        console_handler = logging.StreamHandler()

        class ColoredFormatter(logging.Formatter):
            """Formatter com cores ANSI"""

            COLORS = {
                'DEBUG': '\033[36m',      # Cyan
                'INFO': '\033[32m',       # Verde
                'WARNING': '\033[33m',    # Amarelo
                'ERROR': '\033[31m',      # Vermelho
                'CRITICAL': '\033[35m'    # Magenta
            }
            RESET = '\033[0m'

            def format(self, record):
                log_color = self.COLORS.get(record.levelname, '')
                record.levelname = f"{log_color}{record.levelname}{self.RESET}"
                record.msg = f"{log_color}{record.msg}{self.RESET}"
                return super().format(record)

        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def carregar_configuracao(self):
        """Carregar configurações dos canais"""

        config_padrao = {
            "console": {
                "ativo": True,
                "filtros": {
                    "probabilidade_min": 50,
                    "confianca_min": 45,
                    "risco_reward_min": 0.5,
                    "ativos_permitidos": [],
                    "acoes_permitidas": ["COMPRA", "VENDA", "OBSERVAR"],
                    "prioridades_permitidas": ["BAIXA", "MEDIA", "ALTA", "CRITICA"]
                }
            },
            "webhook": {
                "ativo": True,
                "urls": [
                    "https://httpbin.org/post"  # URL de teste
                ],
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "filtros": {
                    "probabilidade_min": 60,
                    "confianca_min": 55,
                    "risco_reward_min": 1.0,
                    "ativos_permitidos": [],
                    "acoes_permitidas": ["COMPRA", "VENDA"],
                    "prioridades_permitidas": ["MEDIA", "ALTA", "CRITICA"]
                }
            },
            "telegram": {
                "ativo": False,  # Desabilitado por padrão
                "bot_token": "",
                "chat_ids": [],
                "filtros": {
                    "probabilidade_min": 75,
                    "confianca_min": 70,
                    "risco_reward_min": 2.0,
                    "ativos_permitidos": [],
                    "acoes_permitidas": ["COMPRA", "VENDA"],
                    "prioridades_permitidas": ["ALTA", "CRITICA"]
                }
            },
            "arquivo": {
                "ativo": True,
                "formato": "json",  # json ou txt
                "max_alertas": 1000,
                "filtros": {
                    "probabilidade_min": 40,
                    "confianca_min": 35,
                    "risco_reward_min": 0.0,
                    "ativos_permitidos": [],
                    "acoes_permitidas": ["COMPRA", "VENDA", "OBSERVAR"],
                    "prioridades_permitidas": ["BAIXA", "MEDIA", "ALTA", "CRITICA"]
                }
            }
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_carregada = json.load(f)
                # Mesclar com padrão para garantir compatibilidade
                self.config = {**config_padrao, **config_carregada}
            else:
                self.config = config_padrao
                self.salvar_configuracao()

        except Exception as e:
            self.logger.error(f"❌ Erro carregando configuração: {e}")
            self.config = config_padrao

    def salvar_configuracao(self):
        """Salvar configuração no arquivo"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Erro salvando configuração: {e}")

    def inicializar_banco_dados(self):
        """Inicializar banco de dados para histórico"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas_enviados (
                    id_alerta TEXT PRIMARY KEY,
                    timestamp_envio DATETIME,
                    ativo TEXT,
                    acao_recomendada TEXT,
                    probabilidade_sucesso INTEGER,
                    confianca INTEGER,
                    preco_entrada REAL,
                    preco_alvo REAL,
                    stop_loss REAL,
                    risk_reward REAL,
                    canal_origem TEXT,
                    prioridade TEXT,
                    canais_enviados TEXT,  -- JSON
                    status_entrega TEXT,   -- JSON
                    justificativa_tecnica TEXT,
                    justificativa_macro TEXT
                )
            ''')

            # Índices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas_enviados(timestamp_envio)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alertas_ativo ON alertas_enviados(ativo)')

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"❌ Erro inicializando banco: {e}")

    def verificar_rate_limit(self, canal: str) -> bool:
        """Verificar rate limit"""
        agora = datetime.now()

        # Reset a cada minuto
        if (agora - self.ultimo_reset).seconds >= 60:
            self.contadores_minuto = {}
            self.ultimo_reset = agora

        count_atual = self.contadores_minuto.get(canal, 0)
        limite = self.rate_limits.get(canal, 10)

        if count_atual >= limite:
            return False

        self.contadores_minuto[canal] = count_atual + 1
        return True

    def filtrar_alerta(self, alerta: AlertaOportunidade, canal: str) -> bool:
        """Verificar se alerta passa pelos filtros do canal"""

        if canal not in self.config:
            return False

        if not self.config[canal].get('ativo', False):
            return False

        filtros = self.config[canal].get('filtros', {})

        # Aplicar filtros
        if alerta.probabilidade_sucesso < filtros.get('probabilidade_min', 0):
            return False

        if alerta.confianca < filtros.get('confianca_min', 0):
            return False

        if alerta.risk_reward < filtros.get('risco_reward_min', 0):
            return False

        ativos_permitidos = filtros.get('ativos_permitidos', [])
        if ativos_permitidos and alerta.ativo not in ativos_permitidos:
            return False

        acoes_permitidas = filtros.get('acoes_permitidas', [])
        if acoes_permitidas and alerta.acao_recomendada not in acoes_permitidas:
            return False

        prioridades_permitidas = filtros.get('prioridades_permitidas', [])
        if prioridades_permitidas and alerta.prioridade not in prioridades_permitidas:
            return False

        return True

    def enviar_console(self, alerta: AlertaOportunidade) -> bool:
        """Enviar alerta colorido para console"""
        try:
            if not self.verificar_rate_limit('console'):
                return False

            # Emojis e cores por ação
            config_visual = {
                'COMPRA': {'emoji': '🟢 📈', 'cor': '\033[32m'},      # Verde
                'VENDA': {'emoji': '🔴 📉', 'cor': '\033[31m'},       # Vermelho
                'OBSERVAR': {'emoji': '🟡 👁️', 'cor': '\033[33m'}    # Amarelo
            }

            visual = config_visual.get(alerta.acao_recomendada,
                                     {'emoji': '⚪', 'cor': '\033[37m'})

            # Cores por prioridade
            cor_prioridade = {
                'CRITICA': '\033[95m',   # Magenta brilhante
                'ALTA': '\033[91m',      # Vermelho brilhante
                'MEDIA': '\033[93m',     # Amarelo brilhante
                'BAIXA': '\033[94m'      # Azul brilhante
            }.get(alerta.prioridade, '\033[37m')

            reset = '\033[0m'

            # Mensagem formatada
            print(f"\n{'='*80}")
            print(f"{visual['cor']}🚨 ALERTA DE OPORTUNIDADE {visual['emoji']}{reset}")
            print(f"{'='*80}")

            print(f"{cor_prioridade}📊 {alerta.ativo} - {alerta.acao_recomendada} "
                  f"[{alerta.prioridade}]{reset}")

            print(f"\n💎 MÉTRICAS:")
            print(f"   Probabilidade: {visual['cor']}{alerta.probabilidade_sucesso}%{reset}")
            print(f"   Confiança: {visual['cor']}{alerta.confianca}%{reset}")
            print(f"   Risk/Reward: {visual['cor']}{alerta.risk_reward:.2f}{reset}")
            print(f"   Timeframe: {alerta.timeframe}")

            print(f"\n💰 PREÇOS:")
            print(f"   Entrada: ${alerta.preco_entrada:.5f}")
            print(f"   Alvo: {visual['cor']}${alerta.preco_alvo:.5f}{reset}")
            print(f"   Stop: ❌ ${alerta.stop_loss:.5f}")

            print(f"\n💡 CATALISADORES:")
            for i, catalyst in enumerate(alerta.catalysts[:3], 1):
                print(f"   {i}. {catalyst}")

            print(f"\n📈 TÉCNICA: {alerta.justificativa_tecnica[:100]}...")
            print(f"🌐 MACRO: {alerta.justificativa_macro[:100]}...")

            print(f"\n⏰ {alerta.timestamp.strftime('%H:%M:%S')} | "
                  f"ID: {alerta.id_alerta[:8]} | Origem: {alerta.canal_origem}")
            print(f"{'='*80}\n")

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro console: {e}")
            return False

    def enviar_webhook(self, alerta: AlertaOportunidade) -> bool:
        """Enviar via webhook"""
        try:
            if not self.verificar_rate_limit('webhook'):
                return False

            config_webhook = self.config['webhook']

            # Payload formatado
            payload = {
                'timestamp': alerta.timestamp.isoformat(),
                'sistema': 'AgentEspecialistaMercadoFinanceiro',
                'tipo': 'alerta_oportunidade',
                'alerta': {
                    'id': alerta.id_alerta,
                    'ativo': alerta.ativo,
                    'acao': alerta.acao_recomendada,
                    'probabilidade': alerta.probabilidade_sucesso,
                    'confianca': alerta.confianca,
                    'preco_entrada': alerta.preco_entrada,
                    'preco_alvo': alerta.preco_alvo,
                    'stop_loss': alerta.stop_loss,
                    'risk_reward': alerta.risk_reward,
                    'timeframe': alerta.timeframe,
                    'prioridade': alerta.prioridade,
                    'justificativa_tecnica': alerta.justificativa_tecnica,
                    'justificativa_macro': alerta.justificativa_macro,
                    'catalysts': alerta.catalysts
                }
            }

            urls = config_webhook.get('urls', [])
            headers = config_webhook.get('headers', {})
            timeout = config_webhook.get('timeout', 10)

            sucessos = 0
            for url in urls:
                try:
                    response = requests.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=timeout
                    )

                    if response.status_code in [200, 201, 202]:
                        sucessos += 1

                except requests.exceptions.RequestException as e:
                    self.logger.error(f"❌ Webhook {url}: {e}")

            if sucessos > 0:
                self.logger.info(f"✅ Webhook: {alerta.ativo} -> {sucessos}/{len(urls)} URLs")
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Erro webhook: {e}")
            return False

    def enviar_telegram(self, alerta: AlertaOportunidade) -> bool:
        """Enviar via Telegram Bot (se configurado)"""
        try:
            if not self.verificar_rate_limit('telegram'):
                return False

            config_telegram = self.config['telegram']

            bot_token = os.getenv('TELEGRAM_BOT_TOKEN', config_telegram.get('bot_token', ''))

            if not bot_token:
                return False

            # Mensagem formatada
            emoji_acao = {
                'COMPRA': '🟢 📈',
                'VENDA': '🔴 📉',
                'OBSERVAR': '🟡 👁️'
            }.get(alerta.acao_recomendada, '⚪')

            mensagem = f"""🚨 *ALERTA DE OPORTUNIDADE*

{emoji_acao} *{alerta.ativo}* - {alerta.acao_recomendada}

📊 *Métricas:*
• Probabilidade: *{alerta.probabilidade_sucesso}%*
• Confiança: *{alerta.confianca}%*
• R/R: *{alerta.risk_reward:.2f}*

💰 *Preços:*
• Entrada: `${alerta.preco_entrada:.5f}`
• Alvo: `${alerta.preco_alvo:.5f}`
• Stop: `${alerta.stop_loss:.5f}`

⏰ {alerta.timestamp.strftime('%H:%M:%S')} | {alerta.prioridade}"""

            chat_ids = config_telegram.get('chat_ids', [])
            sucessos = 0

            for chat_id in chat_ids:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

                payload = {
                    'chat_id': chat_id,
                    'text': mensagem,
                    'parse_mode': 'Markdown'
                }

                response = requests.post(url, json=payload, timeout=10)

                if response.status_code == 200:
                    sucessos += 1

            return sucessos > 0

        except Exception as e:
            self.logger.error(f"❌ Erro Telegram: {e}")
            return False

    def enviar_arquivo(self, alerta: AlertaOportunidade) -> bool:
        """Salvar alerta em arquivo estruturado"""
        try:
            if not self.verificar_rate_limit('arquivo'):
                return False

            # Carregar alertas existentes
            alertas_existentes = []
            if os.path.exists(self.alertas_file):
                with open(self.alertas_file, 'r', encoding='utf-8') as f:
                    alertas_existentes = json.load(f)

            # Adicionar novo alerta
            novo_alerta = {
                'id_alerta': alerta.id_alerta,
                'timestamp': alerta.timestamp.isoformat(),
                'ativo': alerta.ativo,
                'acao_recomendada': alerta.acao_recomendada,
                'probabilidade_sucesso': alerta.probabilidade_sucesso,
                'confianca': alerta.confianca,
                'preco_entrada': alerta.preco_entrada,
                'preco_alvo': alerta.preco_alvo,
                'stop_loss': alerta.stop_loss,
                'risk_reward': alerta.risk_reward,
                'timeframe': alerta.timeframe,
                'prioridade': alerta.prioridade,
                'justificativa_tecnica': alerta.justificativa_tecnica,
                'justificativa_macro': alerta.justificativa_macro,
                'catalysts': alerta.catalysts,
                'canal_origem': alerta.canal_origem
            }

            alertas_existentes.insert(0, novo_alerta)  # Mais recente primeiro

            # Limitar número de alertas
            max_alertas = self.config['arquivo']['filtros'].get('max_alertas', 1000)
            alertas_existentes = alertas_existentes[:max_alertas]

            # Salvar arquivo
            with open(self.alertas_file, 'w', encoding='utf-8') as f:
                json.dump(alertas_existentes, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro arquivo: {e}")
            return False

    def enviar_alerta(self, alerta: AlertaOportunidade) -> Dict[str, bool]:
        """Método principal - enviar para todos os canais"""

        resultados = {
            'console': False,
            'webhook': False,
            'telegram': False,
            'arquivo': False
        }

        canais_enviados = []

        # Tentar cada canal
        for canal in resultados.keys():
            if self.filtrar_alerta(alerta, canal):
                try:
                    if canal == 'console':
                        success = self.enviar_console(alerta)
                    elif canal == 'webhook':
                        success = self.enviar_webhook(alerta)
                    elif canal == 'telegram':
                        success = self.enviar_telegram(alerta)
                    elif canal == 'arquivo':
                        success = self.enviar_arquivo(alerta)

                    resultados[canal] = success
                    if success:
                        canais_enviados.append(canal)

                except Exception as e:
                    self.logger.error(f"❌ Erro {canal}: {e}")

        # Salvar histórico
        self._salvar_historico(alerta, canais_enviados, resultados)

        return resultados

    def _salvar_historico(self, alerta: AlertaOportunidade, canais_enviados: List[str], status_entrega: Dict[str, bool]):
        """Salvar no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO alertas_enviados
                (id_alerta, timestamp_envio, ativo, acao_recomendada, probabilidade_sucesso,
                 confianca, preco_entrada, preco_alvo, stop_loss, risk_reward, canal_origem,
                 prioridade, canais_enviados, status_entrega, justificativa_tecnica, justificativa_macro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alerta.id_alerta, alerta.timestamp, alerta.ativo, alerta.acao_recomendada,
                alerta.probabilidade_sucesso, alerta.confianca, alerta.preco_entrada,
                alerta.preco_alvo, alerta.stop_loss, alerta.risk_reward, alerta.canal_origem,
                alerta.prioridade, json.dumps(canais_enviados), json.dumps(status_entrega),
                alerta.justificativa_tecnica, alerta.justificativa_macro
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"❌ Erro salvando histórico: {e}")

# Exemplo e teste
def testar_sistema_alertas():
    """Testar o sistema com alertas de exemplo"""

    print("🚀 Testando Sistema de Alertas Simplificado...")

    sistema = SistemaAlertasSimplificado()

    # Alerta de exemplo 1 - COMPRA
    alerta1 = AlertaOportunidade(
        id_alerta=f"ALT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_001",
        timestamp=datetime.now(),
        ativo="AAPL",
        acao_recomendada="COMPRA",
        probabilidade_sucesso=85,
        confianca=78,
        preco_entrada=150.25,
        preco_alvo=162.00,
        stop_loss=145.50,
        risk_reward=2.47,
        justificativa_tecnica="Rompimento resistência $150 com volume, RSI 65 confirma momentum positivo",
        justificativa_macro="VIX baixo 19.5, ambiente favorável growth stocks, Fed dovish suporta múltiplos",
        catalysts=[
            "Earnings season próximo com expectativas positivas",
            "Lançamento produtos Q4",
            "Ambiente macro favorável VIX baixo"
        ],
        timeframe="MÉDIO_PRAZO (2-4 semanas)",
        canal_origem="AnaliseMacroEspecialista",
        prioridade="ALTA"
    )

    # Alerta de exemplo 2 - VENDA
    alerta2 = AlertaOportunidade(
        id_alerta=f"ALT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_002",
        timestamp=datetime.now(),
        ativo="NVDA",
        acao_recomendada="VENDA",
        probabilidade_sucesso=72,
        confianca=65,
        preco_entrada=145.80,
        preco_alvo=135.20,
        stop_loss=150.30,
        risk_reward=2.35,
        justificativa_tecnica="Divergência bearish no RSI, resistência forte em $146",
        justificativa_macro="Taxas elevadas pressionam growth, rotação para value",
        catalysts=[
            "Pressão regulatória em AI",
            "Taxas Treasury 10Y > 4%",
            "Rotação setorial para value"
        ],
        timeframe="CURTO_PRAZO (3-10 dias)",
        canal_origem="AnalisePortfolioEspecialista",
        prioridade="MEDIA"
    )

    # Enviar alertas
    print(f"\n📨 Enviando alertas...")

    resultado1 = sistema.enviar_alerta(alerta1)
    resultado2 = sistema.enviar_alerta(alerta2)

    # Resumo
    print(f"\n📊 RESUMO DE ENVIOS:")
    print(f"   Alerta 1 (AAPL): {sum(resultado1.values())}/4 canais")
    print(f"   Alerta 2 (NVDA): {sum(resultado2.values())}/4 canais")

    return sistema

if __name__ == "__main__":
    sistema = testar_sistema_alertas()
    print(f"\n✅ Sistema de Alertas Simplificado implementado!")
    print(f"   Configuração: {sistema.config_path}")
    print(f"   Histórico: {sistema.db_path}")
    print(f"   Alertas ativos: {sistema.alertas_file}")