# Endpoint Sentinel AI (v2.0)

## Overview
A comprehensive **Predictive Endpoint Detection & Response (PEDR)** system. It monitors system health (CPU, RAM, Network, GPU) and security events (File Integrity, Process spawning) to forecast anomalies and potential compromises before they crash the system.

## 🏗️ Architecture (v2.0)
- **Monitoring Agent**: Python (`backend/collector.py`) collecting full system telemetry.
- **Security Agent**: **Osquery** based daemon for deep system introspection.
- **Backend**: FastAPI (`backend/main.py`) with SQLite persistence & Background Scheduler.
- **ML Engine**: XGBoost (Risk), Isolation Forest (Anomaly), and PyTorch LSTM (Forecasting).
- **Dashboard**: **Streamlit** premium UI with Real-time Charts, Alerting, and Reporting.

## 🚀 Installation & Usage

### 1. Requirements
*   Docker Desktop installed.
*   (Optional) NVIDIA GPU for GPU monitoring.

### 2. Start the System
The entire specific is containerized. Run:
```powershell
docker-compose up --build -d
```
*Note: The first run might take a few minutes to build the ML images and train the initial models.*

### 3. Access the Dashboard
Go to **[http://localhost:8501](http://localhost:8501)** in your browser.

- **Overview Tab**: Live fleet status, Risk Matrix, and Health Scores.
- **Alerts Tab**: Historical log of all security incidents.
- **Reporting Tab**: Download specific incident reports as CSV.

### 4. Monitoring & Metrics
*   **Prometheus**: [http://localhost:9090](http://localhost:9090) (System Metrics)
*   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

## 🧪 Simulation & Testing
The system includes a **Traffic Simulator** container (`traffic-simulator`) that generates mock data for 5 virtual desktops.
To test specific scenarios (e.g., Crypto Mining), the system detects patterns like:
- **High CPU + Network** -> Potential Initial Access / Mining
- **Mas File Changes** -> Potential Ransomware

## 🧠 Machine Learning Models
- **Risk Classifier**: `XGBoost` trained on synthetic attack patterns.
- **Anomaly Logic**: `Isolation Forest` for detecting unknown threats.
- **Health Trend**: `LSTM` (PyTorch) for time-series forecasting.
