#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Alertas Avançado - Notificações Multi-Canal
Implementa notificações via email, Telegram, webhook e console com filtros personalizáveis
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

@dataclass
class ConfiguracaoCanal:
    """Configuração de canal de notificação"""
    ativo: bool
    filtro_probabilidade_min: int
    filtro_confianca_min: int
    filtro_risco_reward_min: float
    filtro_ativos: List[str]  # Lista de ativos permitidos (vazio = todos)
    filtro_acoes: List[str]   # COMPRA, VENDA, OBSERVAR
    filtro_prioridades: List[str]  # BAIXA, MEDIA, ALTA, CRITICA

class SistemaAlertasAvancado:
    """
    Sistema de alertas multi-canal com filtros personalizáveis

    Recursos:
    - Email SMTP com anexos
    - Telegram Bot
    - Webhooks HTTP
    - Console/Log local
    - Filtros granulares por canal
    - Histórico de alertas
    - Rate limiting
    - Templates customizáveis
    """

    def __init__(self, config_path: str = "config/alertas_config.json"):
        self.config_path = config_path
        self.db_path = "data/alertas/historico_alertas.db"
        self.logger = self._setup_logger()

        # Criar diretórios necessários
        os.makedirs("data/alertas", exist_ok=True)
        os.makedirs("config", exist_ok=True)

        self.carregar_configuracao()
        self.inicializar_banco_dados()

        # Rate limiting (max alertas por minuto por canal)
        self.rate_limits = {
            'email': 5,
            'telegram': 10,
            'webhook': 20,
            'console': 100
        }

        # Contadores de rate limiting
        self.contadores_minuto = {}
        self.ultimo_reset = datetime.now()

    def _setup_logger(self) -> logging.Logger:
        """Configurar logger para alertas"""
        logger = logging.getLogger('SistemaAlertas')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # Handler para arquivo
            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler('logs/alertas.log')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            # Handler para console
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        return logger

    def carregar_configuracao(self):
        """Carregar configurações dos canais"""

        # Configuração padrão
        config_padrao = {
            "email": {
                "ativo": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "usuario": "",  # Configurar via variável de ambiente
                "senha": "",    # Configurar via variável de ambiente
                "destinatarios": [],
                "filtros": {
                    "probabilidade_min": 70,
                    "confianca_min": 65,
                    "risco_reward_min": 1.5,
                    "ativos_permitidos": [],
                    "acoes_permitidas": ["COMPRA", "VENDA"],
                    "prioridades_permitidas": ["MEDIA", "ALTA", "CRITICA"]
                }
            },
            "telegram": {
                "ativo": True,
                "bot_token": "",  # Configurar via variável de ambiente
                "chat_ids": [],   # Lista de chat IDs
                "filtros": {
                    "probabilidade_min": 75,
                    "confianca_min": 70,
                    "risco_reward_min": 2.0,
                    "ativos_permitidos": [],
                    "acoes_permitidas": ["COMPRA", "VENDA"],
                    "prioridades_permitidas": ["ALTA", "CRITICA"]
                }
            },
            "webhook": {
                "ativo": True,
                "urls": [],  # Lista de URLs para POST
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "filtros": {
                    "probabilidade_min": 60,
                    "confianca_min": 55,
                    "risco_reward_min": 1.0,
                    "ativos_permitidos": [],
                    "acoes_permitidas": ["COMPRA", "VENDA", "OBSERVAR"],
                    "prioridades_permitidas": ["BAIXA", "MEDIA", "ALTA", "CRITICA"]
                }
            },
            "console": {
                "ativo": True,
                "nivel_log": "INFO",
                "filtros": {
                    "probabilidade_min": 50,
                    "confianca_min": 45,
                    "risco_reward_min": 0.5,
                    "ativos_permitidos": [],
                    "acoes_permitidas": ["COMPRA", "VENDA", "OBSERVAR"],
                    "prioridades_permitidas": ["BAIXA", "MEDIA", "ALTA", "CRITICA"]
                }
            }
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
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
                    canais_enviados TEXT,  -- JSON com lista de canais
                    status_entrega TEXT    -- JSON com status por canal
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estatisticas_alertas (
                    data_hora DATETIME,
                    canal TEXT,
                    total_enviados INTEGER,
                    total_filtrados INTEGER,
                    taxa_sucesso_entrega REAL
                )
            ''')

            # Índices para performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas_enviados(timestamp_envio)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alertas_ativo ON alertas_enviados(ativo)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alertas_canal ON alertas_enviados(canal_origem)')

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"❌ Erro inicializando banco de dados: {e}")

    def verificar_rate_limit(self, canal: str) -> bool:
        """Verificar se canal está dentro do rate limit"""
        agora = datetime.now()

        # Reset contadores a cada minuto
        if (agora - self.ultimo_reset).seconds >= 60:
            self.contadores_minuto = {}
            self.ultimo_reset = agora

        # Verificar limite do canal
        count_atual = self.contadores_minuto.get(canal, 0)
        limite = self.rate_limits.get(canal, 10)

        if count_atual >= limite:
            self.logger.warning(f"⚠️ Rate limit atingido para {canal}: {count_atual}/{limite}")
            return False

        # Incrementar contador
        self.contadores_minuto[canal] = count_atual + 1
        return True

    def filtrar_alerta(self, alerta: AlertaOportunidade, canal: str) -> bool:
        """Verificar se alerta passa pelos filtros do canal"""

        if canal not in self.config:
            return False

        if not self.config[canal].get('ativo', False):
            return False

        filtros = self.config[canal].get('filtros', {})

        # Filtro de probabilidade
        if alerta.probabilidade_sucesso < filtros.get('probabilidade_min', 0):
            return False

        # Filtro de confiança
        if alerta.confianca < filtros.get('confianca_min', 0):
            return False

        # Filtro de risk/reward
        if alerta.risk_reward < filtros.get('risco_reward_min', 0):
            return False

        # Filtro de ativos
        ativos_permitidos = filtros.get('ativos_permitidos', [])
        if ativos_permitidos and alerta.ativo not in ativos_permitidos:
            return False

        # Filtro de ações
        acoes_permitidas = filtros.get('acoes_permitidas', [])
        if acoes_permitidas and alerta.acao_recomendada not in acoes_permitidas:
            return False

        # Filtro de prioridades
        prioridades_permitidas = filtros.get('prioridades_permitidas', [])
        if prioridades_permitidas and alerta.prioridade not in prioridades_permitidas:
            return False

        return True

    def enviar_email(self, alerta: AlertaOportunidade) -> bool:
        """Enviar alerta por email"""
        try:
            if not self.verificar_rate_limit('email'):
                return False

            config_email = self.config['email']

            # Obter credenciais das variáveis de ambiente
            usuario = os.getenv('SMTP_USUARIO', config_email.get('usuario', ''))
            senha = os.getenv('SMTP_SENHA', config_email.get('senha', ''))

            if not usuario or not senha:
                self.logger.warning("⚠️ Credenciais de email não configuradas")
                return False

            # Criar mensagem
            msg = MimeMultipart()
            msg['From'] = usuario
            msg['Subject'] = f"🚨 Alerta de Oportunidade - {alerta.ativo} ({alerta.acao_recomendada})"

            # Corpo do email em HTML
            corpo_html = self._gerar_template_email(alerta)
            msg.attach(MimeText(corpo_html, 'html'))

            # Enviar para cada destinatário
            destinatarios = config_email.get('destinatarios', [])
            if not destinatarios:
                self.logger.warning("⚠️ Nenhum destinatário de email configurado")
                return False

            with smtplib.SMTP(config_email['smtp_server'], config_email['smtp_port']) as server:
                server.starttls()
                server.login(usuario, senha)

                for destinatario in destinatarios:
                    msg['To'] = destinatario
                    server.send_message(msg)
                    del msg['To']

            self.logger.info(f"✅ Email enviado: {alerta.ativo} para {len(destinatarios)} destinatários")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro enviando email: {e}")
            return False

    def enviar_telegram(self, alerta: AlertaOportunidade) -> bool:
        """Enviar alerta via Telegram Bot"""
        try:
            if not self.verificar_rate_limit('telegram'):
                return False

            config_telegram = self.config['telegram']

            # Obter token do bot das variáveis de ambiente
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN', config_telegram.get('bot_token', ''))

            if not bot_token:
                self.logger.warning("⚠️ Token do Telegram Bot não configurado")
                return False

            # Gerar mensagem
            mensagem = self._gerar_template_telegram(alerta)

            # Enviar para cada chat ID
            chat_ids = config_telegram.get('chat_ids', [])
            if not chat_ids:
                self.logger.warning("⚠️ Nenhum chat ID do Telegram configurado")
                return False

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
                else:
                    self.logger.error(f"❌ Erro Telegram chat {chat_id}: {response.text}")

            if sucessos > 0:
                self.logger.info(f"✅ Telegram enviado: {alerta.ativo} para {sucessos}/{len(chat_ids)} chats")
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Erro enviando Telegram: {e}")
            return False

    def enviar_webhook(self, alerta: AlertaOportunidade) -> bool:
        """Enviar alerta via webhook HTTP"""
        try:
            if not self.verificar_rate_limit('webhook'):
                return False

            config_webhook = self.config['webhook']

            # Preparar payload JSON
            payload = {
                'timestamp': alerta.timestamp.isoformat(),
                'alerta': asdict(alerta),
                'sistema': 'AgentEspecialistaMercadoFinanceiro',
                'versao': '1.0'
            }

            # Enviar para cada URL
            urls = config_webhook.get('urls', [])
            headers = config_webhook.get('headers', {})
            timeout = config_webhook.get('timeout', 10)

            if not urls:
                self.logger.warning("⚠️ Nenhuma URL de webhook configurada")
                return False

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
                    else:
                        self.logger.error(f"❌ Webhook falhou {url}: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    self.logger.error(f"❌ Erro webhook {url}: {e}")

            if sucessos > 0:
                self.logger.info(f"✅ Webhook enviado: {alerta.ativo} para {sucessos}/{len(urls)} URLs")
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Erro enviando webhook: {e}")
            return False

    def enviar_console(self, alerta: AlertaOportunidade) -> bool:
        """Enviar alerta para console/log"""
        try:
            if not self.verificar_rate_limit('console'):
                return False

            # Gerar mensagem para console
            mensagem = self._gerar_template_console(alerta)

            # Log baseado na prioridade
            if alerta.prioridade == 'CRITICA':
                self.logger.critical(mensagem)
            elif alerta.prioridade == 'ALTA':
                self.logger.warning(mensagem)
            elif alerta.prioridade == 'MEDIA':
                self.logger.info(mensagem)
            else:
                self.logger.debug(mensagem)

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro enviando console: {e}")
            return False

    def _gerar_template_email(self, alerta: AlertaOportunidade) -> str:
        """Gerar template HTML para email"""

        cor_acao = {
            'COMPRA': '#28a745',    # Verde
            'VENDA': '#dc3545',     # Vermelho
            'OBSERVAR': '#ffc107'   # Amarelo
        }.get(alerta.acao_recomendada, '#6c757d')

        catalysts_html = '<br>'.join([f"• {cat}" for cat in alerta.catalysts])

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: {cor_acao}; color: white; padding: 15px; border-radius: 5px; }}
                .content {{ padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 3px; }}
                .justificativa {{ background-color: #e9ecef; padding: 10px; margin: 10px 0; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 Alerta de Oportunidade - {alerta.ativo}</h2>
                <p>Ação Recomendada: <strong>{alerta.acao_recomendada}</strong></p>
            </div>

            <div class="content">
                <h3>📊 Métricas Principais</h3>
                <div class="metric">
                    <strong>Probabilidade:</strong><br>{alerta.probabilidade_sucesso}%
                </div>
                <div class="metric">
                    <strong>Confiança:</strong><br>{alerta.confianca}%
                </div>
                <div class="metric">
                    <strong>Risk/Reward:</strong><br>{alerta.risk_reward:.2f}
                </div>
                <div class="metric">
                    <strong>Timeframe:</strong><br>{alerta.timeframe}
                </div>

                <h3>💰 Níveis de Preço</h3>
                <p><strong>Entrada:</strong> ${alerta.preco_entrada:.5f}</p>
                <p><strong>Alvo:</strong> ${alerta.preco_alvo:.5f}</p>
                <p><strong>Stop Loss:</strong> ${alerta.stop_loss:.5f}</p>

                <h3>💡 Catalisadores</h3>
                <p>{catalysts_html}</p>

                <div class="justificativa">
                    <h4>📈 Justificativa Técnica</h4>
                    <p>{alerta.justificativa_tecnica}</p>
                </div>

                <div class="justificativa">
                    <h4>🌐 Justificativa Macro</h4>
                    <p>{alerta.justificativa_macro}</p>
                </div>

                <hr>
                <p><small>
                    <strong>ID:</strong> {alerta.id_alerta}<br>
                    <strong>Origem:</strong> {alerta.canal_origem}<br>
                    <strong>Timestamp:</strong> {alerta.timestamp.strftime('%d/%m/%Y %H:%M:%S')}<br>
                    <strong>Prioridade:</strong> {alerta.prioridade}
                </small></p>
            </div>
        </body>
        </html>
        """

    def _gerar_template_telegram(self, alerta: AlertaOportunidade) -> str:
        """Gerar template para Telegram (Markdown)"""

        emoji_acao = {
            'COMPRA': '🟢 📈',
            'VENDA': '🔴 📉',
            'OBSERVAR': '🟡 👁️'
        }.get(alerta.acao_recomendada, '⚪')

        catalysts_text = '\n'.join([f"• {cat}" for cat in alerta.catalysts[:3]])  # Max 3 para Telegram

        return f"""
🚨 *ALERTA DE OPORTUNIDADE* 🚨

{emoji_acao} *{alerta.ativo}* - {alerta.acao_recomendada}

📊 *Métricas:*
• Probabilidade: *{alerta.probabilidade_sucesso}%*
• Confiança: *{alerta.confianca}%*
• Risk/Reward: *{alerta.risk_reward:.2f}*
• Timeframe: *{alerta.timeframe}*

💰 *Preços:*
• Entrada: `${alerta.preco_entrada:.5f}`
• Alvo: `${alerta.preco_alvo:.5f}`
• Stop: `${alerta.stop_loss:.5f}`

💡 *Catalisadores:*
{catalysts_text}

📈 *Técnica:* {alerta.justificativa_tecnica[:200]}...

🌐 *Macro:* {alerta.justificativa_macro[:200]}...

⏰ {alerta.timestamp.strftime('%H:%M:%S')} | ID: `{alerta.id_alerta[:8]}`
        """.strip()

    def _gerar_template_console(self, alerta: AlertaOportunidade) -> str:
        """Gerar template para console"""

        return (f"🚨 ALERTA {alerta.prioridade}: {alerta.ativo} {alerta.acao_recomendada} | "
                f"Prob: {alerta.probabilidade_sucesso}% | Conf: {alerta.confianca}% | "
                f"R/R: {alerta.risk_reward:.2f} | ${alerta.preco_entrada:.5f} -> ${alerta.preco_alvo:.5f}")

    def enviar_alerta(self, alerta: AlertaOportunidade) -> Dict[str, bool]:
        """Enviar alerta para todos os canais ativos (método principal)"""

        resultados = {
            'email': False,
            'telegram': False,
            'webhook': False,
            'console': False
        }

        canais_enviados = []

        # Tentar enviar para cada canal
        for canal in resultados.keys():
            if self.filtrar_alerta(alerta, canal):
                try:
                    if canal == 'email':
                        success = self.enviar_email(alerta)
                    elif canal == 'telegram':
                        success = self.enviar_telegram(alerta)
                    elif canal == 'webhook':
                        success = self.enviar_webhook(alerta)
                    elif canal == 'console':
                        success = self.enviar_console(alerta)

                    resultados[canal] = success
                    if success:
                        canais_enviados.append(canal)

                except Exception as e:
                    self.logger.error(f"❌ Erro enviando para {canal}: {e}")
                    resultados[canal] = False

        # Salvar no histórico
        self._salvar_historico_alerta(alerta, canais_enviados, resultados)

        # Log de resultado
        canais_ok = [c for c, ok in resultados.items() if ok]
        if canais_ok:
            self.logger.info(f"✅ Alerta {alerta.id_alerta[:8]} enviado: {', '.join(canais_ok)}")
        else:
            self.logger.warning(f"⚠️ Alerta {alerta.id_alerta[:8]} não enviado para nenhum canal")

        return resultados

    def _salvar_historico_alerta(self, alerta: AlertaOportunidade, canais_enviados: List[str], status_entrega: Dict[str, bool]):
        """Salvar histórico do alerta no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO alertas_enviados
                (id_alerta, timestamp_envio, ativo, acao_recomendada, probabilidade_sucesso,
                 confianca, preco_entrada, preco_alvo, stop_loss, risk_reward, canal_origem,
                 prioridade, canais_enviados, status_entrega)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alerta.id_alerta,
                alerta.timestamp,
                alerta.ativo,
                alerta.acao_recomendada,
                alerta.probabilidade_sucesso,
                alerta.confianca,
                alerta.preco_entrada,
                alerta.preco_alvo,
                alerta.stop_loss,
                alerta.risk_reward,
                alerta.canal_origem,
                alerta.prioridade,
                json.dumps(canais_enviados),
                json.dumps(status_entrega)
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"❌ Erro salvando histórico: {e}")

    def gerar_relatorio_alertas(self, dias: int = 7) -> Dict:
        """Gerar relatório de estatísticas dos alertas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Alertas dos últimos N dias
            cursor.execute('''
                SELECT
                    COUNT(*) as total_alertas,
                    COUNT(CASE WHEN canais_enviados != '[]' THEN 1 END) as alertas_enviados,
                    ativo,
                    acao_recomendada,
                    AVG(probabilidade_sucesso) as prob_media,
                    AVG(confianca) as conf_media,
                    canal_origem
                FROM alertas_enviados
                WHERE timestamp_envio >= datetime('now', '-{} days')
                GROUP BY ativo, acao_recomendada, canal_origem
                ORDER BY total_alertas DESC
            '''.format(dias))

            dados = cursor.fetchall()

            # Estatísticas por canal
            cursor.execute('''
                SELECT
                    json_extract(canais_enviados, '$[0]') as canal,
                    COUNT(*) as total
                FROM alertas_enviados
                WHERE timestamp_envio >= datetime('now', '-{} days')
                  AND canais_enviados != '[]'
                GROUP BY canal
                ORDER BY total DESC
            '''.format(dias))

            canais_stats = cursor.fetchall()

            conn.close()

            return {
                'periodo_dias': dias,
                'alertas_por_ativo': dados,
                'distribuicao_canais': canais_stats,
                'timestamp_relatorio': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ Erro gerando relatório: {e}")
            return {}

# Função de teste e exemplo de uso
def exemplo_uso_sistema_alertas():
    """Exemplo de como usar o sistema de alertas"""

    print("🚀 Testando Sistema de Alertas Avançado...")

    # Inicializar sistema
    sistema = SistemaAlertasAvancado()

    # Criar alerta de exemplo
    alerta_exemplo = AlertaOportunidade(
        id_alerta="ALT_20251106_001",
        timestamp=datetime.now(),
        ativo="AAPL",
        acao_recomendada="COMPRA",
        probabilidade_sucesso=85,
        confianca=78,
        preco_entrada=150.25,
        preco_alvo=162.00,
        stop_loss=145.50,
        risk_reward=2.47,
        justificativa_tecnica="Rompimento da resistência em $150 com volume crescente, RSI em 65 confirma momentum positivo",
        justificativa_macro="VIX baixo em 19.5, ambiente favorável para growth stocks, Fed dovish suporta múltiplos",
        catalysts=[
            "Earnings season próximo com expectativas positivas",
            "Lançamento de novos produtos no Q4",
            "Ambiente macro favorável com VIX baixo"
        ],
        timeframe="MÉDIO_PRAZO (2-4 semanas)",
        canal_origem="AnaliseMacroEspecialista",
        prioridade="ALTA"
    )

    # Enviar alerta
    resultados = sistema.enviar_alerta(alerta_exemplo)

    print(f"\n📊 Resultados do envio:")
    for canal, sucesso in resultados.items():
        status = "✅" if sucesso else "❌"
        print(f"   {canal}: {status}")

    # Gerar relatório
    relatorio = sistema.gerar_relatorio_alertas(30)
    print(f"\n📈 Relatório gerado para últimos 30 dias")

    return sistema, alerta_exemplo

if __name__ == "__main__":
    sistema, alerta = exemplo_uso_sistema_alertas()
    print("\n✅ Sistema de Alertas Avançado implementado com sucesso!")