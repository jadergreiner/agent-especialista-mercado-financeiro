#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API RESTful para Sistema de Otimização de Persistência
Endpoints para acesso eficiente aos dados versionados
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.otimizacao_persistencia import SistemaOtimizacaoPersistencia, TipoDado

class APIPersistencia:
    """
    API RESTful para o Sistema de Otimização de Persistência

    Endpoints:
    - GET /api/dados/<id_versao> - Carregar dados por ID
    - POST /api/dados - Salvar novos dados
    - GET /api/buscar - Buscar dados por critérios
    - GET /api/estatisticas - Estatísticas do sistema
    - POST /api/arquivar - Executar arquivamento
    - POST /api/limpar - Limpar dados expirados
    - GET /api/tipos-dado - Listar tipos de dados disponíveis
    """

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Permitir CORS para integração com dashboard

        self.sistema = SistemaOtimizacaoPersistencia()

        self._configurar_rotas()
        self._configurar_tratamento_erros()

    def _configurar_rotas(self):
        """Configurar todas as rotas da API"""

        @self.app.route('/api/dados/<id_versao>', methods=['GET'])
        def carregar_dados(id_versao: str):
            """Carregar dados por ID da versão"""
            try:
                usar_cache = request.args.get('cache', 'true').lower() == 'true'
                dados = self.sistema.carregar_dados(id_versao, usar_cache=usar_cache)

                if dados is None:
                    abort(404, description='Dados não encontrados')

                return jsonify({
                    'status': 'success',
                    'id_versao': id_versao,
                    'dados': dados,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                abort(500, description=str(e))

        @self.app.route('/api/dados', methods=['POST'])
        def salvar_dados():
            """Salvar novos dados"""
            try:
                payload = request.get_json()

                if not payload:
                    abort(400, description='Payload JSON requerido')

                # Validar campos obrigatórios
                if 'dados' not in payload or 'tipo_dado' not in payload:
                    abort(400, description='Campos "dados" e "tipo_dado" são obrigatórios')

                # Validar tipo de dado
                try:
                    tipo_dado = TipoDado(payload['tipo_dado'])
                except ValueError:
                    abort(400, description=f'Tipo de dado inválido: {payload["tipo_dado"]}')

                # Salvar dados
                id_versao = self.sistema.salvar_dados(
                    dados=payload['dados'],
                    tipo_dado=tipo_dado,
                    tags=payload.get('tags', []),
                    metadados=payload.get('metadados', {})
                )

                return jsonify({
                    'status': 'success',
                    'id_versao': id_versao,
                    'message': 'Dados salvos com sucesso',
                    'timestamp': datetime.now().isoformat()
                }), 201

            except Exception as e:
                abort(500, description=str(e))

        @self.app.route('/api/buscar', methods=['GET'])
        def buscar_dados():
            """Buscar dados por critérios"""
            try:
                # Parâmetros de busca
                tipo_dado = request.args.get('tipo_dado')
                tags = request.args.getlist('tags')
                periodo_inicio = request.args.get('periodo_inicio')
                periodo_fim = request.args.get('periodo_fim')
                limite = request.args.get('limite', 100, type=int)

                # Validar tipo de dado
                tipo_dado_enum = None
                if tipo_dado:
                    try:
                        tipo_dado_enum = TipoDado(tipo_dado)
                    except ValueError:
                        abort(400, description=f'Tipo de dado inválido: {tipo_dado}')

                # Converter datas
                inicio = None
                fim = None
                try:
                    if periodo_inicio:
                        inicio = datetime.fromisoformat(periodo_inicio.replace('Z', '+00:00'))
                    if periodo_fim:
                        fim = datetime.fromisoformat(periodo_fim.replace('Z', '+00:00'))
                except ValueError:
                    abort(400, description='Formato de data inválido (use ISO format)')

                # Executar busca
                resultados = self.sistema.buscar_dados(
                    tipo_dado=tipo_dado_enum,
                    tags=tags if tags else None,
                    periodo_inicio=inicio,
                    periodo_fim=fim,
                    limite=limite
                )

                # Converter resultados para JSON
                resultados_json = []
                for versao in resultados:
                    resultados_json.append({
                        'id_versao': versao.id_versao,
                        'tipo_dado': versao.tipo_dado.value,
                        'timestamp_criacao': versao.timestamp_criacao,
                        'hash_conteudo': versao.hash_conteudo,
                        'tamanho_original': versao.tamanho_original,
                        'tamanho_comprimido': versao.tamanho_comprimido,
                        'tags': versao.tags,
                        'metadados': versao.metadados
                    })

                return jsonify({
                    'status': 'success',
                    'resultados': resultados_json,
                    'total': len(resultados_json),
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                abort(500, description=str(e))

        @self.app.route('/api/estatisticas', methods=['GET'])
        def obter_estatisticas():
            """Obter estatísticas do sistema"""
            try:
                stats = self.sistema.obter_estatisticas()

                return jsonify({
                    'status': 'success',
                    'estatisticas': stats
                })

            except Exception as e:
                abort(500, description=str(e))

        @self.app.route('/api/arquivar', methods=['POST'])
        def executar_arquivamento():
            """Executar arquivamento de dados antigos"""
            try:
                payload = request.get_json() or {}
                dias_limite = payload.get('dias_limite')

                stats = self.sistema.arquivar_dados_antigos(dias_limite)

                return jsonify({
                    'status': 'success',
                    'resultado_arquivamento': stats,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                abort(500, description=str(e))

        @self.app.route('/api/limpar', methods=['POST'])
        def limpar_dados_expirados():
            """Limpar dados expirados"""
            try:
                payload = request.get_json() or {}
                dias_limite = payload.get('dias_limite')

                stats = self.sistema.limpar_dados_expirados(dias_limite)

                return jsonify({
                    'status': 'success',
                    'resultado_limpeza': stats,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                abort(500, description=str(e))

        @self.app.route('/api/tipos-dado', methods=['GET'])
        def listar_tipos_dados():
            """Listar tipos de dados disponíveis"""
            try:
                tipos = [{'valor': tipo.value, 'nome': tipo.name} for tipo in TipoDado]

                return jsonify({
                    'status': 'success',
                    'tipos_dados': tipos
                })

            except Exception as e:
                abort(500, description=str(e))

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check da API"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'versao': '1.0.0'
            })

        @self.app.route('/api/docs', methods=['GET'])
        def documentacao():
            """Documentação da API"""
            docs = {
                'titulo': 'API Sistema de Otimização de Persistência',
                'versao': '1.0.0',
                'endpoints': [
                    {
                        'metodo': 'GET',
                        'url': '/api/dados/<id_versao>',
                        'descricao': 'Carregar dados por ID da versão',
                        'parametros': {
                            'cache': 'Usar cache em memória (true/false)'
                        }
                    },
                    {
                        'metodo': 'POST',
                        'url': '/api/dados',
                        'descricao': 'Salvar novos dados',
                        'body': {
                            'dados': 'Dados a serem salvos (objeto)',
                            'tipo_dado': 'Tipo de dado (enum)',
                            'tags': 'Lista de tags (opcional)',
                            'metadados': 'Metadados adicionais (opcional)'
                        }
                    },
                    {
                        'metodo': 'GET',
                        'url': '/api/buscar',
                        'descricao': 'Buscar dados por critérios',
                        'parametros': {
                            'tipo_dado': 'Filtrar por tipo de dado',
                            'tags': 'Filtrar por tags (múltiplas)',
                            'periodo_inicio': 'Data início (ISO format)',
                            'periodo_fim': 'Data fim (ISO format)',
                            'limite': 'Máximo de resultados (padrão: 100)'
                        }
                    },
                    {
                        'metodo': 'GET',
                        'url': '/api/estatisticas',
                        'descricao': 'Obter estatísticas do sistema'
                    },
                    {
                        'metodo': 'POST',
                        'url': '/api/arquivar',
                        'descricao': 'Executar arquivamento de dados antigos',
                        'body': {
                            'dias_limite': 'Dias para manter local (opcional)'
                        }
                    },
                    {
                        'metodo': 'POST',
                        'url': '/api/limpar',
                        'descricao': 'Limpar dados expirados',
                        'body': {
                            'dias_limite': 'Dias para manter no arquivo (opcional)'
                        }
                    },
                    {
                        'metodo': 'GET',
                        'url': '/api/tipos-dado',
                        'descricao': 'Listar tipos de dados disponíveis'
                    },
                    {
                        'metodo': 'GET',
                        'url': '/api/health',
                        'descricao': 'Health check da API'
                    }
                ]
            }

            return jsonify(docs)

    def _configurar_tratamento_erros(self):
        """Configurar tratamento de erros HTTP"""

        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'status': 'error',
                'codigo': 400,
                'erro': 'Bad Request',
                'descricao': error.description,
                'timestamp': datetime.now().isoformat()
            }), 400

        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'status': 'error',
                'codigo': 404,
                'erro': 'Not Found',
                'descricao': error.description,
                'timestamp': datetime.now().isoformat()
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'status': 'error',
                'codigo': 500,
                'erro': 'Internal Server Error',
                'descricao': error.description,
                'timestamp': datetime.now().isoformat()
            }), 500

    def executar(self, host: str = '127.0.0.1', port: int = 5001, debug: bool = True):
        """Executar servidor da API"""
        print(f"🚀 Iniciando API de Persistência...")
        print(f"   URL: http://{host}:{port}")
        print(f"   Docs: http://{host}:{port}/api/docs")
        print(f"   Modo: {'Debug' if debug else 'Produção'}")

        self.app.run(host=host, port=port, debug=debug)

def main():
    """Função principal"""
    api = APIPersistencia()
    api.executar()

if __name__ == "__main__":
    main()