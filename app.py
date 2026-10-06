import streamlit as st
from recall.index import load_index, apply_filters, get_facet_counts
from recall.ranking import rank_moments, get_narrowing_question
from recall.ui import load_css, render_moment_card, get_image_base64
from recall.logging_utils import start_task, log_event, get_step
from recall.ai import parse_era, detail_rerank, parse_description

st.set_page_config(page_title="Recall: Find a photo", layout="wide")
load_css()

index = load_index()

# State
if 'filters' not in st.session_state:
    st.session_state['filters'] = {}
if 'viewing_event' not in st.session_state:
    st.session_state['viewing_event'] = None

# Sidebar
with st.sidebar:
    st.header("Test session")
    participant = st.selectbox("Participant code", ["Guest", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"])
    task = st.selectbox("Task", ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6", "Free search"])
    if st.button("Start task"):
        start_task(participant, task)
        st.session_state['filters'] = {}
        st.session_state['viewing_event'] = None
        st.success(f"Started {task}")
        
    if st.session_state.get('task_active'):
        if st.button("Give up"):
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "gave_up", step=get_step())
            st.session_state['task_active'] = False
            st.warning("Task ended")
            
    st.divider()
    st.write(f"Library stats: {len(index['photos'])} photos, {len(index['events'])} moments")
    
# Main View: Moment Detail
if st.session_state['viewing_event']:
    ev_id = st.session_state['viewing_event']
    event = next((e for e in index['events'] if e['id'] == ev_id), None)
    
    if st.button("← Back to results"):
        st.session_state['viewing_event'] = None
        st.rerun()
        
    if event:
        log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "moment_open", detail=ev_id, step=get_step())
        
        st.subheader(event.get('event_label', 'Moment'))
        st.write(f"{event['start'][:10]} · {event.get('place')} · {', '.join(event.get('people', []))}")
        
        cols = st.columns(3)
        for i, pid in enumerate(event['photo_ids']):
            with cols[i % 3]:
                st.image(f"library/photos/{pid}", use_container_width=True)
                if st.button("✅ This is the photo", key=f"confirm_{pid}"):
                    if st.session_state.get('task_active'):
                        log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "photo_confirmed", detail=pid, step=get_step())
                        st.session_state['task_active'] = False
                        st.balloons()
                        st.success(f"Found! Task logged.")
                    else:
                        st.success("You found it! (Task not active)")
    st.stop()

# State for Guided Mode
if 'app_mode' not in st.session_state:
    st.session_state['app_mode'] = 'search'
if 'search_retries' not in st.session_state:
    st.session_state['search_retries'] = 0
if 'help_step' not in st.session_state:
    st.session_state['help_step'] = 1

st.title("Find a photo you half-remember")
st.markdown("##### Demo library: AI-generated and stock images · not your Google Photos")

if st.session_state['app_mode'] == 'search':
    col_s1, col_s2 = st.columns([4, 1])
    with col_s1:
        query = st.text_input("Search your photos", placeholder="e.g. Goa 2021", key="search_bar")
    with col_s2:
        st.write("") 
        st.write("")
        if st.button("Help me remember"):
            st.session_state['app_mode'] = 'help'
            st.session_state['help_step'] = 1
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "entered_help_mode", step=get_step())
            st.rerun()

    if query:
        st.session_state['search_retries'] += 1
        q_lower = query.lower()
        matched = []
        for pid, p in index['photos'].items():
            text_to_search = f"{p.get('place','')} {p.get('city','')} {' '.join(p.get('people',[]))} {p.get('text_in_image','')}".lower()
            if q_lower in text_to_search:
                matched.append(pid)
                
        n = len(matched)
        if n == 0 or n > 40 or st.session_state['search_retries'] >= 2:
            st.warning(f"Found {n} photos. Can't find it? Let's narrow it down with what you remember.")
            if st.button("Try 'Help me remember'"):
                st.session_state['app_mode'] = 'help'
                st.session_state['help_step'] = 1
                log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "entered_help_mode", step=get_step())
                st.rerun()
        else:
            st.success(f"Found {n} photos.")
            cols = st.columns(min(n, 4))
            for i, pid in enumerate(matched[:4]):
                cols[i].image(f"library/photos/{pid}", use_container_width=True)

elif st.session_state['app_mode'] == 'help':
    if st.button("← Back to Search"):
        st.session_state['app_mode'] = 'search'
        st.rerun()
        
    st.subheader("Help me remember")
    
    # M4: Optional Describe it box
    with st.expander("Or describe what you remember, like you'd tell a friend...", expanded=False):
        desc = st.text_input("Description", placeholder="e.g. Sometime in my Scotland era, I was wearing a mask...")
        if st.button("Auto-fill filters"):
            with st.spinner("Thinking..."):
                chips = parse_description(desc, index)
                # Apply chips
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

    # Active Filters
    active_filters = {k: v for k, v in st.session_state['filters'].items() if v}
    if active_filters:
        st.write("**Your memory so far:**")
        chips = []
        for k, v in active_filters.items():
            if k == "date_range":
                chips.append(f"Time: {v[0]} to {v[1]}")
            elif k == "anything_else":
                chips.append(f"Detail: {v}")
            elif k == "era_chip":
                chips.append(f"{v} ✎")
            else:
                chips.append(f"{k.capitalize()}: {', '.join(v) if isinstance(v, list) else v}")
        st.info(" · ".join(chips))
        
        if st.button("Clear all"):
            st.session_state['filters'] = {}
            st.session_state['help_step'] = 1
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "filter_change", detail="Clear all", step=get_step())
            st.rerun()
            
    st.write("---")
    
    # Compute facets
    facets = get_facet_counts(index, st.session_state['filters'])
    matched_events, matched_photos = apply_filters(index, active_filters)
    n_photos = len(matched_photos)
    n_moments = len(matched_events)
    
    st.write(f"**{n_photos} photos · {n_moments} moments match**")
    
    step = st.session_state['help_step']
    
    def advance_step(facet, val, step_idx):
        if val and val != "Skip" and val != "Not sure / Any":
            if facet not in st.session_state['filters']:
                st.session_state['filters'][facet] = []
            if isinstance(val, list):
                for v in val:
                    if v != "Not sure / Any" and v not in st.session_state['filters'][facet]:
                        st.session_state['filters'][facet].append(v)
            else:
                if val not in st.session_state['filters'][facet]:
                    st.session_state['filters'][facet].append(val)
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), f"help_q{step_idx}_answered", detail=f"{facet}={val}", step=get_step())
        else:
            log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), f"help_q{step_idx}_skipped", detail=str(val), step=get_step())
            
        st.session_state['help_step'] += 1
        st.rerun()

    if n_moments <= 5 and n_moments > 0 and step > 1:
        st.success("We've narrowed it down! Are any of these it?")
        st.session_state['help_step'] = 5
        step = 5

    if step == 1:
        st.markdown("#### Q1: Roughly when?")
        
        era_text = st.text_input("Describe the time in your own words (e.g. 'before COVID', 'when I was in Scotland')", key="era_box")
        if st.button("Interpret time"):
            with st.spinner("Parsing..."):
                res = parse_era(era_text, index['chapters'])
                if res.get('start') and res.get('end'):
                    st.session_state['filters']['date_range'] = (res['start'], res['end'])
                    st.session_state['filters']['era_chip'] = f"Interpreted as {res['start']} to {res['end']} ({res.get('matched_chapter', 'Custom')})"
                    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "era_parsed", detail=era_text, step=get_step())
                    advance_step('era', 'parsed', 1)
                else:
                    st.error("Couldn't place that — pick a chapter instead.")
                    
        opts = [f"{k} ({v})" for k, v in facets['chapters'].items() if v > 0]
        opts.extend(["Not sure / Any", "Skip"])
        sel = st.multiselect("Or select a life chapter", opts, key="q1_chaps")
        if st.button("Next (Who)", key="btn_q1"):
            clean_sel = [s.rsplit(' (', 1)[0] for s in sel] if sel else "Skip"
            advance_step('chapters', clean_sel, 1)
            
    elif step == 2:
        st.markdown("#### Q2: Who was there?")
        opts = [f"{k} ({v})" for k, v in facets['who'].items() if v > 0]
        opts.extend(["Not sure / Any", "Skip"])
        sel = st.multiselect("Select people", opts, key="q2")
        col_b1, col_b2 = st.columns([1, 10])
        with col_b1:
            if st.button("← Back", key="back_2"):
                st.session_state['help_step'] = 1
                st.rerun()
        with col_b2:
            if st.button("Next (Where)", key="btn_q2"):
                clean_sel = [s.rsplit(' (', 1)[0] for s in sel] if sel else "Skip"
                advance_step('who', clean_sel, 2)
                
    elif step == 3:
        st.markdown("#### Q3: Where?")
        opts = [f"{k} ({v})" for k, v in facets['where'].items() if v > 0]
        opts.extend(["Not sure / Any", "Skip"])
        sel = st.multiselect("Select a place", opts, key="q3")
        col_b1, col_b2 = st.columns([1, 10])
        with col_b1:
            if st.button("← Back", key="back_3"):
                st.session_state['help_step'] = 2
                st.rerun()
        with col_b2:
            if st.button("Next (What)", key="btn_q3"):
                clean_sel = [s.rsplit(' (', 1)[0] for s in sel] if sel else "Skip"
                advance_step('where', clean_sel, 3)
                
    elif step == 4:
        st.markdown("#### Q4: What was happening?")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            opts1 = [f"{k} ({v})" for k, v in facets['what'].items() if v > 0]
            opts1.extend(["Not sure / Any", "Skip"])
            sel_what = st.multiselect("Event type", opts1, key="q4_what")
        with col_w2:
            opts2 = [f"{k} ({v})" for k, v in facets['type'].items() if v > 0]
            opts2.extend(["Not sure / Any", "Skip"])
            sel_type = st.multiselect("Photo type", opts2, key="q4_type")
            
        col_b1, col_b2 = st.columns([1, 10])
        with col_b1:
            if st.button("← Back", key="back_4"):
                st.session_state['help_step'] = 3
                st.rerun()
        with col_b2:
            if st.button("Show results", key="btn_q4"):
                if sel_what:
                    clean_what = [s.rsplit(' (', 1)[0] for s in sel_what]
                    if 'what' not in st.session_state['filters']: st.session_state['filters']['what'] = []
                    st.session_state['filters']['what'].extend([v for v in clean_what if v not in ["Skip", "Not sure / Any"]])
                if sel_type:
                    clean_type = [s.rsplit(' (', 1)[0] for s in sel_type]
                    if 'type' not in st.session_state['filters']: st.session_state['filters']['type'] = []
                    st.session_state['filters']['type'].extend([v for v in clean_type if v not in ["Skip", "Not sure / Any"]])
                
                log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "help_q4_answered", step=get_step())
                st.session_state['help_step'] = 5
                st.rerun()
                
    else: # step >= 5
        st.markdown("#### Results")
        
        # M4 Anything else?
        with st.expander("Anything else you remember? (e.g. wearing a mask, red saree, uniform)"):
            any_else = st.text_input("Detail", key="anything_else_input", value=st.session_state['filters'].get('anything_else', ''))
            if st.button("Re-rank"):
                st.session_state['filters']['anything_else'] = any_else
                log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "detail_rerank", detail=any_else, step=get_step())
                st.rerun()

        if st.button("← Edit answers", key="back_5"):
            st.session_state['help_step'] = 4
            st.rerun()
            
        ranked_events = rank_moments(matched_events, max_results=None)
        
        # Apply detail reranking if provided
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
        
        for ev in ranked_events[:5]:
            render_moment_card(ev, list(matched_events).index(ev) if ev in matched_events else 0)

        if len(ranked_events) > 5:
            st.write("---")
            st.write("None of these? → **Show 5 more** · or answer one quick question")
            q = get_narrowing_question(ranked_events, st.session_state['filters'])
            if q:
                st.info(q['text'])
                cols = st.columns(len(q['options']))
                for i, opt in enumerate(q['options']):
                    if cols[i].button(opt['label'], key=f"q_{opt['label']}"):
                        facet = q['facet']
                        if facet not in st.session_state['filters']:
                            st.session_state['filters'][facet] = []
                        st.session_state['filters'][facet].append(opt['value'])
                        log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "question_answered", detail=f"{facet}={opt['value']}", step=get_step())
                        st.rerun()
