#!/usr/bin/env python3
"""
Script de Retenção e Rotação de Audit DB
Deleta registros antigos e compacta DB.

Origin: TASK-26 - Retenção rotação audit DB
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "backend" / "data" / "audit.sqlite"
RETENTION_DAYS = 90

def main():
    if not DB_PATH.exists():
        print("Audit DB não encontrado.")
        return

    cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    cutoff_str = cutoff.isoformat()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Deletar registros antigos
    cur.execute("DELETE FROM audit_events WHERE timestamp < ?", (cutoff_str,))
    deleted = cur.rowcount
    conn.commit()

    # Compactar DB
    cur.execute("VACUUM")
    conn.commit()
    conn.close()

    print(f"Retenção aplicada: {deleted} registros deletados. DB compactado.")

if __name__ == "__main__":
    main()