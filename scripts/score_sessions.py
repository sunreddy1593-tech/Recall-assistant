import json
import csv
import os
import sys

def main():
    import pandas as pd
    answer_key = {}
    with open("tests/answer_key.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            answer_key[row["scenario"]] = [p.strip() for p in row["target_files"].split(";")]
            answer_key[row["task_prompt_for_tester"]] = [p.strip() for p in row["target_files"].split(";")]

    df = pd.DataFrame()
    if len(sys.argv) > 1 and sys.argv[1].endswith(".csv"):
        df = pd.read_csv(sys.argv[1])
    else:
        if not os.path.exists("logs/events.jsonl"):
            print("No logs found.")
            return
        data = []
        with open("logs/events.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except:
                        pass
        df = pd.DataFrame(data)
        
    from recall.session_metrics import process_sessions
    sessions = process_sessions(df)
                
    print(f"{'Participant':<12} | {'Task':<10} | {'Status':<10} | {'Steps':<6} | {'Elapsed(s)':<10} | {'Target Photo':<30} | {'Selected Photo':<30}")
    print("-" * 120)
    
    for sdata in sessions:
        participant = sdata["participant"]
        task = sdata["task"]
        
        target_photos = answer_key.get(task, [])
        if not target_photos and task and task.startswith("S"):
            target_photos = answer_key.get(task.split()[0], [])
            
        success = "Unknown"
        steps = sdata["max_step"] if sdata["max_step"] is not None else "Unknown"
        elapsed = f"{sdata['max_elapsed']:.1f}" if sdata["max_elapsed"] is not None else "Unknown"
        selected_photo = sdata["confirmed_photo"] or "None"
        
        if task == "FREE":
            success = "N/A"
            target_str = "Free Exploration"
        else:
            if sdata["abandoned"]:
                success = "Abandoned"
            elif selected_photo != "None":
                if selected_photo in target_photos:
                    success = "Correct"
                else:
                    success = "Incorrect"
            else:
                success = "Incomplete"
                
            target_str = target_photos[0] if target_photos else "Unknown"
            
        print(f"{participant or 'Unknown':<12} | {str(task)[:10] if task else 'Unknown':<10} | {success:<10} | {str(steps):<6} | {str(elapsed):<10} | {target_str[:30]:<30} | {selected_photo[:30]:<30}")

if __name__ == "__main__":
    main()
