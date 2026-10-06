import json
import csv
import os
import sys

def main():
    if not os.path.exists("logs/events.jsonl"):
        print("No logs found.")
        return
        
    answer_key = {}
    with open("tests/answer_key.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            answer_key[row["scenario"]] = [p.strip() for p in row["target_files"].split(";")]
            answer_key[row["task_prompt_for_tester"]] = [p.strip() for p in row["target_files"].split(";")]

    sessions = {}
    with open("logs/events.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            try:
                ev = json.loads(line)
                sid = ev["session_id"]
                if sid not in sessions:
                    sessions[sid] = {"events": [], "participant": ev.get("participant"), "task": ev.get("task")}
                sessions[sid]["events"].append(ev)
            except:
                pass
                
    print(f"{'Participant':<12} | {'Task':<10} | {'Success':<8} | {'Steps':<6} | {'Elapsed(s)':<10} | {'Target Photo':<30} | {'Selected Photo':<30}")
    print("-" * 120)
    
    for sid, sdata in sessions.items():
        participant = sdata["participant"]
        task = sdata["task"]
        events = sdata["events"]
        
        target_photos = answer_key.get(task, [])
        if not target_photos and task and task.startswith("S"):
            target_photos = answer_key.get(task.split()[0], [])
            
        success = "N"
        steps = 0
        elapsed = 0
        selected_photo = "None"
        
        for ev in events:
            if ev.get("step"):
                steps = max(steps, ev["step"])
            if ev.get("elapsed_s") is not None:
                elapsed = max(elapsed, ev["elapsed_s"])
            if ev["event"] == "photo_confirmed":
                det = str(ev.get("detail", ""))
                selected_photo = det.split(" in ")[0] if " in " in det else det
                
        if task == "FREE":
            success = "N/A"
            target_str = "Free Exploration"
        else:
            if selected_photo in target_photos:
                success = "Y"
            target_str = target_photos[0] if target_photos else "Unknown"
            
        print(f"{participant or 'Unknown':<12} | {str(task)[:10] if task else 'Unknown':<10} | {success:<8} | {steps:<6} | {elapsed:<10.1f} | {target_str[:30]:<30} | {selected_photo[:30]:<30}")

if __name__ == "__main__":
    main()
