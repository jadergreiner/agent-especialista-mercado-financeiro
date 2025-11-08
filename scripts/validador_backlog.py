"""
Script de Validação do Backlog

Verifica se há pendências não registradas ou tarefas duplicadas no arquivo docs/gestao-agil/backlog.md.
"""
import re
from collections import Counter

BACKLOG_PATH = 'docs/gestao-agil/backlog.md'


def ler_backlog():
    with open(BACKLOG_PATH, encoding='utf-8') as f:
        return f.read()


def extrair_tarefas(texto):
    # Considera tarefas como linhas iniciadas por '- ' ou '* '
    linhas = texto.splitlines()
    tarefas = [l.strip('-* ').strip() for l in linhas if l.strip().startswith(('- ', '* '))]
    return tarefas


def verificar_duplicadas(tarefas):
    contagem = Counter(tarefas)
    return [t for t, c in contagem.items() if c > 1]


def main():
    texto = ler_backlog()
    tarefas = extrair_tarefas(texto)
    duplicadas = verificar_duplicadas(tarefas)
    print(f"Total de tarefas encontradas: {len(tarefas)}")
    if duplicadas:
        print("\nTarefas duplicadas:")
        for t in duplicadas:
            print(f"- {t}")
    else:
        print("\nNenhuma tarefa duplicada encontrada.")
    if not tarefas:
        print("\nAviso: Nenhuma tarefa encontrada no backlog!")

if __name__ == "__main__":
    main()
