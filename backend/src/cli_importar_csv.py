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
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, List, Dict, Any

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
    # Ex: "04.11.2025" -> "2025-11-04"
    dt = datetime.strptime(d.strip(), '%d.%m.%Y')
    return dt.date().isoformat()


def _ler_csv_diario(caminho: Path, instrumento: str, fonte: Optional[str]) -> List[RegistroDiario]:
    registros: List[RegistroDiario] = []
    with caminho.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Normalizar nomes de colunas removendo acentos e pontos
        def norm(k: str) -> str:
            mt = {
                'Data': 'data',
                'Último': 'ultimo', 'Ultimo': 'ultimo',
                'Abertura': 'abertura',
                'Máxima': 'maxima', 'Maxima': 'maxima',
                'Mínima': 'minima', 'Minima': 'minima',
                'Vol.': 'vol', 'Vol': 'vol',
                'Var%': 'varpct', 'Variação%': 'varpct',
            }
            return mt.get(k.strip(), k.strip())
        # Mapear cabeçalho
        header_map = {norm(k): k for k in reader.fieldnames or []}
        required = ['data', 'ultimo', 'abertura', 'maxima', 'minima']
        for r in required:
            if r not in header_map:
                raise ValueError(f'Coluna obrigatória ausente no CSV: {r} (arquivo: {caminho.name})')
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
    return registros


def _inserir_precos_diarios(regs: Iterable[RegistroDiario], caminho_bd: Optional[Path] = None) -> int:
    inicializar_banco(caminho_bd)
    conn = _conectar(caminho_bd)
    try:
        cur = conn.cursor()
        inseridos = 0
        for r in regs:
            try:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO precos_diarios (
                        data, instrumento, ultimo, abertura, maxima, minima, volume,
                        variacao_pct, fonte, arquivo, inserido_em
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        r.data, r.instrumento, r.ultimo, r.abertura, r.maxima, r.minima,
                        r.volume, r.variacao_pct, r.fonte, r.arquivo, datetime.utcnow().isoformat()
                    )
                )
                if cur.rowcount:
                    inseridos += 1
            except Exception as e:
                raise
        conn.commit()
        return inseridos
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

    total_regs = 0
    total_files = 0
    for arq, instrumento in fontes:
        print(f"\n📥 Lendo: {arq} | Instrumento: {instrumento}")
        regs = _ler_csv_diario(arq, instrumento, args.fonte)
        qtd = _inserir_precos_diarios(regs)
        print(f"   ✓ Registros importados: {qtd}")
        total_regs += qtd
        total_files += 1
    print(f"\n✅ Importação concluída. Arquivos: {total_files} | Registros inseridos: {total_regs}")


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
