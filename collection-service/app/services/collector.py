import logging
from typing import Dict, Any
import httpx
import psycopg2
from fastapi import HTTPException, status
from app.config import settings
from app.db import get_db_connection
from app.schemas.measurement import MeasurementCreate

logger = logging.getLogger(settings.SERVICE_NAME)


def store_and_forward_measurement(payload: MeasurementCreate) -> Dict[str, Any]:
    """
    1. Vérifie l'existence et l'état actif du capteur dans PostgreSQL.
    2. Insère la mesure horodatée dans la table `mesures`.
    3. Notifie le service de traitement (`processing-service`) via HTTP/REST
       pour évaluer les seuils et générer les alertes éventuelles.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, parcelle_id, nom, actif FROM capteurs WHERE id = %s;",
                    (payload.sensor_id,),
                )
                sensor = cur.fetchone()
                if not sensor:
                    logger.warning(f"Capteur inconnu rejeté : {payload.sensor_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Capteur inconnu : '{payload.sensor_id}'",
                    )

                if not sensor["actif"]:
                    logger.warning(f"Capteur inactif rejeté : {payload.sensor_id}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Le capteur '{payload.sensor_id}' est inactif.",
                    )

                cur.execute(
                    """
                    INSERT INTO mesures (capteur_id, temperature, humidite_sol, humidite_air, measured_at)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, received_at;
                    """,
                    (
                        payload.sensor_id,
                        payload.temperature,
                        payload.soil_humidity,
                        payload.air_humidity,
                        payload.measured_at,
                    ),
                )
                inserted = cur.fetchone()
                measurement_id = inserted["id"]
                conn.commit()
                logger.info(
                    f"Mesure #{measurement_id} enregistrée pour le capteur {payload.sensor_id} "
                    f"(T={payload.temperature}°C, Sol={payload.soil_humidity}%, Air={payload.air_humidity}%)"
                )

    except HTTPException:
        raise
    except psycopg2.Error as db_err:
        logger.error(f"Erreur d'accès à PostgreSQL lors de la collecte : {db_err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de données temporairement inaccessible.",
        )

    # Appel HTTP synchrone au service de traitement pour évaluer les seuils
    alerts_triggered = 0
    alert_messages = []
    processing_status = "accepted"
    response_message = "Measurement received and processed"

    try:
        eval_url = f"{settings.PROCESSING_SERVICE_URL}/api/v1/evaluate"
        with httpx.Client(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            resp = client.post(
                eval_url,
                json={
                    "measurement_id": measurement_id,
                    "sensor_id": payload.sensor_id,
                    "temperature": payload.temperature,
                    "soil_humidity": payload.soil_humidity,
                    "air_humidity": payload.air_humidity,
                    "measured_at": payload.measured_at.isoformat(),
                },
            )
            resp.raise_for_status()
            eval_data = resp.json()
            alerts_triggered = eval_data.get("alerts_count", 0)
            alert_messages = [a.get("message", "") for a in eval_data.get("alerts", [])]
    except httpx.TimeoutException:
        logger.error(
            f"Timeout lors de l'appel à processing-service pour la mesure #{measurement_id}"
        )
        processing_status = "accepted_degraded"
        response_message = (
            "Measurement stored, but processing-service timed out during threshold check"
        )
    except httpx.RequestError as req_err:
        logger.error(
            f"Service de traitement indisponible pour la mesure #{measurement_id}: {req_err}"
        )
        processing_status = "accepted_degraded"
        response_message = (
            "Measurement stored, but processing-service is currently unreachable"
        )
    except httpx.HTTPStatusError as http_err:
        logger.error(
            f"Erreur HTTP de processing-service pour la mesure #{measurement_id}: {http_err}"
        )
        processing_status = "accepted_degraded"
        response_message = "Measurement stored, but processing-service returned an error"

    return {
        "status": processing_status,
        "message": response_message,
        "measurement_id": measurement_id,
        "alerts_triggered": alerts_triggered,
        "alerts": alert_messages,
    }

