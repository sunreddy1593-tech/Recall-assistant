def rank_moments(events, max_results=5):
    # Sort events
    # 1. number of matched facets (we don't strictly track this per event in apply_filters yet, but we can assume they all match the active filters)
    # 2. fewer photos first (more specific)
    # 3. recency (newest first)
    
    def sort_key(ev):
        n_photos = len(ev.get("matched_photo_ids", ev.get("photo_ids", [])))
        start_time = ev.get("start", "")
        return (n_photos, start_time) # We want smaller n_photos, but newer start_time.
        
    sorted_events = sorted(events, key=lambda e: (len(e.get("matched_photo_ids", e.get("photo_ids", []))),), reverse=False)
    # To properly do recency, we can just sort by start_time descending after n_photos
    sorted_events.sort(key=lambda e: e.get("start", ""), reverse=True)
    sorted_events.sort(key=lambda e: len(e.get("matched_photo_ids", e.get("photo_ids", []))))
    
    if max_results is not None:
        return sorted_events[:max_results]
    return sorted_events

def get_narrowing_question(events, current_filters):
    if len(events) <= 5:
        return None
        
    # Find a facet that splits the candidates well
    types = set()
    places = set()
    labels = set()
    
    for ev in events:
        types.add(ev.get("event_type"))
        places.add(ev.get("place"))
        labels.add(ev.get("event_label"))
        
    if len(types) > 1 and not current_filters.get("type"):
        return {
            "facet": "type",
            "text": "What type of photo is it?",
            "options": [{"label": "Photos", "value": "Photos"}, {"label": "Screenshots", "value": "Screenshots"}, {"label": "Documents", "value": "Documents"}]
        }
    if len(labels) > 1 and not current_filters.get("what"):
        options = [{"label": l, "value": l} for l in list(labels)[:3]]
        return {
            "facet": "what",
            "text": "Was it closer to...",
            "options": options
        }
    if len(places) > 1 and not current_filters.get("where"):
        options = [{"label": p, "value": p} for p in list(places)[:3] if p != "Unknown place"]
        if options:
            return {
                "facet": "where",
                "text": "Where was it?",
                "options": options
            }
            
    return None
