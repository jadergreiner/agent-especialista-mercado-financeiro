#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador simples de conteúdo em Português para arquivos Markdown.

Uso (pre-commit fornece a lista de arquivos modificados via argumentos):
    python scripts/check_portugues_docs.py <arquivos>

Regra:
- Cada arquivo .md analisado deve conter indícios mínimos de Português,
  como stopwords comuns ou caracteres acentuados típicos.

Limitações:
- Heurística simples; pode haver falso-positivo/negativo em casos extremos.
"""
from __future__ import annotations

import sys
from pathlib import Path

STOPWORDS_PT = {
    " de ", " em ", " para ", " com ", " que ", " por ", " não ", " uma ", " ao ", " é ",
    "ção", "ções", "ções ", "ções\n"
}

ACENTOS_PT = "áéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ"


def eh_markdown(caminho: Path) -> bool:
    sufixo = caminho.suffix.lower()
    return sufixo in {".md", ".mdx"}


def tem_portugues(texto: str) -> bool:
    t = f" {texto} "  # padding para encontrar stopwords com espaços
    # Indicadores por stopwords
    if any(sw in t for sw in STOPWORDS_PT):
        return True
    # Indicadores por acentos típicos
    if any(ch in texto for ch in ACENTOS_PT):
        return True
    return False


def verificar_arquivo(arquivo: Path) -> list[str]:
    erros: list[str] = []
    try:
        conteudo = arquivo.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [f"Não foi possível ler '{arquivo}': {e}"]

    if not tem_portugues(conteudo):
        erros.append(
            f"Arquivo sem indícios de Português: {arquivo}. \n"
            "Inclua texto explicativo em Português (ex.: título, resumo, comentários)."
        )
    return erros


def main() -> int:
    arquivos = [Path(a) for a in sys.argv[1:] if eh_markdown(Path(a))]
    if not arquivos:
        return 0

    erros_totais: list[str] = []
    for arq in arquivos:
        erros_totais.extend(verificar_arquivo(arq))

    if erros_totais:
        print("\n[ERRO] Falha na verificacao de Portugues (docs):\n")
        for e in erros_totais:
            print(f"- {e}")
        print("\n[INFO] Politica: Chats e dados devem estar SEMPRE em Portugues.")
        print("       Veja docs/knowledgebase.md e .github/copilot-instructions.md\n")
        return 1

    print("[OK] Verificacao de Portugues (docs) aprovada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
