import os
import time
import random
import logging
from datetime import datetime, timezone
from typing import Dict, Any
import httpx

COLLECTION_SERVICE_URL = os.getenv(
    "COLLECTION_SERVICE_URL", "http://collection-service:8000"
)
SIMULATION_INTERVAL_SECONDS = float(os.getenv("SIMULATION_INTERVAL_SECONDS", "5"))
SIMULATION_ANOMALY_PROBABILITY = float(
    os.getenv("SIMULATION_ANOMALY_PROBABILITY", "0.25")
)
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "5.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | simulator | %(message)s",
)
logger = logging.getLogger("simulator")

# Capteurs actifs associés aux 3 parcelles (définis dans database/init.sql)
ACTIVE_SENSORS = [
    {"sensor_id": "sensor-001", "parcel_id": "parcel-001", "base_temp": 26.0, "base_soil": 42.0, "base_air": 52.0},
    {"sensor_id": "sensor-002", "parcel_id": "parcel-001", "base_temp": 27.5, "base_soil": 39.0, "base_air": 49.0},
    {"sensor_id": "sensor-003", "parcel_id": "parcel-002", "base_temp": 29.0, "base_soil": 34.0, "base_air": 45.0},
    {"sensor_id": "sensor-004", "parcel_id": "parcel-002", "base_temp": 30.0, "base_soil": 31.0, "base_air": 43.0},
    {"sensor_id": "sensor-005", "parcel_id": "parcel-003", "base_temp": 25.0, "base_soil": 48.0, "base_air": 58.0},
]


def generate_measurement(sensor_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Génère une mesure réaliste pour un capteur donné.
    Avec une probabilité `SIMULATION_ANOMALY_PROBABILITY`, simule un dépassement de seuil
    (stress hydrique ou coup de chaud) pour démontrer la détection d'alertes.
    """
    is_anomaly = random.random() < SIMULATION_ANOMALY_PROBABILITY

    if is_anomaly:
        anomaly_type = random.choice(["heatwave", "dry_soil", "dry_air", "combined"])
        if anomaly_type == "heatwave":
            temp = random.uniform(35.5, 41.5)
            soil = sensor_profile["base_soil"] + random.uniform(-4.0, 4.0)
            air = sensor_profile["base_air"] + random.uniform(-5.0, 5.0)
        elif anomaly_type == "dry_soil":
            temp = sensor_profile["base_temp"] + random.uniform(-2.0, 3.0)
            soil = random.uniform(14.0, 24.2)
            air = sensor_profile["base_air"] + random.uniform(-5.0, 5.0)
        elif anomaly_type == "dry_air":
            temp = sensor_profile["base_temp"] + random.uniform(-1.0, 4.0)
            soil = sensor_profile["base_soil"] + random.uniform(-4.0, 4.0)
            air = random.uniform(18.0, 29.2)
        else:
            temp = random.uniform(36.0, 40.5)
            soil = random.uniform(16.0, 23.5)
            air = random.uniform(20.0, 28.5)
    else:
        temp = min(34.2, sensor_profile["base_temp"] + random.uniform(-3.0, 3.5))
        soil = max(26.5, sensor_profile["base_soil"] + random.uniform(-5.0, 6.0))
        air = max(31.5, sensor_profile["base_air"] + random.uniform(-6.0, 6.0))

    return {
        "sensor_id": sensor_profile["sensor_id"],
        "temperature": round(temp, 2),
        "soil_humidity": round(soil, 2),
        "air_humidity": round(air, 2),
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }


def send_measurement_with_retry(payload: Dict[str, Any]) -> bool:
    """
    Envoie une mesure au service de collecte avec gestion des erreurs et tentatives limitées
    (Section 15.2 & 15.3 : pas de boucle infinie, backoff progressif).
    """
    endpoint = f"{COLLECTION_SERVICE_URL}/api/v1/measurements"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS) as client:
                response = client.post(endpoint, json=payload)
                if response.status_code in (200, 201):
                    data = response.json()
                    logger.info(
                        f"[OK] Capteur={payload['sensor_id']} | T={payload['temperature']}°C, "
                        f"Sol={payload['soil_humidity']}%, Air={payload['air_humidity']}% "
                        f"-> ID={data.get('measurement_id')} (Alertes={data.get('alerts_triggered', 0)})"
                    )
                    return True
                else:
                    logger.warning(
                        f"[REJET HTTP {response.status_code}] Capteur={payload['sensor_id']} : {response.text}"
                    )
                    return False
        except httpx.TimeoutException:
            logger.error(
                f"[TIMEOUT] Tentative {attempt}/{MAX_RETRIES} dépassée ({HTTP_TIMEOUT_SECONDS}s) "
                f"vers {endpoint} pour {payload['sensor_id']}"
            )
        except httpx.RequestError as exc:
            logger.error(
                f"[INDISPONIBLE] Tentative {attempt}/{MAX_RETRIES} échouée vers {endpoint} : {exc}"
            )

        if attempt < MAX_RETRIES:
            backoff = 1.5 * attempt
            time.sleep(backoff)

    logger.error(
        f"[ABANDON] Impossible de transmettre la mesure de {payload['sensor_id']} après {MAX_RETRIES} tentatives."
    )
    return False


def run_simulation_loop():
    logger.info(
        f"Démarrage du simulateur IoT AgriSense -> Cible: {COLLECTION_SERVICE_URL} "
        f"(Intervalle: {SIMULATION_INTERVAL_SECONDS}s, Capteurs actifs: {len(ACTIVE_SENSORS)})"
    )
    cycle = 0
    while True:
        cycle += 1
        sensor_profile = random.choice(ACTIVE_SENSORS)
        measurement = generate_measurement(sensor_profile)
        send_measurement_with_retry(measurement)
        time.sleep(SIMULATION_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_simulation_loop()

