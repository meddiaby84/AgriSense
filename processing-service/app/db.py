import sqlite3
from contextlib import contextmanager
from app.config import settings

POSTGRES_INIT_SCRIPT = """
CREATE TABLE IF NOT EXISTS parcelles (
    id VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    localisation VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS capteurs (
    id VARCHAR(50) PRIMARY KEY,
    parcelle_id VARCHAR(50) NOT NULL REFERENCES parcelles(id) ON DELETE CASCADE,
    nom VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'multicapteur-agro',
    actif BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS mesures (
    id BIGSERIAL PRIMARY KEY,
    capteur_id VARCHAR(50) NOT NULL REFERENCES capteurs(id) ON DELETE CASCADE,
    temperature NUMERIC(6,2) NOT NULL,
    humidite_sol NUMERIC(6,2) NOT NULL,
    humidite_air NUMERIC(6,2) NOT NULL,
    measured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alertes (
    id BIGSERIAL PRIMARY KEY,
    mesure_id BIGINT NOT NULL REFERENCES mesures(id) ON DELETE CASCADE,
    indicateur VARCHAR(50) NOT NULL,
    valeur NUMERIC(8,2) NOT NULL,
    seuil NUMERIC(8,2) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(30) NOT NULL DEFAULT 'ACTIVE'
);

INSERT INTO parcelles (id, nom, localisation) VALUES
    ('parcel-001', 'Parcelle Nord - Blé Dur', 'Zone Nord-Est (Secteur A1)'),
    ('parcel-002', 'Parcelle Sud - Maraîchage Tomates', 'Zone Sud (Serre Ouverte B2)'),
    ('parcel-003', 'Parcelle Ouest - Verger Agrumes', 'Zone Ouest (Coteau C1)')
ON CONFLICT (id) DO NOTHING;

INSERT INTO capteurs (id, parcelle_id, nom, type, actif) VALUES
    ('sensor-001', 'parcel-001', 'Capteur Nord-1 (Sol & Air)', 'Station-Agro-THS', TRUE),
    ('sensor-002', 'parcel-001', 'Capteur Nord-2 (Sol & Air)', 'Station-Agro-THS', TRUE),
    ('sensor-003', 'parcel-002', 'Capteur Maraîchage-1', 'Station-Agro-THS', TRUE),
    ('sensor-004', 'parcel-002', 'Capteur Maraîchage-2', 'Station-Agro-THS', TRUE),
    ('sensor-005', 'parcel-003', 'Capteur Verger-1', 'Station-Agro-THS', TRUE),
    ('sensor-006', 'parcel-003', 'Capteur Verger-Maintenance', 'Station-Agro-THS', FALSE)
ON CONFLICT (id) DO NOTHING;
"""

SQLITE_INIT_SCRIPT = """
CREATE TABLE IF NOT EXISTS parcelles (
    id VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    localisation VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS capteurs (
    id VARCHAR(50) PRIMARY KEY,
    parcelle_id VARCHAR(50) NOT NULL REFERENCES parcelles(id) ON DELETE CASCADE,
    nom VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'multicapteur-agro',
    actif BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS mesures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capteur_id VARCHAR(50) NOT NULL REFERENCES capteurs(id) ON DELETE CASCADE,
    temperature NUMERIC(6,2) NOT NULL,
    humidite_sol NUMERIC(6,2) NOT NULL,
    humidite_air NUMERIC(6,2) NOT NULL,
    measured_at TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mesure_id INTEGER NOT NULL REFERENCES mesures(id) ON DELETE CASCADE,
    indicateur VARCHAR(50) NOT NULL,
    valeur NUMERIC(8,2) NOT NULL,
    seuil NUMERIC(8,2) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(30) NOT NULL DEFAULT 'ACTIVE'
);

INSERT OR IGNORE INTO parcelles (id, nom, localisation) VALUES
    ('parcel-001', 'Parcelle Nord - Blé Dur', 'Zone Nord-Est (Secteur A1)'),
    ('parcel-002', 'Parcelle Sud - Maraîchage Tomates', 'Zone Sud (Serre Ouverte B2)'),
    ('parcel-003', 'Parcelle Ouest - Verger Agrumes', 'Zone Ouest (Coteau C1)');

INSERT OR IGNORE INTO capteurs (id, parcelle_id, nom, type, actif) VALUES
    ('sensor-001', 'parcel-001', 'Capteur Nord-1 (Sol & Air)', 'Station-Agro-THS', 1),
    ('sensor-002', 'parcel-001', 'Capteur Nord-2 (Sol & Air)', 'Station-Agro-THS', 1),
    ('sensor-003', 'parcel-002', 'Capteur Maraîchage-1', 'Station-Agro-THS', 1),
    ('sensor-004', 'parcel-002', 'Capteur Maraîchage-2', 'Station-Agro-THS', 1),
    ('sensor-005', 'parcel-003', 'Capteur Verger-1', 'Station-Agro-THS', 1),
    ('sensor-006', 'parcel-003', 'Capteur Verger-Maintenance', 'Station-Agro-THS', 0);
"""

_postgres_initialized = False


class SQLiteCursorWrapper:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cur = cursor

    def execute(self, sql: str, params=None):
        adapted_sql = sql.replace("%s", "?")
        if params is not None:
            p_list = [
                p.isoformat() if hasattr(p, "isoformat") else p for p in params
            ]
            return self._cur.execute(adapted_sql, tuple(p_list))
        return self._cur.execute(adapted_sql)

    def fetchone(self):
        row = self._cur.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(r) for r in self._cur.fetchall()]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cur.close()


class SQLiteConnectionWrapper:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path, timeout=15.0, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SQLITE_INIT_SCRIPT)
        self._conn.commit()

    def cursor(self):
        return SQLiteCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


@contextmanager
def get_db_connection():
    global _postgres_initialized
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "", 1)
        conn = SQLiteConnectionWrapper(db_path)
        try:
            yield conn
        finally:
            conn.close()
    else:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        try:
            if not _postgres_initialized:
                with conn.cursor() as cur:
                    cur.execute(POSTGRES_INIT_SCRIPT)
                conn.commit()
                _postgres_initialized = True
            yield conn
        finally:
            conn.close()
