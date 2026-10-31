# 🌱 AgriSense — Plateforme distribuée de supervision et d'analyse des données IoT agricoles

**Module :** Systèmes répartis et distribués (Master ADIA)

AgriSense est une architecture distribuée conteneurisée permettant de simuler des capteurs agricoles répartis sur plusieurs parcelles, de collecter et valider leurs mesures via une API REST, de calculer des indicateurs statistiques, de détecter des dépassements de seuils en temps réel et de visualiser l'ensemble dans un tableau de bord interactif.

---

## 1. Architecture des services

| Service | Rôle | Technologie | Port Hôte |
|---|---|---|---|
| `simulator` | Génère périodiquement des mesures IoT (température, humidité sol/air) avec gestion de retry/timeout | Python, HTTPX | — |
| `collection-service` | Réceptionne (`POST /api/v1/measurements`), valide (Pydantic + existence capteur), stocke et transmet au service de traitement | FastAPI, Psycopg2, HTTPX | `8001` |
| `processing-service` | Évalue les seuils d'alerte, calcule les statistiques (`min`, `max`, `moyenne`) et expose les API de consultation | FastAPI, Psycopg2 | `8002` |
| `postgres` | Persistance relationnelle (`parcelles`, `capteurs`, `mesures`, `alertes`) | PostgreSQL 16 | `5432` |
| `dashboard` | Interface de supervision à 4 pages (consomme uniquement les API REST) | Streamlit, Plotly, Pandas | `8501` |

---

## 2. Démarrage rapide avec Docker Compose

### Prérequis
- Docker et Docker Compose installés.

### Lancement
```bash
# 1. Copier le fichier d'environnement si nécessaire
cp .env.example .env

# 2. Construire et démarrer l'ensemble des 5 conteneurs
docker compose up --build -d

# 3. Vérifier l'état des conteneurs
docker compose ps
```

### Accès aux interfaces
- **Tableau de bord Streamlit :** http://localhost:8501
- **Swagger UI — Service de collecte :** http://localhost:8001/docs
- **Swagger UI — Service de traitement :** http://localhost:8002/docs

---

## 3. Exécution des tests

### 3.1. Tests unitaires (Validation & Détection de seuils)
```bash
# Depuis les conteneurs ou un environnement Python local :
pytest collection-service/tests/ processing-service/tests/
```

### 3.2. Tests d'intégration bout-en-bout
Avec la stack Docker démarrée :
```bash
pytest tests/integration/test_integration.py
```

### 3.3. Mesure de performance et test de charge
```bash
python tests/load_test.py
```

---

## 4. Scénario de démonstration de panne et résilience (Section 18.3)

1. **Arrêter le service de traitement :**
   ```bash
   docker compose stop processing-service
   ```
   - Le `collection-service` continue d'accepter et d'enregistrer les mesures dans PostgreSQL en mode dégradé (`status: accepted_degraded`) sans perte de données, tout en journalisant le timeout/indisponibilité.
   - Le `dashboard` affiche l'état `🔴 Indisponible` pour le service de traitement.

2. **Arrêter le service de collecte :**
   ```bash
   docker compose stop collection-service
   ```
   - Le `simulator` détecte l'échec réseau, applique sa politique de *retry* avec *backoff* (`MAX_RETRIES=3`), journalise l'incident sans crasher, puis reprend automatiquement dès que le service redémarre :
   ```bash
   docker compose start processing-service collection-service
   ```

