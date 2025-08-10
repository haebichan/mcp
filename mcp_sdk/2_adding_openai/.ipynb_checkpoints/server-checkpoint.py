# server.py
import openai
from fastmcp import FastMCP
import pandas as pd
from io import StringIO
import os
import csv

openai.api_key = os.environ['OPENAI_API_KEY']

mcp = FastMCP(name="Smart CSV Agent", stateless_http=True)

@mcp.tool()
def echo(text: str) -> str:
    return f"Echo: {text}"

@mcp.tool()
def summarize_csv(csv_text: str) -> str:
    """
    Load CSV with pandas and send summary request to OpenAI.
    """
    try:
        # Load into pandas for cleaner parsing
        df = pd.read_csv(StringIO(csv_text), sep=None, engine="python")

        # Optional: limit rows in prompt to avoid token bloat
        preview = df.head(20).to_csv(index=False)

        prompt = f"""
            Here is some CSV data (first 20 rows shown):
            {preview}
            
            Please give a concise high-level summary of the revenue data.
            If you notice trends or outliers, mention them.
            """

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error processing CSV: {e}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)
