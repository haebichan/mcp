from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
import uvicorn
import os

app = FastAPI()

# === Input Schemas ===
class SummarizeCSVInput(BaseModel):
    filepath: str
    instruction: str

class FilterCSVInput(BaseModel):
    filepath: str
    column: str
    value: str

# === ADDED: Tool schema for connection management ===
TOOLS_SCHEMA = [
    {
        "name": "summarize_csv",
        "description": "Summarize a CSV file with basic statistics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "instruction": {"type": "string"}
            },
            "required": ["filepath", "instruction"]
        }
    },
    {
        "name": "filter_csv", 
        "description": "Filter CSV rows based on column value",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "column": {"type": "string"},
                "value": {"type": "string"}
            },
            "required": ["filepath", "column", "value"]
        }
    }
]

# === Tool Implementations ===
async def summarize_csv(input: SummarizeCSVInput):
    if not os.path.exists(input.filepath):
        return {"output": f"Error: File '{input.filepath}' not found."}
    df = pd.read_csv(input.filepath)
    summary = df.describe(include='all').to_dict()
    return {"output": f"Summary stats:\n{summary}"}

async def filter_csv(input: FilterCSVInput):
    if not os.path.exists(input.filepath):
        return {"output": f"Error: File '{input.filepath}' not found."}
    df = pd.read_csv(input.filepath)
    filtered = df[df[input.column] == input.value]
    return {"output": filtered.to_csv(index=False)}

# === MCP-Compliant JSON-RPC 2.0 Handler ===
@app.post("/rpc")
async def rpc_handler(req: Request):
    body = await req.json()
    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")

    try:
        # ADDED: Connection management endpoints
        if method == "tools/list":
            result = {"tools": TOOLS_SCHEMA}
        elif method == "initialize":
            result = {
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Mini Analyst Agent", "version": "1.0.0"}
            }
        # Your original tool handlers
        elif method == "summarize_csv":
            input_data = SummarizeCSVInput(**params)
            result = await summarize_csv(input_data)
        elif method == "filter_csv":
            input_data = FilterCSVInput(**params)
            result = await filter_csv(input_data)
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found."
                },
                "id": req_id
            }

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": req_id
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": str(e)
            },
            "id": req_id
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)