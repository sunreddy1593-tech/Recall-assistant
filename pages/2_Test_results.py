import streamlit as st
import pandas as pd
import os
import json
from recall.ui import load_css, render_top_banner, render_brand_header

st.set_page_config(page_title="Recall · Test Results", layout="wide")
load_css()

render_top_banner()
render_brand_header(show_stream_pill=False)

st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:12px;">🧪 Usability Metrics</span>
    </div>
    <h1 style="margin-top: 4px; margin-bottom: 4px;">User Test Results</h1>
    <p style="font-size: 14px; color: #515F74; margin-bottom: 20px;">
        Evaluation session metrics and interaction logs for Recall prototype.
    </p>
""", unsafe_allow_html=True)

LOG_FILE = "logs/events.jsonl"
df = pd.DataFrame()

if 'LOGS_SHEET_CSV_URL' in st.secrets:
    csv_url = st.secrets['LOGS_SHEET_CSV_URL']
    if "/edit" in csv_url:
        csv_url = csv_url.replace("/edit?", "/export?format=csv&").replace("#", "&")
    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"Failed to load logs from Google Sheets: {e}")
else:
    if os.path.exists(LOG_FILE):
        data = []
        with open(LOG_FILE, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except:
                        pass
        df = pd.DataFrame(data)

if df.empty:
    st.info("No log entries found.")
else:
        
        show_all = st.checkbox("Show all sources (including tests)", value=False)
        if not show_all and 'source' in df.columns:
            df = df[df['source'] == 'participant']
            
        if df.empty:
            st.info("No logs matching selected source.")
        else:
            tasks_started = df[df['event'] == 'task_start']
            tasks_completed = df[df['event'] == 'photo_confirmed']
            tasks_gave_up = df[df['event'] == 'gave_up']
        
            n_started = len(tasks_started)
            n_completed = len(tasks_completed)
            n_gave_up = len(tasks_gave_up)
            success_rate = f"{(n_completed / n_started * 100):.0f}%" if n_started > 0 else "N/A"
            
            # Calculate medians
            median_time = "N/A"
            median_steps = "N/A"
            if not tasks_completed.empty:
                valid_times = tasks_completed['elapsed_s'].dropna()
                if not valid_times.empty:
                    median_time = f"{valid_times.median():.1f}s"
                valid_steps = tasks_completed['step'].dropna()
                if not valid_steps.empty:
                    median_steps = f"{valid_steps.median():.0f}"
                    
            # KPI Metric Tiles
            st.markdown("### Evaluation Summary")
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            
            with kpi1:
                st.markdown(f"""
                    <div class="callout-card" style="text-align: center; padding: 12px 8px;">
                        <div style="font-size: 24px; font-weight: 700; color: #00685F;">{n_started}</div>
                        <div style="font-size: 12px; color: #515F74; font-weight: 600; text-transform: uppercase;">Tasks Started</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with kpi2:
                st.markdown(f"""
                    <div class="callout-card" style="text-align: center; padding: 12px 8px;">
                        <div style="font-size: 24px; font-weight: 700; color: #00685F;">{n_completed}</div>
                        <div style="font-size: 12px; color: #515F74; font-weight: 600; text-transform: uppercase;">Completed</div>
                    </div>
                """, unsafe_allow_html=True)
    
            with kpi3:
                st.markdown(f"""
                    <div class="callout-card" style="text-align: center; padding: 12px 8px; background-color: #BDECE2;">
                        <div style="font-size: 24px; font-weight: 700; color: #00201D;">{success_rate}</div>
                        <div style="font-size: 12px; color: #00201D; font-weight: 600; text-transform: uppercase;">Success Rate</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with kpi4:
                st.markdown(f"""
                    <div class="callout-card" style="text-align: center; padding: 12px 8px;">
                        <div style="font-size: 24px; font-weight: 700; color: #00685F;">{median_time}</div>
                        <div style="font-size: 12px; color: #515F74; font-weight: 600; text-transform: uppercase;">Median Time</div>
                    </div>
                """, unsafe_allow_html=True)
    
            with kpi5:
                st.markdown(f"""
                    <div class="callout-card" style="text-align: center; padding: 12px 8px;">
                        <div style="font-size: 24px; font-weight: 700; color: #00685F;">{median_steps}</div>
                        <div style="font-size: 12px; color: #515F74; font-weight: 600; text-transform: uppercase;">Median Steps</div>
                    </div>
                """, unsafe_allow_html=True)


            st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
            st.markdown("### Raw Event Logs")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download test logs as CSV",
                data=csv,
                file_name='recall_test_logs.csv',
                mime='text/csv',
                type="primary"
            )
