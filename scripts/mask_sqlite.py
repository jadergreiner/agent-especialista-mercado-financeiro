"""Script simples para gerar uma cópia mascarada de um banco SQLite.

Uso:
  python scripts/mask_sqlite.py --src backend/data/app.sqlite --dst backend/data/app_masked.sqlite

Regras de mascaramento: por coluna nome padrão (name,email,cpf) são mascarados.
"""
import argparse
import sqlite3
import os
import shutil


def mask_value(col, val):
    if val is None:
        return None
    key = col.lower()
    if "email" in key:
        parts = val.split("@")
        return parts[0][:1] + "***@" + (parts[1] if len(parts) > 1 else "masked")
    if "name" in key:
        return val[0] + "***"
    if "cpf" in key or "ssn" in key or "document" in key:
        return "***-***-" + str(val)[-4:]
    return val


def mask_db(src, dst):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copy2(src, dst)
    conn = sqlite3.connect(dst)
    cur = conn.cursor()
    # descobrir tabelas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cur.fetchall()]
    for t in tables:
        # pegar colunas
        cur.execute(f"PRAGMA table_info('{t}')")
        cols = [r[1] for r in cur.fetchall()]
        col_list = ",".join(cols)
        cur.execute(f"SELECT rowid, {col_list} FROM {t}")
        rows = cur.fetchall()
        for row in rows:
            rowid = row[0]
            values = list(row[1:])
            changed = False
            for i, c in enumerate(cols):
                newv = mask_value(c, values[i])
                if newv != values[i]:
                    values[i] = newv
                    changed = True
            if changed:
                placeholders = ",".join(["?" for _ in cols])
                set_clause = ",".join([f"{c}=?" for c in cols])
                cur.execute(f"UPDATE {t} SET {set_clause} WHERE rowid = ?", values + [rowid])
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    args = parser.parse_args()
    mask_db(args.src, args.dst)
    print(f"Masked DB created: {args.dst}")


if __name__ == '__main__':
    main()
