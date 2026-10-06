import pytest
import os
import json
import time
from recall.index import load_index, apply_filters, get_facet_counts
from recall.ranking import rank_moments, get_narrowing_question
from recall.ai import parse_era, detail_rerank, parse_description
from recall.logging_utils import log_event, start_task, get_step
import streamlit as st

def test_scenario_s1_scotland_facemask():
    """Test full scenario S1: Scotland, face mask from initial state to results and photo confirmation."""
    index = load_index()
    
    # 1. Start task
    log_file = "logs/events.jsonl"
    initial_log_count = 0
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            initial_log_count = len(f.readlines())
            
    # Session state for testing
    st.session_state['session_id'] = "P-Ananya_Scotland_Test"
    st.session_state['participant'] = "P-Ananya"
    st.session_state['task'] = "Find Scotland face mask photo"
    st.session_state['task_start_time'] = time.time()
    st.session_state['step_count'] = 0
    st.session_state['task_active'] = True
    
    log_event(st.session_state['session_id'], st.session_state['participant'], st.session_state['task'], "task_start")
    
    # 2. Step 1 (When): Filter by chapter "Masters in Scotland"
    filters = {"chapters": ["Masters in Scotland"]}
    matched_events, matched_photos = apply_filters(index, filters)
    assert len(matched_events) > 0, "Should match Scotland events"
    assert len(matched_photos) > 0, "Should match Scotland photos"
    
    log_event(st.session_state['session_id'], st.session_state['participant'], st.session_state['task'], "help_q1_answered", detail="chapters=['Masters in Scotland']", step=get_step())
    
    # 3. Step 2 (Who): Skip / Not sure
    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "help_q2_skipped", detail="Skip", step=get_step())
    
    # 4. Step 3 (Where): Filter where="Edinburgh" or skip
    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "help_q3_answered", detail="where=['Edinburgh']", step=get_step())
    
    # 5. Step 4 (What / Detail): "face mask" detail reranking
    detail = "wearing a face mask"
    ranked_events = rank_moments(matched_events, max_results=None)
    
    candidate_photos = []
    for ev in ranked_events:
        for pid in ev.get("matched_photo_ids", ev["photo_ids"]):
            candidate_photos.append(index["photos"][pid])
            
    top_pids = detail_rerank(candidate_photos, detail)
    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "detail_rerank", detail=detail, step=get_step())
    
    if top_pids:
        def get_best_rank(ev):
            pids = ev.get("matched_photo_ids", ev["photo_ids"])
            ranks = [top_pids.index(pid) for pid in pids if pid in top_pids]
            return min(ranks) if ranks else float('inf')
        ranked_events.sort(key=get_best_rank)
        
    top_event = ranked_events[0]
    
    # 6. Moment View: Open moment
    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "moment_open", detail=top_event['id'], step=get_step())
    
    # 7. Photo confirmation
    target_pid = top_event['photo_ids'][0]
    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "photo_confirmed", detail=target_pid, step=get_step())
    
    # Verify logs
    with open(log_file, "r") as f:
        lines = f.readlines()
        assert len(lines) >= initial_log_count + 5, "All events should be appended to log file"
        last_event = json.loads(lines[-1])
        assert last_event["event"] == "photo_confirmed"
        assert last_event["participant"] == "P-Ananya"

def test_not_sure_path():
    """Test that clicking 'Not sure' or 'Skip' on all facets still returns candidate moments."""
    index = load_index()
    empty_filters = {}
    matched_events, matched_photos = apply_filters(index, empty_filters)
    assert len(matched_events) == len(index['events'])
    assert len(matched_photos) == len(index['photos'])
    
    ranked = rank_moments(matched_events, max_results=None)
    assert len(ranked) >= 5, "Should return moments even with no filters"
    
    # Test narrowing question for large results
    q = get_narrowing_question(ranked, empty_filters)
    assert q is not None, "Narrowing question should be generated when >5 moments match"
    assert "options" in q
    assert len(q["options"]) >= 2

def test_search_flooded_threshold():
    """Test search logic for broad query vs specific query."""
    index = load_index()
    
    # Broad query
    query = "pune"
    matched = []
    for pid, p in index['photos'].items():
        text_to_search = f"{p.get('place','')} {p.get('city','')} {' '.join(p.get('people',[]))} {p.get('text_in_image','')} {p.get('description','')} {p.get('activity','')} {p.get('scene','')}".lower()
        if query in text_to_search:
            matched.append(pid)
    assert len(matched) > 0
