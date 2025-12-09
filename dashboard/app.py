import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px

# Configuration
API_URL = "http://backend:8000/api" # Inside Docker network
# For local dev, might need localhost
# API_URL = "http://localhost:8000/api"

st.set_page_config(page_title="Endpoint Sentinel", layout="wide", page_icon="🛡️")

st.title("🛡️ Predictive Endpoint Health & Security")

# Top Metrics Row
kpi1, kpi2, kpi3 = st.columns(3)

def fetch_data():
    try:
        response = requests.get(f"{API_URL}/dashboard")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return None
    return None

placeholder = st.empty()

while True:
    data = fetch_data()
    
    with placeholder.container():
        if not data:
            st.error("Cannot connect to Backend API. Is Docker running?")
            time.sleep(5)
            continue
            
        endpoints = data.get("endpoints", [])
        alerts = data.get("alerts", [])
        
        # Calculate Aggregates
        total_endpoints = len(endpoints)
        compromised = sum(1 for e in endpoints if e["status"] == "Compromised")
        avg_health = sum(e["health_score"] for e in endpoints) / total_endpoints if total_endpoints else 100
        
        with kpi1:
            st.metric("Monitored Endpoints", total_endpoints)
        with kpi2:
            st.metric("Security Incidents", compromised, delta_color="inverse")
        with kpi3:
            st.metric("Avg Fleet Health", f"{avg_health:.1f}%", delta=f"{avg_health-100:.1f}")

        # Charts Section
        col1, col2 = st.columns(2)
        
        if endpoints:
            df = pd.DataFrame(endpoints)
            
            with col1:
                st.subheader("Risk Distribution")
                fig = px.pie(df, names="status", values="risk_score", color="status",
                             color_discrete_map={"Healthy": "#00CC96", "Compromised": "#EF553B"},
                             hole=0.4)
                st.plotly_chart(fig, use_container_width=True, key=f"risk_pie_{time.time()}")
                
            with col2:
                st.subheader("CPU vs Risk Correlation")
                # Extract metrics from nested dict if pandas didn't flatten it
                # Assuming flat for simplicity or normalizing
                try:
                    df["cpu"] = df["metrics"].apply(lambda x: x["cpu_usage"])
                    df["risk"] = df["risk_score"]
                    fig2 = px.scatter(df, x="cpu", y="risk", color="status", size="risk",
                                      hover_data=["endpoint_id"],
                                      color_discrete_map={"Healthy": "#00CC96", "Compromised": "#EF553B"})
                    st.plotly_chart(fig2, use_container_width=True, key=f"cpu_scatter_{time.time()}")
                except:
                    st.info("Waiting for more data points...")

        # endpoints table
        st.subheader("Live Endpoint Status")
        if endpoints:
            # Flatten for display
            flat_data = []
            for e in endpoints:
               row = {
                   "ID": e["endpoint_id"],
                   "Status": e["status"],
                   "Health": f"{e['health_score']}%",
                   "Risk Score": f"{e['risk_score']:.2f}",
                   "Action": e["action_required"],
                   "Last Update": e["timestamp"]
               }
               flat_data.append(row)
            
            st.dataframe(pd.DataFrame(flat_data), use_container_width=True)

        # Alerts
        if alerts:
            st.subheader("🚨 Security Alerts Log")
            for alert in reversed(alerts[-5:]):
                st.warning(f"**DETECTED**: {alert['endpoint_id']} - {alert['status']} (Risk: {alert['risk_score']:.2f}) - Recommended: {alert['action_required']}")

    time.sleep(2)
