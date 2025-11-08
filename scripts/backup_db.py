"""Backup simples do banco SQLite + restore.

Uso:
  python scripts/backup_db.py backup --src backend/data/audit.sqlite --out backups/
  python scripts/backup_db.py restore --src backups/audit-2025-11-08.sqlite --dst backend/data/audit.sqlite
"""
import argparse
import os
import shutil
from datetime import datetime


def backup(src, out_dir):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    os.makedirs(out_dir, exist_ok=True)
    basename = os.path.basename(src)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    dst = os.path.join(out_dir, f"{os.path.splitext(basename)[0]}-{ts}.sqlite")
    shutil.copy2(src, dst)
    print(f"Backup created: {dst}")


def restore(src, dst):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"Restored {src} -> {dst}")


def cleanup_backups(out_dir, retain_days=30):
    """Remove backups antigos, mantendo apenas os últimos retain_days dias."""
    import glob
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=retain_days)
    pattern = os.path.join(out_dir, "*.sqlite")
    files = glob.glob(pattern)
    removed = 0
    for f in files:
        try:
            # Extrair timestamp do nome do arquivo
            basename = os.path.basename(f)
            ts_str = basename.split('-')[-1].replace('.sqlite', '')
            ts = datetime.strptime(ts_str, '%Y%m%dT%H%M%SZ')
            if ts < cutoff:
                os.remove(f)
                removed += 1
        except ValueError:
            pass  # Ignorar arquivos com nome inválido
    print(f"Cleanup: {removed} backups antigos removidos.")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')
    p1 = sub.add_parser('backup')
    p1.add_argument('--src', required=True)
    p1.add_argument('--out', required=True)
    p2 = sub.add_parser('restore')
    p2.add_argument('--src', required=True)
    p2.add_argument('--dst', required=True)
    p3 = sub.add_parser('cleanup')
    p3.add_argument('--dir', required=True)
    p3.add_argument('--retain-days', type=int, default=30)
    args = parser.parse_args()
    if args.cmd == 'backup':
        backup(args.src, args.out)
    elif args.cmd == 'restore':
        restore(args.src, args.dst)
    elif args.cmd == 'cleanup':
        cleanup_backups(args.dir, args.retain_days)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
