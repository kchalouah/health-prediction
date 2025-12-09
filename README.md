# Endpoint Sentinel AI

## Overview
A predictive endpoint security system that monitors system health and uses machine learning to detect anomalies (e.g., malware, resource exhaustion) before they cause failure.

## Architecture
- **Agent**: Python script (`agent/main.py`) collecting metrics via `psutil`.
- **Backend**: FastAPI (`backend/main.py`) for data ingestion and API.
- **ML Engine**: Scikit-Learn Isolation Forest (`backend/ml_engine.py`) for anomaly detection.
- **Frontend**: React + Tailwind (`frontend/`) for real-time dashboard.

## Installation

1. **Backend & Agent setup**:
   **Windows (PowerShell)**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   pip install -r requirements.txt
   ```
   
   **Mac/Linux**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   ```

## Running the System (Docker + Host Agent)

This is the recommended way to run the project.

### 1. Start Backend & Dashboard (Docker)
This will start the Database, API, and Frontend web server.
```powershell
docker-compose up --build
```
*Wait until you see "Uvicorn running on http://0.0.0.0:8000"*

### 2. Start the Agent (On Host)
The agent runs on your physical machine to send *real* data.
**First time setup only:**
```powershell
# Create/Activate environment
python -m venv venv
.\venv\Scripts\Activate

# Install ONLY the agent dependencies (Fast & Light)
pip install -r requirements-agent.txt
```

**Run the Agent:**
```powershell
python agent/main.py
```

### 3. Open Dashboard
Go to [http://localhost:5173](http://localhost:5173) in your browser.

### 4. System Usage
- The **Status Card** will show your PC's health.
- To test the detection, run the simulator in a new terminal window:
  ```powershell
  python agent/simulator.py
  ```
  *This will safely generate CPU load to trigger the alarm.*

## ML Training
To retrain the model with new data:
```bash
python notebooks/generate_data.py
python backend/train_model.py
```
