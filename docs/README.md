# Predictive Endpoint Security System (v2)

A complete, dockerized prototype for forecasting endpoint health and security risks using Machine Learning.

## 🏗️ Architecture
1.  **Backend (FastAPI)**: Serves the ML model and ingests data.
2.  **ML Engine**: Random Forest model trained on synthetic data (CPU, RAM, Disk patterns).
3.  **Dashboard (Streamlit)**: Real-time interactive UI for alerting and visualizing fleet status.
4.  **Monitoring**: 
    -   `Prometheus`: Scrapes metrics from backend and node-exporter.
    -   `Node Exporter`: Collects Docker host metrics.
5.  **Traffic Simulator**: Automatically sends fake "endpoint" data to the backend for the demo.

## 🚀 One-Command Setup
No manual installation required. Everything adheres to the "Code MUST run as-is with docker-compose" rule.

1.  **Run the System**:
    ```powershell
    docker-compose up --build -d
    ```
2.  **Access the Dashboard**:
    Open [http://localhost:8501](http://localhost:8501)
    
3.  **See Prometheus Metrics**:
    Open [http://localhost:9090](http://localhost:9090)

## 📁 Project Structure
- **/backend**: API Logic
- **/dashboard**: Viz Logic
- **/ml**: Training & Prediction
- **/configs**: Prometheus Config
- **/docker**: Dockerfiles
- **/notebooks**: Traffic Generator & Experiments

## 🧪 Guide de Test (Step-by-Step)

### 1. Verification of the Infrastructure
*   **Run**: `docker-compose ps`
*   **Check**: Ensure `backend`, `dashboard`, `prometheus`, `node-exporter` are all "Up" (running).

### 2. Dashboard Monitoring
*   Open **[http://localhost:8501](http://localhost:8501)**.
*   **Verify**: 
    *   Top Key Metrics (Monitored Endpoints, Avg Health) are updating.
    *   The "Live Endpoint Status" table shows different "Desktop-X" IDs.
    *   **Wait**: Every few seconds, the `traffic-simulator` sends new data.

### 3. Simulating an Attack
The system includes an automatic **Traffic Simulator**. You don't need to do anything manually!
*   **Watch**: Look at the "Security Alerts Log" on the Dashboard.
*   **Expectation**: Every ~10-20 seconds, the simulator sends "Attack Data" (High CPU, High Disk Usage).
*   **Result**: 
    1.  The Endpoint Status changes to **Compromised**.
    2.  A Red Alert appears in the log: *"DETECTED: Desktop-X - Compromised (Risk: 0.9x)"*.
    3.  The "Risk Distribution" chart updates.

### 4. Prometheus Metrics (Advanced)
*   Open **[http://localhost:9090](http://localhost:9090)**.
*   In the query bar, type: `endpoint_risk_score`.
*   Click **Execute** -> **Graph**.
*   **Result**: You should see the risk score lines moving up and down for each endpoint over time.
