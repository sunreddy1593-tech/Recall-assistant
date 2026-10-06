import json
import re
from datetime import datetime
import requests
import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=False)
def parse_era(user_phrase, chapters_data, today_str=None):
    if not today_str:
        today_str = datetime.today().strftime("%Y-%m-%d")
        
    api_key = st.secrets.get("GEMINI_API_KEY")
    model = st.secrets.get("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
    
    fallback = {"start": None, "end": None, "matched_chapter": None, "confidence": 0, "explanation": "Fallback"}
    
    if api_key:
        prompt = f"""
You are an AI era parser. Today is {today_str}.
The user said: "{user_phrase}"

Available chapters:
{json.dumps(chapters_data)}

Return a strict JSON object:
{{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "matched_chapter": str|null, "confidence": 0-1, "explanation": "≤ 12 words"}}

Rules:
- "before COVID" -> up to 2020-03-15
- "college first year" -> first 12 months of the College chapter
- "when I was in Scotland" -> Scotland chapter
- "summer 2019" -> 2019-04-01..2019-07-31 (Indian summer)
- "around 3-4 years ago" -> relative to today
- If no match, confidence should be < 0.5.
"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200:
                text = r.json()['candidates'][0]['content']['parts'][0]['text']
                res = json.loads(text)
                if res.get("confidence", 0) >= 0.5:
                    return res
        except Exception as e:
            print(f"Era parser error: {e}")

    # Fallback
    user_lower = user_phrase.lower()
    
    if "before covid" in user_lower:
        return {"start": "1990-01-01", "end": "2020-03-15", "matched_chapter": "Before COVID", "confidence": 0.9, "explanation": "Built-in"}
    if "lockdown" in user_lower:
        return {"start": "2020-03-15", "end": "2021-06-30", "matched_chapter": "During lockdown", "confidence": 0.9, "explanation": "Built-in"}
        
    # Check chapter aliases
    for c in chapters_data:
        aliases = str(c.get('aliases', '')).split(';')
        aliases.append(c['name'].lower())
        for a in aliases:
            if a and a.strip().lower() in user_lower:
                return {"start": c["start"][:10], "end": c["end"][:10], "matched_chapter": c["name"], "confidence": 0.8, "explanation": "Matched chapter alias"}
                
    # Check years
    years = re.findall(r'\b(201\d|202\d)\b', user_phrase)
    if years:
        y = years[0]
        return {"start": f"{y}-01-01", "end": f"{y}-12-31", "matched_chapter": None, "confidence": 0.7, "explanation": f"Matched year {y}"}
        
    return fallback

@st.cache_data(show_spinner=False)
def detail_rerank(candidate_photos, detail):
    api_key = st.secrets.get("GEMINI_API_KEY")
    model = st.secrets.get("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
    
    ranked_ids = []
    
    if api_key and candidate_photos:
        prompt = f"""
Rank these photos by relevance to the detail: "{detail}"
Photos:
{json.dumps([{"id": p["id"], "caption": p.get("caption"), "objects": p.get("objects", []), "clothing": p.get("clothing_colours", [])} for p in candidate_photos])}

Return a JSON list of objects: {{"id": str, "score": float (0-1)}}. Keep only those with score > 0.
"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200:
                text = r.json()['candidates'][0]['content']['parts'][0]['text']
                res = json.loads(text)
                res = sorted(res, key=lambda x: x['score'], reverse=True)
                return [x['id'] for x in res if x['score'] > 0]
        except Exception as e:
            print(f"Rerank error: {e}")
            
    # Fallback
    detail_words = set(re.findall(r'\w+', detail.lower())) - {'find', 'a', 'photo', 'of', 'the', 'you', 'your', 'in', 'at', 'on', 'with', 'from', 'for', 'it', 'place', 'while', 'took', 'his', 'her', 'my', 'and', 'was', 'this', 'that'}
    scores = []
    for p in candidate_photos:
        text = (p.get('caption', '') + " " + " ".join(p.get('objects', [])) + " " + " ".join(p.get('clothing_colours', [])) + " " + p.get('text_in_image', '')).lower()
        matches = [w for w in detail_words if len(w) > 2 and w in text]
        if matches:
            print(f"Matched {matches} in {p['id']}")
            scores.append((p['id'], len(matches)))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in scores]

@st.cache_data(show_spinner=False)
def parse_description(user_text, index_data):
    api_key = st.secrets.get("GEMINI_API_KEY")
    model = st.secrets.get("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
    
    # Extract unique values to limit AI hallucination
    chapters = [c["name"] for c in index_data.get("chapters", [])]
    people = list(set([p for p in index_data.get("people", [])]))
    places = list(set([p.get("place") for p in index_data.get("photos", {}).values() if p.get("place") and p.get("place") != "Unknown place"]))
    events = list(set([ev.get("event_label") for ev in index_data.get("events", []) if ev.get("event_label")]))
    
    fallback = {"chapters": [], "who": [], "where": [], "what": [], "type": [], "anything_else": user_text}
    
    if api_key:
        prompt = f"""
Turn this description into filter chips: "{user_text}"

Available filters (ONLY use these values if they match exactly):
- chapters: {json.dumps(chapters)}
- who: {json.dumps(people)}
- where: {json.dumps(places)}
- what: {json.dumps(events)}
- type: ["Photos", "Screenshots", "Documents"]

Return a strict JSON object:
{{"chapters": [str], "who": [str], "where": [str], "what": [str], "type": [str], "anything_else": str}}
For anything_else, put details like colors, specific objects, or mood that don't fit the filters. If none, leave blank.
"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200:
                text = r.json()['candidates'][0]['content']['parts'][0]['text']
                res = json.loads(text)
                
                # Cleanup hallucinated values
                clean = {}
                clean["chapters"] = [c for c in res.get("chapters", []) if c in chapters]
                clean["who"] = [w for w in res.get("who", []) if w in people]
                clean["where"] = [w for w in res.get("where", []) if w in places]
                clean["what"] = [w for w in res.get("what", []) if w in events]
                clean["type"] = [t for t in res.get("type", []) if t in ["Photos", "Screenshots", "Documents"]]
                clean["anything_else"] = res.get("anything_else", "")
                return clean
        except Exception as e:
            print(f"Desc parser error: {e}")
            
    # Fallback
    user_lower = user_text.lower()
    res = {"chapters": [], "who": [], "where": [], "what": [], "type": [], "anything_else": user_text}
    for w in people:
        if w.lower() in user_lower: res["who"].append(w)
    for p in places:
        p_words = set(p.lower().replace('-', ' ').split()) - {'of', 'the', 'in', 'and'}
        u_words = set(re.findall(r'\w+', user_lower))
        if p_words.intersection(u_words):
            res["where"].append(p)
    return res
