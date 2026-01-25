import json
import datetime

# Implements Section 5.9 & 9: Self-Learning Logger
LOG_FILE = "agent_actions.jsonl"

def log_action(action_type, input_data, output_data):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action_type,
        "input": input_data,
        "output": output_data
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")