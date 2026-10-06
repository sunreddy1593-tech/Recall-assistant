import streamlit as st
import os
import time
from datetime import datetime
from recall.index import load_index, apply_filters, get_facet_counts
from recall.ranking import rank_moments, get_narrowing_question
from recall.ui import load_css, render_top_banner, render_brand_header, render_step_tracker, render_moment_card, get_image_base64
from recall.logging_utils import start_task, log_event, get_step
from recall.ai import parse_era, detail_rerank, parse_description

st.set_page_config(page_title="Recall · Photo Assistant", layout="wide", initial_sidebar_state="collapsed")
load_css()

index = load_index()

# Initialize session states
if 'filters' not in st.session_state:
    st.session_state['filters'] = {}
if 'viewing_event' not in st.session_state:
    st.session_state['viewing_event'] = None
if 'selected_photo_pid' not in st.session_state:
    st.session_state['selected_photo_pid'] = None
if 'photo_found_confirmed' not in st.session_state:
    st.session_state['photo_found_confirmed'] = None
if 'app_mode' not in st.session_state:
    st.session_state['app_mode'] = 'search'
if 'search_retries' not in st.session_state:
    st.session_state['search_retries'] = 0
if 'help_step' not in st.session_state:
    st.session_state['help_step'] = 1
if 'step_history' not in st.session_state:
    st.session_state['step_history'] = []

# Sidebar: Test Session
with st.sidebar:
    st.markdown("""
        <div class="test-widget-card">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 16px;">🧪</span>
                    <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 14px; font-weight: 700; color: #131B2E;">Test Session</span>
                </div>
            </div>
    """, unsafe_allow_html=True)
    
    participant = st.selectbox("Participant code", ["P-Ananya · Study A", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "Guest"], key="sb_participant")
    task_options = [
        "Find the photo of college chai break outside campus",
        "Find Scotland face mask photo",
        "Find Dublin pub celebration",
        "Find Bangalore airport arrival",
        "Find Pune birthday rooftop photo",
        "Free search"
    ]
    task = st.selectbox("Task", task_options, key="sb_task")
    
    col_st1, col_st2 = st.columns([1.5, 1])
    with col_st1:
        if st.button("▶ Start task", type="primary", use_container_width=True):
            p_code = participant.split(" · ")[0]
            start_task(p_code, task)
            st.session_state['filters'] = {}
            st.session_state['viewing_event'] = None
            st.session_state['selected_photo_pid'] = None
            st.session_state['photo_found_confirmed'] = None
            st.session_state['step_history'] = []
            st.session_state['app_mode'] = 'search'
            st.session_state['help_step'] = 1
            st.success("Task started!")
            st.rerun()
            
    with col_st2:
        if st.session_state.get('task_active'):
            if st.button("Give up", use_container_width=True):
                log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "gave_up", step=get_step())
                st.session_state['task_active'] = False
                st.warning("Task ended.")
                st.rerun()
                
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.get('task_active'):
        st.markdown(f"""
            <div style="background-color: #EAEDFF; border-radius: 10px; padding: 10px; margin-bottom: 12px; font-size: 12px; color: #131B2E;">
                <div style="font-weight: 600; color: #00685F; margin-bottom: 2px;">⚡ Active Test Session</div>
                <div style="color: #515F74;"><b>{st.session_state.get('participant')}</b></div>
                <div style="margin-top: 4px; font-style: italic;">"{st.session_state.get('task')}"</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="font-size: 12px; color: #515F74; padding: 8px 0;">
            <b>Library stats:</b> {len(index['photos'])} photos · {len(index['events'])} moments
        </div>
    """, unsafe_allow_html=True)

# Top Disclaimer Banner
render_top_banner()

# ==========================================
# SCREEN 07 / 09 / 10: MOMENT VIEW & FOUND IT
# ==========================================
if st.session_state['viewing_event']:
    ev_id = st.session_state['viewing_event']
    event = next((e for e in index['events'] if e['id'] == ev_id), None)
    
    if not event:
        st.session_state['viewing_event'] = None
        st.rerun()

    # Success State View (Screen 10: Found It)
    if st.session_state.get('photo_found_confirmed'):
        confirmed_pid = st.session_state['photo_found_confirmed']
        confirmed_photo = index['photos'].get(confirmed_pid, {})
        elapsed = "0:38s"
        if st.session_state.get('task_start_time'):
            sec = int(time.time() - st.session_state['task_start_time'])
            mins = sec // 60
            secs = sec % 60
            elapsed = f"{mins}:{secs:02d}s"
            
        step_count = st.session_state.get('step_count', 5)
        
        render_brand_header(show_stream_pill=False)
        
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:13px;">✓ Memory Identified</span>
                <span style="font-size: 13px; color: #515F74; font-weight: 500;">✨ Verified memory match</span>
            </div>
        """, unsafe_allow_html=True)
        
        col_img, col_info = st.columns([1, 1])
        with col_img:
            st.image(f"library/photos/{confirmed_pid}", use_container_width=True)
            camera = confirmed_photo.get('camera')
            filesize = confirmed_photo.get('filesize')
            metadata_html = ""
            if camera or filesize:
                cam_span = f"<span>📷 {camera}</span>" if camera else ""
                size_span = f"<span>{filesize}</span>" if filesize else ""
                metadata_html = f'<div class="metadata-strip">{cam_span}{size_span}</div>'
                
            st.markdown(metadata_html, unsafe_allow_html=True)
            
        with col_info:
            start_dt = datetime.fromisoformat(event["start"])
            date_str = start_dt.strftime("%d %b %Y")
            st.markdown(f"""
                <h2 style="margin-bottom: 4px;">{event.get('event_label', 'Moment')} · {date_str}</h2>
                <div style="font-size: 14px; color: #515F74; margin-bottom: 14px;">
                    📍 {event.get('place', '')} &middot; with {', '.join(event.get('people', []))}
                </div>
                
                <div class="metric-highlight-box">
                    <div>
                        <div style="font-size: 24px; font-weight: 700; color: #00685F;">{elapsed}</div>
                        <div style="font-size: 12px; color: #00201D;">surfaced in {step_count} cues</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Retrieval Path
            st.markdown(f"""
                <div class="callout-card" style="margin-top: 14px;">
                    <div class="callout-header">
                        <span>🌳</span>
                        <span>Retrieval Path</span>
                    </div>
                    <div class="retrieval-step-row">
                        <span><b>1. When:</b> {st.session_state['filters'].get('chapters', ['Life chapter'])[0] if st.session_state['filters'].get('chapters') else 'Selected timeframe'}</span>
                        <span style="font-size:12px; color:#515F74;">Narrowed</span>
                    </div>
                    <div class="retrieval-step-row">
                        <span><b>2. Who:</b> {', '.join(st.session_state['filters'].get('who', ['Companion'])) if st.session_state['filters'].get('who') else 'Companions'}</span>
                        <span style="font-size:12px; color:#515F74;">Filtered</span>
                    </div>
                    <div class="retrieval-step-row">
                        <span><b>3. Where:</b> {st.session_state['filters'].get('where', ['Place'])[0] if st.session_state['filters'].get('where') else 'Location'}</span>
                        <span style="font-size:12px; color:#515F74;">Isolated</span>
                    </div>
                    <div class="retrieval-step-row" style="background-color: #BDECE2; border-color: #00685F;">
                        <span><b>✓ Target Confirmed:</b> {confirmed_pid}</span>
                        <span style="font-weight: 600; color: #00685F;">{elapsed}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Try another recall task →", type="primary", use_container_width=True):
                st.session_state['filters'] = {}
                st.session_state['viewing_event'] = None
                st.session_state['selected_photo_pid'] = None
                st.session_state['photo_found_confirmed'] = None
                st.session_state['app_mode'] = 'search'
                st.session_state['help_step'] = 1
                st.rerun()
        st.stop()

    # Screen 09: Moment View
    render_brand_header(show_stream_pill=False)
    
    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← Back", key="btn_back_to_results"):
            st.session_state['viewing_event'] = None
            st.session_state['selected_photo_pid'] = None
            st.rerun()
            
    with col_title:
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span class="memory-stream-pill" style="background:#EAEDFF; color:#515F74;">Candidate moment · {len(event['photo_ids'])} photos</span>
            </div>
        """, unsafe_allow_html=True)

    start_dt = datetime.fromisoformat(event["start"])
    date_str = start_dt.strftime("%d %b %Y")
    st.markdown(f"""
        <h2 style="margin-top: 4px; margin-bottom: 2px;">{event.get('event_label', 'Moment')} · {date_str} · {event.get('place', '')}</h2>
        <div style="font-size: 14px; color: #515F74; margin-bottom: 16px;">
            📍 {event.get('place', '')} &middot; with {', '.join(event.get('people', []))}
        </div>
    """, unsafe_allow_html=True)

    # In-focus main photo
    if not st.session_state.get('selected_photo_pid') or st.session_state['selected_photo_pid'] not in event['photo_ids']:
        st.session_state['selected_photo_pid'] = event['photo_ids'][0]
        
    focus_pid = st.session_state['selected_photo_pid']
    focus_photo = index['photos'].get(focus_pid, {})
    
    col_hero, col_cta = st.columns([1.5, 1])
    with col_hero:
        st.image(f"library/photos/{focus_pid}", use_container_width=True)
        camera = focus_photo.get('camera')
        filesize = focus_photo.get('filesize')
        metadata_html = ""
        if camera or filesize:
            cam_span = f"<span>📷 {camera}</span>" if camera else ""
            size_span = f"<span>{filesize}</span>" if filesize else ""
            metadata_html = f'<div class="metadata-strip">{cam_span}{size_span}</div>'
            
        st.markdown(metadata_html, unsafe_allow_html=True)
        
    with col_cta:
        st.markdown(f"""
            <div class="callout-card">
                <div class="callout-header">
                    <span>🎯</span>
                    <span>In focus · {focus_pid}</span>
                </div>
                <p style="font-size: 13px; color: #515F74; margin-bottom: 14px;">
                    {focus_photo.get('description', 'High visual match for candidate cues')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col_c1, col_c2 = st.columns([1.5, 1])
        with col_c1:
            if st.button("✅ This is the photo", type="primary", key=f"confirm_focus_{focus_pid}", use_container_width=True):
                if st.session_state.get('task_active'):
                    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "photo_confirmed", detail=focus_pid, step=get_step())
                    st.session_state['task_active'] = False
                st.session_state['photo_found_confirmed'] = focus_pid
                st.balloons()
                st.rerun()
                
        with col_c2:
            if st.button("Not it", key=f"reject_focus_{focus_pid}", use_container_width=True):
                st.session_state['viewing_event'] = None
                st.rerun()
                
        st.markdown("<p style='font-size: 12px; color: #515F74; text-align: center; margin-top: 6px;'>Selecting locks this photograph as the verified memory cue</p>", unsafe_allow_html=True)

    # Photos in this moment grid
    st.markdown("### Photos in this moment")
    cols_photos = st.columns(min(len(event['photo_ids']), 6))
    for i, pid in enumerate(event['photo_ids']):
        with cols_photos[i % len(cols_photos)]:
            path = f"library/photos/{pid}"
            if os.path.exists(path):
                st.image(path, use_container_width=True)
                btn_label = "In Focus" if pid == focus_pid else "Select"
                btn_type = "primary" if pid == focus_pid else "secondary"
                if st.button(btn_label, key=f"sel_p_{pid}", type=btn_type, use_container_width=True):
                    st.session_state['selected_photo_pid'] = pid
                    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "photo_view", detail=pid, step=get_step())
                    st.rerun()

    # Timeline Context: Before & After Moments
    st.markdown("---")
    st.markdown("### 📈 Timeline Context")
    st.markdown("<p style='font-size: 13px; color: #515F74; margin-top: -10px;'>What happened right around this moment</p>", unsafe_allow_html=True)
    
    # Find event index in all events sorted by start
    all_events_sorted = sorted(index['events'], key=lambda x: x['start'])
    curr_idx = next((i for i, e in enumerate(all_events_sorted) if e['id'] == ev_id), -1)
    
    timeline_events = []
    if curr_idx > 0:
        timeline_events.append(("Before", all_events_sorted[curr_idx - 1]))
    timeline_events.append(("THIS MOMENT", event))
    if curr_idx < len(all_events_sorted) - 1:
        timeline_events.append(("After", all_events_sorted[curr_idx + 1]))
        
    tl_cols = st.columns(len(timeline_events))
    for i, (rel_label, tl_ev) in enumerate(timeline_events):
        with tl_cols[i]:
            tl_dt = datetime.fromisoformat(tl_ev["start"]).strftime("%d %b %Y")
            is_current = (rel_label == "THIS MOMENT")
            bg_card = "#BDECE2" if is_current else "#FFFFFF"
            border_card = "#00685F" if is_current else "#E2E8F0"
            st.markdown(f"""
                <div style="background-color: {bg_card}; border: 1px solid {border_card}; border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                    <div style="font-size: 11px; font-weight: 700; color: #00685F; text-transform: uppercase;">{rel_label} · {tl_dt}</div>
                    <div style="font-weight: 600; font-size: 14px; margin: 4px 0;">{tl_ev.get('event_label', 'Moment')}</div>
                    <div style="font-size: 12px; color: #515F74;">{tl_ev.get('place', '')} · {len(tl_ev['photo_ids'])} photos</div>
                </div>
            """, unsafe_allow_html=True)
            if tl_ev['photo_ids']:
                st.image(f"library/photos/{tl_ev['photo_ids'][0]}", use_container_width=True)
            if not is_current:
                if st.button(f"Inspect cluster →", key=f"tl_btn_{tl_ev['id']}", use_container_width=True):
                    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "moment_open", detail=tl_ev['id'], step=get_step())
                    st.session_state['viewing_event'] = tl_ev['id']
                    st.session_state['selected_photo_pid'] = None
                    st.rerun()

    st.stop()

# ==========================================
# SCREEN 01 & 02: HOME & KEYWORD SEARCH
# ==========================================
render_brand_header(show_stream_pill=True)

if st.session_state['app_mode'] == 'search':
    # Search Bar Row
    col_s1, col_s2 = st.columns([4, 1.2])
    with col_s1:
        query = st.text_input("Search photos", placeholder="Search your photos (e.g. Goa 2021, Scotland rain, Chai tapri)...", key="photoSearchInput", label_visibility="collapsed")
    with col_s2:
        if st.button("✨ Help me remember", type="primary", key="btn_help_remember_main", use_container_width=True):
            st.session_state['app_mode'] = 'help'
            st.session_state['help_step'] = 1
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "entered_help_mode", step=get_step())
            st.rerun()

    # AI Memory Prompt / Fuzzy Recall Callout
    st.markdown("""
        <div class="callout-card" style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 36px; height: 36px; border-radius: 9999px; background-color: #BDECE2; color: #00685F; display: flex; align-items: center; justify-content: center; font-size: 18px;">✦</div>
                <div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-weight: 600; font-size: 14px; color: #131B2E;">Can't pinpoint the date?</span>
                        <span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:10px; padding: 2px 6px;">NEW</span>
                    </div>
                    <div style="font-size: 12px; color: #515F74;">Describe sensory cues, weather, or who was there</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if query:
        st.session_state['search_retries'] += 1
        q_lower = query.lower()
        matched = []
        for pid, p in index['photos'].items():
            text_to_search = f"{p.get('place','')} {p.get('city','')} {' '.join(p.get('people',[]))} {p.get('text_in_image','')} {p.get('description','')} {p.get('activity','')} {p.get('scene','')}".lower()
            if q_lower in text_to_search:
                matched.append(pid)
                
        n = len(matched)
        
        # SCREEN 02: SEARCH FLOODED
        if n == 0 or n > 40 or st.session_state['search_retries'] >= 2:
            st.markdown(f"""
                <div style="margin-top: 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h2 style="margin: 0; display: inline;">{n} photos found</h2>
                        <span class="memory-stream-pill" style="background:#FFDAD6; color:#BA1A1A; font-size:11px; margin-left: 8px;">BROAD SEARCH</span>
                        <div style="font-size: 13px; color: #515F74; margin-top: 2px;">Across multiple years · Pune, Edinburgh, Dublin, Bengaluru</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Friendly Intervention Banner Card
            with st.container():
                st.markdown("""
                    <div class="callout-card" style="border: 1.5px solid #00685F; background: linear-gradient(135deg, #F2F3FF 0%, #EAEDFF 100%);">
                        <div style="display: flex; align-items: flex-start; gap: 12px;">
                            <div style="width: 40px; height: 40px; border-radius: 9999px; background-color: #00685F; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 20px; shrink: 0;">🧠</div>
                            <div>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <h3 style="margin: 0; color: #131B2E;">Can't find it?</h3>
                                    <span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:10px;">RECALL AI</span>
                                </div>
                                <div style="font-weight: 600; font-size: 14px; color: #131B2E; margin-top: 4px;">Let's narrow it down with what you remember.</div>
                                <div style="font-size: 13px; color: #515F74; margin-top: 2px; line-height: 1.4;">
                                    Which life chapter, who you were with, or sensory details like rainy cobblestones, rooftop cakes, or chai outside campus.
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_c1, col_c2 = st.columns([1, 3])
                with col_c1:
                    if st.button("✨ Help me remember", key="btn_help_remember_flood", type="primary", use_container_width=True):
                        st.session_state['app_mode'] = 'help'
                        st.session_state['help_step'] = 1
                        log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "entered_help_mode", step=get_step())
                        st.rerun()
                with col_c2:
                    st.caption("Guided step-by-step recall: When, Who, Where, What")
            
            # Show photo sample
            if matched:
                st.markdown("#### Photo search results:")
                cols = st.columns(min(n, 6))
                for i, pid in enumerate(matched[:6]):
                    cols[i].image(f"library/photos/{pid}", use_container_width=True)
        else:
            st.markdown(f"<h3>Found {n} photos</h3>", unsafe_allow_html=True)
            cols = st.columns(min(n, 4))
            for i, pid in enumerate(matched[:4]):
                with cols[i]:
                    st.image(f"library/photos/{pid}", use_container_width=True)
                    if st.button("View photo", key=f"srch_view_{pid}", use_container_width=True):
                        # Find event for this photo
                        ev = next((e for e in index['events'] if pid in e['photo_ids']), None)
                        if ev:
                            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "moment_open", detail=ev['id'], step=get_step())
                            st.session_state['viewing_event'] = ev['id']
                            st.session_state['selected_photo_pid'] = pid
                            st.rerun()

    else:
        # Screen 01 Default Timeline Feed
        # Group library photos by Chapter / Month for rich timeline browsing
        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        
        # Sections
        sections = [
            ("February 2026", "Back in India", ["P029.jpg", "P030.jpg", "P031.jpg", "P032.jpg", "P033.jpg", "P034.jpg"]),
            ("December 2025", "Dublin, Ireland", ["P025.jpg", "P026.jpg", "P027.jpg", "P028.jpg"]),
            ("October 2024", "Dublin, Ireland", ["P021.jpg", "P022.jpg", "P023.jpg", "P024.jpg"]),
            ("May 2024", "Edinburgh, Scotland", ["P016.jpg", "P017.jpg", "P018.jpg", "P019.jpg", "P020.jpg"]),
            ("November 2020", "Pune, Maharashtra", ["P001.jpg", "P002.jpg", "P003.jpg", "P004.jpg", "P005.jpg", "P006.jpg"])
        ]
        
        for date_title, subtitle, pids in sections:
            available_pids = [p for p in pids if p in index['photos'] and os.path.exists(f"library/photos/{p}")]
            if available_pids:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 16px; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <h3 style="margin: 0; font-size: 16px;">{date_title}</h3>
                            <span style="color: #515F74; font-size: 14px;">· {subtitle}</span>
                        </div>
                        <span class="memory-stream-pill" style="font-size: 11px;">{len(available_pids)} photos</span>
                    </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(3)
                for idx, pid in enumerate(available_pids[:6]):
                    with cols[idx % 3]:
                        st.image(f"library/photos/{pid}", use_container_width=True)
                        if st.button("Open moment", key=f"home_open_{pid}_{idx}", use_container_width=True):
                            ev = next((e for e in index['events'] if pid in e['photo_ids']), None)
                            if ev:
                                log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "moment_open", detail=ev['id'], step=get_step())
                                st.session_state['viewing_event'] = ev['id']
                                st.session_state['selected_photo_pid'] = pid
                                st.rerun()

# ==========================================
# GUIDED RECALL MODE (Screens 03, 04, 05, 06, 07, 08)
# ==========================================
elif st.session_state['app_mode'] == 'help':
    col_top_back, col_top_txt = st.columns([1, 6])
    with col_top_back:
        if st.button("← Back to Search", key="btn_exit_help"):
            st.session_state['app_mode'] = 'search'
            st.rerun()
            
    with col_top_txt:
        st.markdown(f"""
            <div style="font-size: 13px; color: #515F74; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">
                Recall Guide · Step {min(st.session_state['help_step'], 4)} of 4
            </div>
        """, unsafe_allow_html=True)

    # Screen 03: Optional Describe It Conversational Sketchbook (M4)
    with st.expander("✨ Or describe what you remember in your own words (Describe it)...", expanded=(st.session_state['help_step'] == 1 and bool(st.session_state.get('show_describe_box')))):
        st.markdown("<p style='font-size: 13px; color: #515F74;'>Talk freely or type a loose recollection. Recall parses episodic cues into searchable anchors.</p>", unsafe_allow_html=True)
        desc = st.text_area("Your stream of memory", placeholder="e.g. birthday dinner with college friends before COVID, or when I was wearing a mask in Scotland...", key="desc_input_box", height=70)
        
        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            if st.button("Parse cues & auto-fill", type="primary", use_container_width=True):
                if desc:
                    with st.spinner("Parsing episodic cues..."):
                        chips = parse_description(desc, index)
                        st.session_state['filters'] = {}
                        if chips.get("chapters"): st.session_state['filters']["chapters"] = chips["chapters"]
                        if chips.get("who"): st.session_state['filters']["who"] = chips["who"]
                        if chips.get("where"): st.session_state['filters']["where"] = chips["where"]
                        if chips.get("what"): st.session_state['filters']["what"] = chips["what"]
                        if chips.get("type"): st.session_state['filters']["type"] = chips["type"]
                        if chips.get("anything_else"): st.session_state['filters']["anything_else"] = chips["anything_else"]
                        
                        log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "used_describe_it", detail=desc, step=get_step())
                        st.session_state['help_step'] = 5
                        st.rerun()

    # Active Filters Summary ("Your memory so far")
    active_filters = {k: v for k, v in st.session_state['filters'].items() if v}
    if active_filters:
        st.markdown("""
            <div style="background-color: #F2F3FF; border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-size: 11px; font-weight: 700; color: #515F74; text-transform: uppercase;">Your memory so far</span>
                    <span style="font-size: 11px; color: #00685F;">Tap chip to edit</span>
                </div>
        """, unsafe_allow_html=True)
        
        chips_html = []
        for k, v in active_filters.items():
            if k == "date_range":
                chips_html.append(f'<span class="cue-chip-tag active">📅 Time: {v[0]} to {v[1]}</span>')
            elif k == "anything_else":
                chips_html.append(f'<span class="cue-chip-tag active">✨ Detail: {v}</span>')
            elif k == "era_chip":
                chips_html.append(f'<span class="cue-chip-tag active">🗓️ {v}</span>')
            else:
                val_str = ', '.join(v) if isinstance(v, list) else str(v)
                chips_html.append(f'<span class="cue-chip-tag active">{k.capitalize()}: {val_str}</span>')
                
        st.markdown("".join(chips_html) + "</div>", unsafe_allow_html=True)
        
        if st.button("Clear all filters", key="btn_clear_all_filters"):
            st.session_state['filters'] = {}
            st.session_state['help_step'] = 1
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "filter_change", detail="Clear all", step=get_step())
            st.rerun()

    # Compute Facet Counts & Matched items
    facets = get_facet_counts(index, st.session_state['filters'])
    matched_events, matched_photos = apply_filters(index, active_filters)
    n_photos = len(matched_photos)
    n_moments = len(matched_events)
    
    step = st.session_state['help_step']
    
    # Progress Step Indicator
    if step <= 4:
        render_step_tracker(current_step=step, n_photos=n_photos, n_moments=n_moments)

    def advance_step(facet, val, step_idx):
        if val and val != "Skip" and val != "Not sure" and val != "Not sure / Any":
            if facet not in st.session_state['filters']:
                st.session_state['filters'][facet] = []
            if isinstance(val, list):
                for v in val:
                    if v not in ["Skip", "Not sure", "Not sure / Any"] and v not in st.session_state['filters'][facet]:
                        st.session_state['filters'][facet].append(v)
            else:
                if val not in st.session_state['filters'][facet]:
                    st.session_state['filters'][facet].append(val)
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), f"help_q{step_idx}_answered", detail=f"{facet}={val}", step=get_step())
        else:
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), f"help_q{step_idx}_skipped", detail=str(val), step=get_step())
            
        st.session_state['help_step'] += 1
        st.rerun()

    # Early Narrowing Alert
    if n_moments <= 5 and n_moments > 0 and step > 1 and step < 5:
        st.markdown(f"""
            <div style="background-color: #BDECE2; border: 1px solid #00685F; border-radius: 12px; padding: 12px 16px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-weight: 700; color: #00201D;">🎯 We've narrowed it down to {n_moments} moments!</span>
                    <div style="font-size: 13px; color: #00201D;">Ready to see the candidate moments?</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Show matching moments now →", type="primary", key="btn_early_results"):
            st.session_state['help_step'] = 5
            st.rerun()

    # ==========================================
    # STEP 1: WHEN (Screen 04)
    # ==========================================
    if step == 1:
        st.markdown("<h2>Roughly when was it?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px; color: #515F74;'>Pick a life chapter, narrow by years, or just describe the timeframe.</p>", unsafe_allow_html=True)
        
        # Section 1: Life chapters
        st.markdown("#### A phase of your life")
        chap_opts = [f"{k} ({v})" for k, v in facets['chapters'].items() if v > 0]
        sel_chaps = st.pills("Select life chapters", chap_opts, selection_mode="multi", key="pills_q1_chaps", label_visibility="collapsed")
        
        # Section 2: Specific Years
        st.markdown("#### Or specific years")
        year_counts = {}
        for p in matched_photos:
            photo_obj = index['photos'].get(p, {}) if isinstance(p, str) else p
            y = photo_obj.get('year') if isinstance(photo_obj, dict) else None
            if y:
                year_counts[str(y)] = year_counts.get(str(y), 0) + 1
        year_opts = [f"{y} ({c})" for y, c in sorted(year_counts.items())]
        sel_years = st.pills("Select years", year_opts, selection_mode="multi", key="pills_q1_years", label_visibility="collapsed")
        
        # Section 3: Natural language era description
        st.markdown("#### Describe the time in your own words")
        era_text = st.text_input("Era description", placeholder="e.g. before COVID, college first year, summer in Scotland...", key="era_box", label_visibility="collapsed")
        if era_text:
            if st.button("Parse era description", key="btn_parse_era"):
                with st.spinner("Interpreting time..."):
                    res = parse_era(era_text, index['chapters'])
                    if res.get('start') and res.get('end'):
                        st.session_state['filters']['date_range'] = (res['start'], res['end'])
                        st.session_state['filters']['era_chip'] = f"Interpreted as {res['start']} to {res['end']} ({res.get('matched_chapter', 'Custom')})"
                        log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "era_parsed", detail=era_text, step=get_step())
                        st.success(f"Understood: {res['start']} to {res['end']}")
                        st.session_state['help_step'] = 2
                        st.rerun()
                    else:
                        st.error("Couldn't place that — pick a chapter above instead.")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3 = st.columns([1, 1, 2])
        with col_b1:
            if st.button("Not sure", key="btn_not_sure_1", use_container_width=True):
                advance_step('chapters', 'Not sure', 1)
        with col_b2:
            if st.button("Skip", key="btn_skip_1", use_container_width=True):
                advance_step('chapters', 'Skip', 1)
        with col_b3:
            if st.button("Next: Who was there →", type="primary", key="btn_q1_next", use_container_width=True):
                clean_chaps = [s.rsplit(' (', 1)[0] for s in sel_chaps] if sel_chaps else []
                if clean_chaps:
                    st.session_state['filters']['chapters'] = clean_chaps
                if sel_years:
                    clean_years = [s.rsplit(' (', 1)[0] for s in sel_years]
                    st.session_state['filters']['years'] = clean_years
                advance_step('chapters', clean_chaps or 'Skip', 1)

    # ==========================================
    # STEP 2: WHO (Screen 05)
    # ==========================================
    elif step == 2:
        st.markdown("<h2>Who was there?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px; color: #515F74;'>Pick the people you remember being with, or describe the group dynamic.</p>", unsafe_allow_html=True)
        
        # Group dynamic
        st.markdown("#### Group dynamic")
        dyn_opts = ["Just me", "A group", "Not sure"]
        sel_dyn = st.segmented_control("Group dynamic", dyn_opts, default="A group", key="seg_group_dynamic", label_visibility="collapsed")
        
        # People pills with counts
        st.markdown("#### People")
        people_opts = [f"{k} ({v})" for k, v in facets['who'].items() if v > 0]
        sel_who = st.pills("Select people", people_opts, selection_mode="multi", key="pills_q2_who", label_visibility="collapsed")
        
        # Unnamed person sensory clue
        st.markdown("#### Or describe someone you don't have named")
        unnamed = st.text_input("Unnamed person / appearance", placeholder="e.g. chai stall uncle, professor with beard, friend with yellow jacket...", key="unnamed_person_box", label_visibility="collapsed")
        if unnamed:
            st.session_state['filters']['anything_else'] = unnamed

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3, col_b4 = st.columns([1, 1, 1, 2])
        with col_b1:
            if st.button("← Back", key="back_to_1", use_container_width=True):
                st.session_state['help_step'] = 1
                st.rerun()
        with col_b2:
            if st.button("Not sure", key="btn_not_sure_2", use_container_width=True):
                advance_step('who', 'Not sure', 2)
        with col_b3:
            if st.button("Skip", key="btn_skip_2", use_container_width=True):
                advance_step('who', 'Skip', 2)
        with col_b4:
            if st.button("Next: Where? →", type="primary", key="btn_q2_next", use_container_width=True):
                clean_who = [s.rsplit(' (', 1)[0] for s in sel_who] if sel_who else []
                if clean_who:
                    st.session_state['filters']['who'] = clean_who
                advance_step('who', clean_who or 'Skip', 2)

    # ==========================================
    # STEP 3: WHERE (Screen 06)
    # ==========================================
    elif step == 3:
        st.markdown("<h2>Where was this?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px; color: #515F74;'>Pick locations you recall visiting, or search by neighborhood or vibe.</p>", unsafe_allow_html=True)
        
        # Location vibe chips
        st.markdown("#### Setting vibe")
        vibe_opts = ["🏫 On campus", "☕ Café / restaurant", "🚗 Road trip", "🌳 Outdoors", "🏠 Indoors"]
        st.pills("Setting vibe", vibe_opts, selection_mode="multi", key="pills_vibe", label_visibility="collapsed")
        
        # Places with counts
        st.markdown("#### Places & Neighborhoods")
        where_opts = [f"{k} ({v})" for k, v in facets['where'].items() if v > 0]
        sel_where = st.pills("Select places", where_opts, selection_mode="multi", key="pills_q3_where", label_visibility="collapsed")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3, col_b4 = st.columns([1, 1, 1, 2])
        with col_b1:
            if st.button("← Back", key="back_to_2", use_container_width=True):
                st.session_state['help_step'] = 2
                st.rerun()
        with col_b2:
            if st.button("Not sure", key="btn_not_sure_3", use_container_width=True):
                advance_step('where', 'Not sure', 3)
        with col_b3:
            if st.button("Skip", key="btn_skip_3", use_container_width=True):
                advance_step('where', 'Skip', 3)
        with col_b4:
            if st.button("Next: What happened? →", type="primary", key="btn_q3_next", use_container_width=True):
                clean_where = [s.rsplit(' (', 1)[0] for s in sel_where] if sel_where else []
                if clean_where:
                    st.session_state['filters']['where'] = clean_where
                advance_step('where', clean_where or 'Skip', 3)

    # ==========================================
    # STEP 4: WHAT (Screen 07)
    # ==========================================
    elif step == 4:
        st.markdown("<h2>What was happening?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px; color: #515F74;'>Pick the event or activity Recall identified from your photo clusters.</p>", unsafe_allow_html=True)
        
        # Content type selector
        st.markdown("#### Content type")
        type_opts = [f"{k} ({v})" for k, v in facets['type'].items() if v > 0]
        sel_type = st.pills("Content type", type_opts, selection_mode="multi", key="pills_q4_type", label_visibility="collapsed")
        
        # Activity / Event options
        st.markdown("#### Event or activity")
        what_opts = [f"{k} ({v})" for k, v in facets['what'].items() if v > 0]
        sel_what = st.pills("Event type", what_opts, selection_mode="multi", key="pills_q4_what", label_visibility="collapsed")
        
        # Anything else detail input
        st.markdown("#### Anything else you remember?")
        detail_val = st.text_input("Detail clue", placeholder="e.g. wearing a mask, sparklers, red saree, graduation cap, rainy cobblestones...", key="q4_detail_box", value=st.session_state['filters'].get('anything_else', ''), label_visibility="collapsed")
        if detail_val:
            st.session_state['filters']['anything_else'] = detail_val

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3 = st.columns([1, 1, 2])
        with col_b1:
            if st.button("← Back", key="back_to_3", use_container_width=True):
                st.session_state['help_step'] = 3
                st.rerun()
        with col_b2:
            if st.button("Skip", key="btn_skip_4", use_container_width=True):
                st.session_state['help_step'] = 5
                st.rerun()
        with col_b3:
            if st.button("Show matching moments →", type="primary", key="btn_q4_show_results", use_container_width=True):
                if sel_what:
                    clean_what = [s.rsplit(' (', 1)[0] for s in sel_what]
                    st.session_state['filters']['what'] = clean_what
                if sel_type:
                    clean_type = [s.rsplit(' (', 1)[0] for s in sel_type]
                    st.session_state['filters']['type'] = clean_type
                log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "help_q4_answered", step=get_step())
                st.session_state['help_step'] = 5
                st.rerun()

    # ==========================================
    # STEP 5: RESULTS (Screen 08)
    # ==========================================
    else:
        # Rank moments
        ranked_events = rank_moments(matched_events, max_results=None)
        
        # Detail re-rank if "anything else" is supplied
        detail = st.session_state['filters'].get('anything_else')
        if detail:
            candidate_photos = []
            for ev in ranked_events:
                for pid in ev.get("matched_photo_ids", ev["photo_ids"]):
                    candidate_photos.append(index["photos"][pid])
            
            top_pids = detail_rerank(candidate_photos, detail)
            if top_pids:
                def get_best_rank(ev):
                    pids = ev.get("matched_photo_ids", ev["photo_ids"])
                    ranks = [top_pids.index(pid) for pid in pids if pid in top_pids]
                    return min(ranks) if ranks else float('inf')
                    
                ranked_events.sort(key=get_best_rank)

        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:12px;">✨ RECALL RESULTS · {len(ranked_events)} MATCHING MOMENTS</span>
            </div>
            <h2 style="margin-top: 4px; margin-bottom: 2px;">Is it one of these?</h2>
            <div style="font-size: 14px; color: #515F74; margin-bottom: 16px;">
                Narrowed down from <b>{len(index['events'])} memories</b> based on your cues.
            </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2 = st.columns([1, 3])
        with col_act1:
            if st.button("← Edit answers", key="btn_edit_answers_5", use_container_width=True):
                st.session_state['help_step'] = 4
                st.rerun()
                
        with col_act2:
            with st.expander("✨ Re-rank with extra detail (e.g. mask, red saree, uniform)..."):
                re_detail = st.text_input("Sensory or clothing detail", value=st.session_state['filters'].get('anything_else', ''), key="rerank_detail_box")
                if st.button("Apply detail re-rank", key="btn_apply_rerank"):
                    st.session_state['filters']['anything_else'] = re_detail
                    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "detail_rerank", detail=re_detail, step=get_step())
                    st.rerun()

        st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

        # Show Top 5 Moment Cards
        for idx, ev in enumerate(ranked_events[:5]):
            render_moment_card(ev, idx)

        # If > 5 moments match, show narrowing question & show more
        if len(ranked_events) > 5:
            st.markdown("""
                <div class="callout-card" style="border: 1px solid #00685F; margin-top: 16px;">
                    <div class="callout-header">
                        <span>💡</span>
                        <span>Help me remember cue</span>
                    </div>
            """, unsafe_allow_html=True)
            
            q = get_narrowing_question(ranked_events, st.session_state['filters'])
            if q:
                st.markdown(f"<div style='font-size: 15px; font-weight: 600; color: #131B2E; margin-bottom: 8px;'>{q['text']}</div>", unsafe_allow_html=True)
                st.markdown("<div style='font-size: 13px; color: #515F74; margin-bottom: 10px;'>Filter the candidate moments by location atmosphere:</div>", unsafe_allow_html=True)
                cols_q = st.columns(len(q['options']))
                for i, opt in enumerate(q['options']):
                    with cols_q[i]:
                        if st.button(opt['label'], key=f"btn_narrow_q_{i}", use_container_width=True):
                            facet = q['facet']
                            if facet not in st.session_state['filters']:
                                st.session_state['filters'][facet] = []
                            st.session_state['filters'][facet].append(opt['value'])
                            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "question_answered", detail=f"{facet}={opt['value']}", step=get_step())
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.expander(f"Show {min(5, len(ranked_events)-5)} more candidate moments..."):
                for idx, ev in enumerate(ranked_events[5:10], start=5):
                    render_moment_card(ev, idx)
