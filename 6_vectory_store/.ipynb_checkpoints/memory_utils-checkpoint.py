# memory_utils.py

import requests

def fetch_memory_summary(session_id: str):
    try:
        res = requests.get(f"http://localhost:8080/memory/{session_id}")
        memory = res.json()
        if isinstance(memory, list) and memory:
            summaries = [f"[{m['tool']}] {m['output'][:80]}..." for m in memory]
            return "\n".join(summaries)
    except Exception as e:
        return f"(Error loading memory: {e})"
    return "(no prior memory)"
