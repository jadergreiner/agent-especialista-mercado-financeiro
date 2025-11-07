#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Conversacional v2 - Prompt-First

Interface interativa (REPL) para análise de ativos via prompt.
Implementa histórico de comandos, logs de sessão, latência e cache.
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.dados.analisador_trading_cripto import AnalisadorTradingCripto
from src.dados.analisador_intraday_forex import AnalisadorIntradayForex
from validador_contratos import ValidadorContrato
from cache_sessoes import CacheSessoes


class LogSessao:
    """Registra sessões de uso sem dados sensíveis."""

    def __init__(self, arquivo: Optional[Path] = None):
        if arquivo is None:
            arquivo = Path(__file__).parent / 'logs' / 'sessoes_cli.jsonl'
        arquivo.parent.mkdir(exist_ok=True)
        self.arquivo = arquivo
        self.sessao_id = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        self.comandos: List[Dict[str, Any]] = []

    def registrar_comando(self, comando: str, latencia_ms: float, sucesso: bool, erro: Optional[str] = None):
        """Registra comando executado."""
        entrada = {
            'sessao_id': self.sessao_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'comando': comando.split()[0] if comando else 'vazio',  # apenas o verbo, sem o par
            'latencia_ms': round(latencia_ms, 2),
            'sucesso': sucesso,
            'erro': erro
        }
        self.comandos.append(entrada)

        # Append ao arquivo JSONL
        with open(self.arquivo, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + '\n')

    def resumo(self) -> str:
        """Retorna resumo da sessão."""
        total = len(self.comandos)
        sucesso = sum(1 for c in self.comandos if c['sucesso'])
        latencia_media = sum(c['latencia_ms'] for c in self.comandos) / total if total else 0
        return f"Sessão {self.sessao_id}: {sucesso}/{total} comandos bem-sucedidos | latência média: {latencia_media:.0f}ms"


class NormalizadorSimbolo:
    """Normaliza símbolos e aliases."""

    ALIASES = {
        'BTCUSD': 'BTCUSDT',
        'ETHUSD': 'ETHUSDT',
        'XBTUSD': 'BTCUSDT',
    }

    @classmethod
    def normalizar(cls, simbolo: str) -> tuple[str, str]:
        """
        Normaliza símbolo.

        Returns:
            (simbolo_normalizado, mensagem_normalizacao)
        """
        simbolo_original = simbolo
        simbolo = simbolo.upper().replace('/', '').replace('-', '').strip()

        # Aplica aliases
        if simbolo in cls.ALIASES:
            normalizado = cls.ALIASES[simbolo]
            return normalizado, f"Normalizando: {simbolo_original} → {normalizado}"

        return simbolo, ""


class CLIConversacional:
    """CLI interativo (REPL) para análise de ativos."""

    def __init__(self):
        self.historico: List[str] = []
        self.max_historico = 5
        self.log = LogSessao()
        self.cache = CacheSessoes()
        self.analisador_cripto = AnalisadorTradingCripto()
        self.analisador_forex = AnalisadorIntradayForex()
        self.cache_hits = 0
        self.cache_misses = 0
        # Histórico persistente
        self.arquivo_historico = Path(__file__).parent / 'logs' / 'historico_cli.txt'
        self.arquivo_historico.parent.mkdir(exist_ok=True)
        self._carregar_historico_persistente()

    def _carregar_historico_persistente(self, limite: int = 100):
        """Carrega últimos comandos do histórico persistente, se existir."""
        if self.arquivo_historico.exists():
            try:
                linhas = self.arquivo_historico.read_text(encoding='utf-8').splitlines()
                # Mantém apenas os comandos (após separador \t)
                comandos = [l.split('\t', 1)[1] if '\t' in l else l for l in linhas[-limite:]]
                for cmd in comandos[-self.max_historico:]:
                    if cmd:
                        self.adicionar_historico(cmd)
            except Exception:
                # Não falhar por causa do histórico
                pass

    def _registrar_historico_persistente(self, comando: str):
        """Registra comando em arquivo persistente com timestamp UTC."""
        try:
            ts = datetime.now(timezone.utc).isoformat()
            with open(self.arquivo_historico, 'a', encoding='utf-8') as f:
                f.write(f"{ts}\t{comando}\n")
        except Exception:
            # Não interromper fluxo se não conseguir gravar
            pass

    def exibir_banner(self):
        """Exibe banner inicial."""
        print("=" * 70)
        print("💰 AGENT ESPECIALISTA DE MERCADO FINANCEIRO")
        print("   Prompt-First v2 - CLI Conversacional + Cache")
        print("=" * 70)
        print("Digite 'ajuda' para ver comandos | 'sair' para encerrar")
        print("=" * 70)
        print()

    def exibir_ajuda(self):
        """Exibe ajuda."""
        print("\n📚 COMANDOS:")
        print("-" * 70)
        print("  ajuda                               - Exibe esta ajuda")
        print("  sair                                - Encerra a sessão")
        print("  analisar <par> [<pares>...] [tf]    - Análise de um ou mais pares")
        print("  cache                               - Exibe estatísticas do cache")
        print("  historico [N]                       - Lista os últimos N comandos (padrão 10)")
        print()
        print("EXEMPLOS:")
        print("  analisar EURUSD                     - Análise Forex intraday")
        print("  analisar BTCUSDT                    - Análise Cripto intraday")
        print("  analisar BTCUSD                     - Normalizado para BTCUSDT")
        print("  analisar EURUSD GBPUSD              - Análise de múltiplos pares (batch)")
        print("  analisar EURUSD diario              - Análise Forex timeframe diário")
        print("  analisar EURUSD GBPUSD semanal      - Batch com timeframe semanal")
        print("  historico 20                        - Exibe os últimos 20 comandos")
        print("-" * 70)

    def adicionar_historico(self, comando: str):
        """Adiciona comando ao histórico."""
        self.historico.append(comando)
        if len(self.historico) > self.max_historico:
            self.historico.pop(0)

    def inferir_classe(self, par: str) -> str:
        """Infere classe de ativo pelo par."""
        par_upper = par.upper()

        # Cripto: termina em USDT, BTC, ETH ou aliases conhecidos
        if any(par_upper.endswith(sufixo) for sufixo in ['USDT', 'BTC', 'ETH', 'BUSD']):
            return 'cripto'

        # Forex: 6 caracteres e sem números
        if len(par_upper) == 6 and par_upper.isalpha():
            return 'forex'

        # Default: cripto (mais comum em prompt-first)
        return 'cripto'

    def analisar(self, par: str, timeframe: str = 'intraday') -> Dict[str, Any]:
        """
        Executa análise do par com cache.

        Args:
            par: Símbolo do ativo
            timeframe: Timeframe da análise (intraday, diario, semanal, mensal)

        Returns:
            Contrato mínimo de resposta
        """
        # Normaliza símbolo
        par_normalizado, msg_norm = NormalizadorSimbolo.normalizar(par)
        if msg_norm:
            print(f"  ℹ️  {msg_norm}")

        # Infere classe
        classe = self.inferir_classe(par_normalizado)
        print(f"  📊 Classe detectada: {classe.upper()} | Timeframe: {timeframe}")

        # Tenta obter do cache
        resultado_cache = self.cache.obter(par_normalizado, classe, timeframe)
        if resultado_cache is not None:
            print(f"  ⚡ Cache HIT! (latência reduzida)")
            self.cache_hits += 1
            return resultado_cache

        print(f"  🔄 Cache MISS - consultando fonte de dados...")
        self.cache_misses += 1

        # Executa análise
        if classe == 'cripto':
            relatorio = self.analisador_cripto.analisar(par_normalizado)
            resultado = self._converter_para_contrato_minimo(relatorio, 'cripto', par_normalizado, timeframe)
        else:  # forex
            relatorio = self.analisador_forex.analisar(par_normalizado)
            resultado = self._converter_para_contrato_minimo(relatorio, 'forex', par_normalizado, timeframe)

        # Armazena no cache
        self.cache.armazenar(par_normalizado, classe, resultado, timeframe)

        return resultado

    def _converter_para_contrato_minimo(self, relatorio: Dict[str, Any], classe: str, par: str, timeframe: str = 'intraday') -> Dict[str, Any]:
        """Converte relatório completo para contrato mínimo v1."""
        resumo_rel = relatorio.get('resumo', {})

        # Campos do contrato mínimo
        return {
            'classe_ativo': classe,
            'par': par,
            'timeframe': timeframe,
            'timestamp': relatorio.get('timestamp', datetime.now(timezone.utc).isoformat()),
            'resumo': {
                'preco_atual': resumo_rel.get('precoAtual', 0.0),
                'operacao': resumo_rel.get('operacao', 'ESPERAR'),
                'entrada': resumo_rel.get('entrada', 0.0),
                'alvo1': resumo_rel.get('alvo1', 0.0),
                'stop': resumo_rel.get('stop', 0.0),
                'rr': resumo_rel.get('rr', 'N/A'),
                'riscos_chave': resumo_rel.get('riscosChave', []),
                'proximos_passos': resumo_rel.get('proximosPassos', [])
            },
            'justificativas': resumo_rel.get('justificativas', [])
        }

    def processar_comando(self, entrada: str) -> bool:
        """
        Processa comando do usuário.

        Returns:
            False se deve sair, True caso contrário
        """
        entrada = entrada.strip()
        if not entrada:
            return True

        self.adicionar_historico(entrada)
        self._registrar_historico_persistente(entrada)

        inicio = time.time()
        sucesso = True
        erro = None

        try:
            partes = entrada.split()
            comando = partes[0].lower()

            if comando == 'sair':
                print("\n👋 Encerrando sessão...")
                print(self.log.resumo())

                # Limpa cache expirado ao sair
                removidos = self.cache.limpar_expirados()
                if removidos > 0:
                    print(f"🧹 {removidos} entradas expiradas removidas do cache")

                return False

            elif comando == 'ajuda':
                self.exibir_ajuda()

            elif comando == 'historico':
                # Lista últimos N comandos do histórico persistente
                n = 10
                if len(partes) >= 2 and partes[1].isdigit():
                    try:
                        n = max(1, min(100, int(partes[1])))
                    except ValueError:
                        n = 10
                try:
                    linhas = []
                    if self.arquivo_historico.exists():
                        linhas = self.arquivo_historico.read_text(encoding='utf-8').splitlines()
                    ultimos = linhas[-n:]
                    print(f"\n🕘 Últimos {min(n, len(ultimos))} comandos:")
                    print("-" * 70)
                    for i, linha in enumerate(ultimos, 1):
                        # separador TAB: timestamp \t comando
                        if '\t' in linha:
                            ts, cmd = linha.split('\t', 1)
                        else:
                            ts, cmd = "", linha
                        print(f"{i:>3}. {ts}  |  {cmd}")
                    print("-" * 70)
                except Exception as e_hist:
                    print(f"❌ Erro ao ler histórico: {e_hist}")

            elif comando == 'cache':
                # Exibe estatísticas do cache
                stats = self.cache.estatisticas()
                print("\n📊 ESTATÍSTICAS DO CACHE:")
                print("-" * 70)
                print(f"  Total de entradas: {stats['total']}")
                print(f"  Válidas: {stats['validas']}")
                print(f"  Expiradas: {stats['expiradas']}")
                print(f"  Por classe: {stats['por_classe']}")
                print(f"\n  Cache hits: {self.cache_hits}")
                print(f"  Cache misses: {self.cache_misses}")
                if self.cache_hits + self.cache_misses > 0:
                    taxa_hit = (self.cache_hits / (self.cache_hits + self.cache_misses)) * 100
                    print(f"  Taxa de acerto: {taxa_hit:.1f}%")
                print("-" * 70)

            elif comando == 'analisar':
                if len(partes) < 2:
                    print("❌ Uso: analisar <par> [<par2> <par3> ...] [intraday|diario|semanal|mensal]")
                    print("   Exemplo: analisar EURUSD")
                    print("   Exemplo: analisar EURUSD GBPUSD BTCUSDT")
                    print("   Exemplo: analisar EURUSD diario")
                    sucesso = False
                    erro = 'argumentos_insuficientes'
                else:
                    # Suporte a múltiplos pares (batch) e timeframe opcional no final
                    aceitos_tf = {"intraday", "diario", "semanal", "mensal"}
                    timeframe = 'intraday'
                    if len(partes) >= 3 and partes[-1].lower() in aceitos_tf:
                        timeframe = partes[-1].lower()
                        pares = partes[1:-1]
                    else:
                        pares = partes[1:]

                    if not pares:
                        print("❌ Informe ao menos um par para analisar")
                        sucesso = False
                        erro = 'argumentos_insuficientes'
                        return True

                    if len(pares) == 1:
                        # Análise única
                        par = pares[0]
                        print(f"\n🔍 Analisando {par} ({timeframe})...")
                        resultado = self.analisar(par, timeframe=timeframe)

                        # Valida contrato
                        print("\n🔍 Validando contrato mínimo...")
                        valido, erros_validacao = ValidadorContrato.validar(resultado)
                        if not valido:
                            print("⚠️  Aviso: contrato com problemas:")
                            for erro_val in erros_validacao:
                                print(f"   - {erro_val}")
                        else:
                            print("✅ Contrato válido")

                        # Exibe resposta formatada
                        print("\n" + "=" * 70)
                        print("📋 RESULTADO (Contrato Mínimo v2)")
                        print("=" * 70)
                        print(json.dumps(resultado, indent=2, ensure_ascii=False))
                        print("=" * 70)
                    else:
                        # Análise em batch (múltiplos pares)
                        print(f"\n🔍 Analisando {len(pares)} pares em batch (tf={timeframe})...")
                        resultados = []

                        for idx, par in enumerate(pares, 1):
                            print(f"\n[{idx}/{len(pares)}] Processando {par}...")
                            try:
                                resultado = self.analisar(par, timeframe=timeframe)
                                resultados.append(resultado)
                            except Exception as e_par:
                                print(f"   ❌ Erro ao analisar {par}: {e_par}")

                        # Exibe resumo consolidado
                        print("\n" + "=" * 70)
                        print(f"📋 RESULTADOS BATCH ({len(resultados)}/{len(pares)} bem-sucedidos)")
                        print("=" * 70)

                        for res in resultados:
                            operacao = res['resumo']['operacao']
                            par_res = res['par']
                            preco = res['resumo']['preco_atual']
                            print(f"\n{par_res}:")
                            print(f"  Operação: {operacao}")
                            print(f"  Preço atual: {preco}")
                            if operacao != 'ESPERAR':
                                print(f"  Entrada: {res['resumo']['entrada']}")
                                print(f"  Stop: {res['resumo']['stop']}")
                                print(f"  Alvo: {res['resumo']['alvo1']}")
                                print(f"  R:R: {res['resumo']['rr']}")

                        print("=" * 70)

            else:
                print(f"❌ Comando desconhecido: '{comando}'")
                print("   Digite 'ajuda' para ver comandos disponíveis")
                sucesso = False
                erro = 'comando_desconhecido'

        except Exception as e:
            print(f"❌ Erro ao processar comando: {e}")
            sucesso = False
            erro = str(type(e).__name__)

        finally:
            latencia_ms = (time.time() - inicio) * 1000
            self.log.registrar_comando(entrada, latencia_ms, sucesso, erro)

            # Exibe latência se > 1s
            if latencia_ms > 1000:
                print(f"⏱️  Tempo de resposta: {latencia_ms/1000:.1f}s")

        return True

    def loop(self):
        """Loop principal REPL."""
        self.exibir_banner()

        while True:
            try:
                entrada = input("\n> ").strip()
                if not self.processar_comando(entrada):
                    break
            except KeyboardInterrupt:
                print("\n\n👋 Encerrando sessão (Ctrl+C)...")
                print(self.log.resumo())
                break
            except EOFError:
                print("\n\n👋 Encerrando sessão (EOF)...")
                print(self.log.resumo())
                break


def main():
    """Ponto de entrada do CLI conversacional."""
    cli = CLIConversacional()
    cli.loop()


if __name__ == '__main__':
    main()
