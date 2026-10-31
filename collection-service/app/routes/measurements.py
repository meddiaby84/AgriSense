from fastapi import APIRouter, status
from app.schemas.measurement import MeasurementCreate, MeasurementResponse
from app.services.collector import store_and_forward_measurement
from app.db import get_db_connection

router = APIRouter(prefix="/api/v1", tags=["Collection"])


@router.post(
    "/measurements",
    response_model=MeasurementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Recevoir et valider une nouvelle mesure IoT",
)
def receive_measurement(payload: MeasurementCreate):
    return store_and_forward_measurement(payload)


@router.get("/health", summary="Vérifier l'état de santé du service de collecte")
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
        "service": "collection-service",
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }

