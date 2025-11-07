"""
CLI para importar dados manuais (CSV) de preços diários para o banco SQLite.

Diretório padrão de importação: backend/data/manual
Suporta arquivos no formato (colunas em PT-BR):
- "Data" (dd.mm.yyyy)
- "Último"
- "Abertura"
- "Máxima"
- "Mínima"
- "Vol." (ex: 44,99K / 1,20M)
- "Var%" (ex: 0,03%)

Uso:
  - Importar um arquivo específico:
      python backend/src/cli_importar_csv.py importar-diario --arquivo backend/data/manual/ibov.csv --instrumento WIN
  - Importar todos os CSVs do diretório padrão:
      python backend/src/cli_importar_csv.py importar-diario --dir backend/data/manual --instrumento WIN
"""
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional, List, Dict, Any, Tuple

# Garantir que possamos importar o módulo de persistência
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.persistencia.recomendacoes import inicializar_banco, _conectar  # type: ignore


BASE_MANUAL_DIR = Path(__file__).parent.parent / 'data' / 'manual'
DEFAULT_INSTRUMENTO = 'WIN'
DEFAULT_DIR = BASE_MANUAL_DIR / DEFAULT_INSTRUMENTO


@dataclass
class RegistroDiario:
    data: str
    instrumento: str
    ultimo: float
    abertura: float
    maxima: float
    minima: float
    volume: Optional[int]
    variacao_pct: Optional[float]
    fonte: Optional[str]
    arquivo: Optional[str]


def _ptbr_to_float(valor: str) -> float:
    """Converte string PT-BR para float (remove milhar, troca vírgula por ponto)."""
    v = (valor or '').strip()
    # remover espaços e símbolos
    v = v.replace('\u00A0', ' ').replace(' ', '')
    # remover separador de milhar '.' e trocar ',' por '.'
    v = v.replace('.', '').replace(',', '.')
    # remover quaisquer símbolos restantes
    v = v.replace('%', '')
    if v == '' or v == '-':
        return 0.0
    return float(v)


def _parse_volume_ptbr(v: str) -> Optional[int]:
    if not v:
        return None
    v = v.strip().replace('\u00A0', ' ')
    mult = 1
    if v.endswith('K'):
        mult = 1_000
        v = v[:-1]
    elif v.endswith('M'):
        mult = 1_000_000
        v = v[:-1]
    v = v.strip()
    # volume pode ter milhar e vírgula decimal
    num = _ptbr_to_float(v)
    return int(round(num * mult))


def _parse_data_ptbr(d: str) -> str:
    """
    Converte data PT-BR para formato ISO (YYYY-MM-DD).
    Aceita múltiplos formatos: dd.mm.yyyy, dd/mm/yyyy, dd-mm-yyyy
    """
    d = d.strip()
    # Tentar formatos comuns PT-BR
    formatos = ['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y']
    for fmt in formatos:
        try:
            dt = datetime.strptime(d, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue
    raise ValueError(f'Data não reconhecida: {d}. Formatos aceitos: dd.mm.yyyy, dd/mm/yyyy, dd-mm-yyyy')


def _abrir_dict_reader(caminho: Path) -> Tuple[csv.DictReader, Any]:
    """Tenta abrir um CSV detectando encoding e delimitador ("," ou ";")."""
    encodings = ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1')
    last_err: Optional[Exception] = None
    for enc in encodings:
        try:
            f = caminho.open('r', encoding=enc, newline='')
            sample = f.read(4096)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;')
            except Exception:
                dialect = csv.excel
            reader = csv.DictReader(f, dialect=dialect)
            return reader, f
        except Exception as e:
            last_err = e
            try:
                f.close()  # type: ignore
            except Exception:
                pass
            continue
    raise last_err or RuntimeError(f'Não foi possível abrir CSV: {caminho}')


def _ler_csv_diario(caminho: Path, instrumento: str, fonte: Optional[str]) -> List[RegistroDiario]:
    registros: List[RegistroDiario] = []
    reader, handle = _abrir_dict_reader(caminho)
    try:
        # Normalizar nomes de colunas removendo acentos e pontos
        def norm(k: str) -> str:
            k2 = (k or '').lstrip('\ufeff').strip()
            # remover aspas envolventes eventuais do cabeçalho
            if len(k2) >= 2 and k2[0] == '"' and k2[-1] == '"':
                k2 = k2[1:-1]
            mt = {
                'Data': 'data', 'DATA': 'data',
                'Último': 'ultimo', 'Ultimo': 'ultimo', 'ULTIMO': 'ultimo', 'ÚLTIMO': 'ultimo',
                'Abertura': 'abertura', 'ABERTURA': 'abertura',
                'Máxima': 'maxima', 'Maxima': 'maxima', 'MÁXIMA': 'maxima', 'MAXIMA': 'maxima',
                'Mínima': 'minima', 'Minima': 'minima', 'MÍNIMA': 'minima', 'MINIMA': 'minima',
                'Vol.': 'vol', 'Vol': 'vol', 'VOL.': 'vol', 'VOLUME': 'vol',
                'Var%': 'varpct', 'Variação%': 'varpct', 'Variacao%': 'varpct', 'VAR%': 'varpct',
            }
            return mt.get(k2, k2)
        # Mapear cabeçalho
        header_map = {norm(k): k for k in (reader.fieldnames or [])}
        required = ['data', 'ultimo', 'abertura', 'maxima', 'minima']
        for r in required:
            if r not in header_map:
                raise ValueError(f'Coluna obrigatória ausente no CSV: {r} (arquivo: {caminho.name}) | headers={reader.fieldnames}')
        for row in reader:
            try:
                data_iso = _parse_data_ptbr(row[header_map['data']])
                ultimo = _ptbr_to_float(row[header_map['ultimo']])
                abertura = _ptbr_to_float(row[header_map['abertura']])
                maxima = _ptbr_to_float(row[header_map['maxima']])
                minima = _ptbr_to_float(row[header_map['minima']])
                volume = _parse_volume_ptbr(row.get(header_map.get('vol', ''), '') if header_map.get('vol') else '')
                varpct_raw = row.get(header_map.get('varpct', ''), '') if header_map.get('varpct') else ''
                variacao_pct = None
                if varpct_raw:
                    # Ex: "0,03%" -> 0.0003 (fração)
                    variacao_pct = _ptbr_to_float(varpct_raw) / 100.0
                registros.append(RegistroDiario(
                    data=data_iso,
                    instrumento=instrumento,
                    ultimo=ultimo,
                    abertura=abertura,
                    maxima=maxima,
                    minima=minima,
                    volume=volume,
                    variacao_pct=variacao_pct,
                    fonte=fonte,
                    arquivo=caminho.name,
                ))
            except Exception as e:
                raise ValueError(f'Erro ao processar linha: {row} -> {e}')
    finally:
        try:
            handle.close()
        except Exception:
            pass
    return registros


@dataclass
class EstatisticasImportacao:
    """Resultado detalhado de uma importação de preços diários."""
    novos: int = 0
    atualizados: int = 0
    erros: int = 0
    total_processado: int = 0


def _inserir_precos_diarios(regs: Iterable[RegistroDiario], caminho_bd: Optional[Path] = None) -> EstatisticasImportacao:
    """
    Insere ou atualiza registros de preços diários usando INSERT OR REPLACE (UPSERT).

    Estratégia de unicidade:
    - O índice idx_precos_diarios_uniq garante um registro único por (data, instrumento, fonte).
    - Se houver conflito, o registro antigo é substituído (última importação vence).
    - Detecta se foi inserção nova ou atualização comparando rowcount com last_insert_rowid.

    Retorna:
        EstatisticasImportacao com contadores de novos, atualizados, erros e total processado.
    """
    inicializar_banco(caminho_bd)
    conn = _conectar(caminho_bd)
    try:
        cur = conn.cursor()
        stats = EstatisticasImportacao()

        for r in regs:
            stats.total_processado += 1
            try:
                # Verifica se já existe registro para detectar atualização vs inserção
                cur.execute(
                    """
                    SELECT id FROM precos_diarios
                    WHERE data = ? AND instrumento = ? AND ifnull(fonte, '') = ifnull(?, '')
                    """,
                    (r.data, r.instrumento, r.fonte)
                )
                ja_existe = cur.fetchone()

                # INSERT OR REPLACE: se existir, substitui; senão, insere
                cur.execute(
                    """
                    INSERT OR REPLACE INTO precos_diarios (
                        data, instrumento, ultimo, abertura, maxima, minima, volume,
                        variacao_pct, fonte, arquivo, inserido_em
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        r.data, r.instrumento, r.ultimo, r.abertura, r.maxima, r.minima,
                        r.volume, r.variacao_pct, r.fonte, r.arquivo, datetime.now(timezone.utc).isoformat()
                    )
                )

                # Classifica operação: se já existia, foi atualização; senão, novo registro
                if ja_existe:
                    stats.atualizados += 1
                else:
                    stats.novos += 1

            except Exception as e:
                stats.erros += 1
                print(f"      ❌ Erro ao processar registro {r.data}: {e}")

        conn.commit()
        return stats
    finally:
        conn.close()


def _coletar_fontes_csv(dir_base: Path) -> List[tuple[Path, str]]:
    """Coleta arquivos CSV e infere instrumento pelo nome da subpasta.
    Retorna lista de tuplas (arquivo_csv, instrumento).
    Regras:
    - Se houver CSVs diretamente em dir_base: usa instrumento = nome da pasta (ex.: WIN)
    - Senão, varre subpastas e usa nome da subpasta como instrumento
    """
    resultados: List[tuple[Path, str]] = []
    # CSVs diretamente na pasta
    arquivos_diretos = sorted([p for p in dir_base.glob('*.csv')])
    if arquivos_diretos:
        instrumento = dir_base.name
        for arq in arquivos_diretos:
            resultados.append((arq, instrumento))
        return resultados
    # Varrer subpastas
    for sub in sorted([p for p in dir_base.iterdir() if p.is_dir()]):
        instrumento = sub.name
        for arq in sorted(sub.glob('*.csv')):
            resultados.append((arq, instrumento))
    return resultados


def cmd_importar_diario(args: argparse.Namespace) -> None:
    # Determinar diretório base: por padrão, usar data/manual/WIN para facilitar
    if args.dir:
        base_dir = Path(args.dir)
    else:
        base_dir = DEFAULT_DIR
    base_dir.mkdir(parents=True, exist_ok=True)

    # Se arquivo único for passado, tentar inferir instrumento pela pasta-mãe se não informado
    fontes: List[tuple[Path, str]] = []
    if args.arquivo:
        arq = Path(args.arquivo)
        instrumento = args.instrumento or arq.parent.name or DEFAULT_INSTRUMENTO
        fontes = [(arq, instrumento)]
    else:
        # Coletar do diretório: aceita estrutura data/manual/WIN/*.csv ou data/manual/*/*.csv
        fontes = _coletar_fontes_csv(base_dir)

    if not fontes:
        print(f"\n⚠️  Nenhum CSV encontrado em: {base_dir}")
        print("   Estrutura esperada: data/manual/<ATIVO>/*.csv (ex.: data/manual/WIN/*.csv)")
        return

    stats_totais = EstatisticasImportacao()
    total_files = 0

    for arq, instrumento in fontes:
        print(f"\n📥 Lendo: {arq.name} | Instrumento: {instrumento}")
        regs = _ler_csv_diario(arq, instrumento, args.fonte)
        stats = _inserir_precos_diarios(regs)

        # Exibir estatísticas detalhadas do arquivo
        print(f"   📊 Processados: {stats.total_processado}")
        print(f"   ✨ Novos: {stats.novos}")
        print(f"   🔄 Atualizados: {stats.atualizados}")
        if stats.erros > 0:
            print(f"   ❌ Erros: {stats.erros}")

        # Acumular totais
        stats_totais.novos += stats.novos
        stats_totais.atualizados += stats.atualizados
        stats_totais.erros += stats.erros
        stats_totais.total_processado += stats.total_processado
        total_files += 1

    # Resumo final
    print(f"\n{'='*60}")
    print(f"✅ Importação concluída!")
    print(f"   📁 Arquivos: {total_files}")
    print(f"   📊 Total processado: {stats_totais.total_processado}")
    print(f"   ✨ Novos registros: {stats_totais.novos}")
    print(f"   🔄 Registros atualizados: {stats_totais.atualizados}")
    if stats_totais.erros > 0:
        print(f"   ❌ Erros: {stats_totais.erros}")
    print(f"{'='*60}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Importador CSV de preços diários (dados manuais)')
    sub = p.add_subparsers(dest='cmd')

    p_imp = sub.add_parser('importar-diario', help='Importar CSVs de preços diários para o banco')
    p_imp.add_argument('--arquivo', type=str, help='Caminho de um CSV único a importar')
    p_imp.add_argument('--dir', type=str, help='Diretório com CSVs (padrão: backend/data/manual/WIN). Aceita data/manual/*/*.csv')
    p_imp.add_argument('--instrumento', type=str, help='Identificador do instrumento (inferido pelo nome da pasta se ausente)')
    p_imp.add_argument('--fonte', type=str, default='manual', help='Fonte/Origem dos dados (ex: investing.com)')
    p_imp.set_defaults(func=cmd_importar_diario)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, 'func'):
        parser.print_help()
        return
    args.func(args)


if __name__ == '__main__':
    main()
