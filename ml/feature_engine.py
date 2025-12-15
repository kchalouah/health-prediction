import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import EndpointMetric, SecurityEvent
import logging

logger = logging.getLogger(__name__)

class FeatureEngine:
    def __init__(self, db_session: Session):
        self.db = db_session

    def extract_features(self, endpoint_id: str) -> pd.DataFrame:
        """
        Extracts a feature vector for the given endpoint based on recent history.
        Returns a DataFrame row suitable for the ML model.
        """
        # 1. Fetch recent history (Last 1 hour for trends)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        metrics = self.db.query(EndpointMetric).filter(
            EndpointMetric.endpoint_id == endpoint_id,
            EndpointMetric.timestamp >= one_hour_ago
        ).order_by(EndpointMetric.timestamp.desc()).all()
        
        if not metrics:
            return self._get_empty_features()

        # Convert to Pandas
        data = [m.__dict__ for m in metrics]
        df = pd.DataFrame(data)
        if 'raw_data' in df.columns:
            df = df.drop(columns=['raw_data', '_sa_instance_state']) # Clean up

        # 2. Calculate Statistical Features
        latest = df.iloc[0]
        
        features = {
            # Instant features
            "cpu_usage": latest.cpu_usage,
            "memory_usage": latest.memory_usage,
            "disk_io": latest.disk_read + latest.disk_write,
            "network_traffic": latest.net_sent + latest.net_recv,
            "num_processes": latest.process_count,
            
            # Trend features (Rolling Stats)
            "cpu_mean_1h": df['cpu_usage'].mean(),
            "cpu_std_1h": df['cpu_usage'].std() if len(df) > 1 else 0.0,
            "mem_mean_1h": df['memory_usage'].mean(),
            "mem_trend": self._calculate_slope(df['memory_usage']), # Rising memory?
            
            # High load duration (percent of time CPU > 80%)
            "cpu_stress_ratio": (df[df['cpu_usage'] > 80].shape[0] / len(df)) if len(df) > 0 else 0
        }
        
        # 3. Security Events (Event Frequency)
        sec_events = self.db.query(SecurityEvent).filter(
            SecurityEvent.endpoint_id == endpoint_id,
            SecurityEvent.timestamp >= one_hour_ago
        ).count()
        
        features["file_changes"] = sec_events # Simplified for now
        
        return pd.DataFrame([features])

    def _calculate_slope(self, series: pd.Series) -> float:
        """Calculates the slope of the linear regression line for the series."""
        if len(series) < 2:
            return 0.0
        try:
            y = series.values
            x = np.arange(len(y))
            # Linear fit (degree 1)
            slope, _ = np.polyfit(x, y, 1)
            return slope
        except Exception:
            return 0.0

    def _get_empty_features(self):
        # Return zeros if cold start
        return pd.DataFrame([{
            "cpu_usage": 0, "memory_usage": 0, "disk_io": 0, "network_traffic": 0, 
            "num_processes": 0, "cpu_mean_1h": 0, "cpu_std_1h": 0, "mem_mean_1h": 0,
            "mem_trend": 0, "cpu_stress_ratio": 0, "file_changes": 0
        }])
