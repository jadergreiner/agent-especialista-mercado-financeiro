#!/usr/bin/env python3
"""
Script de Testes de Carga Simples (Smoke Load)
Valida latência e erros sob carga leve.

Origin: TASK-36 - Testes carga simples
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8000/api/v1/dashboard/summary"
CONCURRENT_REQUESTS = 10
TOTAL_REQUESTS = 100

def make_request():
    start = time.time()
    try:
        resp = requests.get(URL, timeout=5)
        latency = time.time() - start
        return resp.status_code, latency
    except Exception as e:
        return 0, time.time() - start

def main():
    latencies = []
    errors = 0

    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(make_request) for _ in range(TOTAL_REQUESTS)]
        for future in futures:
            status, latency = future.result()
            latencies.append(latency)
            if status != 200:
                errors += 1

    avg_latency = statistics.mean(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile

    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Errors: {errors}")
    print(f"Avg latency: {avg_latency:.2f}s")
    print(f"P95 latency: {p95_latency:.2f}s")

    if errors > 5 or avg_latency > 2:
        print("FAIL: Carga não suportada")
        return False
    else:
        print("PASS: Carga OK")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)