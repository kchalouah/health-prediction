import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODELS_DIR, "security_model.joblib")

def generate_synthetic_data(n_samples=5000):
    """Generates synthetic endpoint activity data."""
    logger.info(f"Generating {n_samples} synthetic records...")
    
    # Normal behavior (80%)
    n_normal = int(n_samples * 0.8)
    normal_data = {
        "cpu_usage": np.random.normal(25, 10, n_normal),
        "memory_usage": np.random.normal(40, 15, n_normal),
        "disk_io": np.random.normal(10, 5, n_normal),
        "network_traffic": np.random.normal(50, 20, n_normal),
        "num_processes": np.random.normal(100, 20, n_normal),
        "file_changes": np.random.poisson(2, n_normal),
        "label": 0  # Healthy
    }
    
    # Anomalous/Attack behavior (20%)
    n_attack = n_samples - n_normal
    attack_data = {
        "cpu_usage": np.random.normal(85, 10, n_attack),  # High CPU (Crypto mining)
        "memory_usage": np.random.normal(80, 10, n_attack),
        "disk_io": np.random.normal(80, 20, n_attack),  # High Disk (Ransomware)
        "network_traffic": np.random.normal(200, 50, n_attack), # Exfiltration
        "num_processes": np.random.normal(250, 50, n_attack), # Fork bomb?
        "file_changes": np.random.poisson(50, n_attack), # Mass modification
        "label": 1  # Compromised
    }
    
    # Combine
    df_normal = pd.DataFrame(normal_data)
    df_attack = pd.DataFrame(attack_data)
    df = pd.concat([df_normal, df_attack]).sample(frac=1).reset_index(drop=True)
    
    # Clip values
    df["cpu_usage"] = df["cpu_usage"].clip(0, 100)
    df["memory_usage"] = df["memory_usage"].clip(0, 100)
    
    return df

def train_model():
    """Trains and saves the model."""
    df = generate_synthetic_data()
    
    X = df.drop("label", axis=1)
    y = df["label"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    logger.info("Training Random Forest Model...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"Model Accuracy: {acc:.4f}")
    logger.info(f"\n{classification_report(y_test, y_pred)}")
    
    # Save
    joblib.dump(clf, MODEL_FILE)
    logger.info(f"Model saved to {MODEL_FILE}")

def predict(features):
    """Predicts health status from features."""
    if not os.path.exists(MODEL_FILE):
        logger.warning("Model not found. Training now...")
        train_model()
        
    clf = joblib.load(MODEL_FILE)
    
    # Features dataframe
    df = pd.DataFrame([features])
    
    import random
    
    # Probability of attack
    risk_prob = clf.predict_proba(df)[0][1]
    
    # Add some organic jitter/noise so it feels more "alive" (±5%)
    jitter = random.uniform(-0.05, 0.05)
    risk_prob = max(0.0, min(1.0, risk_prob + jitter))
    
    prediction = "Compromised" if risk_prob > 0.5 else "Healthy"
    
    return risk_prob, prediction

if __name__ == "__main__":
    train_model()
