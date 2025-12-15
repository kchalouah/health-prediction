# Structure du Projet : Explication des Fichiers

Ce document détaille le rôle de chaque dossier et fichier clé du projet pour vous aider à comprendre l'architecture globale.

## 📂 /backend
Le cœur fonctionnel de l'application (API + Logique).
*   **`main.py`** : Point d'entrée FastAPI. Gère les routes API, le scheduler (APScheduler), et expose les métriques Prometheus.
*   **`collector.py`** : Collecte les métriques système (CPU, RAM, GPU, Réseau) via `psutil`.
*   **`security_mon.py`** : Surveille les logs d'Osquery (`/var/log/osquery`) pour détecter les processus suspects.
*   **`database.py`** : Modèles SQLAlchemy pour la persistance des alertes et métriques dans `endpoint.db` (SQLite).

## 📂 /ml
Le moteur d'intelligence artificielle avancé.
*   **`models.py`** : Contient les 3 modèles :
    1.  **RiskClassifier** (XGBoost) : Pour le score de compromission.
    2.  **AnomalyDetector** (Isolation Forest) : Pour les menaces inconnues.
    3.  **HealthForecaster** (LSTM) : Pour la prédiction de tendance.
*   **`feature_engine.py`** : Transforme les données brutes en indicateurs temporels (moyennes glissantes, tendances).
*   **`health_scorer.py`** : Logique métier pour calculer le Score de Santé (0-100) et générer des recommandations.
*   **`train.py`** : Script d'entraînement automatisé (génération de données synthétiques + fit des modèles).

## 📂 /dashboard
L'interface utilisateur visuelle.
*   **`app.py`** : Une application Streamlit. Elle interroge le backend (`GET /api/dashboard`) toutes les 2 secondes et affiche les jauges, graphiques et alertes.

## 📂 /configs
Fichiers de configuration pour les outils externes.
*   **`prometheus.yml`** : Dit à Prometheus *où* aller chercher les données (il doit "scraper" le backend sur le port 8000).
*   **`osquery.conf`** : Configure l'agent de sécurité OSQuery pour surveiller les fichiers et processus.

## 📂 /notebooks
Scripts utilitaires pour la démonstration.
*   **`traffic_gen.py`** : Le simulateur. Il envoie en boucle des fausses données au backend pour que le tableau de bord soit vivant sans avoir besoin d'attendre une vraie attaque.

## 📂 /docker
Contient les Dockerfiles spécifiques si nous avons besoin de séparer les dépendances (utilisé par `docker-compose`).

## 📄 Fichiers à la racine
*   **`docker-compose.yml`** : Le chef d'orchestre. Il lance tous les services (backend, dashboard, prometheus, simulateur) en même temps et les connecte ensemble dans un réseau virtuel.
*   **`requirements.txt`** : Liste des librairies Python nécessaires (fastapi, pandas, scikit-learn, etc.).
