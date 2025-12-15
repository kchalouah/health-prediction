# Présentation : Endpoint Sentinel AI

## Slide 1 : Introduction
**Sujet** : Système Prédictif de Santé et Sécurité des Endpoints (PEDR).
**Contexte** : Dans un monde où les cyberattaques sont automatisées, la simple réaction ne suffit plus.
**Objectif** : Développer une solution capable d'anticiper les pannes et les attaques avant qu'elles ne paralysent le système.
**Étudiants** : [Noms] | **Année** : 2025-2026

---

## Slide 2 : La Problématique
*   **Le Constat** : Les antivirus traditionnels fonctionnent par "signature". Ils doivent connaître le virus pour l'arrêter.
*   **La Faille** :
    *   Les attaques **Zero-day** (inconnues) passent au travers.
    *   Les **Ransomwares** agissent en quelques secondes, trop vite pour une intervention humaine.
    *   **Problème Ops** : Un PC peut crasher pour des raisons non-malveillantes (fuite mémoire), causant les mêmes arrêts de production.

---

## Slide 3 : État de l'Art & Recherche
Ce projet s'inscrit dans les tendances Cybersecurity 2024-2025 :

*   **De l'EDR au XDR (Extended Detection Response)** :
    *   *Concept* : Ne plus regarder juste le fichier, mais le contexte global (Réseau + Processus + Disque).
    *   *Notre Approche* : Nous corrélons les métriques *Hardware* avec les logs *Système*.
*   **UEBA (User & Entity Behavior Analytics)** :
    *   *Principe* : Utiliser le ML pour définir une "baseline" de comportement normal et alerter sur la déviation.
    *   *Techno* : C'est ce que fait notre **Isolation Forest** (Détection d'anomalie non-supervisée).
*   **Choix Technologiques (Benchmark)** :
    *   *Collecte* : eBPF (Complexe) vs **Osquery** (Standard Meta/Facebook). -> **Nous avons choisi Osquery** pour sa portabilité SQL.
    *   *Prédiction* : Séries Temporelles Classiques (ARIMA) vs **Deep Learning (LSTM)**. -> **Nous utilisons LSTM** pour capturer les dépendances longues (ex: fuite mémoire lente).

---

## Slide 4 : Comparaison des Solutions
Comment protéger un parc informatique ?

| Solution | Méthode | Avantage | Inconvénient |
| :--- | :--- | :--- | :--- |
| **Antivirus Classique** | Signatures (Base de données) | Très fiable sur le connu | Aveugle sur l'inconnu |
| **EDR Classique** | Analyse comportementale simple | Détecte les mouvements suspects | Souvent réactif (après l'alerte) |
| **Notre Solution (PEDR)** | **Machine Learning Prédictif** | **Anticipe** l'incident (Proactif) | Nécessite un entraînement continu |

**Notre Choix** : Une approche Hybride (Règles + IA) pour combiner la fiabilité des règles et la puissance de prédiction de l'IA.

---

## Slide 4 : Données et Simulation
*   **Le Défi de la Data** : Il est impossible d'avoir des "vraies" attaques sur un réseau de production pour l'entraînement (trop dangereux).
*   **Notre Approche : La Simulation**
    *   Nous avons développé un **Traffic Simulator** (`traffic_gen.py`).
    *   Il génère des métriques réalistes :
        *   *Normal* : Navigation web, bureautique.
        *   *Attaque* : Cryptomining (CPU > 90%), Ransomware (I/O Disque intense, modif de fichiers), Exfiltration (Traffic Réseau sortant).
    *   L'IA apprend donc sur des données "similaires au réel".

---

## Slide 5 : Solution Proposée (Architecture)
Une architecture micro-services moderne **100% Dockerisée** :
1.  **Orchestration** : **Docker Compose** pilote l'ensemble des conteneurs (Backend, ML, UI, DB).
2.  **Backend (Le Cerveau)** : FastAPI (Python) + APScheduler. Analyse les données toutes les 5 secondes.
3.  **Monitoring (Les Yeux)** :
    *   **Prometheus** : Base de données temporelle pour la collecte industrielle de métriques (`/metrics`).
    *   `psutil` / `GPUtil` : Sondes hardware.
    *   **Osquery** : Inspection sécurité.
4.  **Persistance** : SQLite.
5.  **Frontend** : Streamlit.

---

## Slide 6 : Machine Learning & Ingénierie des Données
L'IA ne "comprend" pas les chiffres bruts. Nous devons les transformer.

### 1. Feature Engineering (Préparation)
*   **Fenêtres Glissantes** : On ne regarde pas juste l'instant T, mais la moyenne sur 1h (`cpu_mean_1h`) et la volatilité (`cpu_std`).
*   **Tendances** : Est-ce que la RAM monte doucement ? (Fuite mémoire).

### 2. Stratégie Multi-Modèles
*   **XGBoost** (Le Gardien) : Classifie "Sain" vs "Compromis" basé sur les attaques apprises.
*   **Isolation Forest** (L'Expert) : Détecte les anomalies pures (jamais vues auparavant).
*   **LSTM** (Le Devin) : Analyse la séquence temporelle pour prédire la santé future.

---

## Slide 7 : Défis Techniques & Solutions
*   **Défi 1 : La Latence**
    *   *Problème* : L'IA peut être lente.
    *   *Solution* : Utilisation de modèles optimisés (`joblib`) et traitement asynchrone. Inférence < 50ms.
*   **Défi 2 : Faux Positifs**
    *   *Problème* : Une mise à jour Windows ressemble à une attaque (CPU + Disque).
    *   *Solution* : Cross-validation avec les logs Osquery (Processus signé vs Processus inconnu).
*   **Défi 3 : Intégration Docker**
    *   *Problème* : Accéder aux infos bas niveau de l'hôte depuis un conteneur.
    *   *Solution* : Montage de volumes partagés (`/proc`, `/var/run`) en lecture seule.

---

## Slide 8 : Démonstration (Scénario)
Nous allons vous montrer le système en action :
1.  **Vue d'ensemble** : Le Dashboard montre une flotte saine (Vert).
2.  **L'Attaque** : Lancement du script de simulation "Ransomware".
3.  **La Réaction** :
    *   Les jauges CPU et Disque s'affolent.
    *   L'IA détecte l'anomalie en **< 2 secondes**.
    *   Le statut passe à "COMPROMIS" (Rouge).
    *   Une notification apparaît avec l'action recommandée : **"Isoler le poste"**.

---

## Slide 9 : Conclusion
*   **Bilan** : Nous avons créé un prototype fonctionnel d'EDR Prédictif qui prouve que l'IA peut sécuriser les endpoints pro-activement.
*   **Points Forts** : Architecture modulaire, Dashboard clair, IA explicable (on sait pourquoi ça alerte).
*   **Ouverture** : Vers une réponse autonome (le système tue le processus lui-même) et un apprentissage fédéré.

---

## Slide 10 : Références Bibliographiques & Outils
Pour construire ce projet, nous nous sommes basés sur les standards de l'industrie :

### 📚 Académique & Algorithmes
*   **XGBoost** : Chen, T., & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. KDD '16.
*   **Isolation Forest** : Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). *Isolation Forest*. ICDM '08.
*   **LSTM for Anomaly Detection** : Malhotra, P., et al. (2015). *Long Short Term Memory Networks for Anomaly Detection in Time Series*.

### 🛠️ Outils & Standards Industriels
*   **MITRE ATT&CK Framework** : Référentiel mondial des comportement d'attaques (TTPs) sur lequel nous basons nos scénarios.
*   **Osquery** : Outil d'instrumentation créé par Facebook, standard de facto pour la télémétrie endpoint.
*   **FastAPI / Docker** : Architectures micro-services modernes pour le déploiement cloud-native.
