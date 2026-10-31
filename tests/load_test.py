"""
Script d'évaluation de performance et de test de charge (Section 18.4 du TRD).
Mesure le temps de réponse moyen, P95, le débit (req/s) et le taux d'erreurs
en augmentant le nombre de requêtes simultanées vers collection-service.
"""
import asyncio
import time
import random
import statistics
from datetime import datetime, timezone
import httpx

COLLECTION_URL = "http://localhost:8001/api/v1/measurements"
SENSORS = ["sensor-001", "sensor-002", "sensor-003", "sensor-004", "sensor-005"]


async def send_one_request(client: httpx.AsyncClient):
    payload = {
        "sensor_id": random.choice(SENSORS),
        "temperature": round(random.uniform(20.0, 38.0), 2),
        "soil_humidity": round(random.uniform(18.0, 60.0), 2),
        "air_humidity": round(random.uniform(25.0, 75.0), 2),
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }
    start = time.perf_counter()
    try:
        resp = await client.post(COLLECTION_URL, json=payload, timeout=10.0)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return resp.status_code in (200, 201), elapsed_ms
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return False, elapsed_ms


async def run_stage(concurrency: int, total_requests: int):
    semaphore = asyncio.Semaphore(concurrency)
    latencies = []
    successes = 0
    errors = 0

    async with httpx.AsyncClient() as client:
        async def worker():
            nonlocal successes, errors
            async with semaphore:
                ok, ms = await send_one_request(client)
                latencies.append(ms)
                if ok:
                    successes += 1
                else:
                    errors += 1

        t0 = time.perf_counter()
        await asyncio.gather(*(worker() for _ in range(total_requests)))
        total_duration = time.perf_counter() - t0

    avg_ms = statistics.mean(latencies) if latencies else 0.0
    p95_ms = (
        sorted(latencies)[int(0.95 * len(latencies)) - 1]
        if len(latencies) >= 2
        else avg_ms
    )
    rps = total_requests / total_duration if total_duration > 0 else 0.0
    error_rate = (errors / total_requests) * 100.0 if total_requests > 0 else 0.0

    return {
        "concurrency": concurrency,
        "total_requests": total_requests,
        "duration_s": round(total_duration, 2),
        "avg_ms": round(avg_ms, 2),
        "p95_ms": round(p95_ms, 2),
        "rps": round(rps, 2),
        "error_rate": round(error_rate, 2),
    }


async def main():
    print("=" * 80)
    print("AgriSense - Benchmark de Performance et Test de Charge (Section 18.4)")
    print(f"Cible : {COLLECTION_URL}")
    print("=" * 80)
    print(
        f"{'Clients simult.':<16} | {'Requêtes':<10} | {'Durée (s)':<10} | "
        f"{'Moy (ms)':<10} | {'P95 (ms)':<10} | {'Débit (req/s)':<14} | {'Erreurs (%)'}"
    )
    print("-" * 80)

    stages = [
        (5, 50),
        (10, 100),
        (25, 150),
        (50, 200),
    ]
    for concurrency, total_req in stages:
        res = await run_stage(concurrency, total_req)
        print(
            f"{res['concurrency']:<16} | {res['total_requests']:<10} | {res['duration_s']:<10} | "
            f"{res['avg_ms']:<10} | {res['p95_ms']:<10} | {res['rps']:<14} | {res['error_rate']}%"
        )
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

