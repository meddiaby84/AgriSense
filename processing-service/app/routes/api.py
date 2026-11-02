from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.config import settings
from app.db import get_db_connection
from app.schemas.models import EvaluateMeasurementRequest
from app.services.processor import (
    evaluate_and_store_alerts,
    compute_descriptive_stats,
    period_to_cutoff_datetime,
)

router = APIRouter(prefix="/api/v1", tags=["Processing & Consultation"])


@router.post("/evaluate", summary="Évaluer les seuils d'une mesure et générer les alertes")
def evaluate_measurement(payload: EvaluateMeasurementRequest):
    return evaluate_and_store_alerts(payload)


@router.get("/parcels", summary="Consulter la liste des parcelles et leurs capteurs")
def list_parcels():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        p.id,
                        p.nom,
                        p.localisation,
                        p.created_at,
                        COUNT(DISTINCT c.id) AS total_sensors,
                        COUNT(DISTINCT CASE WHEN c.actif THEN c.id END) AS active_sensors
                    FROM parcelles p
                    LEFT JOIN capteurs c ON c.parcelle_id = p.id
                    GROUP BY p.id, p.nom, p.localisation, p.created_at
                    ORDER BY p.id;
                    """
                )
                return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de données inaccessible : {e}",
        )


@router.get("/sensors", summary="Consulter la liste des capteurs")
def list_sensors(parcel_id: Optional[str] = Query(default=None)):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if parcel_id:
                    cur.execute(
                        """
                        SELECT c.id, c.parcelle_id, p.nom AS parcelle_nom, c.nom, c.type, c.actif
                        FROM capteurs c
                        JOIN parcelles p ON p.id = c.parcelle_id
                        WHERE c.parcelle_id = %s
                        ORDER BY c.id;
                        """,
                        (parcel_id,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT c.id, c.parcelle_id, p.nom AS parcelle_nom, c.nom, c.type, c.actif
                        FROM capteurs c
                        JOIN parcelles p ON p.id = c.parcelle_id
                        ORDER BY c.id;
                        """
                    )
                return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de données inaccessible : {e}",
        )


@router.get("/measurements", summary="Consulter les mesures avec filtres (parcelle, capteur, période)")
def list_measurements(
    parcel_id: Optional[str] = Query(default=None),
    sensor_id: Optional[str] = Query(default=None),
    period: Optional[str] = Query(default="last_24_hours"),
    limit: int = Query(default=200, ge=1, le=2000),
):
    cutoff = period_to_cutoff_datetime(period)
    conditions = []
    params = []

    if parcel_id:
        conditions.append("c.parcelle_id = %s")
        params.append(parcel_id)
    if sensor_id:
        conditions.append("m.capteur_id = %s")
        params.append(sensor_id)
    if cutoff:
        conditions.append("m.measured_at >= %s")
        params.append(cutoff)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.append(limit)

    query = f"""
        SELECT
            m.id,
            m.capteur_id AS sensor_id,
            c.nom AS sensor_name,
            c.parcelle_id AS parcel_id,
            p.nom AS parcel_name,
            CAST(m.temperature AS FLOAT) AS temperature,
            CAST(m.humidite_sol AS FLOAT) AS soil_humidity,
            CAST(m.humidite_air AS FLOAT) AS air_humidity,
            m.measured_at,
            m.received_at
        FROM mesures m
        JOIN capteurs c ON c.id = m.capteur_id
        JOIN parcelles p ON p.id = c.parcelle_id
        {where_clause}
        ORDER BY m.measured_at DESC
        LIMIT %s;
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, tuple(params))
                return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de données inaccessible : {e}",
        )


@router.get("/measurements/{measurement_id}", summary="Consulter une mesure par son identifiant")
def get_measurement(measurement_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        m.id,
                        m.capteur_id AS sensor_id,
                        c.nom AS sensor_name,
                        c.parcelle_id AS parcel_id,
                        p.nom AS parcel_name,
                        CAST(m.temperature AS FLOAT) AS temperature,
                        CAST(m.humidite_sol AS FLOAT) AS soil_humidity,
                        CAST(m.humidite_air AS FLOAT) AS air_humidity,
                        m.measured_at,
                        m.received_at
                    FROM mesures m
                    JOIN capteurs c ON c.id = m.capteur_id
                    JOIN parcelles p ON p.id = c.parcelle_id
                    WHERE m.id = %s;
                    """,
                    (measurement_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Mesure #{measurement_id} introuvable.",
                    )
                return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de données inaccessible : {e}",
        )


@router.get("/parcels/{parcel_id}/measurements", summary="Consulter les mesures d'une parcelle")
def get_parcel_measurements(
    parcel_id: str,
    period: Optional[str] = Query(default="last_24_hours"),
    limit: int = Query(default=200, ge=1, le=2000),
):
    return list_measurements(
        parcel_id=parcel_id, sensor_id=None, period=period, limit=limit
    )


@router.get("/alerts", summary="Consulter les alertes déclenchées")
def list_alerts(
    parcel_id: Optional[str] = Query(default=None),
    sensor_id: Optional[str] = Query(default=None),
    period: Optional[str] = Query(default="last_24_hours"),
    limit: int = Query(default=100, ge=1, le=1000),
):
    cutoff = period_to_cutoff_datetime(period)
    conditions = []
    params = []

    if parcel_id:
        conditions.append("c.parcelle_id = %s")
        params.append(parcel_id)
    if sensor_id:
        conditions.append("m.capteur_id = %s")
        params.append(sensor_id)
    if cutoff:
        conditions.append("a.created_at >= %s")
        params.append(cutoff)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.append(limit)

    query = f"""
        SELECT
            a.id,
            a.mesure_id AS measurement_id,
            m.capteur_id AS sensor_id,
            c.nom AS sensor_name,
            c.parcelle_id AS parcel_id,
            p.nom AS parcel_name,
            a.indicateur,
            CAST(a.valeur AS FLOAT) AS valeur,
            CAST(a.seuil AS FLOAT) AS seuil,
            a.message,
            a.statut,
            m.measured_at,
            a.created_at
        FROM alertes a
        JOIN mesures m ON m.id = a.mesure_id
        JOIN capteurs c ON c.id = m.capteur_id
        JOIN parcelles p ON p.id = c.parcelle_id
        {where_clause}
        ORDER BY a.created_at DESC
        LIMIT %s;
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, tuple(params))
                return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de données inaccessible : {e}",
        )


@router.get("/statistics", summary="Consulter les indicateurs statistiques descriptifs")
def get_statistics(
    parcel_id: Optional[str] = Query(default=None),
    sensor_id: Optional[str] = Query(default=None),
    period: Optional[str] = Query(default="last_24_hours"),
):
    records = list_measurements(
        parcel_id=parcel_id, sensor_id=sensor_id, period=period, limit=2000
    )
    alerts = list_alerts(
        parcel_id=parcel_id, sensor_id=sensor_id, period=period, limit=1000
    )
    stats = compute_descriptive_stats(records)

    return {
        "parcel_id": parcel_id or "all",
        "sensor_id": sensor_id or "all",
        "period": period or "last_24_hours",
        "measurements_count": stats["count"],
        "alerts_count": len(alerts),
        "thresholds": settings.thresholds_dict,
        "temperature": stats["temperature"],
        "soil_humidity": stats["soil_humidity"],
        "air_humidity": stats["air_humidity"],
    }


@router.get("/health", summary="Vérifier l'état du service de traitement")
def health_check():
    db_ok = False
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                db_ok = True
    except Exception:
        db_ok = False

    return {
        "service": "processing-service",
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "thresholds": settings.thresholds_dict,
    }
