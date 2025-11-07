#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feed Resolver - Sistema de Resolução de Feeds Alternativos
Responsável por mapear tickers problemáticos para feeds confiáveis
"""

import json
import yfinance as yf
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

class FeedResolver:
    """Resolve feeds alternativos para tickers problemáticos"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'ticker_mapping.json')

        self.config_path = config_path
        self.config = self._load_config()
        self.cache = {}

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração de mapeamento"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão caso arquivo não exista"""
        return {
            "ticker_mapping": {
                "mappings": {
                    "XAUUSD": {
                        "primary_ticker": "GC=F",
                        "fallback_tickers": ["GOLD"],
                        "conversion_factor": 1.0
                    }
                }
            },
            "feed_config": {
                "cache_duration_seconds": 30,
                "retry_attempts": 3
            }
        }

    def resolver_ticker(self, original_ticker: str) -> Optional[float]:
        """
        Resolve ticker usando mapeamento e fallbacks

        Args:
            original_ticker: Ticker original (ex: XAUUSD)

        Returns:
            Preço atual ou None se falhar
        """
        print(f"🔍 Resolvendo ticker: {original_ticker}")

        # Verificar cache
        cache_key = original_ticker
        if self._is_cache_valid(cache_key):
            cached_price = self.cache[cache_key]['price']
            print(f"📋 Cache hit: {original_ticker} = ${cached_price:.2f}")
            return cached_price

        # Buscar mapeamento
        mapping = self._get_mapping(original_ticker)
        if not mapping:
            print(f"❌ Sem mapeamento para: {original_ticker}")
            return None

        # Tentar ticker primário
        primary = mapping['primary_ticker']
        price = self._fetch_price(primary)
        if price:
            price = price * mapping.get('conversion_factor', 1.0)
            self._cache_price(cache_key, price, primary)
            print(f"✅ {original_ticker} → {primary} = ${price:.2f}")
            return price

        # Tentar fallbacks
        for fallback in mapping.get('fallback_tickers', []):
            price = self._fetch_price(fallback)
            if price:
                price = price * mapping.get('conversion_factor', 1.0)
                self._cache_price(cache_key, price, fallback)
                print(f"✅ {original_ticker} → {fallback} (fallback) = ${price:.2f}")
                return price

        print(f"❌ Todos os feeds falharam para: {original_ticker}")
        return None

    def _get_mapping(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Busca mapeamento para ticker"""
        mappings = self.config.get('ticker_mapping', {}).get('mappings', {})
        return mappings.get(ticker)

    def _fetch_price(self, ticker: str) -> Optional[float]:
        """Busca preço de um ticker específico"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')

            if len(hist) > 0:
                price = float(hist['Close'].iloc[-1])
                if self._validate_price(ticker, price):
                    return price
                else:
                    print(f"⚠️ Preço inválido para {ticker}: ${price:.2f}")

        except Exception as e:
            print(f"❌ Erro ao buscar {ticker}: {str(e)[:50]}")

        return None

    def _validate_price(self, ticker: str, price: float) -> bool:
        """Valida se preço está em range aceitável"""
        if 'GC' in ticker or 'GOLD' in ticker or 'XAU' in ticker:
            # Validação específica para ouro
            validation = self.config.get('validation', {}).get('gold_price_range', {})
            min_price = validation.get('min', 1500)
            max_price = validation.get('max', 5000)
            return min_price <= price <= max_price

        return price > 0  # Validação genérica

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se cache ainda é válido"""
        if cache_key not in self.cache:
            return False

        cache_duration = self.config.get('feed_config', {}).get('cache_duration_seconds', 30)
        cache_time = self.cache[cache_key]['timestamp']

        return datetime.now() - cache_time < timedelta(seconds=cache_duration)

    def _cache_price(self, cache_key: str, price: float, source_ticker: str):
        """Armazena preço no cache"""
        self.cache[cache_key] = {
            'price': price,
            'timestamp': datetime.now(),
            'source': source_ticker
        }

    def get_cache_info(self) -> Dict[str, Any]:
        """Retorna informações do cache"""
        return {
            'cached_tickers': list(self.cache.keys()),
            'cache_size': len(self.cache),
            'last_updates': {k: v['timestamp'].isoformat() for k, v in self.cache.items()}
        }

# Instância global para reutilização
feed_resolver = FeedResolver()

def resolver_cotacao_ouro(ticker: str) -> Optional[float]:
    """Função simplificada para resolver cotação de ouro"""
    return feed_resolver.resolver_ticker(ticker)

if __name__ == "__main__":
    # Teste básico
    resolver = FeedResolver()

    print("🧪 TESTE DO FEED RESOLVER")
    print("=" * 40)

    # Testar XAUUSD
    preco = resolver.resolver_ticker("XAUUSD")
    if preco:
        print(f"✅ XAUUSD resolvido: ${preco:.2f}")
    else:
        print("❌ Falha ao resolver XAUUSD")

    # Mostrar info do cache
    cache_info = resolver.get_cache_info()
    print(f"📋 Cache: {cache_info}")