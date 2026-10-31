-- ============================================================================
-- AgriSense - Initialisation du schéma PostgreSQL et données de démonstration
-- ============================================================================

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

-- Index pour accélérer les recherches par parcelle, capteur et période
CREATE INDEX IF NOT EXISTS idx_capteurs_parcelle ON capteurs(parcelle_id);
CREATE INDEX IF NOT EXISTS idx_mesures_capteur_date ON mesures(capteur_id, measured_at DESC);
CREATE INDEX IF NOT EXISTS idx_alertes_mesure ON alertes(mesure_id);
CREATE INDEX IF NOT EXISTS idx_alertes_created_at ON alertes(created_at DESC);

-- ============================================================================
-- Données initiales (Parcelles et Capteurs de démonstration)
-- ============================================================================

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

