import streamlit as st
from recall.ui import load_css, render_top_banner, render_brand_header

st.set_page_config(page_title="Recall · How it works", layout="wide")
load_css()

render_top_banner()
render_brand_header(show_stream_pill=False)

html_content = """<div style="max-width: 800px; margin: 0 auto;">
<div style="margin-bottom: 24px;">
<span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:12px; margin-bottom: 8px;">
✦ The Recall Difference
</span>
<h1 style="margin-top: 8px; margin-bottom: 12px; font-size: 28px;">
Not a better search engine. A recall assistant for when search can't help.
</h1>
<p style="font-size: 16px; color: #515F74; line-height: 1.6;">
Standard search forces you to supply exact keywords you’ve naturally forgotten. Recall mirrors human episodic memory: anchoring to life chapters, people, sensory atmospheres, and half-remembered fragments.
</p>
<div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px;">
<span class="cue-chip-tag">🗓️ Life Chapters</span>
<span class="cue-chip-tag">✨ Sensory Fragments</span>
<span class="cue-chip-tag">👥 Co-presence</span>
</div>
</div>

<div style="margin-bottom: 32px;">
<h2 style="font-size: 20px; margin-bottom: 16px;">How Memories Surface</h2>

<div class="callout-card" style="margin-bottom: 14px; background: #FFFFFF;">
<p style="font-size: 16px; color: #131B2E; margin: 0; line-height: 1.6;">
Precomputed filters. JSON indexed by time, place and category. Detail cues fall back to string matching against static image descriptions.
</p>
</div>
</div>
</div>"""

if hasattr(st, 'html'):
    st.html(html_content)
else:
    st.markdown(html_content, unsafe_allow_html=True)
