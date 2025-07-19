# mcp_server.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
import uvicorn
import os

app = FastAPI()

class SummarizeCSVInput(BaseModel):
    filepath: str
    instruction: str

class FilterCSVInput(BaseModel):
    filepath: str
    column: str
    value: str

@app.post("/tools/summarize_csv")
async def summarize_csv(input: SummarizeCSVInput):
    try:
        if not os.path.exists(input.filepath):
            return {"output": f"Error: File '{input.filepath}' not found."}

        df = pd.read_csv(input.filepath)
        summary = df.describe(include='all').to_dict()
        return {"output": f"Summary stats:\n{summary}"}
    except Exception as e:
        return {"output": f"Error: {str(e)}"}

@app.post("/tools/filter_csv")
async def filter_csv(input: FilterCSVInput):
    try:
        if not os.path.exists(input.filepath):
            return {"output": f"Error: File '{input.filepath}' not found."}

        df = pd.read_csv(input.filepath)
        if input.column not in df.columns:
            return {"output": f"Error: Column '{input.column}' not found in the file."}

        filtered = df[df[input.column] == input.value]
        return {"output": f"Filtered rows:\n{filtered.to_string(index=False)}"}
    except Exception as e:
        return {"output": f"Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
