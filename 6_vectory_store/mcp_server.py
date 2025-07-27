# mcp_server.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
import uvicorn
import os
from typing import Dict

app = FastAPI()

# In-memory store for session state
session_memory: Dict[str, list] = {}

class SummarizeCSVInput(BaseModel):
    filepath: str
    instruction: str
    session_id: str = None

class FilterCSVInput(BaseModel):
    filepath: str
    column: str
    value: str
    session_id: str = None

def save_to_memory(session_id: str, tool: str, result: str):
    if not session_id:
        return
    if session_id not in session_memory:
        session_memory[session_id] = []
    session_memory[session_id].append({"tool": tool, "output": result})

@app.post("/tools/summarize_csv")
async def summarize_csv(input: SummarizeCSVInput):
    try:
        if not os.path.exists(input.filepath):
            return {"output": f"Error: File '{input.filepath}' not found."}

        df = pd.read_csv(input.filepath)
        summary = df.describe(include='all').to_dict()
        result = f"Summary stats:\n{summary}"
        save_to_memory(input.session_id, "summarize_csv", result)
        return {"output": result}
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        save_to_memory(input.session_id, "summarize_csv", error_msg)
        return {"output": error_msg}

@app.post("/tools/filter_csv")
async def filter_csv(input: FilterCSVInput):
    try:
        if not os.path.exists(input.filepath):
            return {"output": f"Error: File '{input.filepath}' not found."}

        df = pd.read_csv(input.filepath)
        filtered = df[df[input.column] == input.value]
        result = filtered.to_csv(index=False)
        save_to_memory(input.session_id, "filter_csv", result)
        return {"output": result}
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        save_to_memory(input.session_id, "filter_csv", error_msg)
        return {"output": error_msg}

@app.get("/memory/{session_id}")
async def get_memory(session_id: str):
    return session_memory.get(session_id, [])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)