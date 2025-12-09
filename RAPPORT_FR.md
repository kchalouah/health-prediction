# Rapport de Projet : Système Prédictif de Santé et Sécurité des Endpoints

**Projet** : Endpoint Health & Security Prediction  
**Date** : Décembre 2025  
**État** : Prototype Fonctionnel (v2)

---

## 1. Introduction
Ce projet vise à développer une solution proactive de cybersécurité capable de prédire l'état de santé et les risques de sécurité des terminaux (endpoints). Contrairement aux antivirus traditionnels réactifs, notre système utilise l'apprentissage automatique (Machine Learning) pour analyser les comportements anormaux (CPU, Disque, Réseau) et anticiper les compromissions avant qu'elles ne deviennent critiques.

## 2. Architecture du Système
Le système repose sur une architecture moderne de micro-services conteneurisés via Docker.

### Composants Principaux :
1.  **Backend (FastAPI)** :
    *   Sert d'API centrale pour l'ingestion des métriques.
    *   Héberge le moteur ML pour l'inférence en temps réel.
    *   Expose les métriques au format Prometheus (`/metrics`).
2.  **Dashboard (Streamlit)** :
    *   Interface utilisateur interactive.
    *   Visualise les scores de santé, les graphiques de tendance et les alertes de sécurité.
3.  **Machine Learning Engine** :
    *   Utilise un modèle **Random Forest** (Forêt Aléatoire).
    *   Entraîné sur des données synthétiques simulant des comportements sains vs attaques (Ransomware, Cryptomining).
4.  **Monitoring & Simulation** :
    *   **Prometheus** : Base de données temporelle pour stocker les métriques.
    *   **Node Exporter** : Collecte les métriques réelles de l'hôte Docker.
    *   **Traffic Simulator** : Script Python générant automatiquement du trafic normal et malveillant pour la démonstration.

## 3. Méthodologie Technique

### 3.1 Génération de Données (Synthetic Data)
Faute de dataset public contenant des métriques "live" exploitables pour une démo temps réel, nous avons créé un générateur de données (`ml/engine.py`) :
*   **Normal** : CPU ~25%, RAM ~40%, Processus ~100.
*   **Attaque** : CPU >85%, Disque >80% (simulant un chiffrement ou minage).

### 3.2 Modèle Prédictif
Nous avons choisi un classifieur **Random Forest** pour sa robustesse et sa capacité à gérer des relations non linéaires entre les métriques système.
*   **Features** : `cpu_usage`, `memory_usage`, `disk_io`, `network_traffic`, `file_changes`.
*   **Target** : `0` (Sain) ou `1` (Compromis).
*   **Score de Risque** : Probabilité prédite par le modèle (0.0 à 1.0).

## 4. Guide de Démarrage
Le projet a été conçu pour être déployé en une seule commande grâce à Docker Compose.

**Prérequis** : Docker & Docker Compose.

**Commande** :
```bash
docker-compose up --build -d
```

**Accès** :
*   Tableau de bord : `http://localhost:8501`
*   Métriques Brutes : `http://localhost:9090` (Prometheus)

## 5. Scénario de Démonstration
1.  Le système démarre et entraîne automatiquement le modèle ML.
2.  Le `traffic-simulator` commence à envoyer des données.
3.  Sur le Dashboard, on observe des endpoints "Sains" (Vert).
4.  Aléatoirement, le simulateur envoie une rafale de données d'attaque.
5.  Le Dashboard passe instantanément l'endpoint en "Compromis" (Rouge) et recommande une action (ex: "Isoler l'endpoint").

## 6. Conclusion
Ce prototype démontre la faisabilité d'une sécurité proactive. En combinant la surveillance système temps réel (Prometheus) et l'IA (Scikit-Learn), nous pouvons détecter des menaces complexes que les signatures statiques pourraient manquer.
