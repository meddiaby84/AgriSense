import os


class Settings:
    SERVICE_NAME: str = "collection-service"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://agrisense_user:agrisense_dev_pwd@postgres:5432/agrisense",
    )
    PROCESSING_SERVICE_URL: str = os.getenv(
        "PROCESSING_SERVICE_URL", "http://processing-service:8000"
    )
    HTTP_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "5.0"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Plages physiques acceptables pour la validation technique (Section 14.2)
    TEMP_MIN_VALID: float = -40.0
    TEMP_MAX_VALID: float = 80.0
    HUMIDITY_MIN_VALID: float = 0.0
    HUMIDITY_MAX_VALID: float = 100.0


settings = Settings()

