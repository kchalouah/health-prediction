from fastapi import FastAPI, BackgroundTasks
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import logging
from datetime import datetime
import pandas as pd
from prometheus_client import make_asgi_app, Gauge

from backend.database import init_db, SessionLocal, EndpointMetric, SecurityEvent
from backend.collector import SystemMonitor
from backend.security_mon import SecurityMonitor
from ml import train
from ml.models import RiskClassifier, AnomalyDetector, HealthForecaster
from ml.health_scorer import HealthScorer
from ml.feature_engine import FeatureEngine

# Setup Persistence
init_db()

# Models
risk_clf = RiskClassifier()
anomaly_det = AnomalyDetector()
forecaster = HealthForecaster()
scorer = HealthScorer()

# Monitors
sys_mon = SystemMonitor()
sec_mon = SecurityMonitor()

app = FastAPI(title="DeepMind Endpoint Sentinel")

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
HEALTH_GAUGE = Gauge('endpoint_health_score', 'Overall Health Score', ['endpoint_id'])
RISK_GAUGE = Gauge('endpoint_risk_prob', 'Risk Probability', ['endpoint_id'])
CPU_GAUGE = Gauge('endpoint_cpu_usage', 'CPU Usage %', ['endpoint_id'])
MEMORY_GAUGE = Gauge('endpoint_memory_usage', 'Memory Usage %', ['endpoint_id'])

# State
state = {
    "endpoints": {},
    "alerts": []
}

def monitor_loop():
    """Background task to collect metrics and run inference."""
    session = SessionLocal()
    endpoint_id = "local-machine-01" # Single endpoint demo
    
    try:
        # 1. Collect
        raw_metrics = sys_mon.get_metrics()
        
        # 2. Persist System Metrics
        metric_entry = EndpointMetric(
            endpoint_id=endpoint_id,
            timestamp=datetime.utcnow(),
            cpu_usage=raw_metrics.get('cpu_usage'),
            memory_usage=raw_metrics.get('memory_usage'),
            disk_usage=raw_metrics.get('disk_usage'),
            disk_read=raw_metrics.get('disk_read_bytes'),
            disk_write=raw_metrics.get('disk_write_bytes'),
            net_sent=raw_metrics.get('net_sent_bytes'),
            net_recv=raw_metrics.get('net_recv_bytes'),
            gpu_usage=raw_metrics.get('gpu_usage'),
            process_count=raw_metrics.get('process_count'),
            raw_data=raw_metrics
        )
        session.add(metric_entry)
        
        # 3. Collect & Persist Security Events
        events = sec_mon.get_new_events()
        security_summary = sec_mon.analyze_events(events)
        
        for evt in events:
            db_evt = SecurityEvent(
                endpoint_id=endpoint_id,
                event_type=evt.get("name"),
                details=str(evt.get("columns")),
                severity="WARNING"
            )
            session.add(db_evt)
            
        session.commit()
        
        # 3. Calculate Features
        feature_engine = FeatureEngine(session)
        features_df = feature_engine.extract_features(endpoint_id)
        
        # Ensure numeric types for XGBoost
        features_df = features_df.astype(float)
        
        # 4. Inference
        risk_prob = risk_clf.predict_risk(features_df)
        is_anomaly = anomaly_det.is_anomaly(features_df)
        trend = forecaster.forecast_trend(features_df)
        
        # 6. Scoring & Recommendations
        alerts = security_summary["anomalies"]
        health_score = scorer.calculate_score(risk_prob, is_anomaly, alerts)
        
        status = "Healthy"
        if risk_prob > 0.7 or len(alerts) > 0:
            status = "Compromised"
        elif is_anomaly:
            status = "Warning"
            
        recommendations = scorer.get_recommendations(status, raw_metrics)
        
        # 7. Update State
        state["endpoints"][endpoint_id] = {
            "endpoint_id": endpoint_id,
            "timestamp": datetime.utcnow().isoformat(),
            "health_score": health_score,
            "risk_score": risk_prob,
            "status": status,
            "trend": trend,
            "metrics": raw_metrics,
            "action_required": recommendations[0] if recommendations else "None"
        }
        
        # Alerts
        if status != "Healthy":
            alert_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint_id": endpoint_id,
                "status": status,
                "risk_score": risk_prob,
                "action_required": recommendations[0] if recommendations else "Check logs"
            }
            state["alerts"].append(alert_entry)
            
        # Prometheus
        HEALTH_GAUGE.labels(endpoint_id=endpoint_id).set(health_score)
        RISK_GAUGE.labels(endpoint_id=endpoint_id).set(risk_prob)
        CPU_GAUGE.labels(endpoint_id=endpoint_id).set(raw_metrics.get("cpu_usage", 0))
        MEMORY_GAUGE.labels(endpoint_id=endpoint_id).set(raw_metrics.get("memory_usage", 0))
        
    except Exception as e:
        logging.error(f"Monitor loop failed: {e}")
    finally:
        session.close()

scheduler = BackgroundScheduler()
scheduler.add_job(monitor_loop, 'interval', seconds=5)

from pydantic import BaseModel

class MetricsPayload(BaseModel):
    endpoint_id: str
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_traffic: float
    num_processes: int
    file_changes: int

@app.post("/api/metrics")
async def receive_metrics(payload: MetricsPayload):
    # 1. Adapt payload to DF
    features = {
        "cpu_usage": payload.cpu_usage,
        "memory_usage": payload.memory_usage,
        "disk_io": payload.disk_io,
        "network_traffic": payload.network_traffic,
        "num_processes": payload.num_processes,
        "file_changes": payload.file_changes, 
        # Missing trends for synthetic data - assume stable/zero for now to avoid errors
        "cpu_mean_1h": payload.cpu_usage,
        "cpu_std_1h": 0.0,
        "mem_mean_1h": payload.memory_usage,
        "mem_trend": 0.0,
        "cpu_stress_ratio": 1.0 if payload.cpu_usage > 80 else 0.0
    }
    
    df = pd.DataFrame([features]).astype(float)
    
    # 2. Inference
    risk_prob = risk_clf.predict_risk(df)
    is_anomaly = anomaly_det.is_anomaly(df)
    trend = forecaster.forecast_trend(df)
    
    # 3. Scoring
    alerts = []
    if payload.file_changes > 10:
        alerts.append("High file modification rate")
    
    health_score = scorer.calculate_score(risk_prob, is_anomaly, alerts)
    
    status = "Healthy"
    if risk_prob > 0.7:
        status = "Compromised"
    elif is_anomaly:
        status = "Warning"
        
    # Recommendations
    recs = scorer.get_recommendations(status, payload.model_dump())

    # 4. Update State
    result = {
        "endpoint_id": payload.endpoint_id,
        "timestamp": datetime.utcnow().isoformat(),
        "health_score": health_score,
        "risk_score": risk_prob,
        "status": status,
        "trend": trend,
        "metrics": payload.model_dump(),
        "action_required": recs[0] if recs else "None"
    }
    
    state["endpoints"][payload.endpoint_id] = result
    
    if status != "Healthy":
        alert_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint_id": payload.endpoint_id,
            "status": status,
            "risk_score": risk_prob,
            "action_required": recs[0] if recs else "None"
        }
        state["alerts"].append(alert_entry)
        
    # Update Prometheus Metrics
    HEALTH_GAUGE.labels(endpoint_id=payload.endpoint_id).set(health_score)
    RISK_GAUGE.labels(endpoint_id=payload.endpoint_id).set(risk_prob)
    CPU_GAUGE.labels(endpoint_id=payload.endpoint_id).set(payload.cpu_usage)
    MEMORY_GAUGE.labels(endpoint_id=payload.endpoint_id).set(payload.memory_usage)
        
    return result

@app.on_event("startup")
async def startup_event():
    logging.info("Starting up...")
    train.train_all() # Ensure models exist
    scheduler.start()

@app.get("/api/dashboard")
def get_dashboard_data():
    return {
        "endpoints": list(state["endpoints"].values()),
        "alerts": state["alerts"][-100:]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
