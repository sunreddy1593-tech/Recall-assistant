import streamlit as st
import pandas as pd
import os
import json

st.title("Test Results")

LOG_FILE = "logs/events.jsonl"

if not os.path.exists(LOG_FILE):
    st.write("No logs yet.")
else:
    data = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
                
    df = pd.DataFrame(data)
    st.dataframe(df)
    
    # Optional CSV download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='test_logs.csv',
        mime='text/csv',
    )
    
    st.subheader("Summary")
    if not df.empty:
        tasks = df[df['event'] == 'task_start'].copy()
        completions = df[df['event'] == 'photo_confirmed'].copy()
        st.write(f"Total tasks started: {len(tasks)}")
        st.write(f"Total tasks completed: {len(completions)}")
