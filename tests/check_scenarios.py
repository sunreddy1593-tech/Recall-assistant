import csv
import json
import re
import os
from recall.index import apply_filters, get_facet_counts
from recall.ranking import rank_moments
from recall.ai import parse_era, detail_rerank, parse_description

def get_target_moments(target_files, events):
    target_pids = set(f.strip() for f in target_files.split(';'))
    target_event_ids = set()
    for ev in events:
        ev_photos = set(ev.get("photo_ids", []))
        if ev_photos.intersection(target_pids):
            target_event_ids.add(ev["id"])
    return target_event_ids

def simulate_scenario(scenario_id, prompt, target_files, index):
    print(f"--- Simulating {scenario_id} ---")
    print(f"Prompt: {prompt}")
    
    target_event_ids = get_target_moments(target_files, index["events"])
    if not target_event_ids:
        print("Error: Target files not found in any moment!")
        return 0, False
        
    # We will simulate applying filters sequentially based on what the user knows.
    # The user can use the description parser or answer questions. Let's use the description parser 
    # to extract keywords, and then apply them as if they answered questions.
    
    chips = parse_description(prompt, index)
    filters = {}
    steps = 0
    
    # 1. When
    # The user might use the era parser or chapter chips.
    era_res = parse_era(prompt, index["chapters"], "2026-10-06")
    if era_res.get("start"):
        filters["date_range"] = (era_res["start"], era_res["end"])
        steps += 1
        print(f"Step {steps}: Applied era '{era_res.get('matched_chapter', 'Date range')}'")
    elif chips.get("chapters"):
        filters["chapters"] = chips["chapters"]
        steps += 1
        print(f"Step {steps}: Selected chapter {chips['chapters']}")
        
    matched_events, matched_photos = apply_filters(index, filters)
    
    # 2. Who
    if chips.get("who"):
        filters["who"] = chips["who"]
        steps += 1
        print(f"Step {steps}: Selected who {chips['who']}")
        matched_events, matched_photos = apply_filters(index, filters)
        
    # 3. Where
    if chips.get("where"):
        filters["where"] = chips["where"]
        steps += 1
        print(f"Step {steps}: Selected where {chips['where']}")
        matched_events, matched_photos = apply_filters(index, filters)
        
    # 4. What / Type
    if chips.get("what"):
        filters["what"] = chips["what"]
        steps += 1
        print(f"Step {steps}: Selected what {chips['what']}")
    if chips.get("type") or "screenshot" in prompt.lower() or "document" in prompt.lower() or "bill" in prompt.lower():
        type_filter = chips.get("type", [])
        if not type_filter:
            if "screenshot" in prompt.lower(): type_filter = ["Screenshots"]
            elif "document" in prompt.lower() or "bill" in prompt.lower(): type_filter = ["Documents"]
        
        if type_filter:
            filters["type"] = type_filter
            steps += 1
            print(f"Step {steps}: Selected type {type_filter}")
            
    matched_events, matched_photos = apply_filters(index, filters)
    
    # 5. Anything else
    detail = chips.get("anything_else", "")
    if detail:
        filters["anything_else"] = detail
        steps += 1
        print(f"Step {steps}: Entered detail '{detail}'")
        
    # Rank moments
    ranked_events = rank_moments(matched_events, max_results=None)
    
    # Apply reranking
    if detail:
        candidate_photos = []
        for ev in ranked_events:
            for pid in ev.get("matched_photo_ids", ev["photo_ids"]):
                candidate_photos.append(index["photos"][pid])
        
        top_pids = detail_rerank(candidate_photos, detail)
        if top_pids:
            boosted = []
            
            # Sort events by their best position in top_pids
            def get_best_rank(ev):
                pids = ev.get("matched_photo_ids", ev["photo_ids"])
                ranks = [top_pids.index(pid) for pid in pids if pid in top_pids]
                return min(ranks) if ranks else float('inf')
                
            ranked_events.sort(key=get_best_rank)
            
    # Check top 5
    top_5_ids = [ev["id"] for ev in ranked_events[:5]]
    found = any(tid in top_5_ids for tid in target_event_ids)
    
    if found:
        # Simulate open moment step
        steps += 1
        print(f"Step {steps}: Opened moment and found photo!")
        print(f"Result: SUCCESS in {steps} steps")
    else:
        print(f"Result: FAILED. Targets {target_event_ids} not in top 5: {top_5_ids}")
        
    return steps, found

def main():
    if not os.path.exists("data/index.json"):
        print("Please build index first.")
        return
        
    with open("data/index.json", "r") as f:
        index = json.load(f)
        
    total_scenarios = 0
    passed = 0
    all_steps = []
    
    with open("tests/answer_key.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario = row["scenario"]
            prompt = row["task_prompt_for_tester"]
            target_files = row["target_files"]
            
            steps, found = simulate_scenario(scenario, prompt, target_files, index)
            total_scenarios += 1
            if found and steps <= 6:
                passed += 1
                all_steps.append(steps)
            print()
            
    print(f"Summary: {passed}/{total_scenarios} scenarios passed within <=6 steps.")
    if all_steps:
        print(f"Average steps: {sum(all_steps)/len(all_steps):.1f}")
        
if __name__ == "__main__":
    main()
