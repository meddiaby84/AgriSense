# 🧪 Résultats Expérimentaux, Tests et Évaluation des Performances — AgriSense

**Date d'exécution :** 2 novembre 2026  
**Environnement d'exécution :** Windows 10/11 — Docker Desktop (WSL2 Linux x86_64, Python 3.11.18, PostgreSQL 16-alpine)  
**Architecture testée :** 5 conteneurs Docker interconnectés (`agrisense-postgres`, `agrisense-collection`, `agrisense-processing`, `agrisense-simulator`, `agrisense-dashboard`)

---

## 1. Résultats des Tests Unitaires (Section 18.1)

Les tests unitaires vérifient de manière isolée :
1. La validation Pydantic des mesures entrantes (`collection-service/tests/test_validation.py`).
2. La détection des dépassements de seuils et le calcul des statistiques descriptives (`processing-service/tests/test_processor.py`).

### Sortie d'exécution (`collection-service`)
```text
============================= test session starts ==============================
platform linux -- Python 3.11.18, pytest-8.3.3, pluggy-1.7.0
rootdir: /app
collected 4 items

tests/test_validation.py::test_valid_measurement_payload PASSED          [ 25%]
tests/test_validation.py::test_invalid_temperature_out_of_range PASSED   [ 50%]
tests/test_validation.py::test_invalid_humidity_negative PASSED          [ 75%]
tests/test_validation.py::test_empty_sensor_id PASSED                    [100%]

============================== 4 passed in 0.12s ===============================
```

### Sortie d'exécution (`processing-service`)
```text
============================= test session starts ==============================
platform linux -- Python 3.11.18, pytest-8.3.3, pluggy-1.7.0
rootdir: /app
collected 5 items

tests/test_processor.py::test_detect_alerts_normal_values PASSED         [ 20%]
tests/test_processor.py::test_detect_alerts_high_temperature PASSED      [ 40%]
tests/test_processor.py::test_detect_alerts_multiple_thresholds PASSED   [ 60%]
tests/test_processor.py::test_compute_descriptive_stats PASSED           [ 80%]
tests/test_processor.py::test_compute_descriptive_stats_empty PASSED     [100%]

============================== 5 passed in 0.49s ===============================
```

---

## 2. Résultats des Tests d'Intégration Bout-en-Bout (Section 18.2)

Les tests d'intégration (`tests/integration/test_integration.py`) vérifient la chaîne complète inter-services :
- État de santé (`/api/v1/health`) des services de collecte et de traitement + connexion PostgreSQL.
- Envoi d'une mesure dépassant deux seuils (`T = 38.4 °C > 35.0 °C` et `Sol = 19.5 % < 25.0 %`) à `collection-service`, persistance en base, appel synchrone à `processing-service`, création automatique des 2 alertes et relecture via `GET /api/v1/measurements/{id}` et `GET /api/v1/statistics`.
- Rejet HTTP `404 Not Found` pour un capteur non enregistré (`sensor-inexistant-999`).

### Sortie d'exécution
```text
============================= test session starts ==============================
platform linux -- Python 3.11.18, pytest-8.3.3, pluggy-1.7.0
collected 3 items

tests/test_integration.py::test_health_endpoints PASSED                  [ 33%]
tests/test_integration.py::test_end_to_end_measurement_and_alert PASSED  [ 66%]
tests/test_integration.py::test_reject_unknown_sensor PASSED             [100%]

============================== 3 passed in 0.32s ===============================
```

---

## 3. Test de Résilience et Tolérance aux Pannes (Section 18.3)

### Protocole expérimental
1. Arrêt volontaire du microservice de traitement : `docker compose stop processing-service`.
2. Envoi d'une nouvelle mesure IoT au service de collecte (`POST /api/v1/measurements`).
3. Vérification de la non-perte de la mesure (persistance garantie dans PostgreSQL) et du passage en **mode dégradé contrôlé** (`status: "accepted_degraded"`).
4. Redémarrage du service : `docker compose start processing-service` et vérification du retour à la normale.

### Trace expérimentale obtenue
```text
Container agrisense-processing Stopping 
Container agrisense-processing Stopped 
HTTP 201 {
  'status': 'accepted_degraded',
  'message': 'Measurement stored, but processing-service is currently unreachable',
  'measurement_id': 1241,
  'alerts_triggered': 0,
  'alerts': []
}
Container agrisense-processing Starting 
Container agrisense-processing Started
```

### Interprétation
- **Aucune perte de donnée IoT** : Même lorsque `processing-service` tombe en panne, `collection-service` intercepte l'exception `httpx.RequestError`, enregistre la mesure `#1241` dans PostgreSQL et retourne un code HTTP `201 Created` avec l'état explicite `accepted_degraded`.
- **Isolation des pannes** : Le simulateur et le service de collecte continuent de fonctionner sans crasher.

---

## 4. Mesure de Performance et Test de Charge (Section 18.4)

### Conditions du test
- **Outil :** Script asynchrone `tests/load_test.py` (`asyncio` + `httpx.AsyncClient`).
- **Route testée :** `POST http://collection-service:8000/api/v1/measurements` (incluant validation Pydantic, vérification du capteur dans PostgreSQL, insertion SQL `mesures`, appel REST inter-service vers `processing-service/api/v1/evaluate` et insertion SQL `alertes`).
- **Volume :** 4 paliers progressifs (5, 10, 25 et 50 clients simultanés), soit **500 requêtes complètes bout-en-bout**.

### Tableau des résultats mesurés

| Clients simultanés | Requêtes envoyées | Durée totale (s) | Temps moyen (ms) | Latence P95 (ms) | Débit (req/s) | Taux d'erreurs (%) |
|---:|---:|---:|---:|---:|---:|---:|
| **5** | 50 | 0,69 s | 63,98 ms | 92,26 ms | **72,19 req/s** | **0,0 %** |
| **10** | 100 | 0,90 s | 87,34 ms | 137,72 ms | **111,16 req/s** | **0,0 %** |
| **25** | 150 | 1,36 s | 214,77 ms | 282,43 ms | **110,63 req/s** | **0,0 %** |
| **50** | 200 | 1,76 s | 407,83 ms | 505,01 ms | **113,33 req/s** | **0,0 %** |

### Analyse et interprétation
1. **Fiabilité sous charge (0,0 % d'erreur) :** Sur l'ensemble des 500 requêtes concurrentes jusqu'à 50 capteurs simultanés, aucune requête n'a échoué (`0,0 %` d'erreur).
2. **Débit maximal (Throughput) :** Le débit passe de `72,19 req/s` (5 clients) à un plateau stable d'environ **`111 à 113 req/s`** dès 10 clients simultanés, soit une capacité de traitement de plus de **6 700 mesures par minute** sur un seul worker Uvicorn.
3. **Évolution de la latence :** La latence moyenne augmente linéairement avec la concurrence (`63,98 ms` pour 5 clients -> `407,83 ms` pour 50 clients) car chaque requête effectue deux transactions PostgreSQL et un appel HTTP synchrone inter-services. Pour dépasser `500 req/s`, il suffirait d'augmenter le nombre de workers Uvicorn (`--workers 4`) et d'utiliser un pool de connexions PostgreSQL.
