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
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="width: 32px; height: 32px; border-radius: 9999px; background: #EAEDFF; color: #00685F; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">01</div>
<div>
<div style="font-size: 12px; font-weight: 700; color: #00685F; text-transform: uppercase;">Local Storage</div>
<div style="font-weight: 600; font-size: 16px; color: #131B2E; margin-top: 2px;">Your Raw Photos</div>
<p style="font-size: 14px; color: #515F74; margin-top: 4px; margin-bottom: 0;">
Your camera roll remains stored privately on-device. Zero unencrypted uploads, zero metadata scraping.
</p>
</div>
</div>
</div>

<div class="callout-card" style="margin-bottom: 14px; background: #FFFFFF;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="width: 32px; height: 32px; border-radius: 9999px; background: #EAEDFF; color: #00685F; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">02</div>
<div>
<div style="font-size: 12px; font-weight: 700; color: #00685F; text-transform: uppercase;">Edge Inference</div>
<div style="font-weight: 600; font-size: 16px; color: #131B2E; margin-top: 2px;">AI Labels Events Offline</div>
<p style="font-size: 14px; color: #515F74; margin-top: 4px; margin-bottom: 0;">
Clusters photos by temporal bursts, co-presence, and ambient setting—creating a lightweight semantic memory graph without external cloud dependencies.
</p>
</div>
</div>
</div>

<div class="callout-card" style="margin-bottom: 14px; background: #FFFFFF;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="width: 32px; height: 32px; border-radius: 9999px; background: #EAEDFF; color: #00685F; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">03</div>
<div>
<div style="font-size: 12px; font-weight: 700; color: #00685F; text-transform: uppercase;">Natural Recall</div>
<div style="font-weight: 600; font-size: 16px; color: #131B2E; margin-top: 2px;">You Answer What You Remember</div>
<p style="font-size: 14px; color: #515F74; margin-top: 4px; margin-bottom: 0;">
Provide a fuzzy timeframe, companions, or sensory anchors you actually recall—like "wearing that yellow kurta near the hostel" or "before COVID".
</p>
</div>
</div>
</div>

<div class="callout-card" style="margin-bottom: 14px; background: #FFFFFF;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="width: 32px; height: 32px; border-radius: 9999px; background: #EAEDFF; color: #00685F; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">04</div>
<div>
<div style="font-size: 12px; font-weight: 700; color: #00685F; text-transform: uppercase;">Instant Match</div>
<div style="font-weight: 600; font-size: 16px; color: #131B2E; margin-top: 2px;">3–5 Moments to Recognise</div>
<p style="font-size: 14px; color: #515F74; margin-top: 4px; margin-bottom: 0;">
Recognition is effortless compared to recall. Your brain spots the exact moment in milliseconds when given a curated tray of candidate scenes.
</p>
</div>
</div>
</div>
</div>

<div style="margin-bottom: 32px;">
<h2 style="font-size: 20px; margin-bottom: 6px;">Where AI is used</h2>
<p style="font-size: 14px; color: #515F74; margin-bottom: 16px;">
Complete transparency into on-device intelligence vs. deterministic hardware metadata.
</p>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">Era → Date Range</div>
<div style="font-size: 13px; color: #515F74;">Interprets human phrases like "college years" or "before COVID" into concrete calendar intervals.</div>
</div>
<span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:11px;">AI</span>
</div>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">Event Labels & Captions</div>
<div style="font-size: 13px; color: #515F74;">Identifies clusters like "birthday dinner", "campus convocation", or "monsoon drive".</div>
</div>
<span class="memory-stream-pill" style="background:#EAEDFF; color:#515F74; font-size:11px;">AI (Precomputed)</span>
</div>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">Anything-else Matching</div>
<div style="font-size: 13px; color: #515F74;">Semantic vector matching for sensory details like "sparklers", "red saree", or "steaming tapri chai".</div>
</div>
<span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:11px;">AI</span>
</div>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">Place Names</div>
<div style="font-size: 13px; color: #515F74;">Raw hardware GPS coordinates reverse-geocoded deterministically via OpenStreetMap.</div>
</div>
<span class="memory-stream-pill" style="background:#F2F3FF; color:#515F74; font-size:11px;">Location Data (No AI)</span>
</div>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">People & Faces</div>
<div style="font-size: 13px; color: #515F74;">On-device facial clustering mapped directly to user-named local contacts.</div>
</div>
<span class="memory-stream-pill" style="background:#F2F3FF; color:#515F74; font-size:11px;">Face Groups</span>
</div>
</div>

<div class="callout-card" style="background: linear-gradient(135deg, #00685F 0%, #008378 100%); color: #FFFFFF; padding: 20px;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<span style="font-size: 24px;">🔒</span>
<div>
<div style="font-weight: 700; font-size: 16px; color: #FFFFFF;">Zero Cloud Ingestion</div>
<p style="font-size: 13px; color: #EAEDFF; margin-top: 4px; line-height: 1.5; margin-bottom: 0;">
Photo clustering, vectors, and embedding indexes remain strictly on local storage. If you disconnect from the internet, Recall operates identically.
</p>
</div>
</div>
</div>
</div>"""

if hasattr(st, 'html'):
    st.html(html_content)
else:
    st.markdown(html_content, unsafe_allow_html=True)
