# Predictive Endpoint Health & Security Forecast System
**Final Project Documentation**

---

## 📖 1. Project Overview
This project is a **proactive cybersecurity system** designed to predict endpoint health issues before they occur. Unlike traditional antivirus software that relies on known signatures, our solution uses **Machine Learning** to analyze behavioral patterns (CPU usage, Disk I/O, Network Traffic) and detect anomalies like Ransomware, Cryptojacking, or system exhaustion.

**Key Features:**
*   **Real-time Monitoring**: Continuous tracking of system metrics.
*   **AI-Powered Detection**: Random Forest model to classify behavior as "Healthy" or "Compromised".
*   **Predictive Alerting**: Generates a risk score (0-100%) to warn administrators.
*   **Fully Dockerized**: Deploys instantly with zero configuration.

---

## 🏗️ 2. System Architecture
The system follows a microservices architecture orchestrated by **Docker Compose**:

### A. The Backend (FastAPI)
*   **Role**: The central nervous system.
*   **Function**: Receives metrics via API, runs the ML inference engine, and exposes data for the Dashboard.
*   **Tech**: Python 3.10, FastAPI, Uvicorn.

### B. The Intelligence (ML Engine)
*   **Role**: The brain.
*   **Function**: Contains a **Random Forest Classifier**.
    *   **Training**: Automatically generates a synthetic dataset on startup (10,000+ samples) containing normal usage patterns and attack signatures.
    *   **Inference**: Takes live metrics tuple `(cpu, ram, disk, net, files)` -> Returns `(RiskProbability, Status)`.

### C. The Dashboard (Streamlit)
*   **Role**: The visual interface.
*   **Function**: Polls the backend every 2s for updates.
*   **Visuals**:
    *   **Health Gauge**: Live average health of the fleet.
    *   **Attack Log**: Real-time feed of detected incidents.
    *   **Correlations**: Scatter plots showing relationships between resource usage and risk.

### D. Monitoring & Simulation
*   **Prometheus**: Industry-standard time-series database scraping `/metrics`.
*   **Node Exporter**: Collects low-level kernel metrics from the host.
*   **Traffic Simulator**: A Python script that acts as a "Virtual Endpoint Fleet", sending data to the backend. It has a built-in "Chaos Mode" (35% probability) to simulate attacks for demonstration.

---

## 🚀 3. Installation & Usage Guide

### Prerequisites
*   Docker Desktop installed and running.

### Step 1: Start the System
Open a terminal in the project folder and run:
```bash
docker-compose up --build -d
```
*Wait ~30 seconds for the images to build and the ML model to train.*

### Step 2: Access Interfaces
*   **Main Dashboard**: [http://localhost:8501](http://localhost:8501)
*   **Prometheus**: [http://localhost:9090](http://localhost:9090)
*   **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Step 3: Stop the System
```bash
docker-compose down
```

---

## 🧠 4. Machine Learning Methodology

### Feature Engineering
We extract 6 key features to determine health:
1.  `cpu_usage`: High sustained usage often indicates mining or infinite loops.
2.  `disk_io`: Rapid mass-writes indicate Ransomware encryption.
3.  `network_traffic`: Large outbound transfer indicates Data Exfiltration.
4.  `memory_usage`: Memory leaks or heavy payloads.
5.  `file_changes`: Unauthorized modification of system files.
6.  `num_processes`: Fork bombs or malware spawning.

### Model Choice
We selected **Random Forest** because:
*   It handles non-linear relationships well (e.g., High CPU is fine *unless* combined with High Disk).
*   It is explainable (Feature Importance).
*   It is robust against overfitting on synthetic data.

---

## 📂 5. Folder Structure
*   `/backend`: API code and Pydantic models.
*   `/ml`: Data generator and Model training logic (`engine.py`).
*   `/dashboard`: Streamlit frontend application.
*   `/docker`: Dockerfiles for each service.
*   `/notebooks`: Jupyter notebooks and the traffic simulator.
*   `/configs`: Configuration for Prometheus and OSQuery.

---

**Developed for the Academic Year 2025-2026**
