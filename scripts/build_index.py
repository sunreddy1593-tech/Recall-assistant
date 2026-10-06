import argparse
import json
import math
import os
import pandas as pd
from datetime import datetime
import reverse_geocoder as rg
from PIL import Image
import tomllib
import requests
import time
import io
import base64
import hashlib

def calculate_distance(lat1, lon1, lat2, lon2):
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return float('inf')
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_image_base64_resized(img_path, max_size=768):
    try:
        with Image.open(img_path) as img:
            img.thumbnail((max_size, max_size))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error reading image {img_path}: {e}")
        return None

def file_hash(img_path):
    h = hashlib.sha256()
    try:
        with open(img_path, 'rb') as f:
            h.update(f.read())
        return h.hexdigest()
    except Exception:
        return img_path

def process_vision_batch(api_key, model, photo_batch):
    # photo_batch: list of (photo_id, base64_img)
    parts = [{"text": "For each of the following images, in the order provided, return exactly one JSON object in a JSON list. Output ONLY the JSON list. Each object must have: {\"caption\": str, \"scene\": \"indoor|outdoor\", \"activity\": str, \"objects\": [str], \"clothing_colours\": [str], \"text_in_image\": str, \"mood\": str}. Keep caption under 20 words."}]
    
    for _, b64 in photo_batch:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": b64
            }
        })
        
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    for _ in range(3):
        try:
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 200:
                text = r.json()['candidates'][0]['content']['parts'][0]['text']
                res = json.loads(text)
                if isinstance(res, list) and len(res) == len(photo_batch):
                    return res
            time.sleep(2)
        except Exception as e:
            print(f"Vision API error: {e}")
            time.sleep(2)
    return None

def process_event_labels(api_key, model, event_captions):
    # event_captions: list of (event_id, list of captions)
    parts = [{"text": "For each event, given its photo captions, return a JSON list of objects. Output ONLY the JSON list. Each object must have: {\"event_label\": str (2-4 words), \"event_type\": \"celebration|trip|everyday|work|school|food|document|screenshot|other\"}. If captions indicate screenshots, bills, receipts, or tickets, type MUST be document or screenshot."}]
    
    for i, (eid, caps) in enumerate(event_captions):
        parts[0]["text"] += f"\n\nEvent {i+1}:\n" + "\n".join(caps)
        
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    for _ in range(3):
        try:
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 200:
                text = r.json()['candidates'][0]['content']['parts'][0]['text']
                res = json.loads(text)
                if isinstance(res, list) and len(res) == len(event_captions):
                    return res
            time.sleep(2)
        except Exception as e:
            print(f"Event API error: {e}")
            time.sleep(2)
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-ai', action='store_true', help='Skip AI processing')
    args = parser.parse_args()

    api_key = None
    vision_model = "gemini-1.5-flash"
    text_model = "gemini-1.5-flash"
    
    if not args.no_ai:
        try:
            with open(".streamlit/secrets.toml", "rb") as f:
                secrets = tomllib.load(f)
                api_key = secrets.get("GEMINI_API_KEY")
                vision_model = secrets.get("GEMINI_VISION_MODEL", vision_model)
                text_model = secrets.get("GEMINI_TEXT_MODEL", text_model)
        except Exception as e:
            print(f"Could not load secrets.toml: {e}")
            
    manifest_path = "library/manifest.csv"
    chapters_path = "library/chapters.csv"
    
    df_manifest = pd.read_csv(manifest_path)
    df_chapters = pd.read_csv(chapters_path)

    df_manifest['taken_at'] = pd.to_datetime(df_manifest['taken_at'])
    df_manifest = df_manifest.sort_values('taken_at').reset_index(drop=True)

    photos = {}
    people_set = set()
    events = []
    
    current_event_photos = []
    current_event_start = None
    last_photo_time = None
    last_lat = None
    last_lon = None

    vision_cache = {}
    if os.path.exists("data/vision_cache.json"):
        with open("data/vision_cache.json", "r") as f:
            vision_cache = json.load(f)

    batch_buffer = []
    
    for i, row in df_manifest.iterrows():
        photo_id = row['filename']
        dt = row['taken_at']
        lat = row['lat'] if 'lat' in row else None
        lon = row['lon'] if 'lon' in row else None
        
        place_override = row['place_override'] if 'place_override' in row and not pd.isna(row['place_override']) else None
        
        city = None
        if place_override:
            venue = place_override
        else:
            venue = "Unknown place"
            if not pd.isna(lat) and not pd.isna(lon):
                results = rg.search((lat, lon))
                if results:
                    city = results[0]['name']
                    venue = city

        people = []
        if 'people' in row and not pd.isna(row['people']):
            people = [p.strip() for p in row['people'].split(';')]
            people_set.update(people)
            
        notes = row['notes'] if 'notes' in row and not pd.isna(row['notes']) else ""

        is_document = False
        if "screenshot" in notes.lower() or "bill" in notes.lower():
            is_document = True

        photo_data = {
            "id": photo_id,
            "taken_at": dt.isoformat(),
            "lat": lat if not pd.isna(lat) else None,
            "lon": lon if not pd.isna(lon) else None,
            "place": venue,
            "city": city,
            "people": people,
            "caption": f"Placeholder caption for {photo_id}",
            "scene": "indoor" if "indoor" in notes.lower() else "outdoor",
            "activity": "unknown",
            "objects": [],
            "clothing_colours": [],
            "text_in_image": notes,
            "mood": "neutral"
        }
        
        # Load from cache if exists
        f_hash = file_hash(f"library/photos/{photo_id}")
        if f_hash in vision_cache and not args.no_ai:
            cached = vision_cache[f_hash]
            photo_data.update(cached)
        elif not args.no_ai and api_key:
            b64 = get_image_base64_resized(f"library/photos/{photo_id}")
            if b64:
                batch_buffer.append((photo_id, b64, f_hash))
                
        photos[photo_id] = photo_data
        
        if len(batch_buffer) >= 8:
            res = process_vision_batch(api_key, vision_model, [(x[0], x[1]) for x in batch_buffer])
            if res:
                for idx, v_data in enumerate(res):
                    pid = batch_buffer[idx][0]
                    photos[pid].update(v_data)
                    vision_cache[batch_buffer[idx][2]] = v_data
            batch_buffer = []

        if is_document or (not args.no_ai and photo_data.get('type') in ['document', 'screenshot']):
            if current_event_photos:
                events.append(create_event(current_event_photos, photos, args.no_ai))
                current_event_photos = []
            events.append(create_event([photo_id], photos, args.no_ai))
            last_photo_time = dt
            last_lat = lat
            last_lon = lon
            continue

        split = False
        if last_photo_time is not None:
            gap = (dt - last_photo_time).total_seconds() / 3600
            if gap > 6:
                split = True
            elif calculate_distance(lat, lon, last_lat, last_lon) > 30:
                split = True
                
        if split and current_event_photos:
            events.append(create_event(current_event_photos, photos, args.no_ai))
            current_event_photos = []

        current_event_photos.append(photo_id)
        last_photo_time = dt
        last_lat = lat
        last_lon = lon

    if current_event_photos:
        events.append(create_event(current_event_photos, photos, args.no_ai))
        
    # Flush remaining vision batch
    if batch_buffer and api_key:
        res = process_vision_batch(api_key, vision_model, [(x[0], x[1]) for x in batch_buffer])
        if res:
            for idx, v_data in enumerate(res):
                pid = batch_buffer[idx][0]
                photos[pid].update(v_data)
                vision_cache[batch_buffer[idx][2]] = v_data
                
    if not args.no_ai:
        os.makedirs("data", exist_ok=True)
        with open("data/vision_cache.json", "w") as f:
            json.dump(vision_cache, f, indent=2)

    # Process event labels in batches
    if not args.no_ai and api_key:
        event_batch = []
        for i, ev in enumerate(events):
            if ev.get("event_type") in ["document", "screenshot"] or args.no_ai:
                continue
            caps = [photos[pid].get("caption", "") for pid in ev["photo_ids"]]
            event_batch.append((i, caps))
            
            if len(event_batch) >= 8:
                res = process_event_labels(api_key, text_model, event_batch)
                if res:
                    for j, e_data in enumerate(res):
                        events[event_batch[j][0]]['event_label'] = e_data.get('event_label', 'Event')
                        events[event_batch[j][0]]['event_type'] = e_data.get('event_type', 'other')
                event_batch = []
                
        if event_batch:
            res = process_event_labels(api_key, text_model, event_batch)
            if res:
                for j, e_data in enumerate(res):
                    events[event_batch[j][0]]['event_label'] = e_data.get('event_label', 'Event')
                    events[event_batch[j][0]]['event_type'] = e_data.get('event_type', 'other')

    chapters_data = df_chapters.to_dict('records')
    for c in chapters_data:
        c['start'] = pd.to_datetime(c['start']).isoformat()
        c['end'] = pd.to_datetime(c['end']).isoformat()
        
    index_data = {
        "photos": photos,
        "events": events,
        "chapters": chapters_data,
        "people": list(people_set)
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/index.json", "w") as f:
        json.dump(index_data, f, indent=2)
    print(f"Index built with {len(photos)} photos and {len(events)} events.")

def create_event(photo_ids, photos_dict, no_ai):
    start_time = min([photos_dict[pid]['taken_at'] for pid in photo_ids])
    end_time = max([photos_dict[pid]['taken_at'] for pid in photo_ids])
    
    places = [photos_dict[pid]['place'] for pid in photo_ids if photos_dict[pid]['place'] != "Unknown place"]
    dominant_place = places[0] if places else "Unknown place"
    
    all_people = set()
    for pid in photo_ids:
        all_people.update(photos_dict[pid]['people'])
        
    event_label = "Placeholder Event"
    event_type = "other"
    
    if no_ai:
        texts = [photos_dict[pid].get('text_in_image', '').lower() for pid in photo_ids]
        combined_text = " ".join(texts)
        if "screenshot" in combined_text:
            event_type = "screenshot"
            event_label = "Screenshot"
        elif "bill" in combined_text or "receipt" in combined_text:
            event_type = "document"
            event_label = "Document"
        elif "birthday" in combined_text or "bday" in combined_text:
            event_type = "celebration"
            event_label = "Birthday Party"
        elif "school" in combined_text or "award" in combined_text:
            event_type = "school"
            event_label = "School Event"
        elif "work" in combined_text or "uniform" in combined_text:
            event_type = "work"
            event_label = "At Work"
        elif "cafe" in combined_text or "dinner" in combined_text:
            event_type = "food"
            event_label = "Out for Food"
        else:
            event_label = f"Event at {dominant_place}"
            
    return {
        "id": f"evt_{start_time.replace(':', '').replace('-', '')}_{len(photo_ids)}",
        "start": start_time,
        "end": end_time,
        "photo_ids": photo_ids,
        "place": dominant_place,
        "people": list(all_people),
        "event_label": event_label,
        "event_type": event_type
    }

if __name__ == "__main__":
    main()
