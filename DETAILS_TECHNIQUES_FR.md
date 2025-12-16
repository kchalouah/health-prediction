# Détails Techniques & Explication du Projet

Ce document fournit une explication détaillée de chaque composant, dépendance et fichier du projet **Endpoint Sentinel AI**.

---

## 📦 1. Les Dépendances (`requirements.txt`)

Ce fichier liste toutes les bibliothèques Python tiers nécessaires au fonctionnement du projet. Voici pourquoi nous utilisons chacune d'elles :

### Serveur & API
*   **`fastapi`** : Un framework web moderne et très rapide.
    *   *Pourquoi ?* : Pour construire l'API Backend qui reçoit les métriques des agents et sert les données au tableau de bord. Il gère la validation des données automatiquement (via Pydantic).
*   **`uvicorn`** : Un serveur web ASGI.
    *   *Pourquoi ?* : FastAPI est l'application, mais Uvicorn est le "moteur" qui la fait tourner en production. Il est optimisé pour les applications asynchrones (`async/await`).
*   **`requests`** : Une bibliothèque pour envoyer des requêtes HTTP.
    *   *Pourquoi ?* : Utilisée par le **simulateur** de trafic (`traffic_gen.py`) pour envoyer des fausses données (`POST`) à l'API backend comme si c'était un vrai agent.

### Traitement de Données
*   **`pandas`** : La référence pour la manipulation de données tabulaires.
    *   *Pourquoi ?* : Indispensable pour l'IA. Nous recevons des métriques brutes, nous les mettons dans un "DataFrame" Pandas pour calculer des moyennes glissantes, des écarts-types, et préparer les données pour le modèle.
*   **`numpy`** : Calcul numérique haute performance.
    *   *Pourquoi ?* : Utilisé en interne par Pandas et Scikit-Learn pour les opérations matricielles rapides.

### Intelligence Artificielle (ML/DL)
*   **`scikit-learn`** : Bibliothèque classique de Machine Learning.
    *   *Pourquoi ?* : Fournit l'algorithme **Isolation Forest** utilisé pour la détection d'anomalies (détecter ce qui est "bizarre" sans l'avoir jamais vu).
*   **`xgboost`** : Bibliothèque de "Gradient Boosting".
    *   *Pourquoi ?* : Fournit le modèle **RiskClassifier**. C'est souvent plus performant et rapide que les Random Forests classiques pour les données structurées (tableaux).
*   **`torch` (PyTorch)** : Framework de Deep Learning.
    *   *Pourquoi ?* : Utilisé pour le modèle **LSTM** (Long Short-Term Memory). C'est un réseau de neurones capable de comprendre les séquences temporelles (le passé influence le futur), idéal pour la prédiction de tendance.
*   **`joblib`** : Outil de sérialisation.
    *   *Pourquoi ?* : Permet de "sauvegarder" un modèle entraîné dans un fichier (`.joblib` ou `.json`) et de le "charger" instantanément au démarrage, évitant de devoir ré-entraîner l'IA à chaque lancement.

### Interface & Visualisation
*   **`streamlit`** : Framework pour créer des applications de données en pur Python.
    *   *Pourquoi ?* : Permet de créer le **Dashboard** interactif (`dashboard/app.py`) sans écrire une seule ligne de HTML, CSS ou JavaScript.
*   **`plotly`** : Bibliothèque de graphiques interactifs.
    *   *Pourquoi ?* : Utilisé dans Streamlit pour afficher la "Matrice de Risque" dynamique et les Heatmaps, permettant de zoomer et survoler les points.

### Monitoring & Système
*   **`prometheus_client`** : Client pour Prometheus.
    *   *Pourquoi ?* : Permet à notre code Python d'exposer ses propres métriques (ex: `endpoint_risk_prob`) sur une page `/metrics` pour qu'une base de données Prometheus puisse les aspirer.
*   **`psutil`** : Process & System Utilities.
    *   *Pourquoi ?* : C'est les "yeux" de l'agent. Il permet au code Python de lire l'utilisation réelle du CPU, de la RAM, et du Disque du système hôte.
*   **`gputil`** : Utilitaire GPU.
    *   *Pourquoi ?* : Permet de détecter la présence d'une carte graphique NVIDIA et de lire son taux d'utilisation.

### Infrastructure & Utilitaires
*   **`sqlalchemy`** : ORM (Object Relational Mapper) pour bases de données.
    *   *Pourquoi ?* : Permet d'interagir avec la base de données SQL (`endpoint.db`) en utilisant des classes Python (`Model`) au lieu d'écrire du SQL brut. C'est plus propre et sécurisé.
*   **`apscheduler`** : Planificateur de tâches avancé.
    *   *Pourquoi ?* : Permet de lancer la boucle de surveillance (`monitor_loop`) en arrière-plan toutes les 5 secondes sans bloquer l'API principale qui doit rester disponible pour répondre aux requêtes.

---

## 📂 2. Structure des Fichiers et Rôles

Ce projet est découpé en modules logiques (Architecture Micro-services).

### 🧠 Backend (`/backend`)
C'est le cerveau du système.
*   **`main.py`** : Le chef d'orchestre.
    *   Démarre le serveur API.
    *   Charge les modèles ML au démarrage.
    *   Lance le planificateur (Scheduler) pour analyser les données périodiquement.
    *   Définit les "Routes" (URL) comme `/api/metrics` (recevoir les données) ou `/api/dashboard` (envoyer l'état au frontend).
*   **`collector.py`** : Les sens.
    *   Contient la classe `SystemMonitor`. Son seul but est d'utiliser `psutil` pour interroger le système d'exploitation et retourner un dictionnaire propre (CPU, RAM, etc.).
*   **`security_mon.py`** : Le chien de garde.
    *   Surveille le fichier de logs généré par l'agent **Osquery** (qui tourne séparément). Il cherche des mots-clés spécifiques dans les logs JSON pour détecter des événements de sécurité.
*   **`database.py`** : La mémoire.
    *   Configure la connexion à la base de données SQLite.
    *   Définit la structure des tables (`EndpointMetric`, `SecurityEvent`) pour que SQLAlchemy sache comment stocker les données.

### 🤖 Intelligence Artificielle (`/ml`)
*   **`models.py`** : Les compétences.
    *   Contient les classes Python qui enveloppent les algorithmes complexes (`RiskClassifier`, `AnomalyDetector`, `HealthForecaster`). Cela permet d'utiliser `model.predict()` simplement dans le backend sans se soucier des maths complexes derrière.
*   **`feature_engine.py`** : Le traducteur.
    *   Les modèles ML ne comprennent pas bien les chiffres bruts isolés. Ce fichier transforme "CPU: 80%" en "Moyenne CPU 1h: 40%, Tendance: +10%". C'est ce qu'on appelle l'ingénierie des fonctionnalités (Feature Engineering).
*   **`health_scorer.py`** : Le juge.
    *   Prend les résultats de tous les modèles (Probabilité de risque, Booléen d'anomalie) et applique une logique métier pour donner une note finale sur 100 et générer une phrase de recommandation humaine (ex: "Tuer le processus").
*   **`train.py`** : Le professeur.
    *   Script exécuté au démarrage pour générer des données synthétiques (fausses mais réalistes) et entraîner les modèles. Cela assure que le système fonctionne "out-of-the-box" sans attendre des semaines de collecte de données.

### 📊 Dashboard (`/dashboard`)
*   **`app.py`** : Le visage.
    *   Un script Streamlit autonome. Il boucle infiniment : il demande l'état actuel au Backend via API, puis redessine toute la page avec les graphiques à jour.

### ⚙️ Configuration & Infrastructure
*   **`docker-compose.yml`** : Le plan de construction.
    *   Définit comment lancer tous ces scripts (Backend, Dashboard, Base de données Prometheus) dans des conteneurs isolés mais connectés entre eux.
*   **`osquery.conf`** : Le règlement.
    *   Fichier de configuration pour l'agent Osquery. Il contient les requêtes SQL qui définissent ce qu'il faut surveiller (ex: "Surveille les processus qui écoutent sur le réseau").
*   **`prometheus.yml`** : La configuration d'archivage.
    *   Dit à la base de données Prometheus : "Va chercher les métriques sur `backend:8000/metrics` toutes les 5 secondes".
