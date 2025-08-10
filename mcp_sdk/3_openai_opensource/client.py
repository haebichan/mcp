import requests
import json

# Read CSV file
with open("sample.csv", "r") as f:
    csv_data = f.read()

# Build RPC payload
rpc_payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "summarize_csv",
        "arguments": {"csv_text": csv_data}
    },
    "id": 2
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-06-18"
}

# Send request to local MCP server
response = requests.post("http://localhost:8080/mcp/rpc", json=rpc_payload, headers=headers)

# Parse response from SSE
for line in response.text.split('\n'):
    if line.startswith('data: '):
        result = json.loads(line[6:])
        print("✅ Summary:", json.dumps(result, indent=2))
        break
