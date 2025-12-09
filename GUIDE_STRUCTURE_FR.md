# Structure du Projet : Explication des Fichiers

Ce document détaille le rôle de chaque dossier et fichier clé du projet pour vous aider à comprendre l'architecture globale.

## 📂 /backend
Le "cerveau" du système. C'est une API FastAPI.
*   **`main.py`** : Le point d'entrée. Il reçoit les données (`POST /api/metrics`), appelle le modèle ML pour une prédiction, et stocke l'état. Il expose aussi les métriques pour Prometheus.
*   **`Dockerfile`** : Instructions pour construire l'image Docker du backend.

## 📂 /ml
Le moteur d'intelligence artificielle.
*   **`engine.py`** : 
    1.  Génère des données synthétiques (CPU/RAM normaux vs attaque).
    2.  Entraîne le modèle Random Forest (`train_model`).
    3.  Fait les prédictions en temps réel (`predict`).
*   **`security_model.joblib`** : Le fichier du modèle entraîné (généré automatiquement).

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
