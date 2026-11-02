import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from app.config import settings
from app.db import get_db_connection
from app.schemas.models import EvaluateMeasurementRequest

logger = logging.getLogger(settings.SERVICE_NAME)


def detect_alerts(
    measurement: Dict[str, float], thresholds: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Évalue une mesure par rapport aux seuils configurés (Section 14.4).
    Fonction pure réutilisable pour les tests unitaires et le service.
    """
    alerts = []

    temp = float(measurement["temperature"])
    soil = float(measurement["soil_humidity"])
    air = float(measurement["air_humidity"])

    temp_max = float(thresholds["temperature_max"])
    soil_min = float(thresholds["soil_humidity_min"])
    air_min = float(thresholds["air_humidity_min"])

    if temp > temp_max:
        alerts.append(
            {
                "indicateur": "temperature",
                "valeur": round(temp, 2),
                "seuil": round(temp_max, 2),
                "message": f"Alerte de température élevée : {temp:.1f} °C > seuil {temp_max:.1f} °C",
            }
        )

    if soil < soil_min:
        alerts.append(
            {
                "indicateur": "soil_humidity",
                "valeur": round(soil, 2),
                "seuil": round(soil_min, 2),
                "message": f"Alerte de sol peu humide : {soil:.1f} % < seuil {soil_min:.1f} %",
            }
        )

    if air < air_min:
        alerts.append(
            {
                "indicateur": "air_humidity",
                "valeur": round(air, 2),
                "seuil": round(air_min, 2),
                "message": f"Alerte d'air peu humide : {air:.1f} % < seuil {air_min:.1f} %",
            }
        )

    return alerts


def compute_descriptive_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule les statistiques descriptives (min, max, moyenne) à partir d'une liste de mesures.
    Fonction pure testable unitairement.
    """
    if not records:
        return {
            "count": 0,
            "temperature": {"min": None, "max": None, "average": None},
            "soil_humidity": {"min": None, "max": None, "average": None},
            "air_humidity": {"min": None, "max": None, "average": None},
        }

    temps = [float(r["temperature"]) for r in records]
    soils = [float(r["soil_humidity"]) for r in records]
    airs = [float(r["air_humidity"]) for r in records]

    return {
        "count": len(records),
        "temperature": {
            "min": round(min(temps), 2),
            "max": round(max(temps), 2),
            "average": round(sum(temps) / len(temps), 2),
        },
        "soil_humidity": {
            "min": round(min(soils), 2),
            "max": round(max(soils), 2),
            "average": round(sum(soils) / len(soils), 2),
        },
        "air_humidity": {
            "min": round(min(airs), 2),
            "max": round(max(airs), 2),
            "average": round(sum(airs) / len(airs), 2),
        },
    }


def period_to_cutoff_datetime(period: Optional[str]) -> Optional[datetime]:
    mapping = {
        "last_15_minutes": timedelta(minutes=15),
        "last_1_hour": timedelta(hours=1),
        "last_6_hours": timedelta(hours=6),
        "last_24_hours": timedelta(hours=24),
        "last_7_days": timedelta(days=7),
        "last_30_days": timedelta(days=30),
    }
    if not period or period == "all":
        return None
    delta = mapping.get(period, timedelta(hours=24))
    return datetime.now(timezone.utc) - delta


def evaluate_and_store_alerts(req: EvaluateMeasurementRequest) -> Dict[str, Any]:
    triggered = detect_alerts(
        {
            "temperature": req.temperature,
            "soil_humidity": req.soil_humidity,
            "air_humidity": req.air_humidity,
        },
        settings.thresholds_dict,
    )

    saved_alerts = []
    if triggered:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    for alert in triggered:
                        cur.execute(
                            """
                            INSERT INTO alertes (mesure_id, indicateur, valeur, seuil, message, statut)
                            VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
                            RETURNING id, mesure_id, indicateur, valeur, seuil, message, created_at, statut;
                            """,
                            (
                                req.measurement_id,
                                alert["indicateur"],
                                alert["valeur"],
                                alert["seuil"],
                                alert["message"],
                            ),
                        )
                        saved_alerts.append(dict(cur.fetchone()))
                    conn.commit()
                    logger.warning(
                        f"{len(saved_alerts)} alerte(s) générée(s) pour la mesure #{req.measurement_id} ({req.sensor_id})"
                    )
        except Exception as db_err:
            logger.error(f"Erreur DB lors de l'enregistrement des alertes : {db_err}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Base de données inaccessible lors de l'enregistrement des alertes.",
            )

    return {
        "measurement_id": req.measurement_id,
        "sensor_id": req.sensor_id,
        "alerts_count": len(saved_alerts),
        "alerts": saved_alerts,
    }
