import json
import time
import os
import requests
import streamlit as st
from datetime import datetime

os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/events.jsonl"

def log_event(session_id, participant, task, event, detail=None, filters=None, n_photos=None, n_moments=None, step=None):
    source = "participant" if participant in [f"P{i}" for i in range(1, 10)] else "test"
    event_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "session_id": session_id,
        "participant": participant,
        "source": source,
        "task": task,
        "event": event,
        "detail": detail,
        "filters": filters,
        "n_photos": n_photos,
        "n_moments": n_moments,
        "elapsed_s": None,
        "step": step
    }
    
    if 'task_start_time' in st.session_state and st.session_state['task_start_time']:
        event_data["elapsed_s"] = round(time.time() - st.session_state['task_start_time'], 1)
        
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event_data) + "\n")
        
    webhook_url = None
    if 'LOG_WEBHOOK_URL' in st.secrets:
        webhook_url = st.secrets['LOG_WEBHOOK_URL']
        
    if webhook_url and source == "participant":
        try:
            import threading
            threading.Thread(target=lambda: requests.post(webhook_url, json=event_data, timeout=5), daemon=True).start()
        except:
            pass

def start_task(participant, task):
    st.session_state['session_id'] = f"{participant}_{task}_{int(time.time())}"
    st.session_state['participant'] = participant
    st.session_state['task'] = task
    st.session_state['task_start_time'] = time.time()
    st.session_state['step_count'] = 0
    st.session_state['task_active'] = True
    
    log_event(st.session_state['session_id'], participant, task, "task_start")
    
def get_step():
    st.session_state['step_count'] = st.session_state.get('step_count', 0) + 1
    return st.session_state['step_count']
