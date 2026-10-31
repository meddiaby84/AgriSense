# PRD & TRD

## Conception et développement d'une plateforme distribuée de supervision et d'analyse des données IoT agricoles

**Version :** 1.0\
**Date :** 31 octobre 2026\
**Type de document :** Product Requirements Document (PRD) et Technical
Requirements Document (TRD)\
**Contexte académique :** Master d'Excellence --- Analytics des données
et Intelligence artificielle (ADIA)\
**Module :** Systèmes répartis et distribués

------------------------------------------------------------------------

# Partie I --- PRD (Product Requirements Document)

## 1. Présentation du produit

### 1.1. Nom du produit

**AgriSense --- Plateforme distribuée de supervision et d'analyse des
données IoT agricoles**

### 1.2. Résumé

AgriSense est une application destinée à collecter, traiter, stocker et
visualiser des données provenant de capteurs agricoles simulés. La
plateforme permet de suivre plusieurs parcelles agricoles à partir de
mesures telles que la température, l'humidité du sol et l'humidité de
l'air.

L'application repose sur plusieurs services indépendants qui
communiquent par API REST. Elle fournit un tableau de bord permettant de
consulter les mesures, de suivre leur évolution et de détecter les
dépassements de seuils prédéfinis.

Pour respecter le cadre du projet académique, les capteurs seront
simulés par un programme logiciel. Aucun matériel IoT physique n'est
nécessaire pour le prototype.

### 1.3. Problématique

Le suivi manuel des conditions environnementales des parcelles peut
rendre difficile la détection rapide de changements susceptibles
d'affecter les cultures. Il est donc utile de disposer d'un système
capable de collecter régulièrement des mesures, de les centraliser, de
les analyser et de signaler automatiquement certaines situations
anormales.

La problématique technique du projet est la suivante :

> Comment concevoir une plateforme distribuée capable de collecter et de
> traiter des données IoT agricoles provenant de plusieurs sources, tout
> en assurant la communication entre services, la disponibilité du
> système, la gestion des erreurs et la visualisation des données ?

### 1.4. Objectif général

Concevoir et développer un prototype distribué permettant de simuler des
capteurs agricoles, de collecter leurs mesures, de les stocker, de les
analyser et de les présenter dans une interface de supervision.

### 1.5. Objectifs spécifiques

-   Simuler plusieurs capteurs associés à différentes parcelles.
-   Générer des mesures de température, d'humidité du sol et d'humidité
    de l'air.
-   Transmettre les mesures à un service de collecte via une API REST.
-   Valider et enregistrer les mesures dans une base de données.
-   Détecter les mesures dépassant des seuils configurés.
-   Afficher les données récentes et leur évolution dans un tableau de
    bord.
-   Gérer les erreurs de communication et l'indisponibilité d'un
    service.
-   Tester le fonctionnement, l'intégration et les performances de la
    plateforme.
-   Déployer les composants de manière reproductible.

## 2. Utilisateurs et parties prenantes

### 2.1. Utilisateurs cibles

**Exploitant agricole (utilisateur principal)**\
Consulte les conditions mesurées sur ses parcelles et repère les
situations nécessitant une attention particulière.

**Responsable de supervision**\
Suit les mesures de plusieurs parcelles, consulte les alertes et vérifie
l'état général de la plateforme.

**Équipe de développement et enseignant**\
Évalue l'architecture distribuée, les échanges entre services, les
tests, le déploiement et les résultats expérimentaux.

### 2.2. Parties prenantes

-   Les membres de l'équipe projet.
-   L'enseignant responsable du module.
-   Les utilisateurs représentés dans le prototype.
-   Les personnes chargées de l'évaluation et de la soutenance.

## 3. Périmètre fonctionnel

### 3.1. Fonctionnalités incluses (MVP)

  -----------------------------------------------------------------------
  ID                Fonctionnalité    Description       Priorité
  ----------------- ----------------- ----------------- -----------------
  F01               Simulation des    Générer           Haute
                    capteurs          automatiquement   
                                      des mesures       
                                      fictives pour     
                                      plusieurs         
                                      capteurs.         

  F02               Identification    Associer chaque   Haute
                    des parcelles     capteur à une     
                                      parcelle          
                                      identifiée.       

  F03               Collecte des      Recevoir les      Haute
                    mesures           mesures           
                                      transmises par le 
                                      service de        
                                      simulation.       

  F04               Validation des    Vérifier les      Haute
                    données           champs            
                                      obligatoires, les 
                                      types et les      
                                      valeurs           
                                      acceptables.      

  F05               Stockage          Enregistrer les   Haute
                                      mesures           
                                      horodatées dans   
                                      une base de       
                                      données.          

  F06               Analyse           Calculer des      Haute
                    descriptive       indicateurs       
                                      simples :         
                                      minimum, maximum  
                                      et moyenne.       

  F07               Détection par     Déclencher une    Haute
                    seuils            alerte lorsqu'une 
                                      mesure dépasse un 
                                      seuil configuré.  

  F08               Tableau de bord   Afficher les      Haute
                                      mesures, les      
                                      indicateurs, les  
                                      graphiques et les 
                                      alertes.          

  F09               Consultation      Filtrer les       Moyenne
                    historique        mesures par       
                                      parcelle, capteur 
                                      et période.       

  F10               Gestion des       Signaler les      Haute
                    erreurs           erreurs de        
                                      communication et  
                                      permettre une     
                                      reprise           
                                      contrôlée.        

  F11               Tests et mesures  Exécuter des      Haute
                                      tests             
                                      fonctionnels,     
                                      d'intégration et  
                                      une mesure de     
                                      charge.           
  -----------------------------------------------------------------------

### 3.2. Fonctionnalités optionnelles

Ces fonctionnalités ne seront développées que si le MVP est stable et
que le temps le permet :

-   Authentification des utilisateurs.
-   Export des mesures au format CSV.
-   Carte géographique des parcelles.
-   Détection statistique d'anomalies au-delà des simples seuils.
-   Prédiction de l'évolution d'une mesure.
-   Notifications par e-mail ou SMS.
-   Connexion à de vrais capteurs physiques.

### 3.3. Hors périmètre

Le prototype ne vise pas à :

-   Piloter automatiquement des équipements d'irrigation.
-   Fournir des recommandations agronomiques certifiées.
-   Garantir une précision issue de capteurs physiques.
-   Entraîner un modèle complexe d'intelligence artificielle.
-   Déployer une infrastructure cloud à grande échelle.
-   Remplacer un système professionnel de gestion agricole.

## 4. Parcours utilisateur principaux

### 4.1. Consulter l'état d'une parcelle

1.  L'utilisateur ouvre le tableau de bord.
2.  Il sélectionne une parcelle.
3.  L'application affiche les dernières mesures disponibles.
4.  L'utilisateur consulte les graphiques d'évolution.
5.  Il vérifie si des alertes sont associées à cette parcelle.

### 4.2. Détecter une situation nécessitant une attention

1.  Le simulateur génère une mesure.
2.  Le service de collecte reçoit et valide la mesure.
3.  Le service de traitement compare la valeur au seuil configuré.
4.  Si le seuil est dépassé, une alerte est enregistrée.
5.  Le tableau de bord affiche l'alerte avec la parcelle, le capteur, la
    valeur et l'heure.

### 4.3. Consulter l'historique

1.  L'utilisateur choisit une parcelle ou un capteur.
2.  Il sélectionne une période.
3.  L'application récupère les mesures correspondantes.
4.  Les résultats sont présentés sous forme de tableau et de graphique.

## 5. Règles métier

1.  Chaque capteur possède un identifiant unique.
2.  Chaque capteur est associé à une parcelle.
3.  Chaque mesure est associée à un capteur et possède une date et une
    heure.
4.  Une mesure doit contenir au minimum la température, l'humidité du
    sol et l'humidité de l'air, selon le format retenu.
5.  Une mesure invalide ne doit pas être enregistrée comme une mesure
    valide.
6.  Les seuils sont configurables et doivent être documentés.
7.  Une alerte est créée lorsqu'une mesure franchit le seuil
    correspondant.
8.  Les données historiques doivent rester consultables.
9.  Les valeurs simulées sont identifiées comme telles dans l'interface
    et dans la documentation.

**Seuils initiaux proposés pour la démonstration :**

  Indicateur              Exemple de seuil Interprétation
  ------------------- -------------------- ------------------------------
  Température           Supérieure à 35 °C Alerte de température élevée
  Humidité du sol        Inférieure à 25 % Alerte de sol peu humide
  Humidité de l'air      Inférieure à 30 % Alerte d'air peu humide

Ces valeurs sont uniquement des paramètres de démonstration. Elles ne
constituent pas des recommandations agronomiques universelles et devront
être ajustées ou justifiées par l'équipe.

## 6. Exigences non fonctionnelles

  -----------------------------------------------------------------------
  ID                      Exigence                Attendu pour le
                                                  prototype
  ----------------------- ----------------------- -----------------------
  NF01                    Modularité              Les composants sont
                                                  séparés en services
                                                  indépendants.

  NF02                    Communication           Les services
                                                  communiquent par API
                                                  REST/HTTP.

  NF03                    Maintenabilité          Le code est organisé,
                                                  documenté et versionné
                                                  sur GitHub.

  NF04                    Robustesse              Les erreurs réseau et
                                                  les indisponibilités
                                                  sont traitées.

  NF05                    Reproductibilité        Le lancement est
                                                  documenté et automatisé
                                                  autant que possible
                                                  avec Docker Compose.

  NF06                    Traçabilité             Les erreurs et
                                                  événements importants
                                                  sont journalisés.

  NF07                    Performance             Une mesure de temps de
                                                  réponse et un test de
                                                  charge sont réalisés.

  NF08                    Utilisabilité           Le tableau de bord
                                                  présente clairement les
                                                  mesures et alertes.

  NF09                    Qualité des données     Les données entrantes
                                                  sont validées avant
                                                  stockage.

  NF10                    Sécurité minimale       Les entrées sont
                                                  contrôlées et les
                                                  secrets ne sont pas
                                                  enregistrés dans le
                                                  dépôt Git.
  -----------------------------------------------------------------------

## 7. Indicateurs de réussite

Le projet sera considéré comme fonctionnel lorsque :

-   Plusieurs capteurs simulés peuvent envoyer des mesures.
-   Les mesures sont reçues, validées et stockées.
-   Les mesures peuvent être consultées par parcelle et par période.
-   Les indicateurs et graphiques sont visibles dans le tableau de bord.
-   Au moins un scénario de dépassement de seuil déclenche une alerte.
-   Au moins un scénario d'indisponibilité d'un service est testé et
    expliqué.
-   Les tests fonctionnels et d'intégration sont exécutables.
-   Une expérience de performance est documentée avec ses conditions et
    ses résultats.
-   Les services peuvent être démarrés à partir des instructions du
    dépôt.

Les objectifs chiffrés de performance seront définis après un premier
test sur l'environnement disponible. Il ne faut pas annoncer de
résultats avant de les avoir mesurés.

## 8. Contraintes et hypothèses

-   L'équipe est composée de 3 à 4 étudiants du même groupe de TD/TP.
-   Les données IoT sont simulées.
-   Le projet doit démontrer une architecture distribuée réelle, et non
    un monolithe simplement découpé en modules.
-   Au moins un mécanisme moderne de communication doit être implémenté
    et justifié.
-   Une interface web, une API documentée ou une interface adaptée doit
    permettre de tester le système.
-   Une gestion d'au moins un scénario de panne, des tests et une mesure
    de performance sont obligatoires.
-   GitHub est utilisé pour le versionnement et la collaboration.
-   Le choix définitif des technologies doit tenir compte des
    compétences et des ressources de l'équipe.

## 9. Livrables produit

-   Prototype fonctionnel.
-   Tableau de bord de supervision.
-   Services indépendants et leurs interfaces documentées.
-   Dépôt GitHub avec historique des contributions.
-   Rapport PDF de 20 pages maximum.
-   Présentation PDF.
-   README avec les prérequis et les instructions d'installation et
    d'exécution.
-   Fichiers Docker et Docker Compose, si utilisés.
-   Scripts de tests et résultats expérimentaux.
-   Données simulées ou instructions permettant de reproduire les
    expériences.

------------------------------------------------------------------------

# Partie II --- TRD (Technical Requirements Document)

## 10. Architecture technique proposée

### 10.1. Principes d'architecture

La solution adopte une architecture distribuée composée de services
indépendants. Chaque service possède une responsabilité précise et
expose une interface permettant aux autres composants de communiquer
avec lui.

Pour limiter la complexité du prototype, la communication principale
sera synchrone via HTTP/REST. L'utilisation de Kafka ou RabbitMQ n'est
pas nécessaire dans le MVP, sauf si l'équipe décide de l'ajouter et peut
en justifier l'intérêt.

### 10.2. Vue logique

``` text
+---------------------------+
| Simulateur de capteurs    |
| Python                    |
+-------------+-------------+
              |
              | HTTP / REST
              v
+---------------------------+
| Service de collecte       |
| FastAPI                   |
| Validation des mesures    |
+-------------+-------------+
              |
              | HTTP / REST
              v
+---------------------------+
| Service de traitement     |
| FastAPI                   |
| Seuils et alertes         |
+-------------+-------------+
              |
              | Accès aux données
              v
+---------------------------+
| Base de données           |
| PostgreSQL                |
+---------------------------+

              ^
              |
       HTTP / REST
              |
+-------------+-------------+
| Tableau de bord           |
| Streamlit                 |
| Graphiques et alertes     |
+---------------------------+
```

Cette architecture est une proposition de conception. L'équipe devra
produire un diagramme d'architecture et un diagramme de déploiement
correspondant à l'implémentation réelle.

### 10.3. Composants et responsabilités

  -----------------------------------------------------------------------
  Composant               Responsabilité          Technologie proposée
  ----------------------- ----------------------- -----------------------
  Simulateur IoT          Générer périodiquement  Python
                          des mesures fictives.   

  Service de collecte     Recevoir, valider et    Python, FastAPI
                          transmettre les         
                          mesures.                

  Service de traitement   Calculer les            Python, FastAPI
                          indicateurs et détecter 
                          les dépassements de     
                          seuils.                 

  Service de données      Persister les mesures,  PostgreSQL, accès via
                          parcelles, capteurs et  API
                          alertes.                

  Interface de            Consulter les données   Streamlit
  supervision             et les alertes.         

  Environnement de        Démarrer les composants Docker Compose
  déploiement             et leur réseau.         
  -----------------------------------------------------------------------

**Point d'architecture important :** pour conserver une séparation
réelle, le tableau de bord ne doit pas accéder directement aux tables
PostgreSQL. Il doit interroger les services via leurs API. L'équipe peut
choisir de faire du service de collecte le point d'accès aux données ou
de créer un service de données dédié. Ce choix devra être explicité dans
le diagramme final.

## 11. Stack technique recommandée

  -----------------------------------------------------------------------
  Besoin                  Technologie             Justification
  ----------------------- ----------------------- -----------------------
  Langage principal       Python                  Adapté à la simulation
                                                  et à l'analyse de
                                                  données.

  API                     FastAPI                 Permet de créer
                                                  rapidement des API REST
                                                  documentées.

  Base de données         PostgreSQL              Stockage relationnel
                                                  des mesures et des
                                                  entités.

  Interface               Streamlit               Création rapide d'un
                                                  tableau de bord Python.

  Analyse                 Pandas                  Calculs descriptifs et
                                                  manipulation des
                                                  mesures.

  Visualisation           Plotly                  Graphiques interactifs.

  Conteneurisation        Docker                  Isolation des
                                                  composants.

  Orchestration locale    Docker Compose          Démarrage reproductible
                                                  de plusieurs services.

  Tests                   Pytest                  Tests unitaires et
                                                  d'intégration.

  Versionnement           Git et GitHub           Collaboration et suivi
                                                  des modifications.
  -----------------------------------------------------------------------

L'équipe n'a pas besoin d'utiliser toutes les technologies citées dans
le document du module. Elle doit sélectionner les outils nécessaires et
justifier ses choix.

## 12. Modèle de données

### 12.1. Entités principales

**Table `parcelles`**

  Champ          Type indicatif           Description
  -------------- ------------------------ ----------------------------
  id             UUID ou BIGINT           Identifiant de la parcelle
  nom            VARCHAR(100)             Nom de la parcelle
  localisation   VARCHAR(255), nullable   Localisation descriptive
  created_at     TIMESTAMP                Date de création

**Table `capteurs`**

  Champ         Type indicatif   Description
  ------------- ---------------- ------------------------------
  id            UUID ou BIGINT   Identifiant du capteur
  parcelle_id   UUID ou BIGINT   Parcelle associée
  nom           VARCHAR(100)     Nom du capteur
  type          VARCHAR(50)      Type ou catégorie du capteur
  actif         BOOLEAN          État du capteur

**Table `mesures`**

  Champ          Type indicatif   Description
  -------------- ---------------- ----------------------------
  id             BIGINT           Identifiant de la mesure
  capteur_id     UUID ou BIGINT   Capteur émetteur
  temperature    NUMERIC(6,2)     Température en °C
  humidite_sol   NUMERIC(6,2)     Humidité du sol en %
  humidite_air   NUMERIC(6,2)     Humidité de l'air en %
  measured_at    TIMESTAMP        Date et heure de la mesure
  received_at    TIMESTAMP        Date et heure de réception

**Table `alertes`**

  Champ        Type indicatif   Description
  ------------ ---------------- --------------------------------
  id           BIGINT           Identifiant de l'alerte
  mesure_id    BIGINT           Mesure à l'origine de l'alerte
  indicateur   VARCHAR(50)      Indicateur concerné
  valeur       NUMERIC(8,2)     Valeur détectée
  seuil        NUMERIC(8,2)     Seuil appliqué
  message      TEXT             Description de l'alerte
  created_at   TIMESTAMP        Date de création
  statut       VARCHAR(30)      État de traitement de l'alerte

Les types UUID ou BIGINT doivent être harmonisés dans l'implémentation.
Les clés étrangères et les contraintes d'intégrité devront être
définies.

### 12.2. Relations

-   Une parcelle peut posséder plusieurs capteurs.
-   Un capteur appartient à une seule parcelle dans le modèle initial.
-   Un capteur peut produire plusieurs mesures.
-   Une mesure peut être associée à zéro, une ou plusieurs alertes selon
    la règle retenue.

## 13. Contrats d'API REST proposés

Les routes suivantes constituent une proposition initiale. Elles devront
être adaptées à la séparation définitive des services.

### 13.1. Service de collecte

  Méthode   Route                    Rôle
  --------- ------------------------ ------------------------------
  POST      `/api/v1/measurements`   Recevoir une nouvelle mesure
  GET       `/api/v1/health`         Vérifier l'état du service

**Exemple de requête `POST /api/v1/measurements`**

``` json
{
  "sensor_id": "sensor-001",
  "temperature": 32.5,
  "soil_humidity": 22.4,
  "air_humidity": 48.2,
  "measured_at": "2026-11-01T10:30:00Z"
}
```

**Exemple de réponse**

``` json
{
  "status": "accepted",
  "message": "Measurement received",
  "measurement_id": 125
}
```

### 13.2. Service de traitement et de consultation

  -------------------------------------------------------------------------------------
  Méthode                 Route                                 Rôle
  ----------------------- ------------------------------------- -----------------------
  GET                     `/api/v1/measurements`                Consulter les mesures

  GET                     `/api/v1/measurements/{id}`           Consulter une mesure

  GET                     `/api/v1/parcels/{id}/measurements`   Consulter les mesures
                                                                d'une parcelle

  GET                     `/api/v1/alerts`                      Consulter les alertes

  GET                     `/api/v1/statistics`                  Consulter les
                                                                indicateurs
                                                                statistiques

  GET                     `/api/v1/health`                      Vérifier l'état du
                                                                service
  -------------------------------------------------------------------------------------

**Exemple de réponse pour les statistiques**

``` json
{
  "parcel_id": "parcel-001",
  "period": "last_24_hours",
  "temperature": {
    "min": 18.2,
    "max": 36.1,
    "average": 27.4
  },
  "soil_humidity": {
    "min": 18.0,
    "max": 54.0,
    "average": 34.6
  }
}
```

Les exemples sont illustratifs. Les formats définitifs devront être
définis dans les schémas Pydantic et documentés avec OpenAPI.

## 14. Traitement des données

### 14.1. Cycle de vie d'une mesure

1.  Le simulateur construit une mesure.
2.  Il envoie la mesure au service de collecte par HTTP.
3.  Le service valide le format et les valeurs.
4.  La mesure valide est transmise au composant responsable du stockage.
5.  Le service de traitement évalue les règles de seuil.
6.  Une alerte est enregistrée si une condition est remplie.
7.  Le tableau de bord récupère les données via les API.

### 14.2. Validation

Le système doit notamment vérifier :

-   La présence de l'identifiant du capteur.
-   L'existence du capteur référencé.
-   Le format de la date.
-   Le type numérique des mesures.
-   Les plages de valeurs acceptées.
-   La cohérence des champs obligatoires.

Les valeurs hors plage doivent être rejetées ou signalées selon une
règle documentée. Il faut distinguer une valeur techniquement invalide
d'une valeur inhabituelle mais possible.

### 14.3. Analyse descriptive

Les indicateurs minimaux sont :

-   Minimum.
-   Maximum.
-   Moyenne.
-   Nombre de mesures reçues.
-   Nombre d'alertes sur une période.

Les calculs doivent pouvoir être filtrés par parcelle et par période.

### 14.4. Détection par seuils

Exemple de logique :

``` python
def detect_alerts(measurement, thresholds):
    alerts = []

    if measurement["temperature"] > thresholds["temperature_max"]:
        alerts.append("Température élevée")

    if measurement["soil_humidity"] < thresholds["soil_humidity_min"]:
        alerts.append("Humidité du sol faible")

    if measurement["air_humidity"] < thresholds["air_humidity_min"]:
        alerts.append("Humidité de l'air faible")

    return alerts
```

Les seuils doivent être centralisés dans une configuration plutôt que
dispersés dans le code.

## 15. Communication interservices et gestion des erreurs

### 15.1. Communication

-   Utiliser HTTP/REST avec des échanges JSON.
-   Définir des contrats d'API explicites.
-   Utiliser des codes HTTP adaptés.
-   Documenter les routes avec OpenAPI/Swagger.
-   Configurer des délais d'attente (timeouts) pour les appels entre
    services.

### 15.2. Scénarios d'erreur à traiter

  -----------------------------------------------------------------------
  Scénario                            Comportement attendu
  ----------------------------------- -----------------------------------
  Service de collecte indisponible    Le simulateur détecte l'échec et
                                      journalise l'erreur.

  Base de données inaccessible        Le service concerné renvoie une
                                      erreur contrôlée et journalise
                                      l'incident.

  Donnée mal formée                   La requête est rejetée avec une
                                      réponse de validation explicite.

  Capteur inconnu                     La mesure est rejetée avec une
                                      erreur appropriée.

  Délai d'attente dépassé             L'appel est interrompu et l'erreur
                                      est tracée.
  -----------------------------------------------------------------------

### 15.3. Reprise et résilience

Pour le prototype, mettre en place au minimum :

-   Des timeouts.
-   Une gestion explicite des exceptions.
-   Des logs compréhensibles.
-   Une stratégie limitée de nouvelle tentative pour les erreurs
    temporaires, si nécessaire.
-   Une réponse d'erreur cohérente pour l'interface.

Éviter les tentatives infinies. Si des nouvelles tentatives sont mises
en place pour l'envoi des mesures, prévoir un identifiant unique ou un
mécanisme d'idempotence afin de limiter les doublons.

## 16. Interface utilisateur

### 16.1. Pages proposées

**Page 1 --- Vue générale**

-   Nombre de parcelles.
-   Nombre de capteurs actifs.
-   Dernières mesures reçues.
-   Nombre d'alertes.
-   État des services.

**Page 2 --- Supervision des parcelles**

-   Liste des parcelles.
-   Dernières mesures par parcelle.
-   État des indicateurs.
-   Sélection d'une parcelle.

**Page 3 --- Analyse des mesures**

-   Courbes de température.
-   Courbes d'humidité du sol.
-   Courbes d'humidité de l'air.
-   Filtres par période et par capteur.

**Page 4 --- Alertes**

-   Liste des alertes.
-   Indicateur concerné.
-   Valeur observée et seuil.
-   Date et parcelle concernées.

### 16.2. Principes ergonomiques

-   Présenter clairement les unités.
-   Distinguer les données simulées des données réelles.
-   Afficher la date et l'heure des mesures.
-   Éviter de surcharger les graphiques.
-   Signaler les erreurs de récupération des données.

## 17. Déploiement avec Docker Compose

### 17.1. Services de conteneurs proposés

``` yaml
services:
  simulator:
    build: ./simulator
    depends_on:
      - collection-service

  collection-service:
    build: ./collection-service
    ports:
      - "8001:8000"
    depends_on:
      - postgres

  processing-service:
    build: ./processing-service
    ports:
      - "8002:8000"
    depends_on:
      - postgres

  dashboard:
    build: ./dashboard
    ports:
      - "8501:8501"
    depends_on:
      - collection-service
      - processing-service

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: agrisense
      POSTGRES_USER: agrisense_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Ce fichier est un squelette d'architecture et non une configuration
prête à exécuter. Les Dockerfiles, variables d'environnement, migrations
et dépendances réseau devront être ajoutés. Les dépendances `depends_on`
ne garantissent pas à elles seules que le service dépendant soit prêt à
accepter des connexions ; prévoir des healthchecks et une stratégie de
reconnexion.

### 17.2. Configuration

Les paramètres suivants doivent être externalisés :

-   URL de la base de données.
-   Adresse des services.
-   Intervalles de simulation.
-   Seuils d'alerte.
-   Niveau de journalisation.
-   Paramètres de test.

Ne pas versionner de mots de passe réels. Fournir un fichier
`.env.example` sans secret.

## 18. Tests et évaluation

### 18.1. Tests unitaires

-   Validation des mesures.
-   Calcul des statistiques.
-   Détection des seuils.
-   Gestion des valeurs manquantes ou invalides.

### 18.2. Tests d'intégration

-   Envoi d'une mesure du simulateur vers le service de collecte.
-   Enregistrement en base de données.
-   Récupération de la mesure par l'API.
-   Création et consultation d'une alerte.
-   Communication entre tableau de bord et services.

### 18.3. Tests de résilience

-   Arrêter temporairement un service.
-   Envoyer une requête pendant son indisponibilité.
-   Vérifier le comportement du service appelant.
-   Redémarrer le service.
-   Vérifier le retour à un fonctionnement normal.

### 18.4. Mesure de performance

Mesurer au minimum :

-   Le temps de réponse moyen d'une API.
-   Le nombre de requêtes traitées sur une durée donnée.
-   Le taux d'erreurs pendant un test de charge.
-   Le comportement lorsque le nombre de requêtes simultanées augmente.

Consigner les conditions du test : machine utilisée, configuration,
nombre de clients, durée et volume de données. Présenter les résultats
dans un tableau ou un graphique et les interpréter.

### 18.5. Outils possibles

-   Pytest pour les tests unitaires et d'intégration.
-   HTTPX pour tester les API.
-   Locust ou un outil équivalent pour la charge.
-   Logs applicatifs pour suivre les incidents.

## 19. Organisation du dépôt GitHub

Structure proposée :

``` text
agrisense/
│
├── simulator/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── collection-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── processing-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── dashboard/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── database/
│   ├── init.sql
│   └── migrations/
│
├── tests/
│   └── integration/
│
├── docs/
│   ├── architecture.md
│   └── diagrams/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

Cette structure est indicative. Elle peut évoluer en fonction de
l'organisation retenue par l'équipe.

## 20. Répartition technique du travail

Pour une équipe de quatre étudiants :

  -----------------------------------------------------------------------
  Membre                  Responsabilité          Livrables
                          principale              
  ----------------------- ----------------------- -----------------------
  Étudiant 1              Simulation IoT          Générateur de mesures,
                                                  format JSON, scénarios
                                                  de simulation

  Étudiant 2              API et collecte         Service de collecte,
                                                  validation,
                                                  documentation API

  Étudiant 3              Données et interface    Modèle PostgreSQL,
                                                  requêtes, tableau de
                                                  bord

  Étudiant 4              Traitement et qualité   Règles d'alerte, tests,
                                                  gestion des pannes,
                                                  mesures de performance
  -----------------------------------------------------------------------

Pour une équipe de trois, les responsabilités peuvent être regroupées.
Chaque membre doit toutefois avoir une contribution identifiable et
comprendre l'architecture complète.

## 21. Plan de réalisation indicatif

Le calendrier ci-dessous est une proposition de travail à adapter au
rythme de l'équipe. Les dates officielles du module restent
prioritaires.

  -----------------------------------------------------------------------
  Phase                   Travail                 Résultat attendu
  ----------------------- ----------------------- -----------------------
  1\. Cadrage             Valider le sujet, les   Périmètre du MVP validé
                          fonctionnalités et les  
                          rôles.                  

  2\. Conception          Définir l'architecture, Diagrammes et contrats
                          les données et les API. 

  3\. Développement       Réaliser le simulateur  Échanges interservices
  initial                 et les services.        fonctionnels

  4\. Persistance         Créer les tables et     Données consultables
                          enregistrer les         
                          mesures.                

  5\. Analyse et          Développer les          Tableau de bord
  interface               statistiques, alertes   fonctionnel
                          et graphiques.          

  6\. Intégration         Conteneuriser et        Déploiement
                          démarrer les composants reproductible
                          ensemble.               

  7\. Qualité             Réaliser les tests,     Résultats expérimentaux
                          simuler une panne et    
                          mesurer les             
                          performances.           

  8\. Finalisation        Rédiger le rapport, le  Livrables prêts pour la
                          README et les           soutenance
                          diapositives.           
  -----------------------------------------------------------------------

## 22. Risques techniques et mesures préventives

  -----------------------------------------------------------------------
  Risque                  Conséquence             Mesure préventive
  ----------------------- ----------------------- -----------------------
  Périmètre trop large    Retard et prototype     Prioriser le MVP
                          incomplet               

  Services trop couplés   Architecture distribuée Définir des
                          peu convaincante        responsabilités et
                                                  contrats clairs

  Erreurs de              Perte ou échec de       Timeouts, logs et
  communication           transmission            gestion des erreurs

  Données incohérentes    Statistiques            Validation et
                          incorrectes             contraintes de données

  Problèmes Docker        Difficulté de lancement Tester chaque conteneur
                                                  progressivement

  Développement tardif    Défauts découverts trop Écrire les tests au fur
  des tests               tard                    et à mesure

  Temps limité            Rapport ou              Réserver du temps à
                          démonstration           l'intégration et à la
                          incomplets              documentation
  -----------------------------------------------------------------------

## 23. Décisions techniques à faire valider

Avant le développement, l'équipe doit confirmer avec l'enseignant :

1.  Le nombre de services indépendants et leurs responsabilités.
2.  Le choix d'HTTP/REST comme mécanisme principal de communication.
3.  Le mode d'accès à PostgreSQL et la responsabilité de chaque service
    sur les données.
4.  Le choix de Streamlit pour l'interface.
5.  Les seuils utilisés pour la démonstration.
6.  Le scénario de panne qui sera présenté.
7.  L'outil et le protocole de mesure de performance.

------------------------------------------------------------------------

# Partie III --- Synthèse et critères de validation

## 24. Définition du MVP final

La première version livrable doit permettre de démontrer le scénario
complet suivant :

1.  Des capteurs fictifs génèrent des mesures pour plusieurs parcelles.
2.  Les mesures sont envoyées à un service indépendant via HTTP/REST.
3.  Les données sont validées puis stockées.
4.  Un service de traitement calcule des statistiques et vérifie les
    seuils.
5.  Les alertes sont enregistrées lorsqu'une condition est remplie.
6.  Le tableau de bord affiche les mesures, les graphiques et les
    alertes.
7.  L'équipe simule l'indisponibilité d'un service et explique le
    comportement obtenu.
8.  Les tests et les résultats de performance sont présentés.

## 25. Checklist de validation avant la soutenance

-   [ ] Le sujet et le périmètre ont été validés par l'enseignant.
-   [ ] Les services sont réellement indépendants.
-   [ ] Les échanges REST fonctionnent.
-   [ ] Les données simulées sont reçues et stockées.
-   [ ] Les mesures peuvent être consultées par parcelle et par période.
-   [ ] Les statistiques sont calculées.
-   [ ] Les alertes par seuil sont déclenchées.
-   [ ] Le tableau de bord fonctionne.
-   [ ] Un scénario de panne a été testé.
-   [ ] Les tests unitaires et d'intégration sont disponibles.
-   [ ] Une mesure de performance a été réalisée et interprétée.
-   [ ] Le déploiement est documenté et reproductible.
-   [ ] Le dépôt GitHub contient le code et les livrables.
-   [ ] Chaque membre sait expliquer sa contribution et l'architecture
    globale.

## 26. Références de cadrage

Ce document est construit à partir du sujet 3 --- « Plateforme de
supervision de données IoT » --- et des exigences générales du document
de projet du module *Systèmes répartis et distribués* (année 2026).

Les éléments suivants proviennent du cadrage du module : simulation de
capteurs, collecte et stockage de mesures, visualisation, alertes sur
seuils, architecture distribuée, communication interservices, gestion
des pannes, tests, mesure de performance, déploiement reproductible et
dépôt GitHub.

Les noms de produit, le découpage précis des services, le modèle de
données, les routes API, les seuils de démonstration et la stack
proposée sont des choix de conception suggérés dans ce document. Ils
doivent être discutés et validés par l'équipe et l'enseignant avant leur
implémentation.
