import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_URL = "http://backend:8000/api"

st.set_page_config(page_title="DeepMind Sentinel", layout="wide", page_icon="🛡️")

# Custom CSS for "Premium" look
st.markdown("""
<style>
    .reportview-container {
        background: #0E1117;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #4F4F4F;
    }
    h1, h2, h3 {
        color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Predictive Endpoint Health & Security System")
st.markdown("Real-time AI-powered EDR monitoring")

# --- Sidebar ---
st.sidebar.header("Control Panel")
refresh_rate = st.sidebar.slider("Refresh Rate (s)", 1, 60, 2)
st.sidebar.markdown("---")
st.sidebar.info("Model Status: **Active** (LSTM + XGBoost)")

# Define Tabs
tab_overview, tab_alerts, tab_reports = st.tabs(["Overview", "Alerts & Incidents", "Reporting"])

# Placeholders inside tabs
with tab_overview:
    placeholder_overview = st.empty()
with tab_alerts:
    placeholder_alerts = st.empty()


def fetch_data():
    try:
        response = requests.get(f"{API_URL}/dashboard")
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None

while True:
    data = fetch_data()
    
    # --- Reporting Tab (Static-ish, only updates on interaction but we put it here to access latest data) ---
    with tab_reports:
        st.header("Incident Reporting")
        st.markdown("Download comprehensive reports of security incidents.")
        
        if data and data.get("alerts"):
            df_alerts = pd.DataFrame(data["alerts"])
            csv = df_alerts.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Download Incident Report (CSV)",
                data=csv,
                file_name=f"security_incidents_{int(time.time())}.csv",
                mime="text/csv",
                key="download-csv"
            )
            
            st.dataframe(df_alerts)
        else:
            st.info("No incident data available to generate report.")

    if not data:
        with placeholder_overview.container():
            st.error("Cannot connect to Backend API. Waiting...")
        time.sleep(5)
        continue
        
    endpoints = data.get("endpoints", [])
    alerts = data.get("alerts", [])
    
    # --- Overview Tab ---
    with placeholder_overview.container():
        # 1. Top Level KPIs
        total_endpoints = len(endpoints)
        if total_endpoints > 0:
            avg_health = sum(e["health_score"] for e in endpoints) / total_endpoints
            compromised_count = sum(1 for e in endpoints if e["status"] == "Compromised")
            
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            kpi1.metric("Active Endpoints", total_endpoints)
            kpi2.metric("Fleet Health Score", f"{avg_health:.1f}", delta=f"{avg_health-100:.1f}")
            kpi3.metric("Compromised", compromised_count, delta_color="inverse")
            kpi4.metric("Active Alerts", len(alerts), delta_color="inverse")
            
            st.divider()

            # 2. Main Visualizations
            col_left, col_right = st.columns([2, 1])
            
            df = pd.DataFrame(endpoints)
            
            if not df.empty:
                # Safe Extraction
                df["cpu"] = df["metrics"].apply(lambda x: x.get("cpu_usage", 0) if x else 0)
                df["mem"] = df["metrics"].apply(lambda x: x.get("memory_usage", 0) if x else 0)
                df["net"] = df["metrics"].apply(lambda x: x.get("network_traffic", 0) if x else 0)
                
                with col_left:
                    st.subheader("Endpoint Risk Matrix")
                    fig = px.scatter(df, x="cpu", y="risk_score", 
                                     size="mem", color="status",
                                     hover_name="endpoint_id",
                                     range_y=[0, 1.1], range_x=[0, 100],
                                     color_discrete_map={"Healthy": "#00CC96", "Compromised": "#FF4B4B", "Warning": "#FFA500"},
                                     title="Risk vs CPU Usage (Size = Memory)")
                    st.plotly_chart(fig, use_container_width=True, key=f"risk_matrix_{time.time()}")
            
                with col_right:
                    st.subheader("Health Distribution")
                    fig_pie = px.pie(df, names="status", values="health_score", 
                                     color="status", hole=.5,
                                     color_discrete_map={"Healthy": "#00CC96", "Compromised": "#FF4B4B", "Warning": "#FFA500"})
                    st.plotly_chart(fig_pie, use_container_width=True, key=f"health_pie_{time.time()}")

                st.divider()
                
                # New Graphics Section
                g1, g2 = st.columns(2)
                
                with g1:
                    st.subheader("Resource Heatmap (CPU/RAM)")
                    # Normalize for heatmap
                    heat_data = df[["endpoint_id", "cpu", "mem"]].set_index("endpoint_id")
                    fig_heat = px.imshow(heat_data.T, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r")
                    st.plotly_chart(fig_heat, use_container_width=True, key=f"heatmap_{time.time()}")

                with g2:
                    st.subheader("Network Traffic (KB/s)")
                    fig_bar = px.bar(df, x="endpoint_id", y="net", color="status",
                                     title="Real-time Bandwidth Usage",
                                     color_discrete_map={"Healthy": "#00CC96", "Compromised": "#FF4B4B"})
                    st.plotly_chart(fig_bar, use_container_width=True, key=f"net_bar_{time.time()}")

            # 3. Detailed Endpoint List
            st.subheader("Live Endpoint Status")
            
            for i, row in df.iterrows():
                with st.expander(f"{row['endpoint_id']} - {row['status']} (Health: {row['health_score']})", expanded=row['status']!="Healthy"):
                    c1, c2, c3 = st.columns(3)
                    metrics = row['metrics'] if row['metrics'] else {}
                    
                    # Fix: Safe access with defaults
                    cpu = metrics.get('cpu_usage', 0)
                    mem = metrics.get('memory_usage', 0)
                    disk = metrics.get('disk_usage', 0)
                    
                    c1.markdown(f"**CPU**: {cpu:.1f}%")
                    c1.markdown(f"**RAM**: {mem:.1f}%")
                    c1.markdown(f"**Disk**: {disk if disk is not None else 0:.1f}%")
                    
                    gpu = metrics.get('gpu_usage', 0)
                    net = metrics.get('network_traffic', 0)
                    
                    c2.markdown(f"**GPU**: {gpu:.1f}%")
                    c2.markdown(f"**Net**: {net:.0f} KB/s")
                    c2.markdown(f"**Procs**: {metrics.get('process_count', 0)}")
                    
                    c3.markdown(f"**Risk Prob**: {row['risk_score']:.2f}")
                    c3.markdown(f"**Trend**: {row['trend']}")
                    if row['action_required'] != "None":
                        c3.error(f"**Action**: {row['action_required']}")
                    else:
                        c3.success("**Action**: None")
        else:
            st.info("No endpoints connected yet.")
            
        # Toasts for Overview
        if alerts:
            latest = alerts[-1]
            # Simple check to avoid spamming toast on every loop for same alert logic would be complex here
            # For demo, just showing connection is alive
            pass

    # --- Alerts Tab ---
    with placeholder_alerts.container():
         st.subheader("🚨 Security Incident Log")
         
         if alerts:
             df_alerts = pd.DataFrame(alerts)
             # Filter options
             status_filter = st.multiselect("Filter by Status", df_alerts['status'].unique(), default=df_alerts['status'].unique(), key=f"filter_{time.time()}")
             
             filtered_df = df_alerts[df_alerts['status'].isin(status_filter)]
             
             st.dataframe(filtered_df, use_container_width=True)
             
             st.markdown("### Timeline")
             for _, alert in filtered_df.iloc[::-1].iterrows():
                 color = "red" if alert["status"] == "Compromised" else "orange"
                 st.markdown(f":{color}[{alert['timestamp']}] **{alert['endpoint_id']}** - {alert['status']} -> {alert['action_required']}")

         else:
             st.info("No alerts recorded.")

    time.sleep(refresh_rate)
