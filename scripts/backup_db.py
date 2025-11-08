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


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')
    p1 = sub.add_parser('backup')
    p1.add_argument('--src', required=True)
    p1.add_argument('--out', required=True)
    p2 = sub.add_parser('restore')
    p2.add_argument('--src', required=True)
    p2.add_argument('--dst', required=True)
    args = parser.parse_args()
    if args.cmd == 'backup':
        backup(args.src, args.out)
    elif args.cmd == 'restore':
        restore(args.src, args.dst)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
