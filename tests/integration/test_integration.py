import os
from datetime import datetime, timezone
import httpx
import pytest

COLLECTION_URL = os.getenv("COLLECTION_SERVICE_URL", "http://localhost:8001")
PROCESSING_URL = os.getenv("PROCESSING_SERVICE_URL", "http://localhost:8002")


def is_stack_online() -> bool:
    try:
        r1 = httpx.get(f"{COLLECTION_URL}/api/v1/health", timeout=2.0)
        r2 = httpx.get(f"{PROCESSING_URL}/api/v1/health", timeout=2.0)
        return r1.status_code == 200 and r2.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not is_stack_online(),
    reason="Les services Docker (localhost:8001 et localhost:8002) ne sont pas démarrés.",
)


def test_health_endpoints():
    r_col = httpx.get(f"{COLLECTION_URL}/api/v1/health")
    assert r_col.status_code == 200
    assert r_col.json()["status"] == "healthy"

    r_proc = httpx.get(f"{PROCESSING_URL}/api/v1/health")
    assert r_proc.status_code == 200
    assert r_proc.json()["status"] == "healthy"


def test_end_to_end_measurement_and_alert():
    payload = {
        "sensor_id": "sensor-001",
        "temperature": 38.4,  # > 35.0 -> Doit déclencher une alerte
        "soil_humidity": 19.5,  # < 25.0 -> Doit déclencher une alerte
        "air_humidity": 45.0,
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }
    resp = httpx.post(f"{COLLECTION_URL}/api/v1/measurements", json=payload, timeout=5.0)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "accepted"
    assert data["alerts_triggered"] >= 2
    measurement_id = data["measurement_id"]

    # Vérifier que la mesure est consultable via processing-service
    r_get = httpx.get(f"{PROCESSING_URL}/api/v1/measurements/{measurement_id}")
    assert r_get.status_code == 200
    assert r_get.json()["sensor_id"] == "sensor-001"

    # Vérifier les statistiques
    r_stats = httpx.get(
        f"{PROCESSING_URL}/api/v1/statistics", params={"parcel_id": "parcel-001"}
    )
    assert r_stats.status_code == 200
    assert r_stats.json()["measurements_count"] >= 1


def test_reject_unknown_sensor():
    payload = {
        "sensor_id": "sensor-inexistant-999",
        "temperature": 25.0,
        "soil_humidity": 40.0,
        "air_humidity": 50.0,
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }
    resp = httpx.post(f"{COLLECTION_URL}/api/v1/measurements", json=payload, timeout=5.0)
    assert resp.status_code == 404

