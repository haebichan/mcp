from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Simple in-memory store
session_memory = {
    "test-session-123": [
        {"tool": "dummy_tool", "output": "Hello from memory!"},
        {"tool": "another_tool", "output": "Another result."}
    ]
}

@app.get("/memory/{session_id}")
async def get_memory(session_id: str):
    return session_memory.get(session_id, [])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
