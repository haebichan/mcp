# server.py
import os
import requests
import pandas as pd
from io import StringIO
from fastmcp import FastMCP

# Small CPU-friendly Llama via Ollama (change if you want)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")

mcp = FastMCP(name="Smart CSV Agent (Ollama)", stateless_http=True)

@mcp.tool()
def echo(text: str) -> str:
    return f"Echo: {text}"

@mcp.tool()
def summarize_csv(csv_text: str) -> str:
    """
    Load CSV with pandas, then summarize via a local Llama model served by Ollama.
    """
    try:
        df = pd.read_csv(StringIO(csv_text), sep=None, engine="python")

        # keep prompt small & informative
        preview = df.head(20).to_markdown(index=False)
        stats = df.describe(include="all").to_string()

        prompt = (
            "You are a concise data analyst. Summarize the dataset with 3–6 bullets: "
            "trends by region, highs/lows, and simple stats. Return only bullet points.\n\n"
            f"Preview (first rows):\n{preview}\n\n"
            f"Stats snapshot:\n{stats}\n"
        )

        payload = {
            "model": OLLAMA_MODEL,
            "stream": False,  # easier to consume
            "messages": [
                {"role": "system", "content": "Be brief and factual."},
                {"role": "user", "content": prompt}
            ],
        }

        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()

        # Ollama chat returns: {"message": {"role": "assistant", "content": "..."}}
        msg = data.get("message", {})
        text = msg.get("content", "")
        return text or "No response from model."
    except Exception as e:
        return f"Error processing CSV: {e}"

if __name__ == "__main__":
    # Exposes MCP at http://127.0.0.1:8080/mcp/rpc (SSE)
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)
