import pytest
from pydantic import ValidationError
from app.schemas.measurement import MeasurementCreate


def test_valid_measurement_payload():
    m = MeasurementCreate(
        sensor_id="sensor-001",
        temperature=32.5,
        soil_humidity=22.4,
        air_humidity=48.2,
        measured_at="2026-11-01T10:30:00Z",
    )
    assert m.sensor_id == "sensor-001"
    assert m.temperature == 32.5
    assert m.soil_humidity == 22.4
    assert m.air_humidity == 48.2


def test_invalid_temperature_out_of_range():
    with pytest.raises(ValidationError):
        MeasurementCreate(
            sensor_id="sensor-001",
            temperature=125.0,  # Hors plage [-40, 80]
            soil_humidity=40.0,
            air_humidity=50.0,
            measured_at="2026-11-01T10:30:00Z",
        )


def test_invalid_humidity_negative():
    with pytest.raises(ValidationError):
        MeasurementCreate(
            sensor_id="sensor-001",
            temperature=25.0,
            soil_humidity=-5.0,  # Hors plage [0, 100]
            air_humidity=50.0,
            measured_at="2026-11-01T10:30:00Z",
        )


def test_empty_sensor_id():
    with pytest.raises(ValidationError):
        MeasurementCreate(
            sensor_id="   ",
            temperature=25.0,
            soil_humidity=40.0,
            air_humidity=50.0,
            measured_at="2026-11-01T10:30:00Z",
        )

