from app.services.processor import detect_alerts, compute_descriptive_stats

DEFAULT_THRESHOLDS = {
    "temperature_max": 35.0,
    "soil_humidity_min": 25.0,
    "air_humidity_min": 30.0,
}


def test_detect_alerts_normal_values():
    measurement = {
        "temperature": 26.5,
        "soil_humidity": 42.0,
        "air_humidity": 55.0,
    }
    alerts = detect_alerts(measurement, DEFAULT_THRESHOLDS)
    assert len(alerts) == 0


def test_detect_alerts_high_temperature():
    measurement = {
        "temperature": 38.2,
        "soil_humidity": 42.0,
        "air_humidity": 55.0,
    }
    alerts = detect_alerts(measurement, DEFAULT_THRESHOLDS)
    assert len(alerts) == 1
    assert alerts[0]["indicateur"] == "temperature"
    assert alerts[0]["valeur"] == 38.2
    assert alerts[0]["seuil"] == 35.0


def test_detect_alerts_multiple_thresholds():
    measurement = {
        "temperature": 39.0,
        "soil_humidity": 18.5,
        "air_humidity": 22.0,
    }
    alerts = detect_alerts(measurement, DEFAULT_THRESHOLDS)
    assert len(alerts) == 3
    indicators = {a["indicateur"] for a in alerts}
    assert indicators == {"temperature", "soil_humidity", "air_humidity"}


def test_compute_descriptive_stats():
    records = [
        {"temperature": 20.0, "soil_humidity": 30.0, "air_humidity": 40.0},
        {"temperature": 30.0, "soil_humidity": 50.0, "air_humidity": 60.0},
    ]
    stats = compute_descriptive_stats(records)
    assert stats["count"] == 2
    assert stats["temperature"] == {"min": 20.0, "max": 30.0, "average": 25.0}
    assert stats["soil_humidity"] == {"min": 30.0, "max": 50.0, "average": 40.0}
    assert stats["air_humidity"] == {"min": 40.0, "max": 60.0, "average": 50.0}


def test_compute_descriptive_stats_empty():
    stats = compute_descriptive_stats([])
    assert stats["count"] == 0
    assert stats["temperature"]["min"] is None

