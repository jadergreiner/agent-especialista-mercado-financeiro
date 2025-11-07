#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Contratos - Prompt-First v1

Valida estrutura de contratos mínimos de resposta (Forex/Cripto).
"""
from typing import Dict, Any, List, Tuple


class ValidadorContrato:
    """Valida contratos mínimos de resposta."""

    CAMPOS_OBRIGATORIOS_COMUM = [
        'classe_ativo',
        'par',
        'timeframe',
        'timestamp',
        'resumo'
    ]

    CAMPOS_OBRIGATORIOS_RESUMO = [
        'preco_atual',
        'operacao',
        'entrada',
        'alvo1',
        'stop'
    ]

    OPERACOES_VALIDAS = {'COMPRA', 'VENDA', 'ESPERAR'}

    @classmethod
    def validar(cls, payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida contrato mínimo.

        Returns:
            (valido, lista_erros)
        """
        erros = []

        # Valida campos obrigatórios raiz
        for campo in cls.CAMPOS_OBRIGATORIOS_COMUM:
            if campo not in payload:
                erros.append(f"Campo obrigatório ausente: {campo}")

        # Valida resumo
        if 'resumo' in payload:
            resumo = payload['resumo']
            if not isinstance(resumo, dict):
                erros.append("Campo 'resumo' deve ser um dicionário")
            else:
                for campo in cls.CAMPOS_OBRIGATORIOS_RESUMO:
                    if campo not in resumo:
                        erros.append(f"Campo obrigatório ausente em resumo: {campo}")

                # Valida operação
                if 'operacao' in resumo:
                    operacao = resumo['operacao']
                    if operacao not in cls.OPERACOES_VALIDAS:
                        erros.append(f"Operação inválida: '{operacao}'. Deve ser uma de: {cls.OPERACOES_VALIDAS}")

        # Valida tipos básicos
        if 'classe_ativo' in payload and not isinstance(payload['classe_ativo'], str):
            erros.append("Campo 'classe_ativo' deve ser string")

        if 'par' in payload and not isinstance(payload['par'], str):
            erros.append("Campo 'par' deve ser string")

        if 'resumo' in payload and isinstance(payload['resumo'], dict):
            resumo = payload['resumo']
            for campo_numerico in ['preco_atual', 'entrada', 'alvo1', 'stop']:
                if campo_numerico in resumo:
                    valor = resumo[campo_numerico]
                    if not isinstance(valor, (int, float)):
                        erros.append(f"Campo 'resumo.{campo_numerico}' deve ser numérico")

        return (len(erros) == 0, erros)

    @classmethod
    def validar_e_imprimir(cls, payload: Dict[str, Any], label: str = "Contrato") -> bool:
        """Valida e imprime resultado."""
        valido, erros = cls.validar(payload)

        if valido:
            print(f"✅ {label}: VÁLIDO")
        else:
            print(f"❌ {label}: INVÁLIDO")
            for erro in erros:
                print(f"   - {erro}")

        return valido


# Exemplo de uso
if __name__ == '__main__':
    # Contrato válido - Forex
    contrato_forex_valido = {
        'classe_ativo': 'forex',
        'par': 'EURUSD',
        'timeframe': 'intraday',
        'timestamp': '2025-11-06T12:00:00Z',
        'resumo': {
            'preco_atual': 1.0765,
            'operacao': 'COMPRA',
            'entrada': 1.0750,
            'alvo1': 1.0800,
            'stop': 1.0720,
            'rr': '1:1.6',
            'riscos_chave': ['volatilidade'],
            'proximos_passos': ['aguardar_pullback']
        },
        'justificativas': ['DXY em recuo']
    }

    # Contrato inválido - campo ausente
    contrato_invalido = {
        'classe_ativo': 'cripto',
        'par': 'BTCUSDT',
        'resumo': {
            'preco_atual': 68500.00,
            'operacao': 'INVALIDA',  # operação inválida
            'entrada': 68600.00
            # falta alvo1 e stop
        }
    }

    print("=" * 70)
    print("TESTE DE VALIDAÇÃO DE CONTRATOS")
    print("=" * 70)

    print("\n1. Contrato Forex válido:")
    ValidadorContrato.validar_e_imprimir(contrato_forex_valido, "Forex")

    print("\n2. Contrato inválido (campos ausentes e operação inválida):")
    ValidadorContrato.validar_e_imprimir(contrato_invalido, "Cripto")

    print("\n" + "=" * 70)
