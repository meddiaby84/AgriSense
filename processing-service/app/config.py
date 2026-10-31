import os


class Settings:
    SERVICE_NAME: str = "processing-service"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://agrisense_user:agrisense_dev_pwd@postgres:5432/agrisense",
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Seuils configurables centralisés (Section 5 & Section 14.4)
    THRESHOLD_TEMPERATURE_MAX: float = float(
        os.getenv("THRESHOLD_TEMPERATURE_MAX", "35.0")
    )
    THRESHOLD_SOIL_HUMIDITY_MIN: float = float(
        os.getenv("THRESHOLD_SOIL_HUMIDITY_MIN", "25.0")
    )
    THRESHOLD_AIR_HUMIDITY_MIN: float = float(
        os.getenv("THRESHOLD_AIR_HUMIDITY_MIN", "30.0")
    )

    @property
    def thresholds_dict(self):
        return {
            "temperature_max": self.THRESHOLD_TEMPERATURE_MAX,
            "soil_humidity_min": self.THRESHOLD_SOIL_HUMIDITY_MIN,
            "air_humidity_min": self.THRESHOLD_AIR_HUMIDITY_MIN,
        }


settings = Settings()

