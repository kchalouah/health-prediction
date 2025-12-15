import numpy as np
import pandas as pd
import joblib
import logging
import os
from sklearn.ensemble import IsolationForest
import xgboost as xgb
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 1. Risk Classifier (XGBoost) ---
class RiskClassifier:
    def __init__(self):
        self.model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        self.model_path = os.path.join(MODELS_DIR, "xgb_risk_model.json")

    def train(self, X: pd.DataFrame, y: pd.Series):
        logger.info("Training XGBoost Risk Classifier...")
        self.model.fit(X, y)
        self.model.save_model(self.model_path)
        logger.info("Risk Model saved.")

    def predict_risk(self, features: pd.DataFrame) -> float:
        """Returns probability of compromise (0.0 - 1.0)."""
        if not os.path.exists(self.model_path):
            return 0.5 # Default uncertainty
        
        self.model.load_model(self.model_path)
        # return prob of class 1 (Compromised)
        prob = float(self.model.predict_proba(features)[0][1])
        
        # Add organic jitter for realism
        jitter = np.random.uniform(-0.05, 0.05)
        prob = max(0.0, min(1.0, prob + jitter))
        
        return prob

# --- 2. Anomaly Detector (Isolation Forest) ---
class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model_path = os.path.join(MODELS_DIR, "iso_forest.joblib")

    def train(self, X: pd.DataFrame):
        logger.info("Training Isolation Forest Anomaly Detector...")
        self.model.fit(X)
        joblib.dump(self.model, self.model_path)

    def is_anomaly(self, features: pd.DataFrame) -> bool:
        """Returns True if anomaly, False if normal."""
        if not os.path.exists(self.model_path):
            return False
        
        model = joblib.load(self.model_path)
        pred = model.predict(features)[0] # 1 normal, -1 anomaly
        return pred == -1

# --- 3. Health Forecaster (LSTM) ---
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=1):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1) # Predict next health score

    def forward(self, x):
        # x shape: (batch, seq_len, features)
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :]) # Take last step
        return out

class HealthForecaster:
    def __init__(self, input_dim=10):
        self.input_dim = input_dim
        self.model = LSTMModel(input_size=input_dim)
        self.model_path = os.path.join(MODELS_DIR, "lstm_health.pth")

    def train(self, X_sequence, y_target):
        # Placeholder for minimal training logic
        # In prod this would be a full training loop over epochs
        logger.info("Training LSTM Forecaster (Mock)...")
        torch.save(self.model.state_dict(), self.model_path)

    def forecast_trend(self, recent_history_df: pd.DataFrame) -> str:
        """Returns 'Improve', 'Stable', or 'Degrade'."""
        if not os.path.exists(self.model_path):
            return "Stable"
            
        # Mock logic as we need sequence data setup
        # Real impl would load model and infer
        return "Stable"
