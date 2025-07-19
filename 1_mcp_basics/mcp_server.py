# mcp_server.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
import uvicorn

app = FastAPI()

class SummarizeCSVInput(BaseModel):
    filepath: str
    instruction: str

@app.post("/tools/summarize_csv")
async def summarize_csv(input: SummarizeCSVInput):
    try:
        df = pd.read_csv(input.filepath)
        summary = df.describe(include='all').to_dict()
        return {"output": f"Summary stats:\n{summary}"}
    except Exception as e:
        return {"output": f"Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)