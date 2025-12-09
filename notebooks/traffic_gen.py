import requests
import time
import random
import logging

logging.basicConfig(level=logging.INFO)

API_URL = "http://backend:8000/api/metrics"

def generate_payload():
    # 65% chance of healthy data (meaning 35% ATTACKS!)
    is_normal = random.random() < 0.65
    
    if is_normal:
        return {
            "endpoint_id": f"Desktop-{random.randint(1, 5)}",
            "cpu_usage": random.uniform(10, 40),
            "memory_usage": random.uniform(30, 60),
            "disk_io": random.uniform(0, 20),
            "network_traffic": random.uniform(0, 100),
            "num_processes": int(random.uniform(50, 120)),
            "file_changes": int(random.expovariate(1.0))
        }
    else:
        # Attack!
        return {
            "endpoint_id": f"Desktop-{random.randint(1, 5)}",
            "cpu_usage": random.uniform(80, 100),
            "memory_usage": random.uniform(70, 95),
            "disk_io": random.uniform(50, 100),
            "network_traffic": random.uniform(500, 2000),
            "num_processes": int(random.uniform(200, 500)),
            "file_changes": int(random.uniform(20, 100))
        }

if __name__ == "__main__":
    print("Starting Synthetic Traffic Generator...")
    time.sleep(5) # Wait for backend
    
    while True:
        try:
            data = generate_payload()
            requests.post(API_URL, json=data)
            print(f"Sent: {data['endpoint_id']} - CPU: {data['cpu_usage']:.1f}%")
        except Exception as e:
            print(f"Connection Error: {e}")
        
        time.sleep(2)
