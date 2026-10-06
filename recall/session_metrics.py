import pandas as pd

EXCLUDED_SESSIONS = {
    "P9_S1_1791286744",
    "P9_FREE_1791287043"
}

def process_sessions(df):
    """
    Groups raw event logs into unique valid sessions.
    Returns a list of dicts, one per session.
    """
    sessions = {}
    if df.empty:
        return []

    # Handle missing columns safely
    for col in ['session_id', 'task', 'event', 'elapsed_s', 'step', 'detail']:
        if col not in df.columns:
            df[col] = None

    for _, row in df.iterrows():
        sid = row.get('session_id')
        if pd.isna(sid) or not sid:
            continue
            
        if sid not in sessions:
            sessions[sid] = {
                'session_id': sid,
                'participant': row.get('participant'),
                'source': row.get('source'),
                'task': str(row.get('task')) if pd.notna(row.get('task')) else 'Unknown',
                'events': [],
                'start_time': None,
                'confirmed_photo': None,
                'max_elapsed': None,
                'max_step': None,
                'abandoned': False,
            }
            
        sessions[sid]['events'].append(row.to_dict())

    # Calculate metrics per session
    valid_sessions = []
    for sid, sdata in sessions.items():
        if sid in EXCLUDED_SESSIONS:
            continue
            
        events = sdata['events']
        has_start = any(e['event'] == 'task_start' for e in events)
        if not has_start:
            continue
            
        # Extract confirmations deterministically (last confirmation wins, or keep track of all?)
        confirmations = [e for e in events if e['event'] == 'photo_confirmed']
        if confirmations:
            # use the last one by timestamp if we have one, otherwise just take the last in array
            last_conf = confirmations[-1]
            det = str(last_conf.get('detail', ''))
            sdata['confirmed_photo'] = det.split(" in ")[0] if " in " in det else det

        sdata['abandoned'] = any(e['event'] == 'gave_up' for e in events)
        
        # Max elapsed and step
        elapsed_vals = [e['elapsed_s'] for e in events if pd.notna(e['elapsed_s'])]
        if elapsed_vals:
            sdata['max_elapsed'] = max(elapsed_vals)
            
        step_vals = [e['step'] for e in events if pd.notna(e['step'])]
        if step_vals:
            sdata['max_step'] = max(step_vals)

        valid_sessions.append(sdata)

    return valid_sessions
