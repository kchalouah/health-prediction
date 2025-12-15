# Predictive Endpoint Health & Security Forecast System v2.0
**Final Project Documentation - Extended Edition**

---

## 📖 1. Project Overview
This project is an advanced **Predictive EDR System** that forecasts endpoint health and security risks. It moves beyond simple signatures to analyzes behavioral patterns using Time-Series Forecasting and Anomaly Detection.

**New Capabilities (v2.0):**
*   **Full Supervision**: Monitors CPU, Memory, Disk I/O, Network Traffic, and GPU usage.
*   **Security Telemetry**: Integrates **Osquery** logs for file integrity and process monitoring.
*   **Advanced ML**:
    *   **XGBoost**: For risk classification (Healthy vs Compromised).
    *   **Isolation Forest**: For zero-day anomaly detection.
    *   **LSTM (PyTorch)**: For health trend forecasting.
*   **Production Architecture**: Uses SQLite persistence, Background Scheduler, and Docker volumes.

---

## 🏗️ 2. System Architecture

### A. The Backend (FastAPI + Scheduler)
*   **`backend/main.py`**: Runs the API and a background scheduler (every 5s) to collect metrics.
*   **`backend/collector.py`**: Uses `psutil` and `GPUtil` to fetch system resources.
*   **`backend/security_mon.py`**: Watches `/var/log/osquery` for events.
*   **`backend/database.py`**: SQLite persistence layer (`endpoint.db`).

### B. Machine Learning Engine
*   **`ml/feature_engine.py`**: Transforms raw metrics into rolling windows (mean/std/trend over 1h).
*   **`ml/models.py`**: Encapsulates the 3 ML models (Risk, Anomaly, Forecast).
*   **`ml/health_scorer.py`**: Computes the final 0-100 score based on risk prob and anomalies.

### C. The Dashboard (Streamlit)
*   **Overview Tab**: Fleet Health KPIs, Real-time Risk Matrix, and Resource Heatmaps.
*   **Alerts Tab**: Filterable timeline of security incidents with specific recommendations.
*   **Reporting Tab**: Feature to export security incidents as CSV reports.
*   **Visualizations**: Risk Matrix (Scatter), Health Distribution (Pie), Network Traffic (Bar).

---

## 🚀 3. Installation & Usage

### Prerequisites
*   Docker Desktop installed.
*   (Optional) NVIDIA GPU for GPU monitoring.

### Step 1: Start the System
```bash
docker-compose up --build -d
```
*Wait ~1 minute. The system will automatically generate synthetic training data and train the initial models on startup.*

### Step 2: Access Interfaces
*   **Dashboard**: [http://localhost:8501](http://localhost:8501)
*   **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Prometheus**: [http://localhost:9090](http://localhost:9090)

### Step 3: Verify Functionality
1.  Open the Dashboard.
2.  Watch the "Local-Machine-01" endpoint appear.
3.  Simulate an attack (if using `traffic_gen.py` or manually consuming resources).
4.  Observe the "Risk Score" increase and "Action Required" update.

---

## 🧠 4. ML Evaluation
*   **Accuracy**: ~95% on synthetic validation set.
*   **Latency**: Inference takes <50ms per endpoint.
*   **Models**:
    *   `RiskClassifier`: XGBoost (Gradient Boosting)
    *   `AnomalyDetector`: Isolation Forest (Unsupervised)
    *   `HealthForecaster`: LSTM (Sequence Modeling)

---

**Developed for the Academic Year 2025-2026**
