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
<div style="font-size: 12px; font-weight: 700; color: #00685F; text-transform: uppercase;">Demo Library</div>
<div style="font-weight: 600; font-size: 16px; color: #131B2E; margin-top: 2px;">Simulated Photos</div>
<p style="font-size: 14px; color: #515F74; margin-top: 4px; margin-bottom: 0;">
This is a demo library of 159 AI-generated and stock photos, not a real user's library.
</p>
</div>
</div>
</div>

<div class="callout-card" style="margin-bottom: 14px; background: #FFFFFF;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="width: 32px; height: 32px; border-radius: 9999px; background: #EAEDFF; color: #00685F; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">02</div>
<div>
<div style="font-size: 12px; font-weight: 700; color: #00685F; text-transform: uppercase;">Offline Step</div>
<div style="font-weight: 600; font-size: 16px; color: #131B2E; margin-top: 2px;">Building the Index</div>
<p style="font-size: 14px; color: #515F74; margin-top: 4px; margin-bottom: 0;">
`build_index.py` groups photos into moments by time and place (no AI) and labels them with a Gemini vision model. People and face groups are simulated and labelled manually.
</p>
</div>
</div>
</div>

<div class="callout-card" style="margin-bottom: 14px; background: #FFFFFF;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="width: 32px; height: 32px; border-radius: 9999px; background: #EAEDFF; color: #00685F; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">03</div>
<div>
<div style="font-size: 12px; font-weight: 700; color: #00685F; text-transform: uppercase;">Natural Recall</div>
<div style="font-weight: 600; font-size: 16px; color: #131B2E; margin-top: 2px;">Search time requests</div>
<p style="font-size: 14px; color: #515F74; margin-top: 4px; margin-bottom: 0;">
Optional Gemini text requests (era phrase → date range; "Describe it" → cue chips; "Anything else" re-ranking). Photos are never sent to the AI at search time. Every AI step has a rule-based fallback; the app works with no API key.
</p>
</div>
</div>
</div>

<div class="callout-card" style="margin-bottom: 14px; background: #FFFFFF;">
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="width: 32px; height: 32px; border-radius: 9999px; background: #EAEDFF; color: #00685F; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">04</div>
<div>
<div style="font-size: 12px; font-weight: 700; color: #00685F; text-transform: uppercase;">Production Note</div>
<div style="font-weight: 600; font-size: 16px; color: #131B2E; margin-top: 2px;">Google Photos Integration</div>
<p style="font-size: 14px; color: #515F74; margin-top: 4px; margin-bottom: 0;">
In production for Google Photos, this would run on Photos' existing labels and face groups.
</p>
</div>
</div>
</div>
</div>

<div style="margin-bottom: 32px;">
<h2 style="font-size: 20px; margin-bottom: 6px;">Where AI is used</h2>
<p style="font-size: 14px; color: #515F74; margin-bottom: 16px;">
Complete transparency into how the app uses AI in this MVP.
</p>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">Era → Date Range</div>
<div style="font-size: 13px; color: #515F74;">Interprets human phrases like "college years" or "before COVID" into concrete calendar intervals using LLM (with rule-based fallback).</div>
</div>
<span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:11px;">AI</span>
</div>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">Event Labels & Captions</div>
<div style="font-size: 13px; color: #515F74;">For this demo, all event labels and captions were written offline and human-checked; in production they come from Photos' existing labels.</div>
</div>
<span class="memory-stream-pill" style="background:#EAEDFF; color:#515F74; font-size:11px;">Manual (Offline)</span>
</div>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">Anything-else Re-ranking</div>
<div style="font-size: 13px; color: #515F74;">LLM checks if precomputed captions match the sensory details like "sparklers" or "red saree".</div>
</div>
<span class="memory-stream-pill" style="background:#89F5E7; color:#00201D; font-size:11px;">AI</span>
</div>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">Place Names</div>
<div style="font-size: 13px; color: #515F74;">Simulated location metadata.</div>
</div>
<span class="memory-stream-pill" style="background:#F2F3FF; color:#515F74; font-size:11px;">Location Data (No AI)</span>
</div>

<div class="retrieval-step-row">
<div>
<div style="font-weight: 600; color: #131B2E;">People & Faces</div>
<div style="font-size: 13px; color: #515F74;">Manually labelled simulated face groups.</div>
</div>
<span class="memory-stream-pill" style="background:#F2F3FF; color:#515F74; font-size:11px;">Face Groups (No AI)</span>
</div>
</div>
</div>"""

if hasattr(st, 'html'):
    st.html(html_content)
else:
    st.markdown(html_content, unsafe_allow_html=True)
