from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.config import settings


class MeasurementCreate(BaseModel):
    sensor_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Identifiant unique du capteur émetteur (ex: sensor-001)",
    )
    temperature: float = Field(
        ...,
        description="Température mesurée en degrés Celsius (°C)",
    )
    soil_humidity: float = Field(
        ...,
        description="Humidité du sol en pourcentage (%)",
    )
    air_humidity: float = Field(
        ...,
        description="Humidité de l'air en pourcentage (%)",
    )
    measured_at: datetime = Field(
        ...,
        description="Date et heure ISO 8601 de la mesure",
    )

    @field_validator("sensor_id")
    @classmethod
    def validate_sensor_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("L'identifiant du capteur ne peut pas être vide.")
        return cleaned

    @field_validator("temperature")
    @classmethod
    def validate_temperature_range(cls, value: float) -> float:
        if not (settings.TEMP_MIN_VALID <= value <= settings.TEMP_MAX_VALID):
            raise ValueError(
                f"Température techniquement invalide ({value} °C). "
                f"Plage acceptée : [{settings.TEMP_MIN_VALID}, {settings.TEMP_MAX_VALID}] °C."
            )
        return round(value, 2)

    @field_validator("soil_humidity", "air_humidity")
    @classmethod
    def validate_humidity_range(cls, value: float) -> float:
        if not (settings.HUMIDITY_MIN_VALID <= value <= settings.HUMIDITY_MAX_VALID):
            raise ValueError(
                f"Humidité techniquement invalide ({value} %). "
                f"Plage acceptée : [{settings.HUMIDITY_MIN_VALID}, {settings.HUMIDITY_MAX_VALID}] %."
            )
        return round(value, 2)


class MeasurementResponse(BaseModel):
    status: str
    message: str
    measurement_id: int
    alerts_triggered: Optional[int] = 0
    alerts: Optional[List[str]] = None

