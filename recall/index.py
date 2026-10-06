import json
import os
from datetime import datetime
import pandas as pd

_index_cache = None

def load_index():
    global _index_cache
    if _index_cache is not None:
        return _index_cache
        
    path = "data/index.json"
    if not os.path.exists(path):
        return {"photos": {}, "events": [], "chapters": [], "people": []}
        
    with open(path, "r") as f:
        _index_cache = json.load(f)
    return _index_cache

def apply_filters(index, filters):
    """
    filters: dict
    {
        "chapters": ["College"],
        "year": "2019",
        "date_range": ("2019-01-01", "2019-12-31"),
        "where": ["Café Bodega, Panjim"],
        "who": ["Ananya"],
        "what": ["Birthday Party"],
        "type": ["Photos"]
    }
    """
    photos = index["photos"]
    events = index["events"]
    chapters = index["chapters"]
    
    # Filter photos first based on properties
    matched_photos = set(photos.keys())
    
    if filters.get("who"):
        # For each photo, check if ANY of the selected 'who' are present (or if ALL are present? Usually OR within a facet)
        who_set = set(filters["who"])
        if "Just me" in who_set:
            who_set.add("Just me") # Depending on how it's saved
            
        new_matched = set()
        for pid in matched_photos:
            p_people = set(photos[pid].get("people", []))
            if "Not sure" in who_set:
                new_matched.add(pid)
            elif "Just me" in who_set and not p_people:
                 new_matched.add(pid)
            elif p_people.intersection(who_set):
                new_matched.add(pid)
            elif "Just me" in p_people and "Just me" in who_set:
                new_matched.add(pid)
        matched_photos = new_matched
        
    if filters.get("where"):
        where_set = set(filters["where"])
        new_matched = set()
        for pid in matched_photos:
            p = photos[pid]
            locs = {p.get("place"), p.get("city")}
            if locs.intersection(where_set):
                new_matched.add(pid)
        matched_photos = new_matched
        
    # Time filtering
    if filters.get("year"):
        y = str(filters["year"])
        matched_photos = {pid for pid in matched_photos if photos[pid]["taken_at"].startswith(y)}
        
    if filters.get("date_range"):
        start, end = filters["date_range"]
        matched_photos = {pid for pid in matched_photos if start <= photos[pid]["taken_at"] <= end}
        
    if filters.get("chapters"):
        chap_set = set(filters["chapters"])
        # Find chapter ranges
        chap_ranges = []
        for c in chapters:
            if c["name"] in chap_set:
                chap_ranges.append((c["start"], c["end"]))
                
        new_matched = set()
        for pid in matched_photos:
            t = photos[pid]["taken_at"]
            for s, e in chap_ranges:
                if s <= t <= e:
                    new_matched.add(pid)
                    break
        matched_photos = new_matched
        
    # Now filter events based on matched photos and event filters
    matched_events = []
    for ev in events:
        ev_photos = set(ev["photo_ids"]).intersection(matched_photos)
        if not ev_photos:
            continue
            
        if filters.get("what"):
            if ev.get("event_label") not in filters["what"]:
                continue
                
        if filters.get("type"):
            types = filters["type"]
            ev_type = ev.get("event_type", "other")
            if "Photos" in types and ev_type not in ["document", "screenshot"]:
                pass # match
            elif "Screenshots" in types and ev_type == "screenshot":
                pass
            elif "Documents" in types and ev_type == "document":
                pass
            else:
                continue
                
        matched_events.append({**ev, "matched_photo_ids": list(ev_photos)})
        
    final_photos = set()
    for ev in matched_events:
        final_photos.update(ev["matched_photo_ids"])
        
    return matched_events, final_photos

def get_facet_counts(index, current_filters):
    # To do true faceted search, we compute options by applying all OTHER filters
    facets = {
        "where": {},
        "who": {},
        "what": {},
        "chapters": {},
        "type": {"Photos": 0, "Screenshots": 0, "Documents": 0}
    }
    
    # helper to get events/photos with one filter removed
    def get_matches_without(facet_key):
        temp_filters = current_filters.copy()
        if facet_key in temp_filters:
            del temp_filters[facet_key]
        return apply_filters(index, temp_filters)
        
    # For each facet, we count how many items would remain if we selected that option
    
    # 1. Who
    evs, phs = get_matches_without("who")
    for pid in phs:
        people = index["photos"][pid].get("people", [])
        if not people:
            facets["who"]["Just me"] = facets["who"].get("Just me", 0) + 1
        for p in people:
            facets["who"][p] = facets["who"].get(p, 0) + 1
            
    # 2. Where
    evs, phs = get_matches_without("where")
    for pid in phs:
        p = index["photos"][pid]
        place = p.get("place")
        city = p.get("city")
        if place and place != "Unknown place":
            facets["where"][place] = facets["where"].get(place, 0) + 1
        elif city:
            facets["where"][city] = facets["where"].get(city, 0) + 1
            
    # 3. What (events)
    evs, phs = get_matches_without("what")
    for ev in evs:
        label = ev.get("event_label")
        if label:
            facets["what"][label] = facets["what"].get(label, 0) + 1
            
    # 4. Chapters
    evs, phs = get_matches_without("chapters")
    for pid in phs:
        t = index["photos"][pid]["taken_at"]
        for c in index["chapters"]:
            if c["start"] <= t <= c["end"]:
                facets["chapters"][c["name"]] = facets["chapters"].get(c["name"], 0) + 1
                
    # 5. Type
    evs, phs = get_matches_without("type")
    for ev in evs:
        t = ev.get("event_type", "other")
        count = len(ev.get("matched_photo_ids", ev["photo_ids"]))
        if t == "screenshot":
            facets["type"]["Screenshots"] += count
        elif t == "document":
            facets["type"]["Documents"] += count
        else:
            facets["type"]["Photos"] += count
            
    return facets
