import requests
import json
import os
import openai
import pandas as pd

# Get user input
user_query = input("Enter your question: ")

# Set up OpenAI
openai.api_key = os.environ['OPENAI_API_KEY']

# Get available tools from MCP server
tools_payload = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-06-18"
}

# Request tools list
tools_response = requests.post("http://localhost:8080/mcp/rpc", json=tools_payload, headers=headers)

# Parse tools from SSE response
available_tools = ""
for line in tools_response.text.split('\n'):
    if line.startswith('data: '):
        tools_result = json.loads(line[6:])
        if "result" in tools_result and "tools" in tools_result["result"]:
            tools_list = []
            for tool in tools_result["result"]["tools"]:
                name = tool["name"]
                desc = tool.get("description", "")
                # Get parameter names from inputSchema
                params = []
                if "inputSchema" in tool and "properties" in tool["inputSchema"]:
                    params = list(tool["inputSchema"]["properties"].keys())
                
                tool_desc = f"- {name}({', '.join([f'{p}: str' for p in params])}): {desc}"
                tools_list.append(tool_desc)
            
            available_tools = "\n".join(tools_list)
        break

print(f"🔍 Found tools:\n{available_tools}")

# Ask GPT to decide what to do
planning_prompt = f"""
User question: "{user_query}"

Available tools:
{available_tools}

Based on the user's question, which tool should I call and with what arguments?
If they want CSV analysis, use "summarize_csv" and I'll read the file.

Return JSON only:
{{"tool": "tool_name", "args": {{"param": "value"}}}}
"""

# Get GPT's decision
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": planning_prompt}]
)

# Parse GPT's plan
plan = json.loads(response.choices[0].message.content)
tool_name = plan["tool"]
args = plan["args"]

print(f"🧠 GPT decided to use: {tool_name}")

# If it's CSV analysis, read the file
if tool_name == "summarize_csv" and "csv_text" in args:
    df = pd.read_csv("sample.csv")
    args["csv_text"] = df.to_csv(index=False)
    
    print("📁 Loaded CSV file")

# Build RPC payload
rpc_payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": tool_name,
        "arguments": args
    },
    "id": 2
}

# Send request to local MCP server
response = requests.post("http://localhost:8080/mcp/rpc", json=rpc_payload, headers=headers)


# Parse response from SSE
for line in response.text.split('\n'):
    if line.startswith('data: '):
        result = json.loads(line[6:])
        # Extract just the text result
        if "result" in result and "content" in result["result"]:
            answer = result["result"]["content"][0]["text"]
            print(f"✅ Answer: {answer}")
        break