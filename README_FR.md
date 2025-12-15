# Endpoint Sentinel AI (v2.0)

## Vue d'ensemble
Un système complet de **Détection et Réponse Prédictive sur les Endpoints (PEDR)**. Il surveille la santé du système (CPU, RAM, Réseau, GPU) et les événements de sécurité (Intégrité des fichiers, Processus) pour prévoir les anomalies et les compromissions potentielles avant qu'elles ne provoquent une panne du système.

## 🏗️ Architecture (v2.0)
- **Agent de Monitoring** : Script Python (`backend/collector.py`) collectant la télémétrie complète.
- **Agent de Sécurité** : Daemon basé sur **Osquery** pour une introspection profonde du système.
- **Backend** : FastAPI (`backend/main.py`) avec persistance SQLite et plannificateur de tâches.
- **Moteur ML** : XGBoost (Risque), Isolation Forest (Anomalie), et PyTorch LSTM (Prévision).
- **Tableau de Bord** : Interface **Streamlit** premium avec graphiques en temps réel, alertes et rapports.

## 🚀 Installation et Utilisation

### 1. Prérequis
*   Docker Desktop installé.
*   (Optionnel) NVIDIA GPU pour la surveillance GPU.

### 2. Démarrer le Système
Tout est conteneurisé. Lancez simplement :
```powershell
docker-compose up --build -d
```
*Note : Le premier lancement peut prendre quelques minutes pour construire les images ML et entraîner les modèles initiaux.*

### 3. Accéder au Tableau de Bord
Allez sur **[http://localhost:8501](http://localhost:8501)** dans votre navigateur.

- **Onglet Vue d'ensemble** : État de la flotte en direct, Matrice de Risque, et Scores de Santé.
- **Onglet Alertes** : Historique de tous les incidents de sécurité.
- **Onglet Rapports** : Téléchargement de rapports d'incidents spécifiques en format CSV.

### 4. Monitoring & Métriques
*   **Prometheus** : [http://localhost:9090](http://localhost:9090) (Métriques Système)
*   **API Docs** : [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

## 🧪 Simulation et Tests
Le système inclut un conteneur **Traffic Simulator** (`traffic-simulator`) qui génère des données fictives pour 5 bureaux virtuels.
Pour tester des scénarios spécifiques (ex: Crypto Mining), le système détecte des modèles comme :
- **CPU Élevé + Réseau Élevé** -> Accès Initial Potentiel / Minage
- **Changements de Fichiers Massifs** -> Ransomware Potentiel

## 🧠 Modèles de Machine Learning
- **Classificateur de Risque** : `XGBoost` entraîné sur des modèles d'attaque synthétiques.
- **Détection d'Anomalie** : `Isolation Forest` pour détecter les menaces inconnues.
- **Tendance de Santé** : `LSTM` (PyTorch) pour la prévision de séries chronologiques.
