# Rapport de Projet : Système Prédictif de Santé et Sécurité des Endpoints

**Projet** : Endpoint Health & Security Prediction  
**Date** : Décembre 2025  
**État** : Prototype Fonctionnel (v2)

---

## 1. Introduction
Ce projet vise à développer une solution proactive de cybersécurité capable de prédire l'état de santé et les risques de sécurité des terminaux (endpoints). Contrairement aux antivirus traditionnels réactifs, notre système utilise l'apprentissage automatique (Machine Learning) pour analyser les comportements anormaux (CPU, Disque, Réseau) et anticiper les compromissions avant qu'elles ne deviennent critiques.

## 2. Architecture du Système (v2.0)
Le système repose sur une architecture de micro-services évoluée.

### Composants Principaux :
1.  **Backend Intelligent** :
    *   **FastAPI** + **APScheduler** pour la collecte et l'analyse temps-réel (5s).
    *   **SQLite** pour la persistance des incidents et l'historique.
    *   **Osquery Integration** pour l'analyse forensique des logs système.
2.  **Dashboard Premium (Streamlit)** :
    *   Interface à onglets : Vue d'ensemble, Alertes, Rapports.
    *   Export CSV des incidents pour la conformité.
    *   Visualisations avancées : Heatmaps CPU/RAM, Matrice de Risque.
3.  **Moteur ML Tri-Modèle** :
    *   **XGBoost** : Classification supervisée des risques connus.
    *   **Isolation Forest** : Détection non-supervisée des zéros-days (Anomalies).
    *   **LSTM (PyTorch)** : Réseau de neurones récurrent pour la prédiction de tendances futures.

## 3. Méthodologie Technique

### 3.1 Ingénierie des Fonctionnalités (Feature Engineering)
Les données brutes ne suffisent pas. Nous calculons des "fenêtres glissantes" sur 1 heure :
*   `cpu_mean_1h`, `cpu_std_1h` : Pour détecter la volatilité.
*   `usage_trend` : La pente de la courbe d'utilisation (détection de fuite mémoire).

### 3.2 Stratégie Multi-Modèles
Contrairement aux approches classiques (un seul modèle), nous combinons trois signaux :
*   **Le Risque (Probabilité)** : Calculé par XGBoost sur des patterns d'attaque connus (Ransomware, Mining).
*   **L'Anomalie (Booléen)** : Si Isolation Forest détecte un point "bizarre" (outlier), on lève une alerte "Warning" même si le risque est bas.
*   **La Prévision** : LSTM anticipe si le score de santé va chuter, permettant une intervention *avant* l'incident.

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
