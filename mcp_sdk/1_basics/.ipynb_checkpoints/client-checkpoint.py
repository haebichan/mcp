import requests
import json

# MCP protocol format for calling tools
rpc_payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",  # MCP method for calling tools
    "params": {
        "name": "echo",      # Tool name
        "arguments": {"text": "Hello MCP!"}  # Tool arguments
    },
    "id": 1
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-06-18"
}

response = requests.post("http://localhost:8080/mcp/rpc", json=rpc_payload, headers=headers)

# Parse SSE response
raw_response = response.text
print("Raw response:", raw_response)

# # Extract JSON from SSE format
# if "data: " in raw_response:
#     # Get the line that starts with "data: "
#     for line in raw_response.split('\n'):
#         if line.startswith('data: '):
#             json_data = line[6:]  # Remove "data: " prefix
#             try:
#                 result = json.loads(json_data)
#                 print("✅ Parsed result:", json.dumps(result, indent=2))
                
#                 # Extract the actual tool result
#                 if "result" in result and "content" in result["result"]:
#                     tool_output = result["result"]["content"][0]["text"]
#                     print(f"🎯 Tool output: {tool_output}")
#                 break
#             except json.JSONDecodeError as e:
#                 print(f"❌ JSON decode error: {e}")
# else:
#     print("❌ No SSE data found")