from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EvaluateMeasurementRequest(BaseModel):
    measurement_id: int
    sensor_id: str
    temperature: float
    soil_humidity: float
    air_humidity: float
    measured_at: Optional[datetime] = None


class IndicatorStats(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    average: Optional[float] = None

