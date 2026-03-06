import os
import json

def get_state_path(state_dir, day_str):
    os.makedirs(state_dir, exist_ok=True)
    return os.path.join(state_dir, f"state_{day_str}.json")

def load_state(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"seen_job_ids": []}

def save_state(path, state):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)