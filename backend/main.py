from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import sys
import os
import uvicorn
import logging
from datetime import datetime
from prometheus_client import make_asgi_app, Gauge

# Add parent dir to path to import ml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml import engine

app = FastAPI(title="Predictive Endpoint Security API")

# Prometheus Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

RISK_GAUGE = Gauge('endpoint_risk_score', 'Current risk score of endpoint', ['endpoint_id'])
CPU_GAUGE = Gauge('endpoint_cpu_usage', 'CPU usage of endpoint', ['endpoint_id'])

# In-memory storage for demo
endpoint_state = {}
alert_history = []

class MetricsPayload(BaseModel):
    endpoint_id: str
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_traffic: float
    num_processes: int
    file_changes: int

@app.on_event("startup")
async def startup_event():
    # Retrain model on startup to ensure it exists
    engine.train_model()

@app.post("/api/metrics")
async def receive_metrics(payload: MetricsPayload):
    # 1. Run Prediction
    features = {
        "cpu_usage": payload.cpu_usage,
        "memory_usage": payload.memory_usage,
        "disk_io": payload.disk_io,
        "network_traffic": payload.network_traffic,
        "num_processes": payload.num_processes,
        "file_changes": payload.file_changes
    }
    
    risk_score, status = engine.predict(features)
    
    # Update Prometheus
    RISK_GAUGE.labels(endpoint_id=payload.endpoint_id).set(risk_score)
    CPU_GAUGE.labels(endpoint_id=payload.endpoint_id).set(payload.cpu_usage)
    
    # 2. Generate Health Score (Inverted Risk)
    health_score = int((1.0 - risk_score) * 100)
    
    # 3. Update State
    result = {
        "endpoint_id": payload.endpoint_id,
        "timestamp": datetime.utcnow(),
        "metrics": payload.model_dump(),
        "risk_score": risk_score,
        "health_score": health_score,
        "status": status,
        "action_required": "None"
    }
    
    if status == "Compromised":
        result["action_required"] = "Isolate Endpoint & Scan"
        alert_history.append(result)
        
    endpoint_state[payload.endpoint_id] = result
    return result

@app.get("/api/dashboard")
def get_dashboard_data():
    return {
        "endpoints": list(endpoint_state.values()),
        "alerts": alert_history[-50:] # Last 50 alerts
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
