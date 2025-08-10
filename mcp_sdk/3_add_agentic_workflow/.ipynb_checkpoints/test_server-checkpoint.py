from fastmcp import FastMCP
import pandas as pd
import os

SAMPLECSV = 'sample.csv'
mcp = FastMCP(name="Smart CSV Agent", stateless_http=True)

@mcp.resource("resource://sample-csv")  # Add the "resource://" scheme
def get_sample_csv() -> str:
    """Returns the content of sample.csv."""
    try:
        df = pd.read_csv(SAMPLECSV)
        return df.to_csv(index=False)
    except Exception as e:
        return f"Error reading CSV: {e}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)