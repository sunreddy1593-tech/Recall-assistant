import pytest
import os
import time
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
import json

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")

with open(os.path.join(os.path.dirname(__file__), "..", "data", "index.json")) as f:
    index_data = json.load(f)
    valid_event = index_data['events'][0]
    valid_event_id = valid_event['id']
    valid_photo_id = valid_event['photo_ids'][0]

def test_applied_cues_rendering():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.secrets = {}
    at.run()
    
    at.session_state['photo_found_confirmed'] = valid_photo_id
    at.session_state['filters'] = {
        'chapters': ['Scotland <Masters> & fun'],
        'what': ['Sick Day']
    }
    at.session_state['viewing_event'] = valid_event_id
    at.session_state['task_start_time'] = time.time() - 42
    at.run()

    applied_cues_md = next((md.value for md in at.markdown if "Applied cues" in md.value), "")
    
    assert '<div class="callout-card"' in applied_cues_md
    assert "```html" not in applied_cues_md
    assert 'When:' in applied_cues_md
    assert 'Activity:' in applied_cues_md
    assert 'Who:' not in applied_cues_md
    assert '<b>1. When:</b>' in applied_cues_md
    assert '<b>2. Activity:</b>' in applied_cues_md
    assert 'Scotland &lt;Masters&gt; &amp; fun' in applied_cues_md

def test_elapsed_time_freezes():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.secrets = {}
    at.run()
    
    at.session_state['app_mode'] = 'search'
    at.session_state['viewing_event'] = valid_event_id
    at.session_state['selected_photo_pid'] = valid_photo_id
    at.session_state['task_active'] = True
    start_t = time.time() - 42.0
    at.session_state['task_start_time'] = start_t
    at.session_state['session_id'] = 'test_session'
    at.session_state['participant'] = 'test'
    at.session_state['task'] = 'test'
    at.session_state['rejected_photos'] = set()
    at.run()
    
    confirm_btn = next((btn for btn in at.button if "✅" in btn.label), None)
    assert confirm_btn is not None
    
    with patch('recall.logging_utils.log_event') as mock_log:
        confirm_btn.click().run()
        mock_log.assert_called_once()
        
    assert at.session_state['confirmed_elapsed_time'] == '0:42s'
    
    at.session_state['task_start_time'] = start_t - 100 
    at.run()
    
    applied_cues_md = next((md.value for md in at.markdown if "Applied cues" in md.value), "")
    assert '0:42s' in applied_cues_md

def test_elapsed_time_zero_and_invalid():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.secrets = {}
    at.run()
    
    at.session_state['viewing_event'] = valid_event_id
    at.session_state['selected_photo_pid'] = valid_photo_id
    at.session_state['task_active'] = True
    at.session_state['task_start_time'] = time.time()
    at.run()
    
    confirm_btn = next((btn for btn in at.button if "✅" in btn.label), None)
    with patch('recall.logging_utils.log_event'):
        confirm_btn.click().run()
    assert at.session_state['confirmed_elapsed_time'] == '0:00s'
    
    at.session_state['task_active'] = True
    at.session_state['task_start_time'] = "Not a timestamp"
    if 'confirmed_elapsed_time' in at.session_state:
        del at.session_state['confirmed_elapsed_time']
    at.session_state['photo_found_confirmed'] = None
    at.run()
    
    confirm_btn = next((btn for btn in at.button if "✅" in btn.label), None)
    with patch('recall.logging_utils.log_event'):
        confirm_btn.click().run()
    assert at.session_state['confirmed_elapsed_time'] == 'Time unavailable'

def test_reset_clears_duration():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.secrets = {}
    at.run()
    
    at.session_state['photo_found_confirmed'] = valid_photo_id
    at.session_state['confirmed_elapsed_time'] = '0:42s'
    at.session_state['viewing_event'] = valid_event_id
    at.run()
    
    try_another_btn = next((btn for btn in at.button if "Try another recall task" in btn.label), None)
    assert try_another_btn is not None
    try_another_btn.click().run()
    
    assert 'confirmed_elapsed_time' not in at.session_state
    
    at.session_state['photo_found_confirmed'] = valid_photo_id
    at.session_state['confirmed_elapsed_time'] = '0:42s'
    at.run()
    
    start_task_btn = next((btn for btn in at.button if "Start task" in btn.label), None)
    assert start_task_btn is not None
    start_task_btn.click().run()
    
    assert 'confirmed_elapsed_time' not in at.session_state
