# 📘 Rapport Technique — Projet AgriSense

**Titre :** Conception et développement d'une plateforme distribuée de supervision et d'analyse des données IoT agricoles  
**Formation :** Master d'Excellence — Analytics des données et Intelligence Artificielle (ADIA)  
**Module :** Systèmes répartis et distribués  
**Auteur :** Mohamed DIABY (`meddiaby84`)  
**Dépôt GitHub :** https://github.com/meddiaby84/AgriSense  

---

## 1. Contexte et Problématique
La supervision agricole moderne nécessite le suivi continu de paramètres environnementaux critiques (température ambiante, humidité du sol, humidité de l'air) répartis sur plusieurs parcelles géographiques. Une architecture monolithique classique présente des limites en matière de passage à l'échelle, d'isolation des pannes et de découplage entre l'ingestion IoT haute fréquence et l'analytique métier.

**Problématique traitée :**
> *Comment concevoir une plateforme distribuée capable de collecter, valider, stocker et analyser en temps réel des flux IoT agricoles multi-parcelles, tout en garantissant la tolérance aux pannes inter-services et la reproductibilité du déploiement ?*

---

## 2. Architecture Distribuée Retenue

La plateforme **AgriSense** repose sur **5 composants conteneurisés indépendants** orchestrés via `Docker Compose` :

1. **`simulator` (Python / HTTPX)** : Simule 5 capteurs actifs répartis sur 3 parcelles agricoles. Génère périodiquement des mesures JSON horodatées en UTC et gère les pannes réseau grâce à une politique de *retry avec backoff progressif* (`MAX_RETRIES=3`, `HTTP_TIMEOUT_SECONDS=5.0`).
2. **`collection-service` (FastAPI — Port `8001`)** : Point d'entrée IoT (`POST /api/v1/measurements`). Assure la validation technique (schémas Pydantic et plages physiques), vérifie l'existence et l'état actif du capteur dans PostgreSQL, persiste la mesure brute et notifie le service de traitement par HTTP REST.
3. **`processing-service` (FastAPI — Port `8002`)** : Moteur d'analyse descriptive (`min`, `max`, `average`) et d'évaluation des seuils agronomiques (`Température > 35 °C`, `Humidité sol < 25 %`, `Humidité air < 30 %`). Génère automatiquement les alertes dans la table `alertes` et expose les routes REST de consultation pour le tableau de bord.
4. **`postgres` (PostgreSQL 16)** : Système de gestion de base de données relationnelle assurant l'intégrité référentielle entre les 4 tables (`parcelles`, `capteurs`, `mesures`, `alertes`).
5. **`dashboard` (Streamlit + Plotly — Port `8501`)** : Interface web de supervision à 4 vues consommant **exclusivement** les API REST des services (`collection-service` et `processing-service`), sans aucun accès direct à la base de données.

---

## 3. Modèle de Données Relationnel

Le schéma relationnel (`database/init.sql`) comprend 4 entités principales :
- **`parcelles`** (`id`, `nom`, `localisation`, `created_at`) : 3 parcelles initialisées (`parcel-001` Blé Dur, `parcel-002` Maraîchage Tomates, `parcel-003` Verger Agrumes).
- **`capteurs`** (`id`, `parcelle_id`, `nom`, `type`, `actif`) : 6 capteurs initialisés (`sensor-001` à `sensor-005` actifs, et `sensor-006` en maintenance avec `actif = FALSE`).
- **`mesures`** (`id`, `capteur_id`, `temperature`, `humidite_sol`, `humidite_air`, `measured_at`, `received_at`) : Stocke les mesures validées avec double horodatage (émission capteur et réception serveur).
- **`alertes`** (`id`, `mesure_id`, `indicateur`, `valeur`, `seuil`, `message`, `created_at`, `statut`) : Historise chaque dépassement de seuil lié à une mesure.

---

## 4. Distinction Validation Technique vs Alerte Métier

Conformément à la section 14.2 du TRD, AgriSense distingue strictement :
1. **Les données techniquement invalides (rejetées avant stockage)** :
   - Valeurs physiquement impossibles (`température ∉ [-40, 80] °C` ou `humidité ∉ [0, 100] %`) -> Rejet **HTTP `422 Unprocessable Entity`**.
   - Capteur inconnu (`sensor-999`) -> Rejet **HTTP `404 Not Found`**.
   - Capteur en maintenance (`sensor-006`, `actif = FALSE`) -> Rejet **HTTP `400 Bad Request`**.
2. **Les valeurs critiques mais valides (stockées + déclenchement d'alerte)** :
   - Exemple : `Température = 38.4 °C`, `Humidité sol = 19.5 %` -> Mesure acceptée (**HTTP `201 Created`**), stockée dans `mesures`, et création de 2 entrées dans `alertes`.

---

## 5. Gestion des Pannes et Résilience (Systèmes Distribués)

Deux mécanismes complémentaires de résilience ont été implémentés et vérifiés expérimentalement :
- **Mode dégradé sur `collection-service`** : Si `processing-service` est arrêté ou dépasse le délai d'attente (`timeout`), `collection-service` conserve la mesure enregistrée dans PostgreSQL et renvoie `status: "accepted_degraded"` (HTTP 201) au lieu de provoquer une erreur 500 ou de perdre la mesure.
- **Retry avec Backoff sur `simulator`** : Si `collection-service` est arrêté, le simulateur journalise l'incident et effectue jusqu'à 3 tentatives espacées (`1.5s`, `3.0s`, `4.5s`) avant de passer au cycle suivant sans interrompre son exécution.

---

## 6. Synthèse des Tests et Performances

L'ensemble des résultats détaillés est disponible dans [`docs/resultats_experimentaux.md`](./resultats_experimentaux.md) :
- **Tests unitaires :** `9/9 PASSED` (`4 passed` sur `collection-service`, `5 passed` sur `processing-service`).
- **Tests d'intégration :** `3/3 PASSED` sur l'environnement Docker actif.
- **Benchmark de charge (500 requêtes jusqu'à 50 clients simultanés) :** Débit soutenu de **`113,33 req/s`**, temps de réponse moyen de **`63,98 ms`** à faible charge (`407,83 ms` à 50 clients simultanés) et **`0,0 %` d'erreur**.
