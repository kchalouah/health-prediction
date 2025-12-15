import json
import logging
import os
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

OSQUERY_LOG_PATH = "/var/log/osquery/osqueryd.results.log"

class SecurityMonitor:
    def __init__(self, log_path=OSQUERY_LOG_PATH):
        self.log_path = log_path
        self._last_position = 0
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        if not os.path.exists(self.log_path):
            # Create if not exists (for tests/startup)
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, 'a'):
                os.utime(self.log_path, None)

    def get_new_events(self) -> List[Dict[str, Any]]:
        """Reads new lines from the osquery results log."""
        events = []
        if not os.path.exists(self.log_path):
            return events

        try:
            with open(self.log_path, 'r') as f:
                # Move to last known position
                f.seek(self._last_position)
                
                lines = f.readlines()
                self._last_position = f.tell()

                for line in lines:
                    try:
                        if line.strip():
                            data = json.loads(line)
                            # Flatten useful fields
                            event = {
                                "timestamp": data.get("unixTime"),
                                "name": data.get("name"),
                                "action": data.get("action"),
                                "columns": data.get("columns", {})
                            }
                            events.append(event)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error reading security logs: {e}")
            
        return events

    def analyze_events(self, events: List[Dict]) -> Dict[str, Any]:
        """Aggregates raw events into security indicators."""
        summary = {
            "file_changes": 0,
            "process_events": 0,
            "socket_events": 0,
            "anomalies": []
        }
        
        for event in events:
            name = event.get("name")
            cols = event.get("columns", {})
            
            if name == "large_files":
                summary["file_changes"] += 1
                summary["anomalies"].append(f"Large file detected: {cols.get('path')} ({cols.get('size')} bytes)")
                
            elif name == "high_load_processes":
                summary["process_events"] += 1
                # Check for suspicious process names (basic heuristic)
                pname = cols.get("name", "")
                if pname in ["xmrig", "nc", "ncat"]:
                    summary["anomalies"].append(f"Suspicious process detected: {pname}")

            elif name == "listening_ports":
                summary["socket_events"] += 1
                port = cols.get("port")
                if port == "4444" or port == "6667": # Common C2 ports
                     summary["anomalies"].append(f"Suspicious port open: {port}")
                     
        return summary
