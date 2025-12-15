# 🛠️ Code Reference & Function Documentation

This document explains the core functions found in the key files of the project.

## 1. Backend (`backend/main.py`)
This file is the specific point of the system.

*   **`startup_event()`**:
    *   *Purpose*: Runs when the server starts. It triggers the `monitor_loop` (scheduler) and ensures ML models are trained (or loaded) before accepting traffic.
*   **`receive_metrics(payload)`**:
    *   *Purpose*: The main entry point for data. It accepts JSON metrics from agents, converts them to a DataFrame, runs ML inference, and updates the global state.
    *   *Crucial Step*: It exports metrics to Prometheus Gauges (`HEALTH_GAUGE`, `RISK_GAUGE`) for external monitoring.

## 2. ML Engine & Training (Model Layer)

### A. Training Loop (`ml/train.py`)
This script is responsible for building the brains of the system.
*   **`generate_synthetic_data(n_samples)`**:
    *   *Purpose*: Simulates hours of telemetry data. It creates "Normal" behavior patterns (low variability) and "Attack" patterns (spikes in CPU/Network or massive File Changes).
*   **`train_models()`**:
    *   *Purpose*: Orchestrates the full training pipeline.
    *   1. Generates data.
    *   2. Splits into Train/Test sets.
    *   3. Trains `XGBClassifier` (Risk) and `IsolationForest` (Anomaly).
    *   4. Saves models to disk (`.json`, `.joblib`).

### B. Feature Engineering (`ml/feature_engine.py`)
Raw data isn't enough; we need context (trends).
*   **`FeatureEngineer.transform(raw_metrics)`**:
    *   *Logic*:
        *   Calculates **Rolling Averages** (e.g., `cpu_mean_1h`) to detect shifts.
        *   Calculates **Trends** (Slope) to see if usage is accelerating.
        *   Computes **Stress Ratios** (e.g., IO per CPU cycle) to identify inefficiencies.

### C. Models (`ml/models.py`)
*   **`RiskClassifier.predict_risk(features)`**:
    *   *Purpose*: Returns a probability (0.0 to 1.0) that an endpoint is compromised.
    *   *Logic*: Uses a pre-trained **XGBoost** model. It includes a small "organic jitter" to simulate real-world variance in confidence scores.
*   **`AnomalyDetector.is_anomaly(features)`**:
    *   *Purpose*: Identifies "Unknown Unknowns" (Zero-days).
    *   *Model*: **Isolation Forest**. If a data point is too different from the training distribution (e.g., weird CPU usage pattern), it flags it as an anomaly even if the Risk score is low.
*   **`HealthForecaster.forecast_trend()`**:
    *   *Purpose*: Uses **LSTM (PyTorch)** to predict if system health will degrade in the next hour based on the last sequence of events.

## 3. Data Collection & Persistence (Backend Layer)

### A. Metrics Collection (`backend/collector.py`)
The eyes and ears of the agent.
*   **`collect_system_metrics()`**:
    *   *Library*: Uses `psutil` for CPU/RAM and `GPUtil` for Nvidia GPUs.
    *   *Return*: A dictionary normalized key-value pairs ready for the API.
*   **`SecurityMonitor.check_osquery_logs()`** (`backend/security_mon.py`):
    *   *Purpose*: Tails the `/var/log/osquery/osqueryd.results.log` file.
    *   *Logic*: Parses JSON logs looking for specific "snapshot" or "event" keys that match security queries defined in `osquery.conf`.

### B. Database (`backend/database.py`)
*   **`EndpointMetric` Model**: Stores time-series data of every heartbeat (CPU, RAM, etc.).
*   **`SecurityEvent` Model**: Stores high-level security alerts (e.g., "Malware Detected").
*   **Use Case**: Used by the Dashboard to generate historical reports (CSV export).

## 4. Business Logic

*   **`calculate_score(risk_prob, is_anomaly, alerts)`**:
    *   *Purpose*: Aggregates various signals into a single 0-100 Health Score.
    *   *Formula*: Starts at 100. Deducts points for high risk (-50), anomalies (-20), and active alerts (-10 each).
*   **`get_recommendations(status, features)`**:
    *   *Purpose*: Returns specific, actionable advice.
    *   *Logic*: Checks specific counters (e.g., `cpu > 80` -> "Kill Process"). If the endpoint is "Compromised", it defaults to "Isolate Endpoint".

## 4. Dashboard (`dashboard/app.py`)
The user interface built with Steamlit.

*   **`fetch_data()`**:
    *   *Purpose*: Polls the Backend API `/api/dashboard` endpoint every few seconds to get the latest snapshot of the fleet.
*   **`tab_reports` Logic**:
    *   *Purpose*: Converts the list of Alert dictionaries into a Pandas DataFrame and offers it as a CSV download (`st.download_button`).

## 5. Security Monitor (`backend/security_mon.py`)
Integration with Osquery.

*   **`check_osquery_logs()`**:
    *   *Purpose*: Reads the shared log file (`/var/log/osquery/osqueryd.results.log`).
    *   *Logic*: Parses JSON lines. tailored to look for specific "decorations" or query names (e.g., `simulated_attack`) and injects them into the main alerting pipeline.
