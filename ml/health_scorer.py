import logging
import random

logger = logging.getLogger(__name__)

class HealthScorer:
    def calculate_score(self, risk_prob: float, is_anomaly: bool, alerts: list) -> int:
        """
        Calculates a unified health score (0-100).
        100 = Perfect Health
        0 = Critical Failure / Compromise
        """
        base_score = 100
        
        # 1. Deduct for Risk
        # Risk prob 0.0 -> 1.0. If risk is 0.8, deduct 80 points.
        base_score -= (risk_prob * 100)
        
        # 2. Deduct for Anomaly
        if is_anomaly:
            base_score -= 20
            
        # 3. Deduct for active alerts
        # Count critical usage alerts from processing logic
        # (Assuming 'alerts' passed here are simple strings or dicts)
        base_score -= (len(alerts) * 10)
        
        # Clamp
        final_score = int(max(0, min(100, base_score)))
        
        return final_score

    def get_recommendations(self, risk_status: str, metrics: dict) -> list:
        recs = []
        
        # 1. Check specific triggers first (High Priority)
        cpu = metrics.get('cpu_usage', 0)
        net = metrics.get('network_traffic', 0)
        disk_io = metrics.get('disk_io', 0)
        files = metrics.get('file_changes', 0)
        
        if cpu > 85:
            recs.append("Kill High CPU Process (Potential Crypto-mining)")
        if net > 2000: # Adjust based on your traffic gen scale
            recs.append("Block Suspicious Outbound IPs (Exfiltration)")
        if disk_io > 100:
            recs.append("Enable Ransomware Shield (High Disk Activity)")
        if files > 15:
            recs.append("Lock Filesystem (Mass Modification)")

        # 2. Add General Actions if Compromised
        if risk_status == "Compromised":
            recs.append("Isolate Endpoint from Network")
            recs.append("Run Full Systems Scan")
        
        # 3. Warnings
        if not recs and risk_status == "Warning":
            recs.append("Monitor Closely")
            
        if not recs:
            recs.append("No actions required")
            
        return recs
