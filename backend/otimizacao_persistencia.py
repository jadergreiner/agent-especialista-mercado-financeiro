#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Otimização de Persistência - Armazenamento Avançado de Dados
Implementa versionamento, compressão, arquivamento e APIs RESTful para dados financeiros
"""

import os
import json
import gzip
import pickle
import sqlite3
import hashlib
import shutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import time
from enum import Enum
import logging

class TipoDado(Enum):
    """Tipos de dados suportados"""
    PRECO_ATIVO = "preco_ativo"
    INDICADOR_MACRO = "indicador_macro"
    OPORTUNIDADE = "oportunidade"
    PORTFOLIO = "portfolio"
    ALERTA = "alerta"
    ANALISE = "analise"
    CORRELACAO = "correlacao"
    EVENTO_MERCADO = "evento_mercado"

@dataclass
class VersaoData:
    """Metadados de versionamento de dados"""
    id_versao: str
    tipo_dado: TipoDado
    timestamp_criacao: str
    hash_conteudo: str
    tamanho_original: int
    tamanho_comprimido: int
    caminho_arquivo: str
    tags: List[str]
    metadados: Dict[str, Any]

@dataclass
class ConfigArquivamento:
    """Configuração de arquivamento automático"""
    dias_manter_local: int = 30
    dias_manter_arquivo: int = 365
    compressao_ativa: bool = True
    nivel_compressao: int = 6
    arquivar_automatico: bool = True
    backup_incremental: bool = True
    max_versoes_locais: int = 100

class SistemaOtimizacaoPersistencia:
    """
    Sistema avançado de persistência com otimizações

    Funcionalidades:
    - Versionamento automático de dados
    - Compressão inteligente
    - Arquivamento temporal baseado em regras
    - APIs RESTful para acesso eficiente
    - Cache em memória para dados frequentes
    - Backup incremental
    """

    def __init__(self, diretorio_base: str = "data/persistencia"):
        self.diretorio_base = Path(diretorio_base)
        self.config = ConfigArquivamento()

        # Diretórios organizados
        self.dir_ativo = self.diretorio_base / "ativo"
        self.dir_arquivo = self.diretorio_base / "arquivo"
        self.dir_cache = self.diretorio_base / "cache"
        self.dir_backup = self.diretorio_base / "backup"
        self.dir_indices = self.diretorio_base / "indices"

        # Base de dados de metadados
        self.db_path = self.diretorio_base / "metadados.db"

        # Cache em memória
        self.cache_memoria = {}
        self.cache_limite = 1000  # Máximo de itens em cache

        # Lock para operações thread-safe
        self.lock = threading.RLock()

        # Configurar logging
        self.logger = self._configurar_logging()

        # Inicializar sistema
        self._inicializar_estrutura()
        self._inicializar_database()

        # Iniciar processo de arquivamento automático
        self._iniciar_arquivamento_automatico()

    def _configurar_logging(self) -> logging.Logger:
        """Configurar sistema de logging"""
        logger = logging.getLogger('otimizacao_persistencia')
        logger.setLevel(logging.INFO)

        os.makedirs('logs', exist_ok=True)

        handler = logging.FileHandler('logs/persistencia.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _inicializar_estrutura(self):
        """Criar estrutura de diretórios"""
        for diretorio in [self.dir_ativo, self.dir_arquivo, self.dir_cache,
                         self.dir_backup, self.dir_indices]:
            diretorio.mkdir(parents=True, exist_ok=True)

            # Subdiretórios por tipo de dado
            for tipo_dado in TipoDado:
                (diretorio / tipo_dado.value).mkdir(exist_ok=True)

    def _inicializar_database(self):
        """Inicializar base de dados de metadados"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Tabela de versões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS versoes (
                id_versao TEXT PRIMARY KEY,
                tipo_dado TEXT NOT NULL,
                timestamp_criacao TEXT NOT NULL,
                hash_conteudo TEXT NOT NULL,
                tamanho_original INTEGER NOT NULL,
                tamanho_comprimido INTEGER NOT NULL,
                caminho_arquivo TEXT NOT NULL,
                tags TEXT,
                metadados TEXT,
                arquivado BOOLEAN DEFAULT FALSE,
                timestamp_arquivamento TEXT,
                indice_busca TEXT
            )
        ''')

        # Tabela de cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_stats (
                chave TEXT PRIMARY KEY,
                hits INTEGER DEFAULT 0,
                misses INTEGER DEFAULT 0,
                ultimo_acesso TEXT,
                tamanho_dados INTEGER
            )
        ''')

        # Tabela de jobs de arquivamento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs_arquivamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_job TEXT NOT NULL,
                status TEXT DEFAULT 'PENDENTE',
                timestamp_criacao TEXT NOT NULL,
                timestamp_execucao TEXT,
                parametros TEXT,
                resultado TEXT
            )
        ''')

        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_versoes_tipo ON versoes(tipo_dado)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_versoes_timestamp ON versoes(timestamp_criacao)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_versoes_arquivado ON versoes(arquivado)')

        conn.commit()
        conn.close()

    def salvar_dados(self, dados: Any, tipo_dado: TipoDado,
                    tags: Optional[List[str]] = None,
                    metadados: Optional[Dict[str, Any]] = None) -> str:
        """
        Salvar dados com versionamento automático

        Args:
            dados: Dados a serem salvos (dict, list, etc.)
            tipo_dado: Tipo de dado
            tags: Tags para categorização
            metadados: Metadados adicionais

        Returns:
            ID da versão criada
        """
        with self.lock:
            try:
                # Serializar dados
                dados_json = json.dumps(dados, ensure_ascii=False, indent=2)
                dados_bytes = dados_json.encode('utf-8')

                # Calcular hash para deduplicação
                hash_conteudo = hashlib.sha256(dados_bytes).hexdigest()

                # Verificar se já existe versão com mesmo hash
                if self._versao_existe(hash_conteudo):
                    self.logger.info(f"Dados já existem (hash: {hash_conteudo[:8]})")
                    return self._obter_id_por_hash(hash_conteudo)

                # Gerar ID único da versão
                timestamp = datetime.now().isoformat()
                id_versao = f"{tipo_dado.value}_{int(time.time() * 1000)}_{hash_conteudo[:8]}"

                # Salvar dados
                caminho_arquivo = self._salvar_arquivo(dados_bytes, id_versao, tipo_dado)

                # Comprimir se configurado
                tamanho_original = len(dados_bytes)
                tamanho_comprimido = tamanho_original

                if self.config.compressao_ativa and tamanho_original > 1024:  # > 1KB
                    caminho_comprimido = self._comprimir_arquivo(caminho_arquivo)
                    if caminho_comprimido:
                        caminho_arquivo = caminho_comprimido
                        tamanho_comprimido = os.path.getsize(caminho_arquivo)

                # Criar metadados da versão
                versao = VersaoData(
                    id_versao=id_versao,
                    tipo_dado=tipo_dado,
                    timestamp_criacao=timestamp,
                    hash_conteudo=hash_conteudo,
                    tamanho_original=tamanho_original,
                    tamanho_comprimido=tamanho_comprimido,
                    caminho_arquivo=str(caminho_arquivo),
                    tags=tags or [],
                    metadados=metadados or {}
                )

                # Salvar metadados no banco
                self._salvar_metadados_versao(versao)

                # Atualizar cache
                self._atualizar_cache(id_versao, dados)

                # Criar índice de busca
                self._criar_indice_busca(id_versao, dados, tags)

                self.logger.info(f"Dados salvos: {id_versao} ({tamanho_original} -> {tamanho_comprimido} bytes)")

                return id_versao

            except Exception as e:
                self.logger.error(f"Erro salvando dados: {e}")
                raise

    def carregar_dados(self, id_versao: str, usar_cache: bool = True) -> Optional[Any]:
        """
        Carregar dados por ID da versão

        Args:
            id_versao: ID da versão
            usar_cache: Se deve usar cache em memória

        Returns:
            Dados carregados ou None se não encontrado
        """
        try:
            # Verificar cache primeiro
            if usar_cache and id_versao in self.cache_memoria:
                self._registrar_hit_cache(id_versao)
                return self.cache_memoria[id_versao]

            # Buscar metadados
            versao = self._obter_metadados_versao(id_versao)
            if not versao:
                self._registrar_miss_cache(id_versao)
                return None

            # Carregar arquivo
            dados = self._carregar_arquivo(versao.caminho_arquivo)

            # Atualizar cache se não estava
            if usar_cache and id_versao not in self.cache_memoria:
                self._atualizar_cache(id_versao, dados)

            self._registrar_hit_cache(id_versao)
            return dados

        except Exception as e:
            self.logger.error(f"Erro carregando dados {id_versao}: {e}")
            self._registrar_miss_cache(id_versao)
            return None

    def buscar_dados(self, tipo_dado: Optional[TipoDado] = None,
                    tags: Optional[List[str]] = None,
                    periodo_inicio: Optional[datetime] = None,
                    periodo_fim: Optional[datetime] = None,
                    limite: int = 100) -> List[VersaoData]:
        """
        Buscar dados por critérios

        Args:
            tipo_dado: Filtrar por tipo de dado
            tags: Filtrar por tags
            periodo_inicio: Data início
            periodo_fim: Data fim
            limite: Máximo de resultados

        Returns:
            Lista de versões encontradas
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Construir query dinâmica
            where_clauses = []
            params = []

            if tipo_dado:
                where_clauses.append("tipo_dado = ?")
                params.append(tipo_dado.value)

            if periodo_inicio:
                where_clauses.append("timestamp_criacao >= ?")
                params.append(periodo_inicio.isoformat())

            if periodo_fim:
                where_clauses.append("timestamp_criacao <= ?")
                params.append(periodo_fim.isoformat())

            if tags:
                # Buscar por tags (JSON contains)
                for tag in tags:
                    where_clauses.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            query = f'''
                SELECT id_versao, tipo_dado, timestamp_criacao, hash_conteudo,
                       tamanho_original, tamanho_comprimido, caminho_arquivo,
                       tags, metadados
                FROM versoes
                WHERE {where_sql}
                ORDER BY timestamp_criacao DESC
                LIMIT ?
            '''
            params.append(limite)

            cursor.execute(query, params)

            resultados = []
            for row in cursor.fetchall():
                versao = VersaoData(
                    id_versao=row[0],
                    tipo_dado=TipoDado(row[1]),
                    timestamp_criacao=row[2],
                    hash_conteudo=row[3],
                    tamanho_original=row[4],
                    tamanho_comprimido=row[5],
                    caminho_arquivo=row[6],
                    tags=json.loads(row[7]) if row[7] else [],
                    metadados=json.loads(row[8]) if row[8] else {}
                )
                resultados.append(versao)

            conn.close()
            return resultados

        except Exception as e:
            self.logger.error(f"Erro na busca: {e}")
            return []

    def arquivar_dados_antigos(self, dias_limite: Optional[int] = None) -> Dict[str, int]:
        """
        Arquivar dados antigos baseado em regras

        Args:
            dias_limite: Dias para manter local (padrão da config)

        Returns:
            Estatísticas do arquivamento
        """
        dias = dias_limite or self.config.dias_manter_local
        data_limite = datetime.now() - timedelta(days=dias)

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Buscar dados elegíveis para arquivamento
            cursor.execute('''
                SELECT id_versao, caminho_arquivo, tipo_dado
                FROM versoes
                WHERE timestamp_criacao < ? AND arquivado = FALSE
            ''', (data_limite.isoformat(),))

            candidatos = cursor.fetchall()

            stats = {
                'candidatos': len(candidatos),
                'arquivados': 0,
                'erros': 0,
                'espaco_liberado': 0
            }

            for id_versao, caminho_arquivo, tipo_dado in candidatos:
                try:
                    # Mover para área de arquivo
                    caminho_origem = Path(caminho_arquivo)
                    caminho_destino = self.dir_arquivo / tipo_dado / caminho_origem.name

                    if caminho_origem.exists():
                        # Criar diretório se não existe
                        caminho_destino.parent.mkdir(parents=True, exist_ok=True)

                        # Mover arquivo
                        shutil.move(str(caminho_origem), str(caminho_destino))

                        # Atualizar registro
                        cursor.execute('''
                            UPDATE versoes
                            SET arquivado = TRUE,
                                timestamp_arquivamento = ?,
                                caminho_arquivo = ?
                            WHERE id_versao = ?
                        ''', (datetime.now().isoformat(), str(caminho_destino), id_versao))

                        stats['arquivados'] += 1
                        stats['espaco_liberado'] += caminho_destino.stat().st_size

                        # Remover do cache
                        if id_versao in self.cache_memoria:
                            del self.cache_memoria[id_versao]

                except Exception as e:
                    self.logger.error(f"Erro arquivando {id_versao}: {e}")
                    stats['erros'] += 1

            conn.commit()
            conn.close()

            self.logger.info(f"Arquivamento concluído: {stats}")
            return stats

        except Exception as e:
            self.logger.error(f"Erro no arquivamento: {e}")
            return {'erro': str(e)}

    def limpar_dados_expirados(self, dias_limite: Optional[int] = None) -> Dict[str, int]:
        """
        Remover dados expirados permanentemente

        Args:
            dias_limite: Dias para manter no arquivo (padrão da config)

        Returns:
            Estatísticas da limpeza
        """
        dias = dias_limite or self.config.dias_manter_arquivo
        data_limite = datetime.now() - timedelta(days=dias)

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Buscar dados expirados
            cursor.execute('''
                SELECT id_versao, caminho_arquivo
                FROM versoes
                WHERE timestamp_criacao < ? AND arquivado = TRUE
            ''', (data_limite.isoformat(),))

            expirados = cursor.fetchall()

            stats = {
                'candidatos': len(expirados),
                'removidos': 0,
                'erros': 0,
                'espaco_liberado': 0
            }

            for id_versao, caminho_arquivo in expirados:
                try:
                    caminho = Path(caminho_arquivo)
                    if caminho.exists():
                        tamanho = caminho.stat().st_size
                        caminho.unlink()
                        stats['espaco_liberado'] += tamanho

                    # Remover registro
                    cursor.execute('DELETE FROM versoes WHERE id_versao = ?', (id_versao,))
                    stats['removidos'] += 1

                except Exception as e:
                    self.logger.error(f"Erro removendo {id_versao}: {e}")
                    stats['erros'] += 1

            conn.commit()
            conn.close()

            self.logger.info(f"Limpeza concluída: {stats}")
            return stats

        except Exception as e:
            self.logger.error(f"Erro na limpeza: {e}")
            return {'erro': str(e)}

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obter estatísticas do sistema de persistência"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Estatísticas básicas
            cursor.execute('SELECT COUNT(*) FROM versoes')
            total_versoes = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM versoes WHERE arquivado = FALSE')
            versoes_ativas = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM versoes WHERE arquivado = TRUE')
            versoes_arquivadas = cursor.fetchone()[0]

            # Por tipo de dado
            cursor.execute('''
                SELECT tipo_dado, COUNT(*), SUM(tamanho_original), SUM(tamanho_comprimido)
                FROM versoes
                GROUP BY tipo_dado
            ''')
            por_tipo = {}
            for row in cursor.fetchall():
                por_tipo[row[0]] = {
                    'count': row[1],
                    'tamanho_original': row[2],
                    'tamanho_comprimido': row[3],
                    'compressao_pct': (1 - (row[3] / row[2])) * 100 if row[2] > 0 else 0
                }

            # Cache stats
            cursor.execute('SELECT SUM(hits), SUM(misses) FROM cache_stats')
            cache_stats = cursor.fetchone()
            cache_hits = cache_stats[0] or 0
            cache_misses = cache_stats[1] or 0
            cache_hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100 if (cache_hits + cache_misses) > 0 else 0

            conn.close()

            # Tamanhos de diretórios
            tamanho_ativo = self._calcular_tamanho_diretorio(self.dir_ativo)
            tamanho_arquivo = self._calcular_tamanho_diretorio(self.dir_arquivo)
            tamanho_cache = self._calcular_tamanho_diretorio(self.dir_cache)

            return {
                'versoes': {
                    'total': total_versoes,
                    'ativas': versoes_ativas,
                    'arquivadas': versoes_arquivadas
                },
                'por_tipo': por_tipo,
                'cache': {
                    'hits': cache_hits,
                    'misses': cache_misses,
                    'hit_rate': cache_hit_rate,
                    'itens_memoria': len(self.cache_memoria)
                },
                'armazenamento': {
                    'ativo_mb': tamanho_ativo / 1024 / 1024,
                    'arquivo_mb': tamanho_arquivo / 1024 / 1024,
                    'cache_mb': tamanho_cache / 1024 / 1024,
                    'total_mb': (tamanho_ativo + tamanho_arquivo + tamanho_cache) / 1024 / 1024
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Erro obtendo estatísticas: {e}")
            return {'erro': str(e)}

    def _versao_existe(self, hash_conteudo: str) -> bool:
        """Verificar se já existe versão com o hash"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM versoes WHERE hash_conteudo = ?', (hash_conteudo,))
        existe = cursor.fetchone() is not None
        conn.close()
        return existe

    def _obter_id_por_hash(self, hash_conteudo: str) -> str:
        """Obter ID da versão pelo hash"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT id_versao FROM versoes WHERE hash_conteudo = ?', (hash_conteudo,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else ""

    def _salvar_arquivo(self, dados_bytes: bytes, id_versao: str, tipo_dado: TipoDado) -> Path:
        """Salvar arquivo no disco"""
        nome_arquivo = f"{id_versao}.json"
        caminho = self.dir_ativo / tipo_dado.value / nome_arquivo

        with open(caminho, 'wb') as f:
            f.write(dados_bytes)

        return caminho

    def _comprimir_arquivo(self, caminho: Path) -> Optional[Path]:
        """Comprimir arquivo usando gzip"""
        try:
            caminho_comprimido = caminho.with_suffix(caminho.suffix + '.gz')

            with open(caminho, 'rb') as f_in:
                with gzip.open(caminho_comprimido, 'wb', compresslevel=self.config.nivel_compressao) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remover original
            caminho.unlink()

            return caminho_comprimido

        except Exception as e:
            self.logger.error(f"Erro comprimindo {caminho}: {e}")
            return None

    def _carregar_arquivo(self, caminho_arquivo: str) -> Any:
        """Carregar dados do arquivo"""
        caminho = Path(caminho_arquivo)

        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

        # Detectar se é comprimido
        if caminho.suffix == '.gz':
            with gzip.open(caminho, 'rb') as f:
                dados_bytes = f.read()
        else:
            with open(caminho, 'rb') as f:
                dados_bytes = f.read()

        # Decodificar JSON
        dados_str = dados_bytes.decode('utf-8')
        return json.loads(dados_str)

    def _salvar_metadados_versao(self, versao: VersaoData):
        """Salvar metadados da versão no banco"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO versoes
            (id_versao, tipo_dado, timestamp_criacao, hash_conteudo,
             tamanho_original, tamanho_comprimido, caminho_arquivo, tags, metadados)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            versao.id_versao,
            versao.tipo_dado.value,
            versao.timestamp_criacao,
            versao.hash_conteudo,
            versao.tamanho_original,
            versao.tamanho_comprimido,
            versao.caminho_arquivo,
            json.dumps(versao.tags),
            json.dumps(versao.metadados)
        ))

        conn.commit()
        conn.close()

    def _obter_metadados_versao(self, id_versao: str) -> Optional[VersaoData]:
        """Obter metadados da versão do banco"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            SELECT tipo_dado, timestamp_criacao, hash_conteudo,
                   tamanho_original, tamanho_comprimido, caminho_arquivo, tags, metadados
            FROM versoes WHERE id_versao = ?
        ''', (id_versao,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return VersaoData(
            id_versao=id_versao,
            tipo_dado=TipoDado(row[0]),
            timestamp_criacao=row[1],
            hash_conteudo=row[2],
            tamanho_original=row[3],
            tamanho_comprimido=row[4],
            caminho_arquivo=row[5],
            tags=json.loads(row[6]) if row[6] else [],
            metadados=json.loads(row[7]) if row[7] else {}
        )

    def _atualizar_cache(self, chave: str, dados: Any):
        """Atualizar cache em memória"""
        # Limitar tamanho do cache
        if len(self.cache_memoria) >= self.cache_limite:
            # Remover item mais antigo (LRU simplificado)
            primeira_chave = next(iter(self.cache_memoria))
            del self.cache_memoria[primeira_chave]

        self.cache_memoria[chave] = dados

    def _registrar_hit_cache(self, chave: str):
        """Registrar hit no cache"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR IGNORE INTO cache_stats (chave, hits, misses, ultimo_acesso)
            VALUES (?, 0, 0, ?)
        ''', (chave, datetime.now().isoformat()))

        cursor.execute('''
            UPDATE cache_stats
            SET hits = hits + 1, ultimo_acesso = ?
            WHERE chave = ?
        ''', (datetime.now().isoformat(), chave))

        conn.commit()
        conn.close()

    def _registrar_miss_cache(self, chave: str):
        """Registrar miss no cache"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR IGNORE INTO cache_stats (chave, hits, misses, ultimo_acesso)
            VALUES (?, 0, 0, ?)
        ''', (chave, datetime.now().isoformat()))

        cursor.execute('''
            UPDATE cache_stats
            SET misses = misses + 1, ultimo_acesso = ?
            WHERE chave = ?
        ''', (datetime.now().isoformat(), chave))

        conn.commit()
        conn.close()

    def _criar_indice_busca(self, id_versao: str, dados: Any, tags: Optional[List[str]]):
        """Criar índice de busca textual"""
        try:
            # Extrair texto searchável
            texto_busca = []

            if isinstance(dados, dict):
                for valor in dados.values():
                    if isinstance(valor, (str, int, float)):
                        texto_busca.append(str(valor))

            if tags:
                texto_busca.extend(tags)

            indice = ' '.join(texto_busca).lower()

            # Salvar no banco
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE versoes
                SET indice_busca = ?
                WHERE id_versao = ?
            ''', (indice, id_versao))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Erro criando índice: {e}")

    def _calcular_tamanho_diretorio(self, diretorio: Path) -> int:
        """Calcular tamanho total de um diretório"""
        total = 0
        try:
            for arquivo in diretorio.rglob('*'):
                if arquivo.is_file():
                    total += arquivo.stat().st_size
        except:
            pass
        return total

    def _iniciar_arquivamento_automatico(self):
        """Iniciar processo de arquivamento automático"""
        if not self.config.arquivar_automatico:
            return

        def job_arquivamento():
            while True:
                try:
                    # Arquivar dados antigos
                    self.arquivar_dados_antigos()

                    # Aguardar 1 hora
                    time.sleep(3600)

                except Exception as e:
                    self.logger.error(f"Erro no job de arquivamento: {e}")
                    time.sleep(300)  # Aguardar 5 minutos em caso de erro

        thread_arquivamento = threading.Thread(target=job_arquivamento, daemon=True)
        thread_arquivamento.start()

def testar_sistema():
    """Testar funcionalidades do sistema"""
    print("🧪 Testando Sistema de Otimização de Persistência...")

    # Inicializar sistema
    sistema = SistemaOtimizacaoPersistencia("data/teste_persistencia")

    # Dados de teste
    dados_teste = [
        {
            'tipo': TipoDado.PRECO_ATIVO,
            'dados': {
                'ativo': 'AAPL',
                'preco': 150.25,
                'volume': 1000000,
                'timestamp': datetime.now().isoformat()
            },
            'tags': ['acao', 'nasdaq', 'tech']
        },
        {
            'tipo': TipoDado.INDICADOR_MACRO,
            'dados': {
                'indicador': 'VIX',
                'valor': 18.5,
                'timestamp': datetime.now().isoformat()
            },
            'tags': ['volatilidade', 'mercado']
        },
        {
            'tipo': TipoDado.OPORTUNIDADE,
            'dados': {
                'ativo': 'NVDA',
                'acao': 'COMPRA',
                'probabilidade': 85,
                'risk_reward': 3.2,
                'timestamp': datetime.now().isoformat()
            },
            'tags': ['ia', 'semicondutores', 'crescimento']
        }
    ]

    print(f"📝 Salvando {len(dados_teste)} registros de teste...")

    ids_versoes = []
    for item in dados_teste:
        id_versao = sistema.salvar_dados(
            dados=item['dados'],
            tipo_dado=item['tipo'],
            tags=item['tags'],
            metadados={'teste': True}
        )
        ids_versoes.append(id_versao)
        print(f"   ✅ {item['tipo'].value}: {id_versao}")

    # Testar carregamento
    print(f"\n📖 Testando carregamento...")
    for id_versao in ids_versoes:
        dados = sistema.carregar_dados(id_versao)
        if dados:
            print(f"   ✅ Carregado: {id_versao}")
        else:
            print(f"   ❌ Erro carregando: {id_versao}")

    # Testar busca
    print(f"\n🔍 Testando busca...")

    # Busca por tipo
    resultados = sistema.buscar_dados(tipo_dado=TipoDado.PRECO_ATIVO)
    print(f"   📊 Preços de ativos: {len(resultados)} encontrados")

    # Busca por tags
    resultados = sistema.buscar_dados(tags=['tech'])
    print(f"   🏷️  Tag 'tech': {len(resultados)} encontrados")

    # Estatísticas
    print(f"\n📈 Estatísticas do sistema:")
    stats = sistema.obter_estatisticas()

    print(f"   📋 Versões: {stats['versoes']['total']} total, {stats['versoes']['ativas']} ativas")
    print(f"   💾 Cache: {stats['cache']['hit_rate']:.1f}% hit rate, {stats['cache']['itens_memoria']} em memória")
    print(f"   💿 Armazenamento: {stats['armazenamento']['total_mb']:.1f} MB total")

    for tipo, info in stats['por_tipo'].items():
        print(f"   📁 {tipo}: {info['count']} itens, {info['compressao_pct']:.1f}% compressão")

    print(f"\n✅ Sistema de Otimização de Persistência implementado com sucesso!")
    return sistema

if __name__ == "__main__":
    testar_sistema()