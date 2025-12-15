import pandas as pd
import numpy as np
import logging
from ml.models import RiskClassifier, AnomalyDetector, HealthForecaster

logger = logging.getLogger(__name__)

def generate_synthetic_data(n_samples=5000):
    """Generates synthetic endpoint telemetry for training."""
    logger.info(f"Generating {n_samples} synthetic records...")
    
    # Healthy Data
    n_normal = int(n_samples * 0.85)
    normal = {
        "cpu_usage": np.random.normal(20, 10, n_normal),
        "memory_usage": np.random.normal(40, 10, n_normal),
        "disk_io": np.random.normal(5000, 2000, n_normal),
        "network_traffic": np.random.normal(10000, 5000, n_normal),
        "num_processes": np.random.normal(120, 20, n_normal),
        "file_changes": np.random.poisson(1, n_normal),
        # Trend features
        "cpu_mean_1h": np.random.normal(20, 5, n_normal),
        "cpu_std_1h": np.random.normal(5, 2, n_normal),
        "mem_mean_1h": np.random.normal(40, 5, n_normal),
        "mem_trend": np.random.normal(0, 0.1, n_normal),
        "cpu_stress_ratio": np.zeros(n_normal),
        "label": 0
    }
    
    # Compromised Data (Crypto Mining, Ransomware, Exfiltration)
    n_attack = n_samples - n_normal
    attack = {
        "cpu_usage": np.random.normal(90, 5, n_attack),
        "memory_usage": np.random.normal(85, 10, n_attack),
        "disk_io": np.random.normal(500000, 100000, n_attack), # Ransomware
        "network_traffic": np.random.normal(1000000, 200000, n_attack), # Exfil
        "num_processes": np.random.normal(250, 50, n_attack),
        "file_changes": np.random.poisson(20, n_attack),
        # Trend features
        "cpu_mean_1h": np.random.normal(85, 5, n_attack),
        "cpu_std_1h": np.random.normal(15, 5, n_attack),
        "mem_mean_1h": np.random.normal(80, 5, n_attack),
        "mem_trend": np.random.normal(1.5, 0.5, n_attack),
        "cpu_stress_ratio": np.full(n_attack, 0.8),
        "label": 1
    }
    
    df = pd.concat([pd.DataFrame(normal), pd.DataFrame(attack)])
    
    # Clip and Noise
    for col in df.columns:
        if col != 'label':
             df[col] = df[col] + np.random.normal(0, 0.1, len(df))
             
    df['cpu_usage'] = df['cpu_usage'].clip(0, 100)
    df['memory_usage'] = df['memory_usage'].clip(0, 100)
    
    return df.sample(frac=1).reset_index(drop=True)

def train_all():
    """Main training routine."""
    df = generate_synthetic_data()
    
    # Features (Drop label)
    X = df.drop("label", axis=1)
    y = df["label"]
    
    # 1. Train Risk Classifier
    risk_model = RiskClassifier()
    risk_model.train(X, y)
    
    # 2. Train Anomaly Detector (Use only normal data for training ideally, but semi-supervised here)
    # We train on everything but anticipate outliers
    iso_model = AnomalyDetector()
    iso_model.train(X)
    
    # 3. Train Forecaster (Mock for now as we lack sequences in simple synthetic gen)
    # in production we would generate sequences
    lstm_model = HealthForecaster()
    lstm_model.train(None, None)
    
    logger.info("All models trained successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_all()
