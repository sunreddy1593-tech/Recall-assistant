import streamlit as st
import base64
import os
from datetime import datetime

def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #0F172A;
            background-color: #FAFAFA;
        }
        
        h1, h2, h3 {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        
        .moment-card {
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .moment-title {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 4px;
        }
        
        .moment-meta {
            font-size: 0.9rem;
            color: #64748B;
            margin-bottom: 12px;
        }
        
        .thumbnail-grid {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
            overflow-x: auto;
        }
        
        .thumbnail-img {
            border-radius: 8px;
            height: 100px;
            object-fit: cover;
        }
        
        .btn-primary {
            background-color: #0D9488;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

def get_image_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_moment_card(event, index):
    st.markdown(f'<div class="moment-card">', unsafe_allow_html=True)
    
    start_dt = datetime.fromisoformat(event["start"])
    date_str = start_dt.strftime("%d %b %Y")
    
    st.markdown(f'<div class="moment-title">{event.get("event_label", "Moment")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="moment-meta">{date_str} &middot; {event.get("place", "")} &middot; {len(event.get("matched_photo_ids", event["photo_ids"]))} photos</div>', unsafe_allow_html=True)
    
    # Render thumbnails
    html_thumbs = '<div class="thumbnail-grid">'
    photo_ids = event.get("matched_photo_ids", event["photo_ids"])
    for pid in photo_ids[:4]:
        path = f"library/photos/{pid}"
        b64 = get_image_base64(path)
        if b64:
            html_thumbs += f'<img src="data:image/jpeg;base64,{b64}" class="thumbnail-img" />'
    html_thumbs += '</div>'
    st.markdown(html_thumbs, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button(f"Is it in here? Open", key=f"open_{event['id']}"):
        st.session_state['viewing_event'] = event['id']
        st.rerun()
