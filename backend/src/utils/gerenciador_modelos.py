"""
Gerenciador de Modelos YAML
Responsável por carregar e fornecer templates de saída para diferentes tipos de análise.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class GerenciadorModelos:
    """Gerencia o carregamento e acesso aos modelos YAML de saída."""

    def __init__(self):
        """Inicializa o gerenciador e carrega os modelos disponíveis."""
        self.diretorio_modelos = Path(__file__).parent.parent.parent.parent / "modelos"
        self.modelos_cache: Dict[str, Dict[str, Any]] = {}
        self._carregar_modelos()

    def _carregar_modelos(self) -> None:
        """Carrega todos os modelos YAML do diretório de modelos."""
        if not self.diretorio_modelos.exists():
            print(f"Aviso: Diretório de modelos não encontrado: {self.diretorio_modelos}")
            return

        for arquivo_yaml in self.diretorio_modelos.glob("*.yaml"):
            try:
                with open(arquivo_yaml, 'r', encoding='utf-8') as f:
                    conteudo = yaml.safe_load(f)
                    nome_modelo = arquivo_yaml.stem
                    self.modelos_cache[nome_modelo] = conteudo
                    print(f"Modelo carregado: {nome_modelo}")
            except Exception as e:
                print(f"Erro ao carregar modelo {arquivo_yaml.name}: {e}")

    def obter_modelo(self, mercado: str, tipo_analise: str) -> Optional[Dict[str, Any]]:
        """
        Obtém o modelo apropriado baseado no mercado e tipo de análise.

        Args:
            mercado: Tipo de mercado (forex, cripto, acoes, futuros)
            tipo_analise: Tipo de análise (rapida, tecnica, fundamental, completa)

        Returns:
            Dicionário com o template do modelo ou None se não encontrado
        """
        # Normalizar entradas
        mercado = mercado.lower()
        tipo_analise = tipo_analise.lower()

        # Mapear combinações de mercado + tipo para arquivos de modelo
        mapeamento_modelos = {
            ("forex", "rapida"): "forex_rapida",
            ("cripto", "tecnica"): "cripto_futuros_tecnica",
            ("futuros", "tecnica"): "cripto_futuros_tecnica",
            ("acoes", "fundamental"): "acoes_fundamental",
            ("ações", "fundamental"): "acoes_fundamental",
            ("cripto", "completa"): "cripto_completa",
        }

        chave = (mercado, tipo_analise)
        nome_modelo = mapeamento_modelos.get(chave)

        if nome_modelo and nome_modelo in self.modelos_cache:
            return self._preparar_modelo(self.modelos_cache[nome_modelo])

        # Fallback: tentar encontrar modelo por mercado apenas
        for nome, modelo in self.modelos_cache.items():
            if mercado in nome:
                return self._preparar_modelo(modelo)

        return None

    def _preparar_modelo(self, modelo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara uma cópia do modelo com valores padrão e timestamp.

        Args:
            modelo: Dicionário com o template original

        Returns:
            Cópia do modelo pronta para ser preenchida
        """
        import copy
        modelo_preparado = copy.deepcopy(modelo)

        # Adicionar timestamp se não existir
        if 'timestamp_analise' in modelo_preparado:
            modelo_preparado['timestamp_analise'] = datetime.now().isoformat()

        return modelo_preparado

    def listar_modelos_disponiveis(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos os modelos carregados.

        Returns:
            Dicionário com nome e metadados de cada modelo
        """
        return {
            nome: {
                'mercado': modelo.get('mercado', 'N/A'),
                'tipo_analise': modelo.get('tipo_analise', 'N/A'),
                'campos': list(modelo.keys())
            }
            for nome, modelo in self.modelos_cache.items()
        }

    def recarregar_modelos(self) -> None:
        """Recarrega todos os modelos do disco."""
        self.modelos_cache.clear()
        self._carregar_modelos()


# Instância global do gerenciador
gerenciador_modelos = GerenciadorModelos()
