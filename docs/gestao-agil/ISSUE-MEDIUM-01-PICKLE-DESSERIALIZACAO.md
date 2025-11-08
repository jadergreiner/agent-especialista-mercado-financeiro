---
title: "ISSUE: Remediar desserialização insegura com pickle"
labels: [security, severity-medium]
---

# Resumo

Localização: `backend/carregador_dados_historicos.py`

O scanner de segurança reportou uso de `pickle.loads` para desserialização de dados (linha ~608). Desserializar objetos arbitrários com `pickle` é inseguro quando a origem dos bytes não é totalmente confiável.

## Evidência

Trecho relevante:

```python
dados_bytes = gzip.decompress(dados_comprimidos)
dados_dict = pickle.loads(dados_bytes)
```

## Risco

- Execução arbitrária de código se um atacante controlar os bytes serializados.
- Comprometimento da integridade/confidencialidade do ambiente.

## Remediação sugerida

1. Evitar `pickle` para dados vindos de fontes externas. Preferir formatos seguros (JSON, msgpack com validação) ou protobufs.
2. Se for imprescindível manter `pickle`, garantir assinatura e verificação dos dados (HMAC) e validação estrita do conteúdo antes da desserialização.
3. Implementar validação do schema pós-desserialização (p.ex. pydantic) e filtros de tipo.

## Critérios de aceitação

- Substituir esta chamada por uma desserialização segura ou adicionar verificação criptográfica dos dados.
- Testes unitários que demonstrem que dados malformados/assinados incorretamente são rejeitados.
- Revisão de segurança confirmando que o vetor foi mitigado.

## Prioridade

Alta para segurança (atualmente marcado Medium pelo scanner, confiança: HIGH).

## Sugestão de dono

Equipe: `backend` / responsável: @time-backend (atribuir conforme organização)

## Notas

Manter logs de auditoria para operações de leitura/desserialização enquanto a mudança é implantada.
