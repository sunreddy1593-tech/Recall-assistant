import streamlit as st
import base64
import os
from datetime import datetime

TOKENS = {
    "colors": {
        "background": "#FAF8FF",
        "surface": "#FAF8FF",
        "surface_container_lowest": "#FFFFFF",
        "surface_container_low": "#F2F3FF",
        "surface_container": "#EAEDFF",
        "surface_container_high": "#E2E7FF",
        "surface_container_highest": "#DAE2FD",
        "on_surface": "#131B2E",
        "on_surface_variant": "#515F74",
        "secondary": "#515F74",
        "outline": "#6D7A77",
        "outline_variant": "#BCC9C6",
        "border": "#E2E8F0",
        "primary": "#00685F",
        "primary_container": "#008378",
        "on_primary": "#FFFFFF",
        "primary_fixed": "#89F5E7",
        "primary_fixed_dim": "#6BD8CB",
        "on_primary_fixed": "#00201D",
        "secondary_container": "#D5E3FC",
        "on_secondary_container": "#57657A",
        "tertiary": "#38645C",
        "tertiary_container": "#517D75",
        "tertiary_fixed": "#BDECE2",
        "error": "#BA1A1A",
        "error_container": "#FFDAD6",
    },
    "fonts": {
        "headline": "'Plus Jakarta Sans', sans-serif",
        "body": "'Inter', sans-serif",
    },
    "radius": {
        "sm": "4px",
        "md": "8px",
        "lg": "12px",
        "xl": "16px",
        "full": "9999px",
    }
}

def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        /* Global Canvas & Typography */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FAF8FF !important;
            color: #131B2E !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            font-size: 15px !important;
            line-height: 1.5 !important;
        }

        [data-testid="stSidebar"] {
            background-color: #F2F3FF !important;
            border-right: 1px solid #E2E8F0 !important;
        }

        h1, h2, h3, h4, h5, h6, .headline-text {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            color: #131B2E !important;
            letter-spacing: -0.015em !important;
        }

        h1 { font-size: 1.75rem !important; font-weight: 700 !important; line-height: 1.25 !important; }
        h2 { font-size: 1.35rem !important; line-height: 1.3 !important; }
        h3 { font-size: 1.15rem !important; line-height: 1.35 !important; }
        h4 { font-size: 1.0rem !important; }

        /* Top Banner */
        .top-disclaimer-banner {
            background-color: #F2F3FF;
            border-bottom: 1px solid #E2E8F0;
            padding: 6px 16px;
            font-size: 13px;
            font-weight: 500;
            color: #515F74;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            border-radius: 8px;
            margin-bottom: 12px;
        }

        .recall-brand-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 4px 0 16px 0;
            margin-bottom: 8px;
            border-bottom: 1px solid #EAEDFF;
        }

        .recall-logo-wrap {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .recall-logo-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: linear-gradient(135deg, #00685F, #008378);
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 700;
        }

        .recall-logo-text {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 20px;
            font-weight: 700;
            color: #131B2E;
            letter-spacing: -0.02em;
        }

        .memory-stream-pill {
            background-color: #EAEDFF;
            color: #3D4947;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 9999px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        /* Native Streamlit Buttons */
        .stButton > button {
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            padding: 8px 16px !important;
            min-height: 40px !important;
            transition: all 0.15s ease-in-out !important;
            border: 1px solid #E2E8F0 !important;
            background-color: #FFFFFF !important;
            color: #131B2E !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        }

        .stButton > button:hover {
            background-color: #F2F3FF !important;
            border-color: #CBD5E1 !important;
            color: #00685F !important;
        }

        .stButton > button:active {
            transform: scale(0.98) !important;
        }

        .stButton > button[kind="primary"] {
            background-color: #00685F !important;
            border-color: #00685F !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 4px rgba(0, 104, 95, 0.2) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #008378 !important;
            border-color: #008378 !important;
            color: #FFFFFF !important;
        }

        /* Streamlit Pills & Segmented Controls */
        [data-testid="stPills"] button, [data-testid="stSegmentedControl"] button {
            border-radius: 9999px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            border: 1px solid #E2E8F0 !important;
            background-color: #FFFFFF !important;
            color: #515F74 !important;
            padding: 6px 14px !important;
            min-height: 36px !important;
        }

        [data-testid="stPills"] button[aria-selected="true"], [data-testid="stSegmentedControl"] button[aria-selected="true"] {
            background-color: #BDECE2 !important;
            border-color: #00685F !important;
            color: #00201C !important;
            font-weight: 600 !important;
        }

        /* Input Fields */
        .stTextInput input, .stTextArea textarea {
            border-radius: 10px !important;
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            color: #131B2E !important;
            font-size: 15px !important;
            padding: 10px 14px !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #00685F !important;
            box-shadow: 0 0 0 2px rgba(0, 104, 95, 0.15) !important;
        }

        /* Expander */
        [data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
            overflow: hidden !important;
        }

        /* Custom Cards */
        .moment-card-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            transition: all 0.2s ease;
        }

        .moment-card-box:hover {
            border-color: #CBD5E1;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
        }

        .moment-header-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 6px;
        }

        .moment-card-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 17px;
            font-weight: 600;
            color: #131B2E;
            line-height: 1.3;
        }

        .moment-meta-line {
            font-size: 13px;
            color: #515F74;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }

        .attendee-badges {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin-right: 6px;
        }

        .avatar-circle {
            width: 22px;
            height: 22px;
            border-radius: 9999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
            color: #FFFFFF;
            background-color: #00685F;
        }

        .avatar-circle.c1 { background-color: #515F74; }
        .avatar-circle.c2 { background-color: #38645C; }
        .avatar-circle.c3 { background-color: #008378; }

        .callout-card {
            background-color: #F2F3FF;
            border: 1px solid #EAEDFF;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 16px;
        }

        .callout-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            font-size: 15px;
            color: #131B2E;
            margin-bottom: 4px;
        }

        .stepper-container {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 10px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        }

        .stepper-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            font-weight: 600;
            color: #515F74;
        }

        .stepper-item.active {
            color: #00685F;
        }

        .stepper-item.completed {
            color: #00685F;
        }

        .stepper-circle {
            width: 24px;
            height: 24px;
            border-radius: 9999px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
            background-color: #EAEDFF;
            color: #515F74;
        }

        .stepper-item.active .stepper-circle {
            background-color: #00685F;
            color: #FFFFFF;
            box-shadow: 0 2px 4px rgba(0, 104, 95, 0.25);
        }

        .stepper-item.completed .stepper-circle {
            background-color: #89F5E7;
            color: #00201D;
        }

        .stepper-line {
            flex: 1;
            height: 2px;
            background-color: #EAEDFF;
            margin: 0 8px;
        }

        .stepper-line.completed {
            background-color: #00685F;
        }

        .cue-chip-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 9999px;
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            color: #131B2E;
            font-size: 13px;
            font-weight: 500;
            margin: 3px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        }

        .cue-chip-tag.active {
            background-color: #BDECE2;
            border-color: #00685F;
            color: #00201C;
            font-weight: 600;
        }

        .metric-highlight-box {
            background: linear-gradient(135deg, #BDECE2 0%, #EAEDFF 100%);
            border-radius: 12px;
            padding: 14px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 12px 0;
            color: #00201D;
        }

        .metadata-strip {
            background-color: #F2F3FF;
            border-radius: 8px;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
            color: #515F74;
            font-weight: 500;
            margin: 8px 0;
        }

        .retrieval-step-row {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 10px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .test-widget-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 14px;
            margin-bottom: 16px;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
        }

        /* Image styling */
        [data-testid="stImage"] img {
            border-radius: 10px !important;
            object-fit: cover !important;
        }
        </style>
    """, unsafe_allow_html=True)

def get_image_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_top_banner():
    st.markdown("""
        <div class="top-disclaimer-banner">
            <span>ℹ️</span>
            <span>Demo library · AI-generated and stock images · not your real photos</span>
        </div>
    """, unsafe_allow_html=True)

def render_brand_header(show_stream_pill=True):
    pill_html = '<div class="memory-stream-pill"><span>◀</span><span>Memory Stream</span></div>' if show_stream_pill else ''
    st.markdown(f"""
        <div class="recall-brand-header">
            <div class="recall-logo-wrap">
                <div class="recall-logo-icon">✦</div>
                <span class="recall-logo-text">Recall</span>
            </div>
            {pill_html}
        </div>
    """, unsafe_allow_html=True)

def render_step_tracker(current_step=1, n_photos=None, n_moments=None):
    steps = [
        (1, "When"),
        (2, "Who"),
        (3, "Where"),
        (4, "What")
    ]
    
    items_html = []
    for idx, (step_num, label) in enumerate(steps):
        if step_num < current_step:
            cls = "completed"
            circle_content = "✓"
        elif step_num == current_step:
            cls = "active"
            circle_content = str(step_num)
        else:
            cls = ""
            circle_content = str(step_num)
            
        item_html = f'<div class="stepper-item {cls}"><div class="stepper-circle">{circle_content}</div><span>{label}</span></div>'
        items_html.append(item_html)
        
        if idx < len(steps) - 1:
            line_cls = "completed" if step_num < current_step else ""
            items_html.append(f'<div class="stepper-line {line_cls}"></div>')
            
    tracker_html = "".join(items_html)
    
    count_badge = ""
    if n_photos is not None and n_moments is not None:
        count_badge = f'<div style="text-align: right; margin-bottom: 8px;"><span class="memory-stream-pill" style="background:#89F5E7; color:#00201D;">🔍 {n_photos} photos · {n_moments} moments</span></div>'
        
    st.markdown(f"""
        {count_badge}
        <div class="stepper-container">
            {tracker_html}
        </div>
    """, unsafe_allow_html=True)

def render_moment_card(event, index):
    start_dt = datetime.fromisoformat(event["start"])
    date_str = start_dt.strftime("%d %b %Y")
    
    people = event.get("people", [])
    people_str = ", ".join(people) if people else "Just me"
    place = event.get("place", "")
    event_label = event.get("event_label", "Moment")
    photo_ids = event.get("matched_photo_ids", event["photo_ids"])
    n_photos = len(photo_ids)
    
    import html
    # Generate avatar circles for attendees
    avatars_html = ""
    if people:
        avatars_html = '<div class="attendee-badges">'
        classes = ["c1", "c2", "c3"]
        for i, person in enumerate(people[:3]):
            initial = html.escape(person[0].upper())
            person_safe = html.escape(person)
            c = classes[i % len(classes)]
            avatars_html += f'<div class="avatar-circle {c}" title="{person_safe}">{initial}</div>'
        avatars_html += '</div>'
    
    event_label_safe = html.escape(event_label)
    place_safe = html.escape(place)
    people_str_safe = html.escape(people_str)
    
    html_content = (
        f'<div class="moment-card-box">'
        f'<div class="moment-header-row">'
        f'<div>'
        f'<div class="moment-card-title">{event_label_safe}</div>'
        f'<div class="moment-meta-line">{date_str} &middot; <b>{place_safe}</b></div>'
        f'</div>'
        f'<span style="color:#515F74; font-size:18px;">🔖</span>'
        f'</div>'
        f'<div class="moment-meta-line" style="margin-bottom: 12px;">'
        f'{avatars_html}<span>{people_str_safe}</span>'
        f'</div>'
        f'</div>'
    )
    with st.container():
        st.markdown(html_content, unsafe_allow_html=True)
        
        # 4 thumbnails in 4 columns
        cols = st.columns(4)
        for i, pid in enumerate(photo_ids[:4]):
            with cols[i]:
                path = f"library/photos/{pid}"
                if os.path.exists(path):
                    st.image(path, use_container_width=True)
                    
        col_meta, col_btn = st.columns([2, 1])
        with col_meta:
            st.markdown(f"<span style='color:#515F74; font-size:13px; font-weight:500;'>📷 {n_photos} photos</span>", unsafe_allow_html=True)
        with col_btn:
            if st.button("Open moment →", key=f"open_{event['id']}_{index}", type="primary"):
                if 'session_id' in st.session_state:
                    from recall.logging_utils import log_event, get_step
                    log_event(st.session_state.get('session_id'), st.session_state.get('participant'), st.session_state.get('task'), "moment_open", detail=event['id'], step=get_step())
                st.session_state['viewing_event'] = event['id']
                st.rerun()
        st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)
