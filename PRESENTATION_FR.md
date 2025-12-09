# Présentation : Endpoint Sentinel AI

## Slide 1 : Titre
**Sujet** : Predictive Endpoint Health & Security Forecast
**Sous-titre** : Une approche proactive par Machine Learning
**Étudiants** : [Noms des étudiants]
**Année** : 2025-2026

---

## Slide 2 : La Problématique
*   **Constat** : Les antivirus traditionnels sont réactifs (attendent une signature).
*   **Le Déficit** : Les attaques modernes (Zero-day, Ransomware) agissent vite.
*   **Notre Solution** : Analyser le *comportement* du PC (CPU, RAM, Disque) pour prédire une anomalie avant le crash complet.

---

## Slide 3 : Architecture Technique
*   **Dockerisé** : 100% conteneurisé pour la portabilité.
*   **Backend** : FastAPI (Python) pour la rapidité et l'inférence ML.
*   **Frontend** : Streamlit pour un Dashboard interactif et moderne.
*   **Monitoring** : Prometheus pour la collecte industrielle de métriques.

---

## Slide 4 : Le Cœur "Intelligence Artificielle"
*   **Algorithme** : Random Forest (Forêt Aléatoire).
*   **Données** :
    *   Entraînement sur des données synthétiques (Simulation d'attaques).
    *   Features : Utilisation CPU, I/O Disque, Trafic Réseau.
*   **Résultat** : Un "Score de Santé" (0-100%) en temps réel.

---

## Slide 5 : Démonstration (Live)
*   **Scénario** :
    1.  Lancement de la stack `docker-compose`.
    2.  Visualisation de la flotte saine (~90-100% santé).
    3.  Injection automatique d'une attaque (Simulateur).
    4.  **Détection** : Alerte Rouge immédiate et chute du score de santé.

---

## Slide 6 : Conclusion & Avenir
*   **Ce que nous avons réalisé** : Un prototype fonctionnel de bout en bout.
*   **Améliorations futures** :
    *   Intégration d'un agent réel (ex: OSQuery) sur tous les postes.
    *   Réponse automatique (tuer le processus malveillant).
